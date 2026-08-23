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

if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
    print("❌ Facebook Credentials नहीं मिले!")
    sys.exit(1)

print(f"✅ Facebook Page ID: {FB_PAGE_ID[:5]}***")

# ============================================
# 🌐 Session Setup
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
# 🎨 ZARASO_PHIA STYLE PROMPTS
# ============================================

PROMPTS = [
    "Ultra HD 4K full body shot of a stunning Indian woman, unfiltered and unmatched look, natural beauty, glowing skin, wearing casual stylish outfit, city background, natural sunlight, candid pose, professional photography, hyper realistic, sharp focus on face and body, 8k resolution",
    "Ultra HD 4K full body shot of a fashionable Indian woman, OOTD style, wearing trendy fusion outfit, stylish accessories, urban background, street style photography, confident pose, natural lighting, sharp focus on outfit and face, professional photography, hyper realistic, 8k resolution",
    "Ultra HD 4K full body shot of an Indian woman in traditional desi wear, beautiful ethnic outfit, traditional jewelry, cultural background, warm golden lighting, graceful pose, natural beauty, sharp focus on face and outfit, professional photography, hyper realistic, 8k resolution",
    "Ultra HD 4K full body shot of a beautiful Indian woman in casual look, simple yet stylish outfit, natural makeup, glowing skin, outdoor background, natural sunlight, candid smile, relaxed pose, professional photography, hyper realistic, sharp focus on face and body, 8k resolution",
    "Ultra HD 4K full body shot of a modern Indian woman, contemporary fusion wear, elegant style, urban background, natural lighting, confident pose, sharp focus on face and outfit, professional photography, hyper realistic, 8k resolution",
    "Ultra HD 4K full body shot of an Indian woman, unfiltered beauty, natural look, no makeup, glowing skin, simple outfit, outdoor natural background, sunlight, candid pose, professional photography, hyper realistic, sharp focus on face, 8k resolution",
    "Ultra HD 4K full body shot of a stylish Indian woman, street fashion style, trendy outfit, cool accessories, city street background, natural lighting, confident pose, professional photography, hyper realistic, sharp focus on face and outfit, 8k resolution",
    "Ultra HD 4K full body shot of a desi Indian girl, traditional ethnic wear, beautiful jewelry, natural beauty, cultural background, warm lighting, graceful pose, professional photography, hyper realistic, sharp focus on face and outfit, 8k resolution",
    "Ultra HD 4K full body shot of a beautiful Indian woman on beach, stylish summer dress, natural beauty, glowing skin, white sand, blue ocean, golden hour lighting, candid pose, professional photography, hyper realistic, sharp focus on face and body, 8k resolution",
    "Ultra HD 4K full body shot of a modern city girl Indian woman, stylish outfit, urban background, natural lighting, confident pose, sharp focus on face and outfit, professional photography, hyper realistic, 8k resolution"
]

# ============================================
# 🎨 IMAGE GENERATION
# ============================================

def generate_ultra_hd_image(filename="ultra_hd_photo.jpg", max_retries=5):
    """
    ULTRA HD IMAGE GENERATE - zaraso_phia Style
    """
    print("🎨 zaraso_phia STYLE में ULTRA HD फोटो बना रहा हूँ...")
    
    for attempt in range(max_retries):
        try:
            prompt = random.choice(PROMPTS)
            enhanced_prompt = f"{prompt}, professional photography, hyper realistic, sharp focus, 8k resolution, photorealistic, cinematic lighting"
            
            clean_prompt = enhanced_prompt.strip().replace('\n', ' ').replace('  ', ' ')
            encoded_prompt = urllib.parse.quote(clean_prompt[:350])
            
            url = (
                f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                f"?width=1536&height=2048"
                f"&model=flux"
                f"&nologo=true"
                f"&seed={random.randint(1, 9999999)}"
                f"&quality=ultra"
                f"&enhance=true"
            )
            
            print(f"⏳ Attempt {attempt + 1}/{max_retries}: Generating ULTRA HD...")
            response = session.get(url, timeout=180)
            
            if response.status_code == 200:
                content_size = len(response.content)
                print(f"📊 Image Size: {content_size/1024:.1f} KB")
                
                if content_size > 50000:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ ULTRA HD फोटो बन गई! ({content_size/1024:.1f} KB)")
                    enhance_ultra_hd_image(filename)
                    return filename, prompt
                else:
                    print(f"⚠️ Image too small ({content_size/1024:.1f} KB), Retrying...")
                    time.sleep(3)
            else:
                print(f"❌ API Error: {response.status_code}, Retrying...")
                time.sleep(5)
                
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} Error: {e}")
            time.sleep(5)
    
    return generate_fallback_image(filename), "Fallback Image"

def generate_fallback_image(filename="fallback.jpg"):
    """Fallback Image"""
    try:
        prompt = "Beautiful Indian woman full body portrait, natural beauty, professional photography, 8k quality, sharp focus"
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1536&height=2048&model=flux&nologo=true&quality=ultra&enhance=true"
        response = session.get(url, timeout=180)
        
        if response.status_code == 200 and len(response.content) > 50000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Fallback Success! ({len(response.content)/1024:.1f} KB)")
            enhance_ultra_hd_image(filename)
            return filename
    except:
        pass
    
    return create_placeholder(filename)

def create_placeholder(filename="placeholder.jpg"):
    try:
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (1536, 2048), color=(255, 220, 240))
        draw = ImageDraw.Draw(img)
        draw.text((500, 900), "✨ ULTRA HD ✨", fill=(200, 50, 100))
        img.save(filename, quality=98)
        return filename
    except:
        with open(filename, 'wb') as f:
            f.write(b'ULTRA_HD_PLACEHOLDER')
        return filename

