import os
import sys
import time
import random
import requests
import urllib.parse
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# ============================================
# 🔐 GITHUB SECRETS से VARIABLES लें
# ============================================
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

# Check Credentials
if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
    print("❌ Facebook Credentials नहीं मिले!")
    sys.exit(1)

print(f"✅ Facebook Page ID: {FB_PAGE_ID[:5]}***")
print(f"✅ Facebook Token: {FB_ACCESS_TOKEN[:10]}...")

# ============================================
# 🌐 मजबूत नेटवर्क सेशन सेटअप
# ============================================
session = requests.Session()
retry_strategy = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    raise_on_status=False
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# ============================================
# 🎨 FACE-FOCUSED PROMPTS
# ============================================

PROMPTS = [
    """
    Close-up portrait of a gorgeous Indian bride, 
    symmetrical facial features, highly detailed realistic eyes, 
    perfect nose and lips, natural skin texture,
    traditional red bridal lehenga, soft golden hour lighting,
    8k resolution, photorealistic, sharp focus on face.
    """,
    """
    Close-up portrait of a stunning Bollywood actress,
    symmetrical face, detailed expressive eyes, natural skin,
    modern fusion wear, professional studio lighting,
    high fashion editorial style, sharp focus on face.
    """,
    """
    Close-up portrait of a South Indian woman,
    symmetrical facial features, clear realistic eyes,
    silk saree with gold border, temple jewelry,
    natural sunlight, sharp focus on face.
    """,
    """
    Close-up portrait of a royal Rajasthani woman,
    symmetrical face, detailed expressive eyes,
    traditional jewelry, golden hour lighting,
    sharp focus on face, majestic look.
    """,
    """
    Close-up portrait of a happy Indian woman celebrating festival,
    symmetrical facial features, joyful expression,
    traditional lehenga, festive warm lighting,
    sharp focus on face, vibrant colors.
    """
]

# ============================================
# 🎨 AI से PHOTO GENERATE करें
# ============================================

def generate_ai_image(filename="generated_photo.jpg"):
    """
    Pollinations AI से Face-Focused फोटो जनरेट करें
    """
    print("🎨 AI से Face-Focused फोटो बना रहा हूँ...")
    
    prompt = random.choice(PROMPTS)
    clean_prompt = prompt.strip().replace('\n', ' ').replace('  ', ' ')
    encoded_prompt = urllib.parse.quote(clean_prompt[:200])
    
    # Square Resolution - Face Distortion से बचाता है
    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1024"
        f"&model=flux"
        f"&nologo=true"
        f"&seed={random.randint(1, 9999999)}"
        f"&quality=high"
        f"&enhance=true"
    )
    
    try:
        print("⏳ 30-60 सेकंड लग सकते हैं...")
        response = session.get(url, timeout=180)
        
        if response.status_code == 200:
            content_size = len(response.content)
            if content_size > 50000:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ फोटो बन गई! ({content_size/1024:.1f} KB)")
                
                # Enhance Face
                enhance_face_quality(filename)
                return filename
            else:
                print(f"⚠️ फोटो बहुत छोटी है ({content_size} bytes)")
                return None
        else:
            print(f"❌ AI Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return None

def enhance_face_quality(image_path):
    """
    Face Enhancement - Natural Look
    """
    try:
        from PIL import Image, ImageEnhance
        
        img = Image.open(image_path)
        width, height = img.size
        print(f"📐 Resolution: {width}x{height}")
        
        # Square Crop - Face को Center में
        if width != height:
            new_size = min(width, height)
            left = (width - new_size) // 2
            top = (height - new_size) // 2
            img = img.crop((left, top, left + new_size, top + new_size))
        
        # हल्की Sharpness (Natural Look)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.05)
        
        # हल्का Contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.02)
        
        # High Quality Save
        img.save(image_path, quality=98, optimize=True, format='JPEG')
        print(f"✅ Face Enhanced!")
        return True
        
    except Exception as e:
        print(f"⚠️ Enhancement Error: {e}")
        return False

# ============================================
# 📝 CAPTION GENERATE
# ============================================

def generate_caption():
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

✨ AI Generated Perfect Look! 🤩

आपको कैसा लगा? 🤔
👇 Comment में बताओ:
❤️ - पसंद आया
💔 - नहीं पसंद

🎯 100+ Reactions = Next Look और भी Better!

#AIFashion #IndianBeauty #AIArt #ViralFashion #ExplorePage #FYP #StyleInspo #FashionGoals #AIModel #DigitalFashion #AIArtwork #ModernBride #IndianWear #FusionFashion #AIArtist #VirtualFashion #TechStyle #InstaFashion #DailyFashion #Fashionista #AICouture #VirtualInfluencer #IndianFashionBlogger #AIForFashion""",
        
        f"""{time_text}

🔥 AI ने बनाया ये Stunning Look! 💃

क्या आपको लगता है ये Real है या AI? 🤔
👇 3 Second mein comment karo:
1️⃣ Rate करो (1-10)
2️⃣ Sabse best kya hai?

💡 50+ Comments = Next Post Aaj Raat hi!

#AIBride #IndianWedding #AIArt #TrendingReels #ViralPost #FYP #ExplorePage #AIFashion #BridalWear #AICommunity #DigitalArt #AIInfluencer #AIModel #FashionAI #IndianFashion #BollywoodStyle #AIArtCommunity #ViralReels #InstagramReels #Explore #TrendingNow #AIContent #AIGirl #ArtificialIntelligence #TechFashion #FutureOfFashion #AIforIndia #IndianAI #DesiBride #ShaadiGoals"""
    ]
    
    return random.choice(captions)

