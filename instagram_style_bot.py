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
# 🔐 GITHUB SECRETS से VARIABLES लें
# ============================================
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
TARGET_PROFILE = os.environ.get("TARGET_PROFILE", "zaraso_phia")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
GEMINI_API = os.environ.get("GEMINI_API")
HF_TOKEN = os.environ.get("HF_TOKEN")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN") 

if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
    print("❌ Facebook Credentials नहीं मिले!")
    sys.exit(1)

print(f"Target Profile: @{TARGET_PROFILE}")
print(f"Facebook Page: {FB_PAGE_ID[:3]}***")

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
# 🧠 GEMINI AI से INSTAGRAM स्टाइल प्रॉम्प्ट बनाना
# ============================================
def generate_prompt_via_gemini(instagram_caption):
    if not GEMINI_API:
        return None
    print("🧠 Gemini AI से Instagram कैप्शन के आधार पर रियल-स्टाइल प्रॉम्प्ट बना रहा हूँ...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API}"
    headers = {"Content-Type": "application/json"}
    
    prompt_to_gemini = (
        f"Analyze this Instagram post description: '{instagram_caption}'. "
        "Create a highly detailed image generation prompt for a photorealistic Indian woman in a waist-up pose. "
        "Ensure the prompt focus on sharp symmetrical facial features, realistic natural skin texture, clear eyes, and elegant traditional/fusion attire matching the style of the caption. "
        "Only output the prompt text in English. Do not add any introduction or conversational words."
    )
    
    payload = {
        "contents": [{"parts": [{"text": prompt_to_gemini}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            generated_text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ Gemini जनरेटेड प्रॉम्प्ट: {generated_text[:150]}...")
            return generated_text.strip()
    except Exception as e:
        print(f"⚠️ Gemini API कॉल विफल: {e}")
    return None

# ============================================
# 📸 PLAYWRIGHT INSTAGRAM SCRAPER
# ============================================
PROMPTS = [
    "A stunning high-quality waist-up portrait of an Indian bride standing gracefully, showing her traditional red bridal wear down to the waist. Symmetrical facial features, realistic skin, dslr.",
    "A glamorous waist-up fashion editorial shot of a Bollywood actress, showing her modern designer fusion wear. Natural skin structure, professional studio lighting, symmetrical face, photorealistic."
]

def learn_style_from_instagram():
    print(f"🎯 Target Profile: @{TARGET_PROFILE}")
    if not IG_USERNAME or not IG_PASSWORD:
        print("⚠️ Instagram Credentials नहीं मिले! फ़ॉलबैक प्रॉम्ट्स का उपयोग कर रहा हूँ...")
        return random.choice(PROMPTS)
        
    print("🚀 Playwright द्वारा Instagram पर लॉगिन और स्क्रैपिंग प्रारंभ...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-gpu", "--no-sandbox"])
            context = browser.new_context(
                viewport={"width": 390, "height": 844},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
            )
            page = context.new_page()
            
            # लॉगिन प्रक्रिया
            print("🔑 Instagram लॉगिन पेज खोल रहा हूँ...")
            page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle", timeout=60000)
            time.sleep(3)
            
            if page.locator("input[name='username']").is_visible():
                page.fill("input[name='username']", IG_USERNAME)
                page.fill("input[name='password']", IG_PASSWORD)
                time.sleep(1)
                page.click("button[type='submit']")
                print("⏳ लॉगिन विवरण सबमिट किए गए...")
                time.sleep(10)
                
            # प्रोफाइल पर जाना
            target_url = f"https://www.instagram.com/{TARGET_PROFILE}/"
            print(f"🎯 Target प्रोफाइल लोड हो रहा है: {target_url}")
            page.goto(target_url, wait_until="networkidle", timeout=60000)
            time.sleep(5)
            
            posts = page.locator("a[href*='/p/']").all()
            if posts:
                print("📸 नवीनतम पोस्ट मिल गई! डिटेल्स एक्सट्रैक्ट कर रहा हूँ...")
                posts[0].click()
                time.sleep(4)
                
                caption_text = ""
                spans = page.locator("article span").all()
                for span in spans[:5]:
                    text = span.inner_text()
                    if text and len(text) > 12:
                        caption_text = text
                        break
                        
                print(f"📝 कैप्शन मिला: {caption_text[:80]}...")
                
                if GEMINI_API and caption_text:
                    generated_prompt = generate_prompt_via_gemini(caption_text)
                    if generated_prompt:
                        browser.close()
                        return generated_prompt
                
                if caption_text:
                    browser.close()
                    return f"A realistic portrait of an Indian woman inspired by: {caption_text[:120]}. Waist-up, photorealistic, sharp focus on face, symmetrical eyes."
            else:
                print("⚠️ पोस्ट ढूंढने में असमर्थ (शायद प्राइवेट अकाउंट या लॉगिन वॉल है)।")
            browser.close()
    except Exception as e:
        print(f"⚠️ Playwright स्क्रैपिंग त्रुटि: {e}")
        
    print("🔄 फ़ॉलबैक: रैंडम प्रॉम्प्ट का चयन किया जा रहा है...")
    return random.choice(PROMPTS)

# ============================================
# ☁️ इमेज को सुरक्षित क्लाउड पर अपलोड करना
# ============================================
def upload_image_to_cloud(image_path):
    print("⏳ Catbox.moe पर सुरक्षित अपलोड प्रारंभ...")
    try:
        url = "https://catbox.moe/user/api.php"
        files = {
            'reqtype': (None, 'fileupload'),
            'fileToUpload': open(image_path, 'rb')
        }
        response = requests.post(url, files=files, timeout=45)
        if response.status_code == 200 and response.text.startswith("https://"):
            print("✅ Catbox डायरेक्ट लिंक तैयार है!")
            return response.text.strip()
    except Exception as e:
        print(f"⚠️ Catbox अपलोड विफल: {e}")

    print("⏳ Tmpfiles.org पर फॉलबैक अपलोड प्रारंभ...")
    try:
        with open(image_path, 'rb') as f:
            response = session.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=45)
        if response.status_code == 200:
            data = response.json()
            file_url = data.get("data", {}).get("url")
            direct_url = file_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
            print("✅ Tmpfiles डायरेक्ट लिंक तैयार है!")
            return direct_url
    except Exception as e:
        print(f"⚠️ Tmpfiles अपलोड विफल: {e}")
    return None

# ============================================
# 🎭 REPLICATE FACE RESTORE (GFPGAN Only to Prevent 429 Rate Limit)
# ============================================
def restore_face_replicate(image_url, filename="generated_photo.jpg"):
    if not REPLICATE_API_TOKEN:
        print("⚠️ REPLICATE_API_TOKEN नहीं मिला! रीस्टोरेशन बाईपास हो रहा है...")
        return False
        
    print("🚀 Replicate GFPGAN v1.4 से चेहरा रीस्टोर किया जा रहा है...")
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 429 एरर से बचने के लिए सीधा और विश्वसनीय GFPGAN v1.4 मॉडल रन करें
    payload = {
        "version": "92836085e34d856012c05f1890d6d405ab8854b0c400b8296996b7cd3d02f2b1",
        "input": {
            "img": image_url,
            "version": "v1.4",
            "scale": 2
        }
    }
    
    try:
        response = session.post("https://api.replicate.com/v1/predictions", headers=headers, json=payload, timeout=60)
        
        # यदि 429 (रेट लिमिट) त्रुटि मिलती है, तो 12 सेकंड प्रतीक्षा करके पुनः प्रयास करें
        if response.status_code == 429:
            print("⏳ API रेट लिमिट आ गई है। 12 सेकंड प्रतीक्षा कर रहा हूँ...")
            time.sleep(12)
            response = session.post("https://api.replicate.com/v1/predictions", headers=headers, json=payload, timeout=60)

        if response.status_code != 201:
            print(f"❌ Replicate API Error: Code {response.status_code} - {response.text[:200]}")
            return False

        prediction = response.json()
        poll_url = prediction["urls"]["get"]
        
        print("⏳ चेहरे के पिक्सल को ठीक किया जा रहा है...")
        for _ in range(30):
            time.sleep(2)
            status_resp = session.get(poll_url, headers=headers, timeout=30)
            if status_resp.status_code == 200:
                status_data = status_resp.json()
                status = status_data.get("status")
                if status == "succeeded":
                    output_url = status_data.get("output")
                    if isinstance(output_url, list):
                        output_url = output_url[0]
                    img_resp = session.get(output_url, timeout=60)
                    if img_resp.status_code == 200:
                        with open(filename, 'wb') as f:
                            f.write(img_resp.content)
                        print("🎉 सफलता! चेहरा रीस्टोर और साफ़ हो गया!")
                        return True
                elif status in ["failed", "canceled"]:
                    print(f"❌ Replicate प्रक्रिया विफल: {status}")
                    break
    except Exception as e:
        print(f"❌ फेस रीस्टोरेशन एरर: {e}")
    return False

# ============================================
# 🎨 MULTI-ENGINE GENERATOR
# ============================================
def generate_ai_image_hf(prompt_text, model_id="playgroundai/playground-v2.5-1024px-aesthetic", filename="generated_photo.jpg"):
    if not HF_TOKEN:
        return None
    print(f"🚀 Hugging Face से जनरेट कर रहा हूँ...")
    api_url = f"https://api-inference.hf-mirror.com/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt_text, "parameters": {"width": 1024, "height": 1024}}
    try:
        response = session.post(api_url, headers=headers, json=payload, timeout=120)
        if response.status_code == 200 and len(response.content) > 10000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
    except:
        pass
    return None

def generate_ai_hercai(prompt_text, filename="generated_photo.jpg"):
    print("🚀 Hercai V3 से जनरेट कर रहा हूँ...")
    url = "https://hercai.onrender.com/v3/hercai"
    payload = {
        "prompt": prompt_text + ", photorealistic portrait, sharp focus face, symmetrical realistic eyes, 8k resolution",
        "model": "v3"  
    }
    try:
        response = session.post(url, json=payload, timeout=90)
        if response.status_code == 200:
            img_url = response.json().get("reply")  
            if img_url:
                img_response = session.get(img_url, timeout=90)
                if img_response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(img_response.content)
                    return filename
    except:
        pass
    return None

def generate_ai_image(prompt_text, filename="generated_photo.jpg"):
    print("\n🎨 [इमेज जनरेटर] प्रक्रिया शुरू हो रही है...")
    image_path = generate_ai_image_hf(prompt_text, "playgroundai/playground-v2.5-1024px-aesthetic", filename)
    if image_path:
        return image_path
        
    image_path = generate_ai_hercai(prompt_text, filename)
    if image_path:
        return image_path

    print("🔄 [लेयर 3] पोलिनेशंस बैकअप सर्वर...")
    clean_prompt = prompt_text.strip().replace('\n', ' ').replace('  ', ' ')
    encoded_prompt = urllib.parse.quote(clean_prompt[:250])
    flux_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1280&model=flux-realism&nologo=true&quality=high"
    try:
        response = session.get(flux_url, timeout=120)
        if response.status_code == 200 and len(response.content) > 50000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
    except:
        pass
    return create_placeholder_image(filename)

def generate_ai_image_simple(filename="generated_photo.jpg"):
    simple_prompt = "Stunning Indian woman standing gracefully, waist-up portrait, detailed attire, realistic skin, sharp focus"
    return generate_ai_image(simple_prompt, filename)

def create_placeholder_image(filename="placeholder.jpg"):
    backup_prompt = "Beautiful Indian woman, waist-up portrait, realistic face, sharp focus"
    encoded = urllib.parse.quote(backup_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1280&model=flux-realism&nologo=true&quality=high"
    try:
        response = requests.get(url, timeout=120)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
    except:
        pass
    return filename

# ============================================
# 🖼️ IMAGE ENHANCE
# ============================================
def enhance_image_quality(image_path):
    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps
        
        img = Image.open(image_path)
        print(f"📐 Original Resolution: {img.size[0]}x{img.size[1]}")
        
        target_width = 1536
        target_height = 1920
        print(f"📐 Fitting image to: {target_width}x{target_height} (बिना विकृति के)")
        img = ImageOps.fit(img, (target_width, target_height), Image.Resampling.LANCZOS)
        
        img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=100, threshold=3))
        
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(1.05)
        
        sharp_enhancer = ImageEnhance.Sharpness(img)
        img = sharp_enhancer.enhance(1.15)
        
        img.save(image_path, quality=95, optimize=True, format='JPEG')
        print(f"✅ एन्हांसमेंट सफलतापूर्वक पूरा हुआ! फाइल साइज: {os.path.getsize(image_path)/1024:.1f} KB")
        return True
    except Exception as e:
        print(f"⚠️ Enhancement Error: {e}")
        return False

# ============================================
# 📷 PHOTO QUALITY CHECK
# ============================================
def check_image_quality(image_path):
    try:
        if not os.path.exists(image_path):
            return False
        file_size = os.path.getsize(image_path)
        if file_size < 10000:  
            return False
        from PIL import Image
        img = Image.open(image_path)
        width, height = img.size
        if width < 512 or height < 512:
            return False
        img.verify()
        return True
    except:
        return False

# ============================================
# 📝 CAPTION GENERATE
# ============================================
def generate_caption():
    hour = datetime.now().hour
    time_text = "🌅 Good Morning!" if 6 <= hour < 12 else "☀️ Afternoon glow" if 12 <= hour < 17 else "🌆 Evening elegance" if 17 <= hour < 21 else "🌙 Night queen"
    captions = [
        f"""{time_text}

✨ AI Generated Elegant Look! 🤩

आपको कैसा लगा? 🤔
👇 Comment में बताओ:
❤️ - पसंद आया
💔 - नहीं पसंद

#AIFashion #IndianBeauty #AIArt #ViralFashion #ExplorePage #FYP #StyleInspo #FashionGoals #AIModel"""
    ]
    return random.choice(captions)

# ============================================
# 📤 FACEBOOK पर POST करें
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
            response = requests.post(fb_url, data=payload, files=files, timeout=120)
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

def cleanup_files(*files):
    for file in files:
        if file and os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass

# ============================================
# 🚀 MAIN BOT
# ============================================
def main():
    print("\n" + "="*60)
    print("🚀 INSTAGRAM STYLE AI BOT START")
    print("="*60)
    start_time = time.time()
    
    try:
        # STEP 1: इंस्टाग्राम से रियल स्टाइल प्राप्त करना (Playwright + Gemini)
        style_prompt = learn_style_from_instagram()
        
        # STEP 2: इमेज जनरेशन
        image_path = generate_ai_image(style_prompt, "instagram_style_photo.jpg")
        if not image_path:
            print("❌ फोटो नहीं बन पाई!")
            return False
            
        # STEP 3: रीप्लिकेट फ़ेस रिस्टोरेशन (Rate Limit सुधार के साथ)
        if REPLICATE_API_TOKEN:
            live_url = upload_image_to_cloud(image_path)
            if live_url:
                success_restore = restore_face_replicate(live_url, image_path)
                if not success_restore:
                    print("⚠️ फेस रिस्टोरेशन विफल रहा, मूल फोटो का उपयोग किया जा रहा है...")
            else:
                print("⚠️ इमेज क्लाउड पर अपलोड नहीं हो सकी।")
        
        # STEP 4: इमेज एन्हांसमेंट
        enhance_image_quality(image_path)
        
        # STEP 5: क्वालिटी जांच और री-ट्राई मैकेनिज्म
        quality_ok = check_image_quality(image_path)
        if not quality_ok:
            print("⚠️ Quality Check Fail हुई! दोबारा प्रयास कर रहा हूँ...")
            image_path = generate_ai_image_simple("retry_photo.jpg")
            if image_path:
                if REPLICATE_API_TOKEN:
                    live_url = upload_image_to_cloud(image_path)
                    if live_url:
                        # री-ट्राई के लिए API कॉल करने से पहले 10s प्रतीक्षा करें (Rate limiting सुरक्षा)
                        time.sleep(10)
                        restore_face_replicate(live_url, image_path)
                enhance_image_quality(image_path)
                quality_ok = check_image_quality(image_path)
                if not quality_ok:
                    image_path = create_placeholder_image("placeholder_final.jpg")
        
        # STEP 6: फेसबुक पर अपलोड
        caption = generate_caption()
        post_id = post_to_facebook(image_path, caption)
        
        cleanup_files(image_path, "retry_photo.jpg", "placeholder_final.jpg")
        
        elapsed = time.time() - start_time
        if post_id:
            print(f"⏱️ कुल समय: {elapsed:.2f} सेकंड")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
