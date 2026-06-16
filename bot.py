import requests
from PIL import Image, ImageDraw, ImageFont
import datetime
import os

# ==========================================
# 1. AYARLAR (GÜVENLİ ÇEKİM - GITHUB ACTIONS İÇİN)
# ==========================================
API_KEY = os.environ.get("51767f38d1182d6a76c40b8f5e30b896")
TELEGRAM_TOKEN = os.environ.get("8675874600:AAEnfPFrb3s46iO-pFxFGNYa3hXmfEldrsg")
TELEGRAM_CHAT_ID = os.environ.get("5956562475")
KLASOR_IKON = "ikonlar"

if not API_KEY or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("HATA: API anahtarları veya Telegram bilgileri eksik! GitHub Secrets kısmını kontrol et.")
    exit()

def get_ikon_adi(durum_id):
    if durum_id == 800: return "gunesli.png"
    elif 801 <= durum_id <= 802: return "azbulutlu.png"
    elif 803 <= durum_id <= 804: return "bulutlu.png"
    elif 300 <= durum_id <= 531: return "yagmurlu.png"
    elif 600 <= durum_id <= 622: return "karli.png"
    elif 200 <= durum_id <= 232: return "firtinali.png"
    elif 701 <= durum_id <= 781: return "sisli.png"
    else: return "bulut.png"

# ==========================================
# 2. HAVA DURUMUNU ÇEK (ANLIK + SAATLİK)
# ==========================================
print("Hava durumu verileri çekiliyor...")

url_anlik = f"http://api.openweathermap.org/data/2.5/weather?q=Ayvalik&appid={API_KEY}&units=metric&lang=tr"
cevap_anlik = requests.get(url_anlik).json()

sicaklik_anlik = round(cevap_anlik["main"]["temp"])
durum_anlik = cevap_anlik["weather"][0]["description"].capitalize()
ikon_anlik_dosya = get_ikon_adi(cevap_anlik["weather"][0]["id"])
ikon_anlik_yol = os.path.join(KLASOR_IKON, ikon_anlik_dosya)

print(f"Mevcut Durum: {sicaklik_anlik}°C, {durum_anlik}")

url_tahmin = f"http://api.openweathermap.org/data/2.5/forecast?q=Ayvalik&appid={API_KEY}&units=metric&lang=tr"
cevap_tahmin = requests.get(url_tahmin).json()
saatlik_veriler = cevap_tahmin["list"][:4] 

# ==========================================
# 3. GÖRSELİ HAZIRLA
# ==========================================
print("Görsel hazırlanıyor...")

try:
    resim = Image.open("sablon.jpg").convert("RGBA")
except FileNotFoundError:
    print("HATA: 'sablon.jpg' dosyası klasörde yok!")
    exit()

cizim = ImageDraw.Draw(resim)

try:
    font_sicaklik = ImageFont.truetype("Montserrat-ExtraBold.ttf", 600)
    font_detay = ImageFont.truetype("OpenSans_Condensed-Light.ttf", 180)
    font_saat = ImageFont.truetype("OpenSans_Condensed-Light.ttf", 90)
    font_saatlik_sicaklik = ImageFont.truetype("Montserrat-ExtraBold.ttf", 100)
except OSError:
    print("HATA: Font dosyaları bulunamadı! İsimleri kontrol et.")
    exit()

aylar = {
    "01": "OCAK", "02": "ŞUBAT", "03": "MART", "04": "NİSAN",
    "05": "MAYIS", "06": "HAZİRAN", "07": "TEMMUZ", "08": "AĞUSTOS",
    "09": "EYLÜL", "10": "EKİM", "11": "KASIM", "12": "ARALIK"
}
bugun = datetime.datetime.now()
tarih_gorsel = f"{bugun.day} {aylar[bugun.strftime('%m')]} {bugun.year}"
tarih_metni = bugun.strftime("%d.%m.%Y")

# --- BÖLÜM 1: ANA (DEV) BİLGİLER ---
X_SOL_HIZA = 150
Y_IKON = 250
Y_DERECE = 800
Y_DETAY = 1600

if os.path.exists(ikon_anlik_yol):
    ikon_resmi = Image.open(ikon_anlik_yol).convert("RGBA").resize((500, 500))
    resim.paste(ikon_resmi, (X_SOL_HIZA, Y_IKON), ikon_resmi) 

cizim.text((X_SOL_HIZA, Y_DERECE), f"{sicaklik_anlik}°C", font=font_sicaklik, fill="white") 
cizim.text((X_SOL_HIZA, Y_DETAY), f"{durum_anlik}\n{tarih_gorsel}", font=font_detay, fill="white") 

# --- BÖLÜM 2: SAATLİK ÇİZELGE ---
Y_SAATLIK_BASLANGIC = 2100 
BOSLUK = 350 

for i, tahmin in enumerate(saatlik_veriler):
    ham_saat = tahmin["dt_txt"] 
    saat_metni = ham_saat.split(" ")[1][:5] 
    
    saatlik_sicaklik = f"{round(tahmin['main']['temp'])}°"
    saatlik_ikon_dosya = get_ikon_adi(tahmin["weather"][0]["id"])
    saatlik_ikon_yol = os.path.join(KLASOR_IKON, saatlik_ikon_dosya)
    
    X_GUNCEL = X_SOL_HIZA + (i * BOSLUK)
    
    cizim.text((X_GUNCEL, Y_SAATLIK_BASLANGIC), saat_metni, font=font_saat, fill="white")
    
    if os.path.exists(saatlik_ikon_yol):
        mini_ikon = Image.open(saatlik_ikon_yol).convert("RGBA").resize((120, 120))
        resim.paste(mini_ikon, (X_GUNCEL, Y_SAATLIK_BASLANGIC + 130), mini_ikon)
        
    cizim.text((X_GUNCEL, Y_SAATLIK_BASLANGIC + 280), saatlik_sicaklik, font=font_saatlik_sicaklik, fill="white")

yeni_resim_adi = "bugun_hava.jpg"
final_resim = resim.convert("RGB")
final_resim.save(yeni_resim_adi, quality=80, optimize=True)
print("Görsel başarıyla oluşturuldu!")

# ==========================================
# 4. TELEGRAM'A GÖNDER
# ==========================================
print("Telegram'a gönderiliyor... Lütfen bekleyin.")

caption = f"Günaydın! ☀️ {tarih_metni} tarihinde Ayvalık'ta hava {sicaklik_anlik}°C ve {durum_anlik}. \n\n#ayvalık #cunda #havadurumu"

telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

try:
    with open(yeni_resim_adi, "rb") as photo:
        gonderim_cevabi = requests.post(
            telegram_url, 
            data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, 
            files={"photo": photo},
            timeout=30 
        )

    if gonderim_cevabi.status_code == 200:
        print("İşlem Tamam! Görsel Telegram'a başarıyla gönderildi.")
    else:
        print("Telegram'a gönderim sırasında hata:", gonderim_cevabi.text)
except Exception as e:
    print(f"HATA: Beklenmeyen bir bağlantı sorunu oluştu: {e}")
