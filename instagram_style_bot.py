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
# 🎨 MULTIPLE PROMPTS (बेहतर चेहरे और क्वालिटी के लिए)
# ============================================

PROMPTS = [
    # 1. Traditional Indian Bride
    """
    A stunning high-quality portrait of an Indian bride, 
    highly detailed symmetrical facial features, realistic clear eyes, 
    natural skin texture, sharp focus on face.
    Traditional red bridal wear with gold embroidery.
    Beautiful jewelry, maang tikka, and earrings.
    Soft golden hour lighting, dreamy background.
    8k resolution, photorealistic, professional.
    Canon EOS R5, 85mm lens, f/1.4.
    Same face, same character.
    """,
    
    # 2. Modern Bollywood Style
    """
    A glamorous Bollywood actress portrait, 
    symmetrical facial features, detailed eyes, natural skin structure.
    Modern fusion wear with intricate detailing.
    Studio lighting with soft shadows.
    Professional makeup, perfect skin texture.
    High fashion editorial style.
    Sony A7R IV, 50mm lens, f/1.8.
    Cinematic, dramatic, stunning.
    """,
    
    # 3. South Indian Beauty
    """
    A traditional South Indian woman in silk saree, 
    highly detailed symmetrical face, clear eyes, natural skin.
    Rich kanjivaram saree with gold border.
    Temple jewelry, jasmine flowers in hair.
    Natural sunlight, temple architecture background.
    Authentic, cultural, beautiful, sharp focus on face.
    Nikon Z9, 85mm lens.
    Vibrant colors, sharp details.
    """,
    
    # 4. Royal Rajasthani Style
    """
    A royal Rajasthani woman in traditional attire, 
    clear symmetrical facial features, highly detailed eyes, realistic look.
    Bandhani dupatta, heavy silver jewelry.
    Desert palace background, golden hour.
    Regal, elegant, majestic, sharp focus.
    Leica M11, 50mm Summilux.
    Warm tones, rich textures.
    """,
    
    # 5. Modern Minimalist
    """
    A modern Indian woman in minimalist style, 
    symmetrical face, natural skin texture, highly detailed facial features.
    Simple elegant outfit, subtle jewelry.
    Clean white background, soft natural light.
    Contemporary, fresh, sophisticated.
    Professional headshot quality, sharp focus on face.
    """,
    
    # 6. Festival Special
    """
    An Indian woman celebrating Diwali, 
    happy expression, symmetrical facial features, clear realistic eyes.
    Traditional lehenga with mirror work.
    Diya background, festive lighting.
    Joyful expression, vibrant colors, sharp focus on face.
    Canon EOS R3, 24-70mm lens.
    Festive, warm, celebratory.
    """,
    
    # 7. Wedding Guest Look
    """
    A beautiful woman in wedding guest attire, 
    highly detailed symmetrical face, natural skin, realistic features.
    Elegant saree or lehenga.
    Soft romantic lighting.
    Floral background, dreamy atmosphere, sharp focus on face.
    Professional wedding photography style.
    Rich colors, soft bokeh.
    """,
    
    # 8. Kashmiri Beauty
    """
    A Kashmiri woman in traditional pheran, 
    highly detailed symmetrical face, clear eyes, natural realistic skin.
    Snow-capped mountains background.
    Natural winter lighting, sharp focus on face.
    Authentic, cultural, serene.
    Nikon D850, 70-200mm lens.
    Crystal clear, sharp focus.
    """
]

def create_default_prompt():
    """
    Randomly select a prompt for variety
    """
    return random.choice(PROMPTS)

# ============================================
# 📸 1. INSTAGRAM STYLE (Skip Login)
# ============================================

def learn_style_from_instagram():
    """
    Instagram Login Skip - Directly Use Default Prompt
    """
    print(f"📸 Instagram Login Skip - Using Manual Style Prompts")
    print(f"🎯 Target Profile: @{TARGET_PROFILE}")
    print(f"🔄 Random Prompt Selected for Variety")
    
    # Return random prompt from PROMPTS list
    selected_prompt = random.choice(PROMPTS)
    print(f"✅ Selected Prompt: {selected_prompt[:100]}...")
    
    return selected_prompt

# ============================================
# 🎨 2. HUGGING FACE से PHOTO GENERATE करें (Playground v2.5)
# ============================================

def generate_ai_image_hf(prompt_text, model_id="playgroundai/playground-v2.5-1024px-aesthetic", filename="generated_photo.jpg"):
    """
    Hugging Face Mirror का उपयोग करके Playground v2.5 से फोटो जनरेट करें
    """
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
        
        # यदि मॉडल लोड हो रहा है, तो प्रतीक्षा करें
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
        else:
            print(f"❌ HF Model Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ HF Mirror Connection Error: {e}")
        return None


