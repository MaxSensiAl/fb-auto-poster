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
# 🎨 IMPROVED PROMPTS - Better quality instructions
# ============================================

PROMPTS = [
    """
    Masterpiece, best quality, ultra high resolution, 8k, photorealistic portrait of a beautiful Indian bride,
    waist-up shot, traditional red bridal lehenga, intricate gold jewelry, sharp focus on face,
    highly detailed symmetrical facial features, crystal clear eyes, flawless skin texture,
    professional studio lighting, dslr photography, sharp, no blur, perfect clarity,
    hyper realistic, detailed skin pores, natural looking, cinematic lighting, award winning photography.
    """,
    
    """
    Masterpiece, best quality, photorealistic waist-up portrait of a Bollywood actress,
    modern designer fusion wear, perfect symmetrical face, sharp focus, detailed eyes,
    natural skin texture, professional studio photography, 8k resolution, crystal clear,
    no blur, ultra sharp, high definition, perfect lighting, fashion editorial style.
    """,
    
    """
    Masterpiece, best quality, ultra realistic waist-up portrait of a South Indian woman,
    traditional silk saree, kanjivaram fabric, sharp facial features, clear eyes,
    natural skin, professional portrait photography, 8k, highly detailed, no blur,
    perfect composition, soft natural lighting, temple background.
    """,
    
    """
    Masterpiece, best quality, photorealistic waist-up portrait of a Rajasthani royal woman,
    heavy embroidered lehenga, silver jewelry, palace background, sharp focus on face,
    detailed eyes, natural skin texture, golden sunset lighting, 8k resolution,
    crystal clear, no blur, ultra sharp, professional photography.
    """,
    
    """
    Masterpiece, best quality, 8k photorealistic waist-up portrait of a modern Indian woman,
    pastel saree, minimalist background, perfect symmetrical face, clear detailed eyes,
    natural skin, sharp focus, no blur, studio lighting, fashion photography,
    high definition, crystal clear, ultra sharp.
    """,
    
    """
    Masterpiece, best quality, photorealistic waist-up portrait of an Indian woman celebrating Diwali,
    mirror-work lehenga, happy expression, sharp facial features, detailed eyes,
    festive lighting, professional photography, 8k, no blur, crystal clear,
    ultra sharp, perfect composition.
    """,
    
    """
    Masterpiece, best quality, 8k photorealistic waist-up portrait of an Indian wedding guest,
    elegant designer wear, soft romantic lighting, sharp focus on face,
    detailed eyes, natural skin texture, wedding hall background, no blur,
    crystal clear, professional photography, high definition.
    """,
    
    """
    Masterpiece, best quality, photorealistic waist-up portrait of a Kashmiri beauty,
    traditional embroidered pheran, snow mountains background, sharp facial features,
    clear eyes, natural fair skin, soft winter light, 8k, no blur,
    crystal clear, ultra sharp, professional portrait.
    """
]

def create_default_prompt():
    return random.choice(PROMPTS)

# ============================================
# 📸 1. INSTAGRAM STYLE
# ============================================

def learn_style_from_instagram():
    print(f"📸 Instagram Login Skip - Using Manual Style Prompts")
    print(f"🎯 Target Profile: @{TARGET_PROFILE}")
    selected_prompt = random.choice(PROMPTS)
    print(f"✅ Selected Prompt: {selected_prompt[:100]}...")
    return selected_prompt

# ============================================
# 🎨 2. HUGGING FACE IMAGE GENERATION
# ============================================

def generate_ai_image_hf(prompt_text, model_id="playgroundai/playground-v2.5-1024px-aesthetic", filename="generated_photo.jpg"):
    if not HF_TOKEN:
        print("⚠️ HF_TOKEN नहीं मिला!")
        return None
        
    print(f"🚀 Hugging Face से जनरेट कर रहा हूँ...")
    api_url = f"https://api-inference.hf-mirror.com/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    payload = {
        "inputs": prompt_text,
        "parameters": {
            "width": 1024,
            "height": 1280,
            "guidance_scale": 9.0,
            "num_inference_steps": 60,
            "negative_prompt": "blurry, low quality, distorted face, bad anatomy, ugly, deformed, pixelated"
        }
    }
    
    try:
        response = session.post(api_url, headers=headers, json=payload, timeout=180)
        
        if response.status_code == 503:
            estimated_time = response.json().get("estimated_time", 20)
            print(f"⏳ मॉडल लोड हो रहा है, {estimated_time:.1f} सेकंड प्रतीक्षा...")
            time.sleep(min(estimated_time, 40))
            response = session.post(api_url, headers=headers, json=payload, timeout=180)
            
        if response.status_code == 200 and len(response.content) > 50000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print("✅ Hugging Face से फोटो सफलतापूर्वक डाउनलोड हो गई!")
            return filename
        else:
            print(f"❌ HF Model Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ HF Error: {e}")
        return None

