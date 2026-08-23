import os
import sys
import time
import random
import requests
import urllib.parse
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import base64
import io

# ============================================
# 🔐 GITHUB SECRETS से VARIABLES लें
# ============================================
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
    print("❌ Facebook Credentials नहीं मिले!")
    sys.exit(1)

print(f"✅ Facebook Page ID: {FB_PAGE_ID[:5]}***")

# ============================================
# 🌐 मजबूत नेटवर्क सेशन
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
# 🎨 ULTRA HD PROMPTS - 4K Quality
# ============================================

PROMPTS = [
    # ULTRA HD - पहाड़
    "Ultra HD 8K full body shot of a gorgeous Indian woman in Himalayan mountains, wearing colorful traditional pheran, snowfall, snow-capped peaks background, cinematic lighting, hyper realistic, professional photography, Canon EOS R5, sharp focus",
    
    # ULTRA HD - राजस्थान
    "Ultra HD 8K full body portrait of a stunning Indian woman in traditional Rajasthani attire, standing in front of grand palace, golden hour lighting, majestic background, National Geographic quality, hyper realistic",
    
    # ULTRA HD - गोवा बीच
    "Ultra HD 8K full body shot of a beautiful Indian woman on Goa beach, breezy summer dress, white sand beach, blue ocean, palm trees, sunset lighting, dreamy atmosphere, professional photography, sharp focus",
    
    # ULTRA HD - दिल्ली
    "Ultra HD 8K full body portrait of an Indian woman in modern fusion wear, standing in front of Red Fort Delhi, evening lighting, historical architecture, professional photography, hyper realistic, sharp details",
    
    # ULTRA HD - केरल
    "Ultra HD 8K full body shot of a South Indian woman in traditional saree, standing on houseboat in Kerala backwaters, green palm trees, natural lighting, serene atmosphere, National Geographic quality",
    
    # ULTRA HD - जयपुर
    "Ultra HD 8K full body portrait of an Indian woman in colorful attire, walking in Jaipur's pink city bazaar, vibrant market atmosphere, warm lighting, street photography style, hyper realistic",
    
    # ULTRA HD - हरिद्वार
    "Ultra HD 8K full body shot of an Indian woman on Haridwar ghats, evening aarti background, traditional saree, holding diya, spiritual atmosphere, golden lighting, professional photography",
    
    # ULTRA HD - उदयपुर
    "Ultra HD 8K full body portrait of a woman in elegant fusion wear, standing by Lake Pichola Udaipur, lake palace visible, sunset lighting, romantic vibe, National Geographic quality",
    
    # ULTRA HD - गोल्डन टेंपल
    "Ultra HD 8K full body shot of a Sikh woman at Golden Temple Amritsar, golden temple background, salwar kameez, spiritual atmosphere, warm lighting, hyper realistic, sharp focus",
    
    # ULTRA HD - स्टूडियो
    "Ultra HD 8K full body portrait of an Indian fashion model, professional studio background, designer fusion wear, high-fashion pose, studio lighting, glamorous, sharp focus",
    
    # ULTRA HD - राजस्थानी रेगिस्तान
    "Ultra HD 8K full body portrait of a royal Rajasthani woman in desert, sand dunes background, colorful traditional outfit, golden hour, desert sunset, National Geographic quality",
    
    # ULTRA HD - कश्मीर
    "Ultra HD 8K full body shot of an Indian woman in Kashmir flower garden, pretty dress, smelling flowers, natural lighting, dreamy atmosphere, professional photography, sharp focus",
    
    # ULTRA HD - मुंबई
    "Ultra HD 8K full body portrait of a modern Indian woman on Marine Drive Mumbai, Queen's Necklace background, stylish outfit, evening lighting, city vibe, hyper realistic",
    
    # ULTRA HD - वाराणसी
    "Ultra HD 8K full body shot of an Indian woman on Varanasi ghats, Ganga river background, evening aarti, traditional saree, mystical atmosphere, professional photography",
    
    # ULTRA HD - मैसूर
    "Ultra HD 8K full body portrait of a South Indian woman in silk saree, standing in front of Mysore Palace at night, kanjivaram saree, temple jewelry, night photography, dramatic lighting",
    
    # ULTRA HD - लद्दाख
    "Ultra HD 8K full body shot of an Indian woman on Ladakh road trip, standing near jeep, mountains background, winter jacket, rugged landscape, travel photography, adventure vibe"
]

