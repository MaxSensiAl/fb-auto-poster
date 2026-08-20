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
# (Hugging Face DNS Connection Error को पूरी तरह ठीक करने के लिए)
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
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN") # ✅ रीप्लिकेट सीक्रेट टोकन

# Check Credentials
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
# 🎨 MULTIPLE PROMPTS (कमर तक की फोटो और अत्यंत साफ चेहरे के लिए)
# ============================================

PROMPTS = [
    # 1. Traditional Indian Bride (Waist-up)
    """
    A stunning high-quality waist-up portrait of an Indian bride standing gracefully, 
    showing her traditional red bridal wear down to the waist.
    Razor-sharp focus on face and body, highly detailed symmetrical facial features, realistic clear eyes, 
    extremely detailed natural skin texture, beautiful gold jewelry, dslr photography, 8k resolution, highly focused.
    """,
    
    # 2. Modern Bollywood Style (Waist-up)
    """
    A glamorous waist-up fashion editorial shot of a Bollywood actress standing gracefully, 
    showing her modern designer fusion wear down to her waist.
    Extremely sharp focus on face and body, detailed eyes, natural skin structure, professional studio lighting.
    Symmetrical facial features, photorealistic, 8k, razor-sharp composition.
    """,
    
    # 3. South Indian Beauty (Waist-up)
    """
    A beautiful waist-up portrait of a South Indian woman standing gracefully in a silk saree, 
    traditional design visible down to the waist.
    Sharp focus on face and upper body, symmetrical eyes, detailed realistic skin, rich kanjivaram saree details.
    Natural sunlight, temple architecture background, highly focused, dslr quality, razor-sharp.
    """,
    
    # 4. Royal Rajasthani Style (Waist-up)
    """
    A royal Rajasthani woman standing in a palace, waist-up portrait showing her traditional 
    heavy-embroidered lehenga and silver jewelry down to the waist.
    Symmetrical face, highly detailed realistic eyes, razor-sharp focus on face, realistic skin texture.
    Warm golden sunset lighting, majestic look, crystal clear, highly focused.
    """,
    
    # 5. Modern Minimalist (Waist-up)
    """
    A modern Indian woman standing elegantly, waist-up shot showing her minimalist pastel saree down to the waist.
    Clean symmetrical face, realistic eyes, natural detailed skin, sharp focus on facial features and body.
    Minimalist modern background, soft daylight, contemporary style, photorealistic, sharp focus.
    """,
    
    # 6. Festival Special (Waist-up)
    """
    A happy Indian woman celebrating Diwali, waist-up standing pose showing her entire mirror-work lehenga down to the waist.
    Razor-sharp focus on face and body, happy realistic expression, symmetrical facial features, highly detailed eyes.
    Vibrant colors, festive warm lighting, highly focused, professional photography, dslr.
    """,
    
    # 7. Wedding Guest Look (Waist-up)
    """
    A beautiful Indian woman in wedding guest attire, waist-up standing shot showing elegant designer wear down to her waist.
    Symmetrical facial features, highly detailed realistic eyes, natural skin structure, sharp focus on upper body.
    Soft romantic lighting, elegant wedding hall background with gentle bokeh, dslr photography, highly focused.
    """,
    
    # 8. Kashmiri Beauty (Waist-up)
    """
    A Kashmiri woman standing gracefully, waist-up portrait wearing a traditional embroidered pheran down to the waist.
    Symmetrical face, highly detailed realistic eyes, natural fair skin, sharp focus on face and upper body.
    Snowy mountains background, soft winter sunlight, realistic textures, crystal clear, highly focused.
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
# ☁️ 2. JUGAD: फोटो को लाइव यूआरएल पर अपलोड करना (Replicate के लिए)
# ============================================

def upload_to_tmpfiles(image_path):
    """
    फोटो को Replicate API में भेजने के लिए 1 सेकंड के लिए लाइव यूआरएल बनाना
    """
    print("⏳ फोटो को सुरक्षित क्लाउड होस्ट पर अपलोड कर रहा हूँ...")
    try:
        with open(image_path, 'rb') as f:
            response = session.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=60)
        if response.status_code == 200:
            data = response.json()
            file_url = data.get("data", {}).get("url")
            # डायरेक्ट इमेज डाउनलोड लिंक
            direct_url = file_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
            print("✅ अस्थायी क्लाउड इमेज यूआरएल तैयार है!")
            return direct_url
    except Exception as e:
        print(f"⚠️ क्लाउड अपलोड त्रुटि: {e}")
    return None

# ============================================
# 🎭 3. REPLICATE GFPGAN (TencentARC) - चेहरे को 100% साफ करना
# ============================================

def restore_face_replicate(image_url, filename="generated_photo.jpg"):
    """
    Replicate GFPGAN v1.4 का उपयोग करके चेहरे के पिक्सल्स को असली जैसा पैना और साफ बनाना
    """
    if not REPLICATE_API_TOKEN:
        print("⚠️ REPLICATE_API_TOKEN नहीं मिला! रीस्टोरेशन स्टेप बायपास कर रहा हूँ...")
        return False
        
    print("🚀 Replicate GFPGAN से चेहरा रीस्टोर और पैना (Sharpen) कर रहा हूँ...")
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "version": "92836085e34d856012c05f1890d6d405ab8854b0c400b8296996b7cd3d02f2b1", # GFPGAN v1.4 Hash
        "input": {
            "img": image_url,
            "version": "v1.4",
            "scale": 2
        }
    }
    
    try:
        # Prediction शुरू करें
        response = session.post("https://api.replicate.com/v1/predictions", headers=headers, json=payload, timeout=60)
        if response.status_code == 201:
            prediction = response.json()
            poll_url = prediction["urls"]["get"]
            
            # रिजल्ट तैयार होने तक प्रतीक्षा करें (अधिकतम 60 सेकंड)
            print("⏳ चेहरे के विश्लेषण और पैनेपन की प्रक्रिया चालू है...")
            for _ in range(30):
                time.sleep(2)
                status_resp = session.get(poll_url, headers=headers, timeout=30)
                if status_resp.status_code == 200:
                    status_data = status_resp.json()
                    status = status_data.get("status")
                    if status == "succeeded":
                        output_url = status_data.get("output")
                        # नई फोटो को सेव करें
                        img_resp = session.get(output_url, timeout=60)
                        if img_resp.status_code == 200:
                            with open(filename, 'wb') as f:
                                f.write(img_resp.content)
                            print("🎉 सफलता! GFPGAN द्वारा पूरी तरह साफ किया गया यथार्थवादी चेहरा डाउनलोड हो गया!")
                            return True
                    elif status in ["failed", "canceled"]:
                        print(f"❌ Replicate प्रक्रिया विफल: {status}")
                        break
    except Exception as e:
        print(f"❌ GFPGAN रीस्टोरेशन एरर: {e}")
    return False

# ============================================
# 🎨 4. MULTI-ENGINE GENERATOR (HF, Hercai, Pollinations)
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
            print("✅ Hugging Face (Playground v2.5) से फोटो सफलतापूर्वक डाउनलोड हो गई!")
            return filename
    except Exception as e:
        print(f"❌ HF Mirror Connection Error: {e}")
        return None


def generate_ai_hercai(prompt_text, filename="generated_photo.jpg"):
    print("🚀 [लेयर 2] Hercai V3 (Stable Diffusion XL) से लाइव फोटो बना रहा हूँ...")
    url = "https://hercai.onrender.com/v3/hercai"
    
    payload = {
        "prompt": prompt_text + ", highly detailed, sharp focus, realistic face, 8k resolution, extreme details",
        "model": "v3"  
    }
    
    try:
        response = session.post(url, json=payload, timeout=90)
        if response.status_code == 200:
            data = response.json()
            img_url = data.get("reply")  
            
            if img_url:
                print("📥 फोटो जनरेट हो गई! डाउनलोड कर रहा हूँ...")
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
    """
    3-लेयर इमेज जनरेटर
    """
    print("\n🎨 [इमेज जनरेटर] 3-लेयर प्रक्रिया शुरू हो रही है...")
    
    # LAYER 1: Playground v2.5
    image_path = generate_ai_image_hf(prompt_text, "playgroundai/playground-v2.5-1024px-aesthetic", filename)
    if image_path:
        return image_path
        
    # LAYER 2: Hercai V3 (Stable Diffusion XL)
    image_path = generate_ai_hercai(prompt_text, filename)
    if image_path:
        return image_path

    # LAYER 3: Pollinations (Flux-Realism)
    print("🔄 [लेयर 3] पोलिनेशंस बैकअप सर्वर पर स्विच कर रहा हूँ...")
    clean_prompt = prompt_text.strip().replace('\n', ' ').replace('  ', ' ')
    encoded_prompt = urllib.parse.quote(clean_prompt[:250])
    
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1280"  
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
            print("✅ पोलिनेशंस बैकअप से फोटो सफलतापूर्वक जनरेट हो गई!")
            return filename
    except Exception as e:
        print(f"❌ पोलिनेशंस बैकअप सर्वर विफल: {e}")
        
    return create_placeholder_image(filename)


def generate_ai_image_simple(filename="generated_photo.jpg"):
    print("🔄 सरल प्रॉम्प्ट के साथ Retry कर रहा हूँ...")
    simple_prompts = [
        "Beautiful Indian bride, waist-up portrait, traditional red dress, symmetrical face, razor-sharp focus on face, realistic skin",
        "Stunning Indian woman in saree, waist-up portrait, detailed symmetrical face, clear eyes, professional portrait, sharp focus",
        "Glamorous Bollywood actress portrait, waist-up shot, symmetrical face, sharp focus, professional photography, studio lighting",
        "Elegant Indian woman in traditional jewelry, waist-up portrait, highly detailed face, sharp focus, professional photo"
    ]
    simple_prompt = random.choice(simple_prompts)
    return generate_ai_image(simple_prompt, filename)


def create_placeholder_image(filename="placeholder.jpg"):
    print("🔄 [इमरजेंसी बैकअप] लाइव पोलिनेशन्स एचडी बैकअप जनरेट कर रहा हूँ...")
    backup_prompt = "Stunning Indian woman standing gracefully, waist-up portrait, detailed saree, realistic face, sharp focus"
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
        
    try:
        from PIL import Image
        img = Image.new('RGB', (1024, 1280), color=(30, 30, 40))
        img.save(filename)
        return filename
    except:
        with open(filename, 'wb') as f:
            f.write(b'PLACEHOLDER')
        return filename

# ============================================
# 🖼️ IMAGE ENHANCE (3-PASS ULTRA HD SYSTEM)
# ============================================

def enhance_image_quality(image_path):
    """
    Image Quality Enhance - UnsharpMask फोटोग्राफी फ़िल्टर के साथ (चेहरे और ज्वेलरी को क्रिस्टल-क्लियर बनाने के लिए)
    """
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        
        img = Image.open(image_path)
        width, height = img.size
        print(f"📐 Original Resolution: {width}x{height}")
        
        # 1. रिज़ॉल्यूशन को सीधे 1536x1920 (Ultra HD / 2K) में बदलें
        new_width = 1536
        new_height = 1920
        print(f"📐 Scaling to Ultra HD: {width}x{height} → {new_width}x{new_height}")
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 2. 🌀 [Unsharp Mask] फोटोग्राफी डिटेलिंग फ़िल्टर
        print("⏳ Applying progressive photographic Unsharp Mask...")
        img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=2))
        
        # 3. 🌀 [3-पास प्रोग्रेसिव एन्हांसमेंट]
        print("⏳ 3-Pass progressive sharpness tuning...")
        for i in range(1, 4):  
            sharp_enhancer = ImageEnhance.Sharpness(img)
            img = sharp_enhancer.enhance(1.1)  
            
            contrast_enhancer = ImageEnhance.Contrast(img)
            img = contrast_enhancer.enhance(1.02)
            print(f"✅ Pass {i} complete!")
        
        # 4. High Quality Save
        img.save(image_path, quality=95, optimize=True, format='JPEG')
        new_size = os.path.getsize(image_path)
        print(f"✅ 3-Pass Ultra HD UnsharpMask Done! New Size: {new_size/1024:.1f} KB")
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
            print("❌ File exists नहीं है!")
            return False
        
        file_size = os.path.getsize(image_path)
        print(f"📊 File Size: {file_size/1024:.1f} KB")
        
        if file_size < 10000:  
            return False
        
        try:
            from PIL import Image
            img = Image.open(image_path)
            width, height = img.size
            print(f"📐 Resolution: {width}x{height}")
            
            if width < 512 or height < 512:
                return False
            
            img.verify()
            print("✅ Image Valid है!")
            return True
            
        except ImportError:
            if file_size > 10000:
                return True
            else:
                return False
    except:
        return False

# ============================================
# 📝 5. CAPTION GENERATE करें
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

#AIBride #IndianWedding #AIArt #TrendingReels #ViralPost #FYP #ExplorePage #AIFashion #BridalWear #AICommunity #DigitalArt #AIInfluencer #AIModel #FashionAI #IndianFashion #BollywoodStyle #AIArtCommunity #ViralReels #InstagramReels #Explore #TrendingNow #AIContent #AIGirl #ArtificialIntelligence #TechFashion #FutureOfFashion #AIforIndia #IndianAI #DesiBride #ShaadiGoals""",
        
        f"""{time_text}

💃 AI Generated - Royal Indian Beauty! 👑

कौन सा style सबसे best लगा?
👇 Comment में बताओ:
👑 Traditional
💎 Modern
🌸 Fusion

🎯 200+ Votes = Next Look Special!

#RoyalBeauty #IndianFashion #AIArt #ViralReels #ExplorePage #FYP #TraditionalWear #ModernFashion #AICouture #VirtualInfluencer #AICommunity #DigitalArt #FashionGram #BridalFashion #IndianBride #AIContent #TechFashion #FutureOfFashion #AIforIndia #IndianAI #DesiBride #ShaadiGoals #AIFashionista #StyleInspo #OOTD #FashionGoals"""
    ]
    
    return random.choice(captions)

