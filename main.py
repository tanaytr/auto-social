import argparse, os, requests, tweepy
from google import genai
from google.genai import types

def post_to_x(text, file_path):
    # X Free Tier requires OAuth 1.0a for media upload (v1.1) and v2 for posting
    auth = tweepy.OAuth1UserHandler(
        os.environ["X_API_KEY"], os.environ["X_API_SECRET"],
        os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_SECRET"]
    )
    api_v1 = tweepy.API(auth)
    client_v2 = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"], consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"], access_token_secret=os.environ["X_ACCESS_SECRET"]
    )
    
    # Upload media via v1.1
    media = api_v1.media_upload(filename=file_path)
    # Post tweet via v2
    client_v2.create_tweet(text=text, media_ids=[media.media_id])

def main():
    parser = argparse.ArgumentParser()
    # ... (args setup for type, subject, platform, caption, size, asset_url)
    args = parser.parse_args()
    
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    # 1. Generate/Download Visual
    asset_path = "final_content.jpg"
    if args.asset_url:
        with open(asset_path, 'wb') as f: f.write(requests.get(args.asset_url).content)
    else:
        # Generate with Gemini 3 Flash Image
        response = client.models.generate_image(
            model="gemini-3-flash-image",
            prompt=f"A high-end {args.type} about {args.subject}. Professional lighting.",
            config=types.GenerateImageConfig(aspect_ratio=args.size)
        )
        response.image.save(asset_path)

    # 2. Polish Caption
    prompt = f"Write a viral {args.platform} caption for this {args.subject}: {args.caption}"
    caption_res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    
    # 3. Upload
    if args.platform.upper() == "X":
        post_to_x(caption_res.text, asset_path)
        print("Successfully posted to X!")

if __name__ == "__main__":
    main()