def generate_ai_hercai(prompt_text, filename="generated_photo.jpg"):
    print("🚀 Hercai V3 से फोटो बना रहा हूँ...")
    url = "https://hercai.onrender.com/v3/hercai"
    
    payload = {
        "prompt": prompt_text + ", masterpiece, best quality, 8k, photorealistic, sharp focus, no blur, crystal clear, highly detailed",
        "model": "v3"
    }
    
    try:
        response = session.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            img_url = data.get("reply")
            
            if img_url:
                print("📥 फोटो डाउनलोड कर रहा हूँ...")
                img_response = session.get(img_url, timeout=120)
                if img_response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(img_response.content)
                    print("✅ Hercai V3 से फोटो डाउनलोड हो गई!")
                    return filename
    except Exception as e:
        print(f"❌ Hercai V3 Error: {e}")
    return None

def generate_ai_image(prompt_text, filename="generated_photo.jpg"):
    print("\n🎨 [इमेज जनरेटर] शुरू हो रहा है...")
    
    # LAYER 1: Playground v2.5
    image_path = generate_ai_image_hf(prompt_text, "playgroundai/playground-v2.5-1024px-aesthetic", filename)
    if image_path and os.path.getsize(image_path) > 50000:
        enhance_image_quality(image_path)
        return image_path
        
    # LAYER 2: Hercai V3
    image_path = generate_ai_hercai(prompt_text, filename)
    if image_path and os.path.getsize(image_path) > 50000:
        enhance_image_quality(image_path)
        return image_path

    # LAYER 3: Pollinations
    print("🔄 Pollinations बैकअप पर स्विच...")
    clean_prompt = prompt_text.strip().replace('\n', ' ').replace('  ', ' ')
    encoded_prompt = urllib.parse.quote(clean_prompt[:250])
    
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1280"
        f"&model=flux-realism"
        f"&nologo=true"
        f"&seed={random.randint(1, 9999999)}"
        f"&quality=high"
        f"&enhance=true"
    )
    
    try:
        response = session.get(flux_url, timeout=120)
        if response.status_code == 200 and len(response.content) > 80000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print("✅ Pollinations से फोटो जनरेट हो गई!")
            enhance_image_quality(filename)
            return filename
    except Exception as e:
        print(f"❌ Pollinations Error: {e}")
        
    return create_placeholder_image(filename)

def generate_ai_image_simple(filename="generated_photo.jpg"):
    print("🔄 Simple Prompt Retry...")
    simple_prompts = [
        "Masterpiece, best quality, photorealistic portrait of beautiful Indian bride, waist-up, sharp focus, 8k, crystal clear, no blur",
        "Masterpiece, 8k photorealistic portrait of Indian woman in saree, waist-up, sharp, clear, no blur"
    ]
    simple_prompt = random.choice(simple_prompts)
    return generate_ai_image(simple_prompt, filename)

def create_placeholder_image(filename="placeholder.jpg"):
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (1024, 1280), color=(255, 200, 230))
        draw = ImageDraw.Draw(img)
        text = "✨ AI Beauty ✨"
        try:
            font = ImageFont.load_default()
        except:
            font = None
        draw.text((400, 600), text, fill=(200, 50, 100), font=font)
        img.save(filename)
        print(f"✅ Placeholder Image बन गई!")
        return filename
    except:
        with open(filename, 'wb') as f:
            f.write(b'PLACEHOLDER_IMAGE')
        return filename

# ============================================
# 🖼️ IMAGE ENHANCE - FIXED
# ============================================

def enhance_image_quality(image_path):
    """
    Image Quality Enhance - Blur हटाने के लिए
    """
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        
        # FIX: Use os.path.getsize instead of os.getsize
        if not os.path.exists(image_path) or os.path.getsize(image_path) < 10000:
            print("⚠️ Image too small or not exists!")
            return False
            
        img = Image.open(image_path)
        width, height = img.size
        print(f"📐 Current Resolution: {width}x{height}")
        
        # अगर resolution बहुत छोटा है तो बड़ा करें
        if width < 1024 or height < 1024:
            # Upscale 2x using LANCZOS
            new_width = width * 2
            new_height = height * 2
            print(f"📐 Resizing: {width}x{height} → {new_width}x{new_height}")
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Sharpness Enhance - ब्लर हटाने के लिए
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.5)  # Sharpness बढ़ाएं
        
        # Unsharp Mask for professional sharpening
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=200, threshold=2))
        
        # Contrast Enhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.15)
        
        # Color Enhance
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)
        
        # High Quality Save
        img.save(image_path, quality=98, optimize=True, format='JPEG', subsampling=0)
        
        # Check if enhancement worked
        new_size = os.path.getsize(image_path)
        print(f"✅ Enhanced! New Size: {new_size/1024:.1f} KB")
        return True
        
    except Exception as e:
        print(f"⚠️ Enhancement Error: {e}")
        return False

