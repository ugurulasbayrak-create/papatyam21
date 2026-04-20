# Full 78 Card Tarot System with Meanings and Combinations

MAJOR_ARCANA = [
    {
        "id": 0, "name": "The Fool", "name_tr": "Deli",
        "keywords": ["new beginnings", "adventure", "innocence", "spontaneity"],
        "keywords_tr": ["yeni başlangıçlar", "macera", "masumiyet", "spontanlık"],
        "upright": "Hayatında yepyeni bir sayfa açılıyor. Korkusuzca ileri atıl, evren seni destekliyor.",
        "reversed": "Biraz dur ve düşün. Aceleci davranmak seni zor duruma düşürebilir.",
        "upright_en": "A brand new chapter is opening in your life. Step forward fearlessly, the universe supports you.",
        "reversed_en": "Pause and think. Acting hastily might put you in a difficult position.",
        "element": "Air", "planet": "Uranus"
    },
    {
        "id": 1, "name": "The Magician", "name_tr": "Sihirbaz",
        "keywords": ["manifestation", "power", "action", "resourcefulness"],
        "keywords_tr": ["yaratıcılık", "güç", "aksiyon", "beceriklilik"],
        "upright": "Elinde ihtiyacın olan her şey var. Şimdi harekete geçme zamanı!",
        "reversed": "Yeteneklerini tam kullanamıyorsun. İçindeki gücü keşfetmelisin.",
        "upright_en": "You have everything you need. Now is the time to take action!",
        "reversed_en": "You're not using your talents fully. You need to discover the power within.",
        "element": "Air", "planet": "Mercury"
    },
    {
        "id": 2, "name": "The High Priestess", "name_tr": "Baş Rahibe",
        "keywords": ["intuition", "mystery", "inner knowledge", "subconscious"],
        "keywords_tr": ["sezgi", "gizem", "iç bilgi", "bilinçaltı"],
        "upright": "İç sesine kulak ver. Cevaplar zaten içinde, sadece dinlemen gerekiyor.",
        "reversed": "Sezgilerini görmezden geliyorsun. Mantık her zaman doğru yol değil.",
        "upright_en": "Listen to your inner voice. The answers are already within you.",
        "reversed_en": "You're ignoring your intuition. Logic isn't always the right path.",
        "element": "Water", "planet": "Moon"
    },
    {
        "id": 3, "name": "The Empress", "name_tr": "İmparatoriçe",
        "keywords": ["abundance", "fertility", "nature", "nurturing"],
        "keywords_tr": ["bereket", "doğurganlık", "doğa", "şefkat"],
        "upright": "Bolluk ve bereket kapında. Sevgi dolu bir dönem seni bekliyor.",
        "reversed": "Kendine yeterince bakmıyorsun. Önce sen dolu olmalısın ki verebilesin.",
        "upright_en": "Abundance is at your door. A loving period awaits you.",
        "reversed_en": "You're not taking care of yourself enough. You must be full first to give.",
        "element": "Earth", "planet": "Venus"
    },
    {
        "id": 4, "name": "The Emperor", "name_tr": "İmparator",
        "keywords": ["authority", "structure", "leadership", "stability"],
        "keywords_tr": ["otorite", "yapı", "liderlik", "istikrar"],
        "upright": "Kontrolü ele alma zamanı. Disiplinli olursan hedeflerine ulaşırsın.",
        "reversed": "Çok katı olma. Esnek olmayı öğrenmelisin.",
        "upright_en": "Time to take control. With discipline, you'll reach your goals.",
        "reversed_en": "Don't be too rigid. You need to learn flexibility.",
        "element": "Fire", "planet": "Aries"
    },
    {
        "id": 5, "name": "The Hierophant", "name_tr": "Aziz",
        "keywords": ["tradition", "wisdom", "spiritual guidance", "conformity"],
        "keywords_tr": ["gelenek", "bilgelik", "manevi rehberlik", "uyum"],
        "upright": "Bir öğretmen veya mentor hayatına girebilir. Öğrenmeye açık ol.",
        "reversed": "Kendi yolunu çizme zamanı. Başkalarının kurallarına uymak zorunda değilsin.",
        "upright_en": "A teacher or mentor may enter your life. Be open to learning.",
        "reversed_en": "Time to carve your own path. You don't have to follow others' rules.",
        "element": "Earth", "planet": "Taurus"
    },
    {
        "id": 6, "name": "The Lovers", "name_tr": "Aşıklar",
        "keywords": ["love", "harmony", "choices", "relationships"],
        "keywords_tr": ["aşk", "uyum", "seçimler", "ilişkiler"],
        "upright": "Aşk hayatında güzel gelişmeler var. Önemli bir seçim yapabilirsin.",
        "reversed": "İlişkinde dengesizlik var. İletişimi güçlendirmelisin.",
        "upright_en": "Beautiful developments in your love life. You may make an important choice.",
        "reversed_en": "There's imbalance in your relationship. Strengthen communication.",
        "element": "Air", "planet": "Gemini"
    },
    {
        "id": 7, "name": "The Chariot", "name_tr": "Savaş Arabası",
        "keywords": ["victory", "willpower", "determination", "success"],
        "keywords_tr": ["zafer", "irade", "kararlılık", "başarı"],
        "upright": "Zafer senin! Kararlılığın seni hedefe ulaştıracak.",
        "reversed": "Kontrolü kaybediyorsun. Odaklanman gereken şeyi belirle.",
        "upright_en": "Victory is yours! Your determination will lead you to the goal.",
        "reversed_en": "You're losing control. Determine what you need to focus on.",
        "element": "Water", "planet": "Cancer"
    },
    {
        "id": 8, "name": "Strength", "name_tr": "Güç",
        "keywords": ["courage", "patience", "inner strength", "compassion"],
        "keywords_tr": ["cesaret", "sabır", "iç güç", "şefkat"],
        "upright": "İçindeki aslanı tut. Yumuşak güç, sert güçten daha etkilidir.",
        "reversed": "Kendine güvenin sarsılmış. Gücünü hatırla!",
        "upright_en": "Hold the lion within. Soft power is more effective than hard power.",
        "reversed_en": "Your self-confidence is shaken. Remember your strength!",
        "element": "Fire", "planet": "Leo"
    },
    {
        "id": 9, "name": "The Hermit", "name_tr": "Ermiş",
        "keywords": ["solitude", "introspection", "guidance", "wisdom"],
        "keywords_tr": ["yalnızlık", "içe bakış", "rehberlik", "bilgelik"],
        "upright": "Biraz yalnız kalma zamanı. İçsel yolculuk sana çok şey öğretecek.",
        "reversed": "Çok içine kapandın. Dışarı çık ve insanlarla bağlan.",
        "upright_en": "Time for some solitude. Inner journey will teach you a lot.",
        "reversed_en": "You've withdrawn too much. Go out and connect with people.",
        "element": "Earth", "planet": "Virgo"
    },
    {
        "id": 10, "name": "Wheel of Fortune", "name_tr": "Kader Çarkı",
        "keywords": ["destiny", "change", "cycles", "luck"],
        "keywords_tr": ["kader", "değişim", "döngüler", "şans"],
        "upright": "Şans senden yana dönüyor! Hayat değişiyor, akışa bırak.",
        "reversed": "Zor bir dönemdesin ama bu da geçecek. Sabret.",
        "upright_en": "Luck is turning in your favor! Life is changing, go with the flow.",
        "reversed_en": "You're in a tough period but this too shall pass. Be patient.",
        "element": "Fire", "planet": "Jupiter"
    },
    {
        "id": 11, "name": "Justice", "name_tr": "Adalet",
        "keywords": ["fairness", "truth", "law", "cause and effect"],
        "keywords_tr": ["adalet", "gerçek", "hukuk", "sebep-sonuç"],
        "upright": "Adalet yerini bulacak. Doğru olanı yap, karşılığını alacaksın.",
        "reversed": "Bir haksızlığa uğramış olabilirsin. Adaleti aramaya devam et.",
        "upright_en": "Justice will prevail. Do what's right, you'll be rewarded.",
        "reversed_en": "You may have faced injustice. Keep seeking fairness.",
        "element": "Air", "planet": "Libra"
    },
    {
        "id": 12, "name": "The Hanged Man", "name_tr": "Asılan Adam",
        "keywords": ["surrender", "new perspective", "sacrifice", "waiting"],
        "keywords_tr": ["teslim olma", "yeni bakış açısı", "fedakarlık", "bekleme"],
        "upright": "Bazen beklemek en iyi harekettir. Farklı bir açıdan bak.",
        "reversed": "Sıkışmış hissediyorsun. Bir şeyleri bırakman gerekiyor.",
        "upright_en": "Sometimes waiting is the best action. Look from a different angle.",
        "reversed_en": "You feel stuck. You need to let go of something.",
        "element": "Water", "planet": "Neptune"
    },
    {
        "id": 13, "name": "Death", "name_tr": "Ölüm",
        "keywords": ["transformation", "endings", "change", "rebirth"],
        "keywords_tr": ["dönüşüm", "sonlar", "değişim", "yeniden doğuş"],
        "upright": "Eski kapanıyor, yeni açılıyor. Bu bir son değil, dönüşüm!",
        "reversed": "Değişime direniyorsun. Bırakman gereken şeyi bırak.",
        "upright_en": "The old is closing, the new is opening. This is transformation, not an end!",
        "reversed_en": "You're resisting change. Let go of what you need to release.",
        "element": "Water", "planet": "Scorpio"
    },
    {
        "id": 14, "name": "Temperance", "name_tr": "Denge",
        "keywords": ["balance", "patience", "moderation", "harmony"],
        "keywords_tr": ["denge", "sabır", "ılımlılık", "uyum"],
        "upright": "Denge kuruyorsun. Sabırla ilerle, her şey yerine oturacak.",
        "reversed": "Dengen bozulmuş. Aşırılıklardan kaçın.",
        "upright_en": "You're finding balance. Move with patience, everything will fall into place.",
        "reversed_en": "Your balance is off. Avoid extremes.",
        "element": "Fire", "planet": "Sagittarius"
    },
    {
        "id": 15, "name": "The Devil", "name_tr": "Şeytan",
        "keywords": ["bondage", "materialism", "addiction", "shadow self"],
        "keywords_tr": ["bağımlılık", "maddecilik", "tutku", "gölge benlik"],
        "upright": "Seni tutan zincirlerin farkına var. Özgürleşme zamanı.",
        "reversed": "Bağımlılıklarından kurtuluyorsun. Doğru yoldasın.",
        "upright_en": "Recognize the chains holding you. Time to break free.",
        "reversed_en": "You're breaking free from your addictions. You're on the right path.",
        "element": "Earth", "planet": "Capricorn"
    },
    {
        "id": 16, "name": "The Tower", "name_tr": "Kule",
        "keywords": ["sudden change", "upheaval", "revelation", "awakening"],
        "keywords_tr": ["ani değişim", "yıkım", "aydınlanma", "uyanış"],
        "upright": "Sarsıcı bir değişim geliyor ama bu temizlik için gerekli.",
        "reversed": "Kaçınılmaz değişimi erteliyorsun. Kabul et ve ilerle.",
        "upright_en": "A shocking change is coming but it's necessary for cleansing.",
        "reversed_en": "You're postponing inevitable change. Accept and move forward.",
        "element": "Fire", "planet": "Mars"
    },
    {
        "id": 17, "name": "The Star", "name_tr": "Yıldız",
        "keywords": ["hope", "inspiration", "serenity", "renewal"],
        "keywords_tr": ["umut", "ilham", "huzur", "yenilenme"],
        "upright": "Umut var! Karanlık geceden sonra yıldızlar parlıyor.",
        "reversed": "Umudunu kaybetme. İyileşme zamanı yaklaşıyor.",
        "upright_en": "There is hope! Stars shine after the dark night.",
        "reversed_en": "Don't lose hope. Healing time is approaching.",
        "element": "Air", "planet": "Aquarius"
    },
    {
        "id": 18, "name": "The Moon", "name_tr": "Ay",
        "keywords": ["illusion", "intuition", "subconscious", "mystery"],
        "keywords_tr": ["yanılsama", "sezgi", "bilinçaltı", "gizem"],
        "upright": "Her şey göründüğü gibi değil. Sezgilerine güven.",
        "reversed": "Korkuların seni tutuyor. Gerçeği görmeye hazır ol.",
        "upright_en": "Not everything is as it seems. Trust your intuition.",
        "reversed_en": "Your fears are holding you. Be ready to see the truth.",
        "element": "Water", "planet": "Pisces"
    },
    {
        "id": 19, "name": "The Sun", "name_tr": "Güneş",
        "keywords": ["joy", "success", "vitality", "positivity"],
        "keywords_tr": ["neşe", "başarı", "canlılık", "pozitiflik"],
        "upright": "Güneş yüzüne gülüyor! Mutluluk ve başarı dolu günler geliyor.",
        "reversed": "İçindeki ışığı kaybetme. Neşeni bul.",
        "upright_en": "The sun smiles upon you! Days full of happiness and success are coming.",
        "reversed_en": "Don't lose your inner light. Find your joy.",
        "element": "Fire", "planet": "Sun"
    },
    {
        "id": 20, "name": "Judgement", "name_tr": "Mahkeme",
        "keywords": ["rebirth", "reflection", "reckoning", "awakening"],
        "keywords_tr": ["yeniden doğuş", "değerlendirme", "hesaplaşma", "uyanış"],
        "upright": "Büyük bir farkındalık geliyor. Geçmişi değerlendir, geleceğe hazırlan.",
        "reversed": "Kendini yargılamayı bırak. Affet ve ilerle.",
        "upright_en": "Great awareness is coming. Evaluate the past, prepare for the future.",
        "reversed_en": "Stop judging yourself. Forgive and move forward.",
        "element": "Fire", "planet": "Pluto"
    },
    {
        "id": 21, "name": "The World", "name_tr": "Dünya",
        "keywords": ["completion", "achievement", "wholeness", "travel"],
        "keywords_tr": ["tamamlanma", "başarı", "bütünlük", "seyahat"],
        "upright": "Bir döngü tamamlanıyor. Kutla! Yeni kapılar açılacak.",
        "reversed": "Hedefe yakınsın ama son adımı atmaktan korkuyorsun.",
        "upright_en": "A cycle is completing. Celebrate! New doors will open.",
        "reversed_en": "You're close to the goal but afraid to take the final step.",
        "element": "Earth", "planet": "Saturn"
    }
]

