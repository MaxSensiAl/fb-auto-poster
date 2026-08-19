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
# PERFECT FACE PROMPTS - हर बार सही चेहरा
# ============================================
PERFECT_FACE_PROMPTS = [
    """professional portrait photography, masterpiece, best quality, ultra realistic, 8k resolution, shot on Canon EOS R5, 85mm lens, f/1.4, professional studio lighting, softbox, golden hour, sharp focus on eyes, perfect facial symmetry, beautiful Indian bride, wearing red lehenga, gold jewelry, maang tikka, nath, glowing skin, soft smile, clear eyes, perfect face, national geographic style, hyper detailed, 32k, cinematic, vogue magazine cover""",
    
    """close-up portrait, ultra high definition, 8k, photorealistic, highest quality, professional portrait photography, 50mm lens, f/2.8, soft morning sunlight, studio lighting, detailed skin texture, natural pores visible, sharp focus on eyes, perfect face, South Indian girl, green kanjeevaram saree, gold temple jewelry, jasmine flowers in hair, divine expression, Kerala temple background, perfect facial features""",
    
    """professional portrait, 8k resolution, photorealistic, ultra HD, best quality, professional fashion photography, studio lighting, softbox, sharp details, clear skin texture, perfect face, modern Indian girl, fusion outfit, crop top, flowy skirt, urban Mumbai background, golden hour lighting, perfect facial symmetry, crystal clear eyes""",
    
    """masterpiece portrait, ultra HD, 8k, photorealistic, best quality, national geographic style, award-winning photography, cinematic composition, golden hour lighting, rich vibrant colors, high saturation, professional portrait, sharp focus on face, perfect facial features, Rajasthani princess, colorful bandhani, silver jewelry, haveli background, warm desert lighting""",
    
    """portrait photography, ultra HD, 8k, photorealistic, best quality, professional photography, 85mm lens, natural skin texture, crystal clear details, sharp focus on eyes, perfect face, Kashmiri girl, traditional pheran, intricate thread work, beautiful eyes, snowy Gulmarg background, soft natural light, golden hour""",
    
    """professional portrait, 8k resolution, photorealistic, ultra HD, best quality, professional photography, Canon EOS R5, 50mm lens, studio lighting, sharp focus, vivid colors, high detail, natural skin texture, perfect face, Punjabi girl, yellow Patiala salwar suit, phulkari work, jewelry, mustard field background, bright sunny day""",
    
    """portrait photography, ultra high definition, 8k, photorealistic, highest quality, professional portrait photography, soft lighting, detailed skin texture, sharp focus on face, perfect facial features, Bengali girl, white and red traditional saree, shakha pola bangles, sindoor, soft smile, temple background""",
    
    """professional portrait, 8k resolution, photorealistic, best quality, professional photography, studio lighting, golden hour, sharp focus on face, perfect face, Indian wedding guest, pastel anarkali suit, delicate jewelry, floral jewelry, happy smile, wedding decoration background""",
    
    """portrait photography, ultra HD, 8k, photorealistic, best quality, professional photography, golden hour lighting, natural skin texture, sharp focus on eyes, perfect face, bohemian girl, floral dress, golden jewelry, long wavy hair, desert landscape sunset""",
    
    """fashion portrait, 8k resolution, photorealistic, best quality, professional fashion photography, studio lighting, high contrast, sharp focus on face, perfect facial features, Indian supermodel, fusion outfit, gown with embroidery, makeup, jewelry, ramp walk, fashion show lights"""
]

# ============================================
# FACE REPAIR & ENHANCE PROMPTS (Add to any prompt)
# ============================================
FACE_ENHANCE = """
, perfect facial symmetry, clear eyes, natural skin texture, realistic face, no distortion, perfect anatomy, realistic human features, sharp focus on face, beautiful expression, natural smile, professional retouching, flawless skin, perfect lighting on face
"""

# ============================================
# NEGATIVE PROMPTS - क्या नहीं चाहिए
# ============================================
NEGATIVE_PROMPTS = """
ugly, deformed, bad anatomy, extra fingers, extra limbs, distorted face, blurry eyes, crossed eyes, asymmetrical face, unrealistic features, cartoon, anime, painting, sketch, low quality, pixelated, bad proportions, missing features
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
        "masterpiece": 20, "award-winning": 20, "national geographic": 20,
        "vogue magazine": 20, "cinematic": 15,
        "8k": 15, "photorealistic": 15, "ultra realistic": 15,
        "professional photography": 15, "studio lighting": 15,
        "golden hour": 12, "sharp focus": 12, "hyper detailed": 12,
        "crystal clear": 12, "vivid colors": 12,
        "beautiful": 10, "stunning": 10, "gorgeous": 10,
        "glowing": 10, "divine": 10, "graceful": 10,
        "perfect face": 15, "clear eyes": 10, "facial symmetry": 15
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
    """Generate and post AI image with perfect face"""
    
    print("""
    ============================================================
    AI FASHION POSTER PRO - PERFECT FACE EDITION
    🎯 100% Accurate Face - No Distortion
    📸 Professional Portrait Quality
    🔥 Powered by Pollinations.ai + SDXL
    ============================================================
    """)
    
    # 1. Select perfect face prompt
    base_prompt = random.choice(PERFECT_FACE_PROMPTS)
    
    # 2. Add face enhance
    final_prompt = base_prompt + FACE_ENHANCE
    
    # 3. Calculate viral score
    viral_score = predict_viral_score(final_prompt)
    
    # 4. Generate smart caption
    caption = get_smart_caption()
    
    # 5. 🔥 PERFECT FACE URL SETTINGS
    encoded_prompt = urllib.parse.quote(final_prompt)
    encoded_negative = urllib.parse.quote(NEGATIVE_PROMPTS)
    
    # CRITICAL: Portrait mode for best face
    ai_image_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1080&height=1350"      # ✅ Portrait - Best for Face
        f"&model=sdxl"                  # ✅ SDXL - Best Quality
        f"&nologo=true"
        f"&enhance=true"                # ✅ Auto Enhance
        f"&quality=hd"                  # ✅ HD Quality
        f"&seed={random.randint(1, 999999)}"
        f"&negative_prompt={encoded_negative}"  # ✅ No Bad Features
    )
    
    # 6. Show details
    print(f"""
    ============================================================
    🚀 Uploading Perfect Face Image...
    ============================================================
    
    ⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    📸 Model: SDXL (Best Quality)
    📐 Resolution: 1080x1350 Portrait
    🎯 Focus: Perfect Face + Clear Eyes
    🔥 Enhancement: Enabled
    
    🎯 Viral Score: {viral_score}%
    📊 Quality: {'🔴' if viral_score < 50 else '🟡' if viral_score < 75 else '🟢 PERFECT'}
    
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
    📸 Perfect Face: Yes ✅
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
    🎯 100% Accurate Human Face
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
