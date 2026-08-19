import requests
import random
import os
import sys
import time
import urllib.parse
import base64
from datetime import datetime
from io import BytesIO

# Try importing Gemini (optional)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Google Generative AI not installed. Run: pip install google-generativeai")

# ============================================
# ENVIRONMENT VARIABLES
# ============================================
PAGE_ID = os.environ.get("FB_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API")
HF_TOKEN = os.environ.get("HF_TOKEN")

# Check Facebook credentials
if not PAGE_ID or not ACCESS_TOKEN:
    print("❌ ERROR: Facebook credentials missing!")
    sys.exit(1)

# Configure Gemini if available
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Gemini AI configured successfully!")
    except Exception as e:
        print(f"⚠️ Gemini configuration failed: {e}")

# ============================================
# HIGH-QUALITY PROMPTS
# ============================================
PERFECT_FACE_PROMPTS = [
    # ⭐⭐⭐ Aapka Special High-Quality Prompt
    """A ultra-high-resolution, crystal-clear, detailed portrait of a young South Asian woman wearing a traditional pink and maroon headscarf and shawl. Maintaining the exact same face, features, expression, and clothing as the original photo. The background shows sharp, clear snow-capped mountains and a wooden fence under natural sunlight. High-definition photographic enhancement, rich textures, fine facial details, natural skin texture, crisp focus, cinematic lighting, 8k resolution, hyper-realistic, professional photography, national geographic quality""",
    
    # Backup prompts
    """A stunning medium-close up portrait of a beautiful Indian bride wearing traditional red bridal wear with highly detailed gold embroidery. Sharp focus on symmetrical face and expressive clear eyes. Wearing delicate gold maang tikka and matching earrings. Soft glowing studio light, realistic skin texture with subtle film grain, shot on 85mm lens, f/1.4, flawless cinematic photo, 8k, hyper-realistic""",
    
    """Close-up scenic portrait of a young Kashmiri woman wearing a traditional dark pheran with colorful embroidery. Beautiful rosy cheeks, detailed realistic eyes, snow-covered Gulmarg landscape blurred in the background. Natural soft daylight, highly realistic and authentic face texture, 8k, photorealistic""",
]

# ============================================
# 🎨 HIGH-QUALITY IMAGE GENERATION
# ============================================

def generate_flux_image_high_quality(prompt_text, filename="temp_flux.jpg"):
    """Method 1: Pollinations FLUX - HIGH QUALITY"""
    print("🎨 Method 1: Pollinations FLUX (High Quality Mode)...")
    
    quality_prompt = f"{prompt_text}, ultra-high-resolution, 8k, photorealistic, crystal clear, professional photography, national geographic quality, hyper-detailed, sharp focus"
    
    encoded_prompt = urllib.parse.quote(quality_prompt.strip())
    
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=4096&height=5120"
        f"&model=flux-pro"
        f"&nologo=true"
        f"&seed={random.randint(1, 9999999)}"
        f"&quality=high"
        f"&enhance=true"
    )
    
    try:
        response = requests.get(flux_url, timeout=120)
        if response.status_code == 200:
            content_size = len(response.content)
            if content_size < 100000:
                print(f"⚠️ Image too small ({content_size} bytes), retrying...")
                return None
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ FLUX Success! Size: {content_size} bytes ({content_size/1024:.1f} KB)")
            return filename
        else:
            print(f"❌ FLUX failed: {response.status_code}")
    except Exception as e:
        print(f"❌ FLUX error: {e}")
    return None

def generate_flux_image_high_quality_retry(prompt_text, filename="temp_flux.jpg"):
    """Retry with different parameters"""
    print("🔄 Retrying FLUX with different settings...")
    
    quality_prompt = f"{prompt_text}, 8k, photorealistic, ultra-detailed, professional photography, crystal clear"
    encoded_prompt = urllib.parse.quote(quality_prompt.strip())
    
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=2048&height=2560"
        f"&model=flux"
        f"&nologo=true"
        f"&seed={random.randint(1, 9999999)}"
        f"&quality=high"
        f"&enhance=true"
    )
    
    try:
        response = requests.get(flux_url, timeout=90)
        if response.status_code == 200:
            content_size = len(response.content)
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ FLUX Retry Success! Size: {content_size} bytes ({content_size/1024:.1f} KB)")
            return filename
        else:
            print(f"❌ FLUX retry failed: {response.status_code}")
    except Exception as e:
        print(f"❌ FLUX retry error: {e}")
    return None

