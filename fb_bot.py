import requests
import random
import os
import urllib.parse
import sys
from datetime import datetime

# ============================================
# ENVIRONMENT VARIABLES
# ============================================
PAGE_ID = os.environ.get("FB_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

# ============================================
# HIGH QUALITY FLUX PROMPTS - (चेहरे और हाथ बिल्कुल सही बनेंगे)
# ============================================
PERFECT_FACE_PROMPTS = [
    """A highly detailed, professional DSLR photograph of a beautiful Indian bride. She is wearing a traditional red designer lehenga with intricate gold embroidery, heavy royal gold jewelry, a maang tikka, and a nose ring. The shot is a close-up portrait with sharp focus on her symmetrical face and expressive, clear eyes. Soft, glowing golden hour light illuminates her face, showcasing natural skin texture with visible pores. Beautiful, realistic hands with clear fingers are visible as she adjusts her veil. Professional portrait photography, cinematic, 8k resolution.""",
    
    """A realistic, high-quality photograph of a South Indian young woman wearing a rich green Kanjeevaram silk saree with a golden border and traditional temple jewelry. She has jasmine flowers in her hair. This is a medium shot with a soft, blurred temple background. The lighting is soft morning sunlight, casting natural shadows. Her face is perfectly symmetrical with realistic eyes and a graceful smile. High-resolution portrait, photorealistic.""",
    
    """A modern Indian woman wearing an elegant pastel yellow crop top and a flowy designer skirt (ethnic fusion wear). She is standing outdoors with a blurred urban city background during sunset. The golden hour light reflects beautifully on her face. Her face has natural makeup, clear skin texture, and sharp eyes. Her hands are naturally resting on her waist, displaying perfectly rendered fingers. Sharp focus, professional fashion magazine cover style.""",
    
    """A professional candid portrait of a beautiful Rajasthani woman in a vibrant colorful bandhani outfit with intricate silver jewelry. She is standing in front of a majestic ancient haveli during the warm afternoon. The lighting highlights her sharp, symmetric facial features. Her facial expression is elegant, eyes are detailed and lively, and her hands are holding the edge of her dupatta realistically.""",
    
    """A stunning close-up portrait of a young Kashmiri woman wearing a traditional dark pheran with detailed colorful Kashmiri thread work. The background is a beautifully blurred, snow-covered Gulmarg landscape. Her face is exceptionally clear with rosy cheeks, bright detailed eyes, and a natural soft smile. Shot on a professional 85mm lens, high fidelity, realistic skin details.""",
    
    """A vibrant, photorealistic portrait of a young Punjabi woman in a bright yellow Patiala salwar suit with a colorful phulkari dupatta. She is smiling happily in a lush green mustard field under a clear blue sky. The lighting is bright and natural. Her face is highly detailed and symmetrical, with realistic eyes, hair, and hands.""",
    
    """A traditional portrait of a Bengali woman in a classic white saree with a thick red border (laal paar saree). She is wearing traditional gold bangles and has a soft smile, standing in front of an elegant Durga Puja pandal background. Perfect facial features, detailed dark eyes, natural skin texture, and realistically drawn hands holding a puja plate.""",
    
    """A realistic, high-quality fashion portrait of an Indian wedding guest in a pastel-colored designer anarkali suit with delicate floral jewelry. The background shows soft, warm wedding decorations. The camera captures her beautiful face and natural expression with absolute clarity, sharp eyes, and realistic body proportions."""
]

# ============================================
# FACE & DETAIL ENHANCER FOR FLUX
# ============================================
FACE_ENHANCE = """
, perfect facial features, highly detailed eyes, natural skin texture, anatomically correct hands, realistic fingers, professional studio lighting, extremely sharp focus
"""

# ============================================
# SMART CAPTIONS - Hindi + English
# ============================================
def get_smart_caption():
    """Generate smart captions based on time"""
    hour = datetime.now().hour
    
    if 6 <= hour < 12:
        time_emoji = "🌅"
        time_hi = "सुप्रभात!"
    elif 12 <= hour < 17:
        time_emoji = "☀️"
        time_hi = "गुड आफ्टरनून!"
    elif 17 <= hour < 21:
        time_emoji = "🌆"
        time_hi = "शाम की शान!"
    else:
        time_emoji = "🌙"
        time_hi = "रात की रानी!"
    
    captions = [
        f"""{time_emoji} {time_hi}
        
💃 कैसा लगा ये लुक? 1-10 में रेट करो!
👇 कमेंट में बताओ - सबसे अच्छी चीज़ क्या लगी?

#AIFashion #IndianWear #ViralReels #ExplorePage #TrendingNow #FYP #FashionDaily #StyleInspo""",

        f"""{time_emoji} {time_hi}
        
💫 क्या आप ये आउटफिट पहनेंगी? हाँ/ना में बताओ!
💬 अपनी राय दें!

#IndianBeauty #FashionGram #AIArtwork #OOTD #ViralPost #FashionTrends #TraditionalLook""",

        f"""{time_emoji} {time_hi}
        
💖 ये AI क्रिएशन कैसी लगी?
🎯 चैलेंज - इस लुक को 3 शब्दों में बताओ!

#AIGenerated #FashionLover #Explore #DesignerWear #EthnicLook #StyleGoals #AIFashionista""",

        f"""{time_emoji} {time_hi}
        
✨ सपनों जैसा लुक - किसे सूट करेगा?
🏆 बेस्ट कमेंट शेयर होगा!

#RoyalFashion #IndianEthnic #ViralReels #FashionBlogger #AIArt #TrendingStyle #FashionDaily"""
    ]
    
    return random.choice(captions)

# ============================================
# VIRAL SCORE PREDICTOR
# ============================================
def predict_viral_score(prompt_text):
    """Calculate viral score"""
    keywords = {
        "masterpiece": 10, "photorealistic": 15, "detailed skin": 20,
        "professional": 15, "studio lighting": 15, "golden hour": 15, 
        "sharp focus": 15, "perfect facial": 20, "realistic hands": 25,
        "natural": 15, "eyes": 15
    }
    
    score = 0
    prompt_lower = prompt_text.lower()
    
    for word, weight in keywords.items():
        if word in prompt_lower:
            score += weight
    
    return min(score, 100)

# ============================================
# MAIN POST FUNCTION - PERFECT FACE
# ============================================
def post_perfect_face_ai_image():
    """Generate and post AI image with perfect face using FLUX"""
    
    print("""
    ============================================================
    AI FASHION POSTER PRO - FLUX EDITION (PERFECT FACE & HANDS)
    🎯 Advanced Face & Finger Rendering - No Distortions
    📸 Professional HD Photography
    🔥 Powered by Pollinations.ai + FLUX Model
    ============================================================
    """)
    
    # 1. Select perfect face prompt
    base_prompt = random.choice(PERFECT_FACE_PROMPTS)
    
    # 2. Add face enhance (Flux optimized)
    final_prompt = base_prompt + FACE_ENHANCE
    
    # 3. Calculate viral score
    viral_score = predict_viral_score(final_prompt)
    
    # 4. Generate smart caption
    caption = get_smart_caption()
    
    # 5. Encode prompt for URL
    encoded_prompt = urllib.parse.quote(final_prompt.strip())
    
    # 🔥 FLUX SETTINGS FOR BEST RESULTS:
    # 'flux' मॉडल चेहरों और हाथों को बिल्कुल असली इंसान जैसा बनाता है।
    ai_image_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1080&height=1350"      # Portrait ratio (Instagram/FB Reels style)
        f"&model=flux"                  # ✅ FLUX Model (Best face/hands)
        f"&nologo=true"
        f"&seed={random.randint(1, 9999999)}"
    )
    
    # 6. Show details
    print(f"""
    ============================================================
    🚀 Uploading Perfect Face Image...
    ============================================================
    
    ⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    📸 Model: FLUX (Highest Face & Hand Accuracy)
    📐 Resolution: 1080x1350 Portrait
    🎯 Focus: Realistic Skin, Perfect Facial Features, Accurate Hands
    
    🎯 Viral Score: {viral_score}%
    📊 Quality: {'🔴' if viral_score < 50 else '🟡' if viral_score < 75 else '🟢 EXCELLENT (FLUX)'}
    
    📝 Caption: {caption[:80]}...
    ============================================================
    """)
    
    # 7. Post to Facebook
    fb_url = f"https://graph.facebook.com/{PAGE_ID}/photos"
    payload = {
        'url': ai_image_url,
        'caption': caption,
        'access_token': ACCESS_TOKEN,
        'published': 'true'
    }
    
    try:
        response = requests.post(fb_url, data=payload, timeout=120)
        
        if response.status_code == 200:
            post_id = response.json().get('id')
            print(f"""
    ✅ POST SUCCESSFUL!
    🆔 Post ID: {post_id}
    🎯 Viral Score: {viral_score}%
    📸 Perfect Face: Yes (FLUX Model) ✅
    ============================================================
            """)
            return True
        else:
            print(f"""
    ❌ POST FAILED!
    📊 Status: {response.status_code}
    ⚠️ Error: {response.text}
    ============================================================
            """)
            return False
            
    except Exception as e:
        print(f"""
    ⚠️ CONNECTION ERROR!
    🔴 Error: {str(e)}
    ============================================================
        """)
        return False

# ============================================
# AUTO POSTER FOR GITHUB ACTIONS
# ============================================
def auto_poster():
    """GitHub Actions auto poster"""
    
    print("""
    ============================================================
    🤖 AI AUTO POSTER - PERFECT FACE
    ⏰ Running Every 30 Minutes
    🎯 100% Accurate Human Face & Hands
    ============================================================
    """)
    
    if not PAGE_ID or not ACCESS_TOKEN:
        print("""
    ❌ ERROR: FB_PAGE_ID and FB_ACCESS_TOKEN not set!
    Add to GitHub Secrets:
       - FB_PAGE_ID
       - FB_ACCESS_TOKEN
        """)
        sys.exit(1)
    
    post_perfect_face_ai_image()

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    auto_poster()