# ============================================
# 📤 FACEBOOK POST
# ============================================

def post_to_facebook(image_path, caption):
    """
    Facebook Page पर फोटो पोस्ट करें
    """
    print("📤 Facebook पर पोस्ट कर रहा हूँ...")
    
    # ✅ Page ID को Clean करें (केवल Numbers)
    page_id = ''.join(filter(str.isdigit, FB_PAGE_ID))
    print(f"📌 Cleaned Page ID: {page_id}")
    
    fb_url = f"https://graph.facebook.com/{page_id}/photos"
    
    payload = {
        'caption': caption,
        'access_token': FB_ACCESS_TOKEN,
        'published': 'true'
    }
    
    try:
        if not os.path.exists(image_path) or os.path.getsize(image_path) < 100:
            print("❌ फोटो फ़ाइल इनवैलिड है!")
            return None
        
        with open(image_path, 'rb') as img_file:
            files = {'source': img_file}
            response = session.post(fb_url, data=payload, files=files, timeout=120)
        
        if response.status_code == 200:
            post_id = response.json().get('id')
            print(f"✅ पोस्ट हो गई! Post ID: {post_id}")
            return post_id
        else:
            print(f"❌ Facebook Error: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"⚠️ Facebook Error: {e}")
        return None

# ============================================
# 🧹 CLEANUP
# ============================================

def cleanup_files(*files):
    for file in files:
        if file and os.path.exists(file):
            try:
                os.remove(file)
                print(f"🧹 {file} डिलीट हो गया")
            except:
                pass

# ============================================
# 🚀 MAIN BOT
# ============================================

def main():
    print("\n" + "="*60)
    print("🚀 FACE-FOCUSED AI BOT START")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # STEP 1: AI से फोटो बनाएं
        print("\n🎨 STEP 1: AI से फोटो बना रहा हूँ...")
        image_path = generate_ai_image("face_focused_photo.jpg")
        
        if not image_path:
            print("❌ फोटो नहीं बन पाई!")
            return False
        
        # STEP 2: कैप्शन बनाएं
        print("\n📝 STEP 2: कैप्शन बना रहा हूँ...")
        caption = generate_caption()
        print(f"✅ कैप्शन तैयार ({len(caption)} अक्षर)")
        
        # STEP 3: Facebook पर पोस्ट करें
        print("\n📤 STEP 3: Facebook पर पोस्ट कर रहा हूँ...")
        post_id = post_to_facebook(image_path, caption)
        
        # STEP 4: क्लीनअप
        print("\n🧹 STEP 4: क्लीनअप...")
        cleanup_files(image_path)
        
        elapsed = time.time() - start_time
        
        if post_id:
            print("\n" + "="*60)
            print("🎉 SUCCESS! पोस्ट हो गई!")
            print(f"⏱️ कुल समय: {elapsed:.2f} सेकंड")
            print(f"📱 Post ID: {post_id}")
            print("="*60)
            return True
        else:
            print("\n❌ पोस्ट नहीं हो पाई!")
            return False
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================
# 🎯 EXECUTE
# ============================================

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
