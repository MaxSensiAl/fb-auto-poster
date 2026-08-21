import os
import sys
import time
import random
import requests
import urllib.parse
import logging
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import replicate  # ✅ Replicate SDK आयात किया गया

# ============================================
# 📝 लॉगिंग सेटअप
# ============================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================
# 🌐 GITHUB Actions के लिए IPv4-Force DNS पैच
# ============================================
import urllib3.util.connection as urllib3_connection
urllib3_connection.HAS_IPV6 = False

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

# अनिवार्य क्रेडेंशियल्स की जांच
REQUIRED_SECRETS = ["FB_PAGE_ID", "FB_ACCESS_TOKEN"]
missing_secrets = [s for s in REQUIRED_SECRETS if not os.environ.get(s)]
if missing_secrets:
    logger.critical(f"❌ अनिवार्य क्रेडेंशियल्स गायब हैं: {missing_secrets}")
    sys.exit(1)

logger.info(f"Target Profile: @{TARGET_PROFILE}")
logger.info(f"Facebook Page ID: {FB_PAGE_ID[:3]}***")

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

def learn_style_from_instagram():
    logger.info("📸 Instagram Login Skip - Using Manual Style Prompts")
    logger.info(f"🎯 Target Profile: @{TARGET_PROFILE}")
    selected_prompt = random.choice(PROMPTS)
    logger.info(f"✅ Selected Prompt: {selected_prompt[:100].strip()}...")
    return selected_prompt

# ============================================
# ☁️ 2. इमेज अपलोडर (tmpfiles.org + catbox.moe फॉलबैक)
# ============================================
def upload_image_for_replicate(image_path):
    logger.info("⏳ फोटो को सुरक्षित क्लाउड होस्ट पर अपलोड कर रहा हूँ...")
    
    # 1. पहला प्रयास: tmpfiles.org
    try:
        with open(image_path, 'rb') as f:
            response = session.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            file_url = data.get("data", {}).get("url")
            direct_url = file_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
            logger.info("✅ अस्थायी क्लाउड इमेज यूआरएल (tmpfiles.org) तैयार है!")
            return direct_url
    except Exception as e:
        logger.warning(f"⚠️ tmpfiles.org अपलोड विफल रहा: {e}")

    # 2. दूसरा प्रयास (फॉलबैक): catbox.moe
    try:
        logger.info("🔄 फॉलबैक सर्वर (catbox.moe) पर अपलोड करने का प्रयास कर रहा हूँ...")
        with open(image_path, 'rb') as f:
            response = session.post(
                "https://catbox.moe/user/api.php", 
                data={"reqtype": "fileupload"}, 
                files={"fileToUpload": f}, 
                timeout=60
            )
        if response.status_code == 200 and response.text.startswith("https://"):
            logger.info("✅ फॉलबैक सर्वर (catbox.moe) इमेज यूआरएल तैयार है!")
            return response.text.strip()
    except Exception as e:
        logger.error(f"❌ catbox.moe अपलोड भी विफल रहा: {e}")
    
    return None

# ============================================
# 🎭 3. REPLICATE GFPGAN (SDK आधारित सुरक्षित संस्करण)
# ============================================
def restore_face_replicate_sdk(image_url, filename="generated_photo.jpg"):
    """Replicate SDK का उपयोग करके GFPGAN चलाना ताकि हैश एरर न आए"""
    if not REPLICATE_API_TOKEN:
        logger.warning("⚠️ REPLICATE_API_TOKEN नहीं मिला! रीस्टोरेशन स्किप।")
        return False
        
    logger.info("🚀 Replicate SDK से GFPGAN (tencentarc/gfpgan) चला रहा हूँ...")
    
    # SDK स्वतः REPLICATE_API_TOKEN एनवायरनमेंट वेरिएबल का उपयोग करता है
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
    
    try:
        # tencentarc/gfpgan का विशिष्ट और स्थिर v1.4 वर्जन उपयोग करना
        output = replicate.run(
            "tencentarc/gfpgan:92836085e34d856012c05f1890d6d405ab8854b0c400b8296996b7cd3d02f2b1",
            input={
                "img": image_url,
                "scale": 2,
                "version": "v1.4"
            }
        )
        
        if output:
            img_url = output[0] if isinstance(output, list) else output
            logger.info("📥 चेहरा रीस्टोर हो गया, इमेज डाउनलोड कर रहा हूँ...")
            img_resp = session.get(img_url, timeout=60)
            if img_resp.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(img_resp.content)
                logger.info("🎉 सफलता! GFPGAN SDK द्वारा चेहरा सफलतापूर्वक रीस्टोर और डाउनलोड हो गया!")
                return True
    except Exception as e:
        logger.error(f"❌ Replicate SDK Error: {e}")
    return False

