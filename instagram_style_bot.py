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
# 🌐 GITHUB Actions के लिए IPv4-Force DNS पैच
# ============================================
import urllib3.util.connection as urllib3_connection
urllib3_connection.HAS_IPV6 = False

from playwright.sync_api import sync_playwright

# ============================================
# 🔐 GITHUB SECRETS से VARIABLES लें और साफ करें (.strip())
# ============================================
IG_USERNAME = os.environ.get("IG_USERNAME", "").strip()
IG_PASSWORD = os.environ.get("IG_PASSWORD", "").strip()
TARGET_PROFILE = os.environ.get("TARGET_PROFILE", "zaraso_phia").strip()
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "").strip()
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN", "").strip()
GEMINI_API = os.environ.get("GEMINI_API", "").strip()
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()

# Check Credentials
if not IG_USERNAME or not IG_PASSWORD:
    print("❌ Instagram Credentials नहीं मिले! लॉगिन सिस्टम के लिए यह आवश्यक है।")
    sys.exit(1)

if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
    print("❌ Facebook Credentials नहीं मिले!")
    sys.exit(1)

print(f"✅ Instagram Target: @{TARGET_PROFILE}")
print(f"✅ Instagram User: {IG_USERNAME[:3]}***")
print(f"✅ Cleaned Facebook Page ID: {FB_PAGE_ID[:4]}***")

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
# 🎨 MULTIPLE PROMPTS
# ============================================

PROMPTS = [
    "traditional red bridal lehenga Indian bride, arms down, highly detailed realistic face",
    "Bollywood actress in modern designer fusion wear, arms relaxed at sides",
    "South Indian woman in rich silk kanjivaram saree, traditional jewelry, realistic face",
    "royal Rajasthani woman in lehenga, standing gracefully",
    "modern Indian woman in elegant pastel saree, simple standing pose",
    "Indian woman celebrating festival in mirror-work lehenga",
    "beautiful Indian woman in wedding guest attire",
    "Kashmiri woman standing in traditional embroidered pheran"
]

def create_default_prompt():
    return random.choice(PROMPTS)

# ============================================
# 🔐 1. PLAYWRIGHT INSTAGRAM LOGIN & SCRAPE SYSTEM
# ============================================

def login_and_get_instagram_style(page):
    """
    इंस्टाग्राम पर लॉगिन करके टारगेट प्रोफाइल का नवीनतम पोस्ट चेक करना
    """
    print("\n🔐 [लॉगिन सिस्टम] इंस्टाग्राम वेब पर जा रहा हूँ...")
    page.goto("https://www.instagram.com/accounts/login/")
    
    try:
        # इनपुट लोड होने की प्रतीक्षा करें
        page.wait_for_selector('input[name="username"]', timeout=40000)
        
        # क्रेडेंशियल्स भरें
        page.fill('input[name="username"]', IG_USERNAME)
        page.fill('input[name="password"]', IG_PASSWORD)
        page.wait_for_timeout(1000)
        
        # लॉगिन बटन दबाएं
        page.click('button[type="submit"]')
        print("⏳ लॉगिन होने की प्रतीक्षा कर रहा हूँ (10 सेकंड)...")
        page.wait_for_timeout(10000)
        
        # पॉपअप्स को संभालना
        try:
            if page.locator("text=Not Now").is_visible():
                page.click("text=Not Now")
                page.wait_for_timeout(2000)
        except:
            pass
            
        print("✅ इंस्टाग्राम लॉगिन प्रक्रिया पूर्ण!")
        
        # टारगेट प्रोफाइल पर जाएं
        profile_url = f"https://www.instagram.com/{TARGET_PROFILE}/"
        print(f"🎯 टारगेट प्रोफाइल पर जा रहा हूँ: {profile_url}")
        page.goto(profile_url)
        page.wait_for_timeout(6000)
        
        # नवीनतम पोस्ट चेक करें
        try:
            print("🔍 नवीनतम पोस्ट खोलकर स्टाइल/कैप्शन चेक कर रहा हूँ...")
            first_post = page.locator('a[href^="/p/"]').first
            first_post.click()
            page.wait_for_timeout(5000)
            
            # कैप्शन टेक्स्ट निकालें
            caption_element = page.locator('article span').first
            caption_text = caption_element.inner_text()
            print(f"📝 नवीनतम पोस्ट का लाइव कैप्शन मिला: {caption_text[:150]}...")
            
            # क्लोज करें
            page.locator('svg[aria-label="Close"]').first.click()
            page.wait_for_timeout(2000)
            return caption_text
            
        except Exception as e:
            print(f"⚠️ नवीनतम पोस्ट चेक करने में त्रुटि (बायपास): {e}")
            
    except Exception as e:
        print(f"❌ लॉगिन या स्क्रैपिंग विफल: {e}")
        
    print("🔄 बैकअप के लिए लोकल डिफ़ॉल्ट प्रॉम्प्ट का उपयोग कर रहा हूँ...")
    return random.choice(PROMPTS)