# Minor Arcana - Wands (Değnekler) - Fire Element
WANDS = [
    {"id": 22, "name": "Ace of Wands", "name_tr": "Değnek Ası", "number": 1, "suit": "Wands",
     "upright": "Yeni bir tutku, yeni bir proje! Enerji patlıyor.",
     "reversed": "Motivasyonun düşük. İlhamı bulmak için bekle.",
     "keywords_tr": ["yeni başlangıç", "tutku", "ilham", "potansiyel"]},
    {"id": 23, "name": "Two of Wands", "name_tr": "İki Değnek", "number": 2, "suit": "Wands",
     "upright": "Planlama zamanı. Büyük hayaller kur, dünya senin.",
     "reversed": "Kararsızlık var. Bir yol seçmelisin.",
     "keywords_tr": ["planlama", "karar", "vizyon", "keşif"]},
    {"id": 24, "name": "Three of Wands", "name_tr": "Üç Değnek", "number": 3, "suit": "Wands",
     "upright": "Çabalarının meyvesi geliyor. Sabırla bekle.",
     "reversed": "Gecikmeler var ama pes etme.",
     "keywords_tr": ["ilerleme", "genişleme", "beklenti", "fırsat"]},
    {"id": 25, "name": "Four of Wands", "name_tr": "Dört Değnek", "number": 4, "suit": "Wands",
     "upright": "Kutlama zamanı! Aile ve yuva mutluluğu.",
     "reversed": "Ev huzuru biraz sarsılmış. Dengeyi bul.",
     "keywords_tr": ["kutlama", "yuva", "mutluluk", "topluluk"]},
    {"id": 26, "name": "Five of Wands", "name_tr": "Beş Değnek", "number": 5, "suit": "Wands",
     "upright": "Rekabet var ama bu seni güçlendirir.",
     "reversed": "Çatışmadan kaçın. Barış yolunu seç.",
     "keywords_tr": ["rekabet", "çatışma", "mücadele", "gerilim"]},
    {"id": 27, "name": "Six of Wands", "name_tr": "Altı Değnek", "number": 6, "suit": "Wands",
     "upright": "Zafer! Başarın tanınacak, alkış sana.",
     "reversed": "Başarıyı göremiyorsun. Küçük zaferleri de kutla.",
     "keywords_tr": ["zafer", "tanınma", "başarı", "güven"]},
    {"id": 28, "name": "Seven of Wands", "name_tr": "Yedi Değnek", "number": 7, "suit": "Wands",
     "upright": "Pozisyonunu koru. Mücadele et, hak ettin.",
     "reversed": "Yoruldun. Bazen geri adım atmak da güçtür.",
     "keywords_tr": ["savunma", "direnç", "mücadele", "azim"]},
    {"id": 29, "name": "Eight of Wands", "name_tr": "Sekiz Değnek", "number": 8, "suit": "Wands",
     "upright": "Hızlı gelişmeler! Her şey hızlanıyor.",
     "reversed": "Gecikmeler yaşanabilir. Sabırlı ol.",
     "keywords_tr": ["hız", "hareket", "ilerleme", "haber"]},
    {"id": 30, "name": "Nine of Wands", "name_tr": "Dokuz Değnek", "number": 9, "suit": "Wands",
     "upright": "Son engel kaldı. Dayanıklılığın test ediliyor.",
     "reversed": "Çok yıprandın. Mola ver.",
     "keywords_tr": ["dayanıklılık", "azim", "savunma", "yorgunluk"]},
    {"id": 31, "name": "Ten of Wands", "name_tr": "On Değnek", "number": 10, "suit": "Wands",
     "upright": "Çok yük aldın. Bazılarını bırakman gerekiyor.",
     "reversed": "Yüklerinden kurtuluyorsun. Hafifle.",
     "keywords_tr": ["yük", "sorumluluk", "stres", "tükenme"]},
    {"id": 32, "name": "Page of Wands", "name_tr": "Değnek Uşağı", "number": 11, "suit": "Wands",
     "upright": "Heyecanlı bir haber geliyor. Yeni macera başlıyor.",
     "reversed": "Enerjini yanlış yere harcıyorsun.",
     "keywords_tr": ["haber", "heyecan", "macera", "keşif"]},
    {"id": 33, "name": "Knight of Wands", "name_tr": "Değnek Şövalyesi", "number": 12, "suit": "Wands",
     "upright": "Harekete geç! Tutkulu biri hayatına girebilir.",
     "reversed": "Düşünmeden hareket etme. Aceleci olma.",
     "keywords_tr": ["aksiyon", "tutku", "macera", "cesaret"]},
    {"id": 34, "name": "Queen of Wands", "name_tr": "Değnek Kraliçesi", "number": 13, "suit": "Wands",
     "upright": "Karizmatik ve güçlü bir kadın. Özgüvenin zirve.",
     "reversed": "Kendine daha çok güven. Işığını sakla ma.",
     "keywords_tr": ["karizma", "güç", "özgüven", "bağımsızlık"]},
    {"id": 35, "name": "King of Wands", "name_tr": "Değnek Kralı", "number": 14, "suit": "Wands",
     "upright": "Liderlik zamanı. Vizyonun başkalarına ilham veriyor.",
     "reversed": "Diktatör olma. Esnek liderlik gerekli.",
     "keywords_tr": ["liderlik", "vizyon", "girişimcilik", "karizma"]}
]

