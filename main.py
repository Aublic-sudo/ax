import os import json import cloudscraper import time from base64 import b64decode from Crypto.Cipher import AES from Crypto.Util.Padding import unpad from pyrogram import Client, filters from pyrogram.types import Message from dotenv import load_dotenv

Load environment variables

load_dotenv() BOT_TOKEN = os.getenv("BOT_TOKEN") API_ID = int(os.getenv("API_ID")) API_HASH = os.getenv("API_HASH") AUTH_USERS = os.getenv("AUTH_USERS", "").split(",")

AES Decrypt Function

def decrypt_link(encrypted_link): try: key = "638udh3829162018".encode("utf8") iv = "fedcba9876543210".encode("utf8") encrypted_link = encrypted_link.strip().replace('-', '+').replace('_', '/') encrypted_link += '=' * (-len(encrypted_link) % 4) cipher = AES.new(key, AES.MODE_CBC, iv) ciphertext = b64decode(encrypted_link) plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size) return plaintext.decode() except Exception as e: return f"Error: {str(e)}"

Initialize Bot

bot = Client( "classx_combined_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN )

user_sessions = {}

RG Vikramjeet Handler

@bot.on_message(filters.command("rgvikramjeet") & filters.user(AUTH_USERS)) async def rgvikramjeet_handler(client: Client, message: Message): await message.reply("Send UserID:TOKEN for RG Vikramjeet") user_sessions[message.from_user.id] = {"stage": "rg_waiting_token"}

WebSankul Handler

@bot.on_message(filters.command("websankul") & filters.user(AUTH_USERS)) async def websankul_handler(client: Client, message: Message): await message.reply("Send your Registered Phone Number for WebSankul") user_sessions[message.from_user.id] = {"stage": "web_waiting_phone"}

Universal Message Handler

@bot.on_message(filters.text & filters.user(AUTH_USERS)) async def universal_handler(client: Client, message: Message): user_id = message.from_user.id session = user_sessions.get(user_id, {})

if not session:
    return

if session.get("stage") == "rg_waiting_token":
    await handle_rgvikramjeet_flow(client, message, session)
elif session.get("stage") == "web_waiting_phone":
    await handle_websankul_phone(client, message, session)
elif session.get("stage") == "web_waiting_otp":
    await handle_websankul_otp(client, message, session)

RG Vikramjeet Flow

async def handle_rgvikramjeet_flow(client, message, session): try: userid, token = message.text.split(":") scraper = cloudscraper.create_scraper() headers = { "Host": "rgvikramjeetapi.classx.co.in", "Client-Service": "Appx", "Auth-Key": "appxapi", "User-Id": userid, "Authorization": token } res = scraper.get( f"https://rgvikramjeetapi.classx.co.in/get/mycourse?userid={userid}", headers=headers )

if res.status_code == 200 and res.json().get('data'):
        batches = res.json()['data']
        reply = "**BATCH-ID - BATCH NAME**\n"
        for batch in batches:
            reply += f"{batch['id']} - {batch['course_name']}\n"
        await message.reply(reply)
        session.update({"stage": "rg_batch_selected", "userid": userid, "token": token, "scraper": scraper})
    else:
        await message.reply("No batches found or invalid token.")
except Exception as e:
    await message.reply(f"Error: {e}")

WebSankul OTP Flow

async def handle_websankul_phone(client, message, session): phone_number = message.text.strip() scraper = cloudscraper.create_scraper()

payload = {"mobile": phone_number}
headers = {
    "Host": "websankullive.classx.co.in",
    "Client-Service": "Appx",
    "Auth-Key": "appxapi"
}

res = scraper.post("https://websankullive.classx.co.in/sendotp", headers=headers, data=payload)

if res.status_code == 200 and res.json().get("status") == True:
    await message.reply("OTP sent! Now send the OTP.")
    session.update({"stage": "web_waiting_otp", "phone_number": phone_number, "scraper": scraper})
else:
    await message.reply("Failed to send OTP. Check your number.")

async def handle_websankul_otp(client, message, session): otp = message.text.strip() scraper = session["scraper"]

payload = {"mobile": session["phone_number"], "otp": otp}
headers = {
    "Host": "websankullive.classx.co.in",
    "Client-Service": "Appx",
    "Auth-Key": "appxapi"
}

res = scraper.post("https://websankullive.classx.co.in/verifyotp", headers=headers, data=payload)

if res.status_code == 200 and res.json().get("status") == True:
    token = res.json()["token"]
    await message.reply(f"Logged in! Your token: `{token}`")
    session.clear()
else:
    await message.reply("OTP verification failed.")

if name == 'main': bot.run()