# ============================================
# 🎨 2. MULTI-ENGINE GENERATOR (HF Mirror, Hercai V3, Pollinations)
# ============================================

def generate_ai_image_hf(prompt_text, model_id="black-forest-labs/FLUX.1-schnell", filename="generated_photo.jpg"):
    if not HF_TOKEN:
        return None
        
    print(f"🚀 Hugging Face Mirror ({model_id}) से कनेक्ट कर रहा हूँ...")
    api_url = f"https://api-inference.hf-mirror.com/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    payload = {
        "inputs": prompt_text,
        "parameters": {
            "width": 1024,
            "height": 1024
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
            print("✅ Hugging Face Mirror से प्रीमियम फोटो सफलतापूर्वक डाउनलोड हो गई!")
            return filename
    except Exception as e:
        print(f"❌ HF Mirror Error: {e}")
    return None


def generate_ai_hercai(prompt_text, filename="generated_photo.jpg"):
    print("🚀 [नया टूल] Hercai V3 (Stable Diffusion XL) से लाइव फोटो बना रहा हूँ...")
    url = "https://hercai.onrender.com/v3/hercai"
    
    payload = {
        "prompt": prompt_text,
        "model": "v3"  
    }
    
    try:
        response = session.post(url, json=payload, timeout=90)
        if response.status_code == 200:
            data = response.json()
            img_url = data.get("reply")
            
            if img_url:
                img_response = session.get(img_url, timeout=90)
                if img_response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(img_response.content)
                    print("✅ Hercai V3 से हाई-क्वालिटी फोटो डाउनलोड हो गई!")
                    return filename
    except Exception as e:
        print(f"❌ Hercai V3 जनरेशन विफल: {e}")
    return None


def generate_ai_image(prompt_text, filename="generated_photo.jpg"):
    # 1. पहला प्रयास: Flux.1-schnell (Hugging Face Mirror)
    image_path = generate_ai_image_hf(prompt_text, "black-forest-labs/FLUX.1-schnell", filename)
    if image_path:
        enhance_image_quality(image_path)
        return image_path
        
    # 2. दूसरा प्रयास: Hercai V3
    image_path = generate_ai_hercai(prompt_text, filename)
    if image_path:
        enhance_image_quality(image_path)
        return image_path

    # 3. तीसरा प्रयास: पोलिनेशंस बैकअप
    print("🔄 बैकअप पोलिनेशंस सर्वर पर स्विच कर रहा हूँ...")
    clean_prompt = prompt_text.strip().replace('\n', ' ').replace('  ', ' ')
    encoded_prompt = urllib.parse.quote(clean_prompt[:250])
    
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1024"  
        f"&model=flux-realism"  
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
            print("✅ पोलिनेशंस बैकअप से फोटो डाउनलोड हो गई!")
            enhance_image_quality(filename)
            return filename
    except Exception as e:
        print(f"❌ बैकअप सर्वर विफल: {e}")
        
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
    try:
        from PIL import Image, ImageEnhance
        
        img = Image.open(image_path)
        width, height = img.size
        print(f"📐 Current Resolution: {width}x{height}")
        
        if width < 1024 or height < 1024:
            new_width = 1024
            new_height = 1024
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.01)  
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.01)  
        
        img.save(image_path, quality=95, optimize=True, format='JPEG')
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
    # संस्करण विशिष्ट यूआरएल का उपयोग (Error 100 को पूरी तरह हल करने के लिए)
    fb_url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/photos"
    
    payload = {
        'caption': caption,
        'access_token': FB_ACCESS_TOKEN,
        'published': 'true'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
    }
    
    try:
        with open(image_path, 'rb') as img_file:
            files = {'source': img_file}
            response = session.post(fb_url, data=payload, files=files, headers=headers, timeout=120)
        
        if response.status_code == 200:
            post_id = response.json().get('id')
            print(f"✅ फेसबुक पोस्ट हो गई! Post ID: {post_id}")
            return post_id
        else:
            print(f"❌ Facebook Error: {response.text[:500]}")
            return None
    except Exception as e:
        print(f"⚠️ Facebook Error: {e}")
        return None

# ============================================
# 📸 5. INSTAGRAM पर POST करें (PLAYWRIGHT WEB SYSTEM)
# ============================================

