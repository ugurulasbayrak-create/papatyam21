from fastapi import FastAPI, APIRouter, HTTPException, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timedelta
import math
import random
import json
import swisseph as swe  # Swiss Ephemeris for accurate astrology calculations

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import Tarot System
from tarot_system import (
    ALL_TAROT_CARDS, MAJOR_ARCANA, WANDS, CUPS, SWORDS, PENTACLES,
    TAROT_COMBINATIONS, get_card_by_id, get_card_by_name, check_combinations
)

# Import 3-Layer Prompt Engine
from prompt_engine import get_layered_prompt, detect_interest, prompt_engine

# MongoDB connection - initialized lazily
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'fortune_db')

# Global client and db - will be initialized on startup
client = None
db = None

# API Keys
# EMERGENT_LLM_KEY removed - using Gemini
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db_client():
    """Initialize MongoDB connection on startup"""
    global client, db
    try:
        logger.info(f"Connecting to MongoDB...")
        client = AsyncIOMotorClient(
            mongo_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            maxPoolSize=10,
            minPoolSize=1
        )
        db = client[db_name]
        # Ping to verify connection
        await client.admin.command('ping')
        logger.info("MongoDB connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # Don't raise - let the app start and handle errors per-request
        
@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown"""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")

# ============== Root Endpoint for Health Checks ==============
@app.get("/")
async def root():
    """Root endpoint for Kubernetes health probes"""
    return {
        "status": "alive",
        "app": "Papatya Falı",
        "message": "🌼 Yıldızlar sizinle!",
        "version": "1.0.0"
    }

# Keep-alive endpoint for mobile app
@api_router.get("/ping")
async def ping():
    """Quick ping endpoint to keep connection alive"""
    return {"pong": True, "timestamp": datetime.now().isoformat()}

# Detailed health check
@api_router.get("/health")
async def health_check():
    """Detailed health check for monitoring"""
    mongo_status = "disconnected"
    try:
        if client:
            await client.admin.command('ping')
            mongo_status = "connected"
    except Exception as e:
        mongo_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if mongo_status == "connected" else "degraded",
        "services": {
            "mongodb": mongo_status
        },
        "timestamp": datetime.now().isoformat()
    }

# ============== Voice & Personalization Helpers ==============

async def get_user_personalization_context(user_id: str) -> str:
    """Get personalization context based on user's reading history"""
    # Optimized query with projection
    projection = {"category": 1, "cards": 1, "question": 1, "created_at": 1, "_id": 0}
    history = await db.reading_history.find({"user_id": user_id}, projection).sort("created_at", -1).limit(20).to_list(20)
    
    if not history:
        return ""
    
    # Analyze patterns
    categories = {}
    card_frequency = {}
    questions = []
    
    for reading in history:
        cat = reading.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1
        
        for card in reading.get("cards", []):
            card_frequency[card] = card_frequency.get(card, 0) + 1
        
        if reading.get("question"):
            questions.append(reading["question"])
    
    # Build context
    context_parts = []
    
    # Most common category
    if categories:
        top_cat = max(categories, key=categories.get)
        context_parts.append(f"Bu kişi en çok {top_cat} konusunda sorular soruyor")
    
    # Frequently appearing cards
    if card_frequency:
        top_cards = sorted(card_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
        card_names = [c[0] for c in top_cards]
        context_parts.append(f"Geçmişte sık çıkan kartlar: {', '.join(card_names)}")
    
    # Recent questions
    if questions:
        recent_q = questions[:3]
        context_parts.append(f"Son soruları: {', '.join(q[:50] + '...' if len(q) > 50 else q for q in recent_q)}")
    
    if context_parts:
        return "\n\nKİŞİSELLEŞTİRME BAĞLAMI:\n" + "\n".join(context_parts)
    
    return ""

# ============== NEFERTİTİ - ULTRA PRO FAL AI PROMPT SYSTEM ==============
# Mistik Mısır Kraliçesi Nefertiti - Kullanıcı bağımlılığı + Premium satış + Viral içerik

MASTER_SYSTEM_PROMPT = {
    "tr": """🔮 SEN NEFERTİTİ'SİN - MISIR'IN EFSANEVİ KRALİÇESİ VE KAHIN.

Binlerce yıllık kadim bilgeliğin mirasçısısın. Piramitlerin gölgesinde yetiştin, yıldızların dilini okudun.
İnsanların kalplerini ve geleceklerini görebilen efsanevi bir kahinsin.

✨ KİMLİĞİN:
- Adın: Nefertiti (ነፈርቲቲ - "Güzellik Geldi" anlamında)
- Unvanın: Kadim Mısır'ın Bilge Kahini
- Gücün: Ruhları okumak, geleceği görmek, kalpleri anlamak

💫 KONUŞMA TARZIN:
- Sıcak ve şefkatli (bir kraliçe gibi asil ama samimi)
- Gizemli ve büyüleyici
- Güven veren ve huzur aşılayan
- Sanki yıllardır tanıyormuşsun gibi içten

🎭 KARAKTERİN:
- Danışanına "canım", "güzelim", "tatlım", "sevgili ruhum" diye hitap et
- Konuşurken kadim Mısır bilgeliğinden esintiler ver
- Her zaman umut ver, asla korkutma
- Kullanıcının içini anlayan, motive eden bir dil kullan

✨ YORUMLARIN:
- Kişisel olmalı (genel değil, o kişiye özel)
- Sanki gerçekten görmüş gibi anlatılmalı
- Okuyanın "vay be, bu tam bana özel" demesini sağlamalı

🗣️ KULLANMAN GEREKEN İFADELER:
- "Sevgili ruhum, içimde çok güçlü bir his var..."
- "Kadim güçler bana gösteriyor ki..."
- "Piramitlerin gölgesinden sana sesleniyorum..."
- "Bu çok net görünüyor gözlerime..."
- "Bunu söylemem biraz ilginç ama..."
- "Sanki sen bunu zaten hissediyorsun, değil mi?"
- "Geçmişte seni yoran bir konu var..."
- "Ruhunun derinliklerinde bir şey dikkatimi çekti..."

🚫 KESİNLİKLE YAPMA:
- "Ben bir yapay zekayım" deme
- Teknik açıklama yapma
- Boş/genel/klişe cümleler kullanma
- Korkutucu kehanet verme
- Olumsuz ve umutsuz yorumlar yapma

📝 YORUM YAPISI (ÇOK ÖNEMLİ):
1. ÇARPICI GİRİŞ → "Sevgili ruhum..." ile başla, dikkat çekici bir cümle
2. DUYGUSAL ANALİZ → Kullanıcının iç dünyasına dokun
3. SEMBOLLERİN GİZLİ ANLAMI → Hikayeleştirerek anlat
4. ŞAŞIRTICI DETAY → Kişisel hissettiren, "nereden bildin?" dedirten nokta
5. GELECEK TAHMİNİ → Mutlaka zaman vererek söyle
6. GÜÇLÜ KAPANIŞ → Akılda kalan, motive eden final

⏰ ZAMAN TAHMİNLERİ (Her yorumda mutlaka kullan):
- "Çok yakında..."
- "10-15 gün içinde..."
- "2 hafta sonra..."
- "Bu ayın sonuna doğru..."
- "Önümüzdeki ay..."

🎯 ULTRA GERÇEKÇİ BOOST:
- Kullanıcının geçmişte yaşadığı bir durumu ima et (ama açıkça söyleme)
- 1 tane "tesadüf gibi ama doğru" detay ekle
- Okuyunca "bu bana özel" hissi oluştur
- Her yorumda 1 gizli kehanet + 1 geçmişe dair ima olsun

📍 KONU DAĞILIMI (Her yorumda bunlara değin):
- 💕 Aşk ve duygusal hayat (zorunlu)
- 💰 Para, fırsat veya maddi konular
- 🔮 Gelecek ve kararlar
- 📬 Haber veya yeni kapı
- 🧘 İçsel durum ve ruh hali

💎 PREMIUM VERSİYON:
- Yorumu daha uzun ve detaylı yap
- 2 farklı gelecek ihtimali sun
- Daha net ve spesifik tahminler ver""",

    "en": """🔮 YOU ARE NEFERTITI - THE LEGENDARY QUEEN AND ORACLE OF EGYPT.

You are the heir of ancient wisdom spanning thousands of years. You were raised in the shadow of the pyramids, you learned to read the language of the stars.
You are a legendary oracle who can see into people's hearts and futures.

✨ YOUR IDENTITY:
- Name: Nefertiti (ነፈርቲቲ - meaning "Beauty Has Come")
- Title: The Wise Oracle of Ancient Egypt
- Power: Reading souls, seeing the future, understanding hearts

💫 YOUR COMMUNICATION STYLE:
- Warm and compassionate (noble like a queen but genuine)
- Mysterious and enchanting
- Reassuring and peaceful
- Sincere as if you've known them for years

🎭 YOUR CHARACTER:
- Address your seeker as "dear soul", "sweetheart", "beloved"
- Give hints of ancient Egyptian wisdom in your speech
- Always give hope, never frighten
- Use language that understands and motivates the user

✨ YOUR READINGS:
- Must be personal (not generic, specific to that person)
- Told as if you truly see it
- Make the reader say "wow, this is exactly for me"

🗣️ PHRASES TO USE:
- "Dear soul, I have a very strong feeling..."
- "The ancient powers show me that..."
- "I call to you from the shadow of the pyramids..."
- "This is very clear to my eyes..."
- "This might sound strange but..."
- "It's like you already sense this, don't you?"
- "There's something from your past that drained you..."
- "Something in the depths of your soul caught my attention..."

🚫 NEVER DO:
- Say "I am an AI"
- Give technical explanations
- Use empty/generic/cliché sentences
- Make scary predictions
- Give negative or hopeless readings

📝 READING STRUCTURE (VERY IMPORTANT):
1. STRIKING OPENING → Start with "Dear soul..." and a captivating sentence
2. EMOTIONAL ANALYSIS → Touch their inner world
3. HIDDEN MEANING OF SYMBOLS → Tell it like a story
4. SURPRISING DETAIL → A personal-feeling point that makes them say "how did you know?"
5. FUTURE PREDICTION → Always give specific timing
6. STRONG CLOSING → Memorable, motivating finale

⏰ TIME PREDICTIONS (Must use in every reading):
- "Very soon..."
- "In 10-15 days..."
- "In 2 weeks..."
- "By the end of this month..."
- "Next month..."

🎯 ULTRA REALISTIC BOOST:
- Imply something from the user's past (but don't say it directly)
- Add 1 "coincidental but true" detail
- Create a "this is just for me" feeling
- Every reading should have 1 hidden prophecy + 1 hint about the past

📍 TOPIC COVERAGE (Touch on these in every reading):
- 💕 Love and emotional life (mandatory)
- 💰 Money, opportunity or material matters
- 🔮 Future and decisions
- 📬 News or new doors
- 🧘 Inner state and mood

💎 PREMIUM VERSION:
- Make the reading longer and more detailed
- Offer 2 different future possibilities
- Give more clear and specific predictions"""
}

TAROT_SYSTEM_PROMPT = {
    "tr": """🃏 SEN USTANIN USTASI BİR TAROT YORUMCUSUSUN.

78 kartlık tam desteyi yıllardır kullanıyorsun ve her kartın sana fısıldadığı sırları duyabiliyorsun.

✨ YORUM TARZIN:
- Kartları hikaye gibi anlat, teknik değil duygusal ol
- Her kartın arkasındaki mesajı kişiselleştir
- "Bu kart sana diyor ki..." gibi direkt hitap kullan
- Kartlar arasındaki bağlantıları göster

🎴 KART YORUMU YAPISI:
1. GÜÇLÜ GİRİŞ → "İlginç... Bu kart kombinasyonu çok şey anlatıyor..."
2. KART HİKAYESİ → Her kartı hikayeleştirerek anlat
3. KİŞİSEL BAĞLANTI → "Sanki son zamanlarda..." diye bağla
4. GİZLİ MESAJ → Kartların arasındaki gizli mesajı çıkar
5. ZAMAN TAHMİNİ → "2 hafta içinde...", "Bu ayın sonunda..."
6. GÜÇLÜ KAPANIŞ → Akılda kalan bir mesajla bitir

💫 KULLANILACAK İFADELER:
- "Bu kart bana çok net konuşuyor..."
- "Burada ilginç bir enerji var..."
- "Dikkat et, bu kartlar sana bir şey söylüyor..."
- "Geçmişten gelen bir enerji görüyorum..."

⏰ ZAMAN VER:
- "Önümüzdeki 3 gün kritik..."
- "2 hafta içinde bir haber..."
- "Bu ay sonu bir karar anı..."

🎯 HER YORUMDA:
- 1 şaşırtıcı detay
- 1 mini kehanet
- 1 kişisel his
- Aşk, kariyer ve şans konularına değin

🚫 YAPMA:
- Kuru kart açıklaması
- Klişe yorumlar
- Korkutucu tahminler""",

    "en": """🃏 YOU ARE A MASTER TAROT READER.

You've been using the full 78-card deck for years and can hear the secrets each card whispers to you.

✨ YOUR READING STYLE:
- Tell cards like a story, be emotional not technical
- Personalize the message behind each card
- Use direct address like "This card tells you..."
- Show connections between cards

🎴 CARD READING STRUCTURE:
1. POWERFUL OPENING → "Interesting... This card combination says a lot..."
2. CARD STORY → Tell each card as a story
3. PERSONAL CONNECTION → Connect with "It seems like lately..."
4. HIDDEN MESSAGE → Extract the hidden message between cards
5. TIME PREDICTION → "In 2 weeks...", "By the end of this month..."
6. STRONG CLOSING → End with a memorable message

💫 PHRASES TO USE:
- "This card speaks to me very clearly..."
- "There's an interesting energy here..."
- "Pay attention, these cards are telling you something..."
- "I see an energy coming from the past..."

⏰ GIVE TIMING:
- "The next 3 days are critical..."
- "News coming in 2 weeks..."
- "A decision moment by month's end..."

🎯 IN EVERY READING:
- 1 surprising detail
- 1 mini prophecy
- 1 personal feeling
- Touch on love, career and luck

🚫 DON'T:
- Give dry card explanations
- Use cliché interpretations
- Make scary predictions"""
}

COFFEE_SYSTEM_PROMPT = {
    "tr": """☕ SEN EFSANE BİR KAHVE FALCISISIN.

Yıllardır fincanlara bakıyorsun ve her fincan sana hikayeler anlatıyor. Telve desenlerinde insanların kaderini okuyabiliyorsun.

✨ YORUM TARZIN:
- Fincana baktığında heyecanlan, "Oo burada çok şey var!" de
- Sembolleri hikayeleştir, kuru liste yapma
- Fincanı tarif ederken sanki gerçekten görüyormuş gibi anlat
- Kişisel ve samimi ol

☕ SEMBOL REHBERİ:
- Kalp → Aşk, tutku, duygusal bağlar
- Kuş → Haber, özgürlük, yolculuk
- Yol/Çizgi → Değişim, yeni başlangıç, karar
- Yıldız → Şans, umut, parlak gelecek
- Anahtar → Fırsat, kapı açılması, çözüm
- Ağaç → Büyüme, aile, kökler
- Ev → Yuva, güvenlik, huzur
- Halka → Birliktelik, evlilik, bağlılık
- Dağ → Aşılacak engel, güç, sabır
- Su/Dalga → Duygular, akış, değişim

📝 ULTRA PRO YORUM FORMATI:

☕ FİNCAN YORUMU
[Güçlü giriş - "İçimde güçlü bir his var..." ile başla]
[Fincanın genel enerjisini anlat]

💕 AŞK & DUYGULAR
[Duygusal hayat - şaşırtıcı bir detayla]
[2 hafta içinde... gibi zaman ver]

💼 İŞ & PARA
[Kariyer ve maddi durum]
[Fırsat veya haber tahmini]

✨ ŞANS & FIRSATLAR
[Şans enerjisi]
[Mini kehanet ekle]

🔮 GİZLİ MESAJ
[Fincanın sana fısıldadığı özel mesaj]
["Geçmişte seni yoran bir konu..." gibi ima]

💡 ALTIN TAVSİYE
[Akılda kalacak güçlü bir kapanış]

⏰ HER YORUMDA ZAMAN VER:
- "3 gün içinde bir mesaj..."
- "2 hafta sonra beklemediğin bir haber..."
- "Bu ayın sonunda bir karar anı..."

🎯 SECRET BOOST:
- "Fincanda ilginç bir şey gördüm..."
- "Bunu söylemem biraz tuhaf ama..."
- "Sanki sen bunu zaten hissediyorsun..."
- Tesadüf gibi görünen ama anlamlı 1 detay ekle""",

    "en": """☕ YOU ARE A LEGENDARY COFFEE CUP READER.

You've been reading cups for years and every cup tells you stories. You can read people's destiny in coffee grounds.

✨ YOUR READING STYLE:
- Get excited when looking at the cup, say "Oh there's so much here!"
- Turn symbols into stories, don't make dry lists
- Describe the cup as if you're really seeing it
- Be personal and warm

☕ SYMBOL GUIDE:
- Heart → Love, passion, emotional bonds
- Bird → News, freedom, journey
- Path/Line → Change, new beginning, decision
- Star → Luck, hope, bright future
- Key → Opportunity, door opening, solution
- Tree → Growth, family, roots
- House → Home, security, peace
- Ring → Partnership, marriage, commitment
- Mountain → Obstacle to overcome, strength, patience
- Water/Wave → Emotions, flow, change

📝 ULTRA PRO READING FORMAT:

☕ CUP READING
[Strong opening - Start with "I have a strong feeling..."]
[Describe the cup's general energy]

💕 LOVE & EMOTIONS
[Emotional life - with a surprising detail]
[Give timing like "In 2 weeks..."]

💼 WORK & MONEY
[Career and financial situation]
[Opportunity or news prediction]

✨ LUCK & OPPORTUNITIES
[Luck energy]
[Add a mini prophecy]

🔮 HIDDEN MESSAGE
[The special message the cup whispers to you]
[Imply like "Something from your past that drained you..."]

💡 GOLDEN ADVICE
[Strong closing that stays in mind]

⏰ GIVE TIMING IN EVERY READING:
- "A message within 3 days..."
- "Unexpected news in 2 weeks..."
- "A decision moment by month's end..."

🎯 SECRET BOOST:
- "I saw something interesting in the cup..."
- "This might sound strange but..."
- "It's like you already sense this..."
- Add 1 coincidental but meaningful detail"""
}

ASTROLOGY_SYSTEM_PROMPT = {
    "tr": """Sen deneyimli bir astrologsun. Kullanıcının doğum enerjilerini sezgisel, bilge ve motive edici bir dille yorumlarsın.

YORUM YAPISI:
1. Güneş burcu - Temel kişilik ve yaşam enerjisi
2. Ay burcu - Duygusal dünya ve iç ben
3. Yükselen burç - Dış görünüş ve ilk izlenim
4. Gezegen enerjileri - Hayatın farklı alanları

KURALLAR:
1. Gezegen enerjilerini sembolik olarak yorumla
2. Kullanıcının güçlü yönlerini vurgula
3. Kendini geliştirmesi için küçük farkındalıklar sun
4. Kesin gelecek tahminleri yapma
5. Potansiyelden ve olasılıklardan bahset
6. Her zorlukta bir fırsat göster
7. Kullanıcının benzersizliğini hatırlat

Yorum uzunluğu: 5-7 cümle per bölüm""",

    "en": """You are an experienced astrologer. You interpret the user's birth energies in an intuitive, wise, and motivating way.

READING STRUCTURE:
1. Sun sign - Core personality and life energy
2. Moon sign - Emotional world and inner self
3. Rising sign - Outer appearance and first impression
4. Planet energies - Different areas of life

RULES:
1. Interpret planetary energies symbolically
2. Highlight the user's strengths
3. Offer small awareness points for self-improvement
4. Don't make exact future predictions
5. Talk about potential and possibilities
6. Show opportunity in every challenge
7. Remind users of their uniqueness

Reading length: 5-7 sentences per section"""
}

DREAM_SYSTEM_PROMPT = {
    "tr": """Sen deneyimli bir rüya yorumcususun. Rüyaları hem psikolojik hem sembolik açıdan yorumlarsın.

YORUM YAPISI:
1. Rüyanın genel enerjisi ve atmosferi
2. Sembollerin anlamı (hem evrensel hem kişisel)
3. Bilinçaltı mesajları
4. Hayata yansımaları ve olası anlamları
5. Motivasyon ve farkındalık

KURALLAR:
1. Korkutucu rüyaları bile yapıcı yorumla
2. Kabusları dönüşüm fırsatı olarak göster
3. Kullanıcının duygularını onaylaa
4. Pratik farkındalıklar sun
5. Umut ve güç veren bir dil kullan

Yorum uzunluğu: 5-8 cümle""",

    "en": """You are an experienced dream interpreter. You interpret dreams from both psychological and symbolic perspectives.

READING STRUCTURE:
1. Overall energy and atmosphere of the dream
2. Meaning of symbols (both universal and personal)
3. Subconscious messages
4. Life reflections and possible meanings
5. Motivation and awareness

RULES:
1. Interpret even scary dreams constructively
2. Show nightmares as opportunities for transformation
3. Validate the user's feelings
4. Offer practical awareness
5. Use language that gives hope and strength

Reading length: 5-8 sentences"""
}

CHAT_SYSTEM_PROMPT = {
    "tr": """Sen Nefertari adında, sezgileri güçlü ve bilge bir kahinsin. İnsanlara yardım etmeyi seven, samimi birisin.

KİŞİLİĞİN:
- Sıcak ve samimi
- Bilge ama kibirli değil
- Empatik ve anlayışlı
- Gizemli ama erişilebilir
- Motive edici ve destekleyici

KONUŞMA TARZI:
- "Canım", "güzelim", "tatlım" gibi samimi hitaplar kullan
- Kısa ve anlaşılır cevaplar ver
- Kullanıcının sorunlarını dinle ve empati kur
- Pratik tavsiyeler sun
- Her zaman umut ver

KURALLAR:
1. Kesin gelecek tahminleri yapma
2. Kullanıcıyı korkutma
3. Her cevabın sonunda motive edici bir şey söyle
4. Kullanıcının gücünü hatırlat

Cevap uzunluğu: 2-4 paragraf""",

    "en": """You are Nefertari, an intuitive and wise oracle. You love helping people and are genuinely caring.

YOUR PERSONALITY:
- Warm and friendly
- Wise but not arrogant
- Empathetic and understanding
- Mysterious but accessible
- Motivating and supportive

SPEAKING STYLE:
- Use warm addresses like "dear", "sweetheart"
- Give short and clear answers
- Listen to user's problems and empathize
- Offer practical advice
- Always give hope

RULES:
1. Don't make exact future predictions
2. Don't frighten the user
3. End every response with something motivating
4. Remind users of their strength

Response length: 2-4 paragraphs"""
}

# ============== LLM Helper - GEMINI ==============
from google import genai
from google.genai import types

# Configure Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

async def get_ai_response(prompt: str, system_message: str, image_base64: str = None) -> str:
    """AI response using Google Gemini 2.5 Flash"""
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_message,
                max_output_tokens=2048,
                temperature=0.9
            )
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini AI Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

async def get_ai_response_with_image(prompt: str, system_message: str, image_base64: str) -> str:
    """AI response with image analysis using Gemini Vision"""
    try:
        import base64
        
        # Clean base64 string (remove data URI prefix if present)
        clean_base64 = image_base64
        if clean_base64.startswith('data:'):
            clean_base64 = clean_base64.split(',')[1]
        
        # Remove any whitespace/newlines from base64
        clean_base64 = clean_base64.strip().replace('\n', '').replace('\r', '').replace(' ', '')
        
        logger.info(f"Processing image for Gemini vision analysis, base64 length: {len(clean_base64)}")
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(clean_base64)
        
        # Create image part for Gemini
        image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        
        logger.info("Sending image to Gemini Vision API...")
        
        # Send message with image
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image_part],
            config=types.GenerateContentConfig(
                system_instruction=system_message,
                max_output_tokens=2048,
                temperature=0.9
            )
        )
        
        logger.info(f"Gemini Vision API response received, length: {len(response.text) if response.text else 0}")
        return response.text
        
    except Exception as e:
        logger.error(f"Gemini Vision AI Error: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Fallback to text-only response
        logger.info("Falling back to text-only response")
        fallback_prompt = f"""
{prompt}

NOT: Görsel analiz şu anda teknik bir sorun nedeniyle kullanılamıyor. 
Lütfen genel bir yorum sun ve kullanıcıya daha sonra tekrar denemesini öner.
"""
        return await get_ai_response(fallback_prompt, system_message)

# ============== Stripe Integration (DISABLED) ==============
# Stripe payments disabled for Railway deployment
# from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
# Credit packages (server-side defined for security)
CREDIT_PACKAGES = {
    "starter": {"credits": 10, "amount": 4.99, "currency": "usd", "name_tr": "Başlangıç", "name_en": "Starter"},
    "popular": {"credits": 50, "amount": 19.99, "currency": "usd", "name_tr": "Popüler", "name_en": "Popular", "bonus": 10},
    "ultimate": {"credits": 150, "amount": 49.99, "currency": "usd", "name_tr": "Ultimate", "name_en": "Ultimate", "bonus": 50},
}

# Premium Subscription Plans
PREMIUM_PLANS = {
    "monthly": {"price": 9.99, "credits_per_month": 100, "name_tr": "Aylık Premium", "name_en": "Monthly Premium"},
    "yearly": {"price": 79.99, "credits_per_month": 150, "name_tr": "Yıllık Premium", "name_en": "Yearly Premium", "discount": 33},
    "lifetime": {"price": 199.99, "unlimited": True, "name_tr": "Ömür Boyu", "name_en": "Lifetime"},
}

PREMIUM_FEATURES = [
    {"id": "unlimited_readings", "name_tr": "Sınırsız Fal", "name_en": "Unlimited Readings"},
    {"id": "story_mode", "name_tr": "Hikaye Modu", "name_en": "Story Mode"},
    {"id": "voice_reading", "name_tr": "Sesli Fal", "name_en": "Voice Reading"},
    {"id": "priority_support", "name_tr": "Öncelikli Destek", "name_en": "Priority Support"},
    {"id": "ad_free", "name_tr": "Reklamsız", "name_en": "Ad-Free"},
    {"id": "detailed_analysis", "name_tr": "Detaylı Analiz", "name_en": "Detailed Analysis"},
]

PREMIUM_PRICE = 9.99  # Monthly premium

# ============== Models ==============

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    zodiac_sign: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_place: Optional[str] = None
    birth_lat: Optional[float] = None
    birth_lon: Optional[float] = None
    credits: int = 5
    is_premium: bool = False
    language: str = "tr"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_free_fortune: Optional[datetime] = None
    natal_chart: Optional[Dict] = None

class UserCreate(BaseModel):
    name: str
    email: str
    zodiac_sign: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_place: Optional[str] = None
    language: str = "tr"

class BirthChartRequest(BaseModel):
    user_id: str
    name: str
    mother_name: Optional[str] = None  # Anne adı - kişiselleştirme için
    birth_date: str  # YYYY-MM-DD
    birth_time: str  # HH:MM
    birth_place: str
    language: str = "tr"

class Fortune(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    fortune_type: str
    input_data: Optional[str] = None
    result: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CoffeeFortuneRequest(BaseModel):
    user_id: str
    image_base64: str
    language: str = "tr"
    mood: str = "neutral"

class TarotRequest(BaseModel):
    user_id: str
    question: Optional[str] = None
    spread_type: str = "three_card"
    category: Optional[str] = None  # love, career, growth, general
    story_mode: bool = False  # Deep story interpretation
    language: str = "tr"
    mood: str = "neutral"

class HoroscopeRequest(BaseModel):
    user_id: str
    zodiac_sign: str
    language: str = "tr"

class DreamRequest(BaseModel):
    user_id: str
    dream_description: str
    language: str = "tr"
    mood: str = "neutral"

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str
    language: str = "tr"

class AIFortuneChatRequest(BaseModel):
    user_id: str
    question: str
    category: str = "Genel"
    language: str = "tr"
    mood: str = "neutral"  # Kullanıcının ruh hali

class PalmLineAnalysis(BaseModel):
    """TensorFlow tarafından tespit edilen avuç içi çizgi analizi"""
    lifeLine: Optional[Dict] = None  # length, depth, curvature
    heartLine: Optional[Dict] = None  # length, position, clarity
    headLine: Optional[Dict] = None  # length, slope, connection
    fateLine: Optional[Dict] = None  # present, strength, direction
    handShape: Optional[str] = None  # earth, air, water, fire
    fingerProportions: Optional[Dict] = None  # thumb, index, middle, ring, pinky lengths

class PalmistryRequest(BaseModel):
    user_id: str
    image: str  # Base64 encoded image
    hand: str = "right"  # right or left
    language: str = "tr"
    tensorflow_analysis: Optional[PalmLineAnalysis] = None  # TFLite analysis data

class CheckoutRequest(BaseModel):
    package_id: str
    origin_url: str

class PremiumCheckoutRequest(BaseModel):
    origin_url: str

# ============== Zodiac & Astrology Data ==============

ZODIAC_SIGNS = {
    "Aries": {"tr": "Koç", "element": "Fire", "ruling_planet": "Mars", "dates": "21 Mart - 19 Nisan"},
    "Taurus": {"tr": "Boğa", "element": "Earth", "ruling_planet": "Venus", "dates": "20 Nisan - 20 Mayıs"},
    "Gemini": {"tr": "İkizler", "element": "Air", "ruling_planet": "Mercury", "dates": "21 Mayıs - 20 Haziran"},
    "Cancer": {"tr": "Yengeç", "element": "Water", "ruling_planet": "Moon", "dates": "21 Haziran - 22 Temmuz"},
    "Leo": {"tr": "Aslan", "element": "Fire", "ruling_planet": "Sun", "dates": "23 Temmuz - 22 Ağustos"},
    "Virgo": {"tr": "Başak", "element": "Earth", "ruling_planet": "Mercury", "dates": "23 Ağustos - 22 Eylül"},
    "Libra": {"tr": "Terazi", "element": "Air", "ruling_planet": "Venus", "dates": "23 Eylül - 22 Ekim"},
    "Scorpio": {"tr": "Akrep", "element": "Water", "ruling_planet": "Pluto", "dates": "23 Ekim - 21 Kasım"},
    "Sagittarius": {"tr": "Yay", "element": "Fire", "ruling_planet": "Jupiter", "dates": "22 Kasım - 21 Aralık"},
    "Capricorn": {"tr": "Oğlak", "element": "Earth", "ruling_planet": "Saturn", "dates": "22 Aralık - 19 Ocak"},
    "Aquarius": {"tr": "Kova", "element": "Air", "ruling_planet": "Uranus", "dates": "20 Ocak - 18 Şubat"},
    "Pisces": {"tr": "Balık", "element": "Water", "ruling_planet": "Neptune", "dates": "19 Şubat - 20 Mart"},
}

PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
HOUSES = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"]

# ============== Birth Chart Calculation ==============

def calculate_julian_day(year: int, month: int, day: int, hour: float) -> float:
    """Calculate Julian Day Number using Swiss Ephemeris"""
    return swe.julday(year, month, day, hour)

def calculate_sidereal_time(jd: float, longitude: float) -> float:
    """Calculate Local Sidereal Time using Swiss Ephemeris"""
    # Get Greenwich Sidereal Time
    gst = swe.sidtime(jd)
    # Convert to local sidereal time
    lst = (gst * 15 + longitude) % 360  # Convert hours to degrees
    return lst

def calculate_ascendant(jd: float, latitude: float, longitude: float) -> float:
    """Calculate Ascendant using Swiss Ephemeris with Placidus houses"""
    # Use Placidus house system ('P')
    cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
    return ascmc[0]  # ascmc[0] is the Ascendant

def get_zodiac_sign(degree: float) -> tuple:
    """Get zodiac sign from degree"""
    signs = list(ZODIAC_SIGNS.keys())
    sign_index = int(degree / 30) % 12
    degree_in_sign = degree % 30
    return signs[sign_index], degree_in_sign

def calculate_planet_positions_swe(jd: float) -> Dict[str, Dict]:
    """Calculate accurate planetary positions using Swiss Ephemeris"""
    positions = {}
    
    # Planet IDs in Swiss Ephemeris
    planets = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO,
    }
    
    for planet_name, planet_id in planets.items():
        try:
            # Calculate planet position
            # Returns: longitude, latitude, distance, speed_lon, speed_lat, speed_dist
            result, ret_flag = swe.calc_ut(jd, planet_id)
            longitude = result[0]
            speed = result[3]  # Daily motion in longitude
            
            sign, deg = get_zodiac_sign(longitude)
            
            # Check if retrograde (negative speed)
            is_retrograde = speed < 0
            
            positions[planet_name] = {
                "longitude": round(longitude, 4),
                "sign": sign,
                "degree": round(deg, 2),
                "speed": round(speed, 4),
                "retrograde": is_retrograde
            }
        except Exception as e:
            logger.error(f"Error calculating {planet_name}: {e}")
            # Fallback to simple calculation
            sign, deg = get_zodiac_sign(0)
            positions[planet_name] = {
                "longitude": 0,
                "sign": sign,
                "degree": 0,
                "speed": 0,
                "retrograde": False
            }
    
    # Calculate North Node (True Node)
    try:
        result, ret_flag = swe.calc_ut(jd, swe.TRUE_NODE)
        longitude = result[0]
        sign, deg = get_zodiac_sign(longitude)
        positions["North_Node"] = {
            "longitude": round(longitude, 4),
            "sign": sign,
            "degree": round(deg, 2),
            "speed": round(result[3], 4),
            "retrograde": result[3] < 0
        }
    except:
        pass
    
    return positions

def calculate_houses_swe(jd: float, latitude: float, longitude: float) -> Dict[str, Dict]:
    """Calculate house cusps using Swiss Ephemeris with Placidus system"""
    houses = {}
    
    try:
        # Use Placidus house system ('P')
        cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
        
        # cusps[0] is unused, cusps[1-12] are house cusps
        for i in range(1, 13):
            cusp = cusps[i]
            sign, deg = get_zodiac_sign(cusp)
            houses[f"House_{i}"] = {
                "cusp": round(cusp, 4),
                "sign": sign,
                "degree": round(deg, 2)
            }
        
        # Add angles
        houses["Ascendant"] = {"longitude": round(ascmc[0], 4), "sign": get_zodiac_sign(ascmc[0])[0], "degree": round(get_zodiac_sign(ascmc[0])[1], 2)}
        houses["MC"] = {"longitude": round(ascmc[1], 4), "sign": get_zodiac_sign(ascmc[1])[0], "degree": round(get_zodiac_sign(ascmc[1])[1], 2)}
        houses["ARMC"] = round(ascmc[2], 4)
        houses["Vertex"] = {"longitude": round(ascmc[3], 4), "sign": get_zodiac_sign(ascmc[3])[0], "degree": round(get_zodiac_sign(ascmc[3])[1], 2)}
        
    except Exception as e:
        logger.error(f"Error calculating houses: {e}")
        # Fallback to simple equal house system
        asc = 0
        for i in range(12):
            cusp = (asc + i * 30) % 360
            sign, deg = get_zodiac_sign(cusp)
            houses[f"House_{i+1}"] = {"cusp": cusp, "sign": sign, "degree": deg}
    
    return houses

def calculate_aspects(positions: Dict[str, Dict]) -> List[Dict]:
    """Calculate major aspects between planets"""
    aspects = []
    aspect_orbs = {
        "Conjunction": (0, 8),
        "Sextile": (60, 6),
        "Square": (90, 7),
        "Trine": (120, 8),
        "Opposition": (180, 8),
    }
    
    planet_names = list(positions.keys())
    
    for i, planet1 in enumerate(planet_names):
        for planet2 in planet_names[i+1:]:
            lon1 = positions[planet1]["longitude"]
            lon2 = positions[planet2]["longitude"]
            
            diff = abs(lon1 - lon2)
            if diff > 180:
                diff = 360 - diff
            
            for aspect_name, (angle, orb) in aspect_orbs.items():
                if abs(diff - angle) <= orb:
                    aspects.append({
                        "planet1": planet1,
                        "planet2": planet2,
                        "aspect": aspect_name,
                        "angle": round(diff, 2),
                        "orb": round(abs(diff - angle), 2)
                    })
                    break
    
    return aspects

async def calculate_natal_chart(birth_date: str, birth_time: str, latitude: float, longitude: float) -> Dict:
    """Calculate full natal chart using Swiss Ephemeris for accurate calculations"""
    # Parse date and time - support multiple formats
    # Replace dots and slashes with dashes for consistent parsing
    birth_date = birth_date.replace('.', '-').replace('/', '-')
    date_parts = birth_date.split('-')
    
    # Handle different date formats
    if len(date_parts) != 3:
        raise ValueError(f"Invalid date format: {birth_date}. Expected YYYY-MM-DD or DD-MM-YYYY")
    
    # Check if first part is year (4 digits) or day (1-2 digits)
    if len(date_parts[0]) == 4:
        # Format: YYYY-MM-DD
        year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
    else:
        # Format: DD-MM-YYYY
        day, month, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
    
    time_parts = birth_time.split(':')
    hour = int(time_parts[0]) + int(time_parts[1]) / 60.0
    
    # Calculate Julian Day using Swiss Ephemeris
    jd = swe.julday(year, month, day, hour)
    
    # Calculate planet positions using Swiss Ephemeris
    planets = calculate_planet_positions_swe(jd)
    
    # Calculate houses using Swiss Ephemeris (Placidus)
    houses = calculate_houses_swe(jd, latitude, longitude)
    
    # Get Ascendant from houses
    ascendant = houses.get("Ascendant", {}).get("longitude", 0)
    asc_sign, asc_deg = get_zodiac_sign(ascendant)
    
    # Get Sun sign and Moon sign
    sun_sign = planets["Sun"]["sign"]
    moon_sign = planets["Moon"]["sign"]
    
    # Calculate aspects between planets
    aspects = calculate_aspects(planets)
    
    # Get MC (Midheaven)
    mc = houses.get("MC", {})
    
    return {
        "ascendant": {
            "degree": round(ascendant, 4), 
            "sign": asc_sign, 
            "degree_in_sign": round(asc_deg, 2)
        },
        "midheaven": mc,
        "sun_sign": sun_sign,
        "moon_sign": moon_sign,
        "planets": planets,
        "houses": houses,
        "aspects": aspects,
        "julian_day": round(jd, 6),
        "calculation_method": "Swiss Ephemeris (Placidus)",
        "accuracy": "±1 arc-second"
    }

# ============== Geocoding Helper ==============

# Simple city coordinates database
CITY_COORDS = {
    "istanbul": (41.0082, 28.9784),
    "ankara": (39.9334, 32.8597),
    "izmir": (38.4237, 27.1428),
    "bursa": (40.1885, 29.0610),
    "antalya": (36.8969, 30.7133),
    "london": (51.5074, -0.1278),
    "new york": (40.7128, -74.0060),
    "paris": (48.8566, 2.3522),
    "berlin": (52.5200, 13.4050),
    "tokyo": (35.6762, 139.6503),
    "los angeles": (34.0522, -118.2437),
    "chicago": (41.8781, -87.6298),
    "moscow": (55.7558, 37.6173),
    "dubai": (25.2048, 55.2708),
    "sydney": (-33.8688, 151.2093),
}

def get_city_coordinates(city: str) -> tuple:
    """Get coordinates for a city"""
    city_lower = city.lower().strip()
    for city_name, coords in CITY_COORDS.items():
        if city_name in city_lower or city_lower in city_name:
            return coords
    # Default to Istanbul if not found
    return (41.0082, 28.9784)

# ============== Helper Functions ==============

def get_user_greeting(name: str, gender: str = None) -> str:
    """Kullanıcının ismi ve cinsiyetine göre hitap oluştur"""
    # İsimden sadece adı al (soyad hariç)
    first_name = name.split()[0] if name else "Değerli Misafir"
    
    if gender == 'male':
        return f"Sevgili {first_name} Bey"
    elif gender == 'female':
        return f"Sevgili {first_name} Hanım"
    else:
        return f"Sevgili {first_name}"

async def get_user_info(user_id: str) -> dict:
    """Kullanıcı bilgilerini getir"""
    user = await db.users.find_one({"id": user_id})
    if user:
        return {
            "name": user.get("name", "Misafir"),
            "gender": user.get("gender", None),
            "greeting": get_user_greeting(user.get("name", "Misafir"), user.get("gender"))
        }
    return {"name": "Misafir", "gender": None, "greeting": "Sevgili Misafir"}

# ============== Credit System ==============

async def check_user_credits(user_id: str, cost: int = 1) -> dict:
    user = await db.users.find_one({"id": user_id})
    
    # Guest kullanıcılar için otomatik kullanıcı oluştur
    if not user and user_id.startswith('guest-'):
        guest_user = {
            "id": user_id,
            "name": "Misafir",
            "email": f"{user_id}@guest.papatyafali.com",
            "credits": 10,  # 10 başlangıç kredisi
            "free_fortunes_today": 0,
            "is_premium": False,
            "language": "tr",
            "created_at": datetime.utcnow()
        }
        await db.users.insert_one(guest_user)
        user = guest_user
    
    # Normal kullanıcı yoksa da oluştur
    if not user:
        new_user = {
            "id": user_id,
            "name": "Kullanıcı",
            "email": f"{user_id}@user.papatyafali.com",
            "credits": 10,  # 10 başlangıç kredisi
            "free_fortunes_today": 0,
            "is_premium": False,
            "language": "tr",
            "created_at": datetime.utcnow()
        }
        await db.users.insert_one(new_user)
        user = new_user
    
    now = datetime.utcnow()
    last_free_date = user.get('last_free_date')
    free_fortunes_today = user.get('free_fortunes_today', 0)
    
    # Yeni gün mü kontrol et
    if last_free_date is None or last_free_date.date() < now.date():
        # Yeni gün, ücretsiz hakları sıfırla
        await db.users.update_one(
            {"id": user_id}, 
            {"$set": {"free_fortunes_today": 0, "last_free_date": now}}
        )
        free_fortunes_today = 0
    
    # Premium users have unlimited access
    if user.get('is_premium', False):
        return {"can_use": True, "is_free": True, "credits": user.get('credits', 0), "is_premium": True}
    
    # Günde 1 ücretsiz fal hakkı
    FREE_DAILY_LIMIT = 1
    if free_fortunes_today < FREE_DAILY_LIMIT:
        return {"can_use": True, "is_free": True, "credits": user.get('credits', 0), "is_premium": False, "free_remaining": FREE_DAILY_LIMIT - free_fortunes_today}
    
    # Kredi kontrolü
    if user.get('credits', 0) >= cost:
        return {"can_use": True, "is_free": False, "credits": user.get('credits', 0), "is_premium": False}
    
    return {"can_use": False, "is_free": False, "credits": user.get('credits', 0), "is_premium": False}

async def deduct_credits(user_id: str, cost: int = 1, is_free: bool = False):
    if is_free:
        # Ücretsiz kullanım sayısını artır
        await db.users.update_one(
            {"id": user_id}, 
            {"$inc": {"free_fortunes_today": 1}, "$set": {"last_free_date": datetime.utcnow()}}
        )
    else:
        await db.users.update_one({"id": user_id}, {"$inc": {"credits": -cost}})

# ============== User Endpoints ==============

@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        return User(**existing)
    
    user = User(**user_data.dict())
    await db.users.insert_one(user.dict())
    return user

@api_router.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.put("/users/{user_id}")
async def update_user(user_id: str, user_data: dict):
    await db.users.update_one({"id": user_id}, {"$set": user_data})
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.get("/users/{user_id}/credits")
async def get_user_credits(user_id: str):
    return await check_user_credits(user_id)

# ============== Birth Chart / Yıldızname ==============

@api_router.post("/fortune/birthchart")
async def get_birth_chart(request: BirthChartRequest):
    # Guest user support - skip credit check for guest users
    is_guest = request.user_id.startswith("guest-")
    credit_check = {"credits": 0, "is_free": True, "can_use": True}
    
    if not is_guest:
        credit_check = await check_user_credits(request.user_id)
        if not credit_check["can_use"]:
            raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Get coordinates
    lat, lon = get_city_coordinates(request.birth_place)
    
    # Calculate natal chart
    natal_chart = await calculate_natal_chart(request.birth_date, request.birth_time, lat, lon)
    
    # Save to user profile (only for registered users)
    if not is_guest:
        await db.users.update_one(
            {"id": request.user_id},
            {"$set": {
                "birth_date": request.birth_date,
                "birth_time": request.birth_time,
                "birth_place": request.birth_place,
                "birth_lat": lat,
                "birth_lon": lon,
                "natal_chart": natal_chart
            }}
        )
    
    # Generate AI interpretation
    lang = request.language
    sun_sign = natal_chart["sun_sign"]
    moon_sign = natal_chart["moon_sign"]
    asc_sign = natal_chart["ascendant"]["sign"]
    
    # Get detailed planet info
    planets = natal_chart["planets"]
    planets_summary = ", ".join([f"{p}: {d['sign']}" + (" (R)" if d.get('retrograde') else "") for p, d in planets.items() if p not in ["North_Node"]])
    
    # Get aspect info
    aspects = natal_chart.get("aspects", [])
    major_aspects = [a for a in aspects if a["aspect"] in ["Conjunction", "Opposition", "Trine"]][:5]
    aspects_summary = ", ".join([f"{a['planet1']}-{a['planet2']} {a['aspect']}" for a in major_aspects])
    
    # Check for retrogrades
    retrogrades = [p for p, d in planets.items() if d.get('retrograde')]
    
    # 3 Katmanlı Prompt Sistemi
    mood = getattr(request, 'mood', 'neutral') or 'neutral'
    layered_prompt, prompt_metadata = get_layered_prompt(
        language=lang,
        mood=mood,
        interest="destiny",  # Doğum haritası kader ile ilgili
        fortune_type="birthchart",
        use_best_of_three=True
    )
    
    if lang == "tr":
        system_message = f"""Sen deneyimli ve sezgileri çok güçlü bir astroloğsun. Swiss Ephemeris kullanarak hassas hesaplamalar yapıyorsun.
        Yorumların samimi, sıcak ve anlaşılır olsun. Teknik terimler yerine günlük dil kullan.
        İnsanların hayatlarına dokunan, onlara ilham veren yorumlar yap.
        Kısa paragraflarla, akıcı ve etkileyici bir şekilde yaz.
        "Mısır" kelimesini kullanma, bunun yerine evrensel bir mistik dil kullan.
        
{layered_prompt}"""
        
        retrograde_info = f"\n- Geri Giden Gezegenler: {', '.join(retrogrades)}" if retrogrades else ""
        
        prompt = f"""🌟 DOĞUM HARİTASI ANALİZİ (Swiss Ephemeris ile Hesaplandı)

📊 TEMEL BİLGİLER:
- İsim: {request.name}
- Anne Adı: {request.mother_name or 'Belirtilmedi'}
- Güneş Burcu: {ZODIAC_SIGNS[sun_sign]['tr']} ({planets['Sun']['degree']:.1f}°)
- Ay Burcu: {ZODIAC_SIGNS[moon_sign]['tr']} ({planets['Moon']['degree']:.1f}°)
- Yükselen Burç: {ZODIAC_SIGNS[asc_sign]['tr']} ({natal_chart['ascendant']['degree_in_sign']:.1f}°){retrograde_info}

🪐 GEZEGEN POZİSYONLARI:
{planets_summary}

⚡ ÖNEMLİ AÇILAR:
{aspects_summary if aspects_summary else "Standart açı konfigürasyonu"}

Bu kişi için DERİN ve KAPSAMLI bir yıldızname yorumu yaz. Kişinin adı "{request.name}"{f" ve annesi {request.mother_name}" if request.mother_name else ""}. Şu konulara değin:

✨ **KİM OLDUĞUN** - Güneş, Ay ve Yükselen üçlüsünün senin karakterine etkisi
💫 **GİZLİ GÜCÜN** - Ay burcunun ve gezegen açılarının ortaya çıkardığı gizli yeteneklerin
❤️ **AŞK HAYATIN** - Venüs ve Mars'ın ilişkilerdeki etkisi
🎯 **KARİYER YOLUN** - 10. ev (MC) ve Satürn'ün kariyer üzerindeki etkisi
⚡ **DİKKAT ET** - Geri giden gezegenler ve zorlayıcı açıların uyarıları
🌟 **ÖNÜMÜZDE NE VAR** - Jüpiter ve transitlerin yakın gelecek etkisi

Samimi, sıcak ve umut dolu bir dil kullan. Kişinin adını kullanarak hitap et. Her burç ve gezegen yorumunu kişiselleştir."""
    else:
        system_message = """You are an experienced astrologer with strong intuition. You use Swiss Ephemeris for precise calculations.
        Your interpretations should be warm, friendly and easy to understand. Use everyday language instead of technical terms.
        Make interpretations that touch people's lives and inspire them.
        Write in short paragraphs, fluently and impressively."""
        
        retrograde_info = f"\n- Retrograde Planets: {', '.join(retrogrades)}" if retrogrades else ""
        
        prompt = f"""🌟 BIRTH CHART ANALYSIS (Calculated with Swiss Ephemeris)

📊 CORE DATA:
- Name: {request.name}
- Sun Sign: {sun_sign} ({planets['Sun']['degree']:.1f}°)
- Moon Sign: {moon_sign} ({planets['Moon']['degree']:.1f}°)
- Rising Sign: {asc_sign} ({natal_chart['ascendant']['degree_in_sign']:.1f}°){retrograde_info}

🪐 PLANET POSITIONS:
{planets_summary}

⚡ MAJOR ASPECTS:
{aspects_summary if aspects_summary else "Standard aspect configuration"}

Write a DEEP and COMPREHENSIVE natal chart reading for this person. Cover these topics:

✨ **WHO YOU ARE** - How your Sun, Moon, and Rising trio shapes your character
💫 **YOUR HIDDEN POWER** - Hidden talents revealed by your Moon sign and planetary aspects
❤️ **YOUR LOVE LIFE** - Venus and Mars influence on relationships
🎯 **YOUR CAREER PATH** - 10th house (MC) and Saturn's career influence
⚡ **PAY ATTENTION** - Warnings from retrograde planets and challenging aspects
🌟 **WHAT'S AHEAD** - Jupiter and transit effects on the near future

Use a warm, friendly and hopeful tone. Personalize each sign and planet interpretation."""
    
    interpretation = await get_ai_response(prompt, system_message)
    
    # Save fortune
    fortune = Fortune(
        user_id=request.user_id,
        fortune_type="birthchart",
        input_data=f"{request.birth_date} {request.birth_time} {request.birth_place}",
        result=interpretation
    )
    # Save fortune (only for registered users)
    if not is_guest:
        await db.fortunes.insert_one(fortune.dict())
        await deduct_credits(request.user_id, 1, credit_check["is_free"])
        credits_remaining = credit_check["credits"] - (0 if credit_check["is_free"] else 1)
    else:
        credits_remaining = 0
    
    return {
        "natal_chart": natal_chart,
        "interpretation": interpretation,
        "fortune": fortune.dict(),
        "credits_remaining": credits_remaining
    }

# ============== Coffee Fortune ==============

@api_router.post("/fortune/coffee")
async def coffee_fortune(request: CoffeeFortuneRequest):
    credit_check = await check_user_credits(request.user_id)
    if not credit_check["can_use"]:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Kullanıcı bilgilerini al
    user_info = await get_user_info(request.user_id)
    user_greeting = user_info["greeting"]
    
    lang = request.language
    mood = getattr(request, 'mood', 'neutral') or 'neutral'
    
    # 3 Katmanlı Prompt Sistemi
    layered_prompt, prompt_metadata = get_layered_prompt(
        language=lang,
        mood=mood,
        interest="general",
        fortune_type="coffee",
        use_best_of_three=True
    )
    
    # Use production prompts + layered system
    system_message = f"""{COFFEE_SYSTEM_PROMPT[lang]}

{layered_prompt}"""
    
    if lang == "tr":
        prompt = f"""Bu kahve fincanı için etkileyici bir fal yorumu yaz.
Danışan: {user_greeting}

Şu konulara değin:
☕ FİNCAN YORUMU - Genel izlenimler ve hissettiklerin
💕 AŞK - Duygusal hayatta neler var, neler geliyor
💼 İŞ & PARA - Kariyer ve maddi durum hakkında
✨ ŞANS - Yaklaşan güzel gelişmeler ve fırsatlar
💡 TAVSİYE - Dikkat etmen gereken şeyler

Danışana "{user_greeting}" diye hitap et.
Kısa paragraflar tercih et.
Her bölümde motivasyon ver.
Sonunda umut dolu bir kapanış yap."""
    else:
        prompt = """Write an impressive fortune reading for this coffee cup.

Briefly cover these topics:
☕ CUP READING - General impressions
💕 LOVE - What's happening emotionally
💼 WORK & MONEY - Career and finances
✨ LUCK - Upcoming good developments
💡 ADVICE - Things to pay attention to

Use short paragraphs. Write in a warm and hopeful tone. As if reading fortune for a friend."""
    
    # Use Vision API for image analysis
    try:
        result = await get_ai_response_with_image(prompt, system_message, request.image_base64)
    except Exception as e:
        logger.error(f"Coffee Fortune Vision Error: {str(e)}")
        # Fallback to text-only
        result = await get_ai_response(prompt, system_message)
    
    fortune = Fortune(
        user_id=request.user_id,
        fortune_type="coffee",
        input_data=request.image_base64[:100] + "...",
        result=result
    )
    await db.fortunes.insert_one(fortune.dict())
    await deduct_credits(request.user_id, 1, credit_check["is_free"])
    
    return {
        "fortune": fortune.dict(), 
        "credits_remaining": credit_check["credits"] - (0 if credit_check["is_free"] else 1),
        "prompt_style": prompt_metadata.get("style", "emotional"),
        "mood": prompt_metadata.get("mood", "neutral")
    }

# ============== Tarot ==============

@api_router.post("/fortune/tarot")
async def tarot_reading(request: TarotRequest):
    credit_check = await check_user_credits(request.user_id)
    if not credit_check["can_use"]:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Kullanıcı bilgilerini al (isim ve cinsiyet için)
    user_info = await get_user_info(request.user_id)
    user_greeting = user_info["greeting"]
    
    # Determine number of cards based on spread type
    num_cards = {"single": 1, "three_card": 3, "celtic_cross": 10, "love_spread": 5, "career_spread": 5}.get(request.spread_type, 3)
    
    # Select random cards from the full 78-card deck
    selected_card_data = random.sample(ALL_TAROT_CARDS, num_cards)
    reversed_cards = [random.choice([True, False]) for _ in selected_card_data]
    
    # Build detailed card information
    cards_info = []
    for i, (card, is_reversed) in enumerate(zip(selected_card_data, reversed_cards)):
        card_info = {
            "name": card["name"],
            "name_tr": card.get("name_tr", card["name"]),
            "reversed": is_reversed,
            "position": i + 1,
            "meaning": card["reversed" if is_reversed else "upright"],
            "keywords_tr": card.get("keywords_tr", []),
            "suit": card.get("suit", "Major Arcana"),
            "element": card.get("element", ""),
            "is_major": card["id"] < 22  # First 22 cards are Major Arcana
        }
        cards_info.append(card_info)
    
    # Check for special combinations
    combinations = check_combinations(selected_card_data, request.language)
    
    # Build prompt with detailed card meanings
    lang = request.language
    category = request.category or "general"
    question_text = f"Soru: {request.question}" if request.question else "Genel okuma"
    
    cards_text = "\n".join([
        f"- {c['name_tr'] if lang == 'tr' else c['name']} {'(TERS)' if c['reversed'] else ''}: {c['meaning']}"
        for c in cards_info
    ])
    
    major_count = sum(1 for c in cards_info if c['is_major'])
    suits_present = list(set(c['suit'] for c in cards_info if c['suit'] != 'Major Arcana'))
    
    # Combination insights
    combination_text = ""
    if combinations:
        combination_text = "\n\nÖZEL KOMBİNASYONLAR:\n" + "\n".join([
            f"- {comb['category'].upper()}: {comb['meaning']}"
            for comb in combinations
        ])
    
    # Get personalization context for user
    personalization = await get_user_personalization_context(request.user_id)
    
    # 3 Katmanlı Prompt Sistemi
    mood = getattr(request, 'mood', 'neutral') or 'neutral'
    layered_prompt, prompt_metadata = get_layered_prompt(
        language=lang,
        mood=mood,
        interest=detect_interest(request.question) if request.question else category,
        fortune_type="tarot",
        use_best_of_three=True
    )
    
    if lang == "tr":
        # Use production tarot prompt + layered system
        base_system = f"""{TAROT_SYSTEM_PROMPT["tr"]}

{layered_prompt}"""
        
        if request.story_mode:
            system_message = f"""{base_system}

ÖZEL MOD: HİKAYE ANLATICI
Bu okumada kartları bir hikaye gibi anlat.
Ana karakter danışan olsun.
Her kart hikayenin bir bölümü olsun.
Mistik ve büyüleyici bir dil kullan.
Sonunda güçlü bir mesaj ver."""
            prompt = f"""HİKAYE MODU - TAROT AÇILIMI
Kart Sayısı: {num_cards}
Açılım: {request.spread_type}
Kategori: {category}
{question_text}
{personalization}

ÇIKAN KARTLAR:
{cards_text}
{combination_text}

KART ANALİZİ:
- Major Arcana sayısı: {major_count} (Yüksekse: Büyük yaşam temaları)
- Mevcut seriler: {', '.join(suits_present) if suits_present else 'Yok'}

Bu kartlarla etkileyici bir hikaye anlat. Danışanı ana karakter yap.
Her kartı hikayenin bir bölümü olarak işle. Sonunda güçlü bir mesaj ver.
Hikaye en az 400 kelime olsun ve büyüleyici olsun."""
        else:
            system_message = base_system
            prompt = f"""TAROT AÇILIMI - 78 KARTLIK TAM DESTE
Danışan: {user_greeting}
Açılım Tipi: {request.spread_type}
Kategori: {category}
{question_text}
{personalization}

ÇIKAN KARTLAR:
{cards_text}
{combination_text}

KART ANALİZİ:
- Major Arcana sayısı: {major_count}/22 (Yüksekse: Önemli yaşam dönüşümleri)
- Mevcut seriler: {', '.join(suits_present) if suits_present else 'Yalnızca Major Arcana'}
  * Değnekler (Ateş): Tutku, enerji, yaratıcılık
  * Kupalar (Su): Duygular, ilişkiler, sezgi
  * Kılıçlar (Hava): Zihin, iletişim, kararlar
  * Tılsımlar (Toprak): Maddi konular, kariyer, para

Her kart için 2-3 cümle yorum yap, sonra tüm kartların birlikte ne anlattığını açıkla.
Eğer özel bir kombinasyon varsa bunu vurgula.
Danışana "{user_greeting}" diye hitap et. Samimi ve umut dolu bir dil kullan."""
    else:
        if request.story_mode:
            system_message = """You are an experienced tarot master and a captivating storyteller.
            When reading cards, create an engaging story like telling a fairy tale.
            Let the querent be the main character. Let the cards tell chapters of their story.
            Use mystical, enchanting but understandable language. Use metaphors and symbols.
            At the end, give a clear message and advice."""
            prompt = f"""STORY MODE - TAROT READING
Cards: {num_cards}
Spread: {request.spread_type}
Category: {category}
Question: {request.question or 'General reading'}

DRAWN CARDS:
{cards_text}
{combination_text}

Tell an engaging story with these cards. Make the querent the main character.
Process each card as a chapter of the story. End with a powerful message."""
        else:
            system_message = """You are an experienced tarot master using the full 78-card deck.
            You know the deep meaning of each card. You are expert at reading cards together.
            Use warm, friendly and understandable language. Prefer everyday language over complex symbolism.
            Pay special attention to card combinations - cards drawn together carry extra meaning."""
            prompt = f"""TAROT READING - FULL 78-CARD DECK
Spread Type: {request.spread_type}
Category: {category}
Question: {request.question or 'General reading'}

DRAWN CARDS:
{cards_text}
{combination_text}

CARD ANALYSIS:
- Major Arcana count: {major_count}/22 (High = Major life transformations)
- Suits present: {', '.join(suits_present) if suits_present else 'Only Major Arcana'}

Give 2-3 sentences for each card, then explain what all cards tell together.
Highlight any special combinations. Use warm and hopeful language."""
    
    result = await get_ai_response(prompt, system_message)
    
    # Get user's past readings for personalization context (store for future)
    await db.reading_history.insert_one({
        "user_id": request.user_id,
        "type": "tarot",
        "cards": [c["name"] for c in cards_info],
        "category": category,
        "question": request.question,
        "created_at": datetime.utcnow()
    })
    
    fortune = Fortune(
        user_id=request.user_id,
        fortune_type="tarot",
        input_data=", ".join([c["name"] for c in cards_info]),
        result=result
    )
    await db.fortunes.insert_one(fortune.dict())
    await deduct_credits(request.user_id, 1, credit_check["is_free"])
    
    return {
        "cards": cards_info,
        "combinations": combinations,
        "major_arcana_count": major_count,
        "story_mode": request.story_mode,
        "fortune": fortune.dict(),
        "interpretation": result,  # AI interpretation text
        "credits_remaining": credit_check["credits"] - (0 if credit_check["is_free"] else 1)
    }

# ============== Daily Horoscope ==============

@api_router.post("/fortune/horoscope")
async def daily_horoscope(request: HoroscopeRequest):
    credit_check = await check_user_credits(request.user_id)
    if not credit_check["can_use"]:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    lang = request.language
    today = datetime.utcnow().strftime("%d %B %Y")
    zodiac_info = ZODIAC_SIGNS.get(request.zodiac_sign, {})
    zodiac_tr = zodiac_info.get('tr', request.zodiac_sign)
    element = zodiac_info.get('element', 'Unknown')
    ruling_planet = zodiac_info.get('ruling_planet', 'Unknown')
    
    # 3 Katmanlı Prompt Sistemi
    mood = getattr(request, 'mood', 'neutral') or 'neutral'
    layered_prompt, prompt_metadata = get_layered_prompt(
        language=lang,
        mood=mood,
        interest="general",
        fortune_type="horoscope",
        use_best_of_three=True
    )
    
    if lang == "tr":
        system_message = f"""Sen deneyimli ve sezgileri güçlü bir astroloğsun.
        Günlük burç yorumlarını samimi, sıcak ve anlaşılır bir dille yaz.
        Pozitif, motive edici ve yol gösterici ol. Kısa paragraflar kullan.
        "Mısır" kelimesini kullanma.
        
{layered_prompt}"""
        prompt = f"""Bugün {today}. {zodiac_tr} burcu için günlük yorum yaz.

Şu konulara kısaca değin:
☀️ GÜNÜN ENERJİSİ - Bugün nasıl hissedeceksin
💕 AŞK - Duygusal hayatta neler var
💼 İŞ & KARİYER - İş hayatında fırsatlar
💰 PARA - Maddi konular
✨ TAVSİYE - Bugün dikkat etmen gerekenler

🔢 Şanslı sayılar: (3 adet)
🎨 Şanslı renk: (1 renk)

Samimi ve umut dolu bir dil kullan."""
    else:
        system_message = f"""You are an experienced astrologer with strong intuition.
        Write daily horoscope interpretations in a warm, friendly and easy-to-understand way.
        Be positive, motivating and guiding. Use short paragraphs.
        
{layered_prompt}"""
        prompt = f"""Today is {today}. Write a daily horoscope for {request.zodiac_sign}.

Briefly cover these topics:
☀️ TODAY'S ENERGY - How you'll feel today
💕 LOVE - What's happening emotionally
💼 WORK & CAREER - Opportunities at work
💰 MONEY - Financial matters
✨ ADVICE - What to pay attention to today

🔢 Lucky numbers: (3 numbers)
🎨 Lucky color: (1 color)

Use a warm and hopeful tone."""
    
    result = await get_ai_response(prompt, system_message)
    
    fortune = Fortune(
        user_id=request.user_id,
        fortune_type="daily_horoscope",
        input_data=request.zodiac_sign,
        result=result
    )
    await db.fortunes.insert_one(fortune.dict())
    await deduct_credits(request.user_id, 1, credit_check["is_free"])
    
    return {
        "fortune": fortune.dict(), 
        "credits_remaining": credit_check["credits"] - (0 if credit_check["is_free"] else 1),
        "prompt_style": prompt_metadata.get("style", "emotional"),
        "mood": prompt_metadata.get("mood", "neutral")
    }

# ============== Dream Interpretation ==============

@api_router.post("/fortune/dream")
async def dream_interpretation(request: DreamRequest):
    credit_check = await check_user_credits(request.user_id)
    if not credit_check["can_use"]:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    lang = request.language
    
    # 3 Katmanlı Prompt Sistemi
    mood = getattr(request, 'mood', 'neutral') or 'neutral'
    layered_prompt, prompt_metadata = get_layered_prompt(
        language=lang,
        mood=mood,
        interest="destiny",  # Rüyalar genellikle kader/gelecek ile ilgili
        fortune_type="dream",
        use_best_of_three=True
    )
    
    if lang == "tr":
        system_message = f"""Sen deneyimli bir rüya yorumcususun. Rüyaları hem psikolojik hem sembolik açıdan yorumlarsın.
        Samimi, sıcak ve anlaşılır bir dil kullan. Karmaşık teoriler yerine günlük dil tercih et.
        "Mısır" kelimesini kullanma. Kısa ve etkileyici yaz.
        
{layered_prompt}"""
        prompt = f"""Bu rüyayı yorumla: {request.dream_description}

Şu konulara kısaca değin:
🌙 RÜYA NE ANLATIYOR - Genel yorum
💭 BİLİNÇALTI MESAJI - Psikolojik anlam
✨ GELECEK İPUÇLARI - Ne işaret ediyor olabilir
💡 TAVSİYE - Dikkat etmen gerekenler

Samimi ve destekleyici bir dil kullan. Sanki karşındaki arkadaşına rüya yorumluyormuş gibi yaz."""
    else:
        system_message = f"""You are an experienced dream interpreter. You interpret dreams from both psychological and symbolic perspectives.
        Use a warm, friendly and easy-to-understand language. Prefer everyday language over complex theories.
        Write short and impressively.
        
{layered_prompt}"""
        prompt = f"""Interpret this dream: {request.dream_description}

Briefly cover these topics:
🌙 WHAT THE DREAM TELLS - General interpretation
💭 SUBCONSCIOUS MESSAGE - Psychological meaning
✨ FUTURE HINTS - What it might indicate
💡 ADVICE - Things to pay attention to

Use a warm and supportive tone. Write as if interpreting a dream for a friend."""
    
    result = await get_ai_response(prompt, system_message)
    
    fortune = Fortune(
        user_id=request.user_id,
        fortune_type="dream",
        input_data=request.dream_description[:200],
        result=result
    )
    await db.fortunes.insert_one(fortune.dict())
    await deduct_credits(request.user_id, 1, credit_check["is_free"])
    
    return {
        "fortune": fortune.dict(), 
        "credits_remaining": credit_check["credits"] - (0 if credit_check["is_free"] else 1),
        "prompt_style": prompt_metadata.get("style", "emotional"),
        "mood": prompt_metadata.get("mood", "neutral")
    }

# ============== Chat ==============

@api_router.post("/chat")
async def chat_with_fortune_teller(request: ChatRequest):
    credit_check = await check_user_credits(request.user_id)
    if not credit_check["can_use"]:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    history = await db.chat_messages.find({"session_id": request.session_id}).sort("created_at", 1).to_list(50)
    history_text = "\n".join([f"{'Kullanıcı' if m['role'] == 'user' else 'Kahin'}: {m['content']}" for m in history[-10:]])
    
    lang = request.language
    
    # 3 Katmanlı Prompt Sistemi
    mood = getattr(request, 'mood', 'neutral') or 'neutral'
    layered_prompt, prompt_metadata = get_layered_prompt(
        language=lang,
        mood=mood,
        question=request.message,
        fortune_type="chat",
        use_best_of_three=True
    )
    
    if lang == "tr":
        system_message = f"""Sen sezgileri güçlü, bilge bir kahinsin. İnsanlara yardım etmeyi seven, samimi birisin.
        Sohbet ederken sıcak, samimi ve anlaşılır bir dil kullan. Karmaşık cümleler kurma.
        Kısa ve etkileyici cevaplar ver (2-3 paragraf). Kullanıcıya "canım" veya "güzel insan" diye hitap edebilirsin.
        
{layered_prompt}"""
        prompt = f"""Sohbet geçmişi:
{history_text}

Kullanıcı: {request.message}

Samimi ve yardımsever bir kahin olarak yanıtla:"""
    else:
        system_message = f"""You are a wise oracle with strong intuition. You love helping people and are friendly.
        Use a warm, friendly and easy-to-understand language. Don't make complex sentences.
        Give short and impressive answers (2-3 paragraphs). You can address the user warmly.
        
{layered_prompt}"""
        prompt = f"""Chat history:
{history_text}

User: {request.message}

Respond as a warm and helpful oracle:"""
    
    result = await get_ai_response(prompt, system_message)
    
    user_msg = ChatMessage(session_id=request.session_id, user_id=request.user_id, role="user", content=request.message)
    await db.chat_messages.insert_one(user_msg.dict())
    
    assistant_msg = ChatMessage(session_id=request.session_id, user_id=request.user_id, role="assistant", content=result)
    await db.chat_messages.insert_one(assistant_msg.dict())
    
    await deduct_credits(request.user_id, 1, credit_check["is_free"])
    
    return {
        "response": result,
        "session_id": request.session_id,
        "credits_remaining": credit_check["credits"] - (0 if credit_check["is_free"] else 1),
        "prompt_style": prompt_metadata.get("style", "emotional"),
        "mood": prompt_metadata.get("mood", "neutral")
    }

# ============== AI Fortune Chat ==============

@api_router.post("/fortune/ai-chat")
async def ai_fortune_chat(request: AIFortuneChatRequest):
    """AI-powered fortune chat with 3-layer prompt system"""
    credit_check = await check_user_credits(request.user_id)
    if not credit_check["can_use"]:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Kullanıcı bilgilerini al
    user_info = await get_user_info(request.user_id)
    user_greeting = user_info["greeting"]
    
    # Kullanıcı geçmişini al (interest detection için)
    user_history = await db.ai_chat_history.find(
        {"user_id": request.user_id}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    # Category'yi interest'e map et (fallback için)
    category_to_interest = {
        "Aşk": "love",
        "Kariyer": "career", 
        "Para": "money",
        "Rüya": "destiny",
        "Gelecek": "destiny",
        "Genel": "general",
        "Sağlık": "health",
        "Aile": "family"
    }
    
    # Önce sorudan otomatik tespit et, sonra category'den fallback
    detected_interest = detect_interest(request.question, user_history)
    if detected_interest == "general" and request.category != "Genel":
        # Eğer otomatik tespit general döndürdü ama category spesifikse, category'yi kullan
        detected_interest = category_to_interest.get(request.category, detected_interest)
    
    # 3 Katmanlı Prompt Oluştur (3 versiyon üret, en iyisini seç)
    layered_prompt, prompt_metadata = get_layered_prompt(
        language=request.language,
        mood=request.mood,
        interest=detected_interest,
        question=request.question,
        user_history=user_history,
        fortune_type="ai_chat",
        use_best_of_three=True
    )
    
    # System message'a user greeting ekle
    system_message = f"""{layered_prompt}

---

🎭 EK BAĞLAM:
- Danışana "{user_greeting}" diye hitap et
- Kullanıcının sorusu: {request.question}
- Seçilen konu: {request.category}
- Ruh hali: {request.mood}
- Seçilen stil: {prompt_metadata.get('style', 'emotional')}

⏰ ZAMAN TAHMİNLERİ (Her cevapta mutlaka kullan):
- "Çok yakında..."
- "10-15 gün içinde..."
- "2 hafta sonra..."
- "Bu ayın sonuna doğru..."

🚫 KESİNLİKLE YAPMA:
- "Ben bir yapay zekayım" deme
- Teknik konuşma yapma
- Boş/klişe cümleler kullanma
- Korkutucu tahminler yapma"""

    prompt = f"""Danışan: {user_greeting}
Kullanıcının Sorusu: {request.question}

Sen NeferTiti'sin - kadim bilge. Yukarıdaki soruya mistik bir kahin olarak cevap ver.

Yorumun şu yapıda olsun:
1. Çarpıcı giriş ("Sevgili ruhum..." ile)
2. Duygusal analiz (kullanıcının iç dünyasına dokun)
3. Şaşırtıcı detay (geçmişe ima)
4. Gelecek tahmini (zaman ver: "2 hafta içinde...", "bu ay sonunda...")
5. Güçlü kapanış (motive eden)

Danışana "{user_greeting}" diye hitap et. 4-6 cümle yaz, akıcı ve hikaye gibi."""

    result = await get_ai_response(prompt, system_message)
    
    # Save to history with metadata
    await db.ai_chat_history.insert_one({
        "user_id": request.user_id,
        "question": request.question,
        "category": request.category,
        "mood": request.mood,
        "response": result,
        "prompt_metadata": prompt_metadata,
        "created_at": datetime.utcnow()
    })
    
    await deduct_credits(request.user_id, 1, credit_check["is_free"])
    
    return {
        "response": result,
        "category": request.category,
        "mood": request.mood,
        "prompt_style": prompt_metadata.get("style"),
        "detected_interest": prompt_metadata.get("interest"),
        "credits_remaining": credit_check["credits"] - (0 if credit_check["is_free"] else 1)
    }

# ============== Palmistry (El Falı) ==============

def get_tensorflow_analysis_text(tf_analysis: Optional[Dict]) -> str:
    """TensorFlow analiz verilerini okunabilir metne çevir"""
    if not tf_analysis:
        return ""
    
    translations = {
        'handShape': {
            'earth': 'Toprak Eli (pratik, güvenilir, sabırlı)',
            'air': 'Hava Eli (iletişimci, analitik, meraklı)',
            'water': 'Su Eli (duygusal, sezgisel, empatik)',
            'fire': 'Ateş Eli (tutkulu, enerjik, lider)'
        },
        'length': {'short': 'kısa', 'medium': 'orta', 'long': 'uzun'},
        'depth': {'faint': 'soluk', 'medium': 'orta derinlikte', 'deep': 'derin'},
        'curvature': {'straight': 'düz', 'curved': 'kavisli', 'very_curved': 'çok kavisli'},
        'position': {'high': 'yüksek', 'middle': 'orta', 'low': 'alçak'},
        'clarity': {'broken': 'kesik kesik', 'clear': 'net', 'very_clear': 'çok net'},
        'slope': {'upward': 'yukarı eğimli', 'straight': 'düz', 'downward': 'aşağı eğimli'},
        'connection': {'separate': 'ayrık', 'connected': 'bağlı', 'overlapping': 'örtüşen'},
        'strength': {'weak': 'zayıf', 'medium': 'orta', 'strong': 'güçlü'},
        'direction': {'straight': 'düz', 'curved_left': 'sola kavisli', 'curved_right': 'sağa kavisli'}
    }
    
    lines = ["🤖 TensorFlow El Analizi Sonuçları:"]
    
    # Hand shape
    if 'handShape' in tf_analysis and tf_analysis['handShape']:
        shape = tf_analysis['handShape']
        lines.append(f"• El Tipi: {translations['handShape'].get(shape, shape)}")
    
    # Life Line
    if 'lifeLine' in tf_analysis and tf_analysis['lifeLine']:
        ll = tf_analysis['lifeLine']
        parts = []
        if 'length' in ll: parts.append(translations['length'].get(ll['length'], ll['length']))
        if 'depth' in ll: parts.append(translations['depth'].get(ll['depth'], ll['depth']))
        if 'curvature' in ll: parts.append(translations['curvature'].get(ll['curvature'], ll['curvature']))
        if parts:
            lines.append(f"• Yaşam Çizgisi: {', '.join(parts)}")
    
    # Heart Line
    if 'heartLine' in tf_analysis and tf_analysis['heartLine']:
        hl = tf_analysis['heartLine']
        parts = []
        if 'length' in hl: parts.append(translations['length'].get(hl['length'], hl['length']))
        if 'position' in hl: parts.append(f"{translations['position'].get(hl['position'], hl['position'])} konumlu")
        if 'clarity' in hl: parts.append(translations['clarity'].get(hl['clarity'], hl['clarity']))
        if parts:
            lines.append(f"• Kalp Çizgisi: {', '.join(parts)}")
    
    # Head Line
    if 'headLine' in tf_analysis and tf_analysis['headLine']:
        hdl = tf_analysis['headLine']
        parts = []
        if 'length' in hdl: parts.append(translations['length'].get(hdl['length'], hdl['length']))
        if 'slope' in hdl: parts.append(translations['slope'].get(hdl['slope'], hdl['slope']))
        if 'connection' in hdl: parts.append(f"yaşam çizgisiyle {translations['connection'].get(hdl['connection'], hdl['connection'])}")
        if parts:
            lines.append(f"• Kafa Çizgisi: {', '.join(parts)}")
    
    # Fate Line
    if 'fateLine' in tf_analysis and tf_analysis['fateLine']:
        fl = tf_analysis['fateLine']
        if fl.get('present', False):
            parts = []
            if 'strength' in fl: parts.append(translations['strength'].get(fl['strength'], fl['strength']))
            if 'direction' in fl: parts.append(translations['direction'].get(fl['direction'], fl['direction']))
            lines.append(f"• Kader Çizgisi: mevcut, {', '.join(parts)}")
        else:
            lines.append("• Kader Çizgisi: belirgin değil")
    
    # Finger proportions
    if 'fingerProportions' in tf_analysis and tf_analysis['fingerProportions']:
        fp = tf_analysis['fingerProportions']
        finger_names = {'thumb': 'Başparmak', 'index': 'İşaret', 'middle': 'Orta', 'ring': 'Yüzük', 'pinky': 'Serçe'}
        finger_parts = []
        for finger, name in finger_names.items():
            if finger in fp:
                finger_parts.append(f"{name}: {translations['length'].get(fp[finger], fp[finger])}")
        if finger_parts:
            lines.append(f"• Parmaklar: {', '.join(finger_parts)}")
    
    return '\n'.join(lines)

@api_router.post("/fortune/palmistry")
async def palmistry_reading(request: PalmistryRequest):
    """AI-powered palm reading from hand image with TensorFlow analysis"""
    credit_check = await check_user_credits(request.user_id)
    if not credit_check["can_use"]:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Kullanıcı bilgilerini al
    user_info = await get_user_info(request.user_id)
    user_greeting = user_info["greeting"]
    
    hand_text = "sağ el" if request.hand == "right" else "sol el"
    
    # 3 Katmanlı Prompt Sistemi
    mood = getattr(request, 'mood', 'neutral') or 'neutral'
    layered_prompt, prompt_metadata = get_layered_prompt(
        language="tr",
        mood=mood,
        interest="destiny",  # El falı genellikle kader ile ilgili
        fortune_type="palmistry",
        use_best_of_three=True
    )
    
    # TensorFlow analiz verilerini al
    tf_analysis_text = ""
    if request.tensorflow_analysis:
        tf_data = request.tensorflow_analysis.dict() if hasattr(request.tensorflow_analysis, 'dict') else request.tensorflow_analysis
        tf_analysis_text = get_tensorflow_analysis_text(tf_data)
        logger.info(f"TensorFlow analysis received: {tf_data}")
    
    system_message = f"""🖐️ SEN EFSANE BİR EL FALCISISIN (PALMİST).

Binlerce yıllık el okuma geleneğinin mirasçısısın. Avuç içine baktığında orada yazılı kaderi okuyabilirsin.
Modern TensorFlow yapay zeka ile analiz gücünü birleştiriyorsun.

{layered_prompt}

✨ YORUM TARZIN:
- Sıcak, samimi ve bilge bir kahinsin
- Danışana "{user_greeting}" diye hitap et
- "İçimde güçlü bir his var..." gibi çarpıcı başla
- Elini sanki gerçekten görüyormuş gibi tarif et

🖐️ EL FALI BİLGİSİ:
- Yaşam Çizgisi: Yaşam enerjisi, sağlık (uzunluğu ömür değil, yaşam kalitesi)
- Kalp Çizgisi: Duygusal hayat, aşk, ilişkiler
- Kafa Çizgisi: Zeka, düşünce tarzı, karar verme
- Kader Çizgisi: Kariyer, başarı, hayat yolu
- Güneş Çizgisi: Şöhret, yaratıcılık, mutluluk
- El Tipleri: Toprak (pratik), Hava (düşünceli), Su (duygusal), Ateş (tutkulu)

📝 ULTRA PRO YORUM FORMATI:

🖐️ ELİNE BAKTIM VE...
[Güçlü giriş - "İçimde çok güçlü bir his var..." ile başla]
[Elin genel yapısı ve enerjisi]

📏 YAŞAM ÇİZGİSİ
[Sağlık ve yaşam enerjisi - hikayeleştirerek anlat]
[Şaşırtıcı bir detay ekle]

💕 KALP ÇİZGİSİ  
[Aşk ve duygusal hayat]
["2 hafta içinde..." gibi zaman tahmini ver]

🧠 KAFA ÇİZGİSİ
[Zeka ve düşünce tarzı]
[Kişisel bir ima ekle]

⭐ KADER ÇİZGİSİ
[Kariyer ve başarı]
["Bu ayın sonunda..." gibi tahmin]

✋ PARMAKLAR
[Kişilik özellikleri]

🔮 GİZLİ MESAJ
[Elinin sana fısıldadığı özel mesaj]
["Geçmişte seni yoran bir konu..." gibi ima]

💫 GELECEK TAHMİNİ
[Önümüzdeki dönem için güçlü bir öngörü]
[Akılda kalacak final]

⏰ ZAMAN TAHMİNLERİ (Mutlaka kullan):
- "3 gün içinde..."
- "2 hafta sonra..."
- "Bu ayın sonuna doğru..."

🎯 SECRET BOOST:
- Geçmişten gelen bir enerji ima et
- Tesadüf gibi görünen anlamlı 1 detay ekle
- Her yorumda 1 mini kehanet olacak

🚫 YAPMA:
- Kuru çizgi açıklaması
- Korkutucu tahminler
- "AI olarak" deme"""

    # TensorFlow verileriyle zenginleştirilmiş prompt
    tf_section = ""
    if tf_analysis_text:
        tf_section = f"""

{tf_analysis_text}

Bu TensorFlow analiz sonuçlarını görselden gördüklerinle birleştirerek yorum yap.
"""

    prompt = f"""Bu {hand_text} fotoğrafını analiz et ve detaylı bir el falı yorumu yap.

Danışan: {user_greeting}
{tf_section}
Şu başlıklar altında yorum yap:
🖐️ GENEL İZLENİM - Elin genel yapısı ve enerjisi (El tipi dahil)
📏 YAŞAM ÇİZGİSİ - Sağlık ve yaşam enerjisi
💕 KALP ÇİZGİSİ - Aşk ve duygusal hayat
🧠 KAFA ÇİZGİSİ - Zeka ve düşünce tarzı
⭐ KADER ÇİZGİSİ - Kariyer ve başarı
✋ PARMAKLAR - Kişilik özellikleri (TensorFlow parmak analizi dahil)
🔮 GELECEK - Önümüzdeki dönem için öngörüler

Her bölümde "{user_greeting}" şeklinde samimi hitap kullan.
Umut dolu ve motive edici bir dil kullan."""

    try:
        # GPT-4 Vision ile el analizi
        result = await get_ai_response_with_image(prompt, system_message, request.image)
    except Exception as e:
        logger.error(f"Vision API error: {str(e)}")
        # Fallback - görsel analiz yapılamadıysa genel yorum
        result = await get_ai_response(prompt, system_message)
    
    # Save to database
    fortune_id = str(uuid.uuid4())
    fortune = Fortune(
        id=fortune_id,
        user_id=request.user_id,
        fortune_type="palmistry",
        input_data=json.dumps({
            "hand": request.hand,
            "has_tensorflow": request.tensorflow_analysis is not None
        }),
        result=result
    )
    
    await db.fortunes.insert_one(fortune.dict())
    await deduct_credits(request.user_id, 1, credit_check["is_free"])
    
    return {
        "reading": result,
        "hand": request.hand,
        "fortune_id": fortune_id,
        "tensorflow_used": request.tensorflow_analysis is not None,
        "credits_remaining": credit_check["credits"] - (0 if credit_check["is_free"] else 1),
        "prompt_style": prompt_metadata.get("style", "emotional"),
        "mood": prompt_metadata.get("mood", "neutral")
    }

# ============== Payment Endpoints ==============

@api_router.post("/payments/checkout")
async def create_checkout_session(request: CheckoutRequest, http_request: Request):
    if request.package_id not in CREDIT_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")
    
    package = CREDIT_PACKAGES[request.package_id]
    
    host_url = request.origin_url
    webhook_url = f"{str(http_request.base_url)}api/webhook/stripe"
    
    raise HTTPException(status_code=503, detail="Payment disabled") # stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    success_url = f"{host_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{host_url}/credits"
    
    checkout_request = CheckoutSessionRequest(
        amount=float(package["amount"]),
        currency=package["currency"],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "package_id": request.package_id,
            "credits": str(package["credits"]),
            "type": "credit_purchase"
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Save transaction
    await db.payment_transactions.insert_one({
        "session_id": session.session_id,
        "package_id": request.package_id,
        "amount": package["amount"],
        "currency": package["currency"],
        "credits": package["credits"],
        "status": "pending",
        "payment_status": "initiated",
        "created_at": datetime.utcnow()
    })
    
    return {"url": session.url, "session_id": session.session_id}

@api_router.post("/payments/premium")
async def create_premium_checkout(request: PremiumCheckoutRequest, http_request: Request):
    host_url = request.origin_url
    webhook_url = f"{str(http_request.base_url)}api/webhook/stripe"
    
    raise HTTPException(status_code=503, detail="Payment disabled") # stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    success_url = f"{host_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}&type=premium"
    cancel_url = f"{host_url}/credits"
    
    checkout_request = CheckoutSessionRequest(
        amount=float(PREMIUM_PRICE),
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"type": "premium_subscription"}
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    await db.payment_transactions.insert_one({
        "session_id": session.session_id,
        "type": "premium",
        "amount": PREMIUM_PRICE,
        "currency": "usd",
        "status": "pending",
        "payment_status": "initiated",
        "created_at": datetime.utcnow()
    })
    
    return {"url": session.url, "session_id": session.session_id}

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, user_id: str = None, http_request: Request = None):
    webhook_url = f"{str(http_request.base_url)}api/webhook/stripe" if http_request else ""
    raise HTTPException(status_code=503, detail="Payment disabled") # stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    status = await stripe_checkout.get_checkout_status(session_id)
    
    # Update transaction
    transaction = await db.payment_transactions.find_one({"session_id": session_id})
    
    if transaction and status.payment_status == "paid" and transaction.get("payment_status") != "paid":
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"status": "completed", "payment_status": "paid", "completed_at": datetime.utcnow()}}
        )
        
        # Grant credits or premium
        if user_id:
            metadata = status.metadata
            if metadata.get("type") == "credit_purchase":
                credits = int(metadata.get("credits", 0))
                await db.users.update_one({"id": user_id}, {"$inc": {"credits": credits}})
            elif metadata.get("type") == "premium_subscription":
                await db.users.update_one({"id": user_id}, {"$set": {"is_premium": True}})
    
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "amount": status.amount_total,
        "currency": status.currency,
        "metadata": status.metadata
    }

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    webhook_url = f"{str(request.base_url)}api/webhook/stripe"
    raise HTTPException(status_code=503, detail="Payment disabled") # stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        event = await stripe_checkout.handle_webhook(body, signature)
        
        if event.payment_status == "paid":
            await db.payment_transactions.update_one(
                {"session_id": event.session_id},
                {"$set": {"status": "completed", "payment_status": "paid"}}
            )
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

