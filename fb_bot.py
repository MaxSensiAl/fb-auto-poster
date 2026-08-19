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
# 🎯 HIGH QUALITY PROMPTS - 10X बेहतर
# ============================================
HIGH_QUALITY_PROMPTS = [
    # 1. उत्तम ब्राइडल - सबसे वायरल
    """masterpiece, best quality, ultra realistic, 8k resolution, award-winning photography, shot on Canon EOS R5, 85mm lens, f/1.4, professional studio lighting, softbox, golden hour, sharp focus, shallow depth of field, bokeh background, national geographic style, hyper detailed, 32k, cinematic, vogue magazine cover style, a breathtakingly beautiful Indian bride wearing heavy red and gold bridal lehenga, intricate zari work, traditional gold jewelry, maang tikka, nath, glowing skin with dewy makeup, soft natural smile""",
    
    # 2. साउथ इंडियन - क्रिस्टल क्लियर
    """ultra high definition, 8k, photorealistic, highest quality, professional portrait photography, 50mm lens, f/2.8, soft morning sunlight, studio lighting, detailed skin texture, natural pores visible, sharp focus, vivid colors, HDR, cinematic composition, national geographic quality, hyper realistic textures, 16k resolution, a gorgeous South Indian girl in green kanjeevaram silk saree, heavy gold temple jewelry, jasmine flowers in hair, divine expression, Kerala temple background""",
    
    # 3. मॉडर्न फ्यूजन - क्लियर + स्टाइलिश
    """8k resolution, photorealistic, ultra HD, best quality, professional fashion photography, studio lighting, softbox, sharp details, clear skin texture, natural pose, shot on Sony A7R IV, 24-70mm lens, fashion magazine editorial, vogue quality, vivid colors, high contrast, crystal clear, a stylish modern Indian girl in fusion outfit, crop top with flowy skirt, urban Mumbai background, golden hour lighting""",
    
    # 4. राजस्थानी - रिच कलर्स
    """ultra HD, 8k, photorealistic, best quality, national geographic style, award-winning photography, cinematic composition, golden hour lighting, rich vibrant colors, high saturation, professional portrait, sharp focus, intricate details, Canon EOS R5, 85mm lens, a beautiful Rajasthani princess in colorful bandhani, heavy silver jewelry, mirror work outfit, haveli background, warm desert lighting""",
    
    # 5. कश्मीरी - क्रिस्प + क्लियर
    """ultra HD, 8k, photorealistic, best quality, professional photography, 85mm lens, natural skin texture, crystal clear details, sharp focus, scenic beauty, winter light, studio lighting, high detail, a stunning Kashmiri girl in traditional pheran, intricate thread work, beautiful eyes, snowy Gulmarg background, soft natural light, golden hour""",
    
    # 6. पंजाबी सुईट - ब्राइट एंड क्लियर
    """8k resolution, photorealistic, ultra HD, best quality, professional photography, Canon EOS R5, 50mm lens, studio lighting, sharp focus, vivid colors, high detail, natural skin texture, a stunning Punjabi girl wearing a bright yellow Patiala salwar suit, beautiful dupatta, vibrant phulkari work, traditional Punjabi jewelry, mustard field background, bright sunny day, happy expression, colorful, joyful""",
    
    # 7. बंगाली शाड़ी - एलिगेंट
    """ultra high definition, 8k, photorealistic, highest quality, professional portrait photography, soft lighting, detailed skin texture, sharp focus, cinematic composition, a graceful Bengali girl, wearing a white and red traditional Bengali saree, shakha pola bangles, beautiful sindoor, soft smile, temple background, cultural vibe, elegant, photorealistic""",
    
    # 8. एथनिक वेडिंग गेस्ट
    """8k resolution, photorealistic, best quality, professional photography, studio lighting, golden hour, sharp focus, shallow depth of field, a stylish Indian girl dressed as a wedding guest, pastel colored anarkali suit, delicate jewelry, floral jewelry, happy smile, wedding decoration background with flowers and lights, festive vibe, elegant pose, soft warm lighting""",
    
    # 9. बोहो-गिप्सी
    """ultra HD, 8k, photorealistic, best quality, professional photography, golden hour lighting, natural skin texture, sharp focus, Canon EOS R5, a beautiful girl with bohemian style, flowy floral dress, golden jewelry, long wavy hair, desert landscape at sunset, golden hour glow, wind blowing her hair, free-spirited look, artistic, cinematic""",
    
    # 10. रैंप वॉक
    """8k resolution, photorealistic, best quality, professional fashion photography, studio lighting, high contrast, sharp focus, a confident Indian supermodel on the runway, modern fusion outfit, floor-length gown with Indian embroidery, stylish makeup, chunky jewelry, ramp walk, fashion show lights, dramatic shadows, high fashion, professional"""
]