# ============================================
# 📷 PHOTO QUALITY CHECK - FIXED
# ============================================

def check_image_quality(image_path):
    print("📷 Photo Quality Check कर रहा हूँ...")
    
    try:
        # FIX: Use os.path.getsize instead of os.getsize
        if not os.path.exists(image_path):
            print("❌ File exists नहीं है!")
            return False
        
        file_size = os.path.getsize(image_path)  # ✅ Fixed here
        print(f"📊 File Size: {file_size/1024:.1f} KB")
        
        if file_size < 50000:
            print("❌ File Size बहुत छोटी है! (< 50KB)")
            return False
        
        try:
            from PIL import Image
            img = Image.open(image_path)
            width, height = img.size
            print(f"📐 Resolution: {width}x{height}")
            
            if width < 1024 or height < 1024:
                print(f"❌ Resolution बहुत कम है! ({width}x{height})")
                return False
            
            img.verify()
            print("✅ Image Valid है!")
            return True
            
        except ImportError:
            return file_size > 50000
                
    except Exception as e:
        print(f"❌ Quality Check Error: {e}")
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

#AIFashion #IndianBeauty #AIArt #ViralFashion #ExplorePage #FYP #StyleInspo #FashionGoals #AIModel #DigitalFashion""",
        
        f"""{time_text}

🔥 AI ने बनाया ये Stunning Look! 💃

क्या आपको लगता है ये Real है या AI? 🤔
👇 3 Second mein comment karo:
1️⃣ Rate करो (1-10)
2️⃣ Sabse best kya hai?

💡 50+ Comments = Next Post Aaj Raat hi!

#AIBride #IndianWedding #AIArt #TrendingReels #ViralPost #FYP #ExplorePage #AIFashion #BridalWear #AICommunity""",
        
        f"""{time_text}

💃 AI Generated - Royal Indian Beauty! 👑

कौन सा style सबसे best लगा?
👇 Comment में बताओ:
👑 Traditional
💎 Modern
🌸 Fusion

🎯 200+ Votes = Next Look Special!

#RoyalBeauty #IndianFashion #AIArt #ViralReels #ExplorePage #FYP #TraditionalWear #ModernFashion #AICouture"""
    ]
    
    return random.choice(captions)

# ============================================
# 📤 FACEBOOK POST
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
    print("🚀 INSTAGRAM STYLE AI BOT START (FIXED)")
    print("="*60)
    
    start_time = time.time()
    
    try:
        print("\n📸 STEP 1: Style Select...")
        style_prompt = learn_style_from_instagram()
        
        print("\n🎨 STEP 2: AI से फोटो बना रहा हूँ...")
        image_path = generate_ai_image(style_prompt, "instagram_style_photo.jpg")
        
        if not image_path:
            print("❌ फोटो नहीं बन पाई!")
            return False
        
        # Quality Check
        print("\n📷 STEP 3: Photo Quality Check...")
        quality_ok = check_image_quality(image_path)
        
        if not quality_ok:
            print("⚠️ Quality Check Fail! Retry...")
            image_path = generate_ai_image_simple("retry_photo.jpg")
            if image_path:
                quality_ok = check_image_quality(image_path)
                if not quality_ok:
                    print("⚠️ Quality फिर Fail! Placeholder...")
                    image_path = create_placeholder_image("placeholder_final.jpg")
        
        # Caption
        print("\n📝 STEP 4: कैप्शन बना रहा हूँ...")
        caption = generate_caption()
        print(f"✅ Caption: {caption[:150]}...")
        
        # Post
        print("\n📤 STEP 5: Facebook पर पोस्ट...")
        post_id = post_to_facebook(image_path, caption)
        
        # Cleanup
        print("\n🧹 STEP 6: Cleanup...")
        cleanup_files(image_path, "retry_photo.jpg", "placeholder_final.jpg")
        
        elapsed = time.time() - start_time
        
        if post_id:
            print("\n" + "="*60)
            print("🎉 SUCCESS!")
            print(f"⏱️ Time: {elapsed:.2f} सेकंड")
            print(f"📱 Post ID: {post_id}")
            print("="*60)
            return True
        else:
            print("\n❌ पोस्ट नहीं हो पाई!")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
