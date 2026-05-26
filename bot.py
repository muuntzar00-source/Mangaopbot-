import os
import re
import cloudscraper
from pyrogram import Client, filters
from PIL import Image, ImageDraw
from fpdf import FPDF

# ================= CONFIG =================

API_ID = 37558426
API_HASH = "5b02bea1ece40e219ecd7b5148cf08a2"
BOT_TOKEN = "8777225560:AAFvgc9GFNFdS0HqqrwQ2BeNOYTtfps7CD0"

OWNER_ID = 1287794053
RIGHTS = "@pp4p44"

app = Client(
    "manga_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

scraper = cloudscraper.create_scraper()
HEADERS = {"User-Agent": "Mozilla/5.0"}

TEMP = "temp"
os.makedirs(TEMP, exist_ok=True)

# ================= CLEAN =================

def clean():
    for f in os.listdir(TEMP):
        try:
            os.remove(f"{TEMP}/{f}")
        except:
            pass

# ================= EXTRACT IMAGES =================

def get_images(url):

    r = scraper.get(url, headers=HEADERS, timeout=60)
    html = r.text

    images = set()

    # روابط مباشرة
    images.update(re.findall(r'https?://[^"\']+\.(?:jpg|jpeg|png|webp)', html))

    # من scripts
    images.update(re.findall(r'https?://[^"\']+\.(?:jpg|jpeg|png|webp)', html, re.S))

    clean_list = []

    for img in images:
        if any(x in img.lower() for x in ["logo", "ads", "icon", "avatar"]):
            continue
        clean_list.append(img)

    return list(dict.fromkeys(clean_list))

# ================= PDF =================

def create_pdf(images, name):

    pdf = FPDF()
    i = 0

    for url in images:
        try:
            r = scraper.get(url, timeout=30)

            path = f"{TEMP}/{i}.jpg"
            with open(path, "wb") as f:
                f.write(r.content)

            img = Image.open(path).convert("RGB")

            draw = ImageDraw.Draw(img)
            draw.text((20, 20), RIGHTS, fill=(255, 0, 0))

            img.save(path, quality=85)

            pdf.add_page()
            pdf.image(path, 0, 0, 210)

            i += 1

        except:
            pass

    file = f"{name}_{RIGHTS}.pdf"
    pdf.output(file)
    return file

# ================= NAME =================

def manga_name(url):
    return url.strip("/").split("/")[-2]

# ================= BOT =================

@app.on_message(filters.text)
async def handler(_, msg):

    if msg.from_user.id != OWNER_ID:
        return

    url = msg.text.strip()

    if "3asq.org" not in url:
        return await msg.reply_text("❌ هذا البوت يعمل فقط على موقع العاشق")

    status = await msg.reply_text("⏳ جاري التحميل...")

    try:
        clean()

        images = get_images(url)

        if not images:
            return await status.edit("❌ لم يتم العثور على صور")

        await status.edit(f"📥 تم العثور على {len(images)} صفحة")

        name = manga_name(url)
        pdf = create_pdf(images, name)

        await msg.reply_document(pdf, caption="✅ تم التحويل بنجاح")

        os.remove(pdf)
        clean()

        await status.delete()

    except Exception as e:
        await status.edit(f"❌ خطأ:\n{e}")

print("Bot Running...")
app.run()