# ============================================
# 🎨 ULTRA HD IMAGE GENERATION
# ============================================

def generate_ultra_hd_image(filename="ultra_hd_photo.jpg", max_retries=5):
    """
    ULTRA HD QUALITY - Multiple Methods with Retry
    """
    print("🎨 ULTRA HD फोटो बना रहा हूँ...")
    
    for attempt in range(max_retries):
        try:
            prompt = random.choice(PROMPTS)
            # Add ULTRA HD keywords
            enhanced_prompt = f"{prompt}, 8k resolution, hyper realistic, photorealistic, National Geographic quality, cinematic lighting, sharp focus, detailed face, natural skin texture"
            
            clean_prompt = enhanced_prompt.strip().replace('\n', ' ').replace('  ', ' ')
            encoded_prompt = urllib.parse.quote(clean_prompt[:300])
            
            # METHOD 1: Pollinations with HIGHEST QUALITY
            url = (
                f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                f"?width=1536&height=2048"  # ✅ 2K Resolution
                f"&model=flux"
                f"&nologo=true"
                f"&seed={random.randint(1, 9999999)}"
                f"&quality=ultra"  # ✅ ULTRA QUALITY
                f"&enhance=true"
            )
            
            print(f"⏳ Attempt {attempt + 1}/{max_retries}: Generating ULTRA HD (1536x2048)...")
            response = session.get(url, timeout=180)
            
            if response.status_code == 200:
                content_size = len(response.content)
                print(f"📊 Image Size: {content_size/1024:.1f} KB")
                
                if content_size > 100000:  # 100KB से बड़ा
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ ULTRA HD फोटो बन गई! ({content_size/1024:.1f} KB)")
                    enhance_ultra_hd_image(filename)
                    return filename, prompt
                else:
                    print(f"⚠️ Image too small ({content_size/1024:.1f} KB), Retrying...")
                    time.sleep(2)
            else:
                print(f"❌ API Error: {response.status_code}, Retrying...")
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} Error: {e}")
            time.sleep(3)
    
    # METHOD 2: Hugging Face (if token available)
    if HF_TOKEN:
        print("🔄 Trying Hugging Face...")
        result = generate_hf_ultra_hd(filename)
        if result:
            return result, "HF Generated"
    
    # METHOD 3: Fallback with HIGHER RESOLUTION
    print("🔄 Fallback: Generating with standard resolution...")
    return generate_fallback_hd(filename), "Fallback HD"

