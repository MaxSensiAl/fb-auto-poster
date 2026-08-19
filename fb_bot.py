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
# PROMPTS (Indian Beauty Focused)
# ============================================
PERFECT_FACE_PROMPTS = [
    """A stunning medium-close up portrait of a beautiful Indian bride. She is wearing traditional red bridal wear with highly detailed gold embroidery. Sharp focus on her symmetrical face and expressive clear eyes. Wearing a delicate gold maang tikka and matching earrings. Soft glowing studio light, realistic skin texture with subtle film grain, shot on 85mm lens, f/1.4, flawless cinematic photo, 8k, photorealistic, highly detailed""",
    
    """Medium shot of a South Indian young woman wearing a rich green Kanjeevaram silk saree with a golden border, visible from waist up. She has jasmine flowers in her hair and wears traditional identical gold earrings. Traditional background with warm morning sunlight, natural skin pores, soft smile, highly detailed and realistic face, 8k, photorealistic""",
    
    """Close-up fashion portrait of a modern Indian influencer girl wearing an elegant pastel yellow dress, looking at the camera with a soft smile. Blurred city lights in the background during golden hour. Symmetrical delicate jewelry, realistic skin texture, beautiful eyes, captured on a professional DSLR, highly realistic, 8k, photorealistic""",
    
    """Medium portrait shot of a beautiful Rajasthani princess visible from waist up. She is wearing a vibrant colorful traditional outfit with intricate silver jewelry. Symmetrical identical silver earrings, flawless facial features, natural lighting, shot on 35mm film, analog photo style, highly detailed, 8k""",
    
    """Close-up scenic portrait of a young Kashmiri woman wearing a traditional dark pheran with colorful embroidery. Beautiful rosy cheeks, detailed realistic eyes, snow-covered Gulmarg landscape blurred in the background. Natural soft daylight, highly realistic and authentic face texture, 8k, photorealistic""",
    
    """Medium shot of a Bengali woman in a classic white saree with a red border, visible from the chest up. She is wearing traditional identical gold bangles and earrings, smiling gracefully. Durga Puja pandal background with warm festive lights, sharp focus on her clear and flawless face, 8k, photorealistic"""
]

# ============================================
# 🎨 IMAGE GENERATION (Multiple Methods)
# ============================================

def generate_flux_image(prompt_text, filename="temp_flux.jpg"):
    """Method 1: Pollinations FLUX (No API Key)"""
    print("🎨 Method 1: Pollinations FLUX...")
    
    encoded_prompt = urllib.parse.quote(prompt_text.strip())
    flux_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=2048&height=2560"
        f"&model=flux"
        f"&nologo=true"
        f"&seed={random.randint(1, 9999999)}"
    )
    
    try:
        response = requests.get(flux_url, timeout=90)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ FLUX Success! Size: {len(response.content)} bytes")
            return filename
        else:
            print(f"❌ FLUX failed: {response.status_code}")
    except Exception as e:
        print(f"❌ FLUX error: {e}")
    return None