# ============================================
# 🎨 4. MULTI-ENGINE GENERATOR (HF, Hercai, Pollinations)
# ============================================
def generate_ai_image_hf(prompt_text, model_id="playgroundai/playground-v2.5-1024px-aesthetic", filename="generated_photo.jpg"):
    if not HF_TOKEN:
        logger.warning("⚠️ HF_TOKEN नहीं मिला! Hercai V3 बैकअप पर जा रहा हूँ...")
        return None
        
    logger.info(f"🚀 Hugging Face Mirror से {model_id} मॉडल द्वारा जनरेट कर रहा हूँ...")
    api_url = f"https://api-inference.hf-mirror.com/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    payload = {
        "inputs": prompt_text,
        "parameters": {
            "width": 1024,
            "height": 1024,
            "negative_prompt": "deformed, ugly, bad anatomy, extra limbs, extra fingers, missing fingers, mutated hands, poorly drawn face, blurry, watermark, text, signature, logo, asymmetric face, bad teeth, distorted jewelry"
        }
    }
    
    try:
        response = session.post(api_url, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 503:
            estimated_time = response.json().get("estimated_time", 20)
            logger.info(f"⏳ मॉडल लोड हो रहा है, {estimated_time:.1f} सेकंड प्रतीक्षा कर रहा हूँ...")
            time.sleep(min(estimated_time, 30))
            response = session.post(api_url, headers=headers, json=payload, timeout=120)
            
        if response.status_code == 200 and len(response.content) > 10000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            logger.info("✅ Hugging Face (Playground v2.5) से फोटो सफलतापूर्वक डाउनलोड हो गई!")
            return filename
        else:
            # 🔍 विस्तृत एरर लॉगिंग
            logger.error(f"❌ HF Mirror विफल (Status: {response.status_code}): {response.text[:200]}")
    except Exception as e:
        logger.error(f"❌ HF Mirror Connection Error: {e}")
    return None

def generate_ai_hercai(prompt_text, filename="generated_photo.jpg"):
    logger.info("🚀 [लेयर 2] Hercai V3 (Stable Diffusion XL) से फोटो बना रहा हूँ...")
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
                logger.info("📥 फोटो जनरेट हो गई! डाउनलोड कर रहा हूँ...")
                img_response = session.get(img_url, timeout=90)
                if img_response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(img_response.content)
                    logger.info("✅ Hercai V3 से हाई-क्वालिटी फोटो डाउनलोड हो गई!")
                    return filename
        else:
            logger.error(f"❌ Hercai API विफल (Status: {response.status_code}): {response.text[:200]}")
    except Exception as e:
        logger.error(f"❌ Hercai V3 जनरेशन विफल: {e}")
    return None

def generate_ai_image(prompt_text, filename="generated_photo.jpg"):
    logger.info("\n🎨 [इमेज जनरेटर] 3-लेयर प्रक्रिया शुरू हो रही है...")
    
    # LAYER 1: Playground v2.5
    image_path = generate_ai_image_hf(prompt_text, "playgroundai/playground-v2.5-1024px-aesthetic", filename)
    if image_path:
        return image_path
        
    # LAYER 2: Hercai V3
    image_path = generate_ai_hercai(prompt_text, filename)
    if image_path:
        return image_path

    # LAYER 3: Pollinations (Flux-Realism)
    logger.info("🔄 [लेयर 3] पोलिनेशंस बैकअप सर्वर पर स्विच कर रहा हूँ...")
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
            logger.info("✅ पोलिनेशंस बैकअप से फोटो सफलतापूर्वक जनरेट हो गई!")
            return filename
    except Exception as e:
        logger.error(f"❌ पोलिनेशंस बैकअप सर्वर विफल: {e}")
        
    return create_placeholder_image(filename)

def generate_ai_image_simple(filename="generated_photo.jpg"):
    logger.info("🔄 सरल प्रॉम्प्ट के साथ Retry कर रहा हूँ...")
    simple_prompts = [
        "Beautiful Indian bride, waist-up portrait, traditional red dress, symmetrical face, razor-sharp focus on face, realistic skin",
        "Stunning Indian woman in saree, waist-up portrait, detailed symmetrical face, clear eyes, professional portrait, sharp focus",
        "Glamorous Bollywood actress portrait, waist-up shot, symmetrical face, sharp focus, professional photography, studio lighting",
        "Elegant Indian woman in traditional jewelry, waist-up portrait, highly detailed face, sharp focus, professional photo"
    ]
    simple_prompt = random.choice(simple_prompts)
    return generate_ai_image(simple_prompt, filename)

def create_placeholder_image(filename="placeholder.jpg"):
    logger.info("🔄 [इमरजेंसी बैकअप] लाइव पोलिनेशन्स एचडी बैकअप जनरेट कर रहा हूँ...")
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
        img = Image.new('RGB', (1024, 1280), color=(30, 30, 40))
        img.save(filename)
        return filename
    except:
        with open(filename, 'wb') as f:
            f.write(b'PLACEHOLDER')
        return filename

# ============================================
# 🖼️ IMAGE ENHANCE (Aspect Ratio Crop + HD 3-Pass)
# ============================================
def enhance_image_quality_safe(image_path, target_ratio=(4, 5), target_short_side=1536):
    try:
        img = Image.open(image_path).convert("RGB")
        orig_w, orig_h = img.size
        
        target_w = target_short_side
        target_h = int(target_short_side * target_ratio[1] / target_ratio[0])  # 1920
        
        if orig_w < orig_h:
            scale = target_w / orig_w
        else:
            scale = target_h / orig_h
            
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        img = img.crop((left, top, left + target_w, top + target_h))
        
        logger.info(f"📐 रीसाइज़ और क्रॉप पूर्ण: {orig_w}x{orig_h} -> {target_w}x{target_h}")
        
        img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))
        img = img.filter(ImageFilter.UnsharpMask(radius=0.5, percent=50, threshold=1))
        
        img = ImageEnhance.Sharpness(img).enhance(1.05)
        img = ImageEnhance.Contrast(img).enhance(1.03)
        img = ImageEnhance.Color(img).enhance(1.02)
        
        img.save(image_path, "JPEG", quality=95, optimize=True, subsampling=0)
        logger.info(f"✅ सुरक्षित 2K HD एन्हांसमेंट पूर्ण! नई फ़ाइल साइज: {os.path.getsize(image_path)/1024:.1f} KB")
        return True
    except Exception as e:
        logger.error(f"⚠️ एन्हांसमेंट त्रुटि: {e}", exc_info=True)
        return False

