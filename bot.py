import os
import re
import asyncio
from pyrogram import Client, filters
from playwright.async_api import async_playwright
from fpdf import FPDF
from PIL import Image
import requests

API_ID = 37558426
API_HASH = "5b02bea1ece40e219ecd7b5148cf08a2"
BOT_TOKEN = "8777225560:AAFvgc9GFNFdS0HqqrwQ2BeNOYTtfps7CD0"

OWNER_ID = 1287794053
RIGHTS = "@pp4p44"

app = Client("manga_bot", API_ID, API_HASH, BOT_TOKEN)

TEMP = "temp"
os.makedirs(TEMP, exist_ok=True)

def clean():
    for f in os.listdir(TEMP):
        try:
            os.remove(f"{TEMP}/{f}")
        except:
            pass


# ================= BROWSER SCRAPER =================

async def get_images(url):
    images = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(8000)  # wait JS load

        imgs = await page.eval_on_selector_all(
            "img",
            "els => els.map(e => e.src || e.getAttribute('data-src'))"
        )

        for img in imgs:
            if not img:
                continue

            if any(x in img.lower() for x in ["logo", "ads", "icon"]):
                continue

            if img.startswith("//"):
                img = "https:" + img

            if img.endswith((".jpg", ".png", ".webp", ".jpeg")):
                images.append(img)

        await browser.close()

    return list(dict.fromkeys(images))


# ================= PDF =================

def create_pdf(images, name):
    pdf = FPDF()
    i = 0

    for url in images:
        try:
            r = requests.get(url, timeout=30)

            path = f"{TEMP}/{i}.jpg"
            with open(path, "wb") as f:
                f.write(r.content)

            img = Image.open(path).convert("RGB")
            img.save(path, quality=85)

            pdf.add_page()
            pdf.image(path, 0, 0, 210)

            i += 1

        except:
            pass

    file = f"{name}_{RIGHTS}.pdf"
    pdf.output(file)
    return file


def manga_name(url):
    return url.strip("/").split("/")[-2]


# ================= BOT =================

@app.on_message(filters.text)
async def handler(_, msg):

    if msg.from_user.id != OWNER_ID:
        return

    url = msg.text.strip()

    if "3asq.org" not in url:
        return await msg.reply_text("❌ هذا النظام يعمل فقط على العاشق")

    status = await msg.reply_text("☁️ جاري فتح الموقع في سيرفر سحابي...")

    try:
        clean()

        images = await get_images(url)

        if not images:
            return await status.edit("❌ لم يتم العثور على صفحات")

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