def generate_hf_image(prompt_text, filename="temp_hf.jpg"):
    """Method 2: Hugging Face SDXL (Requires HF_TOKEN)"""
    if not HF_TOKEN:
        print("⚠️ HF_TOKEN not found, skipping...")
        return None
    
    print("🎨 Method 2: Hugging Face SDXL...")
    
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Better prompt for HF
    enhanced_prompt = f"{prompt_text}, high quality, 8k, photorealistic, detailed face, professional photography"
    
    payload = {
        "inputs": enhanced_prompt,
        "parameters": {
            "negative_prompt": "ugly, deformed, blurry, low quality, bad anatomy, distorted face, extra limbs, cartoon, drawing, painting",
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
            "width": 1024,
            "height": 1280
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ HF Success! Size: {len(response.content)} bytes")
            return filename
        else:
            print(f"❌ HF failed: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"❌ HF error: {e}")
    return None

def generate_placeholder_image(filename="temp_placeholder.jpg"):
    """Method 3: Generate placeholder if everything fails"""
    print("🎨 Creating placeholder image...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a gradient background
        img = Image.new('RGB', (1080, 1350), color=(255, 200, 230))
        draw = ImageDraw.Draw(img)
        
        # Draw some decorative elements
        for i in range(0, 1080, 100):
            draw.line([(i, 0), (i, 1350)], fill=(255, 180, 210), width=2)
        for i in range(0, 1350, 100):
            draw.line([(0, i), (1080, i)], fill=(255, 180, 210), width=2)
        
        # Add text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        text = "✨ AI Beauty ✨"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (1080 - text_width) // 2
        y = (1350 - text_height) // 2 - 50
        draw.text((x, y), text, fill=(200, 50, 100), font=font)
        
        text2 = "Generated by AI Bot"
        try:
            font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        except:
            font2 = ImageFont.load_default()
        text2_bbox = draw.textbbox((0, 0), text2, font=font2)
        text2_width = text2_bbox[2] - text2_bbox[0]
        x2 = (1080 - text2_width) // 2
        y2 = y + text_height + 30
        draw.text((x2, y2), text2, fill=(150, 50, 80), font=font2)
        
        img.save(filename)
        print(f"✅ Placeholder created!")
        return filename
    except Exception as e:
        print(f"❌ Placeholder creation failed: {e}")
        # Final fallback - create empty file
        with open(filename, 'wb') as f:
            f.write(b"PLACEHOLDER_IMAGE")
        return filename

def generate_ultimate_image(prompt):
    """Master function: Try all methods until success"""
    
    print("🖼️ Starting image generation...")
    
    # Try HF first (best quality)
    hf_result = generate_hf_image(prompt)
    if hf_result and os.path.exists(hf_result) and os.path.getsize(hf_result) > 1000:
        return hf_result
    
    # Try FLUX second (good quality)
    flux_result = generate_flux_image(prompt)
    if flux_result and os.path.exists(flux_result) and os.path.getsize(flux_result) > 1000:
        return flux_result
    
    # Final fallback - placeholder
    print("⚠️ All API methods failed! Creating placeholder...")
    return generate_placeholder_image()

# ============================================
# 📝 CAPTION GENERATION (Multiple Methods)
# ============================================

def generate_static_caption():
    """Method 1: Static captions"""
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

#AIGirl #IndianBeauty #AIFashion #ViralPost #Explore #TrendingNow #AICommunity #DigitalArt #AIArt #FashionGram #BridalFashion #IndianBride #AIContent #TechGirl #FutureFashion #AIModeling #VirtualInfluencer #AIReels #InstaReels #FYPシ #ViralReels #AICreations #BeautyAI #IndianTraditions #ModernFashion""",
        
        f"""{time_text}

🌟 AI Generated - Trending Indian Look!

🔥 पहली बार देखकर क्या लगा?
👇 Comment me batao:
😱 - Amazing! 
😍 - Beautiful!
🤯 - Unbelievable!

🎬 Next Post - आपके Favourite Style पर!

#AITrends #IndianFashion #AIModel #ViralContent #ExplorePage #FYP #TrendingReels #AIFashionista #DesiGirl #FashionInspo #AICreation #DigitalArt #AIBeauty #IndianStyle #TraditionalWear #ModernIndian #AIWorld #TechArt #FashionDaily #InstaTrending #ViralNow #AICommunity #ArtOfAI #IndianGirl #FusionWear""",

        f"""{time_text}

✨ AI Magic - Creating Perfect Indian Beauty!

🎯 Quick Poll:
1️⃣ Bridal Look - ❤️
2️⃣ Casual Look - 💙
3️⃣ Traditional Look - 💚
4️⃣ Modern Look - 💛

👇 Reaction mein vote karo!

#AIPortrait #IndianBeauty #AIArtwork #ViralPost #FYP #Explore #TrendingStyle #AICreation #DigitalInfluencer #FashionDaily #IndianFashionBlogger #BridalInspo #AIForGood #TechFashion #ModernArt #AIArtist #VirtualModel #InstagramViral #ReelsViral #AIContentCreator #FutureOfAI #BeautyTech #IndianAesthetic #DesiBeauty #FusionStyle"""
    ]
    return random.choice(captions)

def generate_gemini_caption(prompt_context):
    """Method 2: AI-generated caption using Gemini"""
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        return generate_static_caption()
    
    try:
        print("🤖 Generating Gemini caption...")
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Create a viral Instagram caption for an AI-generated Indian beauty portrait.

Context about the image: {prompt_context[:200]}

Requirements:
1. Write in Hinglish (mix of Hindi and English)
2. Start with a catchy emoji hook
3. Include 2-3 interactive questions 
4. Ask for comments in Hindi
5. Add 25-30 trending hashtags (mix of English and Hindi)
6. Keep it under 2200 characters
7. Make it sound like a popular Indian influencer

Style: Trendy, engaging, desi vibe, encourages interaction
Tone: Excited, friendly, conversational

Caption:"""
        
        response = model.generate_content(prompt)
        if response and response.text:
            print("✅ Gemini caption generated!")
            return response.text[:2200]  # Instagram limit
        
    except Exception as e:
        print(f"⚠️ Gemini caption failed: {e}")
    
    return generate_static_caption()

def generate_ultimate_caption(prompt_context):
    """Master function: Try AI first, fallback to static"""
    
    # Try Gemini first (most engaging)
    gemini_caption = generate_gemini_caption(prompt_context)
    if gemini_caption and len(gemini_caption) > 50:
        return gemini_caption
    
    # Fallback to static
    print("⚠️ Using static caption fallback...")
    return generate_static_caption()

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
        # Check if file exists and is valid
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
            
            # Try alternative method
            print("🔄 Trying alternative upload method...")
            return post_to_facebook_alt(image_path, caption)
            
    except Exception as e:
        print(f"⚠️ Error uploading to Facebook: {e}")
        return None

def post_to_facebook_alt(image_path, caption):
    """Alternative method: Upload as URL"""
    try:
        # Read image and encode as base64
        with open(image_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        
        fb_url = f"https://graph.facebook.com/{PAGE_ID}/photos"
        payload = {
            'caption': caption,
            'access_token': ACCESS_TOKEN,
            'published': 'true',
            'source': img_data
        }
        
        response = requests.post(fb_url, data=payload, timeout=120)
        if response.status_code == 200:
            post_id = response.json().get('id')
            print(f"✅ ALT POST SUCCESSFUL! Post ID: {post_id}")
            return post_id
        else:
            print(f"❌ ALT Upload Failed: {response.text[:200]}")
    except Exception as e:
        print(f"❌ ALT upload error: {e}")
    return None

# ============================================
# 🧹 CLEANUP FUNCTION
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
# 🎯 MAIN BOT WORKFLOW
# ============================================

def run_bot():
    """Complete workflow - NEVER FAILS"""
    
    print("\n" + "="*60)
    print("🚀 STARTING ULTIMATE AI BOT")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # Step 1: Select random prompt
        selected_prompt = random.choice(PERFECT_FACE_PROMPTS)
        print(f"📝 Selected prompt: {selected_prompt[:100]}...")
        
        # Step 2: Generate image (multi-method)
        print("\n🖼️ IMAGE GENERATION PHASE")
        image_path = generate_ultimate_image(selected_prompt)
        
        if not image_path or not os.path.exists(image_path):
            print("❌ CRITICAL: No image generated!")
            return False
        
        print(f"✅ Image ready: {image_path} ({os.path.getsize(image_path)} bytes)")
        
        # Step 3: Generate caption (AI + fallback)
        print("\n📝 CAPTION GENERATION PHASE")
        caption = generate_ultimate_caption(selected_prompt)
        print(f"✅ Caption generated ({len(caption)} chars)")
        
        # Step 4: Post to Facebook (with retry)
        print("\n📤 POSTING PHASE")
        post_id = post_local_file_to_facebook(image_path, caption)
        
        # Step 5: Cleanup
        cleanup_files(image_path)
        
        elapsed = time.time() - start_time
        
        if post_id:
            print("\n" + "="*60)
            print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            print(f"⏱️ Time: {elapsed:.2f} seconds")
            print(f"📱 Post ID: {post_id}")
            print("="*60)
            return True
        else:
            print("\n" + "="*60)
            print("❌ WORKFLOW FAILED AT POSTING STAGE")
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
    # Run the bot
    success = run_bot()
    
    # Exit with proper code
    sys.exit(0 if success else 1)
