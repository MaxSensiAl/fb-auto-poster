import requests
import random
import os
import sys
import time
from datetime import datetime

# ============================================
# ENVIRONMENT VARIABLES (GitHub Secrets से आएंगे)
# ============================================
PAGE_ID = os.environ.get("FB_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

# ============================================
# HIGH QUALITY FLUX PROMPTS - (हमेशा फुल-बॉडी और रियलिस्टिक फोटो)
# ============================================
PERFECT_FACE_PROMPTS = [
    """Full-length portrait photograph of a beautiful Indian bride standing gracefully. She is wearing a traditional red designer lehenga with intricate gold embroidery. The shot shows her entire outfit from head to toe. Symmetrical gold wedding jewelry, a delicate maang tikka, matching earrings, and a small nose ring. Soft, glowing golden hour light illuminates the scene, showcasing natural skin texture with subtle film grain. The background is a soft-focus elegant palace corridor. Shot on 35mm film, Kodak Portra 400, authentic analog photography style.""",
    
    """Medium-full shot of a South Indian young woman wearing a rich green Kanjeevaram silk saree with a golden border. The photo shows her from the knees up, displaying the full drape of the saree. She is wearing traditional gold temple jewelry with perfectly identical earrings and has jasmine flowers in her hair. The background is a softly blurred traditional Kerala temple courtyard. Soft morning sunlight casting natural shadows, realistic skin pores, candid photo style.""",
    
    """Full-length fashion photograph of a modern Indian woman wearing an elegant pastel yellow crop top and a flowy designer ethnic skirt. She is standing outdoors with a blurred urban city background during sunset. The golden hour light reflects naturally on her skin. Her hands are resting on her waist, showcasing realistic fingers. The fabric of her skirt flows naturally with realistic drape and folds. Shot on a professional 50mm camera, high fidelity photo, no plastic look.""",
    
    """Full-body candid portrait of a beautiful Rajasthani woman in a vibrant, colorful bandhani outfit with intricate silver jewelry. She is standing in front of a majestic ancient haveli during the warm afternoon. The shot captures her entire dress, displaying natural folds in the fabric. The lighting highlights her sharp, symmetric facial features. Symmetrical identical earrings, authentic skin texture with natural pores, analog film look.""",
    
    """Full-length scenic portrait of a young Kashmiri woman wearing a traditional dark pheran with detailed colorful Kashmiri embroidery. She is standing in a snow-covered Gulmarg landscape, with the majestic mountains blurred in the background. Her face is clear with rosy cheeks and natural skin texture. Symmetrical silver earrings, natural clothing folds with accurate physics. Shot on a professional DSLR, authentic photo style.""",
    
    """Medium-full shot of a young Punjabi woman wearing a bright yellow Patiala salwar suit with a colorful phulkari dupatta. She is standing happily in a lush green mustard field under a clear blue sky. The camera captures her from the knees up, showing the full traditional suit. Natural bright sunlight, realistic eyes, natural skin texture, perfectly matched earrings, realistic fabric movement.""",
    
    """Full-length traditional portrait of a Bengali woman in a classic white saree with a thick red border (laal paar saree). She is wearing traditional gold bangles, perfectly matched symmetrical gold earrings, and is standing gracefully in front of a beautifully decorated Durga Puja pandal. Saree fabric drapes naturally to the ground, soft realistic lighting, analog photo quality.""",
    
    """Full-body fashion portrait of an Indian wedding guest in a pastel-colored designer anarkali suit. She is standing in a softly lit wedding venue with warm decorative lights in the background. The photo shows her entire outfit with elegant, natural folds. Sharp focus on her natural face, symmetrical delicate jewelry, authentic skin pores, shot on film style."""
]

# ============================================
# REAL PHOTO & DETAIL ENHANCER (CGI और प्लास्टिक लुक हटाने के लिए)
# ============================================
PHOTO_ENHANCE = """
, perfect facial symmetry, highly detailed eyes, natural skin texture with visible pores, subtle film grain, perfectly matched symmetrical identical earrings, natural soft fabric draping, realistic clothing folds with accurate physics, shot on 35mm film, analog photography, authentic photo, no CGI, no 3D render, no plastic look
"""

# ============================================
# SMART CAPTION GENERATOR
# ============================================
def generate_trending_caption():
    """समय के अनुसार स्मार्ट कैप्शन बनाएं"""
    hour = datetime.now().hour
    
    if 6 <= hour < 12:
        time_text = "🌅 Good Morning! Today's trending beauty"
    elif 12 <= hour < 17:
        time_text = "☀️ Afternoon glow"
    elif 17 <= hour < 21:
        time_text = "🌆 Evening elegance"
    else:
        time_text = "🌙 Night queen"
    
    captions = [
        f"""{time_text}
        
💃 Trending AI Girl - Inspired by today's top fashionistas!

🎯 Question: 1-10 में रेट करो ये लुक कितना ट्रेंडी है?
👇 कमेंट में बताओ - सबसे अच्छी चीज़ क्या लगी?

#TrendingGirl #AIFashionista #ViralFashion #IndianBeauty #TrendingStyle #FYP #ExplorePage #ViralReels #AIFashion #StyleInspo""",

        f"""{time_text}
        
✨ AI Generated - Trending Fashion Girl

💫 क्या आप ये आउटफिट पहनेंगी? हाँ/ना में बताओ!
💬 अपनी राय दें!

#AIGirl #FashionTrends #IndianFashion #ViralPost #OOTD #StyleGoals #AICreation #Explore #TrendingNow"""
    ]
    
    return random.choice(captions)

# ============================================
# 🎨 GENERATE IMAGE FROM HUGGING FACE
# ============================================
def generate_flux_image(prompt_text, filename="temp_output.jpg"):
    """Hugging Face API से FLUX.1-schnell मॉडल के जरिए इमेज बनाएं"""
    print("🎨 Generating High Quality Image via Hugging Face...")
    
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    payload = {
        "inputs": prompt_text,
        "parameters": {
            "width": 1080,
            "height": 1350
        }
    }
    
    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
            
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print("✅ Image generated and saved locally!")
                return filename
            elif response.status_code == 503:
                print("⏳ Model is loading on Hugging Face, waiting 15 seconds...")
                time.sleep(15)
            else:
                print(f"⚠️ Hugging Face Error ({response.status_code}): {response.text}")
                break
        except Exception as e:
            print(f"⚠️ Request Failed: {e}")
            time.sleep(5)
            
    return None

# ============================================
# 📤 POST DIRECT IMAGE FILE TO FACEBOOK
# ============================================
def post_local_file_to_facebook(image_path, caption):
    """फेसबुक ग्राफ एपीआई का उपयोग करके इमेज फ़ाइल अपलोड करें"""
    print("📤 Uploading direct image file to Facebook...")
    fb_url = f"https://graph.facebook.com/{PAGE_ID}/photos"
    
    payload = {
        'caption': caption,
        'access_token': ACCESS_TOKEN,
        'published': 'true'
    }
    
    try:
        with open(image_path, 'rb') as img_file:
            files = {
                'source': img_file
            }
            response = requests.post(fb_url, data=payload, files=files, timeout=120)
            
        if response.status_code == 200:
            post_id = response.json().get('id')
            print(f"✅ POST SUCCESSFUL! Post ID: {post_id}")
            return post_id
        else:
            print(f"❌ Facebook Upload Failed: {response.text}")
            return None
    except Exception as e:
        print(f"⚠️ Error uploading to Facebook: {e}")
        return None

# ============================================
# 🎯 COMPLETE WORKFLOW
# ============================================
def trending_girl_bot():
    """मुख्य वर्कफ़्लो"""
    if not PAGE_ID or not ACCESS_TOKEN or not HF_TOKEN:
        print("❌ ERROR: Required secrets are missing!")
        return False
        
    base_prompt = random.choice(PERFECT_FACE_PROMPTS)
    final_prompt = base_prompt + PHOTO_ENHANCE
    
    local_image = generate_flux_image(final_prompt)
    
    if not local_image:
        print("❌ Image generation failed!")
        return False
        
    caption = generate_trending_caption()
    post_id = post_local_file_to_facebook(local_image, caption)
    
    if os.path.exists(local_image):
        os.remove(local_image)
        
    if post_id:
        print("🎉 Successfully completed!")
        return True
    return False

if __name__ == "__main__":
    trending_girl_bot()
