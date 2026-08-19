import requests
import random
import os
import urllib.parse
import time
from datetime import datetime
import json

# ============================================
# CONFIGURATION
# ============================================
PAGE_ID = os.environ.get("FB_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

# ============================================
# 1. हाई-क्वालिटी AI प्रॉम्प्ट्स (गर्ल फोकस्ड)
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
            "✨ नया लुक, नई स्टाइल! 💃",
            "🌸 फैशन की दुनिया से एक झलक!",
            "💫 स्टाइलिश और ट्रेंडी! कैसा लगा?",
        ],
        "wedding": [
            "💍 शादी का सीजन आ गया!",
            "👰 ब्राइडल लुक में AI की कला!",
            "❤️ रॉयल वेडिंग वाइब्स!",
        ],
        "festival": [
            "🎉 त्योहारों की धूम!",
            "🎊 फेस्टिवल फैशन स्पेशल!",
            "🌺 ट्रेडिशनल लुक, मॉडर्न स्टाइल!",
        ]
    }
    
    captions = base_captions.get(theme, base_captions["fashion"])
    caption = random.choice(captions)
    
    if include_question:
        questions = [
            "\n\n💬 कमेंट में रेट करो 1-10!",
            "\n\n💬 क्या आप ये लुक वियर करेंगी? हाँ/ना",
            "\n\n💬 सबसे अच्छी चीज़ क्या लगी?",
            "\n\n💬 किस सेलिब्रिटी जैसी लग रही है?",
        ]
        caption += random.choice(questions)
    
    # बिलिंगुअल कैप्शन
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
    """प्रॉम्प्ट कितना वायरल होगा? (AI स्कोर)"""
    
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
    
    # कलर/वाइब्रेट वर्ड्स
    color_words = ["golden", "vibrant", "colorful", "warm", "glowing", "bright"]
    for word in color_words:
        if word in prompt_text.lower():
            score += 8
    
    return f"🎯 वायरल स्कोर: {min(score, 100)}%"

# ============================================
# 5. मुख्य अपलोड फंक्शन
# ============================================
def upload_ai_image(style_type="random", custom_title=None, caption=None):
    """AI इमेज जनरेट और अपलोड करें"""
    
    # प्रॉम्प्ट चुनें
    if style_type == "bridal":
        prompt = PROMPTS[0]
    elif style_type == "south":
        prompt = PROMPTS[1]
    elif style_type == "modern":
        prompt = PROMPTS[2]
    elif style_type == "rajasthani":
        prompt = PROMPTS[3]
    elif style_type == "kashmiri":
        prompt = PROMPTS[4]
    elif style_type == "random":
        prompt = random.choice(PROMPTS)
    else:
        prompt = random.choice(PROMPTS)
    
    # कैप्शन
    if caption:
        final_caption = caption
    else:
        final_caption = generate_caption()
    
    if custom_title:
        final_caption = f"🌟 {custom_title}\n\n{final_caption}"
    
    # वायरल स्कोर चेक (Option 5 के लिए)
    viral_score = predict_viral_score(prompt)
    print(f"\n{prompt[:100]}...")
    print(f"{viral_score}")
    
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
            print(f"📝 कैप्शन: {final_caption[:100]}...")
            print(f"📊 {viral_score}")
            return response.json().get('id')
        else:
            print(f"❌ फेल: {response.status_code}")
            print(f"⚠️ एरर: {response.text}")
            return None
            
    except Exception as e:
        print(f"⚠️ कनेक्शन एरर: {e}")
        return None

# ============================================
# 6. बल्क अपलोड
# ============================================
def bulk_upload(count=5, delay=300):
    """एक साथ कई पोस्ट"""
    print(f"\n📦 {count} पोस्ट अपलोड हो रही हैं...\n")
    
    styles = ["bridal", "south", "modern", "rajasthani", "kashmiri", "random"]
    titles = [
        "✨ रॉयल ब्राइडल लुक!",
        "🌸 साउथ इंडियन ब्यूटी!",
        "💃 मॉडर्न फ्यूजन फैशन!",
        "👑 राजस्थानी रानी!",
        "🏔️ कश्मीर की खूबसूरती!",
        "🌟 ट्रेंडिंग एथनिक लुक!"
    ]
    
    success = 0
    for i in range(count):
        style = random.choice(styles)
        title = random.choice(titles)
        
        post_id = upload_ai_image(style_type=style, custom_title=f"{title} ({i+1}/{count})")
        if post_id:
            success += 1
        
        if i < count - 1:
            print(f"⏳ {delay} सेकंड इंतज़ार...")
            time.sleep(delay)
    
    print(f"\n✅ {success}/{count} पोस्ट सफल!")

