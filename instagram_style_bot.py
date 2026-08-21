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

print(f"Target: @{TARGET_PROFILE}")
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
# 🎨 MULTIPLE PROMPTS
# ============================================
PROMPTS = [
    """
    A stunning high-quality waist-up portrait of an Indian bride standing gracefully, 
    showing her traditional red bridal wear down to the waist.
    Highly detailed realistic facial features, natural skin pores, realistic eyes, 
    soft studio lighting, 8k resolution, highly focused, photorealistic.
    """,
    """
    A glamorous waist-up fashion editorial shot of a Bollywood actress standing gracefully, 
    showing her modern designer fusion wear down to her waist.
    Extremely sharp focus, natural skin texture, realistic human eyes, professional studio lighting, 
    symmetrical facial features, photorealistic, 8k.
    """,
    """
    A beautiful waist-up portrait of a South Indian woman standing gracefully in a silk saree, 
    traditional design visible down to the waist.
    Sharp focus on face, natural warm skin tone, realistic detailed eyes, rich Kanjivaram saree details, 
    natural sunlight background, dslr quality.
    """,
    """
    A royal Rajasthani woman standing in a palace, waist-up portrait showing her traditional 
    heavy-embroidered lehenga down to the waist.
    Symmetrical highly detailed face, realistic eyes, natural skin structure, warm golden hour lighting, 
    crystal clear focus.
    """
]

def create_default_prompt():
    return random.choice(PROMPTS)

def learn_style_from_instagram():
    print(f"📸 Instagram Login Skip - Using Manual Style Prompts")
    selected_prompt = random.choice(PROMPTS)
    return selected_prompt

# ============================================
# ☁️ इमेज को सुरक्षित लाइव URL पर अपलोड करना (Dual Backup)
# ============================================
def upload_image_to_cloud(image_path):
    # 1. Catbox.moe पर प्रयास करें (यह रीप्लिकेट के लिए सबसे स्थिर है)
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

    # 2. Tmpfiles.org पर फॉलबैक प्रयास करें
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
# 🎭 REPLICATE FACE RESTORE (CodeFormer + GFPGAN)
# ============================================
def restore_face_replicate(image_url, filename="generated_photo.jpg"):
    if not REPLICATE_API_TOKEN:
        print("⚠️ REPLICATE_API_TOKEN नहीं मिला! रीस्टोरेशन बाईपास हो रहा है...")
        return False
        
    print("🚀 CodeFormer (Replicate) से चेहरा और डिटेल्स साफ़ कर रहा हूँ...")
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # उत्कृष्ट परिणामों के लिए CodeFormer का उपयोग
    payload = {
        "version": "7de2ac0394e09d5434e357d203f4b840a4d2b21ca15d211418984dbaf5aa60f5",
        "input": {
            "image": image_url,
            "codeformer_fidelity": 0.65,
            "background_enhance": True,
            "face_upsample": True,
            "upscale": 2
        }
    }
    
    try:
        response = session.post("https://api.replicate.com/v1/predictions", headers=headers, json=payload, timeout=60)
        
        # यदि CodeFormer फेल होता है तो GFPGAN v1.4 पर स्विच करें
        if response.status_code != 201:
            print(f"⚠️ CodeFormer त्रुटि (Code: {response.status_code}). GFPGAN v1.4 पर स्विच कर रहा हूँ...")
            payload_gfpgan = {
                "version": "92836085e34d856012c05f1890d6d405ab8854b0c400b8296996b7cd3d02f2b1",
                "input": {
                    "img": image_url,
                    "version": "v1.4",
                    "scale": 2
                }
            }
            response = session.post("https://api.replicate.com/v1/predictions", headers=headers, json=payload_gfpgan, timeout=60)
            if response.status_code != 201:
                print(f"❌ Replicate API Error: Code {response.status_code} - {response.text[:200]}")
                return False

        prediction = response.json()
        poll_url = prediction["urls"]["get"]
        
        print("⏳ चेहरे के पिक्सल और डिटेल्स को ठीक किया जा रहा है...")
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
                        print("🎉 सफलता! चेहरा पूरी तरह से रिस्टोर और साफ हो गया!")
                        return True
                elif status in ["failed", "canceled"]:
                    print(f"❌ Replicate प्रक्रिया विफल: {status} - {status_data.get('error', '')}")
                    break
    except Exception as e:
        print(f"❌ फेस रीस्टोरेशन एरर: {e}")
    return False