# Minor Arcana - Cups (Kupalar) - Water Element
CUPS = [
    {"id": 36, "name": "Ace of Cups", "name_tr": "Kupa Ası", "number": 1, "suit": "Cups",
     "upright": "Yeni aşk, yeni duygular! Kalbin açılıyor.",
     "reversed": "Duygularını bastırıyorsun. Hissetmeye izin ver.",
     "keywords_tr": ["yeni aşk", "duygusal başlangıç", "şefkat", "sezgi"]},
    {"id": 37, "name": "Two of Cups", "name_tr": "İki Kupa", "number": 2, "suit": "Cups",
     "upright": "Karşılıklı sevgi var. Güzel bir bağ kuruluyor.",
     "reversed": "İlişkide dengesizlik. İletişimi güçlendir.",
     "keywords_tr": ["birliktelik", "ortaklık", "uyum", "bağ"]},
    {"id": 38, "name": "Three of Cups", "name_tr": "Üç Kupa", "number": 3, "suit": "Cups",
     "upright": "Kutlama zamanı! Arkadaşlarla güzel anlar.",
     "reversed": "Sosyal hayatını ihmal etme.",
     "keywords_tr": ["kutlama", "dostluk", "neşe", "topluluk"]},
    {"id": 39, "name": "Four of Cups", "name_tr": "Dört Kupa", "number": 4, "suit": "Cups",
     "upright": "Önündeki fırsatları görmüyorsun. Gözlerini aç.",
     "reversed": "Farkındalık geliyor. Yeni şeylere açılıyorsun.",
     "keywords_tr": ["meditasyon", "kayıtsızlık", "içe dönüş", "fırsat"]},
    {"id": 40, "name": "Five of Cups", "name_tr": "Beş Kupa", "number": 5, "suit": "Cups",
     "upright": "Kayıp acısı var ama arkanda hâlâ dolu kupalar var.",
     "reversed": "Geçmişi bırakıyorsun. İyileşme başladı.",
     "keywords_tr": ["kayıp", "üzüntü", "pişmanlık", "kabul"]},
    {"id": 41, "name": "Six of Cups", "name_tr": "Altı Kupa", "number": 6, "suit": "Cups",
     "upright": "Geçmişten güzel anılar. Nostalji var.",
     "reversed": "Geçmişte takılı kalma. Şimdiye dön.",
     "keywords_tr": ["nostalji", "çocukluk", "anılar", "masumiyet"]},
    {"id": 42, "name": "Seven of Cups", "name_tr": "Yedi Kupa", "number": 7, "suit": "Cups",
     "upright": "Çok seçenek var. Hayallerin büyük ama hangisi gerçek?",
     "reversed": "Ayakların yere basıyor. Gerçekçi seçimler yap.",
     "keywords_tr": ["seçenekler", "hayaller", "yanılsama", "karar"]},
    {"id": 43, "name": "Eight of Cups", "name_tr": "Sekiz Kupa", "number": 8, "suit": "Cups",
     "upright": "Arayış içindesin. Bazen bırakmak gerekir.",
     "reversed": "Kaçmak çözüm değil. Yüzleş.",
     "keywords_tr": ["ayrılık", "arayış", "bırakma", "yolculuk"]},
    {"id": 44, "name": "Nine of Cups", "name_tr": "Dokuz Kupa", "number": 9, "suit": "Cups",
     "upright": "Dilek kartı! İsteklerin gerçekleşiyor.",
     "reversed": "Memnuniyetsizlik var. Ne istediğini sorgula.",
     "keywords_tr": ["dilek", "tatmin", "mutluluk", "başarı"]},
    {"id": 45, "name": "Ten of Cups", "name_tr": "On Kupa", "number": 10, "suit": "Cups",
     "upright": "Duygusal doyum! Aile mutluluğu, huzur.",
     "reversed": "Aile ilişkilerinde sorun var. Barış için çalış.",
     "keywords_tr": ["mutluluk", "aile", "uyum", "huzur"]},
    {"id": 46, "name": "Page of Cups", "name_tr": "Kupa Uşağı", "number": 11, "suit": "Cups",
     "upright": "Duygusal bir haber geliyor. Sürpriz olabilir.",
     "reversed": "Duygusal olgunlaşma gerekiyor.",
     "keywords_tr": ["haber", "yaratıcılık", "sezgi", "hayal gücü"]},
    {"id": 47, "name": "Knight of Cups", "name_tr": "Kupa Şövalyesi", "number": 12, "suit": "Cups",
     "upright": "Romantik biri geliyor. Teklif olabilir.",
     "reversed": "Hayalperest olma. Gerçeklere bak.",
     "keywords_tr": ["romantizm", "teklif", "hayal", "çekicilik"]},
    {"id": 48, "name": "Queen of Cups", "name_tr": "Kupa Kraliçesi", "number": 13, "suit": "Cups",
     "upright": "Sezgileri güçlü, şefkatli bir kadın.",
     "reversed": "Duygusal olarak dengesizsin. Kendine bak.",
     "keywords_tr": ["sezgi", "şefkat", "empati", "duygusal zeka"]},
    {"id": 49, "name": "King of Cups", "name_tr": "Kupa Kralı", "number": 14, "suit": "Cups",
     "upright": "Duygusal olgunluk. Dengeli ve bilge biri.",
     "reversed": "Duygularını kontrol edemiyorsun.",
     "keywords_tr": ["duygusal denge", "bilgelik", "diplomasi", "şefkat"]}
]

