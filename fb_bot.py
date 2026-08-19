import requests
import random
import os
import urllib.parse
import time
import sys
from datetime import datetime

# ============================================
# ENVIRONMENT VARIABLES
# ============================================
PAGE_ID = os.environ.get("FB_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

# ============================================
# AI PROMPTS - हाई क्वालिटी गर्ल इमेजेस
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
# CAPTIONS - इंगेजमेंट बढ़ाने वाले
# ============================================
CAPTIONS = [
    """✨ नया लुक, नई स्टाइल! 💃

कैसा लगा? कमेंट में बताओ 👇

#AIFashion #IndianWear #TraditionalLook #ViralReels #ExplorePage""",

    """🌸 फैशन की दुनिया से एक झलक!

क्या आप ये लुक वियर करेंगी? हाँ/ना में बताओ 💬

#IndianBeauty #FashionDaily #AIArtwork #TrendingNow #StyleInspo""",

    """💫 स्टाइलिश और ट्रेंडी!

1-10 में रेट करो! ⭐

#OOTD #FashionTrends #DesignerWear #AIGenerated #FYP""",

    """💍 शादी का सीजन आ गया!

इस लुक को क्या कहेंगे? 👇

#BridalFashion #WeddingVibes #RoyalLook #AIArtist #ViralPost""",

    """👰 ब्राइडल लुक में AI की कला!

सबसे अच्छी चीज़ क्या लगी? 💬

#EthnicLook #IndianWear #FashionGram #AICommunity #Explore""",

    """🎉 त्योहारों की धूम!

फेस्टिवल में क्या पहनोगी? 🎊

#FestivalFashion #TraditionalStyle #Colorful #AICreation #ViralReels""",

    """🌺 ट्रेडिशनल लुक, मॉडर्न स्टाइल!

कमेंट में बताओ - कौन सा कलर सबसे सुंदर है?

#IndianEthnic #FashionLover #AIArt #TrendingStyle #FYP""",

    """💃 रॉयल वाइब्स, रॉयल लुक!

इस लुक को कैरेक्टर दो एक नाम! 👑

#RoyalFashion #QueenVibes #DesignerWear #AIFashion #Viral""",

    """🌟 AI की कला और इंडियन ट्रेडिशन का मिलन!

कितना पसंद आया? ❤️

#IndianCulture #AIGenerated #FashionBlogger #StyleGoals #TopFashion""",

    """✨ सपनों की दुनिया से एक झलक!

इस लुक में सबसे खास क्या है? 💬

#DreamLook #FashionDesign #AIArtist #ViralPost #ExplorePage"""
]

# ============================================
# POST TO FACEBOOK FUNCTION
# ============================================
def post_to_facebook():
    """AI इमेज जनरेट करें और Facebook पर पोस्ट करें"""
    
    # 1️⃣ रैंडम प्रॉम्प्ट और कैप्शन चुनें
    selected_prompt = random.choice(PROMPTS)
    selected_caption = random.choice(CAPTIONS)
    
    # 2️⃣ समय और दिन के हिसाब से कस्टमाइज़ करें
    current_hour = datetime.now().hour
    current_day = datetime.now().strftime("%A")
    
    # सुबह/शाम के हिसाब से कैप्शन
    if 6 <= current_hour < 12:
        time_text = "🌅 गुड मॉर्निंग! आज की स्पेशल पोस्ट"
    elif 12 <= current_hour < 17:
        time_text = "☀️ दोपहर की खूबसूरत झलक"
    elif 17 <= current_hour < 21:
        time_text = "🌆 शाम की शान! ये लुक कैसा है?"
    else:
        time_text = "🌙 रात की रानी! क्या आपको पसंद आया?"
    
    final_caption = f"{time_text}\n\n{selected_caption}"
    
    # 3️⃣ वायरल स्कोर कैलकुलेट करें
    viral_score = predict_viral_score(selected_prompt)
    
    print(f"""
    ═══════════════════════════════════════
    📤 अपलोडिंग शुरू...
    ═══════════════════════════════════════
    🕐 समय: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    📅 दिन: {current_day}
    🎯 वायरल स्कोर: {viral_score}%
    📝 कैप्शन: {final_caption[:50]}...
    ═══════════════════════════════════════
    """)
    
    # 4️⃣ इमेज URL बनाएं (FLUX मॉडल - सबसे बेस्ट)
    encoded_prompt = urllib.parse.quote(selected_prompt)
    ai_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true&model=flux"
    
    # 5️⃣ Facebook API कॉल
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
            post_id = response.json().get('id')
            print(f"""
    ✅ पोस्ट सफल!
    🆔 पोस्ट ID: {post_id}
    ═══════════════════════════════════════
            """)
            return True
        else:
            print(f"""
    ❌ अपलोड फेल!
    📊 स्टेटस: {response.status_code}
    ⚠️ एरर: {response.text}
    ═══════════════════════════════════════
            """)
            return False
            
    except Exception as e:
        print(f"""
    ⚠️ कनेक्शन एरर!
    🔴 {str(e)}
    ═══════════════════════════════════════
        """)
        return False

# ============================================
# VIRAL SCORE PREDICTOR
# ============================================
def predict_viral_score(prompt_text):
    """वायरल स्कोर कैलकुलेट करें"""
    
    keywords = {
        "beautiful": 15, "stunning": 15, "royal": 12, "traditional": 10,
        "glowing": 12, "gorgeous": 15, "divine": 12, "ethereal": 10,
        "8k": 10, "photorealistic": 10, "cinematic": 8, "intricate": 8,
        "golden": 10, "vibrant": 8, "colorful": 8, "warm": 6,
        "love": 10, "dream": 8, "magical": 12, "happy": 6, "smile": 8
    }
    
    score = 0
    prompt_lower = prompt_text.lower()
    
    for word, weight in keywords.items():
        if word in prompt_lower:
            score += weight
    
    return min(score, 100)

# ============================================
# SCHEDULED POST - हर 30 मिनट में चलने के लिए
# ============================================
def scheduled_post():
    """हर 30 मिनट में चलने वाला फंक्शन"""
    
    print("""
    ╔═══════════════════════════════════════╗
    ║   🤖 AI FASHION POSTER PRO v3.0     ║
    ║   🕐 हर 30 मिनट में पोस्ट          ║
    ║   ❤️  फेसबुक ऑटो पोस्टर           ║
    ╚═══════════════════════════════════════╝
    """)
    
    # पहले चेक करें
    if not PAGE_ID or not ACCESS_TOKEN:
        print("""
    ❌ ERROR: FB_PAGE_ID और FB_ACCESS_TOKEN सेट नहीं है!
    📌 GitHub Secrets में डालें:
       - FB_PAGE_ID
       - FB_ACCESS_TOKEN
        """)
        sys.exit(1)
    
    # पोस्ट करें
    success = post_to_facebook()
    
    if success:
        print("✅ आज की पोस्ट सफलतापूर्वक अपलोड हो गई!")
        print(f"🕐 अगली पोस्ट 30 मिनट में...")
    else:
        print("❌ पोस्ट फेल हो गई! चेक करें:")
        print("   1. Facebook Page ID सही है?")
        print("   2. Access Token एक्सपायर तो नहीं हुआ?")
        print("   3. Page पर पोस्ट करने की permission है?")
        sys.exit(1)

# ============================================
# MAIN - यही चलेगा
# ============================================
if __name__ == "__main__":
    scheduled_post()
