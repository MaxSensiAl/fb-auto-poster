import os
import sys
import time
import random
import requests
import urllib.parse
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# ============================================
# 🔐 GITHUB SECRETS से VARIABLES लें
# ============================================
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

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
# 🎨 20+ UNIQUE PROMPTS - अलग-अलग स्टाइल, अलग-अलग बैकग्राउंड
# ============================================

PROMPTS = [
    # 1. पहाड़ों पर घूमना
    """
    Full body shot of a beautiful Indian woman standing in Himalayan mountains.
    She is wearing a colorful traditional pheran, enjoying the snowfall.
    Snow-capped peaks in background, clear blue sky, winter wonderland.
    Natural lighting, sharp focus on face and outfit.
    8k resolution, photorealistic, professional photography.
    """,
    
    # 2. राजस्थानी महल
    """
    Full body portrait of a stunning Indian woman in traditional Rajasthani attire.
    Standing in front of a grand palace, intricate architecture visible.
    Yellow sandstone palace, clear sky, royal vibe.
    She is wearing a colorful lehenga and heavy silver jewelry.
    Golden hour lighting, majestic background.
    """,
    
    # 3. गोवा बीच
    """
    Full body shot of a beautiful Indian woman on Goa beach.
    She is wearing a breezy summer dress, hair flowing in the wind.
    White sand beach, blue ocean, palm trees in background.
    Sunset lighting, dreamy and romantic atmosphere.
    Professional photography, sharp focus.
    """,
    
    # 4. दिल्ली के किले
    """
    Full body portrait of an Indian woman in modern fusion wear.
    Standing in front of Red Fort, Delhi, historical architecture.
    Evening lighting, city vibe, cultural heritage.
    She is wearing a stylish ethnic dress, confident pose.
    Professional photography, sharp details.
    """,
    
    # 5. केरल बैकवाटर्स
    """
    Full body shot of a South Indian woman in traditional saree.
    Standing on a houseboat in Kerala backwaters.
    Green palm trees, calm water, houseboat background.
    She is wearing a beautiful kasavu saree, holding a coconut.
    Natural lighting, serene and peaceful atmosphere.
    """,
    
    # 6. जयपुर का बाजार
    """
    Full body portrait of an Indian woman in colorful attire.
    Walking in Jaipur's famous bazaar, pink city buildings background.
    She is wearing a bright lehenga, shopping bags in hand.
    Vibrant market atmosphere, warm lighting.
    Candid street photography style.
    """,
    
    # 7. हरिद्वार आरती
    """
    Full body shot of an Indian woman on Haridwar ghats.
    Evening aarti background, diyas and lights floating.
    She is wearing a traditional saree, holding a diya.
    Spiritual atmosphere, warm golden lighting.
    Professional photography, emotional and serene.
    """,
    
    # 8. उदयपुर की झील
    """
    Full body portrait of a woman in elegant fusion wear.
    Standing by Lake Pichola, Udaipur, lake palace visible.
    She is wearing a flowing dress, hair blowing in the wind.
    Sunset lighting, romantic and dreamy vibe.
    Professional photography, sharp focus.
    """,
    
    # 9. कोलकाता की सड़कें
    """
    Full body shot of a Bengali woman in traditional saree.
    Walking in Kolkata's streets, yellow taxi background.
    She is wearing a white saree with red border, flowers in hair.
    City vibe, cultural atmosphere.
    Street photography style, natural lighting.
    """,
    
    # 10. मैसूर पैलेस
    """
    Full body portrait of a South Indian woman in silk saree.
    Standing in front of Mysore Palace, illuminated at night.
    She is wearing a rich kanjivaram saree, temple jewelry.
    Night photography, palace lights in background.
    Professional photography, dramatic lighting.
    """,
    
    # 11. लद्दाख रोड ट्रिप
    """
    Full body shot of an Indian woman on Ladakh road trip.
    Standing near a jeep, mountains in background.
    She is wearing a winter jacket and sunglasses.
    Rugged landscape, clear blue sky.
    Travel photography style, adventure vibe.
    """,
    
    # 12. वृंदावन के मंदिर
    """
    Full body portrait of a woman in traditional attire.
    Standing in front of a temple in Vrindavan.
    Temple architecture, spiritual atmosphere.
    She is wearing a colorful saree, holding flowers.
    Natural lighting, peaceful vibe.
    """,
    
    # 13. अमेरिका का भवन
    """
    Full body shot of an Indian woman in modern fusion wear.
    Standing in front of iconic architecture, city background.
    She is wearing a contemporary outfit, urban vibe.
    Professional photography, clear sky.
    Modern, stylish, confident look.
    """,
    
    # 14. रामेश्वरम समुद्र
    """
    Full body portrait of a woman on Rameshwaram beach.
    Ocean background, blue water, clear sky.
    She is wearing a flowing summer dress, hair blowing.
    Natural lighting, peaceful beach atmosphere.
    Professional photography, sharp focus.
    """,
    
    # 15. अजंता गुफाएं
    """
    Full body shot of an Indian woman near ancient caves.
    Ajanta caves background, historical architecture.
    She is wearing traditional attire, spiritual vibe.
    Natural lighting, cultural atmosphere.
    Professional photography, historical setting.
    """,
    
    # 16. शिमला मॉल रोड
    """
    Full body portrait of a woman on Mall Road, Shimla.
    Snow-capped mountains background, colonial architecture.
    She is wearing a winter outfit, enjoying the snow.
    Beautiful winter lighting, cozy atmosphere.
    Professional photography, sharp focus.
    """,
    
    # 17. अमृतसर स्वर्ण मंदिर
    """
    Full body shot of a Sikh woman at Golden Temple, Amritsar.
    Golden temple background, sarovar (holy water) visible.
    She is wearing a beautiful salwar kameez.
    Spiritual atmosphere, warm lighting.
    Professional photography, peaceful vibe.
    """,
    
    # 18. मुंबई मरीन ड्राइव
    """
    Full body portrait of a modern Indian woman on Marine Drive.
    Queen's Necklace background, Mumbai skyline.
    She is wearing a stylish outfit, sea breeze blowing hair.
    Evening lighting, city vibe.
    Professional photography, glamorous look.
    """,
    
    # 19. काशी घाट
    """
    Full body shot of an Indian woman on Varanasi ghats.
    Ganga river background, evening aarti atmosphere.
    She is wearing a traditional saree, lighting a diya.
    Spiritual, mystical atmosphere.
    Professional photography, warm lighting.
    """,
    
    # 20. राजस्थानी थार रेगिस्तान
    """
    Full body portrait of a royal Rajasthani woman in desert.
    Sand dunes background, camels visible in distance.
    She is wearing colorful traditional outfit, dancing pose.
    Golden hour lighting, majestic desert sunset.
    Professional photography, sharp focus.
    """,
    
    # 21. हिल स्टेशन बागवानी
    """
    Full body shot of an Indian woman in a flower garden.
    Manali or Kashmir flower garden background.
    She is wearing a pretty dress, smelling flowers.
    Natural lighting, colorful and vibrant.
    Professional photography, dreamy atmosphere.
    """,
    
    # 22. स्टूडियो फैशन शूट
    """
    Full body portrait of an Indian fashion model.
    Professional studio background, dramatic lighting.
    She is wearing designer fusion wear, high-fashion pose.
    Studio lighting, sharp focus, glamorous.
    Professional fashion photography style.
    """
]