# Minor Arcana - Swords (Kılıçlar) - Air Element
SWORDS = [
    {"id": 50, "name": "Ace of Swords", "name_tr": "Kılıç Ası", "number": 1, "suit": "Swords",
     "upright": "Zihinsel netlik! Gerçeği görüyorsun.",
     "reversed": "Kafa karışıklığı var. Düşüncelerini topla.",
     "keywords_tr": ["netlik", "gerçek", "başarı", "zeka"]},
    {"id": 51, "name": "Two of Swords", "name_tr": "İki Kılıç", "number": 2, "suit": "Swords",
     "upright": "Karar vermekte zorlanıyorsun. İç sesini dinle.",
     "reversed": "Karar zamanı geldi. Erteleme.",
     "keywords_tr": ["karar", "çıkmaz", "denge", "tereddüt"]},
    {"id": 52, "name": "Three of Swords", "name_tr": "Üç Kılıç", "number": 3, "suit": "Swords",
     "upright": "Kalp kırıklığı ama bu da geçecek.",
     "reversed": "İyileşme başlıyor. Acı azalıyor.",
     "keywords_tr": ["kalp kırıklığı", "acı", "ayrılık", "üzüntü"]},
    {"id": 53, "name": "Four of Swords", "name_tr": "Dört Kılıç", "number": 4, "suit": "Swords",
     "upright": "Dinlenme zamanı. Mola ver, şarj ol.",
     "reversed": "Çok dinlendin, harekete geç.",
     "keywords_tr": ["dinlenme", "iyileşme", "meditasyon", "mola"]},
    {"id": 54, "name": "Five of Swords", "name_tr": "Beş Kılıç", "number": 5, "suit": "Swords",
     "upright": "Kazandın ama bedeli ne? Pyrrhus zaferi.",
     "reversed": "Çatışma bitiyor. Barış zamanı.",
     "keywords_tr": ["çatışma", "yenilgi", "kayıp", "ego"]},
    {"id": 55, "name": "Six of Swords", "name_tr": "Altı Kılıç", "number": 6, "suit": "Swords",
     "upright": "Zor dönemden çıkıyorsun. Yeni sulara doğru.",
     "reversed": "Geçmişi bırakamıyorsun. İlerle.",
     "keywords_tr": ["geçiş", "yolculuk", "iyileşme", "değişim"]},
    {"id": 56, "name": "Seven of Swords", "name_tr": "Yedi Kılıç", "number": 7, "suit": "Swords",
     "upright": "Dikkatli ol. Hile veya aldatma olabilir.",
     "reversed": "Gerçek ortaya çıkıyor.",
     "keywords_tr": ["hile", "strateji", "kaçış", "aldatma"]},
    {"id": 57, "name": "Eight of Swords", "name_tr": "Sekiz Kılıç", "number": 8, "suit": "Swords",
     "upright": "Sıkışmış hissediyorsun ama çıkış var.",
     "reversed": "Özgürleşiyorsun. Engeller kalkıyor.",
     "keywords_tr": ["sınırlama", "korku", "tuzak", "kısıtlama"]},
    {"id": 58, "name": "Nine of Swords", "name_tr": "Dokuz Kılıç", "number": 9, "suit": "Swords",
     "upright": "Endişe ve uykusuz geceler. Korkuların abartılı.",
     "reversed": "Endişeler azalıyor. Rahatlıyorsun.",
     "keywords_tr": ["endişe", "kabus", "stres", "korku"]},
    {"id": 59, "name": "Ten of Swords", "name_tr": "On Kılıç", "number": 10, "suit": "Swords",
     "upright": "Dibe vurdun ama tek yön yukarı!",
     "reversed": "En kötüsü geride. İyileşme başlıyor.",
     "keywords_tr": ["son", "ihanet", "çöküş", "yeniden başlangıç"]},
    {"id": 60, "name": "Page of Swords", "name_tr": "Kılıç Uşağı", "number": 11, "suit": "Swords",
     "upright": "Meraklı enerji. Yeni fikirler geliyor.",
     "reversed": "Dedikodu yapma. Sözlerine dikkat et.",
     "keywords_tr": ["merak", "zeka", "haber", "iletişim"]},
    {"id": 61, "name": "Knight of Swords", "name_tr": "Kılıç Şövalyesi", "number": 12, "suit": "Swords",
     "upright": "Hızlı hareket. Kararlı ve keskin.",
     "reversed": "Düşünmeden hareket etme.",
     "keywords_tr": ["hız", "cesaret", "mücadele", "kararlılık"]},
    {"id": 62, "name": "Queen of Swords", "name_tr": "Kılıç Kraliçesi", "number": 13, "suit": "Swords",
     "upright": "Zeki ve bağımsız. Net görüşlü kadın.",
     "reversed": "Çok keskin olma. Biraz yumuşa.",
     "keywords_tr": ["zeka", "bağımsızlık", "netlik", "dürüstlük"]},
    {"id": 63, "name": "King of Swords", "name_tr": "Kılıç Kralı", "number": 14, "suit": "Swords",
     "upright": "Adil ve mantıklı lider. Doğru karar verir.",
     "reversed": "Çok soğuk olma. Empati gerekli.",
     "keywords_tr": ["otorite", "adalet", "mantık", "liderlik"]}
]