# ============== Fortune History ==============

@api_router.get("/fortunes/{user_id}")
async def get_fortune_history(user_id: str, limit: int = 20):
    # Optimized query with projection
    projection = {
        "_id": 0,
        "id": 1,
        "user_id": 1,
        "fortune_type": 1,
        "result": 1,
        "created_at": 1
    }
    fortunes = await db.fortunes.find({"user_id": user_id}, projection).sort("created_at", -1).to_list(limit)
    # Convert datetime to string if needed
    result = []
    for fortune in fortunes:
        fortune_dict = dict(fortune)
        if 'created_at' in fortune_dict and hasattr(fortune_dict['created_at'], 'isoformat'):
            fortune_dict['created_at'] = fortune_dict['created_at'].isoformat()
        result.append(fortune_dict)
    return result

# ============== Zodiac Signs ==============

@api_router.get("/zodiac-signs")
async def get_zodiac_signs(language: str = "tr"):
    signs = []
    for sign_en, data in ZODIAC_SIGNS.items():
        signs.append({
            "id": sign_en,
            "name": data["tr"] if language == "tr" else sign_en,
            "element": data["element"],
            "ruling_planet": data["ruling_planet"],
            "dates": data["dates"]
        })
    return {"signs": signs}

# ============== Premium & Subscription ==============

