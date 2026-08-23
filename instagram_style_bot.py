import os
import sys
import time
import random
import requests
import urllib.parse
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import json

# ============================================
# 🔐 GITHUB SECRETS से VARIABLES लें
# ============================================
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

# Check Credentials
if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
    print("❌ Facebook Credentials नहीं मिले!")
    sys.exit(1)

print(f"✅ Facebook Page ID: {FB_PAGE_ID[:5]}***")
print(f"✅ Facebook Token: {FB_ACCESS_TOKEN[:10]}...")

# ============================================
# 🌐 मजबूत नेटवर्क सेशन सेटअप
# ============================================
session = requests.Session()
retry_strategy = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    raise_on_status=False
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# ============================================
# 🎨 20+ UNIQUE PROMPTS
# ============================================

PROMPTS = [
    "Full body shot of a beautiful Indian woman standing in Himalayan mountains, colorful traditional pheran, snowfall, snow-capped peaks background, natural lighting, 8k, photorealistic",
    "Full body portrait of a stunning Indian woman in traditional Rajasthani attire, standing in front of a grand palace, yellow sandstone palace, golden hour lighting, majestic background, 8k",
    "Full body shot of a beautiful Indian woman on Goa beach, breezy summer dress, white sand beach, blue ocean, palm trees, sunset lighting, romantic atmosphere, 8k",
    "Full body portrait of an Indian woman in modern fusion wear, standing in front of Red Fort Delhi, evening lighting, city vibe, confident pose, professional photography, 8k",
    "Full body shot of a South Indian woman in traditional saree, standing on a houseboat in Kerala backwaters, green palm trees, kasavu saree, natural lighting, serene, 8k",
    "Full body portrait of an Indian woman in colorful attire, walking in Jaipur's pink city bazaar, bright lehenga, vibrant market atmosphere, warm lighting, candid style, 8k",
    "Full body shot of an Indian woman on Haridwar ghats, evening aarti background, traditional saree, holding a diya, spiritual atmosphere, golden lighting, 8k",
    "Full body portrait of a woman in elegant fusion wear, standing by Lake Pichola Udaipur, lake palace visible, flowing dress, sunset lighting, romantic vibe, 8k",
    "Full body shot of a Bengali woman in traditional saree, walking in Kolkata streets, yellow taxi background, white saree with red border, street photography, natural lighting, 8k",
    "Full body portrait of a South Indian woman in silk saree, standing in front of Mysore Palace at night, kanjivaram saree, temple jewelry, night photography, dramatic lighting, 8k",
    "Full body shot of an Indian woman on Ladakh road trip, standing near a jeep, mountains background, winter jacket, rugged landscape, travel photography, adventure vibe, 8k",
    "Full body portrait of a woman in traditional attire, standing in front of a temple in Vrindavan, colorful saree, holding flowers, spiritual atmosphere, peaceful, 8k",
    "Full body shot of an Indian woman in modern fusion wear, standing in front of iconic architecture, contemporary outfit, urban vibe, professional photography, 8k",
    "Full body portrait of a woman on Rameshwaram beach, ocean background, flowing summer dress, natural lighting, peaceful beach atmosphere, 8k",
    "Full body shot of an Indian woman near Ajanta caves, traditional attire, historical architecture, spiritual vibe, natural lighting, cultural atmosphere, 8k",
    "Full body portrait of a woman on Mall Road Shimla, snow-capped mountains background, winter outfit, beautiful winter lighting, cozy atmosphere, 8k",
    "Full body shot of a Sikh woman at Golden Temple Amritsar, golden temple background, salwar kameez, spiritual atmosphere, warm lighting, 8k",
    "Full body portrait of a modern Indian woman on Marine Drive Mumbai, Queen's Necklace background, stylish outfit, evening lighting, city vibe, 8k",
    "Full body shot of an Indian woman on Varanasi ghats, Ganga river background, evening aarti, traditional saree, lighting a diya, mystical atmosphere, 8k",
    "Full body portrait of a royal Rajasthani woman in desert, sand dunes background, colorful traditional outfit, dancing pose, golden hour, desert sunset, 8k",
    "Full body shot of an Indian woman in a flower garden, Manali, pretty dress, smelling flowers, natural lighting, dreamy atmosphere, 8k",
    "Full body portrait of an Indian fashion model, professional studio background, designer fusion wear, high-fashion pose, studio lighting, 8k"
]

