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
# HIGH QUALITY PROMPTS - 10X BETTER
# ============================================
HIGH_QUALITY_PROMPTS = [
    """masterpiece, best quality, ultra realistic, 8k resolution, award-winning photography, shot on Canon EOS R5, 85mm lens, f/1.4, professional studio lighting, softbox, golden hour, sharp focus, shallow depth of field, bokeh background, national geographic style, hyper detailed, 32k, cinematic, vogue magazine cover style, a breathtakingly beautiful Indian bride wearing heavy red and gold bridal lehenga, intricate zari work, traditional gold jewelry, maang tikka, nath, glowing skin with dewy makeup, soft natural smile""",
    
    """ultra high definition, 8k, photorealistic, highest quality, professional portrait photography, 50mm lens, f/2.8, soft morning sunlight, studio lighting, detailed skin texture, natural pores visible, sharp focus, vivid colors, HDR, cinematic composition, national geographic quality, hyper realistic textures, 16k resolution, a gorgeous South Indian girl in green kanjeevaram silk saree, heavy gold temple jewelry, jasmine flowers in hair, divine expression, Kerala temple background""",
    
    """8k resolution, photorealistic, ultra HD, best quality, professional fashion photography, studio lighting, softbox, sharp details, clear skin texture, natural pose, shot on Sony A7R IV, 24-70mm lens, fashion magazine editorial, vogue quality, vivid colors, high contrast, crystal clear, a stylish modern Indian girl in fusion outfit, crop top with flowy skirt, urban Mumbai background, golden hour lighting""",
    
    """ultra HD, 8k, photorealistic, best quality, national geographic style, award-winning photography, cinematic composition, golden hour lighting, rich vibrant colors, high saturation, professional portrait, sharp focus, intricate details, Canon EOS R5, 85mm lens, a beautiful Rajasthani princess in colorful bandhani, heavy silver jewelry, mirror work outfit, haveli background, warm desert lighting""",
    
    """ultra HD, 8k, photorealistic, best quality, professional photography, 85mm lens, natural skin texture, crystal clear details, sharp focus, scenic beauty, winter light, studio lighting, high detail, a stunning Kashmiri girl in traditional pheran, intricate thread work, beautiful eyes, snowy Gulmarg background, soft natural light, golden hour""",
    
    """8k resolution, photorealistic, ultra HD, best quality, professional photography, Canon EOS R5, 50mm lens, studio lighting, sharp focus, vivid colors, high detail, natural skin texture, a stunning Punjabi girl wearing a bright yellow Patiala salwar suit, beautiful dupatta, vibrant phulkari work, traditional Punjabi jewelry, mustard field background, bright sunny day, happy expression, colorful, joyful""",
    
    """ultra high definition, 8k, photorealistic, highest quality, professional portrait photography, soft lighting, detailed skin texture, sharp focus, cinematic composition, a graceful Bengali girl, wearing a white and red traditional Bengali saree, shakha pola bangles, beautiful sindoor, soft smile, temple background, cultural vibe, elegant, photorealistic""",
    
    """8k resolution, photorealistic, best quality, professional photography, studio lighting, golden hour, sharp focus, shallow depth of field, a stylish Indian girl dressed as a wedding guest, pastel colored anarkali suit, delicate jewelry, floral jewelry, happy smile, wedding decoration background with flowers and lights, festive vibe, elegant pose, soft warm lighting""",
    
    """ultra HD, 8k, photorealistic, best quality, professional photography, golden hour lighting, natural skin texture, sharp focus, Canon EOS R5, a beautiful girl with bohemian style, flowy floral dress, golden jewelry, long wavy hair, desert landscape at sunset, golden hour glow, wind blowing her hair, free-spirited look, artistic, cinematic""",
    
    """8k resolution, photorealistic, best quality, professional fashion photography, studio lighting, high contrast, sharp focus, a confident Indian supermodel on the runway, modern fusion outfit, floor-length gown with Indian embroidery, stylish makeup, chunky jewelry, ramp walk, fashion show lights, dramatic shadows, high fashion, professional"""
]

