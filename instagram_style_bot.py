import os
import sys
import time
import random
import requests
import urllib.parse
from datetime import datetime
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
# 🎨 MULTIPLE PROMPTS (फुल-बॉडी तस्वीरों के लिए)
# ============================================

PROMPTS = [
    # 1. Traditional Indian Bride (Full Body)
    """
    A stunning full-body portrait of an Indian bride standing gracefully, 
    complete head-to-toe shot showing the entire traditional red bridal lehenga with intricate gold embroidery.
    Symmetrical facial features, detailed clear eyes, natural skin texture.
    Beautiful jewelry, maang tikka, and elegant hand pose.
    Soft golden hour lighting in a heritage palace background.
    8k resolution, photorealistic, professional fashion photography, sharp focus.
    """,
    
    # 2. Modern Bollywood Style (Full Length)
    """
    A glamorous full-length fashion editorial shot of a Bollywood actress, 
    standing pose showing her complete modern fusion gown, elegant design.
    Symmetrical facial features, detailed eyes, natural skin.
    Studio lighting with soft shadows, professional high-fashion pose.
    Sony A7R IV, 35mm lens, sharp focus from head to toe, dramatic look.
    """,
    
    # 3. South Indian Beauty (Knee-Up/Full Body)
    """
    A beautiful full-body portrait of a South Indian woman standing gracefully, 
    wearing a rich kanjivaram silk saree with a traditional gold border, 
    saree draping visible from head to toe.
    Temple jewelry, jasmine flowers in hair, warm natural sunlight.
    Symmetrical face, sharp details, heritage temple architecture background.
    Nikon Z9, professional composition.
    """,
    
    # 4. Royal Rajasthani Style (Full Body)
    """
    A regal Rajasthani woman standing in a heritage palace courtyard, 
    full-body shot displaying her complete traditional ghoonghat and heavy silver-embroidered lehenga.
    Bandhani dupatta draping, royal jewelry, golden hour lighting.
    Symmetrical face, majestic pose, warm desert tones.
    Leica M11, sharp focus, rich details.
    """,
    
    # 5. Modern Minimalist (Full Body)
    """
    A modern Indian woman in minimalist style, 
    full-length standing portrait showing a simple elegant modern pastel saree.
    Symmetrical face, clean natural skin, subtle jewelry.
    Clean minimalist aesthetic background, soft natural light, contemporary sophisticated look.
    Professional photography, sharp focus on the whole body.
    """,
    
    # 6. Festival Special (Full Body)
    """
    A joyful Indian woman celebrating Diwali, 
    full-body standing pose showing her entire mirror-work lehenga.
    Festive lighting, diyas glowing on the ground around her feet.
    Symmetrical face, happy expression, vibrant colors.
    Canon EOS R3, sharp focus from head to toe, celebratory atmosphere.
    """,
    
    # 7. Wedding Guest Look (Full Body)
    """
    A beautiful Indian woman in wedding guest attire, 
    full-length standing shot showing her elegant designer anarkali suit or lehenga.
    Symmetrical facial features, natural skin, soft romantic lighting.
    Dreamy floral background, soft bokeh around her feet.
    Professional wedding photography style, rich details.
    """,
    
    # 8. Kashmiri Beauty (Full Length)
    """
    A Kashmiri woman standing elegantly, 
    full-body portrait wearing a traditional embroidered long pheran, 
    snow-capped mountains and chinar trees background.
    Natural winter sunlight, symmetric face, serene pose.
    Nikon D850, crystal clear sharp focus, realistic textures.
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
# 🎨 2. AI से PHOTO GENERATE करें (High Quality)
# ============================================

def generate_ai_image(prompt_text, filename="generated_photo.jpg"):
    """
    FLUX AI से हाई-क्वालिटी फुल-बॉडी फोटो जनरेट करें
    """
    print("🎨 AI से High Quality फोटो बना रहा हूँ...")
    
    clean_prompt = prompt_text.strip().replace('\n', ' ').replace('  ', ' ')
    encoded_prompt = urllib.parse.quote(clean_prompt[:250])
    
    # ✅ फुल-बॉडी के लिए आस्पेक्ट रेशियो 1024x1536 (2:3 Ratio) किया गया
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1536"  # ✅ फुल-बॉडी के लिए बेहतरीन लंबाई
        f"&model=flux"
        f"&nologo=true"
        f"&seed={random.randint(1, 9999999)}"
        f"&quality=high"  
        f"&enhance=true"  
    )
    
    try:
        print("⏳ 30-60 सेकंड लग सकते हैं...")
        response = requests.get(flux_url, timeout=180)
        
        if response.status_code == 200:
            content_size = len(response.content)
            if content_size > 50000:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ फोटो बन गई! ({content_size/1024:.1f} KB)")
                
                # ✅ Image Enhance
                enhance_image_quality(filename)
                return filename
            else:
                print(f"⚠️ फोटो बहुत छोटी है ({content_size} bytes)")
                return generate_ai_image_simple(filename)
        else:
            print(f"❌ AI Error: {response.status_code}")
            return generate_ai_image_simple(filename)
            
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return generate_ai_image_simple(filename)

def generate_ai_image_simple(filename="generated_photo.jpg"):
    """
    सरल प्रॉम्प्ट के साथ Retry
    """
    print("🔄 सरल प्रॉम्प्ट के साथ Retry कर रहा हूँ...")
    
    simple_prompts = [
        "Stunning Indian bride, standing pose, full-body shot from head to toe, traditional red dress, professional photography",
        "Beautiful Indian woman in saree, full-length standing portrait, detailed face, professional studio shot",
        "Glamorous Bollywood actress, standing pose, full-body shot, elegant gown, fashion photography",
        "Elegant Indian woman in traditional jewelry, full body shot, heritage architecture background"
    ]
    
    simple_prompt = random.choice(simple_prompts)
    encoded = urllib.parse.quote(simple_prompt)
    
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1536&model=flux&nologo=true&quality=high&enhance=true"
    
    try:
        response = requests.get(url, timeout=180)
        if response.status_code == 200 and len(response.content) > 50000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Retry Success! ({len(response.content)/1024:.1f} KB)")
            enhance_image_quality(filename)
            return filename
    except:
        pass
    
    print("⚠️ Placeholder Image बना रहा हूँ...")
    return create_placeholder_image(filename)

def create_placeholder_image(filename="placeholder.jpg"):
    """
    अगर AI काम न करे तो Placeholder Image बनाएं
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (1024, 1536), color=(255, 200, 230))
        draw = ImageDraw.Draw(img)
        
        text = "✨ AI Beauty Full Shot ✨"
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((350, 700), text, fill=(200, 50, 100), font=font)
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
    Image Quality Enhance
    """
    try:
        from PIL import Image, ImageEnhance
        
        img = Image.open(image_path)
        width, height = img.size
        print(f"📐 Current Resolution: {width}x{height}")
        
        if width < 1024 or height < 1536:
            new_width = 1024
            new_height = 1536
            print(f"📐 Resizing: {width}x{height} → {new_width}x{new_height}")
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 2. Sharpness Enhance (प्राकृतिक लुक बनाए रखने के लिए)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.1)  
        
        # 3. Contrast Enhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.05)  
        
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
    """
    Photo Quality Check
    """
    print("📷 Photo Quality Check कर रहा हूँ...")
    try:
        if not os.path.exists(image_path):
            print("❌ File exists नहीं है!")
            return False
        
        file_size = os.path.getsize(image_path)
        print(f"📊 File Size: {file_size/1024:.1f} KB")
        
        if file_size < 10000:
            print("❌ File Size बहुत छोटी है!")
            return False
        
        try:
            from PIL import Image
            img = Image.open(image_path)
            width, height = img.size
            print(f"📐 Resolution: {width}x{height}")
            
            if width < 512 or height < 512:
                print(f"❌ Resolution बहुत कम है!")
                return False
            
            img.verify()
            print("✅ Image Valid है!")
            return True
            
        except ImportError:
            if file_size > 10000:
                return True
            return False
                
    except Exception as e:
        print(f"❌ Quality Check Error: {e}")
        return False

# ============================================
# 📝 3. CAPTION GENERATE करें
# ============================================

def generate_caption():
    """
    Viral Instagram-style Caption
    """
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

✨ AI Generated Full Look! 🤩

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
    """
    Facebook Page पर फोटो पोस्ट करें
    """
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
    print("🚀 INSTAGRAM STYLE AI BOT START (FULL BODY MODE)")
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
        
        # STEP 2.5: Photo Quality Check
        print("\n📷 STEP 2.5: Photo Quality Check...")
        quality_ok = check_image_quality(image_path)
        
        if not quality_ok:
            print("⚠️ Quality Check Fail हुई! री-ट्राई कर रहा हूँ...")
            image_path = generate_ai_image_simple("retry_photo.jpg")
            if image_path:
                quality_ok = check_image_quality(image_path)
                if not quality_ok:
                    image_path = create_placeholder_image("placeholder_final.jpg")
        
        # STEP 3: कैप्शन बनाएं
        print("\n📝 STEP 3: कैप्शन बना रहा हूँ...")
        caption = generate_caption()
        
        # STEP 4: Facebook पर पोस्ट करें
        print("\n📤 STEP 4: Facebook पर पोस्ट कर रहा हूँ...")
        post_id = post_to_facebook(image_path, caption)
        
        # STEP 5: क्लीनअप
        print("\n🧹 STEP 5: क्लीनअप...")
        cleanup_files(image_path, "retry_photo.jpg", "placeholder_final.jpg")
        
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