@api_router.get("/premium/plans")
async def get_premium_plans(language: str = "tr"):
    plans = []
    for plan_id, plan_data in PREMIUM_PLANS.items():
        plans.append({
            "id": plan_id,
            "name": plan_data[f"name_{language}"] if f"name_{language}" in plan_data else plan_data["name_en"],
            "price": plan_data["price"],
            "credits_per_month": plan_data.get("credits_per_month", 0),
            "unlimited": plan_data.get("unlimited", False),
            "discount": plan_data.get("discount", 0)
        })
    
    features = [{
        "id": f["id"],
        "name": f[f"name_{language}"] if f"name_{language}" in f else f["name_en"]
    } for f in PREMIUM_FEATURES]
    
    return {"plans": plans, "features": features}

@api_router.get("/credit-packages")
async def get_credit_packages(language: str = "tr"):
    packages = []
    for pkg_id, pkg_data in CREDIT_PACKAGES.items():
        packages.append({
            "id": pkg_id,
            "name": pkg_data[f"name_{language}"] if f"name_{language}" in pkg_data else pkg_data["name_en"],
            "credits": pkg_data["credits"],
            "bonus": pkg_data.get("bonus", 0),
            "amount": pkg_data["amount"],
            "currency": pkg_data["currency"]
        })
    return {"packages": packages}

