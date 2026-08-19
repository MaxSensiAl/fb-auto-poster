import os
import sys
import time
import random
import requests
import urllib.parse
from datetime import datetime
from playwright.sync_api import sync_playwright

# ============================================
# 🔐 ENVIRONMENT VARIABLES (पहले सेट करें)
# ============================================
# Facebook Credentials
PAGE_ID = os.environ.get("FB_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

# Instagram Credentials (अपने असली ID/PASSWORD डालें)
IG_USERNAME = os.environ.get("IG_USERNAME", "your_instagram_username")
IG_PASSWORD = os.environ.get("IG_PASSWORD", "your_instagram_password")

# AI APIs (Optional)
HF_TOKEN = os.environ.get("HF_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API")

# ============================================
# 🖼️ 1. INSTAGRAM से स्टाइल सीखें
# ============================================

def get_instagram_style(target_profile="zaraso_phia", max_posts=5):
    """
    Instagram प्रोफाइल से पोस्ट लोड करें और उनका स्टाइल एनालिसिस करें
    """
    print(f"📸 Instagram से स्टाइल सीख रहा हूँ: @{target_profile}")
    
    style_data = {
        "subjects": [],
        "colors": [],
        "backgrounds": [],
        "poses": [],
        "moods": [],
        "sample_prompts": []
    }
    
    with sync_playwright() as p:
        # ब्राउज़र को रियल यूज़र जैसा बनाएं
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        
        # 1. Instagram होम पेज
        page.goto('https://www.instagram.com/')
        page.wait_for_timeout(3000)
        
        # 2. लॉगिन
        try:
            page.click('text=Log in')
            page.wait_for_timeout(2000)
            
            page.fill('input[name="username"]', IG_USERNAME)
            page.fill('input[name="password"]', IG_PASSWORD)
            page.click('button[type="submit"]')
            page.wait_for_timeout(5000)
            
            # "Not Now" बटन दबाएं
            try:
                page.click('button:has-text("Not Now")')
                page.wait_for_timeout(2000)
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ लॉगिन में समस्या: {e}")
            browser.close()
            return None
        
        # 3. प्रोफाइल पर जाएं
        page.goto(f'https://www.instagram.com/{target_profile}/')
        page.wait_for_timeout(5000)
        
        # 4. पोस्ट लोड करें (स्क्रॉल करें)
        for i in range(3):
            page.evaluate('window.scrollBy(0, 800)')
            page.wait_for_timeout(2000)
        
        # 5. पोस्ट के लिंक निकालें
        post_links = page.eval_on_selector_all(
            'a[href*="/p/"]',
            'els => els.map(el => el.href)'
        )
        
        # डुप्लिकेट हटाएं
        unique_links = list(dict.fromkeys(post_links))
        print(f"✅ {len(unique_links)} पोस्ट मिले")
        
        # 6. पहले 5 पोस्ट का एनालिसिस करें
        for idx, link in enumerate(unique_links[:max_posts]):
            try:
                print(f"  🔍 पोस्ट {idx+1} एनालिसिस...")
                page.goto(link)
                page.wait_for_timeout(3000)
                
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
                    
                    # कैप्शन/टेक्स्ट निकालें
                    try:
                        caption = page.eval_on_selector(
                            'div._a9zr h1',
                            'el => el.textContent'
                        )
                        if caption:
                            print(f"    📝 कैप्शन: {caption[:100]}...")
                            style_data["sample_prompts"].append(caption)
                    except:
                        pass
                    
                    # ✅ AI को प्रॉम्प्ट भेजने के लिए विवरण तैयार करें
                    style_analysis = analyze_image_style(img_path)
                    if style_analysis:
                        style_data["subjects"].append(style_analysis.get("subject", ""))
                        style_data["colors"].append(style_analysis.get("colors", ""))
                        style_data["backgrounds"].append(style_analysis.get("background", ""))
                        style_data["poses"].append(style_analysis.get("pose", ""))
                        style_data["moods"].append(style_analysis.get("mood", ""))
                    
            except Exception as e:
                print(f"    ❌ पोस्ट {idx+1} स्किप: {e}")
        
        browser.close()
    
    # स्टाइल को सारांशित करें
    if style_data["subjects"]:
        style_summary = summarize_style(style_data)
        return style_summary
    else:
        print("⚠️ कोई डेटा नहीं मिला, डिफॉल्ट प्रॉम्प्ट का उपयोग करेंगे")
        return None

# ============================================
# 📝 2. स्टाइल एनालिसिस (डमी फंक्शन - असली में AI का उपयोग करें)
# ============================================

def analyze_image_style(image_path):
    """
    फोटो का स्टाइल एनालिसिस करें
    आप यहाँ Gemini या अन्य Vision API का उपयोग कर सकते हैं
    """
    # अभी के लिए डमी डेटा
    styles = [
        {
            "subject": "Indian woman with traditional attire",
            "colors": "warm tones, maroon, gold, green",
            "background": "blurred outdoor with nature",
            "pose": "semi-profile looking at camera",
            "mood": "elegant and confident"
        },
        {
            "subject": "Bollywood-inspired actress look",
            "colors": "vibrant reds, oranges, gold jewelry",
            "background": "studio with soft lighting",
            "pose": "front-facing with slight head tilt",
            "mood": "glamorous and striking"
        }
    ]
    return random.choice(styles)

def summarize_style(style_data):
    """
    सारे डेटा से एक AI प्रॉम्प्ट बनाएं
    """
    # सबसे कॉमन एट्रिब्यूट्स चुनें
    from collections import Counter
    
    subjects = Counter(style_data["subjects"]).most_common(1)
    colors = Counter(style_data["colors"]).most_common(1)
    backgrounds = Counter(style_data["backgrounds"]).most_common(1)
    poses = Counter(style_data["poses"]).most_common(1)
    moods = Counter(style_data["moods"]).most_common(1)
    
    prompt = f"""
    A stunning portrait of a {subjects[0][0] if subjects else 'beautiful woman'}.
    Style: {moods[0][0] if moods else 'elegant'} and photorealistic.
    Color palette: {colors[0][0] if colors else 'rich warm tones'}.
    Background: {backgrounds[0][0] if backgrounds else 'soft blurred nature'}.
    Pose: {poses[0][0] if poses else 'confident front-facing'}.
    High quality, 8k, hyper-realistic, professional photography, 
    cinematic lighting, crystal clear, national geographic quality.
    Maintain the same face and character in every generation.
    """
    
    return prompt

# ============================================
# 🎨 3. AI से नई फोटो जनरेट करें
# ============================================

def generate_ai_image(prompt_text, filename="generated_photo.jpg"):
    """
    AI (FLUX) से फोटो जनरेट करें
    """
    print("🎨 AI से नई फोटो बना रहा हूँ...")
    
    # प्रॉम्प्ट को इन्हांस करें
    enhanced_prompt = f"{prompt_text}, ultra-high-resolution, 8k, photorealistic, crystal clear"
    encoded_prompt = urllib.parse.quote(enhanced_prompt.strip())
    
    # FLUX API का उपयोग करें
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
            print(f"❌ AI ने काम नहीं किया: {response.status_code}")
    except Exception as e:
        print(f"❌ AI error: {e}")
    
    return None

# ============================================
# 📝 4. कैप्शन जनरेट करें
# ============================================

def generate_caption(style_prompt):
    """
    Instagram-style caption generate करें
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

✨ AI ने बनाया ये Stunning Look! 

आपको कैसा लगा? 🤔
👇 Comment में बताओ:
❤️ - अगर पसंद आया
💔 - अगर नहीं पसंद

🎯 100+ Reactions = Next Look और भी Better!

#AIFashion #TrendingStyle #IndianBeauty #AICreation #ViralFashion #ExplorePage #FYP #StyleInspo #OOTD #FashionGoals #AIModel #DigitalFashion #AIArtwork #ModernBride #IndianWear #FusionFashion #AIArtist #VirtualFashion #TechStyle #InstaFashion #DailyFashion #Fashionista #AICouture #VirtualInfluencer #IndianFashionBlogger #AIForFashion #AIGirl #IndianBeauty #ViralPost #Explore #TrendingNow""",
        
        f"""{time_text}

🔥 AI Generated Perfect Look!

क्या आपको लगता है ये Real है या AI? 🤔
👇 3 Second mein comment karo:
1️⃣ Kitne number doge? (1-10)
2️⃣ Sabse best kya hai?

💡 50+ Comments = Next Post Aaj Raat hi!

#AIBride #IndianWedding #AIArt #TrendingReels #ViralPost #FYP #ExplorePage #AIFashion #BridalWear #AICommunity #DigitalArt #AIInfluencer #AIModel #FashionAI #IndianFashion #BollywoodStyle #AIArtCommunity #ViralReels #InstagramReels #Explore #TrendingNow #AIContent #AIGirl #ArtificialIntelligence #TechFashion #FutureOfFashion #AIforIndia #IndianAI #DesiBride #ShaadiGoals"""
    ]
    
    return random.choice(captions)

