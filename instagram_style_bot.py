import os
import sys
import time
import random
import requests
import urllib.parse
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from playwright.sync_api import sync_playwright

# ============================================
# 🔐 GITHUB SECRETS से VARIABLES लें
# ============================================
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
TARGET_PROFILE = os.environ.get("TARGET_PROFILE", "zaraso_phia")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
GEMINI_API = os.environ.get("GEMINI_API")
HF_TOKEN = os.environ.get("HF_TOKEN")

# Check Credentials
if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
    print("❌ Facebook Credentials नहीं मिले!")
    sys.exit(1)

print(f"✅ Target: @{TARGET_PROFILE}")
print(f"✅ Facebook Page: {FB_PAGE_ID[:3]}***")

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
# 🎨 FACE-FOCUSED PROMPTS (बेहतर चेहरे के लिए)
# ============================================

PROMPTS = [
    # 1. Traditional Indian Bride - Face Focus
    """
    Close-up portrait of a gorgeous Indian bride, 
    symmetrical facial features, highly detailed realistic eyes, 
    perfect nose and lips, natural skin texture with visible pores,
    traditional red bridal lehenga visible in frame,
    soft golden hour lighting, dreamy bokeh background,
    8k resolution, photorealistic, professional photography,
    Canon EOS R5, 85mm lens, f/1.4, sharp focus on face.
    """,
    
    # 2. Modern Bollywood Style - Face Focus
    """
    Close-up portrait of a stunning Bollywood actress,
    symmetrical face, detailed expressive eyes, natural skin texture,
    modern fusion wear, professional studio lighting,
    soft shadows, high fashion editorial style,
    Sony A7R IV, 50mm lens, f/1.8, sharp focus on face.
    """,
    
    # 3. South Indian Beauty - Face Focus
    """
    Close-up portrait of a South Indian woman,
    symmetrical facial features, clear realistic eyes, warm skin tone,
    silk saree with gold border visible, temple jewelry,
    natural sunlight, sharp focus on face,
    Nikon Z9, 85mm lens, vibrant colors.
    """,
    
    # 4. Royal Rajasthani Style - Face Focus
    """
    Close-up portrait of a royal Rajasthani woman,
    symmetrical face, detailed expressive eyes, natural skin,
    traditional jewelry, desert palace background,
    golden hour lighting, sharp focus on face,
    Leica M11, 50mm Summilux.
    """,
    
    # 5. Festival Special - Face Focus
    """
    Close-up portrait of a happy Indian woman celebrating,
    symmetrical facial features, joyful expression, detailed eyes,
    traditional lehenga, diya background,
    festive warm lighting, sharp focus on face,
    Canon EOS R3, 24-70mm lens.
    """,
    
    # 6. Wedding Guest - Face Focus
    """
    Close-up portrait of a beautiful woman in wedding guest attire,
    symmetrical face, natural skin texture, detailed eyes,
    elegant saree or lehenga, soft romantic lighting,
    dreamy background, sharp focus on face.
    """,
    
    # 7. Kashmiri Beauty - Face Focus
    """
    Close-up portrait of a Kashmiri woman,
    symmetrical facial features, clear realistic eyes, fair skin,
    traditional pheran, snow-capped mountains background,
    natural winter lighting, sharp focus on face,
    Nikon D850, 70-200mm lens.
    """,
    
    # 8. Ultra Realistic Face - Special
    """
    Ultra realistic close-up portrait of an Indian woman,
    hyper-detailed symmetrical facial features, 
    highly detailed realistic eyes with catchlights,
    natural skin texture, visible pores, perfect lighting,
    professional photography, 8k resolution,
    sharp focus on face, cinematic, photorealistic.
    """
]

def create_default_prompt():
    """Face-focused prompt with better quality"""
    return random.choice(PROMPTS)

# ============================================
# 📸 1. INSTAGRAM STYLE (Skip Login)
# ============================================

def learn_style_from_instagram():
    print(f"📸 Instagram Login Skip - Using Manual Style Prompts")
    print(f"🎯 Target Profile: @{TARGET_PROFILE}")
    selected_prompt = random.choice(PROMPTS)
    print(f"✅ Selected Prompt: {selected_prompt[:100]}...")
    return selected_prompt

