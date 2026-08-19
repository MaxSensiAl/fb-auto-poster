import requests
import random
import os
import sys
import time
import urllib.parse
from datetime import datetime

# ============================================
# ENVIRONMENT VARIABLES (केवल फेसबुक सीक्रेट्स चाहिए)
# ============================================
PAGE_ID = os.environ.get("FB_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

# Check if credentials are set
if not PAGE_ID or not ACCESS_TOKEN:
    print("❌ ERROR: Facebook credentials (PAGE_ID / ACCESS_TOKEN) are missing!")
    sys.exit(1)

# ============================================
# OPTIMIZED MEDIUM-SHOT PROMPTS
# ============================================
PERFECT_FACE_PROMPTS = [
    """A stunning medium-close up portrait of a beautiful Indian bride. She is wearing traditional red bridal wear with highly detailed gold embroidery. Sharp focus on her symmetrical face and expressive clear eyes. Wearing a delicate gold maang tikka and matching earrings. Soft glowing studio light, realistic skin texture with subtle film grain, shot on 85mm lens, f/1.4, flawless cinematic photo.""",
    
    """Medium shot of a South Indian young woman wearing a rich green Kanjeevaram silk saree with a golden border, visible from waist up. She has jasmine flowers in her hair and wears traditional identical gold earrings. Traditional background with warm morning sunlight, natural skin pores, soft smile, highly detailed and realistic face.""",
    
    """Close-up fashion portrait of a modern Indian influencer girl wearing an elegant pastel yellow dress, looking at the camera with a soft smile. Blurred city lights in the background during golden hour. Symmetrical delicate jewelry, realistic skin texture, beautiful eyes, captured on a professional DSLR, highly realistic.""",
    
    """Medium portrait shot of a beautiful Rajasthani princess visible from waist up. She is wearing a vibrant colorful traditional outfit with intricate silver jewelry. Symmetrical identical silver earrings, flawless facial features, natural lighting, shot on 35mm film, analog photo style.""",
    
    """Close-up scenic portrait of a young Kashmiri woman wearing a traditional dark pheran with colorful embroidery. Beautiful rosy cheeks, detailed realistic eyes, snow-covered Gulmarg landscape blurred in the background. Natural soft daylight, highly realistic and authentic face texture.""",
    
    """Medium shot of a Bengali woman in a classic white saree with a red border, visible from the chest up. She is wearing traditional identical gold bangles and earrings, smiling gracefully. Durga Puja pandal background with warm festive lights, sharp focus on her clear and flawless face."""
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
# 🎨 GENERATE IMAGE FROM POLLINATIONS FLUX
# ============================================
def generate_flux_image(prompt_text, filename="temp_output.jpg"):
    """बिना किसी API Key के Pollinations FLUX इंजन से उच्च गुणवत्ता वाली इमेज बनाएं"""
    print("🎨 Generating Image via Pollinations FLUX Engine (No API Key Required)...")
    
    encoded_prompt = urllib.parse.quote(prompt_text.strip())
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1080&height=1350"
        f"&model=flux"
        f"&nologo=true"
        f"&seed={random.randint(1, 9999999)}"
    )
    
    try:
        response = requests.get(flux_url, timeout=90)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print("✅ Successfully generated via Pollinations FLUX!")
            return filename
        else:
            print(f"❌ API Failed with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        
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
    final_prompt = random.choice(PERFECT_FACE_PROMPTS)
    
    # Image Generation
    local_image = generate_flux_image(final_prompt)
    
    if not local_image:
        print("❌ Image generation failed!")
        return False
        
    # Posting to Facebook
    caption = generate_trending_caption()
    post_id = post_local_file_to_facebook(local_image, caption)
    
    # Clean up
    if os.path.exists(local_image):
        os.remove(local_image)
        
    if post_id:
        print("🎉 Workflow successfully completed without API Keys!")
        return True
    return False

if __name__ == "__main__":
    if not trending_girl_bot():
        sys.exit(1)
    sys.exit(0)
