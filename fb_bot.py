import os
import sys
import random
import requests
import base64
from datetime import datetime

# ============================================
# ENVIRONMENT VARIABLES
# ============================================
PAGE_ID = os.environ.get("FB_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
GEMINI_API = os.environ.get("GEMINI_API")

if not GEMINI_API:
    print("❌ ERROR: GEMINI_API Key is missing in environment variables!")
    sys.exit(1)

# ============================================
# ULTRA-REALISTIC IMAGEN 3 PROMPTS (No Distortion)
# ============================================
PERFECT_FACE_PROMPTS = [
    """A full-length photography of a beautiful Indian bride standing elegantly in a royal palace corridor. She is wearing a traditional red designer lehenga with highly detailed gold embroidery. Complete outfit visible from head to toe. She wears perfectly matched symmetrical gold wedding jewelry, a delicate maang tikka, and matching earrings. Soft glowing natural lighting, detailed skin texture, captured on a professional DSLR camera, highly realistic, flawless face, cinematic.""",
    
    """A medium-full shot of a beautiful South Indian young woman wearing a rich green Kanjeevaram silk saree with a golden border. Showing her from the knees up, displaying the elegant drape of the saree. Symmetrical gold temple jewelry, jasmine flowers in her hair. Traditional temple background with soft morning sunlight, realistic skin pores, natural look, perfect face.""",
    
    """A full-length fashion photograph of a modern Indian influencer girl wearing an elegant pastel yellow crop top and a flowy designer ethnic skirt. Standing outdoors with a blurred urban city background during sunset, warm natural lighting on her skin, realistic hands, perfect body proportions, shot on 35mm film, authentic photo style.""",
    
    """A full-body candid portrait of a beautiful Rajasthani woman in a vibrant, colorful bandhani outfit with intricate silver jewelry. Standing in a majestic ancient haveli courtyard during the warm afternoon. The camera captures her complete dress, realistic fabric folds, symmetrical identical earrings, flawless facial features, natural daylight.""",
    
    """A full-length portrait of a beautiful young Kashmiri woman wearing a traditional dark pheran with detailed colorful embroidery. Standing in a snow-covered Gulmarg landscape with blurred mountains in the background. Highly detailed face, rosy cheeks, realistic eyes, natural clothing folds, high fidelity photography.""",
    
    """A traditional full-length portrait of a Bengali woman in a classic white saree with a thick red border (laal paar saree). Wearing traditional identical gold bangles and earrings, standing gracefully in front of a decorated Durga Puja pandal. Saree fabric drapes naturally to the ground, soft realistic lighting, authentic photo."""
]

# ============================================
# SMART CAPTION GENERATOR
# ============================================
def generate_trending_caption():
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

🎯 Question: 1-10 में rate karo ye look kitna trendy hai?
👇 Comment me batao - sabse acchi cheez kya lagi?

#TrendingGirl #AIFashionista #ViralFashion #IndianBeauty #TrendingStyle #FYP #ExplorePage #ViralReels #AIFashion #StyleInspo""",

        f"""{time_text}
        
✨ AI Generated - Trending Fashion Girl

💫 Kya aap ye outfit pehnengi? Haan/Na me batao!
💬 Apni rai niche comment me dein!

#AIGirl #FashionTrends #IndianFashion #ViralPost #OOTD #StyleGoals #AICreation #Explore #TrendingNow"""
    ]
    return random.choice(captions)

# ============================================
# 🎨 GENERATE IMAGE FROM GOOGLE IMAGEN 3 (DIRECT REST API)
# ============================================
def generate_imagen_3_image(prompt_text, filename="temp_output.jpg"):
    """Google Imagen 3 API को सीधे कॉल करके इमेज जनरेट करें (No Library Required)"""
    print("🎨 Generating Ultra-Realistic Image via Google Imagen 3 Direct API...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:generateImages?key={GEMINI_API}"
    
    payload = {
        "prompt": prompt_text,
        "numberOfImages": 1,
        "aspectRatio": "3:4",  # बेस्ट पोर्ट्रेट आकार
        "outputMimeType": "image/jpeg"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            # Base64 इमेज डेटा को डिकोड करके फाइल में सेव करें
            image_b64 = data['generatedImages'][0]['image']['imageBytes']
            image_bytes = base64.b64decode(image_b64)
            
            with open(filename, 'wb') as f:
                f.write(image_bytes)
                
            print("✅ Successfully generated via Google Imagen 3 REST API!")
            return filename
        else:
            print(f"❌ Google API Error ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ Direct API Request Failed: {e}")
        
    return None

# ============================================
# 📤 POST DIRECT IMAGE FILE TO FACEBOOK
# ============================================
def post_local_file_to_facebook(image_path, caption):
    print("📤 Uploading direct image file to Facebook...")
    fb_url = f"https://graph.facebook.com/{PAGE_ID}/photos"
    
    payload = {
        'caption': caption,
        'access_token': ACCESS_TOKEN,
        'published': 'true'
    }
    
    try:
        with open(image_path, 'rb') as img_file:
            files = {'source': img_file}
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
    if not PAGE_ID or not ACCESS_TOKEN:
        print("❌ ERROR: Facebook credentials (PAGE_ID, ACCESS_TOKEN) are missing!")
        return False
        
    final_prompt = random.choice(PERFECT_FACE_PROMPTS)
    
    # सीधे API से इमेज बनाएं
    local_image = generate_imagen_3_image(final_prompt)
    
    if not local_image:
        print("❌ Image generation failed!")
        return False
        
    caption = generate_trending_caption()
    post_id = post_local_file_to_facebook(local_image, caption)
    
    if os.path.exists(local_image):
        os.remove(local_image)
        
    if post_id:
        print("🎉 Workflow successfully completed using Google Imagen 3 API!")
        return True
    return False

if __name__ == "__main__":
    trending_girl_bot()