# Minor Arcana - Pentacles (Tılsımlar) - Earth Element
PENTACLES = [
    {"id": 64, "name": "Ace of Pentacles", "name_tr": "Tılsım Ası", "number": 1, "suit": "Pentacles",
     "upright": "Yeni maddi fırsat! Para veya iş haberi.",
     "reversed": "Fırsatı kaçırma. Dikkatli ol.",
     "keywords_tr": ["fırsat", "bolluk", "yeni başlangıç", "para"]},
    {"id": 65, "name": "Two of Pentacles", "name_tr": "İki Tılsım", "number": 2, "suit": "Pentacles",
     "upright": "Denge kuruyorsun. Birden fazla işi idare edebilirsin.",
     "reversed": "Çok fazla şey almışsın. Öncelikleri belirle.",
     "keywords_tr": ["denge", "esneklik", "yönetim", "uyum"]},
    {"id": 66, "name": "Three of Pentacles", "name_tr": "Üç Tılsım", "number": 3, "suit": "Pentacles",
     "upright": "Takım çalışması başarı getiriyor.",
     "reversed": "İş birliği eksik. Birlikte çalışın.",
     "keywords_tr": ["takım çalışması", "ustalık", "işbirliği", "kalite"]},
    {"id": 67, "name": "Four of Pentacles", "name_tr": "Dört Tılsım", "number": 4, "suit": "Pentacles",
     "upright": "Güvenlik istiyorsun ama çok sıkı tutma.",
     "reversed": "Para konusunda rahatla. Cömert ol.",
     "keywords_tr": ["güvenlik", "tutumluluk", "kontrol", "koruma"]},
    {"id": 68, "name": "Five of Pentacles", "name_tr": "Beş Tılsım", "number": 5, "suit": "Pentacles",
     "upright": "Maddi zorluk var ama yardım yakında.",
     "reversed": "Zor dönem bitiyor. İyileşme başlıyor.",
     "keywords_tr": ["zorluk", "kayıp", "yoksunluk", "izolasyon"]},
    {"id": 69, "name": "Six of Pentacles", "name_tr": "Altı Tılsım", "number": 6, "suit": "Pentacles",
     "upright": "Verme ve alma dengesi. Cömertlik ödülleniyor.",
     "reversed": "Dengesiz alışveriş. Adil ol.",
     "keywords_tr": ["cömertlik", "paylaşım", "yardım", "denge"]},
    {"id": 70, "name": "Seven of Pentacles", "name_tr": "Yedi Tılsım", "number": 7, "suit": "Pentacles",
     "upright": "Sabırla bekle. Emeklerin karşılığı geliyor.",
     "reversed": "Sabırsızlık var. Acele etme.",
     "keywords_tr": ["sabır", "yatırım", "değerlendirme", "bekleme"]},
    {"id": 71, "name": "Eight of Pentacles", "name_tr": "Sekiz Tılsım", "number": 8, "suit": "Pentacles",
     "upright": "Çalışkanlık ödülleniyor. Ustalaşıyorsun.",
     "reversed": "Motivasyon düşük. Hedeflerini hatırla.",
     "keywords_tr": ["çalışkanlık", "ustalık", "gelişim", "öğrenme"]},
    {"id": 72, "name": "Nine of Pentacles", "name_tr": "Dokuz Tılsım", "number": 9, "suit": "Pentacles",
     "upright": "Başardın! Özgürlük ve bolluk.",
     "reversed": "Bağımsızlığını kaybetme. Kendine yatırım yap.",
     "keywords_tr": ["bağımsızlık", "lüks", "başarı", "özgürlük"]},
    {"id": 73, "name": "Ten of Pentacles", "name_tr": "On Tılsım", "number": 10, "suit": "Pentacles",
     "upright": "Miras, aile serveti. Uzun vadeli güvenlik.",
     "reversed": "Aile içi mali sorunlar. Planlama yap.",
     "keywords_tr": ["miras", "aile", "zenginlik", "gelenek"]},
    {"id": 74, "name": "Page of Pentacles", "name_tr": "Tılsım Uşağı", "number": 11, "suit": "Pentacles",
     "upright": "Yeni öğrenme fırsatı. Maddi haber geliyor.",
     "reversed": "Fırsatları kaçırıyorsun. Dikkatli ol.",
     "keywords_tr": ["öğrenme", "fırsat", "haber", "çalışkanlık"]},
    {"id": 75, "name": "Knight of Pentacles", "name_tr": "Tılsım Şövalyesi", "number": 12, "suit": "Pentacles",
     "upright": "Sabırlı ve güvenilir. Yavaş ama emin.",
     "reversed": "Çok yavaşsın. Biraz hızlan.",
     "keywords_tr": ["sorumluluk", "sabır", "güvenilirlik", "istikrar"]},
    {"id": 76, "name": "Queen of Pentacles", "name_tr": "Tılsım Kraliçesi", "number": 13, "suit": "Pentacles",
     "upright": "Pratik ve besleyici. Evinin direği.",
     "reversed": "İş-yaşam dengesini kur.",
     "keywords_tr": ["pratiklik", "şefkat", "bolluk", "güvenlik"]},
    {"id": 77, "name": "King of Pentacles", "name_tr": "Tılsım Kralı", "number": 14, "suit": "Pentacles",
     "upright": "Başarılı iş adamı. Maddi güvenlik.",
     "reversed": "Paraya çok odaklanma. Dengeli ol.",
     "keywords_tr": ["zenginlik", "iş başarısı", "güvenlik", "liderlik"]}
]