# ============================================
# 📷 PHOTO QUALITY CHECK
# ============================================
def check_image_quality(image_path):
    logger.info("📷 Photo Quality Check कर रहा हूँ...")
    try:
        if not os.path.exists(image_path):
            logger.error("❌ फ़ाइल मौजूद नहीं है!")
            return False
        
        file_size = os.path.getsize(image_path)
        logger.info(f"📊 File Size: {file_size/1024:.1f} KB")
        
        if file_size < 10000:  
            return False
        
        try:
            img = Image.open(image_path)
            width, height = img.size
            logger.info(f"📐 Resolution: {width}x{height}")
            
            if width < 512 or height < 512:
                return False
            
            img.verify()
            logger.info("✅ छवि मान्य (Valid) है!")
            return True
        except Exception as e:
            logger.error(f"❌ PIL इमेज सत्यापन त्रुटि: {e}")
            if file_size > 10000:
                return True
            return False
    except Exception as e:
        logger.error(f"❌ क्वालिटी चेक त्रुटि: {e}")
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
    logger.info("📤 Facebook पर पोस्ट कर रहा हूँ...")
    fb_url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
    
    payload = {
        'caption': caption,
        'access_token': FB_ACCESS_TOKEN,
        'published': 'true'
    }
    
    try:
        if not os.path.exists(image_path) or os.path.getsize(image_path) < 100:
            logger.error("❌ फोटो फ़ाइल इनवैलिड है!")
            return None
        
        with open(image_path, 'rb') as img_file:
            files = {'source': img_file}
            response = requests.post(fb_url, data=payload, files=files, timeout=120)
        
        if response.status_code == 200:
            post_id = response.json().get('id')
            logger.info(f"✅ पोस्ट सफलतापूर्वक पूर्ण हो गई! Post ID: {post_id}")
            return post_id
        else:
            logger.error(f"❌ Facebook API त्रुटि: {response.text[:500]}")
            return None
    except Exception as e:
        logger.error(f"⚠️ Facebook पोस्टिंग के दौरान अपवाद (Exception): {e}")
        return None

