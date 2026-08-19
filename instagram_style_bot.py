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
if not IG_USERNAME or not IG_PASSWORD:
    print("❌ Instagram Credentials नहीं मिले!")
    print("कृपया GitHub Secrets में IG_USERNAME और IG_PASSWORD सेट करें")
    sys.exit(1)

if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
    print("❌ Facebook Credentials नहीं मिले!")
    sys.exit(1)

print(f"✅ Instagram: {IG_USERNAME[:3]}***")
print(f"✅ Target: @{TARGET_PROFILE}")
print(f"✅ Facebook Page: {FB_PAGE_ID[:3]}***")

# ============================================
# 📸 1. INSTAGRAM से STYLE सीखें
# ============================================

def learn_style_from_instagram():
    """
    Instagram प्रोफाइल से पोस्ट लोड करें और स्टाइल एनालिसिस करें
    """
    print(f"📸 Instagram से स्टाइल सीख रहा हूँ: @{TARGET_PROFILE}")
    
    style_description = {
        "subjects": [],
        "colors": [],
        "backgrounds": [],
        "poses": [],
        "moods": []
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,  # GitHub Actions में Headless चलेगा
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        
        try:
            # 1. Instagram होम पेज
            page.goto('https://www.instagram.com/')
            page.wait_for_timeout(5000)
            
            # 2. लॉगिन
            page.fill('input[name="username"]', IG_USERNAME)
            page.fill('input[name="password"]', IG_PASSWORD)
            page.click('button[type="submit"]')
            page.wait_for_timeout(8000)
            
            # 3. "Not Now" बटन
            try:
                page.click('button:has-text("Not Now")')
                page.wait_for_timeout(3000)
            except:
                pass
            
            # 4. Target Profile पर जाएँ
            page.goto(f'https://www.instagram.com/{TARGET_PROFILE}/')
            page.wait_for_timeout(5000)
            
            # 5. पोस्ट लोड करें
            for i in range(3):
                page.evaluate('window.scrollBy(0, 800)')
                page.wait_for_timeout(2000)
            
            # 6. पोस्ट लिंक निकालें
            post_links = page.eval_on_selector_all(
                'a[href*="/p/"]',
                'els => els.map(el => el.href)'
            )
            
            unique_links = list(dict.fromkeys(post_links))
            print(f"✅ {len(unique_links)} पोस्ट मिले")
            
            # 7. पहली 3 पोस्ट का एनालिसिस करें
            for idx, link in enumerate(unique_links[:3]):
                try:
                    print(f"  🔍 पोस्ट {idx+1} एनालिसिस...")
                    page.goto(link)
                    page.wait_for_timeout(4000)
                    
                    # फोटो डाउनलोड करें
                    img_src = page.eval_on_selector(
                        'img[style*="object-fit"]',
                        'el => el.src'
                    )
                    
                    if img_src:
                        # फोटो सेव करें (रिफरेंस के लिए)
                        img_response = requests.get(img_src)
                        img_path = f"ref_post_{idx+1}.jpg"
                        with open(img_path, 'wb') as f:
                            f.write(img_response.content)
                        print(f"    📷 फोटो सेव: {img_path}")
                        
                        # Caption निकालें
                        try:
                            caption = page.eval_on_selector(
                                'div._a9zr h1',
                                'el => el.textContent'
                            )
                            if caption:
                                print(f"    📝 कैप्शन: {caption[:100]}...")
                        except:
                            pass
                        
                except Exception as e:
                    print(f"    ❌ पोस्ट {idx+1} स्किप: {e}")
            
            browser.close()
            
        except Exception as e:
            print(f"❌ Instagram Error: {e}")
            browser.close()
            return None
    
    # Style Summary बनाएँ
    return create_default_prompt()

# ============================================
# 📝 STYLE PROMPT
# ============================================

def create_default_prompt():
    """
    हाई-क्वालिटी प्रॉम्प्ट
    """
    return """
    A stunning high-quality portrait of an Indian bride.
    Traditional red bridal wear with gold embroidery.
    Beautiful jewelry, maang tikka, and earrings.
    Soft golden hour lighting, dreamy background.
    8k resolution, photorealistic, professional.
    Canon EOS R5, 85mm lens, f/1.4.
    National Geographic quality, sharp focus.
    Same face, same character.
    """

# ============================================
# 🎨 2. AI से PHOTO GENERATE करें
# ============================================

def generate_ai_image(prompt_text, filename="generated_photo.jpg"):
    """
    FLUX AI से हाई-क्वालिटी फोटो जनरेट करें
    """
    print("🎨 AI से नई फोटो बना रहा हूँ...")
    
    enhanced_prompt = f"{prompt_text}, ultra-high-resolution, 8k, photorealistic, crystal clear, professional photography, national geographic quality"
    encoded_prompt = urllib.parse.quote(enhanced_prompt.strip())
    
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1280"
        f"&model=flux-pro"
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
                return filename
            else:
                print(f"⚠️ फोटो बहुत छोटी है ({content_size} bytes)")
        else:
            print(f"❌ AI Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ AI Error: {e}")
    
    return None

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

#AIBride #IndianWedding #AIArt #TrendingReels #ViralPost #FYP #ExplorePage #AIFashion #BridalWear #AICommunity #DigitalArt #AIInfluencer #AIModel #FashionAI #IndianFashion #BollywoodStyle #AIArtCommunity #ViralReels #InstagramReels #Explore #TrendingNow #AIContent #AIGirl #ArtificialIntelligence #TechFashion #FutureOfFashion #AIforIndia #IndianAI #DesiBride #ShaadiGoals"""
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
# 🚀 6. MAIN BOT
# ============================================

def main():
    """पूरा बॉट चलाएं"""
    
    print("\n" + "="*60)
    print("🚀 INSTAGRAM STYLE AI BOT START")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # STEP 1: Instagram से स्टाइल सीखें
        print("\n📸 STEP 1: Instagram स्टाइल सीख रहा हूँ...")
        style_prompt = learn_style_from_instagram()
        
        if not style_prompt:
            style_prompt = create_default_prompt()
        
        print(f"✅ प्रॉम्प्ट तैयार: {style_prompt[:100]}...")
        
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
    success = main()
    sys.exit(0 if success else 1)
