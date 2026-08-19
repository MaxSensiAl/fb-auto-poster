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
# 🌐 मजबूत नेटवर्क सेशन सेटअप (DNS/NameResolution Error को रोकने के लिए)
# ============================================
session = requests.Session()
retry_strategy = Retry(
    total=5,  # कुल 5 बार प्रयास करेगा
    backoff_factor=2,  # हर प्रयास के बीच थोड़ा समय बढ़ाएगा
    status_forcelist=[429, 500, 502, 503, 504],
    raise_on_status=False
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# ============================================
# 🎨 MULTIPLE PROMPTS (अत्यंत यथार्थवादी चेहरों के लिए)
# ============================================

PROMPTS = [
    # 1. Traditional Indian Bride
    """
    Knee-up portrait of a gorgeous Indian bride, standing pose, wearing a highly detailed traditional red lehenga.
    Hyper-realistic face, highly detailed symmetrical eyes, perfect nose and lips, natural realistic skin texture, photorealistic.
    Palace courtyard backdrop, soft cinematic lighting, dslr quality, award winning photography.
    """,
    
    # 2. Modern Bollywood Style
    """
    A stunning three-quarter fashion shot of a Bollywood actress standing elegantly in modern designer fusion wear.
    Highly detailed realistic facial features, perfect eyes, natural skin pores, symmetrical face, sharp focus on face.
    Studio background, professional lighting, realistic shadows, elegant pose.
    """,
    
    # 3. South Indian Beauty
    """
    A beautiful three-quarter standing portrait of a South Indian woman in a rich silk kanjivaram saree.
    Intricate gold border, traditional temple jewelry, jasmine flowers in hair.
    Flawless symmetrical face, realistic detailed eyes, natural warm skin, warm natural sunlight.
    """,
    
    # 4. Royal Rajasthani Style
    """
    A royal Rajasthani woman standing in a palace courtyard, knee-up shot.
    Detailed traditional lehenga and silver jewelry.
    Symmetrical face, perfect realistic eyes, natural skin texture, majestic look.
    Warm sunset lighting, dslr quality, highly detailed.
    """,
    
    # 5. Modern Minimalist
    """
    Modern Indian woman standing elegantly, knee-up shot in a simple pastel designer saree.
    Clean symmetrical face, realistic eyes, natural skin, subtle jewelry.
    Minimalist modern background, soft natural daylight, contemporary style, photorealistic.
    """,
    
    # 6. Festival Special
    """
    A happy Indian woman celebrating festival, knee-up shot wearing a detailed traditional lehenga.
    Vibrant colors, happy realistic expression, symmetrical face, detailed eyes.
    Background decorated with glowing traditional oil lamps (diyas), festive warm light.
    """,
    
    # 7. Wedding Guest Look
    """
    A beautiful Indian woman in wedding guest attire, three-quarter standing shot showing designer anarkali wear.
    Symmetrical facial features, highly detailed realistic eyes, natural skin structure.
    Soft romantic lighting, elegant wedding hall background with gentle bokeh, dslr photography.
    """,
    
    # 8. Kashmiri Beauty
    """
    A Kashmiri woman standing gracefully, knee-up shot in a traditional embroidered pheran.
    Symmetrical face, highly detailed realistic eyes, natural fair skin.
    Snowy mountains background, soft winter sunlight, realistic textures, sharp focus.
    """
]

def create_default_prompt():
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
# 🎨 2. HUGGING FACE से PHOTO GENERATE करें (High Quality)
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
            "height": 1024  # स्थिर वर्गाकार रेशियो (सर्वश्रेष्ठ चेहरे के लिए)
        }
    }
    
    try:
        response = session.post(api_url, headers=headers, json=payload, timeout=120)
        
        # यदि मॉडल लोड हो रहा है, तो प्रतीक्षा करें
        if response.status_code == 503:
            estimated_time = response.json().get("estimated_time", 20)
            print(f"⏳ मॉडल लोड हो रहा है, {estimated_time:.1f} सेकंड प्रतीक्षा कर रहा हूँ...")
            time.sleep(min(estimated_time, 30))
            response = session.post(api_url, headers=headers, json=payload, timeout=120)
            
        if response.status_code == 200 and len(response.content) > 10000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print("✅ Hugging Face से हाई-क्वालिटी फोटो डाउनलोड हो गई!")
            return filename
        else:
            print(f"❌ HF Model Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ HF Connection Error (Bypassed): {e}")
        return None