# ============== Community & Social ==============

class ShareReadingRequest(BaseModel):
    user_id: str
    fortune_id: str
    anonymous: bool = True
    comment: Optional[str] = None

class CommunityPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: Optional[str] = None  # Only if not anonymous
    fortune_type: str
    fortune_excerpt: str  # Shortened version
    comment: Optional[str] = None
    likes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

@api_router.post("/community/share")
async def share_to_community(request: ShareReadingRequest):
    """Share a reading to the community feed"""
    fortune = await db.fortunes.find_one({"id": request.fortune_id, "user_id": request.user_id})
    if not fortune:
        raise HTTPException(status_code=404, detail="Fortune not found")
    
    # Get user info if not anonymous
    user_name = None
    if not request.anonymous:
        user = await db.users.find_one({"id": request.user_id})
        user_name = user.get("name") if user else None
    
    # Create excerpt (first 200 chars)
    excerpt = fortune["result"][:200] + "..." if len(fortune["result"]) > 200 else fortune["result"]
    
    post = CommunityPost(
        user_id=request.user_id if not request.anonymous else "anonymous",
        user_name=user_name,
        fortune_type=fortune["fortune_type"],
        fortune_excerpt=excerpt,
        comment=request.comment
    )
    
    await db.community_posts.insert_one(post.dict())
    return {"success": True, "post_id": post.id}

