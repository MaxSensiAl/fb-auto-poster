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
# 🎨 FULL BODY PROMPTS (पूरे शरीर की फोटो के लिए)
# ============================================

PROMPTS = [
    # 1. Traditional Indian Bride - Full Body
    """
    A stunning full-body portrait of an Indian bride, 
    highly detailed from head to toe, complete traditional bridal attire.
    Symmetrical facial features, realistic clear eyes, natural skin texture.
    Traditional red bridal lehenga with gold embroidery, full outfit visible.
    Beautiful jewelry, maang tikka, earrings, and bridal accessories.
    Standing gracefully, full body shot, feet to head.
    Soft golden hour lighting, dreamy background.
    8k resolution, photorealistic, professional.
    Canon EOS R5, 85mm lens, f/1.4.
    Same face, same character.
    """,
    
    # 2. Modern Bollywood Style - Full Body
    """
    A glamorous Bollywood actress full-body portrait,
    standing confidently, complete outfit from feet to head.
    Symmetrical facial features, detailed eyes, natural skin structure.
    Modern fusion wear with intricate detailing, full ensemble visible.
    Studio lighting with soft shadows.
    Professional makeup, perfect skin texture.
    High fashion editorial style, full body shot.
    Sony A7R IV, 50mm lens, f/1.8.
    Cinematic, dramatic, stunning.
    """,
    
    # 3. South Indian Beauty - Full Body
    """
    A traditional South Indian woman full-body portrait in silk saree,
    complete from head to toe, saree fully visible.
    Highly detailed symmetrical face, clear eyes, natural skin.
    Rich kanjivaram saree with gold border, full outfit.
    Temple jewelry, jasmine flowers in hair.
    Standing gracefully, full body visible.
    Natural sunlight, temple architecture background.
    Authentic, cultural, beautiful, sharp focus.
    Nikon Z9, 85mm lens.
    Vibrant colors, sharp details.
    """,
    
    # 4. Royal Rajasthani Style - Full Body
    """
    A royal Rajasthani woman full-body portrait,
    standing gracefully, complete traditional attire visible.
    Clear symmetrical facial features, highly detailed eyes.
    Bandhani dupatta, heavy silver jewelry, full ensemble.
    Desert palace background, golden hour.
    Full body shot, head to toe.
    Regal, elegant, majestic, sharp focus.
    Leica M11, 50mm Summilux.
    Warm tones, rich textures.
    """,
    
    # 5. Modern Minimalist - Full Body
    """
    A modern Indian woman full-body portrait,
    standing confidently, complete outfit visible.
    Symmetrical face, natural skin texture.
    Simple elegant outfit, subtle jewelry.
    Clean white background, soft natural light.
    Full body shot, head to toe.
    Contemporary, fresh, sophisticated.
    Professional quality, sharp focus.
    """,
    
    # 6. Festival Special - Full Body
    """
    An Indian woman full-body portrait celebrating Diwali,
    complete traditional attire from head to toe.
    Happy expression, symmetrical facial features.
    Traditional lehenga with mirror work, fully visible.
    Diya background, festive lighting.
    Full body shot, standing gracefully.
    Joyful expression, vibrant colors.
    Canon EOS R3, 24-70mm lens.
    Festive, warm, celebratory.
    """,
    
    # 7. Wedding Guest Look - Full Body
    """
    A beautiful woman full-body portrait in wedding guest attire,
    complete outfit from head to toe.
    Highly detailed symmetrical face, natural skin.
    Elegant saree or lehenga, fully visible.
    Soft romantic lighting, floral background.
    Full body shot, standing pose.
    Professional wedding photography style.
    Rich colors, soft bokeh.
    """,
    
    # 8. Kashmiri Beauty - Full Body
    """
    A Kashmiri woman full-body portrait in traditional pheran,
    complete attire from head to toe visible.
    Highly detailed symmetrical face, clear eyes.
    Snow-capped mountains background.
    Natural winter lighting, full body shot.
    Authentic, cultural, serene.
    Nikon D850, 70-200mm lens.
    Crystal clear, sharp focus.
    """,
    
    # 9. Full Body - Standing Pose
    """
    A stunning Indian woman full-body portrait,
    standing gracefully, complete outfit visible.
    Symmetrical facial features, realistic eyes.
    Beautiful traditional or modern attire.
    Full body shot from head to toe.
    Professional photography, sharp focus.
    Natural lighting, dreamy background.
    8k resolution, photorealistic.
    Same face, same character.
    """,
    
    # 10. Full Body - Walking Pose
    """
    A beautiful Indian woman full-body portrait,
    walking gracefully, complete outfit visible.
    Natural pose, symmetrical facial features.
    Traditional or contemporary attire.
    Full body shot, dynamic pose.
    Professional photography, cinematic lighting.
    Sharp focus, high quality.
    Same face, same character.
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
    print(f"🔄 Random Full Body Prompt Selected for Variety")
    
    # Return random prompt from PROMPTS list
    selected_prompt = random.choice(PROMPTS)
    print(f"✅ Selected Prompt: {selected_prompt[:100]}...")
    
    return selected_prompt

# ============================================
# 🎨 2. AI से PHOTO GENERATE करें (FULL BODY)
# ============================================

def generate_ai_image(prompt_text, filename="generated_photo.jpg"):
    """
    FLUX AI से FULL BODY फोटो जनरेट करें
    """
    print("🎨 AI से FULL BODY फोटो बना रहा हूँ...")
    
    # सरल और साफ प्रॉम्प्ट
    clean_prompt = prompt_text.strip().replace('\n', ' ').replace('  ', ' ')
    encoded_prompt = urllib.parse.quote(clean_prompt[:200])
    
    # ✅ FULL BODY के लिए आकार 9:16 (पोर्ट्रेट)
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=768&height=1344"  # ✅ 9:16 पोर्ट्रेट आकार - FULL BODY के लिए
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
                print(f"✅ FULL BODY फोटो बन गई! ({content_size/1024:.1f} KB)")
                
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
        "Beautiful Indian bride full body portrait, complete traditional dress, head to toe, standing pose",
        "Stunning Indian woman full body, saree, complete outfit, professional portrait",
        "Glamorous Bollywood actress full body, complete ensemble, studio photography",
        "Elegant Indian woman full body, traditional jewelry, complete attire, professional photo"
    ]
    
    simple_prompt = random.choice(simple_prompts)
    encoded = urllib.parse.quote(simple_prompt)
    
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1344&model=flux&nologo=true&quality=high&enhance=true"
    
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
        
        img = Image.new('RGB', (768, 1344), color=(255, 200, 230))
        draw = ImageDraw.Draw(img)
        
        text = "✨ FULL BODY ✨"
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((300, 600), text, fill=(200, 50, 100), font=font)
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
        
        # FULL BODY के लिए 9:16 अनुपात बनाए रखें
        if width < 768 or height < 1344:
            new_width = 768
            new_height = 1344
            print(f"📐 Resizing: {width}x{height} → {new_width}x{new_height}")
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 2. Sharpness Enhance (चेहरे की त्वचा को प्राकृतिक रखने के लिए इसे कम किया गया)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.1)  # 10% Sharpness Increase
        
        # 3. Contrast Enhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.05)  # 5% Contrast Increase
        
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
    Photo Quality Check - Resolution, Size, Format
    """
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
            
            # FULL BODY के लिए 9:16 अनुपात चेक करें
            ratio = height / width
            print(f"📊 Aspect Ratio: {ratio:.2f} (Ideal: 1.75 for 9:16)")
            
            print(f"📁 Format: {img.format}")
            img.verify()
            print("✅ Image Valid है!")
            
            img = Image.open(image_path)
            print(f"🎨 Color Mode: {img.mode}")
            
            print("✅ Photo Quality Check Passed!")
            return True
            
        except ImportError:
            print("⚠️ PIL installed नहीं है, basic check कर रहा हूँ...")
            if file_size > 10000:
                print(f"✅ File Size ठीक है: {file_size/1024:.1f} KB")
                return True
            else:
                print("❌ File Size बहुत छोटी है!")
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

✨ AI Generated Full Body Look! 🤩

पूरा लुक कैसा लगा? 🤔
👇 Comment में बताओ:
❤️ - पसंद आया
💔 - नहीं पसंद

🎯 100+ Reactions = Next Look और भी Better!

#AIFashion #IndianBeauty #AIArt #ViralFashion #ExplorePage #FYP #StyleInspo #FashionGoals #AIModel #DigitalFashion #AIArtwork #ModernBride #IndianWear #FusionFashion #AIArtist #VirtualFashion #TechStyle #InstaFashion #DailyFashion #Fashionista #AICouture #VirtualInfluencer #IndianFashionBlogger #AIForFashion""",
        
        f"""{time_text}

🔥 AI ने बनाया ये Stunning Full Body Look! 💃

क्या आपको लगता है ये Real है या AI? 🤔
👇 3 Second mein comment karo:
1️⃣ Rate करो (1-10)
2️⃣ Sabse best kya hai?

💡 50+ Comments = Next Post Aaj Raat hi!

#AIBride #IndianWedding #AIArt #TrendingReels #ViralPost #FYP #ExplorePage #AIFashion #BridalWear #AICommunity #DigitalArt #AIInfluencer #AIModel #FashionAI #IndianFashion #BollywoodStyle #AIArtCommunity #ViralReels #InstagramReels #Explore #TrendingNow #AIContent #AIGirl #ArtificialIntelligence #TechFashion #FutureOfFashion #AIforIndia #IndianAI #DesiBride #ShaadiGoals""",
        
        f"""{time_text}

💃 AI Generated - Full Body Royal Look! 👑

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
    print("📤 Facebook पर FULL BODY फोटो पोस्ट कर रहा हूँ...")
    
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
            print(f"✅ FULL BODY पोस्ट हो गई! Post ID: {post_id}")
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
    """टेम्परेरी फ़ाइल्स डिलीट करें"""
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
    """पूरा बॉट चलाएं - FULL BODY के लिए"""
    
    print("\n" + "="*60)
    print("🚀 FULL BODY INSTAGRAM STYLE AI BOT START")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # STEP 1: Style Select (Instagram Skip)
        print("\n📸 STEP 1: Full Body Style Select...")
        style_prompt = learn_style_from_instagram()
        
        print(f"✅ Selected Full Body Style: {style_prompt[:100]}...")
        
        # STEP 2: AI से FULL BODY फोटो बनाएं
        print("\n🎨 STEP 2: AI से FULL BODY फोटो बना रहा हूँ...")
        image_path = generate_ai_image(style_prompt, "full_body_photo.jpg")
        
        if not image_path:
            print("❌ फोटो नहीं बन पाई!")
            return False
        
        # STEP 2.5: Photo Quality Check
        print("\n📷 STEP 2.5: Photo Quality Check...")
        quality_ok = check_image_quality(image_path)
        
        if not quality_ok:
            print("⚠️ Quality Check Fail हुई! नई फोटो बना रहा हूँ...")
            image_path = generate_ai_image_simple("retry_photo.jpg")
            if image_path:
                quality_ok = check_image_quality(image_path)
                if not quality_ok:
                    print("⚠️ Quality Check फिर Fail हुई! Placeholder use कर रहा हूँ...")
                    image_path = create_placeholder_image("placeholder_final.jpg")
        
        # STEP 3: कैप्शन बनाएं
        print("\n📝 STEP 3: कैप्शन बना रहा हूँ...")
        caption = generate_caption()
        print(f"✅ कैप्शन तैयार ({len(caption)} अक्षर)")
        print(f"📝 Caption Preview: {caption[:150]}...")
        
        # STEP 4: Facebook पर FULL BODY पोस्ट करें
        print("\n📤 STEP 4: Facebook पर FULL BODY पोस्ट कर रहा हूँ...")
        post_id = post_to_facebook(image_path, caption)
        
        # STEP 5: क्लीनअप
        print("\n🧹 STEP 5: क्लीनअप...")
        cleanup_files(image_path, "ref_post_1.jpg", "ref_post_2.jpg", "ref_post_3.jpg", "retry_photo.jpg", "placeholder_final.jpg")
        
        elapsed = time.time() - start_time
        
        if post_id:
            print("\n" + "="*60)
            print("🎉 SUCCESS! FULL BODY पोस्ट हो गई!")
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