def generate_ai_image(prompt_text, filename="generated_photo.jpg"):
    """
    मल्टी-मॉडल एआई जनरेशन सिस्टम (पहले HF, फिर Fallback)
    """
    # 1. पहला प्रयास: Flux.1-schnell (Hugging Face)
    image_path = generate_ai_image_hf(prompt_text, "black-forest-labs/FLUX.1-schnell", filename)
    if image_path:
        enhance_image_quality(image_path)
        return image_path
        
    # 2. दूसरा प्रयास (Fallback 1): RealVisXL V4.0 (वास्तविक चेहरों के लिए)
    image_path = generate_ai_image_hf(prompt_text, "SG161222/RealVisXL_V4.0", filename)
    if image_path:
        enhance_image_quality(image_path)
        return image_path

    # 3. तीसरा प्रयास (Fallback 2): पोलिनेशंस बैकअप (सुरक्षित 1024x1024 रेशियो)
    print("🔄 बैकअप पोलिनेशंस सर्वर पर स्विच कर रहा हूँ...")
    clean_prompt = prompt_text.strip().replace('\n', ' ').replace('  ', ' ')
    encoded_prompt = urllib.parse.quote(clean_prompt[:250])
    
    # चेहरे को बिल्कुल साफ रखने के लिए परफेक्ट 1024x1024 आकार
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1024"  # वर्गाकार आकार चेहरे को विकृत होने से पूरी तरह बचाता है
        f"&model=flux"
        f"&nologo=true"
        f"&seed={random.randint(1, 9999999)}"
        f"&quality=high"
        f"&enhance=false"
    )
    
    try:
        response = session.get(flux_url, timeout=120)
        if response.status_code == 200 and len(response.content) > 50000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print("✅ पोलिनेशंस बैकअप से स्थिर फोटो डाउनलोड हो गई!")
            enhance_image_quality(filename)
            return filename
    except Exception as e:
        print(f"❌ बैकअप सर्वर भी विफल रहा: {e}")
        
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
# 🖼️ IMAGE ENHANCE
# ============================================

def enhance_image_quality(image_path):
    """
    Image Quality Enhance
    """
    try:
        from PIL import Image, ImageEnhance
        
        img = Image.open(image_path)
        width, height = img.size
        print(f"📐 Current Resolution: {width}x{height}")
        
        if width < 1024 or height < 1024:
            new_width = 1024
            new_height = 1024
            print(f"📐 Resizing: {width}x{height} → {new_width}x{new_height}")
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # शार्पनेस को पूरी तरह से प्राकृतिक रखा गया है ताकि चेहरे के पिक्सल्स न बिगड़ें
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.02)  
        
        # कॉन्ट्रास्ट को भी बहुत हल्का रखा गया है
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.02)  
        
        # High Quality Save
        img.save(image_path, quality=95, optimize=True, format='JPEG')
        new_size = os.path.getsize(image_path)
        print(f"✅ Enhanced! New Size: {new_size/1024:.1f} KB")
        return True
        
    except Exception as e:
        print(f"⚠️ Enhancement Error: {e}")
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
            files = {'source': img_file: 'image/jpeg'}
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
    print("🚀 INSTAGRAM STYLE AI BOT START (BYPASS & NETWORK FIXED)")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # STEP 1: Style Select
        style_prompt = learn_style_from_instagram()
        
        # STEP 2: AI से फोटो बनाएं
        image_path = generate_ai_image(style_prompt, "instagram_style_photo.jpg")
        
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