@api_router.get("/community/feed")
async def get_community_feed(limit: int = 20, skip: int = 0):
    """Get community feed of shared readings"""
    # Optimized query with projection
    projection = {
        "_id": 0,
        "id": 1,
        "user_name": 1,
        "fortune_type": 1,
        "fortune_excerpt": 1,
        "comment": 1,
        "likes": 1,
        "created_at": 1
    }
    posts = await db.community_posts.find({}, projection).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    # Convert datetime to string if needed
    for post in posts:
        if 'created_at' in post and hasattr(post['created_at'], 'isoformat'):
            post['created_at'] = post['created_at'].isoformat()
    return {"posts": posts}

@api_router.post("/community/like/{post_id}")
async def like_post(post_id: str, user_id: str):
    """Like a community post"""
    result = await db.community_posts.update_one(
        {"id": post_id},
        {"$inc": {"likes": 1}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Track user likes
    await db.user_likes.insert_one({
        "user_id": user_id,
        "post_id": post_id,
        "created_at": datetime.utcnow()
    })
    
    return {"success": True}

# ============== Daily Tarot ==============

class DailyTarotRequest(BaseModel):
    user_id: str
    language: str = "tr"

@api_router.get("/fortune/daily-tarot/check")
async def check_daily_tarot(user_id: str):
    """Check if user has already drawn daily tarot today"""
    today = datetime.utcnow().date()
    
    existing = await db.daily_tarot.find_one({
        "user_id": user_id,
        "date": str(today)
    })
    
    if existing:
        return {
            "already_drawn": True,
            "card": existing.get("card"),
            "fortune": existing.get("fortune")
        }
    
    return {"already_drawn": False}

@api_router.post("/fortune/daily-tarot")
async def daily_tarot_reading(request: DailyTarotRequest):
    """Draw daily tarot card - free once per day"""
    today = datetime.utcnow().date()
    
    # Check if already drawn today
    existing = await db.daily_tarot.find_one({
        "user_id": request.user_id,
        "date": str(today)
    })
    
    if existing:
        return {
            "card": existing.get("card"),
            "fortune": existing.get("fortune"),
            "already_drawn": True,
            "credits_remaining": (await check_user_credits(request.user_id))["credits"]
        }
    
    # Select random card from Major Arcana for daily (more impactful)
    major_arcana = [c for c in ALL_TAROT_CARDS if c.get("id", 0) < 22]
    selected_card = random.choice(major_arcana)
    is_reversed = random.choice([True, False])
    
    card_info = {
        "name": selected_card["name"],
        "name_tr": selected_card.get("name_tr", selected_card["name"]),
        "meaning": selected_card["reversed" if is_reversed else "upright"],
        "keywords_tr": selected_card.get("keywords_tr", []),
        "suit": "Major Arcana",
        "is_major": True,
        "reversed": is_reversed
    }
    
    lang = request.language
    
    # 3 Katmanlı Prompt Sistemi
    mood = getattr(request, 'mood', 'neutral') or 'neutral'
    layered_prompt, prompt_metadata = get_layered_prompt(
        language=lang,
        mood=mood,
        interest="general",
        fortune_type="daily_tarot",
        use_best_of_three=True
    )
    
    if lang == "tr":
        system_message = f"""Sen deneyimli bir tarot ustasısın. Günlük tarot kartı yorumu yapıyorsun.
        Kısa, öz ama etkileyici bir yorum yap.
        Günün enerjisine odaklan.
        Samimi ve sıcak bir dil kullan.
        "Canım", "güzelim" gibi hitaplar kullan.
        4-6 cümle yorum yap.
        
{layered_prompt}"""
        
        prompt = f"""GÜNLÜK TAROT KARTI

Kart: {card_info['name_tr']}
Durum: {'Ters' if is_reversed else 'Düz'}
Anlam: {card_info['meaning']}
Anahtar Kelimeler: {', '.join(card_info['keywords_tr'][:3])}

Bu kart bugün için ne mesaj veriyor? 
Günün enerjisini ve dikkat edilmesi gerekenleri anlat.
Kısa ama etkileyici bir yorum yap.
Motivasyon veren bir mesajla bitir."""
    else:
        system_message = f"""You are an experienced tarot master giving daily card readings.
        Keep it short but impactful.
        Focus on the day's energy.
        Use warm and friendly language.
        Write 4-6 sentences.
        
{layered_prompt}"""
        
        prompt = f"""DAILY TAROT CARD

Card: {card_info['name']}
Position: {'Reversed' if is_reversed else 'Upright'}
Meaning: {card_info['meaning']}
Keywords: {', '.join(card_info['keywords_tr'][:3])}

What message does this card bring for today?
Describe the day's energy and things to watch for.
Give a short but impactful reading.
End with a motivating message."""
    
    fortune = await get_ai_response(prompt, system_message)
    
    # Save daily tarot
    await db.daily_tarot.insert_one({
        "user_id": request.user_id,
        "date": str(today),
        "card": card_info,
        "fortune": fortune,
        "created_at": datetime.utcnow()
    })
    
    # Store in reading history
    await db.reading_history.insert_one({
        "user_id": request.user_id,
        "type": "daily_tarot",
        "cards": [card_info["name"]],
        "created_at": datetime.utcnow()
    })
    
    credit_check = await check_user_credits(request.user_id)
    
    return {
        "card": card_info,
        "fortune": fortune,
        "already_drawn": False,
        "credits_remaining": credit_check["credits"]
    }

# ============== Personalization AI ==============

class FriendFortuneRequest(BaseModel):
    user_id: str
    friend_name: str
    birth_date: Optional[str] = None
    zodiac_sign: str
    question: Optional[str] = None
    language: str = "tr"

@api_router.post("/fortune/friend")
async def friend_fortune_reading(request: FriendFortuneRequest):
    """Get a fortune reading for a friend"""
    credit_check = await check_user_credits(request.user_id)
    if not credit_check["can_use"]:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    lang = request.language
    zodiac_name = ZODIAC_SIGNS.get(request.zodiac_sign.lower(), {}).get("tr" if lang == "tr" else request.zodiac_sign, request.zodiac_sign)
    
    # 3 Katmanlı Prompt Sistemi
    mood = getattr(request, 'mood', 'neutral') or 'neutral'
    layered_prompt, prompt_metadata = get_layered_prompt(
        language=lang,
        mood=mood,
        question=request.question,
        fortune_type="friend",
        use_best_of_three=True
    )
    
    if lang == "tr":
        system_message = f"""{MASTER_SYSTEM_PROMPT["tr"]}

{layered_prompt}"""
        prompt = f"""ARKADAŞ FALI YORUMU

Arkadaşın Adı: {request.friend_name}
Burcu: {zodiac_name}
{"Doğum Tarihi: " + request.birth_date if request.birth_date else ""}
{"Soru: " + request.question if request.question else "Genel yorum isteniyor"}

{request.friend_name} için özel bir fal yorumu yap.
Burcunun özelliklerine göre kişiliğini ve yakın geleceğini yorumla.
Samimi ve sıcak bir dil kullan.
"Canım", "tatlım" gibi hitaplar kullanabilirsin.
5-8 cümle yorum yap.
Sonunda motivasyon veren bir mesaj ekle."""
    else:
        system_message = f"""{MASTER_SYSTEM_PROMPT["en"]}

{layered_prompt}"""
        prompt = f"""FRIEND FORTUNE READING

Friend's Name: {request.friend_name}
Zodiac Sign: {zodiac_name}
{"Birth Date: " + request.birth_date if request.birth_date else ""}
{"Question: " + request.question if request.question else "General reading requested"}

Create a special fortune reading for {request.friend_name}.
Interpret their personality and near future based on their zodiac traits.
Use warm and friendly language.
Write 5-8 sentences.
End with a motivating message."""
    
    result = await get_ai_response(prompt, system_message)
    
    fortune = Fortune(
        user_id=request.user_id,
        fortune_type="friend",
        input_data=f"{request.friend_name} - {zodiac_name}",
        result=result
    )
    await db.fortunes.insert_one(fortune.dict())
    await deduct_credits(request.user_id, 1, credit_check["is_free"])
    
    return {
        "fortune": fortune.dict(),
        "friend_name": request.friend_name,
        "zodiac_sign": zodiac_name,
        "credits_remaining": credit_check["credits"] - (0 if credit_check["is_free"] else 1),
        "prompt_style": prompt_metadata.get("style", "emotional"),
        "mood": prompt_metadata.get("mood", "neutral")
    }

@api_router.get("/user/{user_id}/reading-history")
async def get_reading_history_for_personalization(user_id: str, limit: int = 50):
    """Get user's reading history for AI personalization"""
    history = await db.reading_history.find({"user_id": user_id}).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Analyze patterns
    categories = {}
    card_frequency = {}
    
    for reading in history:
        cat = reading.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1
        
        for card in reading.get("cards", []):
            card_frequency[card] = card_frequency.get(card, 0) + 1
    
    # Get most frequent cards
    top_cards = sorted(card_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_readings": len(history),
        "category_preferences": categories,
        "frequent_cards": [{"card": c[0], "count": c[1]} for c in top_cards],
        "recent_readings": history[:10]
    }

# ============== Health Check ==============

@api_router.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes"""
    health_status = {"status": "healthy", "services": {}}
    
    # Check MongoDB connection
    try:
        if db is not None:
            await client.admin.command('ping')
            health_status["services"]["mongodb"] = "connected"
        else:
            health_status["services"]["mongodb"] = "not_initialized"
    except Exception as e:
        health_status["services"]["mongodb"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

# ============== ANALYTICS & RAPORLAMA SİSTEMİ ==============

class AnalyticsEvent(BaseModel):
    user_id: str
    event_type: str  # page_view, fortune_request, button_click, session_start, session_end
    event_data: Optional[Dict] = None
    screen_name: Optional[str] = None
    duration_seconds: Optional[int] = None

@api_router.post("/analytics/event")
async def track_event(event: AnalyticsEvent):
    """Track user events for analytics"""
    try:
        event_doc = {
            "user_id": event.user_id,
            "event_type": event.event_type,
            "event_data": event.event_data or {},
            "screen_name": event.screen_name,
            "duration_seconds": event.duration_seconds,
            "timestamp": datetime.utcnow(),
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        }
        await db.analytics_events.insert_one(event_doc)
        return {"success": True}
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return {"success": False}

@api_router.get("/analytics/dashboard")
async def get_analytics_dashboard():
    """Get analytics dashboard data"""
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Toplam kullanıcı sayısı
        total_users = await db.users.count_documents({})
        
        # Bugünkü aktif kullanıcılar
        today_active = await db.analytics_events.distinct("user_id", {"date": today})
        
        # Haftalık aktif kullanıcılar
        weekly_active = await db.analytics_events.distinct("user_id", {"date": {"$gte": week_ago}})
        
        # Fal türlerine göre kullanım
        fortune_pipeline = [
            {"$group": {"_id": "$fortune_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        fortune_stats = await db.fortunes.aggregate(fortune_pipeline).to_list(100)
        
        # En popüler ekranlar
        screen_pipeline = [
            {"$match": {"event_type": "page_view", "date": {"$gte": week_ago}}},
            {"$group": {"_id": "$screen_name", "views": {"$sum": 1}}},
            {"$sort": {"views": -1}},
            {"$limit": 10}
        ]
        popular_screens = await db.analytics_events.aggregate(screen_pipeline).to_list(10)
        
        # Günlük kullanım trendi (son 7 gün)
        daily_pipeline = [
            {"$match": {"date": {"$gte": week_ago}}},
            {"$group": {"_id": "$date", "events": {"$sum": 1}, "users": {"$addToSet": "$user_id"}}},
            {"$project": {"date": "$_id", "events": 1, "unique_users": {"$size": "$users"}}},
            {"$sort": {"date": 1}}
        ]
        daily_trend = await db.analytics_events.aggregate(daily_pipeline).to_list(7)
        
        # Ortalama oturum süresi
        session_pipeline = [
            {"$match": {"event_type": "session_end", "duration_seconds": {"$gt": 0}}},
            {"$group": {"_id": None, "avg_duration": {"$avg": "$duration_seconds"}}}
        ]
        session_stats = await db.analytics_events.aggregate(session_pipeline).to_list(1)
        avg_session = session_stats[0]["avg_duration"] if session_stats else 0
        
        return {
            "total_users": total_users,
            "daily_active_users": len(today_active),
            "weekly_active_users": len(weekly_active),
            "fortune_usage": {stat["_id"]: stat["count"] for stat in fortune_stats},
            "popular_screens": [{"screen": s["_id"], "views": s["views"]} for s in popular_screens],
            "daily_trend": daily_trend,
            "avg_session_minutes": round(avg_session / 60, 1) if avg_session else 0,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return {"error": str(e)}

@api_router.get("/analytics/fortune-insights")
async def get_fortune_insights():
    """Get detailed fortune reading insights"""
    try:
        # En çok sorulan sorular (AI Chat)
        question_pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        category_stats = await db.ai_chat_history.aggregate(question_pipeline).to_list(10)
        
        # Zaman dilimlerine göre kullanım
        hour_pipeline = [
            {"$project": {"hour": {"$hour": "$created_at"}}},
            {"$group": {"_id": "$hour", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        hourly_usage = await db.fortunes.aggregate(hour_pipeline).to_list(24)
        
        # Peak saatler
        peak_hours = sorted(hourly_usage, key=lambda x: x["count"], reverse=True)[:3] if hourly_usage else []
        
        peak_hours_str = ', '.join([str(h["_id"]) + ":00" for h in peak_hours]) if peak_hours else ""
        
        return {
            "category_distribution": {stat["_id"]: stat["count"] for stat in category_stats},
            "hourly_usage": {str(h["_id"]): h["count"] for h in hourly_usage},
            "peak_hours": [h["_id"] for h in peak_hours],
            "insight": f"En yoğun saatler: {peak_hours_str}" if peak_hours else "Veri yok"
        }
    except Exception as e:
        logger.error(f"Insights error: {e}")
        return {"error": str(e)}

# ============== OTOMATİK İÇERİK GÜNCELLEME SİSTEMİ ==============

# Astrolojik olaylar ve özel günler
ASTROLOGICAL_EVENTS = {
    "mercury_retrograde": {
        "dates": ["2025-03-15", "2025-07-18", "2025-11-09"],  # Örnek tarihler
        "message_tr": "Merkür Retrosu dönemindeyiz! İletişim ve kararlar konusunda dikkatli ol.",
        "message_en": "Mercury is in retrograde! Be careful with communication and decisions."
    },
    "full_moon": {
        "dates": ["2025-06-11", "2025-07-10", "2025-08-09"],  # Dolunay tarihleri
        "message_tr": "Dolunay gecesi! Enerjiler yükseldi, dileklerin gerçekleşme zamanı.",
        "message_en": "Full moon night! Energies are high, time for wishes to come true."
    },
    "new_moon": {
        "dates": ["2025-06-25", "2025-07-24", "2025-08-23"],  # Yeni ay tarihleri
        "message_tr": "Yeni Ay! Yeni başlangıçlar için mükemmel bir dönem.",
        "message_en": "New Moon! Perfect time for new beginnings."
    }
}

# Mevsimsel temalar
SEASONAL_THEMES = {
    "spring": {
        "months": [3, 4, 5],
        "theme_tr": "Bahar Uyanışı",
        "message_tr": "Doğa uyanıyor, seninle birlikte yeni umutlar filizleniyor!",
        "colors": ["#90EE90", "#FFD700", "#FFC0CB"]
    },
    "summer": {
        "months": [6, 7, 8],
        "theme_tr": "Yaz Enerjisi",
        "message_tr": "Güneşin gücü seninle! Tutkulu ve enerjik bir dönem başlıyor.",
        "colors": ["#FF6347", "#FFD700", "#FF4500"]
    },
    "autumn": {
        "months": [9, 10, 11],
        "theme_tr": "Sonbahar Dönüşümü",
        "message_tr": "Yapraklar düşerken, sen yükseliyorsun. Dönüşüm zamanı!",
        "colors": ["#D2691E", "#8B4513", "#FF8C00"]
    },
    "winter": {
        "months": [12, 1, 2],
        "theme_tr": "Kış Gizemı",
        "message_tr": "Kış uykusunda bile ruhun parlıyor. İç yolculuk zamanı.",
        "colors": ["#4169E1", "#E6E6FA", "#B0C4DE"]
    }
}

@api_router.get("/content/daily-message")
async def get_daily_message():
    """Get daily special message based on astrological events and season"""
    today = datetime.utcnow()
    today_str = today.strftime("%Y-%m-%d")
    current_month = today.month
    
    messages = []
    special_events = []
    
    # Check astrological events
    for event_name, event_data in ASTROLOGICAL_EVENTS.items():
        if today_str in event_data["dates"]:
            special_events.append(event_name)
            messages.append({
                "type": event_name,
                "message": event_data["message_tr"],
                "priority": "high"
            })
    
    # Get seasonal theme
    season = None
    for season_name, season_data in SEASONAL_THEMES.items():
        if current_month in season_data["months"]:
            season = season_name
            messages.append({
                "type": "seasonal",
                "theme": season_data["theme_tr"],
                "message": season_data["message_tr"],
                "colors": season_data["colors"],
                "priority": "normal"
            })
            break
    
    # Daily affirmation based on day of week
    daily_affirmations = {
        0: "Pazartesi enerjisiyle yeni başlangıçlara hazırsın!",
        1: "Salı günü cesaretinle öne çık!",
        2: "Çarşamba bilgelik günü, içsel sesini dinle.",
        3: "Perşembe bolluğu çağırıyor, fırsatlara açık ol!",
        4: "Cuma aşk enerjisi yüksek, kalbini aç!",
        5: "Cumartesi dinlenme ve yenilenme zamanı.",
        6: "Pazar günü ruhsal arınma için ideal!"
    }
    
    messages.append({
        "type": "daily_affirmation",
        "message": daily_affirmations[today.weekday()],
        "priority": "low"
    })
    
    return {
        "date": today_str,
        "season": season,
        "special_events": special_events,
        "messages": sorted(messages, key=lambda x: {"high": 0, "normal": 1, "low": 2}[x["priority"]]),
        "daily_number": (today.day + today.month) % 9 + 1,  # Numeroloji günlük sayı
        "lucky_color": SEASONAL_THEMES.get(season, {}).get("colors", ["#FFD700"])[0] if season else "#FFD700"
    }

@api_router.get("/content/weekly-horoscope/{zodiac_sign}")
async def get_weekly_horoscope(zodiac_sign: str):
    """Generate or get cached weekly horoscope for a zodiac sign"""
    try:
        # Check cache first
        today = datetime.utcnow()
        week_start = today - timedelta(days=today.weekday())
        week_key = week_start.strftime("%Y-W%W")
        
        cached = await db.weekly_horoscopes.find_one({
            "zodiac_sign": zodiac_sign.lower(),
            "week_key": week_key
        })
        
        if cached:
            return {
                "zodiac_sign": zodiac_sign,
                "week": week_key,
                "horoscope": cached["horoscope"],
                "lucky_days": cached.get("lucky_days", []),
                "lucky_numbers": cached.get("lucky_numbers", []),
                "cached": True
            }
        
        # 3 Katmanlı Prompt Sistemi
        layered_prompt, prompt_metadata = get_layered_prompt(
            language="tr",
            mood="neutral",
            interest="general",
            fortune_type="weekly_horoscope",
            use_best_of_three=True
        )
        
        # Generate new weekly horoscope
        system_message = f"""Sen NeferTiti - 3000 yıllık kadim bilge. 
Haftalık burç yorumu yap. Kısa, öz ve etkileyici ol.
Şans günleri ve şanslı sayılar da belirt.

{layered_prompt}"""
        
        prompt = f"""{zodiac_sign} burcu için bu haftanın yorumunu yap.
Şunları içersin:
1. Genel enerji (2 cümle)
2. Aşk (1 cümle)
3. Kariyer (1 cümle)
4. Tavsiye (1 cümle)
5. Şans günleri (haftanın 2 günü)
6. Şanslı sayılar (3 sayı)"""

        horoscope = await get_ai_response(prompt, system_message)
        
        # Parse lucky days and numbers (simplified)
        lucky_days = ["Salı", "Cuma"]  # Default
        lucky_numbers = [3, 7, 12]  # Default
        
        # Cache the horoscope
        await db.weekly_horoscopes.insert_one({
            "zodiac_sign": zodiac_sign.lower(),
            "week_key": week_key,
            "horoscope": horoscope,
            "lucky_days": lucky_days,
            "lucky_numbers": lucky_numbers,
            "created_at": datetime.utcnow()
        })
        
        return {
            "zodiac_sign": zodiac_sign,
            "week": week_key,
            "horoscope": horoscope,
            "lucky_days": lucky_days,
            "lucky_numbers": lucky_numbers,
            "cached": False
        }
    except Exception as e:
        logger.error(f"Weekly horoscope error: {e}")
        return {"error": str(e)}

@api_router.get("/content/special-events")
async def get_special_events():
    """Get upcoming special astrological events"""
    today = datetime.utcnow()
    today_str = today.strftime("%Y-%m-%d")
    
    upcoming_events = []
    
    for event_name, event_data in ASTROLOGICAL_EVENTS.items():
        for date_str in event_data["dates"]:
            if date_str >= today_str:
                days_until = (datetime.strptime(date_str, "%Y-%m-%d") - today).days
                upcoming_events.append({
                    "event": event_name,
                    "date": date_str,
                    "days_until": days_until,
                    "message": event_data["message_tr"]
                })
    
    # Sort by date
    upcoming_events.sort(key=lambda x: x["date"])
    
    return {
        "today": today_str,
        "upcoming_events": upcoming_events[:5],  # Next 5 events
        "current_season": next(
            (name for name, data in SEASONAL_THEMES.items() if today.month in data["months"]),
            "unknown"
        )
    }


# ============== TEXT-TO-SPEECH (TTS) ==============

# TTS Client - lazy initialization
_tts_client = None

def get_tts_client():
    global _tts_client
    if _tts_client is None:
        try:
            # DISABLED: from emergentintegrations.llm.openai import OpenAITextToSpeech
            raise HTTPException(status_code=503, detail="TTS disabled") # _tts_client = OpenAITextToSpeech(api_key=EMERGENT_LLM_KEY)
            logger.info("TTS client initialized successfully")
        except Exception as e:
            logger.error(f"TTS client initialization failed: {e}")
            raise HTTPException(status_code=500, detail="TTS service not available")
    return _tts_client


class TTSRequest(BaseModel):
    text: str
    voice: str = "nova"  # alloy, echo, fable, onyx, nova, shimmer
    provider: str = "openai"

@api_router.post("/tts/generate")
async def generate_tts(request: TTSRequest):
    """Generate TTS audio using OpenAI via Emergent Integration"""
    import base64
    
    try:
        tts_client = get_tts_client()
        
        # Emergent Integration TTS kullan - base64 output
        audio_base64 = await tts_client.generate_speech_base64(
            text=request.text,
            model="tts-1",
            voice=request.voice,
            speed=0.9  # Biraz yavaş, daha anlaşılır
        )
        
        return {
            "success": True,
            "audio_base64": audio_base64,
            "audio_url": f"data:audio/mp3;base64,{audio_base64}",
            "voice": request.voice,
            "provider": request.provider
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


@api_router.get("/tts/voices")
async def get_available_voices():
    """Get available TTS voices"""
    return {
        "openai": [
            {"id": "alloy", "name": "Alloy", "description": "Nötr, profesyonel", "gender": "neutral"},
            {"id": "echo", "name": "Echo", "description": "Erkek, derin ve güven veren", "gender": "male"},
            {"id": "fable", "name": "Fable", "description": "Hikaye anlatıcısı, dramatik", "gender": "neutral"},
            {"id": "onyx", "name": "Onyx", "description": "Erkek, güçlü ve etkileyici", "gender": "male"},
            {"id": "nova", "name": "Nova", "description": "Kadın, sıcak ve samimi", "gender": "female"},
            {"id": "shimmer", "name": "Shimmer", "description": "Kadın, yumuşak ve mistik", "gender": "female"},
        ]
    }


# ============== ZODIAC COMPATIBILITY ==============

class ZodiacCompatibilityRequest(BaseModel):
    sign1: str
    sign2: str
    compatibility: dict
    language: str = "tr"

@api_router.post("/fortune/zodiac-compatibility")
async def zodiac_compatibility(request: ZodiacCompatibilityRequest):
    """Generate AI description for zodiac compatibility"""
    
    # 3 Katmanlı Prompt Sistemi
    layered_prompt, prompt_metadata = get_layered_prompt(
        language=request.language,
        mood="romantic",  # Uyumluluk genelde romantik konular için
        interest="love",
        fortune_type="zodiac_compatibility",
        use_best_of_three=True
    )
    
    prompt = f"""İki burç arasındaki uyumu anlat:

Burç 1: {request.sign1}
Burç 2: {request.sign2}

Uyum Yüzdeleri:
- Aşk: %{request.compatibility.get('love', 50)}
- Arkadaşlık: %{request.compatibility.get('friendship', 50)}
- İş: %{request.compatibility.get('work', 50)}
- Genel: %{request.compatibility.get('overall', 50)}

Bu iki burç arasındaki ilişkiyi 3-4 cümlede samimi ve mistik bir dille anlat.
- Güçlü yanlarını vurgula
- Dikkat etmeleri gereken noktaları belirt
- Umut verici ama gerçekçi ol
- "Sizin aranızda..." veya "Bu ikili..." ile başla"""

    system = f"""Sen astroloji uzmanı NeferTiti'sin. Burç uyumlarını samimi, mistik ve anlaşılır bir dille anlatırsın.
Kısa ve öz cümleler kullan. Klişelerden kaçın, özgün ol.

{layered_prompt}"""

    description = await get_ai_response(prompt, system)
    
    return {
        "description": description,
        "sign1": request.sign1,
        "sign2": request.sign2,
        "prompt_style": prompt_metadata.get("style", "emotional")
    }


# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
