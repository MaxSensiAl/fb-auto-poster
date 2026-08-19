import requests
import random
import os
import sys
import time
import urllib.parse
from datetime import datetime

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
# 🎯 FIXED: PROMPTS WITH FACE CONSISTENCY
# ============================================
PERFECT_FACE_PROMPTS = [
    # ⭐ This prompt ensures SAME FACE, SAME CHARACTER
    """A ultra-high-resolution, crystal-clear portrait of a young South Asian woman with a specific, consistent face. 
    She has almond-shaped brown eyes, a small nose, heart-shaped face, and warm wheatish complexion. 
    She is wearing a traditional pink and maroon headscarf and shawl with gold embroidery.
    SAME FACE, SAME PERSON in EVERY generation. 
    Background shows sharp, clear snow-capped mountains and wooden fence under natural sunlight.
    High-definition, 8k resolution, hyper-realistic, professional photography, 
    National Geographic quality, sharp focus, cinematic lighting, rich textures.""",
    
    # Backup with specific features
    """A stunning medium-close up portrait of a beautiful Indian bride. 
    SAME FACE: specific woman with round face, big expressive dark eyes, full lips, straight nose, 
    wearing traditional red bridal wear with highly detailed gold embroidery.
    SAME PERSON, IDENTICAL FEATURES every time.
    Wearing delicate gold maang tikka and matching earrings. 
    Soft glowing studio light, realistic skin texture, shot on 85mm lens, f/1.4, 8k, photorealistic""",
]

# ============================================
# 🖼️ IMAGE GENERATION - FIXED FOR QUALITY
# ============================================

def generate_flux_image_high_quality(prompt_text, filename="temp_flux.jpg"):
    """Generate HIGH QUALITY FLUX image - FIXED"""
    print("🎨 Generating FLUX image (High Quality)...")
    
    # Enhanced prompt for better quality and consistency
    quality_prompt = f"{prompt_text} ultra-high-resolution, 8k, photorealistic, crystal clear, professional photography, National Geographic quality, hyper-detailed, sharp focus, same face, same character"
    
    encoded_prompt = urllib.parse.quote(quality_prompt.strip())
    
    # Better parameters for higher quality
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1280"  # Balanced size
        f"&model=flux-pro"
        f"&nologo=true"
        f"&seed={random.randint(1, 9999999)}"  # Random seed for variety
        f"&quality=high"
        f"&enhance=true"
    )
    
    try:
        print(f"⏳ Generating image... (may take 30-60 seconds)")
        response = requests.get(flux_url, timeout=180)
        
        if response.status_code == 200:
            content_size = len(response.content)
            if content_size < 50000:  # Too small = bad quality
                print(f"⚠️ Image too small ({content_size} bytes), retrying...")
                return None
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ FLUX Success! Size: {content_size/1024:.1f} KB")
            return filename
        else:
            print(f"❌ FLUX failed: {response.status_code}")
    except Exception as e:
        print(f"❌ FLUX error: {e}")
    return None

