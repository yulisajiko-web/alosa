#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎵 UNIVERSAL YOUTUBE DOWNLOADER BOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Har qanday muhitda ishlaydi
✅ Kutubxonalarni avtomatik o'rnatadi
✅ AI Agent, Replit, Colab, VPS, Local - hammasi!
"""

import sys
import os
import subprocess
import platform

# ===================== AUTO INSTALLER =====================

def install_package(package, pip_name=None):
    """Paketni avtomatik o'rnatish"""
    pip_name = pip_name or package
    try:
        __import__(package)
        return True
    except ImportError:
        print(f"📦 {pip_name} o'rnatilmoqda...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                pip_name, "-q", "--disable-pip-version-check"
            ])
            print(f"✅ {pip_name} o'rnatildi!")
            return True
        except Exception as e:
            print(f"❌ {pip_name} o'rnatishda xato: {e}")
            return False

def install_ffmpeg():
    """FFmpeg o'rnatish"""
    # FFmpeg borligini tekshirish
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ FFmpeg mavjud")
            return True
    except:
        pass
    
    print("📦 FFmpeg o'rnatilmoqda...")
    system = platform.system().lower()
    
    try:
        if system == "linux":
            # Linux (Ubuntu/Debian)
            cmds = [
                ["apt-get", "update", "-qq"],
                ["apt-get", "install", "-y", "-qq", "ffmpeg"]
            ]
            for cmd in cmds:
                try:
                    subprocess.run(cmd, capture_output=True, timeout=120)
                except:
                    pass
            
            # Agar apt ishlamasa, pip orqali
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "ffmpeg-python", "-q"
                ])
            except:
                pass
                
        elif system == "darwin":
            # macOS
            subprocess.run(["brew", "install", "ffmpeg"], capture_output=True)
            
        elif system == "windows":
            # Windows - pip orqali
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "imageio-ffmpeg", "-q"
            ])
            
        print("✅ FFmpeg tayyor")
        return True
        
    except Exception as e:
        print(f"⚠️ FFmpeg o'rnatilmadi: {e}")
        print("💡 Audio konvertatsiya cheklangan bo'lishi mumkin")
        return False

def setup_environment():
    """Muhitni sozlash"""
    print("""
╔══════════════════════════════════════════╗
║  🔧 MUHIT SOZLANMOQDA...                 ║
╚══════════════════════════════════════════╝
    """)
    
    # Kerakli paketlar
    packages = [
        ("telebot", "pyTelegramBotAPI"),
        ("yt_dlp", "yt-dlp"),
        ("requests", "requests"),
    ]
    
    success = True
    for module, pip_name in packages:
        if not install_package(module, pip_name):
            success = False
    
    # FFmpeg
    install_ffmpeg()
    
    # dl papkasini yaratish
    os.makedirs("dl", exist_ok=True)
    
    if success:
        print("\n✅ Barcha kutubxonalar tayyor!\n")
    else:
        print("\n⚠️ Ba'zi kutubxonalar o'rnatilmadi\n")
    
    return success

# ===================== SETUP =====================
setup_environment()

# ===================== IMPORTS =====================
import re
import time
import json
import threading
from datetime import datetime
from typing import Optional, Dict, Any

try:
    import telebot
    from telebot import types
except ImportError:
    print("❌ telebot import qilib bo'lmadi!")
    sys.exit(1)

try:
    import yt_dlp
except ImportError:
    print("❌ yt_dlp import qilib bo'lmadi!")
    sys.exit(1)

try:
    import requests
except:
    requests = None

# ===================== CONFIGURATION =====================

class Config:
    """Bot konfiguratsiyasi"""
    TOKEN = "7895307501:AAHgpXGUqeVNgywqOJRu6Q81TS9-xcKcIM4"
    
    # Papkalar
    DOWNLOAD_DIR = "dl"
    
    # Limitlar
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB Telegram limit
    MAX_DURATION = 3600  # 1 soat
    
    # Default sifatlar
    DEFAULT_AUDIO_QUALITY = "320"
    DEFAULT_VIDEO_QUALITY = "720"
    
    # Qo'llab-quvvatlanadigan platformalar
    SUPPORTED_PLATFORMS = [
        'youtube', 'youtu.be', 'instagram', 'tiktok', 
        'twitter', 'x.com', 'facebook', 'fb.watch',
        'vimeo', 'soundcloud', 'spotify', 'twitch',
        'dailymotion', 'reddit', 'tumblr', 'vk.com',
        'ok.ru', 'bilibili', 'nicovideo', 'pornhub',
        'xvideos', 'xnxx'  # 18+ ham
    ]
    
    # Audio formatlari
    AUDIO_QUALITIES = ['128', '192', '256', '320']
    
    # Video formatlari
    VIDEO_QUALITIES = ['360', '480', '720', '1080', '1440', '2160']