# ============================================
# 👤 IMAGE ENHANCEMENT
# ============================================

def enhance_ultra_hd_image(image_path):
    try:
        from PIL import Image, ImageEnhance
        
        img = Image.open(image_path)
        width, height = img.size
        print(f"📐 Current Resolution: {width}x{height}")
        
        if width != 1536 or height != 2048:
            print(f"📐 Resizing to 1536x2048...")
            img = img.resize((1536, 2048), Image.Resampling.LANCZOS)
        
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.3)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        
        img.save(image_path, quality=100, optimize=False, format='JPEG')
        new_size = os.path.getsize(image_path)
        print(f"✅ Enhanced! Size: {new_size/1024:.1f} KB")
        print(f"✅ Resolution: 1536x2048")
        return True
        
    except Exception as e:
        print(f"⚠️ Enhancement Error: {e}")
        return False

# ============================================
# 📝 CAPTION
# ============================================

def generate_caption():
    hour = datetime.now().hour
    if 6 <= hour < 12:
        time_text = "🌅 Good Morning!"
    elif 12 <= hour < 17:
        time_text = "☀️ Afternoon glow"
    elif 17 <= hour < 21:
        time_text = "🌆 Evening elegance"
    else:
        time_text = "🌙 Night queen"
    
    captions = [
        f"""{time_text}

✨ Unfiltered and unmatched ✨

Natural beauty, no filter needed 💫
📍 Somewhere in India 🇮🇳

👇 Comment में बताओ:
❤️ - पसंद आया
💔 - नहीं पसंद

#ootd #desivibes #instagood #indianbeauty #ultrahd #4kquality #aifashion #viralreels #explorepage #fyp #styleinspo #fashiongoals #aimodel #digitalfashion #aiartwork #indianwear #fusionfashion #aiartist #virtualfashion #techstyle #instafashion #dailyfashion #fashionista #aicouture #virtualinfluencer #indianfashionblogger #aiforfashion""",
        
        f"""{time_text}

💫 Unfiltered and unmatched 💫

Just raw, real and beautiful 🌟
📍 Dream Destination 🏖️

👇 3 Second mein comment karo:
1️⃣ Rate करो (1-10)
2️⃣ कहां घूमने जाना है?

#ootd #desivibes #instagood #indianbeauty #ultrahd #4kquality #aifashion #viralreels #explorepage #fyp #styleinspo #fashiongoals #aimodel #digitalfashion #aiartwork #indianwear #fusionfashion #aiartist #virtualfashion #techstyle #instafashion #dailyfashion #fashionista #aicouture #virtualinfluencer #indianfashionblogger #aiforfashion"""
    ]
    
    return random.choice(captions)

# ============================================
# 📤 FACEBOOK POST - FIXED
# ============================================

def post_to_facebook(image_path, caption):
    print("📤 Facebook पर ULTRA HD पोस्ट कर रहा हूँ...")
    
    page_id = ''.join(filter(str.isdigit, FB_PAGE_ID))
    url = f"https://graph.facebook.com/{page_id}/photos"
    
    # ✅ PRIVACY REMOVED - यही Fix है
    payload = {
        'access_token': FB_ACCESS_TOKEN,
        'caption': caption,
        'published': 'true'
    }
    
    try:
        with open(image_path, 'rb') as img:
            files = {'source': img}
            response = session.post(url, data=payload, files=files, timeout=180)
        
        if response.status_code == 200:
            post_id = response.json().get('id')
            print(f"✅ ULTRA HD पोस्ट हो गई! Post ID: {post_id}")
            
            time.sleep(3)
            verify_post(post_id)
            return post_id
        else:
            print(f"❌ Facebook Error: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"⚠️ Facebook Error: {e}")
        return None

def verify_post(post_id):
    url = f"https://graph.facebook.com/{post_id}"
    params = {
        'access_token': FB_ACCESS_TOKEN,
        'fields': 'id,message,is_published,permalink_url'
    }
    
    try:
        response = session.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Post Status:")
            print(f"  - Published: {data.get('is_published')}")
            print(f"  - Link: {data.get('permalink_url')}")
            return data
        return None
    except:
        return None

# ============================================
# 🚀 MAIN
# ============================================

def main():
    print("\n" + "="*60)
    print("🚀 ZARASO_PHIA STYLE ULTRA HD BOT")
    print("📸 Resolution: 1536x2048 (4K)")
    print("="*60)
    
    start_time = time.time()
    
    try:
        print("\n🎨 STEP 1: ULTRA HD फोटो बना रहा हूँ...")
        image_path, prompt = generate_ultra_hd_image("ultra_hd_photo.jpg")
        
        if not image_path:
            print("❌ फोटो नहीं बन पाई!")
            return False
        
        print("\n📝 STEP 2: कैप्शन बना रहा हूँ...")
        caption = generate_caption()
        
        print("\n📤 STEP 3: Facebook पर पोस्ट कर रहा हूँ...")
        post_id = post_to_facebook(image_path, caption)
        
        if os.path.exists(image_path):
            os.remove(image_path)
            print("🧹 Cleanup Done")
        
        elapsed = time.time() - start_time
        
        if post_id:
            print("\n" + "="*60)
            print("🎉 ULTRA HD POST SUCCESS!")
            print(f"📐 Resolution: 1536x2048 (4K)")
            print(f"⏱️ Time: {elapsed:.2f}s")
            print(f"📱 Post ID: {post_id}")
            print("="*60)
            return True
        else:
            print("\n❌ पोस्ट नहीं हो पाई!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
