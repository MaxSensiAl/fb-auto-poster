import requests
import random
import os
import urllib.parse
import time
from datetime import datetime
import sys

# ============================================
# CONFIGURATION
# ============================================
PAGE_ID = os.environ.get("FB_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

# ============================================
# 1. हाई-क्वालिटी AI प्रॉम्प्ट्स
# ============================================
PROMPTS = [
    """a breathtakingly beautiful North Indian bride, wearing a heavily embroidered red and gold bridal lehenga, intricate mehndi on hands, traditional gold jewelry set, maang tikka, nath, delicate veil, glowing skin, soft smile, royal palace background with ornate pillars, warm golden hour lighting, cinematic, photorealistic, ultra detailed, 8k, professional wedding photography style""",
    
    """a stunning South Indian girl, wearing a rich green and gold Kanjeevaram silk saree, heavy gold temple jewelry, beautiful jasmine flowers in her hair, kumkum on forehead, traditional Kerala temple background, soft morning sunlight, divine look, graceful pose, realistic, 8k resolution, hyper detailed""",
    
    """a gorgeous modern Indian girl, wearing a stylish crop top with a flowy long skirt, fusion fashion look, confident walk on a Mumbai street, minimal jewelry, sunglasses, urban background, city lights, soft focus, fashion magazine cover style, professional photography, ultra HD, 8k""",
    
    """a beautiful Rajasthani princess, wearing a colorful bandhani dupatta and lehenga, heavy silver jewelry, mirror work outfit, standing in a haveli courtyard, vibrant colors, traditional backdrop, warm desert lighting, ethereal beauty, photorealistic, intricate details, 8k resolution""",
    
    """a stunning Kashmiri girl, wearing a traditional pheran, embroidered with intricate thread work, beautiful eyes, snowy mountain background in Gulmarg, winter setting, soft natural light, dreamy expression, realistic, highly detailed, 8k""",
    
    """a stylish Indian girl dressed as a wedding guest, wearing a pastel colored anarkali suit, delicate jewelry, floral jewelry, happy smile, wedding decoration background with flowers and lights, festive vibe, elegant pose, soft warm lighting, photorealistic, 8k""",
    
    """a beautiful girl with bohemian style, wearing a flowy floral dress, golden jewelry, long wavy hair, standing in a desert landscape at sunset, golden hour glow, wind blowing her hair, free-spirited look, artistic, cinematic, photorealistic, 8k""",
    
    """a stunning Punjabi girl wearing a bright yellow Patiala salwar suit, with a beautiful dupatta, vibrant phulkari work, traditional Punjabi jewelry, standing in a mustard field, bright sunny day, happy expression, colorful, joyful, realistic, highly detailed, 8k""",
    
    """a graceful Bengali girl, wearing a white and red traditional Bengali saree, shakha pola bangles, beautiful sindoor, soft smile, standing near a temple, soft lighting, cultural vibe, elegant, photorealistic, 8k, detailed""",
    
    """a confident Indian supermodel on the runway, wearing a modern fusion outfit - a floor-length gown with Indian embroidery, stylish makeup, chunky jewelry, ramp walk, fashion show lights, dramatic shadows, high fashion, professional, 8k, photorealistic"""
]

# ============================================
# 2. कैप्शन जनरेटर
# ============================================
def generate_caption(theme="fashion", include_question=True):
    """स्मार्ट कैप्शन जनरेटर"""
    
    base_captions = {
        "fashion": [
            "✨ नया लुक, नई स्टाइल! 💃\n\nकैसा लगा? कमेंट में बताओ 👇",
            "🌸 फैशन की दुनिया से एक झलक!\n\nक्या आप ये लुक वियर करेंगी?",
            "💫 स्टाइलिश और ट्रेंडी!\n\n1-10 में रेट करो!",
        ],
        "wedding": [
            "💍 शादी का सीजन आ गया!\n\nइस लुक को क्या कहेंगे?",
            "👰 ब्राइडल लुक में AI की कला!\n\nसबसे अच्छी चीज़ क्या लगी?",
            "❤️ रॉयल वेडिंग वाइब्स!\n\nकौन सा गहना सबसे सुंदर है?",
        ],
        "festival": [
            "🎉 त्योहारों की धूम!\n\nफेस्टिवल में क्या पहनोगी?",
            "🎊 फेस्टिवल फैशन स्पेशल!\n\nकितना पसंद आया?",
            "🌺 ट्रेडिशनल लुक, मॉडर्न स्टाइल!\n\nकमेंट में बताओ!",
        ]
    }
    
    captions = base_captions.get(theme, base_captions["fashion"])
    caption = random.choice(captions)
    
    # हैशटैग जोड़ें
    caption += f"\n\n{get_trending_hashtags('fashion,indian,aiart,viral')}"
    
    return caption

# ============================================
# 3. ट्रेंडिंग हैशटैग जनरेटर
# ============================================
def get_trending_hashtags(niche="fashion"):
    """ट्रेंडिंग हैशटैग ऑटो जनरेट करें"""
    
    hashtags = {
        "fashion": ["#OOTD", "#FashionTrends", "#StyleInspo", "#DesignerWear", "#FashionDaily"],
        "indian": ["#IndianWear", "#EthnicLook", "#TraditionalFashion", "#IndianBeauty"],
        "aiart": ["#AIArtwork", "#DigitalCreation", "#AIGenerated", "#AIArtist"],
        "viral": ["#ViralReels", "#ExplorePage", "#TrendingNow", "#FYP"]
    }
    
    selected = []
    for category in niche.split(','):
        category = category.strip()
        if category in hashtags:
            selected.extend(random.sample(hashtags[category], min(3, len(hashtags[category]))))
    
    return ' '.join(selected[:15])

# ============================================
# 4. वायरल स्कोर प्रेडिक्टर
# ============================================
def predict_viral_score(prompt_text):
    """प्रॉम्प्ट कितना वायरल होगा?"""
    
    viral_keywords = ["beautiful", "stunning", "royal", "traditional", "glowing", 
                     "gorgeous", "divine", "ethereal", "breath-taking"]
    score = 0
    
    for keyword in viral_keywords:
        if keyword in prompt_text.lower():
            score += 15
    
    emotional_words = ["love", "dream", "magical", "divine", "gorgeous", "happy", "smile"]
    for word in emotional_words:
        if word in prompt_text.lower():
            score += 12
    
    detail_words = ["8k", "photorealistic", "cinematic", "intricate", "hyper detailed", "ultra hd"]
    for word in detail_words:
        if word in prompt_text.lower():
            score += 10
    
    color_words = ["golden", "vibrant", "colorful", "warm", "glowing", "bright"]
    for word in color_words:
        if word in prompt_text.lower():
            score += 8
    
    return min(score, 100)

# ============================================
# 5. मुख्य अपलोड फंक्शन
# ============================================
def upload_ai_image(style_type="random", custom_title=None, caption=None):
    """AI इमेज जनरेट और अपलोड करें"""
    
    # प्रॉम्प्ट चुनें
    style_map = {
        "bridal": PROMPTS[0],
        "south": PROMPTS[1],
        "modern": PROMPTS[2],
        "rajasthani": PROMPTS[3],
        "kashmiri": PROMPTS[4],
        "random": random.choice(PROMPTS)
    }
    
    prompt = style_map.get(style_type, random.choice(PROMPTS))
    
    # कैप्शन
    if caption:
        final_caption = caption
    else:
        final_caption = generate_caption()
    
    if custom_title:
        final_caption = f"🌟 {custom_title}\n\n{final_caption}"
    
    # वायरल स्कोर
    viral_score = predict_viral_score(prompt)
    print(f"📊 वायरल स्कोर: {viral_score}%")
    
    # URL एनकोड
    encoded_prompt = urllib.parse.quote(prompt)
    ai_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true&model=flux"
    
    # फेसबुक पोस्ट
    fb_url = f"https://graph.facebook.com/{PAGE_ID}/photos"
    payload = {
        'url': ai_image_url,
        'caption': final_caption,
        'access_token': ACCESS_TOKEN,
        'published': 'true'
    }
    
    try:
        response = requests.post(fb_url, data=payload, timeout=60)
        
        if response.status_code == 200:
            print(f"✅ पोस्ट सफल!")
            print(f"📝 {final_caption[:100]}...")
            return response.json().get('id')
        else:
            print(f"❌ फेल: {response.status_code}")
            print(f"⚠️ {response.text}")
            return None
            
    except Exception as e:
        print(f"⚠️ एरर: {e}")
        return None

# ============================================
# 6. ऑटो-पोस्ट मोड (GitHub Actions के लिए)
# ============================================
def auto_post_mode():
    """GitHub Actions के लिए - बिना input() के"""
    
    print("""
    ╔═══════════════════════════════════════╗
    ║   🤖 AI FASHION POSTER PRO v3.0     ║
    ║   🔥 GitHub Actions Auto-Mode       ║
    ╚═══════════════════════════════════════╝
    """)
    
    # कौन सा मोड चलाना है?
    mode = os.environ.get("POST_MODE", "single")
    
    if mode == "single":
        print("📌 सिंगल पोस्ट मोड")
        style = os.environ.get("STYLE", "random")
        title = os.environ.get("TITLE", "✨ AI फैशन क्रिएशन!")
        upload_ai_image(style_type=style, custom_title=title)
        
    elif mode == "bulk":
        print("📌 बल्क पोस्ट मोड")
        count = int(os.environ.get("POST_COUNT", 3))
        styles = ["bridal", "south", "modern", "rajasthani", "kashmiri", "random"]
        
        for i in range(count):
            style = random.choice(styles)
            title = f"AI फैशन {i+1}/{count} ✨"
            upload_ai_image(style_type=style, custom_title=title)
            if i < count - 1:
                time.sleep(60)  # 1 मिनट का गैप
                
    elif mode == "carousel":
        print("📌 कैरोसेल मोड")
        count = int(os.environ.get("CAROUSEL_COUNT", 4))
        prompts = random.sample(PROMPTS, min(count, len(PROMPTS)))
        
        # सिंगल कैरोसेल फोटो अपलोड
        for i, prompt in enumerate(prompts):
            upload_ai_image(selected_prompt=prompt, custom_title=f"कलेक्शन {i+1}")
            time.sleep(30)
            
    elif mode == "challenge":
        print("📌 डेली चैलेंज मोड")
        themes = [
            ("🌺 राजस्थानी रानी", "rajasthani"),
            ("🌸 केरल ब्राइड", "south"),
            ("💃 बॉलीवुड स्टार", "modern")
        ]
        theme, style = random.choice(themes)
        caption = f"""
        {theme} - आज का AI चैलेंज!
        
        🎯 चैलेंज: कमेंट में इस लुक की 3 खूबियाँ बताओ!
        🏆 बेस्ट कमेंट को स्टोरी में शेयर करेंगे!
        
        {generate_caption('festival')}
        """
        upload_ai_image(style_type=style, custom_title="📌 डेली चैलेंज", caption=caption)
    
    else:
        print("❌ गलत POST_MODE. single/bulk/carousel/challenge में से चुनें.")

# ============================================
# 7. मुख्य फंक्शन
# ============================================
def main():
    """मुख्य फंक्शन - Auto detect"""
    
    # Check if running in GitHub Actions
    is_github_action = os.environ.get("GITHUB_ACTIONS") == "true"
    
    if is_github_action:
        print("🚀 GitHub Actions में चल रहा है...")
        auto_post_mode()
    else:
        # Local run - Interactive mode
        print("💻 लोकल मोड - मेनू लोड हो रहा है...")
        # यहाँ तुम्हारा पुराना मेनू कोड आएगा (input() वाला)
        # लेकिन GitHub Actions में ये नहीं चलेगा

if __name__ == "__main__":
    # पहले चेक करें
    if not PAGE_ID or not ACCESS_TOKEN:
        print("❌ ERROR: FB_PAGE_ID और FB_ACCESS_TOKEN सेट करें!")
        print("📌 GitHub Secrets में सेट करें:")
        print("   FB_PAGE_ID")
        print("   FB_ACCESS_TOKEN")
        exit(1)
    
    main()