# Combine all cards
ALL_TAROT_CARDS = MAJOR_ARCANA + WANDS + CUPS + SWORDS + PENTACLES

# Special Combinations
TAROT_COMBINATIONS = {
    "love": [
        {"cards": ["The Lovers", "Ace of Cups"], "meaning_tr": "Yeni bir aşk kapıda! Duygusal olarak çok güçlü bir dönem başlıyor.", "meaning_en": "New love is at the door! A very strong emotional period is starting."},
        {"cards": ["Two of Cups", "The Empress"], "meaning_tr": "Karşılıklı sevgi büyüyor. İlişkiniz derinleşiyor.", "meaning_en": "Mutual love is growing. Your relationship is deepening."},
        {"cards": ["The Tower", "Three of Swords"], "meaning_tr": "Zor bir dönem ama bu seni daha güçlü yapacak.", "meaning_en": "A difficult period but this will make you stronger."},
        {"cards": ["Ten of Cups", "The Sun"], "meaning_tr": "Mutlu son! Hayalindeki aşk gerçekleşiyor.", "meaning_en": "Happy ending! Your dream love is coming true."},
        {"cards": ["Knight of Cups", "The Lovers"], "meaning_tr": "Romantik bir teklif geliyor!", "meaning_en": "A romantic proposal is coming!"},
    ],
    "career": [
        {"cards": ["Ace of Pentacles", "The Magician"], "meaning_tr": "Yeni iş fırsatı! Başarı garantili.", "meaning_en": "New job opportunity! Success guaranteed."},
        {"cards": ["Ten of Wands", "The Emperor"], "meaning_tr": "Çok çalışıyorsun. Delegasyon öğren.", "meaning_en": "You're working too hard. Learn to delegate."},
        {"cards": ["Wheel of Fortune", "Nine of Pentacles"], "meaning_tr": "Şanslı dönem! Maddi kazanç geliyor.", "meaning_en": "Lucky period! Financial gain is coming."},
        {"cards": ["Three of Pentacles", "The Hierophant"], "meaning_tr": "Takım çalışması başarı getiriyor.", "meaning_en": "Teamwork brings success."},
        {"cards": ["Six of Wands", "The Sun"], "meaning_tr": "Zafer senin! Tanınma ve ödül geliyor.", "meaning_en": "Victory is yours! Recognition and reward are coming."},
    ],
    "growth": [
        {"cards": ["The Hermit", "The Star"], "meaning_tr": "İçsel yolculuk sana umut getiriyor.", "meaning_en": "Inner journey brings you hope."},
        {"cards": ["Death", "The Fool"], "meaning_tr": "Yenilenme zamanı! Eski sen ölüyor, yeni sen doğuyor.", "meaning_en": "Time for renewal! Old you dies, new you is born."},
        {"cards": ["Temperance", "Strength"], "meaning_tr": "Denge ve içsel güç birleşiyor. Çok güçlüsün.", "meaning_en": "Balance and inner strength combine. You are very strong."},
        {"cards": ["The High Priestess", "The Moon"], "meaning_tr": "Sezgilerin çok güçlü. İç sesine güven.", "meaning_en": "Your intuition is very strong. Trust your inner voice."},
        {"cards": ["Judgement", "The World"], "meaning_tr": "Büyük bir dönüşüm tamamlanıyor. Yeni seviye!", "meaning_en": "A great transformation is completing. New level!"},
    ]
}

def get_card_by_id(card_id: int):
    """Get a tarot card by its ID"""
    for card in ALL_TAROT_CARDS:
        if card["id"] == card_id:
            return card
    return None

def get_card_by_name(name: str):
    """Get a tarot card by its name"""
    for card in ALL_TAROT_CARDS:
        if card["name"].lower() == name.lower() or card.get("name_tr", "").lower() == name.lower():
            return card
    return None

def check_combinations(cards: list, lang: str = "tr"):
    """Check if drawn cards form any special combination"""
    card_names = [c["name"] for c in cards]
    found_combinations = []
    
    for category, combos in TAROT_COMBINATIONS.items():
        for combo in combos:
            if all(name in card_names for name in combo["cards"]):
                meaning_key = "meaning_tr" if lang == "tr" else "meaning_en"
                found_combinations.append({
                    "category": category,
                    "cards": combo["cards"],
                    "meaning": combo[meaning_key]
                })
    
    return found_combinations