# ============================================
# 📤 6. FACEBOOK पर POST करें
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
        if not os.path.exists(image_path) or os.path.getsize(image_path) < 100:
            print("❌ फोटो फ़ाइल इनवैलिड है!")
            return None
        
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

# ============================================
# 🧹 7. CLEANUP
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
# 🚀 8. MAIN BOT
# ============================================

def main():
    print("\n" + "="*60)
    print("🚀 INSTAGRAM STYLE AI BOT START (3-PASS ULTRA HD + GFPGAN ENGINE)")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # STEP 1: Style Select
        print("\n📸 STEP 1: Style Select...")
        style_prompt = learn_style_from_instagram()
        
        # STEP 2: AI से फोटो बनाएं
        print("\n🎨 STEP 2: AI से फोटो बना रहा हूँ...")
        image_path = generate_ai_image(style_prompt, "instagram_style_photo.jpg")
        
        if not image_path:
            print("❌ फोटो नहीं बन पाई!")
            return False
            
        # ✅ [GFPGAN चेहरा रीस्टोरेशन बाईपास]
        # इमेज जनरेट होने के बाद, हम उसे Tmpfiles पर अपलोड करके Replicate GFPGAN से चेहरा साफ करेंगे
        if REPLICATE_API_TOKEN:
            live_url = upload_to_tmpfiles(image_path)
            if live_url:
                success_restore = restore_face_replicate(live_url, image_path)
                if not success_restore:
                    print("⚠️ GFPGAN विफल रहा, मूल फोटो का उपयोग कर रहा हूँ...")
        
        # ✅ STEP 2.5: Image Quality Enhance & Polish
        # अब फोटो को 1536x1920 (2K Ultra HD) आकार में बदल कर UnsharpMask और 3-पास शार्पनेस लागू करेंगे
        enhance_image_quality(image_path)
        
        # STEP 2.8: Photo Quality Check
        print("\n📷 STEP 2.8: Photo Quality Check...")
        quality_ok = check_image_quality(image_path)
        
        if not quality_ok:
            print("⚠️ Quality Check Fail हुई! नई फोटो बना रहा हूँ...")
            image_path = generate_ai_image_simple("retry_photo.jpg")
            if image_path:
                # यदि री-ट्राई इमेज बनी है, तो उस पर भी GFPGAN और HD Polish लागू करें
                if REPLICATE_API_TOKEN:
                    live_url = upload_to_tmpfiles(image_path)
                    if live_url:
                        restore_face_replicate(live_url, image_path)
                enhance_image_quality(image_path)
                
                quality_ok = check_image_quality(image_path)
                if not quality_ok:
                    image_path = create_placeholder_image("placeholder_final.jpg")
        
        # STEP 3: कैप्शन बनाएं
        print("\n📝 STEP 3: कैप्शन बना रहा हूँ...")
        caption = generate_caption()
        print(f"✅ कैप्शन तैयार ({len(caption)} अक्षर)")
        
        # STEP 4: Facebook पर पोस्ट करें
        print("\n📤 STEP 4: Facebook पर पोस्ट कर रहा हूँ...")
        post_id = post_to_facebook(image_path, caption)
        
        # STEP 5: क्लीनअप
        print("\n🧹 STEP 5: क्लीनअप...")
        cleanup_files(image_path, "ref_post_1.jpg", "ref_post_2.jpg", "ref_post_3.jpg", "retry_photo.jpg", "placeholder_final.jpg")
        
        elapsed = time.time() - start_time
        
        if post_id:
            print("\n" + "="*60)
            print("🎉 SUCCESS! सब कुछ हो गया!")
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