def generate_hf_image_high_quality(prompt_text, filename="temp_hf.jpg"):
    """Method 2: Hugging Face SDXL"""
    if not HF_TOKEN:
        print("⚠️ HF_TOKEN not found, skipping...")
        return None
    
    print("🎨 Method 2: Hugging Face SDXL (High Quality)...")
    
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    enhanced_prompt = f"{prompt_text}, ultra-high-resolution, 8k, photorealistic, crystal clear, professional photography"
    
    payload = {
        "inputs": enhanced_prompt,
        "parameters": {
            "negative_prompt": "ugly, deformed, blurry, low quality, bad anatomy, distorted face",
            "num_inference_steps": 50,
            "guidance_scale": 7.5,
            "width": 1024,
            "height": 1280,
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            content_size = len(response.content)
            if content_size > 100000:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ HF Success! Size: {content_size} bytes ({content_size/1024:.1f} KB)")
                return filename
        else:
            print(f"❌ HF failed: {response.status_code}")
    except Exception as e:
        print(f"❌ HF error: {e}")
    return None

def generate_ultimate_image_high_quality(prompt):
    """Master: Try all methods for HIGH QUALITY"""
    
    print("🖼️ Starting HIGH-QUALITY image generation...")
    
    # Try 1: Pollinations FLUX (High Quality)
    flux_result = generate_flux_image_high_quality(prompt)
    if flux_result and os.path.exists(flux_result) and os.path.getsize(flux_result) > 100000:
        return flux_result
    
    # Try 2: Hugging Face SDXL
    if HF_TOKEN:
        hf_result = generate_hf_image_high_quality(prompt)
        if hf_result and os.path.exists(hf_result) and os.path.getsize(hf_result) > 100000:
            return hf_result
    
    # Try 3: Standard FLUX (fallback)
    print("🔄 Trying standard FLUX (fallback)...")
    flux_standard = generate_flux_image_high_quality_retry(prompt)
    if flux_standard:
        return flux_standard
    
    # Final: Placeholder
    print("⚠️ Creating high-quality placeholder...")
    return generate_placeholder_high_quality()

def generate_placeholder_high_quality(filename="temp_placeholder.jpg"):
    """Generate a high-quality placeholder"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (2048, 2560), color=(255, 200, 230))
        draw = ImageDraw.Draw(img)
        
        # Decorative lines
        for i in range(0, 2048, 50):
            draw.line([(i, 0), (i, 2560)], fill=(255, 180, 210), width=3)
        for i in range(0, 2560, 50):
            draw.line([(0, i), (2048, i)], fill=(255, 180, 210), width=3)
        
        # Text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
            font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
        except:
            font = ImageFont.load_default()
            font2 = ImageFont.load_default()
        
        text = "✨ AI Beauty ✨"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (2048 - text_width) // 2
        y = (2560 - text_height) // 2 - 80
        draw.text((x, y), text, fill=(200, 50, 100), font=font)
        
        text2 = "Generated by AI Bot - High Quality"
        text2_bbox = draw.textbbox((0, 0), text2, font=font2)
        text2_width = text2_bbox[2] - text2_bbox[0]
        x2 = (2048 - text2_width) // 2
        y2 = y + text_height + 50
        draw.text((x2, y2), text2, fill=(150, 50, 80), font=font2)
        
        img.save(filename, quality=95, optimize=False)
        print(f"✅ High-quality placeholder created!")
        return filename
    except Exception as e:
        print(f"❌ Placeholder creation failed: {e}")
        with open(filename, 'wb') as f:
            f.write(b"HIGH_QUALITY_PLACEHOLDER_IMAGE")
        return filename

# ============================================
# 📝 STATIC CAPTION GENERATOR (FIXED)
# ============================================

def generate_static_caption():  # ✅ Yeh function define kiya
    """Static captions - Always works"""
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

🔥 AI Generated Perfect Indian Bride Look!

क्या आपको लगता है ये Real है या AI? 🤔
👇 3 Second mein comment karo:
1️⃣ Kitne number doge? (1-10)
2️⃣ Sabse best kya hai - Dress, Jewelry, ya Face?

💡 50+ Comments = Next Post Aaj Raat hi!

#AIBride #IndianWedding #AIArt #TrendingReels #ViralPost #FYP #ExplorePage #AIFashion #BridalWear #AICommunity #DigitalArt #AIInfluencer #AIModel #FashionAI #IndianFashion #BollywoodStyle #AIArtCommunity #ViralReels #InstagramReels #Explore #TrendingNow #AIContent #AIGirl #ArtificialIntelligence #TechFashion #FutureOfFashion #AIforIndia #IndianAI #DesiBride #ShaadiGoals""",

        f"""{time_text}

💃 AI ने बनाया ये Stunning Look! 

क्या आप ये outfit पहनेंगी? 👗
👇 Comment mein batao:
❤️ Haan - agar pasand aaya
💔 Na - agar nahi pasand

🎯 100+ Reactions = Next Look और भी Better!

#AIFashion #TrendingStyle #IndianBeauty #AICreation #ViralFashion #ExplorePage #FYP #StyleInspo #OOTD #FashionGoals #AIModel #DigitalFashion #AIArtwork #ModernBride #IndianWear #FusionFashion #AIArtist #VirtualFashion #TechStyle #InstaFashion #DailyFashion #Fashionista #AICouture #VirtualInfluencer #IndianFashionBlogger #AIForFashion""",

        f"""{time_text}

✨ AI Generated - Perfect Indian Beauty!

💫 Vote karo - Best feature kya hai?
👇 Comment me likho:
👁️ Eyes
💎 Jewelry 
👗 Dress
💄 Makeup

📢 200+ Votes = Special Announcement!

#AIGirl #IndianBeauty #AIFashion #ViralPost #Explore #TrendingNow #AICommunity #DigitalArt #AIArt #FashionGram #BridalFashion #IndianBride #AIContent #TechGirl #FutureFashion #AIModeling #VirtualInfluencer #AIReels #InstaReels #FYPシ #ViralReels #AICreations #BeautyAI #IndianTraditions #ModernFashion"""
    ]
    return random.choice(captions)

# ============================================
# 📝 GEMINI CAPTION GENERATOR (FIXED)
# ============================================

def generate_gemini_caption_fixed(prompt_context):
    """Method: Gemini AI caption with correct model"""
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        print("⚠️ Gemini not available, using static caption...")
        return generate_static_caption()  # ✅ Fixed: Sahi function call
    
    try:
        print("🤖 Generating Gemini caption (NEW model)...")
        
        # Try new model first
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Create a viral Instagram caption for an AI-generated high-quality Indian beauty portrait.

Image context: {prompt_context[:200]}

Requirements:
1. Write in Hinglish (Hindi + English mix)
2. Start with catchy emoji hook
3. Include 2-3 interactive questions in Hindi
4. Add 25-30 trending hashtags
5. Keep under 2200 characters
6. Make it engaging and desi vibe

Caption:"""
        
        response = model.generate_content(prompt)
        if response and response.text:
            print("✅ Gemini caption generated!")
            return response.text[:2200]
        
    except Exception as e:
        print(f"⚠️ Gemini caption failed: {e}")
    
    # Fallback to static
    return generate_static_caption()  # ✅ Fixed: Sahi function call

# ============================================
# 📤 FACEBOOK POSTING
# ============================================

def post_local_file_to_facebook(image_path, caption):
    """Upload image to Facebook Page"""
    print("📤 Uploading to Facebook...")
    
    fb_url = f"https://graph.facebook.com/{PAGE_ID}/photos"
    
    payload = {
        'caption': caption,
        'access_token': ACCESS_TOKEN,
        'published': 'true'
    }
    
    try:
        if not os.path.exists(image_path) or os.path.getsize(image_path) < 100:
            print("❌ Image file invalid!")
            return None
        
        with open(image_path, 'rb') as img_file:
            files = {'source': img_file}
            response = requests.post(fb_url, data=payload, files=files, timeout=120)
        
        if response.status_code == 200:
            post_id = response.json().get('id')
            print(f"✅ POST SUCCESSFUL! Post ID: {post_id}")
            return post_id
        else:
            print(f"❌ Facebook Upload Failed: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"⚠️ Error uploading to Facebook: {e}")
        return None

# ============================================
# 🧹 CLEANUP
# ============================================

def cleanup_files(*files):
    """Delete temporary files"""
    for file in files:
        if file and os.path.exists(file):
            try:
                os.remove(file)
                print(f"🧹 Removed: {file}")
            except:
                pass

# ============================================
# 🎯 MAIN BOT - HIGH QUALITY VERSION
# ============================================

def run_bot_high_quality():
    """Complete workflow - HIGH QUALITY version"""
    
    print("\n" + "="*60)
    print("🚀 STARTING HIGH-QUALITY AI BOT")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # Step 1: Select YOUR prompt
        selected_prompt = PERFECT_FACE_PROMPTS[0]
        print(f"📝 Using your high-quality prompt...")
        
        # Step 2: Generate HIGH QUALITY image
        print("\n🖼️ HIGH-QUALITY IMAGE GENERATION")
        image_path = generate_ultimate_image_high_quality(selected_prompt)
        
        if not image_path or not os.path.exists(image_path):
            print("❌ CRITICAL: No image generated!")
            return False
        
        file_size = os.path.getsize(image_path)
        print(f"✅ Image ready: {image_path} ({file_size/1024:.1f} KB)")
        
        if file_size < 100000:
            print(f"⚠️ WARNING: Image quality might be low ({file_size/1024:.1f} KB)")
        
        # Step 3: Generate caption
        print("\n📝 CAPTION GENERATION")
        caption = generate_gemini_caption_fixed(selected_prompt)
        print(f"✅ Caption generated ({len(caption)} chars)")
        
        # Step 4: Post to Facebook
        print("\n📤 POSTING TO FACEBOOK")
        post_id = post_local_file_to_facebook(image_path, caption)
        
        # Step 5: Cleanup
        cleanup_files(image_path)
        
        elapsed = time.time() - start_time
        
        if post_id:
            print("\n" + "="*60)
            print("🎉 HIGH-QUALITY POST SUCCESSFUL!")
            print(f"⏱️ Time: {elapsed:.2f} seconds")
            print(f"📱 Post ID: {post_id}")
            print("="*60)
            return True
        else:
            print("\n" + "="*60)
            print("❌ POST FAILED")
            print("="*60)
            return False
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================
# 🚀 EXECUTION
# ============================================

if __name__ == "__main__":
    success = run_bot_high_quality()
    sys.exit(0 if success else 1)