# ============================================
# 🎯 SMART CAPTIONS - इंगेजमेंट बढ़ाने वाले
# ============================================
def get_smart_caption():
    """टाइम, दिन और मूड के हिसाब से स्मार्ट कैप्शन"""
    
    hour = datetime.now().hour
    day = datetime.now().strftime("%A")
    month = datetime.now().strftime("%B")
    
    # ⏰ Time based greetings
    if 6 <= hour < 12:
        time_emoji = "🌅"
        time_text = "गुड मॉर्निंग! आज की पहली AI क्रिएशन"
    elif 12 <= hour < 17:
        time_emoji = "☀️"
        time_text = "दोपहर की खूबसूरती"
    elif 17 <= hour < 21:
        time_emoji = "🌆"
        time_text = "शाम की शान"
    else:
        time_emoji = "🌙"
        time_text = "रात की रानी"
    
    # 📅 Day based themes
    day_themes = {
        "Monday": "🎯 नए हफ्ते की शुरुआत!",
        "Tuesday": "💪 ट्यूज़डे मोड ऑन!",
        "Wednesday": "🐪 वेडनेसडे वाइब्स!",
        "Thursday": "🎉 थर्सडे की धूम!",
        "Friday": "🔥 फ्राइडे फंडे!",
        "Saturday": "🎊 शनिवार का मज़ा!",
        "Sunday": "😌 संडे स्पेशल!"
    }
    
    day_text = day_themes.get(day, "✨ आज का स्पेशल लुक!")
    
    # 🎨 Caption variations
    captions = [
        f"""{time_emoji} {time_text}!
        
{day_text}

💃 कैसा लगा ये लुक? 1-10 में रेट करो!

👇 कमेंट में बताओ - सबसे अच्छी चीज़ क्या लगी?

#AIFashion #IndianWear #ViralReels #ExplorePage #TrendingNow #FYP #FashionDaily #StyleInspo""",

        f"""{time_emoji} {time_text}!
        
💫 {day_text}

👗 क्या आप ये आउटफिट वियर करेंगी? हाँ/ना में बताओ!

💬 अपनी राय दें - हमें आपका कमेंट चाहिए!

#IndianBeauty #FashionGram #AIArtwork #OOTD #ViralPost #FashionTrends #TraditionalLook""",

        f"""{time_emoji} {time_text}!
        
🌟 {day_text}

💖 ये AI क्रिएशन कैसी लगी?

🎯 चैलेंज - इस लुक को 3 शब्दों में बताओ!

#AIGenerated #FashionLover #Explore #DesignerWear #EthnicLook #StyleGoals #AIFashionista""",

        f"""{time_emoji} {time_text}!
        
👑 {day_text}

✨ सपनों जैसा ये लुक - किसे सूट करेगा?

🏆 बेस्ट कमेंट को शेयर करेंगे!

#RoyalFashion #IndianEthnic #ViralReels #FashionBlogger #AIArt #TrendingStyle #FashionDaily""",

        f"""{time_emoji} {time_text}!
        
🌸 {day_text}

💎 AI की कला और इंडियन ट्रेडिशन का मिलन!

❓ अगर ये आपकी दोस्त होती तो क्या कहते?

#IndianCulture #AIArtist #FashionDesign #AICreation #TopFashion #ExplorePage #Viral"
    ]
    
    return random.choice(captions)

# ============================================
# 🎯 VIRAL SCORE PREDICTOR
# ============================================
def predict_viral_score(prompt_text):
    """वायरल स्कोर कैलकुलेट करें"""
    
    keywords = {
        # Ultra Premium Keywords (20 points)
        "masterpiece": 20, "award-winning": 20, "national geographic": 20,
        "vogue magazine": 20, "cinematic": 15,
        
        # Premium Keywords (15 points)
        "8k": 15, "photorealistic": 15, "ultra realistic": 15,
        "professional photography": 15, "studio lighting": 15,
        
        # High Quality Keywords (12 points)
        "golden hour": 12, "sharp focus": 12, "hyper detailed": 12,
        "crystal clear": 12, "vivid colors": 12,
        
        # Beauty Keywords (10 points)
        "beautiful": 10, "stunning": 10, "gorgeous": 10,
        "glowing": 10, "divine": 10, "graceful": 10,
        
        # Fashion Keywords (8 points)
        "fashion": 8, "style": 8, "traditional": 8,
        "modern": 8, "elegant": 8, "royal": 8,
        
        # Technical Keywords (5 points)
        "bokeh": 5, "depth of field": 5, "hdr": 5,
        "high contrast": 5, "natural skin": 5
    }
    
    score = 0
    prompt_lower = prompt_text.lower()
    
    for word, weight in keywords.items():
        if word in prompt_lower:
            score += weight
    
    # Bonus: अगर सभी 5 Quality Points हैं
    quality_points = ["canon eos r5", "85mm", "studio lighting", "golden hour", "8k"]
    bonus = sum(1 for word in quality_points if word in prompt_lower)
    if bonus >= 4:
        score += 20  # Extra Quality Bonus
    
    return min(score, 100)

# ============================================
# 📤 MAIN POST FUNCTION - HIGH QUALITY
# ============================================
def post_high_quality_ai_image():
    """हाई-क्वालिटी AI Image जनरेट करें और Facebook पर पोस्ट करें"""
    
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   📸 AI FASHION POSTER PRO - HIGH QUALITY   ║
    ║   🎯 10X Better Quality Images              ║
    ║   ⚡ Powered by SDXL + Canon EOS R5         ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    # 1️⃣ High Quality Prompt चुनें
    prompt = random.choice(HIGH_QUALITY_PROMPTS)
    
    # 2️⃣ Viral Score Check
    viral_score = predict_viral_score(prompt)
    
    # 3️⃣ Smart Caption
    caption = get_smart_caption()
    
    # 4️⃣ High Quality URL - SDXL Model + HD Resolution
    encoded_prompt = urllib.parse.quote(prompt)
    
    # 🔥 BEST QUALITY SETTINGS - ALL 5 POINTS
    ai_image_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1920&height=1080"  # ✅ HD Resolution
        f"&model=sdxl"              # ✅ Best Model
        f"&nologo=true"
        f"&seed={random.randint(1, 999999)}"  # Unique Image
    )
    
    # 📊 Show Details
    print(f"""
    ═══════════════════════════════════════════════
    📤 अपलोडिंग शुरू...
    ═══════════════════════════════════════════════
    
    🕐 समय: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    📅 दिन: {datetime.now().strftime('%A')}
    
    📸 Model: SDXL (Best Quality)
    📐 Resolution: 1920x1080 Full HD
    🎨 Camera: Canon EOS R5 + 85mm Lens
    💡 Lighting: Studio Lighting + Golden Hour
    
    🎯 Viral Score: {viral_score}%
    🔥 Quality Level: {'🔴' if viral_score < 50 else '🟡' if viral_score < 75 else '🟢'}
    
    📝 कैप्शन: {caption[:80]}...
    ═══════════════════════════════════════════════
    """)
    
    # 5️⃣ Facebook पर पोस्ट करें
    fb_url = f"https://graph.facebook.com/{PAGE_ID}/photos"
    payload = {
        'url': ai_image_url,
        'caption': caption,
        'access_token': ACCESS_TOKEN,
        'published': 'true'
    }
    
    try:
        response = requests.post(fb_url, data=payload, timeout=90)
        
        if response.status_code == 200:
            post_id = response.json().get('id')
            print(f"""
    ✅ POST SUCCESSFUL!
    🆔 Post ID: {post_id}
    📊 Viral Score: {viral_score}%
    🎯 Quality: 10X Improved!
    ═══════════════════════════════════════════════
            """)
            return True
        else:
            print(f"""
    ❌ POST FAILED!
    📊 Status: {response.status_code}
    ⚠️ Error: {response.text}
    ═══════════════════════════════════════════════
            """)
            return False
            
    except Exception as e:
        print(f"""
    ⚠️ CONNECTION ERROR!
    🔴 {str(e)}
    ═══════════════════════════════════════════════
        """)
        return False

# ============================================
# 🔄 AUTO POSTER - GitHub Actions के लिए
# ============================================
def auto_poster():
    """GitHub Actions Auto Poster"""
    
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   🤖 AI AUTO POSTER - GITHUB ACTIONS        ║
    ║   ⏰ Running on Schedule                    ║
    ║   🔥 High Quality Images Every 30 Mins      ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    # Check Credentials
    if not PAGE_ID or not ACCESS_TOKEN:
        print("""
    ❌ ERROR: FB_PAGE_ID और FB_ACCESS_TOKEN सेट नहीं है!
    📌 GitHub Secrets में डालें:
       - FB_PAGE_ID
       - FB_ACCESS_TOKEN
        """)
        sys.exit(1)
    
    # Post करें
    success = post_high_quality_ai_image()
    
    if not success:
        print("❌ पोस्ट फेल हो गई! Retrying...")
        time.sleep(10)
        # एक बार और Retry करें
        post_high_quality_ai_image()

# ============================================
# 🚀 MAIN
# ============================================
if __name__ == "__main__":
    auto_poster()