def generate_hf_ultra_hd(filename="hf_ultra_hd.jpg"):
    """
    Hugging Face से ULTRA HD Image
    """
    try:
        prompt = random.choice(PROMPTS)
        api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        
        payload = {
            "inputs": f"{prompt}, 8k, photorealistic, sharp focus, detailed face",
            "parameters": {
                "width": 1024,
                "height": 1344,
                "num_inference_steps": 50,
                "guidance_scale": 7.5
            }
        }
        
        response = session.post(api_url, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200 and len(response.content) > 50000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ HF ULTRA HD Success! ({len(response.content)/1024:.1f} KB)")
            enhance_ultra_hd_image(filename)
            return filename
        return None
    except:
        return None

def generate_fallback_hd(filename="fallback_hd.jpg"):
    """
    Fallback HD Image
    """
    try:
        prompt = "Beautiful Indian woman full body portrait, professional photography, 8k quality, sharp focus, detailed face, studio lighting"
        encoded = urllib.parse.quote(prompt)
        
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1536&height=2048&model=flux&nologo=true&quality=ultra&enhance=true"
        response = session.get(url, timeout=180)
        
        if response.status_code == 200 and len(response.content) > 50000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Fallback HD Success! ({len(response.content)/1024:.1f} KB)")
            enhance_ultra_hd_image(filename)
            return filename
    except:
        pass
    
    return create_ultra_hd_placeholder(filename)

def create_ultra_hd_placeholder(filename="placeholder.jpg"):
    """ULTRA HD Placeholder"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (1536, 2048), color=(255, 220, 240))
        draw = ImageDraw.Draw(img)
        
        # Decorative Border
        for i in range(0, 1536, 50):
            draw.line([(i, 0), (i, 2048)], fill=(255, 200, 220), width=2)
        for i in range(0, 2048, 50):
            draw.line([(0, i), (1536, i)], fill=(255, 200, 220), width=2)
        
        # Text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            font = ImageFont.load_default()
            font2 = ImageFont.load_default()
        
        draw.text((400, 900), "✨ ULTRA HD ✨", fill=(200, 50, 100), font=font)
        draw.text((450, 1000), "AI Generated", fill=(150, 50, 80), font=font2)
        
        img.save(filename, quality=98, optimize=False)
        print(f"✅ ULTRA HD Placeholder Created!")
        return filename
    except:
        with open(filename, 'wb') as f:
            f.write(b'ULTRA_HD_PLACEHOLDER')
        return filename

# ============================================
# 👤 ULTRA HD IMAGE ENHANCEMENT
# ============================================

def enhance_ultra_hd_image(image_path):
    """
    ULTRA HD Image Enhancement - 4K Quality
    """
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        
        img = Image.open(image_path)
        width, height = img.size
        print(f"📐 Current Resolution: {width}x{height}")
        
        # 1. RESIZE TO 1536x2048 (2K)
        if width != 1536 or height != 2048:
            print(f"📐 Resizing to 1536x2048...")
            img = img.resize((1536, 2048), Image.Resampling.LANCZOS)
        
        # 2. SHARPNESS ENHANCE (Face Natural)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)  # 50% Sharpness
        
        # 3. CONTRAST ENHANCE
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)  # 20% Contrast
        
        # 4. COLOR ENHANCE
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)  # 10% Color
        
        # 5. BRIGHTNESS ENHANCE
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)  # 5% Brightness
        
        # 6. SAVE WITH MAX QUALITY
        img.save(image_path, quality=100, optimize=False, format='JPEG', subsampling=0)
        new_size = os.path.getsize(image_path)
        print(f"✅ ULTRA HD Enhanced! Size: {new_size/1024:.1f} KB")
        print(f"✅ Resolution: 1536x2048 (2K)")
        return True
        
    except Exception as e:
        print(f"⚠️ Enhancement Error: {e}")
        return False

# ============================================
# 📝 ULTRA HD CAPTIONS
# ============================================

def generate_ultra_hd_caption():
    """ULTRA HD Caption with style"""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        time_text = "🌅 Good Morning!"
    elif 12 <= hour < 17:
        time_text = "☀️ Afternoon glow"
    elif 17 <= hour < 21:
        time_text = "🌆 Evening elegance"
    else:
        time_text = "🌙 Night queen"
    
    titles = [
        "✨ ULTRA HD Quality ✨", "🌟 Next Level Beauty 🌟",
        "💫 Stunning in 2K", "📸 Ultra Sharp Quality",
        "🎯 Perfect Shot", "💎 Crystal Clear",
        "🌟 High Definition Beauty", "✨ Dreamy in HD"
    ]
    
    vibes = [
        "Royal Look 👑", "Beach Vibes 🏖️", "Mountain Queen 🏔️",
        "City Style 🏙️", "Desert Beauty 🏜️", "Garden Paradise 🌺",
        "Studio Glam 📸", "Temple Peace 🛕", "Lake Romance 🌊"
    ]
    
    questions = [
        "👇 Comment में बताओ:\n1️⃣ Quality कैसी लगी? (1-10)\n2️⃣ अगली पोस्ट कहां से हो?\n\n💡 100+ Comments = Next ULTRA HD Post!",
        "👇 3 Second mein comment karo:\n1️⃣ Kitne number doge? (1-10)\n2️⃣ किस देश का लग रहा हूँ?\n\n💡 Best Comment = Next Location!"
    ]
    
    hashtags = [
        "#UltraHD #4KQuality #AIBeauty #IndianFashion #ViralReels #ExplorePage #FYP #StyleInspo #FashionGoals #AIModel #DigitalFashion #AIArtwork #ModernBride #IndianWear #FusionFashion #AIArtist #VirtualFashion #TechStyle #InstaFashion #DailyFashion #Fashionista #AICouture #VirtualInfluencer #IndianFashionBlogger #AIForFashion",
        "#HDQuality #UltraHD #AIArt #ViralFashion #ExplorePage #FYP #StyleInspo #FashionGoals #AIModel #DigitalFashion #AIArtwork #ModernBride #IndianWear #FusionFashion #AIArtist #VirtualFashion #TechStyle #InstaFashion #DailyFashion #Fashionista #AICouture #VirtualInfluencer #IndianFashionBlogger #AIForFashion"
    ]
    
    title = random.choice(titles)
    vibe = random.choice(vibes)
    question = random.choice(questions)
    hashtag = random.choice(hashtags)
    
    return f"""{time_text}

{title} 🎬

{vibe} • {random.choice(['Now', 'Today', 'Here'])} 

📍 {random.choice(['Incredible India', 'Paradise Found', 'Dream Destination'])} 

{question}

{hashtag}
"""

# ============================================
# 📤 FACEBOOK POST (ULTRA HD)
# ============================================

def post_ultra_hd_to_facebook(image_path, caption):
    """Facebook पर ULTRA HD फोटो पोस्ट करें"""
    print("📤 Facebook पर ULTRA HD पोस्ट कर रहा हूँ...")
    
    page_id = ''.join(filter(str.isdigit, FB_PAGE_ID))
    fb_url = f"https://graph.facebook.com/{page_id}/photos"
    
    payload = {
        'caption': caption,
        'access_token': FB_ACCESS_TOKEN,
        'published': 'true'
    }
    
    try:
        with open(image_path, 'rb') as img_file:
            files = {'source': img_file}
            response = session.post(fb_url, data=payload, files=files, timeout=180)
        
        if response.status_code == 200:
            post_id = response.json().get('id')
            print(f"✅ ULTRA HD पोस्ट हो गई! Post ID: {post_id}")
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
# 🚀 MAIN BOT - ULTRA HD
# ============================================

def main():
    print("\n" + "="*60)
    print("🚀 ULTRA HD AI BOT START")
    print("📸 Resolution: 1536x2048 (2K)")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # STEP 1: ULTRA HD Image Generate
        print("\n🎨 STEP 1: ULTRA HD फोटो बना रहा हूँ...")
        image_path, prompt = generate_ultra_hd_image("ultra_hd_photo.jpg")
        
        if not image_path:
            print("❌ ULTRA HD फोटो नहीं बन पाई!")
            return False
        
        # STEP 2: ULTRA HD Caption
        print("\n📝 STEP 2: ULTRA HD कैप्शन बना रहा हूँ...")
        caption = generate_ultra_hd_caption()
        print(f"✅ Caption Ready")
        
        # STEP 3: Facebook Post
        print("\n📤 STEP 3: Facebook पर ULTRA HD पोस्ट कर रहा हूँ...")
        post_id = post_ultra_hd_to_facebook(image_path, caption)
        
        # STEP 4: Cleanup
        print("\n🧹 STEP 4: क्लीनअप...")
        cleanup_files(image_path)
        
        elapsed = time.time() - start_time
        
        if post_id:
            print("\n" + "="*60)
            print("🎉 ULTRA HD POST SUCCESS!")
            print(f"📐 Resolution: 1536x2048 (2K)")
            print(f"⏱️ Time: {elapsed:.2f}s")
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