# ============================================
# 🎨 MULTI-ENGINE GENERATOR
# ============================================
def generate_ai_image_hf(prompt_text, model_id="playgroundai/playground-v2.5-1024px-aesthetic", filename="generated_photo.jpg"):
    if not HF_TOKEN:
        print("⚠️ HF_TOKEN नहीं मिला! Hercai V3 बैकअप पर जा रहा हूँ...")
        return None
        
    print(f"🚀 Hugging Face Mirror से {model_id} मॉडल द्वारा जनरेट कर रहा हूँ...")
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
            print("✅ Hugging Face से फोटो सफलतापूर्वक डाउनलोड हो गई!")
            return filename
    except Exception as e:
        print(f"❌ HF Mirror Connection Error: {e}")
        return None

def generate_ai_hercai(prompt_text, filename="generated_photo.jpg"):
    print("🚀 Hercai V3 (SDXL) से लाइव फोटो बना रहा हूँ...")
    url = "https://hercai.onrender.com/v3/hercai"
    payload = {
        "prompt": prompt_text + ", highly detailed, sharp focus, realistic face, 8k resolution, photorealistic",
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
    except Exception as e:
        print(f"❌ Hercai V3 जनरेशन विफल: {e}")
    return None

def generate_ai_image(prompt_text, filename="generated_photo.jpg"):
    print("\n🎨 [इमेज जनरेटर] प्रक्रिया शुरू हो रही है...")
    image_path = generate_ai_image_hf(prompt_text, "playgroundai/playground-v2.5-1024px-aesthetic", filename)
    if image_path:
        return image_path
        
    image_path = generate_ai_hercai(prompt_text, filename)
    if image_path:
        return image_path

    print("🔄 [लेयर 3] पोलिनेशंस बैकअप सर्वर पर स्विच कर रहा हूँ...")
    clean_prompt = prompt_text.strip().replace('\n', ' ').replace('  ', ' ')
    encoded_prompt = urllib.parse.quote(clean_prompt[:250])
    flux_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1280&model=flux-realism&nologo=true&quality=high"
    
    try:
        response = session.get(flux_url, timeout=120)
        if response.status_code == 200 and len(response.content) > 50000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
    except Exception as e:
        print(f"❌ पोलिनेशंस बैकअप सर्वर विफल: {e}")
        
    return create_placeholder_image(filename)

def generate_ai_image_simple(filename="generated_photo.jpg"):
    simple_prompts = [
        "Beautiful Indian bride, waist-up portrait, traditional red dress, realistic skin, sharp focus",
        "Stunning Indian woman in saree, waist-up portrait, detailed face, professional portrait"
    ]
    return generate_ai_image(random.choice(simple_prompts), filename)

def create_placeholder_image(filename="placeholder.jpg"):
    backup_prompt = "Stunning Indian woman standing gracefully, waist-up portrait, realistic face, sharp focus"
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
        print(f"✅ एन्हांसमेंट सफलतापूर्वक पूरा हुआ! नई फाइल साइज: {os.path.getsize(image_path)/1024:.1f} KB")
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
        style_prompt = learn_style_from_instagram()
        
        image_path = generate_ai_image(style_prompt, "instagram_style_photo.jpg")
        if not image_path:
            print("❌ फोटो नहीं बन पाई!")
            return False
            
        # STEP 3: चेहरे के सुधार के लिए इमेज को अपलोड कर CodeFormer/GFPGAN चलाना
        if REPLICATE_API_TOKEN:
            live_url = upload_image_to_cloud(image_path)
            if live_url:
                success_restore = restore_face_replicate(live_url, image_path)
                if not success_restore:
                    print("⚠️ फेस रिस्टोरेशन विफल रहा, मूल फोटो का उपयोग किया जा रहा है...")
            else:
                print("⚠️ इमेज क्लाउड पर अपलोड नहीं हो सकी, रिस्टोरेशन बाईपास किया गया।")
        
        enhance_image_quality(image_path)
        
        quality_ok = check_image_quality(image_path)
        if not quality_ok:
            print("⚠️ Quality Check Fail हुई! दोबारा प्रयास कर रहा हूँ...")
            image_path = generate_ai_image_simple("retry_photo.jpg")
            if image_path:
                if REPLICATE_API_TOKEN:
                    live_url = upload_image_to_cloud(image_path)
                    if live_url:
                        restore_face_replicate(live_url, image_path)
                enhance_image_quality(image_path)
                quality_ok = check_image_quality(image_path)
                if not quality_ok:
                    image_path = create_placeholder_image("placeholder_final.jpg")
        
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
