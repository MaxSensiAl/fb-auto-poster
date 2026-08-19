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
# 🎨 MULTIPLE PROMPTS (Variety के लिए)
# ============================================

PROMPTS = [
    # 1. Traditional Indian Bride
    """
    A stunning high-quality portrait of an Indian bride.
    Traditional red bridal wear with gold embroidery.
    Beautiful jewelry, maang tikka, and earrings.
    Soft golden hour lighting, dreamy background.
    8k resolution, photorealistic, professional.
    Canon EOS R5, 85mm lens, f/1.4.
    National Geographic quality, sharp focus.
    Same face, same character.
    """,
    
    # 2. Modern Bollywood Style
    """
    A glamorous Bollywood actress portrait.
    Modern fusion wear with intricate detailing.
    Studio lighting with soft shadows.
    Professional makeup, perfect skin texture.
    High fashion editorial style.
    Sony A7R IV, 50mm lens, f/1.8.
    Cinematic, dramatic, stunning.
    """,
    
    # 3. South Indian Beauty
    """
    A traditional South Indian woman in silk saree.
    Rich kanjivaram saree with gold border.
    Temple jewelry, jasmine flowers in hair.
    Natural sunlight, temple architecture background.
    Authentic, cultural, beautiful.
    Nikon Z9, 85mm lens.
    Vibrant colors, sharp details.
    """,
    
    # 4. Royal Rajasthani Style
    """
    A royal Rajasthani woman in traditional attire.
    Bandhani dupatta, heavy silver jewelry.
    Desert palace background, golden hour.
    Regal, elegant, majestic.
    Leica M11, 50mm Summilux.
    Warm tones, rich textures.
    """,
    
    # 5. Modern Minimalist
    """
    A modern Indian woman in minimalist style.
    Simple elegant outfit, subtle jewelry.
    Clean white background, soft natural light.
    Contemporary, fresh, sophisticated.
    Professional headshot quality.
    Sharp focus, natural skin texture.
    """,
    
    # 6. Festival Special
    """
    An Indian woman celebrating Diwali.
    Traditional lehenga with mirror work.
    Diya background, festive lighting.
    Joyful expression, vibrant colors.
    Canon EOS R3, 24-70mm lens.
    Festive, warm, celebratory.
    """,
    
    # 7. Wedding Guest Look
    """
    A beautiful woman in wedding guest attire.
    Elegant saree or lehenga.
    Soft romantic lighting.
    Floral background, dreamy atmosphere.
    Professional wedding photography style.
    Rich colors, soft bokeh.
    """,
    
    # 8. Kashmiri Beauty
    """
    A Kashmiri woman in traditional pheran.
    Snow-capped mountains background.
    Natural winter lighting.
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
# 📸 1. INSTAGRAM STYLE (Manually Define)
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
# 🍪 MANUAL COOKIES USE (Option 1)
# ============================================

def learn_style_with_cookies():
    """
    अगर आपके पास Cookies JSON File है तो इसका उपयोग करें
    """
    print("🍪 Cookies के साथ Instagram Login...")
    
    if not os.path.exists("cookies.json"):
        print("⚠️ cookies.json नहीं मिली! Skip कर रहा हूँ...")
        return create_default_prompt()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox']
        )
        
        context = browser.new_context(
            storage_state="cookies.json",  # ✅ Cookies Load करें
            viewport={'width': 1280, 'height': 720}
        )
        
        page = context.new_page()
        
        try:
            page.goto(f'https://www.instagram.com/{TARGET_PROFILE}/')
            page.wait_for_timeout(5000)
            
            # अगर Cookies काम करें तो Profile Load होगी
            print("✅ Cookies Login Successful!")
            
            # पोस्ट लिंक निकालें
            post_links = page.eval_on_selector_all(
                'a[href*="/p/"]',
                'els => els.map(el => el.href)'
            )
            
            unique_links = list(dict.fromkeys(post_links))
            print(f"✅ {len(unique_links)} पोस्ट मिले")
            
            browser.close()
            
        except Exception as e:
            print(f"❌ Cookies Error: {e}")
            browser.close()
    
    return create_default_prompt()

# ============================================
# 🎨 2. AI से PHOTO GENERATE करें
# ============================================

def generate_ai_image(prompt_text, filename="generated_photo.jpg"):
    """
    FLUX AI से हाई-क्वालिटी फोटो जनरेट करें
    """
    print("🎨 AI से नई फोटो बना रहा हूँ...")
    
    # सरल और साफ प्रॉम्प्ट
    clean_prompt = prompt_text.strip().replace('\n', ' ').replace('  ', ' ')
    encoded_prompt = urllib.parse.quote(clean_prompt[:200])
    
    # FLUX API
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1280"
        f"&model=flux"
        f"&nologo=true"
        f"&seed={random.randint(1, 9999999)}"
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
        "Beautiful Indian bride in traditional red dress, professional photography, high quality",
        "Stunning Indian woman in saree, professional portrait, high resolution",
        "Glamorous Bollywood actress portrait, professional photography, studio lighting",
        "Elegant Indian woman in traditional jewelry, soft lighting, professional photo"
    ]
    
    simple_prompt = random.choice(simple_prompts)
    encoded = urllib.parse.quote(simple_prompt)
    
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1280&model=flux&nologo=true"
    
    try:
        response = requests.get(url, timeout=180)
        if response.status_code == 200 and len(response.content) > 50000:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Retry Success! ({len(response.content)/1024:.1f} KB)")
            return filename
    except:
        pass
    
    print("⚠️ Placeholder Image बना रहा हूँ...")
    return create_placeholder_image(filename)

def create_placeholder_image(filename="placeholder.jpg"):
    """
    अगर AI काम न करे तो Placeholder Image बनाएँ
    """
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
# 📝 3. CAPTION GENERATE करें
# ============================================

def generate_caption():
    """
    Viral Instagram-style Caption with variety
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

✨ AI Generated Perfect Look!

आपको कैसा लगा? 🤔
👇 Comment में बताओ:
❤️ - पसंद आया
💔 - नहीं पसंद

🎯 100+ Reactions = Next Look और भी Better!

#AIFashion #IndianBeauty #AIArt #ViralFashion #ExplorePage #FYP #StyleInspo #FashionGoals #AIModel #DigitalFashion #AIArtwork #ModernBride #IndianWear #FusionFashion #AIArtist #VirtualFashion #TechStyle #InstaFashion #DailyFashion #Fashionista #AICouture #VirtualInfluencer #IndianFashionBlogger #AIForFashion""",
        
        f"""{time_text}

🔥 AI ने बनाया ये Stunning Look!

क्या आपको लगता है ये Real है या AI? 🤔
👇 3 Second mein comment karo:
1️⃣ Rate करो (1-10)
2️⃣ Sabse best kya hai?

💡 50+ Comments = Next Post Aaj Raat hi!

#AIBride #IndianWedding #AIArt #TrendingReels #ViralPost #FYP #ExplorePage #AIFashion #BridalWear #AICommunity #DigitalArt #AIInfluencer #AIModel #FashionAI #IndianFashion #BollywoodStyle #AIArtCommunity #ViralReels #InstagramReels #Explore #TrendingNow #AIContent #AIGirl #ArtificialIntelligence #TechFashion #FutureOfFashion #AIforIndia #IndianAI #DesiBride #ShaadiGoals""",
        
        f"""{time_text}

💃 AI Generated - Royal Indian Beauty!

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
    """टेम्परेरी फ़ाइल्स डिलीट करें"""
    for file in files:
        if file and os.path.exists(file):
            try:
                os.remove(file)
                print(f"🧹 {file} डिलीट हो गया")
            except:
                pass

# ============================================
# 📝 6. COOKIES CREATE (एक बार मैन्युअली)
# ============================================

def create_cookies():
    """
    एक बार मैन्युअली चलाकर Cookies Save करें
    """
    print("🍪 Cookies बना रहा हूँ... कृपया मैन्युअली Login करें")
    
    if not IG_USERNAME or not IG_PASSWORD:
        print("❌ Instagram Credentials नहीं मिले!")
        return False
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto('https://www.instagram.com/')
        input("✅ ब्राउज़र खुला है। कृपया मैन्युअली Login करें और Enter दबाएँ...")
        
        # Cookies Save करें
        context.storage_state(path="cookies.json")
        print("✅ cookies.json Save हो गई!")
        browser.close()
        return True

# ============================================
# 🚀 6. MAIN BOT
# ============================================

def main():
    """पूरा बॉट चलाएं"""
    
    print("\n" + "="*60)
    print("🚀 INSTAGRAM STYLE AI BOT START")
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
        
        # STEP 3: कैप्शन बनाएं
        print("\n📝 STEP 3: कैप्शन बना रहा हूँ...")
        caption = generate_caption()
        print(f"✅ कैप्शन तैयार ({len(caption)} अक्षर)")
        
        # STEP 4: Facebook पर पोस्ट करें
        print("\n📤 STEP 4: Facebook पर पोस्ट कर रहा हूँ...")
        post_id = post_to_facebook(image_path, caption)
        
        # STEP 5: क्लीनअप
        print("\n🧹 STEP 5: क्लीनअप...")
        cleanup_files(image_path, "ref_post_1.jpg", "ref_post_2.jpg", "ref_post_3.jpg")
        
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
    # अगर Cookies बनानी है तो इस Function को Call करें
    # create_cookies()  # एक बार मैन्युअली चलाएँ
    
    success = main()
    sys.exit(0 if success else 1)