def generate_ai_hercai(prompt_text, filename="generated_photo.jpg"):
    """
    Hercai V3 (Stable Diffusion XL) - 100% मुफ्त लाइव जनरेशन (चेहरे और हाथों के लिए बेस्ट)
    """
    print("🚀 [लेयर 2] Hercai V3 (Stable Diffusion XL) से लाइव फोटो बना रहा हूँ...")
    url = "https://hercai.onrender.com/v3/hercai"
    
    payload = {
        "prompt": prompt_text,
        "model": "v3"  # v3 मॉडल SDXL है जो चेहरे और शरीर को बिल्कुल असली दिखाता है
    }
    
    try:
        response = session.post(url, json=payload, timeout=90)
        if response.status_code == 200:
            data = response.json()
            img_url = data.get("reply")  # Hercai जनरेट की गई इमेज का सीधा लिंक 'reply' में देता है
            
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
    3-लेयर इमेज जनरेटर: 
    1. पहले Playground v2.5 (Hugging Face) का प्रयास
    2. विफल होने पर Hercai V3 (SDXL) का प्रयास
    3. अंत में Pollinations (Flux-Realism) पर स्विच
    """
    print("\n🎨 [इमेज जनरेटर] 3-लेयर प्रक्रिया शुरू हो रही है...")
    
    # LAYER 1: Playground v2.5 (Hugging Face Mirror)
    image_path = generate_ai_image_hf(prompt_text, "playgroundai/playground-v2.5-1024px-aesthetic", filename)
    if image_path:
        enhance_image_quality(image_path)
        return image_path
        
    # LAYER 2: Hercai V3 (Stable Diffusion XL)
    image_path = generate_ai_hercai(prompt_text, filename)
    if image_path:
        enhance_image_quality(image_path)
        return image_path

    # LAYER 3: Pollinations (Flux-Realism)
    print("🔄 [लेयर 3] पोलिनेशंस बैकअप सर्वर पर स्विच कर रहा हूँ...")
    clean_prompt = prompt_text.strip().replace('\n', ' ').replace('  ', ' ')
    encoded_prompt = urllib.parse.quote(clean_prompt[:250])
    
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1280"  
        f"&model=flux-realism"  # यथार्थवादी चेहरे के लिए स्पेशल बैकअप मॉडल
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
            enhance_image_quality(filename)
            return filename
    except Exception as e:
        print(f"❌ पोलिनेशंस बैकअप सर्वर विफल: {e}")
        
    return create_placeholder_image(filename)


def generate_ai_image_simple(filename="generated_photo.jpg"):
    """
    सरल प्रॉम्प्ट के साथ Retry
    """
    print("🔄 सरल प्रॉम्प्ट के साथ Retry कर रहा हूँ...")
    
    simple_prompts = [
        "Beautiful Indian bride in traditional red dress, symmetrical face, clear eyes, professional photography, realistic skin",
        "Stunning Indian woman in saree, symmetrical facial features, realistic eyes, professional portrait",
        "Glamorous Bollywood actress portrait, symmetrical face, professional photography, studio lighting",
        "Elegant Indian woman in traditional jewelry, detailed face, soft lighting, professional photo"
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
# 🖼️ IMAGE ENHANCE
# ============================================

def enhance_image_quality(image_path):
    """
    Image Quality Enhance - संतुलित सेटिंग्स के साथ
    """
    try:
        from PIL import Image, ImageEnhance
        
        img = Image.open(image_path)
        
        # 1. Resolution Check
        width, height = img.size
        print(f"📐 Current Resolution: {width}x{height}")
        
        if width < 1024 or height < 1280:
            new_width = 1024
            new_height = 1280
            print(f"📐 Resizing: {width}x{height} → {new_width}x{new_height}")
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 2. Sharpness Enhance (चेहरे की त्वचा को प्राकृतिक रखने के लिए इसे कम किया गया)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.02)  # चेहरे के लुक को प्राकृतिक बनाए रखने के लिए हल्का सुधार
        
        # 3. Contrast Enhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.02)  
        
        # 4. High Quality Save
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
            print("❌ File exists नहीं है!")
            return False
        
        file_size = os.path.getsize(image_path)
        print(f"📊 File Size: {file_size/1024:.1f} KB")
        
        if file_size < 10000:  
            print("❌ File Size बहुत छोटी है! (< 10KB)")
            return False
        
        try:
            from PIL import Image
            img = Image.open(image_path)
            width, height = img.size
            print(f"📐 Resolution: {width}x{height}")
            
            if width < 512 or height < 512:
                print(f"❌ Resolution बहुत कम है! ({width}x{height})")
                return False
            
            img.verify()
            print("✅ Image Valid है!")
            return True
            
        except ImportError:
            if file_size > 10000:
                return True
            else:
                return False
                
    except Exception as e:
        print(f"❌ Quality Check Error: {e}")
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
# 🧹 5. CLEANUP
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
# 🚀 6. MAIN BOT
# ============================================

def main():
    print("\n" + "="*60)
    print("🚀 INSTAGRAM STYLE AI BOT START (3-LAYER ENGINE)")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # STEP 1: Style Select (Instagram Skip)
        print("\n📸 STEP 1: Style Select...")
        style_prompt = learn_style_from_instagram()
        
        print(f"✅ Selected Style: {style_prompt[:100]}...")
        
        # STEP 2: AI से फोटो बनाएं
        print("\n🎨 STEP 2: AI से फोटो बना रहा हूँ...")
        image_path = generate_ai_image(style_prompt, "instagram_style_photo.jpg")
        
        if not image_path:
            print("❌ फोटो नहीं बन पाई!")
            return False
        
        # ✅ STEP 2.5: Photo Quality Check
        print("\n📷 STEP 2.5: Photo Quality Check...")
        quality_ok = check_image_quality(image_path)
        
        if not quality_ok:
            print("⚠️ Quality Check Fail हुई! नई फोटो बना रहा हूँ...")
            # Retry with simple prompt
            image_path = generate_ai_image_simple("retry_photo.jpg")
            if image_path:
                # Check quality again
                quality_ok = check_image_quality(image_path)
                if not quality_ok:
                    print("⚠️ Quality Check फिर Fail हुई! Placeholder use कर रहा हूँ...")
                    image_path = create_placeholder_image("placeholder_final.jpg")
        
        # STEP 3: कैप्शन बनाएं
        print("\n📝 STEP 3: कैप्शन बना रहा हूँ...")
        caption = generate_caption()
        print(f"✅ कैप्शन तैयार ({len(caption)} अक्षर)")
        print(f"📝 Caption Preview: {caption[:150]}...")
        
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
