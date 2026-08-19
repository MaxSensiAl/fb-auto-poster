import requests
import random
import os
import urllib.parse

PAGE_ID = os.environ.get("FB_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

# हर स्टाइल के लिए आकर्षक और साफ़-सुथरे कैप्शन्स
CAPTIONS = [
    "Embracing the elegance of traditional vibes. ✨ #tradition #indianwear #beauty #fashion #aesthetic",
    "Chasing dreams and making memories in style. 💫 #fashionblogger #lifestyle #photography #vibes",
    "Simplicity is the ultimate sophistication. 🌸 #simplestyle #portraits #aesthetic #model #casual",
    "Confidence is quiet, but style speaks volumes. 💃 #outfitoftheday #streetstyle #trending #fashion",
    "Finding beauty in every corner of the world. 🌍 #travelblogger #explorer #lifestyle #scenic",
    "Keep shining, beautiful world. 🌟 #positivity #ootd #aiart #photography #glow"
]

# 6 अलग-अलग हाई-आरपीएम और ट्रेंडिंग एआई स्टाइल्स (Prompts)
PROMPTS = [
    # 1. उत्तर भारतीय महल/ट्रेडिशनल लुक (शादियों और त्यौहारों के सीजन के लिए बेस्ट)
    "A highly detailed portrait of a beautiful Indian girl wearing an elegant red lehenga, delicate gold jewelry, smiling, indoor ancient palace background, warm golden lighting, 8k resolution, photorealistic",
    
    # 2. मॉडर्न वेस्टर्न/शरद ऋतु स्टाइल (प्रीमियम आरपीएम के लिए न्यू यॉर्क स्ट्रीट बैकग्राउंड)
    "A stylish young woman in a beige trench coat and a knitted scarf, walking on a clean city street in autumn, soft daylight, professional depth of field, photorealistic, elegant fashion, highly detailed",
    
    # 3. दक्षिण भारतीय सिल्क साड़ी लुक (फेसबुक पर सबसे लोकप्रिय और वायरल होने वाला लुक)
    "A gorgeous South Indian girl wearing a green silk saree with gold border, traditional temple jewelry, jasmine flowers in her hair, soft natural daylight, temple background, realistic, 8k resolution",
    
    # 4. ट्रेंडी स्ट्रीट स्टाइल/टोक्यो नियॉन लुक (युवा ऑडियंस के लिए बेहद आकर्षक)
    "A cool young female model wearing a modern denim jacket over a white tee, standing on a Tokyo street at night under neon signs, colorful reflections, bokeh effect, professional fashion photography, realistic",
    
    # 5. बीच ट्रेवल/सूर्यास्त लाइफस्टाइल लुक
    "A happy young woman in a white linen dress, enjoying a beautiful beach sunset, golden hour light reflecting on her face, wind blowing her hair, realistic candid lifestyle photography, detailed",
    
    # 6. ग्रामीण भारतीय सादगी/दुपट्टा लुक
    "A graceful Indian girl wearing a simple and colorful salwar kameez with dupatta, sitting near a rustic village background, soft morning sunlight, natural expression, highly detailed, realistic portrait"
]

def generate_and_post():
    selected_prompt = random.choice(PROMPTS)
    caption = random.choice(CAPTIONS)
    encoded_prompt = urllib.parse.quote(selected_prompt)
    
    # FLUX मॉडल के साथ सुपर क्वालिटी यूआरएल
    ai_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true&model=flux"
    
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