def generate_hf_image_high_quality(prompt_text, filename="temp_hf.jpg"):
    """Generate via Hugging Face SDXL"""
    if not HF_TOKEN:
        print("⚠️ HF_TOKEN not found, skipping...")
        return None
    
    print("🎨 Generating via Hugging Face SDXL...")
    
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Enhanced prompt for consistency
    enhanced_prompt = f"{prompt_text}, same face, same character, high quality, 8k, photorealistic"
    
    payload = {
        "inputs": enhanced_prompt,
        "parameters": {
            "negative_prompt": "ugly, deformed, blurry, low quality, bad anatomy, distorted face, different face, changed features",
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
            if content_size > 50000:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ HF Success! Size: {content_size/1024:.1f} KB")
                return filename
        else:
            print(f"❌ HF failed: {response.status_code}")
    except Exception as e:
        print(f"❌ HF error: {e}")
    return None

def generate_ultimate_image_high_quality(prompt):
    """Try multiple methods for best quality"""
    print("🖼️ Starting HIGH-QUALITY image generation...")
    
    # First try FLUX
    result = generate_flux_image_high_quality(prompt)
    if result and os.path.exists(result) and os.path.getsize(result) > 50000:
        return result
    
    # Then try HF if available
    if HF_TOKEN:
        result = generate_hf_image_high_quality(prompt)
        if result and os.path.exists(result) and os.path.getsize(result) > 50000:
            return result
    
    # Fallback: Try FLUX with different settings
    print("🔄 Trying FLUX with different settings...")
    return generate_flux_retry(prompt)

def generate_flux_retry(prompt, filename="temp_flux2.jpg"):
    """Retry FLUX with different parameters"""
    try:
        encoded_prompt = urllib.parse.quote(f"{prompt}, high quality, 8k")
        flux_url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width=1024&height=1024"
            f"&model=flux"
            f"&nologo=true"
            f"&seed={random.randint(1, 9999999)}"
        )
        
        response = requests.get(flux_url, timeout=180)
        if response.status_code == 200:
            content_size = len(response.content)
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ FLUX Retry Success! Size: {content_size/1024:.1f} KB")
            return filename
    except Exception as e:
        print(f"❌ FLUX retry error: {e}")
    return None

# ============================================
# 📝 FIXED: STATIC CAPTION GENERATOR
# ============================================

def generate_static_caption():
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

#AIFashion #TrendingStyle #IndianBeauty #AICreation #ViralFashion #ExplorePage #FYP #StyleInspo #OOTD #FashionGoals #AIModel #DigitalFashion #AIArtwork #ModernBride #IndianWear #FusionFashion #AIArtist #VirtualFashion #TechStyle #InstaFashion #DailyFashion #Fashionista #AICouture #VirtualInfluencer #IndianFashionBlogger #AIForFashion"""
    ]
    return random.choice(captions)

# ============================================
# 📝 GEMINI CAPTION GENERATOR (FIXED)
# ============================================

def generate_gemini_caption_fixed(prompt_context):
    """Fixed Gemini caption generator"""
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        print("⚠️ Gemini not available, using static caption...")
        return generate_static_caption()  # ✅ Now works!
    
    try:
        print("🤖 Generating Gemini caption...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Create a viral Instagram caption for an AI-generated high-quality Indian beauty portrait.

Image context: {prompt_context[:200]}

Requirements:
1. Write in Hinglish (Hindi + English mix)
2. Start with catchy emoji hook
3. Include 2-3 interactive questions in Hindi
4. Add 20-25 trending hashtags
5. Keep under 2200 characters
6. Make it engaging and desi vibe

Caption:"""
        
        response = model.generate_content(prompt)
        if response and response.text:
            print("✅ Gemini caption generated!")
            return response.text[:2200]
        
    except Exception as e:
        print(f"⚠️ Gemini caption failed: {e}")
    
    return generate_static_caption()  # ✅ Fixed fallback

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
# 🎯 MAIN BOT - FIXED VERSION
# ============================================

def run_bot_high_quality():
    """Complete workflow - FIXED version"""
    
    print("\n" + "="*60)
    print("🚀 STARTING HIGH-QUALITY AI BOT")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # Step 1: Select prompt
        selected_prompt = PERFECT_FACE_PROMPTS[0]
        print("📝 Using high-quality prompt with face consistency...")
        
        # Step 2: Generate HIGH QUALITY image
        print("\n🖼️ GENERATING IMAGE...")
        image_path = generate_ultimate_image_high_quality(selected_prompt)
        
        if not image_path or not os.path.exists(image_path):
            print("❌ CRITICAL: No image generated!")
            return False
        
        file_size = os.path.getsize(image_path)
        print(f"✅ Image ready: {image_path} ({file_size/1024:.1f} KB)")
        
        # Step 3: Generate caption
        print("\n📝 GENERATING CAPTION...")
        caption = generate_gemini_caption_fixed(selected_prompt)
        print(f"✅ Caption ready ({len(caption)} chars)")
        
        # Step 4: Post to Facebook
        print("\n📤 POSTING TO FACEBOOK...")
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
