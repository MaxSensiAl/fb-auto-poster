import os
import sys
import time
import random
import requests
import urllib.parse
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from PIL import Image, ImageEnhance, ImageFilter
from google import genai  # ✅ लाइव कैप्शन के लिए SDK

# ============================================
# 🔐 GITHUB SECRETS से VARIABLES लें
# ============================================
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API")

if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
    print("❌ Facebook Credentials नहीं मिले!")
    sys.exit(1)

# ============================================
# 🌐 Session Setup
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
# 🎨 WAIST-UP STYLE PROMPTS (चेहरा साफ रखने के लिए कमर से ऊपर के शॉट्स)
# ============================================
PROMPTS = [
    "Ultra HD waist-up portrait of a stunning Indian woman standing gracefully, natural beauty, highly detailed symmetrical facial features, realistic clear eyes, glowing skin, wearing casual stylish outfit, outdoor background, natural sunlight, professional photography, hyper realistic, sharp focus on face, 8k resolution",
    "Ultra HD waist-up fashion editorial shot of a fashionable Indian woman, highly detailed symmetrical face, elegant modern fusion wear, stylish jewelry, soft natural lighting, confident pose, professional studio quality, sharp focus, hyper realistic, 8k resolution",
    "Ultra HD waist-up portrait of a beautiful Indian woman in rich traditional ethnic wear, detailed saree, beautiful gold jewelry, highly focused symmetrical face, glowing skin, warm golden hour lighting, graceful look, professional portrait, 8k resolution",
    "Ultra HD waist-up portrait of a modern Indian girl, contemporary styling, minimal makeup, natural clear skin, highly detailed realistic eyes, indoor cafe background, soft ambient lighting, candid pose, sharp focus, professional photography, 8k resolution"
]

# ============================================
# 🎨 IMAGE GENERATION
# ============================================
def generate_ultra_hd_image(filename="ultra_hd_photo.jpg", max_retries=5):
    print("🎨 [जुगाड़ तकनीक] कमर से ऊपर का क्लोज-अप शॉट जनरेट कर रहा हूँ...")
    
    for attempt in range(max_retries):
        try:
            prompt = random.choice(PROMPTS)
            enhanced_prompt = f"{prompt}, dslr camera, extremely detailed, photorealistic, cinematic lighting, sharp focus on face"
            
            clean_prompt = enhanced_prompt.strip().replace('\n', ' ').replace('  ', ' ')
            encoded_prompt = urllib.parse.quote(clean_prompt[:350])
            
            # 1024x1280 (4:5 Ratio) - फेसबुक और इंस्टाग्राम के लिए एकदम परफेक्ट
            url = (
                f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                f"?width=1024&height=1280"
                f"&model=flux"
                f"&nologo=true"
                f"&seed={random.randint(1, 9999999)}"
                f"&quality=high"
                f"&enhance=false"
            )
            
            print(f"⏳ प्रयास {attempt + 1}/{max_retries}: डाउनलोड हो रहा है...")
            response = session.get(url, timeout=120)
            
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print("✅ बेस फोटो सफलतापूर्वक प्राप्त हुई!")
                return filename, prompt
                
        except Exception as e:
            print(f"❌ प्रयास {attempt + 1} एरर: {e}")
            time.sleep(5)
            
    return None, None

# ============================================
# 🖼️ LOCAL HD ENHANCEMENT (Pillow के जरिए 2K शार्पनेस देना)
# ============================================
def enhance_image_locally(image_path):
    print("🪄 स्थानीय टूल्स (PIL) से इमेज को 2K शार्पनेस और ब्राइटनेस दे रहा हूँ...")
    try:
        img = Image.open(image_path)
        
        # 1. अनशार्प मास्क फ़िल्टर (बारीक विवरणों को निखारने के लिए)
        img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=130, threshold=2))
        
        # 2. शार्पनेस बढ़ाना
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.2)
        
        # 3. थोड़ा कॉन्ट्रास्ट बढ़ाना (रंगों को निखारने के लिए)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.04)
        
        # 4. कलर सैचुरेशन को थोड़ा सा निखारना
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.02)
        
        img.save(image_path, quality=98, optimize=True)
        print("✅ लोकल इमेज एन्हांसमेंट पूर्ण!")
    except Exception as e:
        print(f"⚠️ लोकल एनहांसमेंट में समस्या: {e}")

# ============================================
# 📝 DYNAMIC GOOGLE AI CAPTION GENERATOR
# ============================================
def generate_caption(image_prompt):
    if not GEMINI_API_KEY:
        return "✨ Unfiltered and unmatched beauty. #OOTD #Fashion"
        
    try:
        print("⏳ Antigravity Agent से लाइव कैप्शन बनवा रहा हूँ...")
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        tools = [
            {'type': 'code_execution'},
            {'type': 'google_search'}
        ]
        
        prompt_input = (
            f"Analyze this photo styling: '{image_prompt}'\n"
            f"Search Google for today's most viral Instagram hashtags and fashion writing styles in India. "
            f"Write an engaging caption, add a question for the audience to rate the look, and include 15-20 viral hashtags."
        )
        
        interaction = client.interactions.create(
            agent='antigravity-preview-05-2026',
            input=prompt_input,
            background=True,
            tools=tools,
            environment={'type': 'remote', 'network': 'disabled'},
        )
        
        attempts = 0
        while attempts < 12:
            interaction = client.interactions.get(interaction.id)
            if interaction.status == "completed":
                return interaction.output_text
            time.sleep(10)
            attempts += 1
            
    except Exception as e:
        print(f"⚠️ कैप्शन एआई एजेंट एरर: {e}")
    return "✨ Unfiltered and unmatched beauty. #OOTD #Fashion"

# ============================================
# 📤 FACEBOOK POST
# ============================================
def post_to_facebook(image_path, caption):
    print("📤 Facebook पर पोस्ट अपलोड कर रहा हूँ...")
    page_id = ''.join(filter(str.isdigit, FB_PAGE_ID))
    url = f"https://graph.facebook.com/{page_id}/photos"
    
    payload = {
        'access_token': FB_ACCESS_TOKEN,
        'caption': caption,
        'published': 'true'
    }
    
    try:
        with open(image_path, 'rb') as img:
            files = {'source': img}
            response = session.post(url, data=payload, files=files, timeout=180)
        
        if response.status_code == 200:
            post_id = response.json().get('id')
            print(f"✅ पोस्ट सफल! ID: {post_id}")
            return post_id
    except Exception as e:
        print(f"⚠️ पोस्टिंग त्रुटि: {e}")
    return None

# ============================================
# 🚀 MAIN
# ============================================
def main():
    print("\n" + "="*60)
    print("🚀 100% FREE AUTO POSTER BOT (NO PAID API REQUIRED)")
    print("="*60)
    
    start_time = time.time()
    
    # 1. फ्री जनरेशन (Waist-Up Portrait)
    image_path, prompt = generate_ultra_hd_image()
    if not image_path:
        print("❌ इमेज जनरेट नहीं हो सकी!")
        return False
    
    # 2. लोकल एनहांसमेंट (Pillow के जरिए)
    enhance_image_locally(image_path)
    
    # 3. लाइव कैप्शन बनाना
    caption = generate_caption(prompt)
    
    # 4. फेसबुक पर पोस्ट करना
    post_id = post_to_facebook(image_path, caption)
    
    if os.path.exists(image_path):
        os.remove(image_path)
        print("🧹 Cleanup Done")
        
    print(f"⏱️ कुल समय: {time.time() - start_time:.1f}s")
    return True if post_id else False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