# ============================================
# 7. कैरोसेल पोस्ट
# ============================================
def upload_carousel_post(prompts_list=None, main_caption=None):
    """कैरोसेल पोस्ट (एक साथ कई फोटो)"""
    
    if not prompts_list:
        prompts_list = random.sample(PROMPTS, min(4, len(PROMPTS)))
    
    if not main_caption:
        main_caption = f"🎨 AI आर्ट कलेक्शन!\n\n{generate_caption()}"
    
    print(f"📸 कैरोसेल पोस्ट - {len(prompts_list)} फोटो")
    
    photo_ids = []
    for i, prompt in enumerate(prompts_list):
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1080&nologo=true"
        
        upload_url = f"https://graph.facebook.com/{PAGE_ID}/photos"
        payload = {
            'url': url,
            'published': 'false',
            'access_token': ACCESS_TOKEN
        }
        
        response = requests.post(upload_url, data=payload)
        if response.status_code == 200:
            photo_ids.append(response.json()['id'])
            print(f"✅ फोटो {i+1}/{len(prompts_list)} अपलोड")
        time.sleep(2)
    
    if photo_ids:
        carousel_url = f"https://graph.facebook.com/{PAGE_ID}/feed"
        carousel_data = {
            'message': main_caption,
            'attached_media': ','.join([f'{{"media_fbid":"{pid}"}}' for pid in photo_ids]),
            'access_token': ACCESS_TOKEN
        }
        
        response = requests.post(carousel_url, data=carousel_data)
        if response.status_code == 200:
            print(f"✅ कैरोसेल पोस्ट सफल!")
            return response.json().get('id')
    
    return None

# ============================================
# 8. कमेंट रिप्लाई बॉट
# ============================================
def auto_reply_comments(post_id):
    """ऑटो कमेंट रिप्लाई"""
    
    comments_url = f"https://graph.facebook.com/{post_id}/comments?access_token={ACCESS_TOKEN}"
    response = requests.get(comments_url)
    comments = response.json().get('data', [])
    
    replies = [
        "❤️ थैंक यू! आपको कौन सा लुक सबसे पसंद आया?",
        "💫 सच में? मुझे खुशी हुई! और कैसा लुक चाहिए?",
        "✨ ऐसे ही सपोर्ट करते रहो! नई पोस्ट जल्दी आएगी",
        "🎨 ये AI ने बनाया है! कमाल है ना?",
        "😊 आपका कमेंट पढ़कर अच्छा लगा! ❤️"
    ]
    
    count = 0
    for comment in comments[:5]:
        reply_url = f"https://graph.facebook.com/{comment['id']}/comments"
        payload = {
            'message': random.choice(replies),
            'access_token': ACCESS_TOKEN
        }
        resp = requests.post(reply_url, data=payload)
        if resp.status_code == 200:
            count += 1
        time.sleep(2)
    
    print(f"✅ {count} कमेंट्स का जवाब दिया")