def get_random_prompt():
    """
    अलग-अलग स्टाइल और बैकग्राउंड के लिए Random Prompt
    """
    prompt = random.choice(PROMPTS)
    print(f"🎯 Selected Location/Style: {prompt[:80]}...")
    return prompt

# ============================================
# 🎨 DYNAMIC CAPTIONS - फोटो के हिसाब से
# ============================================

def generate_dynamic_caption(prompt_text):
    """
    फोटो के स्टाइल के हिसाब से Caption Generate करें
    """
    hour = datetime.now().hour
    if 6 <= hour < 12:
        time_text = "🌅 Good Morning!"
    elif 12 <= hour < 17:
        time_text = "☀️ Afternoon glow"
    elif 17 <= hour < 21:
        time_text = "🌆 Evening elegance"
    else:
        time_text = "🌙 Night queen"
    
    # फोटो के हिसाब से Locale Extract करें
    locations = {
        "mountain": "🏔️ Mountains",
        "palace": "👑 Royal Palace",
        "beach": "🏖️ Beach Vibes",
        "temple": "🛕 Temple Visit",
        "desert": "🏜️ Desert Beauty",
        "garden": "🌺 Garden Paradise",
        "studio": "📸 Studio Shoot",
        "fort": "🏰 Historical Fort",
        "lake": "🌊 Lakeside",
        "market": "🛍️ Market Walk",
        "street": "🚶 Street Style",
        "ocean": "🌊 Ocean View"
    }
    
    # Random Location Tag
    location_tag = random.choice(list(locations.values()))
    
    # Random Hashtags
    hashtags = [
        "#IndianBeauty #AIFashion #TravelInStyle #ExploreIndia",
        "#ViralFashion #IndianWear #FashionGoals #TravelGram",
        "#AICreation #FashionAI #VirtualInfluencer #StyleInspo",
        "#RoyalLook #TraditionalWear #FusionFashion #AIArt",
        "#Photography #Portrait #FashionBlog #TravelDiaries",
        "#IncredibleIndia #CulturalFashion #OOTD #Fashionista"
    ]
    
    title_options = [
        f"Explore more with ✨",
        f"Roaming in style 💃",
        f"Wandering soul 🌍",
        f"New destination, new look 🌟",
        f"Travel diaries 📸",
        f"Wandering through beauty 🦋",
        f"Live your dreams ✨",
        f"Lost in beauty 🌸",
        f"Chasing sunsets 🌅",
        f"Adventures calling 🌍"
    ]
    
    title = random.choice(title_options)
    
    captions = [
        f"""{time_text}

{title} {random.choice(['🤩', '✨', '💫', '🌟', '💃'])} 

{location_tag} • {random.choice(['Today', 'Now', 'Finally', 'Here'])} 

📍 {random.choice(['India', 'New Destination', 'Beauty Spot'])} 

👇 Comment में बताओ:
1️⃣ ये स्टाइल कैसा लगा?
2️⃣ अगली पोस्ट कहां से होनी चाहिए?

💡 100+ Comments = Next Destination Your Choice!

{random.choice(hashtags)}
{random.choice(hashtags)}
""",
        
        f"""{time_text}

{random.choice(['Stunning', 'Beautiful', 'Gorgeous', 'Absolutely Amazing'])} vibes! 💫

{location_tag} • {random.choice(['Exploring', 'Chilling', 'Enjoying', 'Living'])} the moment

📍 {random.choice(['Incredible India', 'Travel Mode ON', 'Paradise Found'])} 

👇 3 Second mein comment karo:
1️⃣ कितने नंबर देते हो? (1-10)
2️⃣ किस देश का लग रहा हूँ?

{random.choice(hashtags)}
{random.choice(hashtags)}
""",
        
        f"""{time_text}

✨ {title} ✨

{location_tag} vibes 💯
{random.choice(['Nature lover', 'Culture explorer', 'Wanderlust', 'Soul traveler'])} 

📍 {random.choice(['Somewhere in India', 'Heaven on Earth', 'Dream Destination'])} 

👇 Comment में बताओ:
❤️ - पसंद आया
💔 - नहीं पसंद
🔥 - और देखना चाहते हो?

{random.choice(hashtags)}
{random.choice(hashtags)}
"""
    ]
    
    return random.choice(captions)