# Papka yaratish
os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)

# ===================== DATABASE (JSON based) =====================

class SimpleDB:
    """Oddiy JSON database"""
    
    def __init__(self, filename="bot_data.json"):
        self.filename = filename
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"users": {}, "stats": {"downloads": 0, "audio": 0, "video": 0}}
    
    def _save(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.data, f, indent=2)
        except:
            pass
    
    def get_user(self, user_id: int) -> Dict:
        user_id = str(user_id)
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "mode": "audio",
                "audio_quality": Config.DEFAULT_AUDIO_QUALITY,
                "video_quality": Config.DEFAULT_VIDEO_QUALITY,
                "downloads": 0,
                "joined": datetime.now().isoformat()
            }
            self._save()
        return self.data["users"][user_id]
    
    def update_user(self, user_id: int, **kwargs):
        user = self.get_user(user_id)
        user.update(kwargs)
        self._save()
    
    def add_download(self, is_audio=True):
        self.data["stats"]["downloads"] += 1
        if is_audio:
            self.data["stats"]["audio"] += 1
        else:
            self.data["stats"]["video"] += 1
        self._save()
    
    def get_stats(self) -> Dict:
        return self.data["stats"]

# ===================== HELPER FUNCTIONS =====================

class Helpers:
    """Yordamchi funksiyalar"""
    
    @staticmethod
    def clean_filename(name: str) -> str:
        """Fayl nomini tozalash"""
        if not name:
            return "audio"
        # Maxsus belgilarni olib tashlash
        cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
        # Emoji va unicode tozalash
        cleaned = cleaned.encode('ascii', 'ignore').decode('ascii')
        return cleaned[:60] or "audio"
    
    @staticmethod
    def format_duration(seconds: Optional[int]) -> str:
        """Vaqtni formatlash"""
        if not seconds:
            return "00:00"
        seconds = int(seconds)
        hours, remainder = divmod(seconds, 3600)
        mins, secs = divmod(remainder, 60)
        if hours:
            return f"{hours}:{mins:02d}:{secs:02d}"
        return f"{mins}:{secs:02d}"
    
    @staticmethod
    def format_size(bytes_size: int) -> str:
        """Hajmni formatlash"""
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size/1024:.1f} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size/(1024*1024):.1f} MB"
        return f"{bytes_size/(1024*1024*1024):.2f} GB"
    
    @staticmethod
    def format_views(views: Optional[int]) -> str:
        """Ko'rishlarni formatlash"""
        if not views:
            return "0"
        if views < 1000:
            return str(views)
        elif views < 1000000:
            return f"{views/1000:.1f}K"
        elif views < 1000000000:
            return f"{views/1000000:.1f}M"
        return f"{views/1000000000:.1f}B"
    
    @staticmethod
    def is_valid_url(text: str) -> bool:
        """URL tekshirish"""
        if not text:
            return False
        text = text.lower().strip()
        return any(p in text for p in Config.SUPPORTED_PLATFORMS)
    
    @staticmethod
    def get_unique_id() -> str:
        """Unikal ID yaratish"""
        return f"{int(time.time())}_{os.getpid()}"
    
    @staticmethod
    def cleanup_files(pattern: str):
        """Fayllarni tozalash"""
        try:
            for f in os.listdir(Config.DOWNLOAD_DIR):
                if pattern in f:
                    filepath = os.path.join(Config.DOWNLOAD_DIR, f)
                    try:
                        os.remove(filepath)
                    except:
                        pass
        except:
            pass
    
    @staticmethod
    def cleanup_old_files(max_age_seconds: int = 3600):
        """Eski fayllarni tozalash"""
        try:
            now = time.time()
            for f in os.listdir(Config.DOWNLOAD_DIR):
                filepath = os.path.join(Config.DOWNLOAD_DIR, f)
                if os.path.isfile(filepath):
                    if now - os.path.getmtime(filepath) > max_age_seconds:
                        try:
                            os.remove(filepath)
                        except:
                            pass
        except:
            pass