# ============================================
# 9. एनालिटिक्स
# ============================================
def get_post_analytics(post_id):
    """पोस्ट परफॉर्मेंस ट्रैक करें"""
    
    url = f"https://graph.facebook.com/{post_id}/insights"
    params = {
        'metric': 'post_impressions,post_reactions,post_comments,post_shares',
        'access_token': ACCESS_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        metrics = {}
        for item in data.get('data', []):
            metrics[item['name']] = item.get('values', [{}])[0].get('value', 0)
        
        print(f"""
        📊 पोस्ट एनालिटिक्स:
        👀 इंप्रेशन: {metrics.get('post_impressions', 0)}
        ❤️ रिएक्शन्स: {metrics.get('post_reactions', 0)}
        💬 कमेंट्स: {metrics.get('post_comments', 0)}
        🔄 शेयर: {metrics.get('post_shares', 0)}
        """)
        return metrics
        
    except Exception as e:
        print(f"⚠️ एनालिटिक्स लोड नहीं हुए: {e}")
        return None

# ============================================
# 10. डेली चैलेंज
# ============================================
def daily_challenge():
    """डेली चैलेंज पोस्ट"""
    
    themes = [
        ("🌺 राजस्थानी रानी", "rajasthani"),
        ("🌸 केरल ब्राइड", "south"),
        ("💃 बॉलीवुड स्टार", "modern"),
        ("🌙 मूनलाइट ब्यूटY", "random"),
        ("✨ फेयरीटेल प्रिंसेस", "bridal")
    ]
    
    theme, style = random.choice(themes)
    
    caption = f"""
    {theme} - आज का AI चैलेंज!
    
    🎯 चैलेंज: कमेंट में इस लुक की 3 खूबियाँ बताओ!
    🏆 बेस्ट कमेंट को स्टोरी में शेयर करेंगे!
    
    {generate_caption('festival', include_question=False)}
    """
    
    post_id = upload_ai_image(style_type=style, custom_title=f"📌 डेली चैलेंज", caption=caption)
    return post_id

# ============================================
# 11. मेनू सिस्टम
# ============================================
def show_menu():
    """मुख्य मेनू"""
    
    while True:
        print("""
    ╔═══════════════════════════════════════╗
    ║   🤖 AI FASHION POSTER PRO v3.0     ║
    ╠═══════════════════════════════════════╣
    ║  1️⃣  सिंगल पोस्ट                    ║
    ║  2️⃣  बल्क पोस्ट (5 पोस्ट)          ║
    ║  3️⃣  कैरोसेल पोस्ट                  ║
    ║  4️⃣  डेली चैलेंज                    ║
    ║  5️⃣  वायरल स्कोर चेक                ║
    ║  6️⃣  कमेंट रिप्लाई बॉट              ║
    ║  7️⃣  एनालिटिक्स देखें               ║
    ║  8️⃣  एक्सिट                         ║
    ╚═══════════════════════════════════════╝
        """)
        
        choice = input("👉 अपना विकल्प चुनें (1-8): ").strip()
        
        if choice == "1":
            style = input("स्टाइल (bridal/south/modern/rajasthani/kashmiri/random): ") or "random"
            title = input("टाइटल (छोड़ें नहीं): ") or None
            post_id = upload_ai_image(style_type=style, custom_title=title)
            if post_id:
                print(f"✅ पोस्ट ID: {post_id}")
                
        elif choice == "2":
            count = input("कितनी पोस्ट? (5): ") or "5"
            delay = input("कितनी देर (सेकंड)? (300): ") or "300"
            bulk_upload(count=int(count), delay=int(delay))
            
        elif choice == "3":
            count = input("कितनी फोटो? (4): ") or "4"
            prompts = random.sample(PROMPTS, min(int(count), len(PROMPTS)))
            upload_carousel_post(prompts_list=prompts)
            
        elif choice == "4":
            post_id = daily_challenge()
            if post_id:
                print(f"✅ चैलेंज पोस्ट: {post_id}")
            
        elif choice == "5":
            print("\n📝 प्रॉम्प्ट दर्ज करें (या Enter दबाकर रैंडम):")
            user_prompt = input("👉 ").strip()
            if not user_prompt:
                user_prompt = random.choice(PROMPTS)
            score = predict_viral_score(user_prompt)
            print(f"\n{score}")
            print(f"\n📝 प्रॉम्प्ट: {user_prompt[:200]}...")
            
        elif choice == "6":
            post_id = input("पोस्ट ID दर्ज करें: ").strip()
            if post_id:
                auto_reply_comments(post_id)
            
        elif choice == "7":
            post_id = input("पोस्ट ID दर्ज करें: ").strip()
            if post_id:
                get_post_analytics(post_id)
            
        elif choice == "8":
            print("👋 शुक्रिया! AI पोस्टर बंद...")
            break
            
        else:
            print("❌ गलत विकल्प! 1-8 में से चुनें।")
        
        if choice != "8":
            input("\n⏎ Enter दबाकर मेनू पर लौटें...")

# ============================================
# 12. मेन रनर
# ============================================
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║   🤖 AI FASHION POSTER PRO v3.0     ║
    ║   ❤️  हाई-क्वालिटी AI पोस्टर       ║
    ║   🚀  इंडियन फैशन स्पेशल           ║
    ╚═══════════════════════════════════════╝
    """)
    
    # पहले चेक करें कि टोकन है या नहीं
    if not PAGE_ID or not ACCESS_TOKEN:
        print("❌ ERROR: FB_PAGE_ID और FB_ACCESS_TOKEN सेट करें!")
        print("📌 Export करें:")
        print("   export FB_PAGE_ID='your_page_id'")
        print("   export FB_ACCESS_TOKEN='your_token'")
        exit()
    
    show_menu()
