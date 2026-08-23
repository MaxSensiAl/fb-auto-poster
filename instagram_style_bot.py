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
import replicate  # ✅ चेहरा साफ करने के लिए SDK
from google import genai  # ✅ लाइव कैप्शन के लिए SDK

# ============================================
# 🔐 GITHUB SECRETS से VARIABLES लें
# ============================================
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")

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
# 🎨 ZARASO_PHIA STYLE PROMPTS
# ============================================
PROMPTS = [
    "Ultra HD full body portrait of a stunning Indian woman, natural beauty, glowing skin, wearing casual stylish outfit, city background, natural sunlight, candid pose, professional photography, hyper realistic, sharp focus on face, 8k resolution",
    "Ultra HD full body fashion shot of a fashionable Indian woman, wearing trendy fusion outfit, urban background, street style photography, confident pose, natural lighting, sharp focus on face, hyper realistic, 8k resolution",
    "Ultra HD full body portrait of an Indian woman in beautiful ethnic outfit, traditional jewelry, cultural background, warm golden lighting, graceful pose, natural beauty, sharp focus on face, hyper realistic, 8k resolution",
    "Ultra HD full body portrait of a beautiful Indian woman in casual look, simple yet stylish outfit, natural makeup, glowing skin, outdoor background, natural sunlight, candid smile, professional photography, hyper realistic, sharp focus on face, 8k resolution"
]

# ============================================
# ☁️ इमेज को टेम्परेरी क्लाउड पर अपलोड करना (Replicate के लिए आवश्यक)
# ============================================
def upload_to_temporary_cloud(image_path):
    print("⏳ फोटो को प्रोसेसिंग के लिए क्लाउड पर अपलोड कर रहा हूँ...")
    try:
        with open(image_path, 'rb') as f:
            response = session.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            file_url = data.get("data", {}).get("url")
            direct_url = file_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
            return direct_url
    except Exception as e:
        print(f"⚠️ अपलोड विफल रहा: {e}")
    return None

# ============================================
# 🎭 चेहरे को साफ करना (GFPGAN Face Restore - FIXED VERSION)
# ============================================
def restore_face_gfpgan(image_path):
    if not REPLICATE_API_TOKEN:
        print("⚠️ REPLICATE_API_TOKEN नहीं मिला! फेस रिस्टोरेशन स्किप कर रहा हूँ।")
        return False
        
    cloud_url = upload_to_temporary_cloud(image_path)
    if not cloud_url:
        print("⚠️ क्लाउड अपलोड फेल हुआ, फेस रिस्टोर नहीं हो सका।")
        return False
        
    print("🚀 GFPGAN v1.4 द्वारा चेहरे को बिल्कुल साफ और शार्प (Sharp) कर रहा हूँ...")
    try:
        client = replicate.Client(api_token=REPLICATE_API_TOKEN)
        
        # ✅ 'tencentarc/gfpgan' का सटीक और स्थिर वर्जन हैश
        output = client.run(
            "tencentarc/gfpgan:9a42a3511d0de2e9b4ab1c0af640f302b5064857453dbe6f62e219ef9243728f",
            input={
                "img": cloud_url,
                "scale": 2,
                "version": "v1.4"
            }
        )
        
        if output:
            result_url = output[0] if isinstance(output, list) else output
            img_resp = session.get(result_url, timeout=60)
            if img_resp.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(img_resp.content)
                print("🎉 सफलता! बिगड़ा हुआ चेहरा पूरी तरह ठीक हो गया है!")
                return True
    except Exception as e:
        print(f"❌ GFPGAN एरर: {e}")
    return False

# ============================================
# 🎨 IMAGE GENERATION
# ============================================
def generate_ultra_hd_image(filename="ultra_hd_photo.jpg", max_retries=5):
    print("🎨 AI फोटो जनरेट कर रहा हूँ...")
    
    for attempt in range(max_retries):
        try:
            prompt = random.choice(PROMPTS)
            enhanced_prompt = f"{prompt}, professional photography, highly detailed symmetrical face, clear eyes, cinematic lighting"
            
            clean_prompt = enhanced_prompt.strip().replace('\n', ' ').replace('  ', ' ')
            encoded_prompt = urllib.parse.quote(clean_prompt[:350])
            
            # साइज 1024x1280 (4:5 Ratio)
            url = (
                f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                f"?width=1024&height=1280"
                f"&model=flux"
                f"&nologo=true"
                f"&seed={random.randint(1, 9999999)}"
                f"&quality=high"
                f"&enhance=false"
            )
            
            print(f"⏳ प्रयास {attempt + 1}/{max_retries}: जनरेट हो रहा है...")
            response = session.get(url, timeout=120)
            
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print("✅ बेस फोटो डाउनलोड हो गई!")
                return filename, prompt
                
        except Exception as e:
            print(f"❌ प्रयास {attempt + 1} एरर: {e}")
            time.sleep(5)
            
    return None, None

# ============================================
# 🖼️ PIL इमेज को और बेहतर बनाना
# ============================================
def polish_image(image_path):
    try:
        img = Image.open(image_path)
        img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=2))
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.05)
        img.save(image_path, quality=95, optimize=True)
        print("✅ फोटो पॉलिशिंग पूर्ण!")
    except Exception as e:
        print(f"⚠️ पॉलिशिंग एरर: {e}")

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
    print("🚀 ZARASO_PHIA STYLE BOT WITH FIXED GFPGAN FACE RESTORE")
    print("="*60)
    
    start_time = time.time()
    
    image_path, prompt = generate_ultra_hd_image()
    if not image_path:
        print("❌ इमेज जनरेट नहीं हो सकी!")
        return False
        
    # 🎭 चेहरे को साफ़ करने का सुधारा गया कदम
    restore_face_gfpgan(image_path)
    
    # 🖼️ अंतिम टच (शार्पनेस और कॉन्ट्रास्ट)
    polish_image(image_path)
    
    # 📝 लाइव कैप्शन बनाना
    caption = generate_caption(prompt)
    
    # 📤 पोस्ट करना
    post_id = post_to_facebook(image_path, caption)
    
    if os.path.exists(image_path):
        os.remove(image_path)
        print("🧹 Cleanup Done")
        
    print(f"⏱️ कुल समय: {time.time() - start_time:.1f}s")
    return True if post_id else False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
