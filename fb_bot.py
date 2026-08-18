import requests
import random
import os
import urllib.parse

PAGE_ID = os.environ.get("FB_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

CAPTIONS = [
    "Exploring the beautiful colors of nature! 🌟 #lifestyle #aiart #beauty #vibes",
    "Chasing dreams and catching flights. ✨ #fashion #trending #aiart #photography",
    "Confidence is not 'they will like me', confidence is 'I will be fine if they don't.' 💫 #motivation #aesthetic",
    "Finding joy in the ordinary. 🌸 #simplelife #portraits #aiartdaily",
    "Style is a way to say who you are without having to speak. 👗 #fashionblogger #style"
]

PROMPTS = [
    "A beautiful girl wearing a casual summer outfit, smiling, high quality, realistic, natural lighting, 8k resolution",
    "A stylish young female model with curly hair, posing in an urban city background, fashion photography, hyperrealistic",
    "An elegant Indian girl in traditional clothing, portrait shot, soft light, cinematographic, highly detailed"
]

def generate_and_post():
    selected_prompt = random.choice(PROMPTS)
    caption = random.choice(CAPTIONS)
    encoded_prompt = urllib.parse.quote(selected_prompt)
    
    # मुफ़्त AI इमेज यूआरएल
    ai_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
    
    fb_url = f"https://graph.facebook.com/{PAGE_ID}/photos"
    payload = {
        'url': ai_image_url,
        'caption': caption,
        'access_token': ACCESS_TOKEN
    }
    
    response = requests.post(fb_url, data=payload)
    
    if response.status_code == 200:
        print("AI Post successfully uploaded!")
    else:
        print("Failed to upload post:", response.text)

if __name__ == "__main__":
    generate_and_post()
