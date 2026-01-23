import os
import time
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from vars import BOT TOKEN
from vars import API HASH
from vars import API ID

app = Client(
    "fb_auto_best_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

print("Bot Started...")

# ==== HELPERS ====

def format_bytes(size):
    if not size:
        return "N/A"
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"

async def progress(current, total, message: Message, start_time):
    now = time.time()
    diff = now - start_time
    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        elapsed = round(diff) * 1000
        remaining = round((total - current) / speed) * 1000 if speed > 0 else 0
        eta = time.strftime('%H:%M:%S', time.gmtime(remaining / 1000))

        try:
            await message.edit(
                f"Uploading...\n"
                f"Percent: {percentage:.1f}%\n"
                f"Size: {format_bytes(current)} / {format_bytes(total)}\n"
                f"Speed: {format_bytes(speed)}/s\n"
                f"ETA: {eta}"
            )
        except:
            pass

# ==== MAIN HANDLER ====

@app.on_message(filters.private & filters.text)
async def auto_best(client, message: Message):

    url = message.text.strip()

    if "facebook.com" not in url and "fb.watch" not in url:
        return await message.reply("Please provide a valid Facebook video link.")

    status = await message.reply("Finding best quality...")

    try:
        # Extract info only (no download)
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "Facebook Video")

        file_path = f"downloads/{int(time.time())}.mp4"

        ydl_opts = {
            "outtmpl": file_path,
            "quiet": True,
            "format": "best",     # <-- Auto best quality
        }

        # Downloading best quality
        await status.edit("Downloading high-quality video...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Upload to Telegram
        await status.edit("Uploading video...")
        start_time = time.time()

        await client.send_video(
            chat_id=message.chat.id,
            video=file_path,
            caption=f"{title}\nAuto Best Quality",
            progress=progress,
            progress_args=(status, start_time),
            supports_streaming=True
        )

        await status.delete()

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await status.edit(f"Error: {str(e)}")


if __name__ == "__main__":
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    app.run()