# ============================================
# 📤 5. FACEBOOK पर पोस्ट करें
# ============================================

def post_to_facebook(image_path, caption):
    """
    Facebook Page पर फोटो पोस्ट करें
    """
    print("📤 Facebook पर पोस्ट कर रहा हूँ...")
    
    if not PAGE_ID or not ACCESS_TOKEN:
        print("❌ Facebook Credentials नहीं मिले!")
        return None
    
    fb_url = f"https://graph.facebook.com/{PAGE_ID}/photos"
    
    payload = {
        'caption': caption,
        'access_token': ACCESS_TOKEN,
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
# 🧹 6. क्लीनअप
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
# 🚀 7. मुख्य बॉट - पूरा वर्कफ्लो
# ============================================

def main_bot():
    """पूरा बॉट चलाएं - Instagram स्टाइल सीखे, AI फोटो बनाए, Facebook पोस्ट करें"""
    
    print("\n" + "="*60)
    print("🚀 AI INSTAGRAM STYLE BOT START")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # STEP 1: Instagram से स्टाइल सीखें
        print("\n📸 STEP 1: Instagram स्टाइल सीख रहा हूँ...")
        style_prompt = get_instagram_style("zaraso_phia", max_posts=3)
        
        if not style_prompt:
            print("⚠️ Instagram से डेटा नहीं मिला, डिफॉल्ट प्रॉम्प्ट का उपयोग कर रहा हूँ")
            style_prompt = """
            A stunning portrait of an Indian woman wearing traditional attire.
            Rich warm colors, gold jewelry, soft natural lighting.
            High quality, 8k, photorealistic, professional photography.
            """
        
        print(f"✅ स्टाइल प्रॉम्प्ट तैयार: {style_prompt[:100]}...")
        
        # STEP 2: AI से नई फोटो बनाएं
        print("\n🎨 STEP 2: AI से नई फोटो बना रहा हूँ...")
        image_path = generate_ai_image(style_prompt, "ai_generated_photo.jpg")
        
        if not image_path:
            print("❌ फोटो नहीं बन पाई!")
            return False
        
        # STEP 3: कैप्शन बनाएं
        print("\n📝 STEP 3: कैप्शन बना रहा हूँ...")
        caption = generate_caption(style_prompt)
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
# 🎯 8. EXECUTE
# ============================================

if __name__ == "__main__":
    # पहले environment variables चेक करें
    if not IG_USERNAME or IG_USERNAME == "your_instagram_username":
        print("⚠️ Instagram username set नहीं है!")
        print("कृपया इस कोड को अपडेट करें:")
        print("  IG_USERNAME = 'your_real_username'")
        print("  IG_PASSWORD = 'your_real_password'")
        sys.exit(1)
    
    success = main_bot()
    sys.exit(0 if success else 1)