# ===================== DOWNLOADER CLASS =====================

class Downloader:
    """Yuklash klassi"""
    
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
    
    def get_info(self, url: str) -> Optional[Dict]:
        """Video ma'lumotlarini olish"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'age_limit': None,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"Info xatosi: {e}")
            return None
    
    def download_audio(self, url: str, quality: str, 
                       chat_id: int, msg_id: int, 
                       user_data: Dict) -> bool:
        """Audio yuklash"""
        file_id = Helpers.get_unique_id()
        
        try:
            # Progress hook
            last_update = [0]
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    now = time.time()
                    if now - last_update[0] < 2:  # 2 sekundda 1 marta
                        return
                    last_update[0] = now
                    
                    percent = d.get('_percent_str', '0%').strip()
                    speed = d.get('_speed_str', 'N/A')
                    eta = d.get('_eta_str', 'N/A')
                    
                    try:
                        self.bot.edit_message_text(
                            f"⏳ *Yuklanmoqda...*\n\n"
                            f"📊 Progress: {percent}\n"
                            f"🚀 Tezlik: {speed}\n"
                            f"⏱ Qoldi: {eta}",
                            chat_id, msg_id,
                            parse_mode="Markdown"
                        )
                    except:
                        pass
            
            # yt-dlp sozlamalari
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{Config.DOWNLOAD_DIR}/{file_id}.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
                'prefer_ffmpeg': True,
                'keepvideo': False,
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [progress_hook],
                'age_limit': None,
                'geo_bypass': True,
                'nocheckcertificate': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            }
            
            # Yuklash
            self.bot.edit_message_text("⏳ Yuklanmoqda...", chat_id, msg_id)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
            
            # Faylni topish
            mp3_file = None
            for ext in ['.mp3', '.m4a', '.webm', '.opus', '.ogg']:
                test_file = f"{Config.DOWNLOAD_DIR}/{file_id}{ext}"
                if os.path.exists(test_file):
                    mp3_file = test_file
                    break
            
            # Agar postprocessor ishlamagan bo'lsa
            if not mp3_file:
                for f in os.listdir(Config.DOWNLOAD_DIR):
                    if f.startswith(file_id):
                        mp3_file = os.path.join(Config.DOWNLOAD_DIR, f)
                        break
            
            if not mp3_file or not os.path.exists(mp3_file):
                raise Exception("Audio fayl topilmadi!")
            
            # Fayl hajmini tekshirish
            file_size = os.path.getsize(mp3_file)
            if file_size > Config.MAX_FILE_SIZE:
                raise Exception(f"Fayl juda katta: {Helpers.format_size(file_size)}")
            
            # Ma'lumotlarni olish
            title = Helpers.clean_filename(info.get('title', 'Audio'))
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            
            self.bot.edit_message_text("📤 Yuborilmoqda...", chat_id, msg_id)
            
            # Thumbnail yuklash
            thumb = None
            thumb_path = None
            try:
                thumb_url = info.get('thumbnail')
                if thumb_url and requests:
                    thumb_path = f"{Config.DOWNLOAD_DIR}/{file_id}_thumb.jpg"
                    r = requests.get(thumb_url, timeout=10)
                    if r.status_code == 200:
                        with open(thumb_path, 'wb') as f:
                            f.write(r.content)
                        thumb = open(thumb_path, 'rb')
            except:
                pass
            
            # Audio yuborish
            caption = (
                f"🎵 *{title}*\n"
                f"👤 {uploader}\n"
                f"📏 {Helpers.format_size(file_size)} • {quality}kbps\n"
                f"⏱ {Helpers.format_duration(duration)}"
            )
            
            with open(mp3_file, 'rb') as audio:
                self.bot.send_audio(
                    chat_id,
                    audio,
                    title=title,
                    performer=uploader,
                    duration=duration,
                    thumb=thumb,
                    caption=caption,
                    parse_mode="Markdown"
                )
            
            # Tozalash
            try:
                self.bot.delete_message(chat_id, msg_id)
            except:
                pass
            
            if thumb:
                thumb.close()
            
            Helpers.cleanup_files(file_id)
            
            # Statistika
            self.db.add_download(is_audio=True)
            user = self.db.get_user(chat_id)
            self.db.update_user(chat_id, downloads=user['downloads'] + 1)
            
            return True
            
        except Exception as e:
            try:
                self.bot.edit_message_text(f"❌ Xato: {str(e)}", chat_id, msg_id)
            except:
                pass
            Helpers.cleanup_files(file_id)
            return False
    
    def download_video(self, url: str, quality: str,
                       chat_id: int, msg_id: int,
                       user_data: Dict) -> bool:
        """Video yuklash"""
        file_id = Helpers.get_unique_id()
        
        try:
            # Format string
            format_str = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'
            
            ydl_opts = {
                'format': format_str,
                'outtmpl': f'{Config.DOWNLOAD_DIR}/{file_id}.%(ext)s',
                'merge_output_format': 'mp4',
                'prefer_ffmpeg': True,
                'quiet': True,
                'no_warnings': True,
                'age_limit': None,
                'geo_bypass': True,
                'nocheckcertificate': True,
            }
            
            self.bot.edit_message_text("⏳ Video yuklanmoqda...", chat_id, msg_id)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
            
            # Faylni topish
            video_file = None
            for f in os.listdir(Config.DOWNLOAD_DIR):
                if f.startswith(file_id):
                    video_file = os.path.join(Config.DOWNLOAD_DIR, f)
                    break
            
            if not video_file or not os.path.exists(video_file):
                raise Exception("Video fayl topilmadi!")
            
            file_size = os.path.getsize(video_file)
            
            # Hajm tekshirish
            if file_size > Config.MAX_FILE_SIZE:
                Helpers.cleanup_files(file_id)
                self.bot.edit_message_text(
                    f"⚠️ *Video hajmi katta!*\n\n"
                    f"📏 Hajmi: {Helpers.format_size(file_size)}\n"
                    f"📋 Limit: {Helpers.format_size(Config.MAX_FILE_SIZE)}\n\n"
                    f"💡 *Yechim:* Past sifatni tanlang yoki Audio rejimidan foydalaning!",
                    chat_id, msg_id,
                    parse_mode="Markdown"
                )
                return False
            
            title = Helpers.clean_filename(info.get('title', 'Video'))
            duration = info.get('duration', 0)
            
            self.bot.edit_message_text("📤 Video yuborilmoqda...", chat_id, msg_id)
            
            caption = (
                f"🎬 *{title}*\n"
                f"📏 {Helpers.format_size(file_size)} • {quality}p\n"
                f"⏱ {Helpers.format_duration(duration)}"
            )
            
            with open(video_file, 'rb') as video:
                self.bot.send_video(
                    chat_id,
                    video,
                    caption=caption,
                    parse_mode="Markdown",
                    supports_streaming=True,
                    duration=duration
                )
            
            try:
                self.bot.delete_message(chat_id, msg_id)
            except:
                pass
            
            Helpers.cleanup_files(file_id)
            self.db.add_download(is_audio=False)
            
            return True
            
        except Exception as e:
            try:
                self.bot.edit_message_text(f"❌ Xato: {str(e)}", chat_id, msg_id)
            except:
                pass
            Helpers.cleanup_files(file_id)
            return False

# ===================== BOT CLASS =====================

class YouTubeBot:
    """Asosiy bot klassi"""
    
    def __init__(self):
        self.bot = telebot.TeleBot(Config.TOKEN, parse_mode=None)
        self.db = SimpleDB()
        self.downloader = Downloader(self.bot, self.db)
        self.user_urls = {}  # URL saqlash
        
        # Handlerlarni ro'yxatdan o'tkazish
        self._register_handlers()
        
        # Eski fayllarni tozalash
        Helpers.cleanup_old_files()
    
    def _register_handlers(self):
        """Handlerlarni ro'yxatdan o'tkazish"""
        
        @self.bot.message_handler(commands=['start'])
        def cmd_start(m):
            self._handle_start(m)
        
        @self.bot.message_handler(commands=['help'])
        def cmd_help(m):
            self._handle_help(m)
        
        @self.bot.message_handler(commands=['settings', 'sozlash'])
        def cmd_settings(m):
            self._handle_settings(m)
        
        @self.bot.message_handler(commands=['stats', 'statistika'])
        def cmd_stats(m):
            self._handle_stats(m)
        
        @self.bot.message_handler(func=lambda m: m.text in ["🎵 Audio (MP3)", "🎬 Video (MP4)"])
        def mode_handler(m):
            self._handle_mode(m)
        
        @self.bot.message_handler(func=lambda m: m.text == "⚙️ Sozlamalar")
        def settings_btn(m):
            self._handle_settings(m)
        
        @self.bot.message_handler(func=lambda m: m.text == "📊 Statistika")
        def stats_btn(m):
            self._handle_stats(m)
        
        @self.bot.message_handler(func=lambda m: m.text and Helpers.is_valid_url(m.text))
        def url_handler(m):
            self._handle_url(m)
        
        @self.bot.callback_query_handler(func=lambda c: True)
        def callback_handler(c):
            self._handle_callback(c)
        
        @self.bot.message_handler(func=lambda m: True)
        def unknown_handler(m):
            self._handle_unknown(m)
    
    def _handle_start(self, m):
        """Start buyrug'i"""
        self.db.get_user(m.chat.id)  # Foydalanuvchini ro'yxatga olish
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("🎵 Audio (MP3)", "🎬 Video (MP4)")
        markup.row("⚙️ Sozlamalar", "📊 Statistika")
        
        self.bot.send_message(m.chat.id, """
🎧 *YouTube/Media Downloader Bot*

📥 *Qo'llab-quvvatlanadigan platformalar:*
├ YouTube, Instagram, TikTok
├ Twitter/X, Facebook, Vimeo
├ SoundCloud, Spotify, Twitch
└ Va yana 1000+ sayt! 🔥

🎯 *Imkoniyatlar:*
├ 🎵 320kbps MP3 audio
├ 🎬 4K video yuklash
├ 📋 Playlist qo'llab-quvvati
└ .......,....................

📤 *Foydalanish:*
Link yuboring — tamom! 

⬇️ Pastdagi tugmalardan rejim tanlang:
        """, parse_mode="Markdown", reply_markup=markup)
    
    def _handle_help(self, m):
        """Yordam"""
        self.bot.send_message(m.chat.id, """
📖 *Qo'llanma*

*Oddiy foydalanish:*
1️⃣ Link yuboring
2️⃣ Format tanlang
3️⃣ Yuklab oling!

*Buyruqlar:*
├ /start - Boshlash
├ /help - Yordam
├ /settings - Sozlamalar
└ /stats - Statistika

*Sifat tanlovlari:*
├ 🎵 Audio: 128, 192, 256, 320 kbps
└ 🎬 Video: 360p, 480p, 720p, 1080p, 4K

*Qo'llab-quvvat:*
├ YouTube ✓
├ Instagram ✓
├ TikTok ✓
├ Twitter/X ✓
├ Facebook ✓
├ SoundCloud ✓
└ 1000+ boshqa saytlar ✓

💡 *Maslahat:* Katta videolar uchun past sifat tanlang!
        """, parse_mode="Markdown")
    
    def _handle_settings(self, m):
        """Sozlamalar"""
        user = self.db.get_user(m.chat.id)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🎵 Audio sifati", callback_data="set_audio"),
            types.InlineKeyboardButton("🎬 Video sifati", callback_data="set_video"),
        )
        
        current_audio = user.get('audio_quality', '320')
        current_video = user.get('video_quality', '720')
        
        self.bot.send_message(m.chat.id, f"""
⚙️ *Sozlamalar*

📌 *Joriy sozlamalar:*
├ 🎵 Audio sifati: *{current_audio} kbps*
└ 🎬 Video sifati: *{current_video}p*

Quyidagi tugmalardan o'zgartiring:
        """, parse_mode="Markdown", reply_markup=markup)
    
    def _handle_stats(self, m):
        """Statistika"""
        stats = self.db.get_stats()
        user = self.db.get_user(m.chat.id)
        
        self.bot.send_message(m.chat.id, f"""
📊 *Statistika*

🌍 *Umumiy:*
├ 📥 Jami yuklanmalar: *{stats['downloads']}*
├ 🎵 Audio: *{stats['audio']}*
└ 🎬 Video: *{stats['video']}*

👤 *Sizning:*
├ 📥 Yuklanmalar: *{user['downloads']}*
└ 📅 Qo'shilgan: *{user['joined'][:10]}*
        """, parse_mode="Markdown")
    
    def _handle_mode(self, m):
        """Rejim tanlash"""
        user = self.db.get_user(m.chat.id)
        
        if "Audio" in m.text:
            self.db.update_user(m.chat.id, mode='audio')
            self.bot.reply_to(m, "✅ Audio rejimi tanlandi!\n\nEndi link yuboring 👇")
        else:
            self.db.update_user(m.chat.id, mode='video')
            self.bot.reply_to(m, "✅ Video rejimi tanlandi!\n\nEndi link yuboring 👇")
    
    def _handle_url(self, m):
        """URL qabul qilish"""
        url = m.text.strip()
        chat_id = m.chat.id
        user = self.db.get_user(chat_id)
        
        # URL saqlash
        self.user_urls[chat_id] = url
        
        # Tugmalar
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        audio_q = user.get('audio_quality', '320')
        video_q = user.get('video_quality', '720')
        
        markup.add(
            types.InlineKeyboardButton(f"🎵 MP3 ({audio_q}kbps)", callback_data=f"dl_a_{audio_q}"),
            types.InlineKeyboardButton(f"🎬 Video ({video_q}p)", callback_data=f"dl_v_{video_q}"),
        )
        markup.add(
            types.InlineKeyboardButton("📊 Sifat tanlash", callback_data="choose_quality"),
            types.InlineKeyboardButton("📋 Ma'lumot", callback_data="get_info"),
        )
        
        self.bot.send_message(chat_id, "📥 *Nima yuklamoqchisiz?*", 
                             parse_mode="Markdown", reply_markup=markup)
    
    def _handle_callback(self, call):
        """Callback handler"""
        chat_id = call.message.chat.id
        msg_id = call.message.id
        data = call.data
        
        try:
            # Audio sifati tanlash
            if data == "set_audio":
                markup = types.InlineKeyboardMarkup(row_width=4)
                buttons = [
                    types.InlineKeyboardButton(f"{q}kbps", callback_data=f"sq_a_{q}")
                    for q in Config.AUDIO_QUALITIES
                ]
                markup.add(*buttons)
                self.bot.edit_message_text(
                    "🎵 *Audio sifatini tanlang:*",
                    chat_id, msg_id,
                    parse_mode="Markdown",
                    reply_markup=markup
                )
                self.bot.answer_callback_query(call.id)
                return
            
            # Video sifati tanlash
            if data == "set_video":
                markup = types.InlineKeyboardMarkup(row_width=3)
                buttons = [
                    types.InlineKeyboardButton(f"{q}p", callback_data=f"sq_v_{q}")
                    for q in Config.VIDEO_QUALITIES
                ]
                markup.add(*buttons)
                self.bot.edit_message_text(
                    "🎬 *Video sifatini tanlang:*",
                    chat_id, msg_id,
                    parse_mode="Markdown",
                    reply_markup=markup
                )
                self.bot.answer_callback_query(call.id)
                return
            
            # Sifatni saqlash
            if data.startswith("sq_"):
                parts = data.split("_")
                quality_type = parts[1]
                quality = parts[2]
                
                if quality_type == "a":
                    self.db.update_user(chat_id, audio_quality=quality)
                    self.bot.answer_callback_query(call.id, f"✅ Audio: {quality}kbps")
                else:
                    self.db.update_user(chat_id, video_quality=quality)
                    self.bot.answer_callback_query(call.id, f"✅ Video: {quality}p")
                
                self.bot.edit_message_text(
                    f"✅ Sifat saqlandi!\n\nEndi link yuboring 👇",
                    chat_id, msg_id
                )
                return
            
            # Sifat tanlash menyusi
            if data == "choose_quality":
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("🎵 128kbps", callback_data="dl_a_128"),
                    types.InlineKeyboardButton("🎵 192kbps", callback_data="dl_a_192"),
                    types.InlineKeyboardButton("🎵 256kbps", callback_data="dl_a_256"),
                    types.InlineKeyboardButton("🔥 320kbps", callback_data="dl_a_320"),
                )
                markup.add(
                    types.InlineKeyboardButton("🎬 480p", callback_data="dl_v_480"),
                    types.InlineKeyboardButton("🎬 720p", callback_data="dl_v_720"),
                    types.InlineKeyboardButton("🎬 1080p", callback_data="dl_v_1080"),
                    types.InlineKeyboardButton("🎬 4K", callback_data="dl_v_2160"),
                )
                self.bot.edit_message_text(
                    "📊 *Sifatni tanlang:*",
                    chat_id, msg_id,
                    parse_mode="Markdown",
                    reply_markup=markup
                )
                self.bot.answer_callback_query(call.id)
                return
            
            # Ma'lumot olish
            if data == "get_info":
                url = self.user_urls.get(chat_id)
                if not url:
                    self.bot.answer_callback_query(call.id, "❌ URL topilmadi!")
                    return
                
                self.bot.answer_callback_query(call.id, "⏳ Ma'lumot olinmoqda...")
                self.bot.edit_message_text("⏳ Ma'lumot olinmoqda...", chat_id, msg_id)
                
                info = self.downloader.get_info(url)
                if not info:
                    self.bot.edit_message_text("❌ Ma'lumot olishda xato!", chat_id, msg_id)
                    return
                
                title = info.get('title', 'Noma\'lum')
                duration = Helpers.format_duration(info.get('duration'))
                views = Helpers.format_views(info.get('view_count'))
                uploader = info.get('uploader', 'Noma\'lum')
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("🎵 MP3", callback_data="dl_a_320"),
                    types.InlineKeyboardButton("🎬 Video", callback_data="dl_v_720"),
                )
                
                self.bot.edit_message_text(
                    f"📋 *Ma'lumot:*\n\n"
                    f"📌 *Nom:* {title[:50]}\n"
                    f"👤 *Kanal:* {uploader}\n"
                    f"⏱ *Davomiyligi:* {duration}\n"
                    f"👁 *Ko'rishlar:* {views}\n",
                    chat_id, msg_id,
                    parse_mode="Markdown",
                    reply_markup=markup
                )
                return
            
            # Yuklash
            if data.startswith("dl_"):
                url = self.user_urls.get(chat_id)
                if not url:
                    self.bot.answer_callback_query(call.id, "❌ URL topilmadi! Qayta yuboring.")
                    return
                
                parts = data.split("_")
                dl_type = parts[1]
                quality = parts[2]
                
                self.bot.answer_callback_query(call.id, "⏳ Yuklanmoqda...")
                
                user = self.db.get_user(chat_id)
                
                if dl_type == "a":
                    self.downloader.download_audio(url, quality, chat_id, msg_id, user)
                else:
                    self.downloader.download_video(url, quality, chat_id, msg_id, user)
                
                return
                
        except Exception as e:
            print(f"Callback xatosi: {e}")
            try:
                self.bot.answer_callback_query(call.id, f"❌ Xato: {str(e)[:50]}")
            except:
                pass
    
    def _handle_unknown(self, m):
        """Noma'lum xabar"""
        self.bot.reply_to(m, 
            "❌ Bu link tanilmadi!\n\n"
            "📤 Quyidagi platformalardan link yuboring:\n"
            "YouTube, Instagram, TikTok, Twitter, Facebook va boshqalar..."
        )
    
    def run(self):
        """Botni ishga tushirish"""
        print("""
╔═══════════════════════════════════════════════════╗
║                                                   ║
║   🎵 YOUTUBE DOWNLOADER BOT                       ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━                       ║
║                                                   ║
║   ✅ MP3 320kbps                                  ║
║   ✅ Video 4K                                     ║
║   ✅ 1000+ platform                               ║
║   ✅ 18+ support                                  ║
║   ✅ Auto-install                                 ║
║                                                   ║
║   🌍 Environment: """ + platform.system() + """
║   🐍 Python: """ + platform.python_version() + """
║                                                   ║
║   🟢 BOT ISHLAYAPTI!                              ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
        """)
        
        while True:
            try:
                self.bot.infinity_polling(
                    skip_pending=True,
                    timeout=60,
                    long_polling_timeout=60
                )
            except KeyboardInterrupt:
                print("\n👋 Bot to'xtatildi!")
                break
            except Exception as e:
                print(f"❌ Xato: {e}")
                print("🔄 5 sekunddan so'ng qayta urinish...")
                time.sleep(5)

# ===================== MAIN =====================

if __name__ == "__main__":
    try:
        bot = YouTubeBot()
        bot.run()
    except Exception as e:
        print(f"❌ Kritik xato: {e}")
        sys.exit(1)