# ============================================
# SMART CAPTIONS - HIGH ENGAGEMENT
# ============================================
def get_smart_caption():
    """Generate smart captions based on time"""
    
    hour = datetime.now().hour
    
    if 6 <= hour < 12:
        time_emoji = "🌅"
        time_text = "Good Morning! Today's first AI creation"
    elif 12 <= hour < 17:
        time_emoji = "☀️"
        time_text = "Afternoon beauty"
    elif 17 <= hour < 21:
        time_emoji = "🌆"
        time_text = "Evening elegance"
    else:
        time_emoji = "🌙"
        time_text = "Night queen"
    
    captions = [
        f"""{time_emoji} {time_text}!
        
💃 How do you like this look? Rate 1-10!

👇 Comment below - What's the best thing about this outfit?

#AIFashion #IndianWear #ViralReels #ExplorePage #TrendingNow #FYP #FashionDaily #StyleInspo""",

        f"""{time_emoji} {time_text}!
        
💫 Would you wear this outfit? Yes/No

💬 Drop your opinion - We need your comment!

#IndianBeauty #FashionGram #AIArtwork #OOTD #ViralPost #FashionTrends #TraditionalLook""",

        f"""{time_emoji} {time_text}!
        
💖 How is this AI creation?

🎯 Challenge - Describe this look in 3 words!

#AIGenerated #FashionLover #Explore #DesignerWear #EthnicLook #StyleGoals #AIFashionista""",

        f"""{time_emoji} {time_text}!
        
✨ Dreamy look - Who would this suit?

🏆 Best comment will be shared!

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
        "fashion": 8, "style": 8, "traditional": 8,
        "modern": 8, "elegant": 8, "royal": 8,
        "bokeh": 5, "depth of field": 5, "hdr": 5,
        "high contrast": 5, "natural skin": 5
    }
    
    score = 0
    prompt_lower = prompt_text.lower()
    
    for word, weight in keywords.items():
        if word in prompt_lower:
            score += weight
    
    return min(score, 100)

# ============================================
# MAIN POST FUNCTION
# ============================================
def post_high_quality_ai_image():
    """Generate and post high quality AI image"""
    
    print("""
    ===================================================
    AI FASHION POSTER PRO - HIGH QUALITY
    10X Better Quality Images
    Powered by SDXL + Canon EOS R5
    ===================================================
    """)
    
    # 1. Select high quality prompt
    prompt = random.choice(HIGH_QUALITY_PROMPTS)
    
    # 2. Calculate viral score
    viral_score = predict_viral_score(prompt)
    
    # 3. Generate smart caption
    caption = get_smart_caption()
    
    # 4. Create high quality URL
    encoded_prompt = urllib.parse.quote(prompt)
    
    ai_image_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1920&height=1080"
        f"&model=sdxl"
        f"&nologo=true"
        f"&seed={random.randint(1, 999999)}"
    )
    
    # 5. Show details
    print(f"""
    ===================================================
    Uploading started...
    ===================================================
    
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Day: {datetime.now().strftime('%A')}
    
    Model: SDXL (Best Quality)
    Resolution: 1920x1080 Full HD
    Camera: Canon EOS R5 + 85mm Lens
    Lighting: Studio Lighting + Golden Hour
    
    Viral Score: {viral_score}%
    Quality Level: {'🔴' if viral_score < 50 else '🟡' if viral_score < 75 else '🟢'}
    
    Caption: {caption[:80]}...
    ===================================================
    """)
    
    # 6. Post to Facebook
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
    Post ID: {post_id}
    Viral Score: {viral_score}%
    Quality: 10X Improved!
    ===================================================
            """)
            return True
        else:
            print(f"""
    ❌ POST FAILED!
    Status: {response.status_code}
    Error: {response.text}
    ===================================================
            """)
            return False
            
    except Exception as e:
        print(f"""
    ⚠️ CONNECTION ERROR!
    Error: {str(e)}
    ===================================================
        """)
        return False

# ============================================
# AUTO POSTER FOR GITHUB ACTIONS
# ============================================
def auto_poster():
    """GitHub Actions auto poster"""
    
    print("""
    ===================================================
    AI AUTO POSTER - GITHUB ACTIONS
    Running on Schedule
    High Quality Images Every 30 Mins
    ===================================================
    """)
    
    if not PAGE_ID or not ACCESS_TOKEN:
        print("""
    ❌ ERROR: FB_PAGE_ID and FB_ACCESS_TOKEN not set!
    Add to GitHub Secrets:
       - FB_PAGE_ID
       - FB_ACCESS_TOKEN
        """)
        sys.exit(1)
    
    success = post_high_quality_ai_image()
    
    if not success:
        print("❌ Post failed! Retrying...")
        time.sleep(10)
        post_high_quality_ai_image()

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    auto_poster()