# ============================================
# 🎨 2. AI से PHOTO GENERATE करें (Face Focus)
# ============================================

def generate_ai_image_hf(prompt_text, model_id="black-forest-labs/FLUX.1-schnell", filename="generated_photo.jpg"):
    """
    Hugging Face API का उपयोग करके प्रीमियम क्वालिटी फोटो जनरेट करें
    """
    if not HF_TOKEN:
        print("⚠️ HF_TOKEN नहीं मिला! बैकअप सर्वर का उपयोग कर रहा हूँ...")
        return None
        
    print(f"🚀 Hugging Face मॉडल ({model_id}) से फोटो बना रहा हूँ...")
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    payload = {
        "inputs": prompt_text,
        "parameters": {
            "width": 1024,
            "height": 1024  # ✅ Square - Face Distortion से बचाता है
        }
    }
    
    try:
        response = session.post(api_url, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 503:
            estimated_time = response.json().get("estimated_time", 20)
            print(f"⏳ मॉडल लोड हो रहा है, {estimated_time:.1f} सेकंड प्रतीक्षा कर रहा हूँ...")
            time.sleep(min(estimated_time, 30))
            response = session.post(api_url, headers=headers, json=payload, timeout=120)
            
        if response.status_code == 200 and len(response.content) > 10000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print("✅ Hugging Face से हाई-क्वालिटी फोटो डाउनलोड हो गई!")
            enhance_face_quality(filename)
            return filename
        else:
            print(f"❌ HF Model Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ HF Connection Error (Bypassed): {e}")
        return None

def generate_ai_image(prompt_text, filename="generated_photo.jpg"):
    """
    Face-Focused AI Image Generation
    """
    print("🎨 AI से Face-Focused फोटो बना रहा हूँ...")
    
    # 1. पहला प्रयास: Flux.1-schnell (Hugging Face)
    image_path = generate_ai_image_hf(prompt_text, "black-forest-labs/FLUX.1-schnell", filename)
    if image_path:
        return image_path
        
    # 2. दूसरा प्रयास: Pollinations (Square Resolution)
    print("🔄 Pollinations बैकअप पर स्विच कर रहा हूँ...")
    clean_prompt = prompt_text.strip().replace('\n', ' ').replace('  ', ' ')
    encoded_prompt = urllib.parse.quote(clean_prompt[:250])
    
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1024"  # ✅ Square = No Face Distortion
        f"&model=flux"
        f"&nologo=true"
        f"&seed={random.randint(1, 9999999)}"
        f"&quality=high"
        f"&enhance=true"
    )
    
    try:
        response = session.get(flux_url, timeout=180)
        if response.status_code == 200 and len(response.content) > 50000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print("✅ Pollinations से Face-Focused फोटो डाउनलोड हो गई!")
            enhance_face_quality(filename)
            return filename
    except Exception as e:
        print(f"❌ Pollinations Error: {e}")
    
    # 3. तीसरा प्रयास: Simple Fallback
    return generate_ai_image_face_fallback(filename)

def generate_ai_image_face_fallback(filename="generated_photo.jpg"):
    """
    Face-Focused Fallback - अगर AI Fail हो तो
    """
    print("🔄 Face-Focused Fallback...")
    
    face_prompts = [
        "Beautiful Indian woman portrait, close-up face, symmetrical features, high quality",
        "Stunning Indian bride close-up, detailed eyes, natural skin, professional photography",
        "Glamorous Bollywood actress portrait, sharp focus on face, studio lighting"
    ]
    
    simple_prompt = random.choice(face_prompts)
    encoded = urllib.parse.quote(simple_prompt)
    
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true&quality=high&enhance=true"
    
    try:
        response = session.get(url, timeout=180)
        if response.status_code == 200 and len(response.content) > 50000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Face-Fallback Success!")
            enhance_face_quality(filename)
            return filename
    except:
        pass
    
    return create_placeholder_image(filename)