def get_random_prompt():
    """Random Prompt Select"""
    prompt = random.choice(PROMPTS)
    print(f"🎯 Selected Style: {prompt[:80]}...")
    return prompt

# ============================================
# 🎨 DYNAMIC CAPTIONS
# ============================================

def generate_dynamic_caption():
    """फोटो के हिसाब से Unique Caption"""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        time_text = "🌅 Good Morning!"
    elif 12 <= hour < 17:
        time_text = "☀️ Afternoon glow"
    elif 17 <= hour < 21:
        time_text = "🌆 Evening elegance"
    else:
        time_text = "🌙 Night queen"
    
    titles = [
        "Exploring new places", "Wandering soul", "Travel diaries",
        "Lost in beauty", "Chasing sunsets", "Adventures calling",
        "New destination, new look", "Roaming in style", "Live your dreams"
    ]
    
    locations = [
        "🏔️ Mountains", "👑 Royal Palace", "🏖️ Beach Vibes",
        "🛕 Temple Visit", "🏜️ Desert Beauty", "🌺 Garden Paradise",
        "📸 Studio Shoot", "🏰 Historical Fort", "🌊 Lakeside",
        "🛍️ Market Walk", "🚶 Street Style", "🌊 Ocean View"
    ]
    
    hashtags_list = [
        "#IndianBeauty #AIFashion #TravelInStyle #ExploreIndia #ViralFashion #IndianWear #FashionGoals #TravelGram #AICreation #FashionAI",
        "#VirtualInfluencer #StyleInspo #RoyalLook #TraditionalWear #FusionFashion #AIArt #Photography #Portrait #FashionBlog #TravelDiaries",
        "#IncredibleIndia #CulturalFashion #OOTD #Fashionista #AIModel #DigitalFashion #ModernBride #IndianWear #FusionFashion #AIArtist"
    ]
    
    title = random.choice(titles)
    location = random.choice(locations)
    hashtags = random.choice(hashtags_list)
    
    return f"""{time_text}

✨ {title} ✨ {random.choice(['🤩', '💫', '🌟', '💃'])} 

{location} • {random.choice(['Today', 'Now', 'Finally', 'Here'])} 

📍 {random.choice(['India', 'New Destination', 'Beauty Spot'])} 

👇 Comment में बताओ:
1️⃣ ये स्टाइल कैसा लगा?
2️⃣ अगली पोस्ट कहां से होनी चाहिए?

💡 100+ Comments = Next Destination Your Choice!

{hashtags}
"""

# ============================================
# 🎨 AI से PHOTO GENERATE - FIXED
# ============================================

def generate_ai_image(filename="generated_photo.jpg", max_retries=3):
    """
    Pollinations AI से फोटो जनरेट करें - Retry के साथ
    """
    print("🎨 AI से फोटो बना रहा हूँ...")
    
    for attempt in range(max_retries):
        try:
            # Get Random Prompt
            prompt = get_random_prompt()
            clean_prompt = prompt.strip().replace('\n', ' ').replace('  ', ' ')
            encoded_prompt = urllib.parse.quote(clean_prompt[:250])
            
            # ✅ 9:16 Resolution - Full Body के लिए
            url = (
                f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                f"?width=768&height=1344"
                f"&model=flux"
                f"&nologo=true"
                f"&seed={random.randint(1, 9999999)}"
                f"&quality=high"
                f"&enhance=true"
            )
            
            print(f"⏳ Attempt {attempt + 1}/{max_retries}: 30-60 सेकंड लग सकते हैं...")
            response = session.get(url, timeout=180)
            
            if response.status_code == 200:
                content_size = len(response.content)
                print(f"📊 Image Size: {content_size/1024:.1f} KB")
                
                if content_size > 50000:  # 50KB से बड़ा
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ फोटो बन गई! ({content_size/1024:.1f} KB)")
                    enhance_image(filename)
                    return filename, prompt
                else:
                    print(f"⚠️ Image too small ({content_size/1024:.1f} KB), Retrying...")
                    time.sleep(3)
            else:
                print(f"❌ API Error: {response.status_code}, Retrying...")
                time.sleep(5)
                
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} Error: {e}")
            time.sleep(5)
    
    # All retries failed - Create placeholder
    print("⚠️ All retries failed! Creating placeholder...")
    return create_placeholder(filename), "Placeholder Image"