def post_to_instagram_playwright(page, image_path, caption):
    """
    प्लेराइट के ज़रिए सीधे डेस्कटॉप व्यू से इंस्टाग्राम पर फोटो अपलोड करना
    """
    print("\n📤 [ऑटो-अपलोड] प्लेराइट ब्राउज़र के ज़रिए इंस्टाग्राम पर पोस्ट कर रहा हूँ...")
    try:
        page.goto("https://www.instagram.com/")
        page.wait_for_timeout(6000)
        
        # 'New Post' (+) बटन पर क्लिक करें
        create_btn = page.locator('svg[aria-label="New post"]').first
        create_btn.click()
        page.wait_for_timeout(4000)
        
        # इमेज अपलोड करें
        file_input = page.locator('input[type="file"]')
        file_input.set_input_files(image_path)
        page.wait_for_timeout(5000)
        
        # 'Next' बटन पर क्लिक करें (Crop स्क्रीन)
        page.click('div:has-text("Next")')
        page.wait_for_timeout(3000)
        
        # 'Next' बटन पर क्लिक करें (Filter स्क्रीन)
        page.click('div:has-text("Next")')
        page.wait_for_timeout(3000)
        
        # कैप्शन लिखें
        caption_textarea = page.locator('div[aria-label="Write a caption..."]')
        caption_textarea.fill(caption)
        page.wait_for_timeout(3000)
        
        # 'Share' बटन पर क्लिक करें
        page.click('div:has-text("Share")')
        print("⏳ पोस्ट पब्लिश हो रही है, कृपया 12 सेकंड प्रतीक्षा करें...")
        page.wait_for_timeout(12000)
        
        print("✅ इंस्टाग्राम पर प्लेराइट के ज़रिए पोस्ट सफलतापूर्वक साझा हो गई!")
        return True
    except Exception as e:
        print(f"❌ प्लेराइट इंस्टाग्राम पोस्टिंग विफल: {e}")
        return False

# ============================================
# 🧹 6. CLEANUP
# ============================================

def cleanup_files(*files):
    for file in files:
        if file and os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass

# ============================================
# 🚀 7. MAIN BOT
# ============================================

def main():
    print("\n" + "="*60)
    print("🚀 PLAYWRIGHT DESKTOP BOT START")
    print("="*60)
    
    start_time = time.time()
    
    try:
        with sync_playwright() as p:
            # हेडलेस क्रोमियम लॉन्च करें (Actions के लिए)
            browser = p.chromium.launch(headless=True)
            
            # कुकीज़ (cookies.json) सपोर्ट चेक करें (बाईपास करने के लिए सर्वश्रेष्ठ तरीका)
            cookies_path = "cookies.json"
            if os.path.exists(cookies_path):
                print("🍪 cookies.json मिल गया! इसका उपयोग करके सीधे लॉगिन कर रहा हूँ...")
                context = browser.new_context(
                    storage_state=cookies_path,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800}
                )
            else:
                # डेस्कटॉप व्यूपोर्ट सेट करें (लॉगिन लोकेटर एरर को हल करने के लिए)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800}
                )
                
            page = context.new_page()
            
            # STEP 1: इंस्टाग्राम लॉगिन और लाइव स्टाइल चेकिंग
            style_prompt = login_and_get_instagram_style(page)
            
            # STEP 2: परफेक्ट फोटो लाइव जनरेट करें
            image_path = generate_ai_image(style_prompt, "instagram_style_photo.jpg")
            
            if not image_path:
                print("❌ फोटो जनरेट या डाउनलोड नहीं हो पाई!")
                browser.close()
                return False
                
            # STEP 2.5: Quality Check
            if not check_image_quality(image_path):
                print("❌ Quality Check Fail!")
                browser.close()
                return False
            
            # STEP 3: कैप्शन बनाएं
            caption = generate_caption()
            
            # STEP 4: Facebook पर पोस्ट करें (Graph API)
            fb_post_id = post_to_facebook(image_path, caption)
            
            # STEP 5: Instagram पर सीधे ब्राउज़र के ज़रिए पोस्ट करें (प्लेराइट)
            ig_success = post_to_instagram_playwright(page, image_path, caption)
            
            # कुकीज़ सेव करें (ताकि अगली बार लॉगिन न करना पड़े)
            try:
                context.storage_state(path=cookies_path)
                print("🍪 भविष्य के लिए cookies.json अपडेट कर दी गई है!")
            except Exception as e:
                print(f"⚠️ कुकीज़ सेव करने में असमर्थ: {e}")
                
            browser.close()
            
        # STEP 6: क्लीनअप
        cleanup_files(image_path, "retry_photo.jpg", "placeholder_final.jpg")
        
        elapsed = time.time() - start_time
        print("\n" + "="*60)
        print(f"🎉 SUCCESS! कार्य संपन्न हुआ (समय: {elapsed:.2f}s)")
        print(f"📱 Facebook Post: {'✅ Success' if fb_post_id else '❌ Fail'}")
        print(f"📸 Instagram Post: {'✅ Success' if ig_success else '❌ Fail'}")
        print("="*60)
        
        return True if (fb_post_id or ig_success) else False
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
