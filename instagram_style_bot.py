import os
import sys
import random
import logging
import requests
from instagrapi import Client

# ============================================
# 📝 लॉगिंग सेटअप
# ============================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================
# 🔐 गिटहब सीक्रेट्स से वेरिएबल्स प्राप्त करना
# ============================================
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
TARGET_PROFILE = os.environ.get("TARGET_PROFILE", "zaraso_phia")  # जिस प्रोफाइल से वीडियो लेना है
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

if not IG_USERNAME or not IG_PASSWORD:
    logger.critical("❌ इंस्टाग्राम लॉग-इन क्रेडेंशियल्स गायब हैं!")
    sys.exit(1)

# ============================================
# 📸 इंस्टाग्राम लॉगिन और वीडियो डाउनलोड प्रक्रिया
# ============================================
def download_trending_reel():
    cl = Client()
    
    try:
        logger.info("⏳ इंस्टाग्राम पर लॉग-इन कर रहा हूँ...")
        cl.login(IG_USERNAME, IG_PASSWORD)
        logger.info("✅ लॉग-इन सफल!")
        
        # लक्षित प्रोफ़ाइल (Target Profile) की आईडी प्राप्त करना
        logger.info(f"🔍 @{TARGET_PROFILE} की रील्स खोज रहा हूँ...")
        user_id = cl.user_id_from_username(TARGET_PROFILE)
        
        # यूजर के हालिया रील्स/वीडियो प्राप्त करना
        user_medias = cl.user_medias(user_id, amount=10)
        
        # केवल वीडियो (रील्स) को फ़िल्टर करना
        video_medias = [m for m in user_medias if m.media_type == 1 or m.media_type == 2]
        
        if not video_medias:
            logger.warning("⚠️ कोई वीडियो या रील नहीं मिली।")
            return None
            
        # किसी एक रील को चुनना (उदाहरण के लिए सबसे ताज़ा या रैंडम)
        selected_media = random.choice(video_medias)
        logger.info(f"🎥 चुनी गई रील आईडी: {selected_media.pk}")
        
        # वीडियो डाउनलोड करना (instagrapi सीधे इसे सुरक्षित डाउनलोड करती है)
        video_path = cl.video_download(selected_media.pk, folder=".")
        logger.info(f"✅ वीडियो डाउनलोड हो गया: {video_path}")
        return video_path

    except Exception as e:
        logger.error(f"❌ इंस्टाग्राम ऑटोमेशन के दौरान त्रुटि: {e}")
        return None

# ============================================
# 📝 टाइटल और हैशटैग जनरेटर
# ============================================
def generate_metadata():
    captions = [
        "🔥 Trending Vibes! Rate this video from 1-10 👇\n\n#TrendingReels #ViralVideo #ExplorePage #InstaDaily #FYP",
        "Unmatched energy! 🤩 Share this with your friends!\n\n#Viral #ReelsInstagram #TrendingNow #DailyInspo #FYP",
        "This is currently taking over the internet! 📈💥\n\n#ViralPost #Trending #InstagramReels #Feature #FYP"
    ]
    return random.choice(captions)

# ============================================
# 📤 फेसबुक पर अपलोड प्रक्रिया
# ============================================
def upload_to_facebook(video_path, caption):
    logger.info("📤 फेसबुक पेज पर वीडियो अपलोड कर रहा हूँ...")
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/videos"
    
    payload = {
        'description': caption,
        'access_token': FB_ACCESS_TOKEN
    }
    
    try:
        with open(video_path, 'rb') as f:
            files = {'source': f}
            response = requests.post(url, data=payload, files=files, timeout=300)
            
        if response.status_code == 200:
            logger.info(f"🎉 सफलतापूर्वक पोस्ट हो गया! Post ID: {response.json().get('id')}")
            return True
        else:
            logger.error(f"❌ फेसबुक पोस्टिंग विफल: {response.text}")
    except Exception as e:
        logger.error(f"⚠️ पोस्टिंग के दौरान समस्या आई: {e}")
    return False

# ============================================
# 🚀 रनर फंक्शन
# ============================================
def main():
    # 1. इंस्टाग्राम से वीडियो डाउनलोड करें
    downloaded_file = download_trending_reel()
    
    if downloaded_file and os.path.exists(downloaded_file):
        # 2. कैप्शन जनरेट करें
        caption = generate_metadata()
        
        # 3. फेसबुक पर अपलोड करें
        success = upload_to_facebook(downloaded_file, caption)
        
        # 4. क्लीनअप (डाउनलोड की गई फाइल को हटाना)
        try:
            os.remove(downloaded_file)
            logger.info("🧹 अस्थायी वीडियो फ़ाइल हटा दी गई है।")
        except Exception as e:
            logger.warning(f"⚠️ फ़ाइल हटाने में विफल: {e}")
            
        if success:
            sys.exit(0)
    
    sys.exit(1)

if __name__ == "__main__":
    main()