def create_placeholder(filename="placeholder.jpg"):
    """Placeholder Image Create"""
    try:
        from PIL import Image, ImageDraw
        
        img = Image.new('RGB', (768, 1344), color=(255, 220, 240))
        draw = ImageDraw.Draw(img)
        draw.text((200, 600), "✨ AI Beauty ✨", fill=(200, 50, 100))
        img.save(filename)
        print("✅ Placeholder Image Created!")
        return filename
    except:
        with open(filename, 'wb') as f:
            f.write(b'PLACEHOLDER_IMAGE')
        return filename

def enhance_image(image_path):
    """Image Enhancement"""
    try:
        from PIL import Image, ImageEnhance
        
        img = Image.open(image_path)
        width, height = img.size
        print(f"📐 Resolution: {width}x{height}")
        
        # Resize to 768x1344 if needed
        if width != 768 or height != 1344:
            print(f"📐 Resizing to 768x1344...")
            img = img.resize((768, 1344), Image.Resampling.LANCZOS)
        
        # Light Enhancement
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.05)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.02)
        
        img.save(image_path, quality=98, optimize=True, format='JPEG')
        print(f"✅ Image Enhanced!")
        return True
        
    except Exception as e:
        print(f"⚠️ Enhancement Error: {e}")
        return False

# ============================================
# 📤 FACEBOOK POST
# ============================================

def post_to_facebook(image_path, caption):
    """Facebook Page पर फोटो पोस्ट करें"""
    print("📤 Facebook पर पोस्ट कर रहा हूँ...")
    
    # Page ID Clean
    page_id = ''.join(filter(str.isdigit, FB_PAGE_ID))
    print(f"📌 Cleaned Page ID: {page_id}")
    
    fb_url = f"https://graph.facebook.com/{page_id}/photos"
    
    payload = {
        'caption': caption,
        'access_token': FB_ACCESS_TOKEN,
        'published': 'true'
    }
    
    try:
        with open(image_path, 'rb') as img_file:
            files = {'source': img_file}
            response = session.post(fb_url, data=payload, files=files, timeout=120)
        
        if response.status_code == 200:
            post_id = response.json().get('id')
            print(f"✅ पोस्ट हो गई! Post ID: {post_id}")
            return post_id
        else:
            print(f"❌ Facebook Error: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"⚠️ Facebook Error: {e}")
        return None

# ============================================
# 🧹 CLEANUP
# ============================================

def cleanup_files(*files):
    for file in files:
        if file and os.path.exists(file):
            try:
                os.remove(file)
                print(f"🧹 {file} डिलीट हो गया")
            except:
                pass

# ============================================
# 🚀 MAIN BOT
# ============================================

def main():
    print("\n" + "="*60)
    print("🚀 AI FASHION TRAVEL BOT START")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # STEP 1: AI से फोटो बनाएं
        print("\n🎨 STEP 1: AI से फोटो बना रहा हूँ...")
        image_path, prompt = generate_ai_image("travel_fashion_photo.jpg")
        
        if not image_path:
            print("❌ फोटो नहीं बन पाई!")
            return False
        
        # STEP 2: Caption
        print("\n📝 STEP 2: कैप्शन बना रहा हूँ...")
        caption = generate_dynamic_caption()
        print(f"✅ Caption Preview: {caption[:100]}...")
        
        # STEP 3: Facebook Post
        print("\n📤 STEP 3: Facebook पर पोस्ट कर रहा हूँ...")
        post_id = post_to_facebook(image_path, caption)
        
        # STEP 4: Cleanup
        print("\n🧹 STEP 4: क्लीनअप...")
        cleanup_files(image_path)
        
        elapsed = time.time() - start_time
        
        if post_id:
            print("\n" + "="*60)
            print("🎉 SUCCESS! पोस्ट हो गई!")
            print(f"⏱️ कुल समय: {elapsed:.2f} सेकंड")
            print(f"📱 Post ID: {post_id}")
            print("="*60)
            return True
        else:
            print("\n❌ पोस्ट नहीं हो पाई!")
            return False
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================
# 🎯 EXECUTE
# ============================================

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