def create_placeholder_image(filename="placeholder.jpg"):
    try:
        from PIL import Image
        img = Image.new('RGB', (1024, 1024), color=(255, 200, 230))
        img.save(filename)
        return filename
    except:
        with open(filename, 'wb') as f:
            f.write(b'PLACEHOLDER')
        return filename

# ============================================
# 👤 FACE ENHANCEMENT
# ============================================

def enhance_face_quality(image_path):
    """
    Face-Focused Image Enhancement - Face को Sharp और Natural रखें
    """
    try:
        from PIL import Image, ImageEnhance
        
        img = Image.open(image_path)
        width, height = img.size
        print(f"📐 Current Resolution: {width}x{height}")
        
        # 1. Square Resolution Maintain करें (Face Distortion से बचने के लिए)
        if width != height:
            new_size = min(width, height)
            print(f"📐 Cropping to Square: {new_size}x{new_size}")
            left = (width - new_size) // 2
            top = (height - new_size) // 2
            img = img.crop((left, top, left + new_size, top + new_size))
        
        # 2. Resolution बढ़ाएँ (Face Details के लिए)
        if width < 1024:
            new_size = 1024
            print(f"📐 Upscaling to {new_size}x{new_size}")
            img = img.resize((new_size, new_size), Image.Resampling.LANCZOS)
        
        # 3. ✅ Face के लिए हल्की Sharpness (Natural Look)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.05)  # 5% - Natural
        
        # 4. ✅ हल्का Contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.02)  # 2% - Natural
        
        # 5. ✅ हल्की Color Enhancement
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.02)  # 2% - Natural
        
        # 6. High Quality Save
        img.save(image_path, quality=98, optimize=True, format='JPEG')
        new_size = os.path.getsize(image_path)
        print(f"✅ Face Enhanced! Size: {new_size/1024:.1f} KB")
        return True
        
    except Exception as e:
        print(f"⚠️ Face Enhancement Error: {e}")
        return False

# ============================================
# 📷 PHOTO QUALITY CHECK
# ============================================

def check_image_quality(image_path):
    print("📷 Photo Quality Check कर रहा हूँ...")
    try:
        if not os.path.exists(image_path):
            return False
        
        file_size = os.path.getsize(image_path)
        if file_size < 10000:
            return False
        
        try:
            from PIL import Image
            img = Image.open(image_path)
            img.verify()
            return True
        except:
            return file_size > 10000
    except:
        return False

# ============================================
# 📝 3. CAPTION GENERATE करें (FIXED EMOJIS)
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
# 📤 4. FACEBOOK पर POST करें
# ============================================

def post_to_facebook(image_path, caption):
    print("📤 Facebook पर पोस्ट कर रहा हूँ...")
    fb_url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    
    payload = {
        'caption': caption,
        'access_token': FB_ACCESS_TOKEN,
        'published': 'true'
    }
    
    try:
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
# 🧹 5. CLEANUP
# ============================================

def cleanup_files(*files):
    for file in files:
        if file and os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass

# ============================================
# 🚀 6. MAIN BOT
# ============================================

def main():
    print("\n" + "="*60)
    print("🚀 FACE-FOCUSED AI BOT START")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # STEP 1: Style Select
        style_prompt = learn_style_from_instagram()
        
        # STEP 2: AI से Face-Focused फोटो बनाएं
        image_path = generate_ai_image(style_prompt, "face_focused_photo.jpg")
        
        if not image_path:
            print("❌ फोटो नहीं बन पाई!")
            return False
            
        # STEP 2.5: Quality Check
        if not check_image_quality(image_path):
            print("❌ Quality Check Fail!")
            return False
        
        # STEP 3: कैप्शन बनाएं
        caption = generate_caption()
        
        # STEP 4: Facebook पर पोस्ट करें
        post_id = post_to_facebook(image_path, caption)
        
        # STEP 5: क्लीनअप
        cleanup_files(image_path, "retry_photo.jpg", "placeholder_final.jpg")
        
        elapsed = time.time() - start_time
        if post_id:
            print(f"🎉 SUCCESS! पोस्ट आईडी: {post_id} (समय: {elapsed:.2f}s)")
            return True
        return False
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