# ============================================
# 🧹 7. CLEANUP
# ============================================
def cleanup_files(*files):
    for file in files:
        if file and os.path.exists(file):
            try:
                os.remove(file)
                logger.info(f"🧹 {file} सफलतापूर्वक डिलीट हो गया।")
            except Exception as e:
                logger.warning(f"⚠️ {file} हटाते समय त्रुटि: {e}")

# ============================================
# 🚀 8. MAIN BOT
# ============================================
def main():
    logger.info("\n" + "="*60)
    logger.info("🚀 INSTAGRAM STYLE AI BOT START (3-PASS ULTRA HD + GFPGAN ENGINE)")
    logger.info("="*60)
    
    start_time = time.time()
    
    try:
        # STEP 1: Style Select
        logger.info("\n📸 STEP 1: Style Select...")
        style_prompt = learn_style_from_instagram()
        
        # STEP 2: AI से फोटो बनाएं
        logger.info("\n🎨 STEP 2: AI से फोटो बना रहा हूँ...")
        image_path = generate_ai_image(style_prompt, "instagram_style_photo.jpg")
        
        if not image_path:
            logger.error("❌ फोटो नहीं बन पाई!")
            return False
            
        # ✅ GFPGAN चेहरा रीस्टोरेशन (SDK आधारित)
        if REPLICATE_API_TOKEN:
            live_url = upload_image_for_replicate(image_path)
            if live_url:
                success_restore = restore_face_replicate_sdk(live_url, image_path)
                if not success_restore:
                    logger.warning("⚠️ GFPGAN विफल रहा, मूल फोटो का उपयोग जारी रख रहा हूँ...")
        
        # ✅ STEP 2.5: Image Quality Enhance & Polish
        enhance_image_quality_safe(image_path)
        
        # STEP 2.8: Photo Quality Check
        logger.info("\n📷 STEP 2.8: Photo Quality Check...")
        quality_ok = check_image_quality(image_path)
        
        if not quality_ok:
            logger.warning("⚠️ Quality Check फ़ेल हुई! नई फोटो बनाने का प्रयास कर रहा हूँ...")
            image_path = generate_ai_image_simple("retry_photo.jpg")
            if image_path:
                if REPLICATE_API_TOKEN:
                    live_url = upload_image_for_replicate(image_path)
                    if live_url:
                        restore_face_replicate_sdk(live_url, image_path)
                enhance_image_quality_safe(image_path)
                
                quality_ok = check_image_quality(image_path)
                if not quality_ok:
                    image_path = create_placeholder_image("placeholder_final.jpg")
        
        # STEP 3: कैप्शन बनाएं
        logger.info("\n📝 STEP 3: कैप्शन बना रहा हूँ...")
        caption = generate_caption()
        logger.info(f"✅ कैप्शन तैयार ({len(caption)} अक्षर)")
        
        # STEP 4: Facebook पर पोस्ट करें
        post_id = post_to_facebook(image_path, caption)
        
        # STEP 5: क्लीनअप
        logger.info("\n🧹 STEP 5: क्लीनअप...")
        cleanup_files(image_path, "ref_post_1.jpg", "ref_post_2.jpg", "ref_post_3.jpg", "retry_photo.jpg", "placeholder_final.jpg")
        
        elapsed = time.time() - start_time
        
        if post_id:
            logger.info("\n" + "="*60)
            logger.info("🎉 कार्य पूर्ण! सब कुछ सफलतापूर्वक निष्पादित हो गया!")
            logger.info(f"⏱️ कुल लिया गया समय: {elapsed:.2f} सेकंड")
            logger.info(f"📱 Post ID: {post_id}")
            logger.info("="*60)
            return True
        else:
            logger.error("\n❌ फेसबुक पर पोस्ट नहीं हो सकी!")
            return False
            
    except Exception as e:
        logger.critical(f"\n❌ गंभीर त्रुटि (CRITICAL ERROR): {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================
# 🎯 EXECUTE
# ============================================
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