# ============================================
# 🎨 AI से PHOTO GENERATE करें
# ============================================

def generate_ai_image(filename="generated_photo.jpg"):
    """
    Pollinations AI से फोटो जनरेट करें
    """
    print("🎨 AI से फोटो बना रहा हूँ...")
    
    # Get Random Prompt (अलग-अलग स्टाइल और बैकग्राउंड)
    prompt = get_random_prompt()
    clean_prompt = prompt.strip().replace('\n', ' ').replace('  ', ' ')
    encoded_prompt = urllib.parse.quote(clean_prompt[:250])
    
    # ✅ 9:16 Resolution - Full Body के लिए
    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=768&height=1344"  # ✅ आपके साइज के हिसाब से
        f"&model=flux"
        f"&nologo=true"
        f"&seed={random.randint(1, 9999999)}"
        f"&quality=high"
        f"&enhance=true"
    )
    
    try:
        print("⏳ 30-60 सेकंड लग सकते हैं...")
        response = session.get(url, timeout=180)
        
        if response.status_code == 200:
            content_size = len(response.content)
            if content_size > 50000:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ फोटो बन गई! ({content_size/1024:.1f} KB)")
                
                # Enhance Image
                enhance_image(filename)
                return filename, prompt
            else:
                print(f"⚠️ फोटो बहुत छोटी है ({content_size} bytes)")
                return None, None
        else:
            print(f"❌ AI Error: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return None, None

def enhance_image(image_path):
    """
    Image Enhancement - Natural Look
    """
    try:
        from PIL import Image, ImageEnhance
        
        img = Image.open(image_path)
        width, height = img.size
        print(f"📐 Resolution: {width}x{height}")
        
        # 9:16 Ratio Maintain
        if width != 768 or height != 1344:
            print(f"📐 Resizing to 768x1344...")
            img = img.resize((768, 1344), Image.Resampling.LANCZOS)
        
        # हल्की Sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.05)
        
        # हल्का Contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.02)
        
        # High Quality Save
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
    """
    Facebook Page पर फोटो पोस्ट करें
    """
    print("📤 Facebook पर पोस्ट कर रहा हूँ...")
    
    # Page ID Clean करें
    page_id = ''.join(filter(str.isdigit, FB_PAGE_ID))
    print(f"📌 Cleaned Page ID: {page_id}")
    
    fb_url = f"https://graph.facebook.com/{page_id}/photos"
    
    payload = {
        'caption': caption,
        'access_token': FB_ACCESS_TOKEN,
        'published': 'true'
    }
    
    try:
        if not os.path.exists(image_path) or os.path.getsize(image_path) < 100:
            print("❌ फोटो फ़ाइल इनवैलिड है!")
            return None
        
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
        image_path, prompt_text = generate_ai_image("travel_fashion_photo.jpg")
        
        if not image_path:
            print("❌ फोटो नहीं बन पाई!")
            return False
        
        # STEP 2: फोटो के हिसाब से कैप्शन बनाएं
        print("\n📝 STEP 2: Dynamic कैप्शन बना रहा हूँ...")
        caption = generate_dynamic_caption(prompt_text)
        print(f"✅ Caption Preview: {caption[:100]}...")
        
        # STEP 3: Facebook पर पोस्ट करें
        print("\n📤 STEP 3: Facebook पर पोस्ट कर रहा हूँ...")
        post_id = post_to_facebook(image_path, caption)
        
        # STEP 4: क्लीनअप
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
