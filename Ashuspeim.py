import requests
import json
import os
import time
import random
import threading
import websocket
import re
import aiohttp
import asyncio
import urllib.parse
import string
import sys
import logging
import base64

# ==================== LOGGING ====================
logging.basicConfig(level=logging.INFO)

# ==================== OWNER CONFIG ====================
OWNER_ID = "722351377157980170"

# ==================== TOKENS ====================
TOKENS = [
    "MTUxOTY0OTE3NzgxMjk5MjA0Mg.G4iPik.oPkZnZgEgIIYNAoQc-58FjmXigYkMFTyPOO7oA",
]

TOKENS = [t for t in TOKENS if t and t.strip() and not t.startswith('.')]

# ==================== FILES ====================
SUDO_FILE = "sudo_users.json"
TOKENS_FILE = "tokens2.txt"
GCNAME_FILE = "gcname.txt"
AUTOREPLY_FILE = "auto_responses.json"

# ==================== PREFIX ====================
PREFIX = "$"

# ==================== FLAGS ====================
ACTIVE_NC_CHANNELS = {}
ACTIVE_SPAM_CHANNELS = {}
AUTOREPLY_TARGETS = {}
AUTOREACT_EMOJIS = {}
multi_running = {}
drown_running = False
pack_running = False
repeat_running = False
counter_running = False
spammingss = False
START_TIME = time.time()

# ==================== HIGH-SPEED CONFIGS ====================
NC_DELAY = 0.001
SPAM_DELAY = 0.001
PARALLEL_SPAM = 15
PARALLEL_NC = 15

# Global Persistent Session for HTTP Requests
http_session = None

# ==================== EXACT FAVORITE NC LIST (UNICODE ENCODED FOR TERMUX SAFETY) ====================
# Uses \u200b / \u0e47 / \U0001f525 to preserve exact invisible symbols and 🔥 emojis without Termux syntax crash
_FIRE = "\U0001f525"
_INVIS = "\u200b\u0e47" * 3

NC_LIST = [
    f"{{target}} ᴛᴇʀɪ ᴍᴋᴄ ʟᴡᴅᴇ ᴄʜxᴅ-{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}",
    f"{{target}} ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʙʜᴏsᴅᴀ-{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}",
    f"{{target}} ᴛᴇʀɪ ʙʜᴇɴ ᴋᴀ ʟᴜɴᴅ-{_INVIS}{_FIRE}{_INVIS}{_FIRE}{_INVIS}{_FIRE}",
    f"{{target}} ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋɪ ᴀɴᴋʜ-{_INVIS}{_FIRE}",
]

# ==================== SPAM MESSAGES ====================
SPAM_MESSAGES = [
    "# \u0f39 \ud83d\udd38\u0f3a ##\ud835\ude08\ud835\ude34\ud835\ude29\ud835\ude36#\ud835\ude12\ud835\ude2f \ud835\ude1b\ud835\ude30\ud835\ude31 #\ud835\ude19\u1d07\ud835\ude15\ud835\ude0e\u20e0\ud835\ude00\u1d07 #\ud835\ude13\u1d00\ud835\ude0e\u1d03\u1d07 #\u026a\ud835\ude00 #s\ud835\ude00\u1d07 #\ud835\ude1b\u1d07\u029d #\ud835\ude1b\u1d0f #\u1d0b\u1d0f #\ud835\ude08\u1d0d\u1d0d\u1d00 #\ud835\ude00\u029c\ud835\ude1c\u1d03\ud835\ude1b\u026a #\ud835\ude08\u1d00\u026aI\u20e0",
    "# \u0f39\ud838\ude38\u0f3a ##\ud835\ude08\ud835\ude34\ud835\ude29\ud835\ude36#\ud835\ude12\ud835\ude2f \ud835\ude1b\ud835\ude30\ud835\ude31 #\ud835\ude19\u1d07\ud835\ude15\ud835\ude0e\u20e0\ud835\ude00\u1d07 #\ud835\ude13\u1d00\ud835\ude0e\u1d03\u1d07 #\u026a\ud835\ude00 #s\ud835\ude00\u1d07 #\ud835\ude1b\u1d07\u029d #\ud835\ude1b\u1d0f #\u1d0b\u1d0f #\ud835\ude08\u1d0d\u1d0d\u1d00 #\ud835\ude00\u029c\ud835\ude1c\u1d03\ud835\ude1b\u026a #\ud835\ude08\u1d00\u026aI\u20e0",
]

# ==================== REPLY TEXTS ====================
REPLY_TEXTS = [
    "\ud835\ude1e\u1d0f \u029d\u029c\u026a \u1d0b\u028f\u1d00 \u1d05\u026a\u0274 \u1d1b\u028c\u1d07 \u1d0a\u1d00\u029d \u1d1b\u0280\u028f \u1d0d\u1d00\u1d00 \u1d0d\u1d1b\u029c\u1d0a\u1d07 \ud835\ude08\u1d18\u0274\u1d00 \ud835\ude00\u029c\u1d0b\u1d1b \ud835\ude05\u1d07\u1d1b\u026a \u1d1b\u029c\u026a \ud83d\udc94",
    "\ud835\ude08\u1d18\u1d00\u1d1a \ud835\ude15\u026a\u1d03\u029c\u1d07 \ud835\ude0e\u1d07\u029d\u1d00\u1d00\u1d0d \ud83e\udd22",
    "\ud835\ude1b\u0280\u028f \ud835\ude0d\u1d00\u1d00 \u0274\u1d07 \ud835\ude00\u029c\u1d0b\u1d1b\u0274\u1d07 \ud835\ude0d\u1d00\u026a \u0262\u1d0f\u029f\u1d05 \ud835\ude0d\u1d07\u1d05\u1d00\u029f \ud835\ude00\u1d07\u1d07\u1d1b\u1d00 \ud83d\udc51",
    "\ud835\ude1b\u1d07\u0280\u026a \ud835\ude0d\u1d00\u1d00 \u1d0b\u026a \ud835\ude00\u029c\u1d0b\u1d1b \ud835\ude0d\u1d07 \ud835\ude0d\u1d07\u0280\u1d00 \ud835\ude13\u1d01\u0274\u1d05 \ud83d\udd95",
    "\ud835\ude09\u029c\u1d0f\ua731\u1d00\u1d18\u026a\u1d0b\u1d07 \ud835\ude08\u1d18\u0274\u026a \ud835\ude09\u1d07\u029c\u1d07\u0274 \ud835\ude00\u029c\u1d1b\u1d00 \ud83d\udd95",
    "Chalti hai gadi chalta hai ghoda daldu kya aapke gand me lawda",
    "Aakh kya marti hai mar de talwar aagar karti hai saccha pyar to khol de salvar",
    "Aao kuch khelte hai aap tang uthao ham pelte hai",
    "teri maa k bhosde mai MDH CHANA MASALA daal k tere baap ko vo spicy bhosda khila dunga \ud83e\udd75\ud83e\udd22",
]

# ==================== LONG SPAM TEMPLATES ====================
LONG_SPAM_TEMPLATES = [
    "{target} \ud835\ude08\ud835\ude34\ud835\ude29\ud835\ude36 \ud835\udc11\ud835\udc2b\ud835\udc21\ud835\udc2c \ud835\udc32\ud835\udc2d\ud835\udc2e " * 150,
    "{target} \ud835\udc13\ud835\udc1e\ud835\udc2b\ud835\udc22 \ud835\udc0d\ud835\udc1a\ud835\udc1a \ud835\udc0a\ud835\udc1a \ud835\udc01\ud835\udc21\ud835\udc2d\ud835\udc2c\ud835\udc1d\ud835\udc1a " * 150,
    "{target} \ud835\udc01\ud835\udc1e\ud835\udc21\ud835\udc1e\ud835\udc27 \ud835\udc0a\ud835\udc1e \ud835\udc0b\ud835\udc1a\ud835\udc2e\ud835\udc1d\ud835\udc1e " * 150,
    "{target} \ud835\udc0d\ud835\udc1a\ud835\udc1d\ud835\udc1a\ud835\udc2b\ud835\udc0c\ud835\udc21\ud835\udc2d " * 150,
    "{target} \ud835\udc01\ud835\udc21\ud835\udc2d\ud835\udc2c\ud835\udc1d\ud835\udc22\ud835\udc2a\ud835\udc1e " * 150,
    "{target} \ud835\udc0c\ud835\udc21\ud835\udc2d\ud835\udc22\ud835\udc32\ud835\udc1a " * 150,
    "{target} \ud835\udc02\ud835\udc1a\ud835\udc27\ud835\udc1d\ud835\udc2e " * 150,
    "{target} \ud835\udc0a\ud835\udc2e\ud835\udc2d\ud835\udc2d\ud835\udc1e \ud835\udc0a\ud835\udc22 \ud835\udc00\ud835\udc2e\ud835\udc2b\ud835\udc1a\ud835\udc1d " * 150,
    "{target} \ud835\udc13\ud835\udc1e\ud835\udc2b\ud835\udc22 \ud835\udc0c\ud835\udc2e\ud835\udc2d\ud835\udc2d\ud835\udc32 \ud835\udc04\ud835\udc22 \ud835\udc05\ud835\udc2e\ud835\udc1d\ud835\udc1d\ud835\udc22 " * 150,
    "{target} \ud835\udc13\ud835\udc1e\ud835\udc2b\ud835\udc22 \ud835\udc01\ud835\udc1e\ud835\udc21\ud835\udc1e\ud835\udc27 \ud835\udc04\ud835\udc22 \ud835\udc00\ud835\udc27\ud835\udc2a\ud835\udc21 " * 150,
    "{target} L + RATIO + MALD + COPE " * 100,
    "{target} GET DUBAYA BY \ud835\ude08\ud835\ude34\ud835\ude29\ud835\ude36 " * 120,
    "{target} \ud835\udc13\ud835\udc2e \ud835\udc02\ud835\udc1a\ud835\udc2b \ud835\udc02\ud835\udc21\ud835\udc2e\ud835\udc2a\ud835\udc1a \ud835\udc21\ud835\udc1a\ud835\udc22 " * 140,
    "{target} \ud835\udc00\ud835\udc2e\ud835\udc2a\ud835\udc1a\ud835\udc2d \ud835\udc0c\ud835\udc1e\ud835\udc22\ud835\udc27 \ud835\udc11\ud835\udc1e\ud835\udc21 " * 150,
    "{target} \ud835\ude08\ud835\ude34\ud835\ude29\ud835\ude36 \ud835\udc0e\ud835\udc0d \ud835\udc13\ud835\udc0e\ud835\udc0f " * 150,
]

def get_long_spam(target_mention):
    template = random.choice(LONG_SPAM_TEMPLATES)
    base = template.replace("{target}", target_mention)
    if len(base) > 2000:
        base = base[:1997] + "..."
    return base

# ==================== DROWN LISTS ====================
hindi_drown = [
    "तू बेकार है {mention} \ud83d\udc80",
    "तेरी माँ का भोसड़ा {mention}",
    "तू गधा है {mention} \ud83e\udecf",
    "तेरी बहन की आँख {mention}",
    "तू पैदा ही नहीं होना चाहिए था {mention}",
    "तेरी औकात नहीं है {mention} \u2620\ufe0f",
    "तू हार चुका है {mention} \ud83d\udd25",
    "बंद कर मुँह अपना {mention} \ud83d\uddd1\ufe0f",
    "तू एक निकम्मा है {mention} \ud83d\ude02",
    "\ud835\ude08\ud835\ude34\ud835\ude29\ud835\ude36 runs you {mention} \ud83d\udcaf",
]

hinglish_drown = [
    "Teri maa ka bhosda {mention} \ud83d\udc80",
    "Madarchod {mention}",
    "Bhosdike {mention} \ud83e\udecf",
    "Chutiya hai tu {mention}",
    "Behen ke laude {mention}",
    "Aukaat mein reh {mention} \ud83d\udd25",
    "\ud835\ude08\ud835\ude34\ud835\ude29\ud835\ude36 runs you {mention} \ud83d\udcaf",
    "Loser hai tu {mention} \ud83d\ude02",
    "Band kar apna munh {mention} \ud83d\uddd1\ufe0f",
    "Kutta saala {mention} \u2620\ufe0f",
]

english_drown = [
    "You're trash {mention} \ud83d\udc80",
    "You're a loser {mention}",
    "\ud835\ude08\ud835\ude34\ud835\ude29\ud835\ude36 runs you {mention} \ud83d\udd25",
    "You're worthless {mention} \ud83d\uddd1\ufe0f",
    "Stay mad {mention} \ud83d\ude02",
    "Get ratio'd {mention} \ud83d\udcaf",
    "You lost {mention} \u2620\ufe0f",
    "Nobody likes you {mention}",
    "Cope harder {mention} \ud83d\ude08",
    "L + ratio + mald {mention} \ud83e\udecf",
]

punjabi_lines = [
    "\u0a2c\u0a47 \u0a1a\u0a41\u0a2a \u0a15\u0a30 \u0a1c\u0a3e \u0a13\u0a02 {mention} \ud83d\udc80",
    "\u0a24\u0a42\u0a28\u0a42\u0a02 \u0a15\u0a4b\u0a08 \u0a28\u0a3 puzzle\u0a40\u0a02 \u0a2a\u0a41\u0a0b\u0a26\u0a3e {mention} \ud83d\uddd1\ufe0f",
    "\u0a24\u0a42\u0a02 \u0a1c\u0a3f\u0a24 \u0a28\u0a39\u0a40\u0a02 \u0a38\u0a15\u0a26\u0a3e \u0a38\u0a3e\u0a21\u0a47 \u0a24\u0a4b\u0a02 {mention} \ud83d\udd25",
    "\u0a2a\u0a3e\u0a17\u0a32 \u0a1c\u0a3f\u0a39\u0a3e \u0a2c\u0a02\u0a26\u0a3e \u0a39\u0a48\u0a02 \u0a24\u0a42\u0a02 {mention} \ud83d\ude02",
    "\u0a08\u0a1f\u0a30\u0a28\u0a32 \u0a28\u0a47 \u0a24\u0a42\u0a28\u0a42\u0a02 \u0a21\u0a41\u0a2c\u0a4b\u0a07\u0a06 {mention} \u2620\ufe0f",
    "\u0a1c\u0a3e\u0a39 \u0a13\u0a25\u0a47 \u0a28\u0a71\u0a38 {mention} \ud83d\ude08",
    "\u0a24\u0a47\u0a30\u0a40 \u0a15\u0a4b\u0a08 \u0a10\u0a15\u0a3e\u0a24 \u0a28\u0a39\u0a40\u0a02 {mention} \ud83d\udcaf",
    "\u0a30\u0a4b\u0a23\u0a3e \u0a2c\u0a02\u0a26 \u0a15\u0a30 {mention} \ud83e\udd21",
    "\u0a2e\u0a3e\u0a02 \u0a28\u0a42\u0a02 \u0a2a\u0a41\u0a0b \u0a15\u0a47 \u0a06 {mention}",
    "\u0a18\u0a30 \u0a1a\u0a32\u0a3e \u0a1c\u0a3e \u0a1a\u0a41\u0a2a\u0a1a\u0a3e\u0a2a {mention} \ud83c\udf0a",
]

urdu_lines = [
    "\u0628\u06d2 \u063a\u0627\u0624\u0628 \u06c1\u0648 \u062c\u0627 \u06c1\u06cc\u0627\u06ba \u0633\u06d2 {mention} \ud83d\udc80",
    "\u062a\u062c\u06be \u0633\u06d2 \u06a9\u0648\u0624\u06cc \u0628\u06c1\u06cc\u06ba \u0688\u0631\u062a\u0627 {mention} \ud83d\ude02",
    "\u0627\u06cc\u067f\u0631\u0646\u0644 \u0628\u06d2 \u062a\u062c\u06be\u06d2 \u062e\u062a\u0645 \u06a9\u0631 \u062f\u06cc\u0627 {mention} \ud83d\udd25",
    "\u062a\u0648 \u06c1\u0645\u06cc\u0634\u06c1 \u06c1\u0627\u0631\u062a\u0627 \u06c1\u06d2 {mention} \u2620\ufe0f",
    "\u0628\u06a9\u0648\u0627\u0633 \u0628\u0620\u062f \u06a9\u0631 {mention} \ud83d\uddd1\ufe0f",
    "\u062a\u06cc\u0631\u06cc \u0645\u0627\u06ba \u0631\u0648 \u0631\u06c1\u06cc \u06c1\u06d2 \u062a\u06cc\u0631\u06cc \u0648\u062c\u06c1 \u0633\u06d2 {mention} \ud83d\udc80",
    "\u0620\u06a9\u0644 \u062c\u0627 \u06c1\u06cc\u0627\u06ba \u0633\u06d2 {mention} \ud83e\udd21",
    "\u062a\u062c\u06be \u0645\u06cc\u06ba \u06a9\u0648\u0624\u06cc \u062f\u0645 \u0628\u06c1\u06cc\u06ba {mention} \ud83d\ude08",
    "\u0627\u06cc\u067f\u0631\u0646\u0644 \u062f\u0631 \u0622\u0620\u06d2 \u06a9\u06cc \u062c\u0631\u0623\u062a \u06c1\u06d2 \u062a\u062c\u06be\u06d2 {mention} \ud83d\udcaf",
    "\u0686\u067e \u06c1\u0648 \u062c\u0627 \u0627\u0628 {mention} \ud83c\udf0a",
]

# ==================== ZALGO CHARACTERS ====================
ZALGO_CHARS = [
    '\u0300','\u0301','\u0302','\u0303','\u0304','\u0305','\u0306','\u0307',
    '\u0308','\u0309','\u030a','\u030b','\u030c','\u030d','\u030e','\u030f',
    '\u0310','\u0311','\u0312','\u0313','\u031a','\u031b','\u033d','\u033e',
    '\u033f','\u0340','\u0341','\u0342','\u0343','\u0344','\u0346','\u034a',
    '\u034b','\u034c','\u0350','\u0351','\u0352','\u0357','\u0358','\u035b',
    '\u0363','\u0364','\u0365','\u0366','\u0367','\u0368','\u0369','\u036a',
    '\u036b','\u036c','\u036d','\u036e','\u036f',
]

def zalgo_text(text, intensity=8):
    out = ""
    for ch in text:
        out += ch
        for _ in range(random.randint(2, intensity)):
            out += random.choice(ZALGO_CHARS)
    return out

# ==================== LOAD FUNCTIONS ====================
def load_tokens():
    try:
        with open(TOKENS_FILE, "r") as f:
            return [t.strip() for t in f.read().splitlines() if t.strip()]
    except:
        return []

def load_sudo():
    if os.path.exists(SUDO_FILE):
        try:
            with open(SUDO_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_sudo(users):
    with open(SUDO_FILE, "w") as f:
        json.dump(users, f)

SUDO_USERS = load_sudo()

def load_gcnames():
    try:
        with open(GCNAME_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return ["𝘼𝙨𝙝𝙪 𝐎𝐍 𝐓𝐎𝐏", "𝘼𝙨𝙝𝙪 𝐑𝐔𝐍𝐒 𝐔"]

def load_autoreplies():
    try:
        with open(AUTOREPLY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_autoreplies(data):
    with open(AUTOREPLY_FILE, "w") as f:
        json.dump(data, f, indent=4)

auto_responses = load_autoreplies()

# ==================== HELPERS ====================
def send_msg(c_id, text, reply_to=None, token=None):
    if not token:
        return None
    headers = {"Authorization": token, "Content-Type": "application/json"}
    payload = {"content": text}
    if reply_to:
        payload["message_reference"] = {"channel_id": str(c_id), "message_id": str(reply_to)}
    try:
        response = requests.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json=payload)
        if response.status_code == 429:
            retry_after = response.json().get("retry_after", 0.3)
            time.sleep(retry_after)
        return response
    except:
        return None

def send_long_menu(c_id, text, token):
    max_len = 1900
    lines = text.split("\n")
    chunks = []
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) + 1 > max_len:
            chunks.append(current_chunk)
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"
    
    if current_chunk:
        chunks.append(current_chunk)

    for chunk in chunks:
        formatted_msg = f"```fix\n{chunk.strip()}\n```"
        send_msg(c_id, formatted_msg, token=token)
        time.sleep(0.3)

def change_gc_name(g_id, name, token=None):
    if not token:
        return None
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        response = requests.patch(f"https://discord.com/api/v9/channels/{g_id}", headers=headers, json={"name": name})
        if response.status_code == 429:
            retry_after = response.json().get("retry_after", 0.2)
            time.sleep(retry_after)
        return response
    except:
        return None

def add_reaction(c_id, m_id, emoji, token=None):
    if not token:
        return
    encoded_emoji = requests.utils.quote(emoji)
    url = f"https://discord.com/api/v9/channels/{c_id}/messages/{m_id}/reactions/{encoded_emoji}/@me"
    try:
        requests.put(url, headers={"Authorization": token})
    except:
        pass

def verify_owner_id(token):
    try:
        r = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get('id')
    except:
        pass
    return None

def extract_user_id_from_mention(mention):
    if mention.startswith('<@') and mention.endswith('>'):
        mention = mention[2:-1]
        if mention.startswith('!'):
            mention = mention[1:]
    else:
        if mention.startswith('@'):
            mention = mention[1:]
    match = re.search(r'\d+', mention)
    if match:
        return match.group()
    return None

def run_async_tasks(tasks):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(asyncio.gather(*tasks))
    finally:
        loop.close()

# ==================== HIGH-SPEED ASYNC WORKERS ====================
async def async_nc_worker(g_id, target_mention, token):
    key = f"{g_id}_{token[:10]}"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        while ACTIVE_NC_CHANNELS.get(key, False):
            base_line = random.choice(NC_LIST)
            new_text = base_line.replace("{target}", target_mention)[:100]
            try:
                async with session.patch(f"https://discord.com/api/v9/channels/{g_id}", headers=headers, json={"name": new_text}) as resp:
                    if resp.status == 429:
                        data = await resp.json()
                        await asyncio.sleep(data.get("retry_after", 0.1))
            except:
                await asyncio.sleep(0.01)

def nc_thread_launcher(g_id, target_mention, token):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [async_nc_worker(g_id, target_mention, token) for _ in range(PARALLEL_NC)]
    loop.run_until_complete(asyncio.gather(*tasks))

async def async_spam_worker(c_id, target_mention, token):
    key = f"{c_id}_{token[:10]}"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        while ACTIVE_SPAM_CHANNELS.get(key, False):
            for msg_template in SPAM_MESSAGES:
                if not ACTIVE_SPAM_CHANNELS.get(key, False): break
                msg = msg_template.replace("##𝘼𝙨𝙝𝙪#𝙊𝙣 𝙏𝙤𝙥", target_mention).replace("𝘼𝙨𝙝𝙪#𝙊𝙣 𝙏𝙤𝙥", target_mention)
                try:
                    async with session.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": msg}) as resp:
                        if resp.status == 429:
                            data = await resp.json()
                            await asyncio.sleep(data.get("retry_after", 0.1))
                except:
                    await asyncio.sleep(0.01)

def spam_thread_launcher(c_id, target_mention, token):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [async_spam_worker(c_id, target_mention, token) for _ in range(PARALLEL_SPAM)]
    loop.run_until_complete(asyncio.gather(*tasks))

# ==================== DISCORD SELF-BOT CLIENT ====================
class DiscordSelfBot:
    def __init__(self, token, bot_index):
        self.token = token
        self.bot_index = bot_index
        self.ws = None
        self.running = True
        self.user_id = None

    def on_message(self, ws, message):
        global ACTIVE_NC_CHANNELS, ACTIVE_SPAM_CHANNELS, AUTOREPLY_TARGETS, AUTOREACT_EMOJIS, START_TIME, SUDO_USERS, multi_running, drown_running, pack_running, repeat_running, counter_running, auto_responses, spammingss, PREFIX
        try:
            data = json.loads(message)
        except:
            return

        if data.get("op") == 10:
            heartbeat_interval = data["d"]["heartbeat_interval"] / 1000
            def heartbeat():
                while self.running:
                    time.sleep(heartbeat_interval)
                    try:
                        ws.send(json.dumps({"op": 1, "d": None}))
                    except:
                        break
            threading.Thread(target=heartbeat, daemon=True).start()
            ws.send(json.dumps({
                "op": 2,
                "d": {
                    "token": self.token,
                    "properties": {"$os": "windows", "$browser": "chrome", "$device": "pc"}
                }
            }))
            r = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": self.token})
            if r.status_code == 200:
                self.user_id = r.json().get('id')
            print(f"✅ Bot {self.bot_index + 1} Connected")

        if data.get("t") == "MESSAGE_CREATE":
            msg = data["d"]
            auth_id = msg.get("author", {}).get("id")
            if not auth_id: return
            content = msg.get("content", "").strip()
            c_id = msg.get("channel_id")
            m_id = msg.get("id")
            guild_id = msg.get("guild_id")
            key_suffix = f"{c_id}_{self.token[:10]}"

            # --- AUTOREPLY (JSON based) ---
            if content in auto_responses:
                send_msg(c_id, auto_responses[content], token=self.token)

            # --- AUTOREPLY TARGET ---
            if c_id in AUTOREPLY_TARGETS:
                if auth_id in AUTOREPLY_TARGETS[c_id]:
                    if self.user_id and auth_id != self.user_id:
                        reply_text = random.choice(REPLY_TEXTS)
                        send_msg(c_id, reply_text, reply_to=m_id, token=self.token)

            # --- AUTOREACT ---
            if c_id in AUTOREACT_EMOJIS:
                emoji = AUTOREACT_EMOJIS[c_id]
                if self.user_id and auth_id != self.user_id:
                    threading.Thread(target=add_reaction, args=(c_id, m_id, emoji, self.token), daemon=True).start()

            # --- COMMANDS ---
            if auth_id != OWNER_ID and auth_id not in SUDO_USERS:
                return
            if not content.startswith(PREFIX):
                return

            cmd_part = content[len(PREFIX):].strip()
            cmd_lower = cmd_part.lower()
            args = cmd_part.split()

            # ========== ULTIMATE DETAILED & STYLISH HELP MENU ==========
            if cmd_lower == "help" or cmd_lower == "h":
                full_help = """
⚡ ══════════════════════════════════════════════════ ⚡
               𝘼𝙨𝙝𝙪  𝙎𝙚𝙡𝙛𝙗𝙤𝙩  𝙑𝟮  —  𝙐𝙡𝙩𝙞𝙢𝙖𝙩𝙚  𝙈𝙚𝙣𝙪
       👑 Owner: Ashu | System Status: Active 👑
⚡ ══════════════════════════════════════════════════ ⚡

[ 1. SPAM MODES — SINGLE TOKEN ]
───────────────────────────────────────────────────────
• $spam @user
  └─ Kaam: Specific user ko mention karke fast parallel spam karta hai.
  └─ Chalu: $spam @user
  └─ Roke: $stopspam

• $spammm <text>
  └─ Kaam: Multi-line (Exact 40 lines per message) fast repeat text spam.
  └─ Chalu: $spammm Text Here
  └─ Roke: $spamoff

• $nc @user
  └─ Kaam: Group Chat / Channel ka naam fast rename karke user ko spam karta hai.
  └─ Chalu: $nc @user
  └─ Roke: $stopnc

• $spamall <msg>
  └─ Kaam: Server ke saare text channels mein ek sath spam karta hai.
  └─ Chalu: $spamall Ashu On Top
  └─ Roke: $stopspamall

• $longspam @user
  └─ Kaam: 2000 character lambe heavy text paragraphs bhej kar channel flood karta hai.
  └─ Chalu: $longspam @user
  └─ Roke: $stoplongspam

• $wordwall <word>
  └─ Kaam: Ek hi lafz/word ka 2000-char lamba wall bana kar spam karta hai.
  └─ Chalu: $wordwall ASHU
  └─ Roke: $stopwordwall

• $zalgo <text>
  └─ Kaam: Corrupted Zalgo/Glitchy fonts ka use karke spam karta hai.
  └─ Chalu: $zalgo Hello World
  └─ Roke: $stopzalgo

• $repeat_spam <text>
  └─ Kaam: Infinite loop mein same message repeat bhejta rehta hai.
  └─ Chalu: $repeat_spam Hello
  └─ Roke: $stoprepeat

• $counter_spam <prefix>
  └─ Kaam: Message ke aage 1, 2, 3 numbers count karke spam karta hai.
  └─ Chalu: $counter_spam Count
  └─ Roke: $stopcounter

• $edit_spam <msg>
  └─ Kaam: Pehle msg bhejta hai fir use baar-baar edit karke spam bypass karta hai.
  └─ Chalu: $edit_spam Bypass
  └─ Roke: $stopeditspam

• $invis
  └─ Kaam: Complete invisible/blank characters ka spam karta hai.
  └─ Chalu: $invis
  └─ Roke: $stopinvis

• $nitro_spam
  └─ Kaam: Fake Nitro gift links generate karke continuous flood karta hai.
  └─ Chalu: $nitro_spam
  └─ Roke: $stopnitro


[ 2. MULTI-TOKEN COMMANDS — ALL BOTS ]
───────────────────────────────────────────────────────
• $multispam <msg>
  └─ Kaam: Saare added tokens ek saath current channel mein spam karenge.
  └─ Chalu: $multispam Ashu Gang
  └─ Roke: $stopmulti

• $multispamall <msg>
  └─ Kaam: Saare tokens server ke saare channels mein spam karte hain.
  └─ Chalu: $multispamall Ashu Multi
  └─ Roke: $stopmulti

• $multinuke <msg>
  └─ Kaam: Saare tokens @everyone tag ke sath saare channels mein nuke spam karenge.
  └─ Chalu: $multinuke Server Down
  └─ Roke: $stopmulti

• $multidm <user_id> <msg>
  └─ Kaam: Saare tokens target user ke Personal DM mein message bhejenge.
  └─ Chalu: $multidm 123456789 Hi
  └─ Roke: Automatic (Task Complete hone par)

• $multi_massdm <msg>
  └─ Kaam: Server ke har ek member ko saare tokens se DM spam karta hai.
  └─ Chalu: $multi_massdm Check this
  └─ Roke: Automatic

• $multijoin <invite_code>
  └─ Kaam: Saare tokens ek saath server join karenge.
  └─ Chalu: $multijoin discord.gg/xyz
  └─ Roke: Automatic

• $multileave <guild_id>
  └─ Kaam: Saare tokens specified server se leave kar denge.
  └─ Chalu: $multileave 987654321
  └─ Roke: Automatic

• $multi_leaveall
  └─ Kaam: Saare tokens unke saare joined servers se leave ho jayenge.
  └─ Chalu: $multi_leaveall
  └─ Roke: Automatic

• $multifriend / $multiblock <user_id>
  └─ Kaam: Target ID ko saare tokens se Mass Friend Request / Block bhejta hai.
  └─ Chalu: $multifriend ID / $multiblock ID
  └─ Roke: Automatic

• $multi_setnick <name>
  └─ Kaam: Server mein saare tokens ka Nickname change kar deta hai.
  └─ Chalu: $multi_setnick Ashu
  └─ Roke: Automatic

• $multireact <msg_id> <emoji>
  └─ Kaam: Ek specific message par saare tokens se emoji reaction dilwata hai.
  └─ Chalu: $multireact 11223344 🔥
  └─ Roke: Automatic


[ 3. DROWN & PACK MODES — FLOODING ]
───────────────────────────────────────────────────────
• $drown_hindi / $drown_hinglish / $drown_english / $drown_mix @user
  └─ Kaam: Selected bhasha (Language) mein targeted non-stop abuse flood karta hai.
  └─ Chalu: $drown_hinglish @user
  └─ Roke: $stopdrown

• $continuous_pack @user <lang>
  └─ Kaam: Continuous loop mein heavy pack/abuse dialogue lines bhejta hai.
  └─ Chalu: $continuous_pack @user hindi
  └─ Roke: $stoppack

• $hindi_pack / $hinglish_pack / $punjabi_pack / $urdu_pack / $god_pack @user
  └─ Kaam: Pre-defined 10-20 heavy regional pack lines single shot mein send karta hai.
  └─ Chalu: $god_pack @user
  └─ Roke: Automatic (Lines complete hone par)


[ 4. AUTO-REPLY & SYSTEM SETTINGS ]
───────────────────────────────────────────────────────
• $autoreply @user
  └─ Kaam: Targeted user jab bhi message karega, bot use automatic roast/reply dega.
  └─ Chalu: $autoreply @user
  └─ Roke: $removeautoreply @user  YA  $stopautoreply

• $addar <trigger>,<response>
  └─ Kaam: Custom word trigger par auto-response set karta hai (e.g. hi -> hello).
  └─ Chalu: $addar hi,hello
  └─ Roke: $removear hi

• $autoreact <emoji>
  └─ Kaam: Channel ke saare aane wale new messages par automatic emoji react karega.
  └─ Chalu: $autoreact 🔥
  └─ Roke: $stopautoreact

• $gcstart <delay>
  └─ Kaam: Group Chat ka name gcname.txt se padh kar continuous fast rename karega.
  └─ Chalu: $gcstart 0.5
  └─ Roke: $gcstop

• $prefix <new_prefix>
  └─ Kaam: Self-bot ka command prefix change karta hai.
  └─ Chalu: $prefix !
  └─ Roke: Automatic

• $access @user / $removeaccess @user
  └─ Kaam: Dusre user ko bot commands chalane ki Sudo permission deta/hata-ta hai.
  └─ Chalu: $access @user
  └─ Roke: $removeaccess @user

• $ping / $status / $restart
  └─ Kaam: Bot ki latency (speed), active status, ya bot ko restart karne ke liye.
  └─ Chalu: $ping / $status / $restart

⚡ ══════════════════════════════════════════════════ ⚡
             🔥  𝘼𝙨𝙝𝙪  𝙊𝙣  𝙏𝙤𝙥  —  𝙁𝙪𝙡𝙡  𝘾𝙤𝙣𝙩𝙧𝙤𝙡  🔥
⚡ ══════════════════════════════════════════════════ ⚡
"""
                send_long_menu(c_id, full_help, token=self.token)
                return

            # ========== OTHER HELP MENUS ==========
            if cmd_lower == "general" or cmd_lower == "gnrl":
                send_msg(c_id, """**```fix
╔══════════════════════════════════════════╗
   ⚙️  𝘼𝙨𝙝𝙪  |  GENERAL COMMANDS
╚══════════════════════════════════════════╝
  • help / h           — Full help index
  • general / gnrl     — This menu
  • spamhelp / sh      — Spam commands menu
  • multihelp / mh     — Multi-token menu
  • drownhelp / dh     — Drown/pack menu
  • trollhelp / th     — Troll/fake menu
  • autoreplyhelp / arh — Auto-reply menu
  • gchelp / gch       — Group chat menu

  • ping               — Check latency
  • status             — Bot status
  • restart            — Restart bot
  • prefix <p>         — Change prefix
  • access @user       — Give sudo access
  • removeaccess @user — Remove sudo access

  ─────────────────────────────────────
        ☠️  𝘼𝙨𝙝𝙪 On Top  ☠️
```**""", token=self.token)
                return

            if cmd_lower == "spamhelp" or cmd_lower == "sh":
                send_msg(c_id, """**```fix
╔══════════════════════════════════════════╗
   💥  𝘼𝙨𝙝𝙪  |  SPAM COMMANDS
╚══════════════════════════════════════════╝
  SINGLE TOKEN SPAM
  • spam @user          — Start spam in channel (+stopspam)
  • nc @user            — Nickname change spam (+stopnc)
  • spamall <msg>       — Spam in all channels (+stopspamall)
  • invis <count>       — Invisible char spam (+stopinvis)
  • nitro_spam <count>  — Fake nitro links spam (+stopnitro)
  • zalgo <count> <t>   — Zalgo text (+stopzalgo)
  • repeat_spam <msg>   — Infinite repeat spam (+stoprepeat)
  • counter_spam <pre>  — Auto-counter spam (+stopcounter)
  • longspam @u <cnt>   — 2000-char spam (+stoplongspam)
  • wordwall <word>     — 2000-char word wall (+stopwordwall)
  • edit_spam <msg>     — Edit-spam bypass (+stopeditspam)
  • spammm <msg>        — Fast 0.05s spam (+spamoff)

  ─────────────────────────────────────
        ☠️  𝘼𝙨𝙝𝙪 On Top  ☠️
```**""", token=self.token)
                return

            if cmd_lower == "multihelp" or cmd_lower == "mh":
                send_msg(c_id, """**```fix
╔══════════════════════════════════════════╗
   🌐  𝘼𝙨𝙝𝙪  |  MULTI-TOKEN COMMANDS
╚══════════════════════════════════════════╝
  SPAM
  • multispam <msg>      — All tokens spam channel
  • multispamall <msg>   — All tokens spam all channels
  • multilongspam <id>   — All tokens long spam
  • multiwordwall <word> — All tokens word wall
  • multizalgo <cnt> <t> — All tokens zalgo spam
  • multieveryone <cnt>  — All tokens @everyone

  DM / FRIENDS
  • multidm <id> <msg>   — All tokens DM user
  • multi_massdm <msg>   — All tokens DM all members
  • multifriend <id>     — All tokens friend request
  • multiblock <id>      — All tokens block user
  • multi_accept_friends — All tokens accept friend reqs
  • multi_del_friends    — All tokens remove friends

  SERVER
  • multijoin <invite>   — All tokens join server
  • multileave <gid>     — All tokens leave server
  • multi_leaveall       — All tokens leave ALL servers
  • multi_setnick <name> — All tokens set nickname
  • multi_set_avatar <f> — All tokens set avatar
  • multi_set_username <n> — All tokens set username
  • multi_status_set <t> — All tokens set status
  • multi_delete_msgs <n> — All tokens delete own msgs

  OTHER
  • multireact <id> <e>  — All tokens react
  • multi_reactall <e>   — All tokens react last 10 msgs
  • multi_ghost_ping @u  — All tokens ghost ping
  • multi_pack @u <l>    — All tokens abuse pack
  • multi_drown <id> <l> — All tokens drown
  • multi_typing <secs>  — All tokens typing indicator
  • multinuke <msg>      — All tokens nuke server

  • stopmulti            — Stop all multi commands

  ─────────────────────────────────────
        ☠️  𝘼𝙨𝙝𝙪 On Top  ☠️
```**""", token=self.token)
                return

            if cmd_lower == "drownhelp" or cmd_lower == "dh":
                send_msg(c_id, """**```fix
╔══════════════════════════════════════════╗
   💀  𝘼𝙨𝙝𝙪  |  DROWN / PACK COMMANDS
╚══════════════════════════════════════════╝
  SINGLE TOKEN
  • drown_hindi @u       — Hindi abuse flood
  • drown_hinglish @u    — Hinglish abuse flood
  • drown_english @u     — English abuse flood
  • drown_mix @u         — Mixed language flood
  • hindi_pack @u        — Hindi pack
  • hinglish_pack @u     — Hinglish pack
  • punjabi_pack @u      — Punjabi pack
  • urdu_pack @u         — Urdu pack
  • mix_all_pack @u      — All languages mix
  • god_pack @u          — All languages combined
  • continuous_pack @u   — Endless pack (+stoppack)
  • stoppack             — Stop continuous pack
  • stopdrown            — Stop any drown

  MULTI TOKEN
  • multi_pack @u <lang>  — All tokens pack
  • multi_drown <id>      — All tokens drown

  ─────────────────────────────────────
        ☠️  𝘼𝙨𝙝𝙪 On Top  ☠️
```**""", token=self.token)
                return

            if cmd_lower == "trollhelp" or cmd_lower == "th":
                send_msg(c_id, """**```fix
╔══════════════════════════════════════════╗
   🎭  𝘼𝙨𝙝𝙪  |  TROLL / FAKE COMMANDS
╚══════════════════════════════════════════╝
  FAKE ACTIONS
  • fake_ban @u          — Fake ban announcement
  • fake_mute @u         — Fake mute announcement
  • fake_kick @u         — Fake kick announcement
  • fake_warn @u         — Fake warning DM

  TROLL CONTENT
  • rick_roll @u         — Disguised rick roll
  • crash_dm @u          — Invisible char DM bomb
  • ip_logger @u         — Fake IP logger
  • countdown [n] [msg]  — Countdown then message
  • typing_spam [secs]   — Keep typing indicator

  ─────────────────────────────────────
        ☠️  𝘼𝙨𝙝𝙪 On Top  ☠️
```**""", token=self.token)
                return

            if cmd_lower == "autoreplyhelp" or cmd_lower == "arh":
                send_msg(c_id, """**```fix
╔══════════════════════════════════════════╗
   🔄  𝘼𝙨𝙝𝙪  |  AUTO-REPLY COMMANDS
╚══════════════════════════════════════════╝
  TARGET BASED
  • autoreply @user      — Auto-reply to user
  • removeautoreply @user — Remove auto-reply
  • stopautoreply        — Clear all auto-replies

  TRIGGER BASED (JSON file)
  • addar trigger,resp   — Add auto-response
  • removear <trigger>   — Remove auto-response
  • lister               — List all auto-responses

  REACTIONS
  • autoreact <emoji>    — Auto-react with emoji
  • stopautoreact        — Stop auto-react

  ─────────────────────────────────────
        ☠️  𝘼𝙨𝙝𝙪 On Top  ☠️
```**""", token=self.token)
                return

            if cmd_lower == "gchelp" or cmd_lower == "gch":
                send_msg(c_id, """**```fix
╔══════════════════════════════════════════╗
   💬  𝘼𝙨𝙝𝙪  |  GROUP CHAT COMMANDS
╚══════════════════════════════════════════╝
  • gcstart [interval]   — Auto-rename GC (gcname.txt)
  • gcstop               — Stop auto-rename
  • gc_mass_add          — Add all friends to GC
  • gc_invite_spam [n]   — Spam in GC
  • set_gc_icon [file]   — Change GC icon

  ─────────────────────────────────────
        ☠️  𝘼𝙨𝙝𝙪 On Top  ☠️
```**""", token=self.token)
                return

            # ========== SPAM COMMANDS (HIGH-SPEED ASYNC BATCH) ==========
            if cmd_lower.startswith("spam "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "❌ Usage: $spam @user", token=self.token)
                    return
                mention = parts[1]
                ACTIVE_SPAM_CHANNELS[key_suffix] = True
                threading.Thread(target=spam_thread_launcher, args=(c_id, mention, self.token), daemon=True).start()
                send_msg(c_id, f"✅ Ultra Fast Spam started (x{PARALLEL_SPAM} async batch)", token=self.token)
                return

            if cmd_lower == "stopspam":
                ACTIVE_SPAM_CHANNELS[key_suffix] = False
                send_msg(c_id, "✅ Spam stopped", token=self.token)
                return

            # ========== $SPAMMM — MULTI-LINE REPEAT SPAM (EXACT 40 TIMES) ==========
            if cmd_lower.startswith("spammm "):
                spammingss = True
                if len(cmd_part.split()) > 1:
                    base_text = " ".join(cmd_part.split()[1:])
                else:
                    base_text = "Garv tmkb me lun daalke fyter bnadunga usko 🤣🔥"
                
                lines_count = 40
                msg_text = (base_text + "\n") * lines_count
                
                if len(msg_text) > 2000:
                    msg_text = msg_text[:1997] + "..."
                
                send_msg(c_id, f"✅ Ultra Fast Spammm started (40 lines/msg). Use $spamoff to stop.", token=self.token)
                
                async def _async_spam_fast():
                    headers = {"Authorization": self.token, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as session:
                        while spammingss:
                            try:
                                async with session.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": msg_text}) as resp:
                                    if resp.status == 429:
                                        d = await resp.json()
                                        await asyncio.sleep(d.get("retry_after", 0.1))
                            except:
                                await asyncio.sleep(0.01)
                
                def _start_fast_loop():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(_async_spam_fast())

                threading.Thread(target=_start_fast_loop, daemon=True).start()
                return

            if cmd_lower == "spamoff":
                spammingss = False
                send_msg(c_id, "✅ Spammm stopped.", token=self.token)
                return

            # ========== NC (HIGH-SPEED ASYNC BATCH) ==========
            if cmd_lower.startswith("nc "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "❌ Usage: $nc @user", token=self.token)
                    return
                mention = parts[1]
                ACTIVE_NC_CHANNELS[key_suffix] = True
                threading.Thread(target=nc_thread_launcher, args=(c_id, mention, self.token), daemon=True).start()
                send_msg(c_id, f"✅ Ultra Fast NC started (x{PARALLEL_NC} async batch)", token=self.token)
                return

            if cmd_lower == "stopnc":
                ACTIVE_NC_CHANNELS[key_suffix] = False
                send_msg(c_id, "✅ NC stopped", token=self.token)
                return

            # ========== UNLIMITED SPAMALL ==========
            if cmd_lower.startswith("spamall "):
                multi_running[f"spamall_{key_suffix}"] = True
                msg_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "𝘼𝙨𝙝𝙪 On Top 🔥"
                if not guild_id:
                    send_msg(c_id, "❌ Run this in a server!", token=self.token)
                    return
                r = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers={"Authorization": self.token})
                if r.status_code == 200:
                    channels = [ch['id'] for ch in r.json() if ch['type'] == 0]
                    send_msg(c_id, f"✅ Endless Spamall across {len(channels)} channels. Use $stopspamall to end.", token=self.token)
                    
                    async def _async_spamall():
                        headers = {"Authorization": self.token, "Content-Type": "application/json"}
                        async with aiohttp.ClientSession() as session:
                            while multi_running.get(f"spamall_{key_suffix}", False):
                                for ch in channels:
                                    if not multi_running.get(f"spamall_{key_suffix}", False): break
                                    try:
                                        async with session.post(f"https://discord.com/api/v9/channels/{ch}/messages", headers=headers, json={"content": msg_text}) as resp:
                                            if resp.status == 429:
                                                d = await resp.json()
                                                await asyncio.sleep(d.get("retry_after", 0.1))
                                    except: pass

                    def _start_spamall_loop():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(_async_spamall())

                    threading.Thread(target=_start_spamall_loop, daemon=True).start()
                return

            if cmd_lower == "stopspamall":
                multi_running[f"spamall_{key_suffix}"] = False
                send_msg(c_id, "✅ Spamall stopped", token=self.token)
                return

            # ========== UNLIMITED LONG SPAM ==========
            if cmd_lower.startswith("longspam "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                mention = parts[1]
                multi_running[f"longspam_{key_suffix}"] = True
                send_msg(c_id, f"✅ Endless Longspam started. Use $stoplongspam to end.", token=self.token)
                def _longspam_loop():
                    while multi_running.get(f"longspam_{key_suffix}", False):
                        msg = get_long_spam(mention)
                        send_msg(c_id, msg, token=self.token)
                        time.sleep(0.3)
                threading.Thread(target=_longspam_loop, daemon=True).start()
                return

            if cmd_lower == "stoplongspam":
                multi_running[f"longspam_{key_suffix}"] = False
                send_msg(c_id, "✅ Longspam stopped.", token=self.token)
                return

            # ========== UNLIMITED WORDWALL ==========
            if cmd_lower.startswith("wordwall "):
                parts = cmd_part.split()
                word = " ".join(parts[1:]) if len(parts) > 1 else "𝘼𝙨𝙝𝙪"
                wall = (word + " ") * (2000 // (len(word) + 1))
                multi_running[f"wordwall_{key_suffix}"] = True
                send_msg(c_id, f"✅ Endless Wordwall started. Use $stopwordwall to end.", token=self.token)
                def _ww_loop():
                    while multi_running.get(f"wordwall_{key_suffix}", False):
                        send_msg(c_id, wall[:2000], token=self.token)
                        time.sleep(0.3)
                threading.Thread(target=_ww_loop, daemon=True).start()
                return

            if cmd_lower == "stopwordwall":
                multi_running[f"wordwall_{key_suffix}"] = False
                send_msg(c_id, "✅ Wordwall stopped.", token=self.token)
                return

            # ========== UNLIMITED ZALGO SPAM ==========
            if cmd_lower.startswith("zalgo "):
                parts = cmd_part.split()
                text = " ".join(parts[1:]) if len(parts) > 1 else "𝘼𝙨𝙝𝙪 On Top"
                multi_running[f"zalgo_{key_suffix}"] = True
                send_msg(c_id, f"✅ Endless Zalgo started. Use $stopzalgo to end.", token=self.token)
                def _zalgo_loop():
                    while multi_running.get(f"zalgo_{key_suffix}", False):
                        send_msg(c_id, zalgo_text(text), token=self.token)
                        time.sleep(0.3)
                threading.Thread(target=_zalgo_loop, daemon=True).start()
                return

            if cmd_lower == "stopzalgo":
                multi_running[f"zalgo_{key_suffix}"] = False
                send_msg(c_id, "✅ Zalgo spam stopped.", token=self.token)
                return

            # ========== REPEAT SPAM ==========
            if cmd_lower.startswith("repeat_spam "):
                msg_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "𝘼𝙨𝙝𝙪 On Top 🔥"
                multi_running[f"repeat_{key_suffix}"] = True
                send_msg(c_id, f"✅ Repeat spam started. Use $stoprepeat to stop.", token=self.token)
                def _repeat():
                    while multi_running.get(f"repeat_{key_suffix}", False):
                        send_msg(c_id, msg_text, token=self.token)
                        time.sleep(0.1)
                threading.Thread(target=_repeat, daemon=True).start()
                return

            if cmd_lower == "stoprepeat":
                multi_running[f"repeat_{key_suffix}"] = False
                send_msg(c_id, "✅ Repeat spam stopped.", token=self.token)
                return

            # ========== COUNTER SPAM ==========
            if cmd_lower.startswith("counter_spam "):
                prefix_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "𝘼𝙨𝙝𝙪"
                multi_running[f"counter_{key_suffix}"] = True
                send_msg(c_id, f"✅ Counter spam started. Use $stopcounter to stop.", token=self.token)
                def _counter():
                    i = 1
                    while multi_running.get(f"counter_{key_suffix}", False):
                        send_msg(c_id, f"{prefix_text} `#{i}`", token=self.token)
                        i += 1
                        time.sleep(0.1)
                threading.Thread(target=_counter, daemon=True).start()
                return

            if cmd_lower == "stopcounter":
                multi_running[f"counter_{key_suffix}"] = False
                send_msg(c_id, "✅ Counter spam stopped.", token=self.token)
                return

            # ========== EDIT SPAM ==========
            if cmd_lower.startswith("edit_spam "):
                msg_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "𝘼𝙨𝙝𝙪 On Top 🔥"
                phrases = [
                    msg_text,
                    "𝐄𝐭𝐞𝐫𝐧𝐚𝐥 𝐑uu𝐧𝐬 𝐔 🔥",
                    "𝐍𝐨𝐛𝐨𝐝𝐲 𝐂𝐚𝐧 𝐒𝐭𝐨𝐩 𝐔𝐬",
                    "𝘼𝙨𝙝𝙪 𝐆𝐚𝐧𝐠 💀",
                ]
                multi_running[f"edit_{key_suffix}"] = True
                send_msg(c_id, f"✅ Edit spam started. Use $stopeditspam to stop.", token=self.token)
                def _edit_loop():
                    while multi_running.get(f"edit_{key_suffix}", False):
                        msg = send_msg(c_id, phrases[0], token=self.token)
                        if msg:
                            i = 1
                            for _ in range(10):
                                if not multi_running.get(f"edit_{key_suffix}", False): break
                                try:
                                    msg_id = msg.json().get("id")
                                    requests.patch(f"https://discord.com/api/v9/channels/{c_id}/messages/{msg_id}", headers={"Authorization": self.token, "Content-Type": "application/json"}, json={"content": phrases[i % len(phrases)]})
                                    i += 1
                                    time.sleep(0.2)
                                except: pass
                threading.Thread(target=_edit_loop, daemon=True).start()
                return

            if cmd_lower == "stopeditspam":
                multi_running[f"edit_{key_suffix}"] = False
                send_msg(c_id, "✅ Edit spam stopped.", token=self.token)
                return

            # ========== INVISIBLE SPAM ==========
            if cmd_lower == "invis":
                invis = "\u200b" * 500
                multi_running[f"invis_{key_suffix}"] = True
                send_msg(c_id, f"✅ Endless Invis started. Use $stopinvis to end.", token=self.token)
                def _invis_loop():
                    while multi_running.get(f"invis_{key_suffix}", False):
                        send_msg(c_id, invis, token=self.token)
                        time.sleep(0.2)
                threading.Thread(target=_invis_loop, daemon=True).start()
                return

            if cmd_lower == "stopinvis":
                multi_running[f"invis_{key_suffix}"] = False
                send_msg(c_id, "✅ Invis spam stopped.", token=self.token)
                return

            # ========== NITRO SPAM ==========
            if cmd_lower == "nitro_spam":
                chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                multi_running[f"nitro_{key_suffix}"] = True
                send_msg(c_id, f"✅ Endless Fake Nitro started. Use $stopnitro to end.", token=self.token)
                def _nitro_loop():
                    while multi_running.get(f"nitro_{key_suffix}", False):
                        code = ''.join(random.choices(chars, k=16))
                        send_msg(c_id, f"🎉 **FREE NITRO** https://discord.gift/{code}", token=self.token)
                        time.sleep(0.3)
                threading.Thread(target=_nitro_loop, daemon=True).start()
                return
                
            if cmd_lower == "stopnitro":
                multi_running[f"nitro_{key_suffix}"] = False
                send_msg(c_id, "✅ Nitro spam stopped.", token=self.token)
                return

            # ========== DROWN COMMANDS ==========
            def start_drown(pool, user_id):
                multi_running[f"drown_{key_suffix}"] = True
                send_msg(c_id, f"✅ Endless Drown started. Use $stopdrown to stop.", token=self.token)
                def _drown_loop():
                    while multi_running.get(f"drown_{key_suffix}", False):
                        line = random.choice(pool).replace("{mention}", f"<@{user_id}>")
                        send_msg(c_id, line, token=self.token)
                        time.sleep(0.2)
                threading.Thread(target=_drown_loop, daemon=True).start()

            if cmd_lower.startswith("drown_hindi "):
                user_id = extract_user_id_from_mention(cmd_part.split()[1])
                if user_id: start_drown(hindi_drown, user_id)
                return

            if cmd_lower.startswith("drown_hinglish "):
                user_id = extract_user_id_from_mention(cmd_part.split()[1])
                if user_id: start_drown(hinglish_drown, user_id)
                return

            if cmd_lower.startswith("drown_english "):
                user_id = extract_user_id_from_mention(cmd_part.split()[1])
                if user_id: start_drown(english_drown, user_id)
                return

            if cmd_lower.startswith("drown_mix "):
                user_id = extract_user_id_from_mention(cmd_part.split()[1])
                if user_id: start_drown(hindi_drown + hinglish_drown + english_drown, user_id)
                return

            if cmd_lower == "stopdrown":
                multi_running[f"drown_{key_suffix}"] = False
                send_msg(c_id, "✅ Drown stopped.", token=self.token)
                return

            # ========== PACK COMMANDS ==========
            if cmd_lower.startswith("hindi_pack "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1])
                for line in hindi_drown[:10]:
                    send_msg(c_id, line.replace("{mention}", f"<@{user_id}>"), token=self.token)
                    time.sleep(0.2)
                return

            if cmd_lower.startswith("hinglish_pack "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1])
                for line in hinglish_drown[:10]:
                    send_msg(c_id, line.replace("{mention}", f"<@{user_id}>"), token=self.token)
                    time.sleep(0.2)
                return

            if cmd_lower.startswith("punjabi_pack "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1])
                for line in punjabi_lines[:10]:
                    send_msg(c_id, line.replace("{mention}", f"<@{user_id}>"), token=self.token)
                    time.sleep(0.2)
                return

            if cmd_lower.startswith("urdu_pack "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1])
                for line in urdu_lines[:10]:
                    send_msg(c_id, line.replace("{mention}", f"<@{user_id}>"), token=self.token)
                    time.sleep(0.2)
                return

            if cmd_lower.startswith("mix_all_pack "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1])
                all_lines = hindi_drown + hinglish_drown + english_drown + punjabi_lines + urdu_lines
                random.shuffle(all_lines)
                for line in all_lines[:15]:
                    send_msg(c_id, line.replace("{mention}", f"<@{user_id}>"), token=self.token)
                    time.sleep(0.2)
                return

            if cmd_lower.startswith("god_pack "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1])
                all_lines = hindi_drown + hinglish_drown + english_drown + punjabi_lines + urdu_lines
                random.shuffle(all_lines)
                for line in all_lines[:20]:
                    send_msg(c_id, line.replace("{mention}", f"<@{user_id}>"), token=self.token)
                    time.sleep(0.2)
                return

            if cmd_lower.startswith("continuous_pack "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                user_id = extract_user_id_from_mention(parts[1])
                lang = parts[2] if len(parts) > 2 else "mix"
                banks = {"hindi": hindi_drown, "hinglish": hinglish_drown, "english": english_drown, "punjabi": punjabi_lines, "urdu": urdu_lines}
                pool = banks.get(lang, hindi_drown + hinglish_drown + english_drown + punjabi_lines + urdu_lines)
                multi_running[f"pack_{key_suffix}"] = True
                send_msg(c_id, f"✅ Continuous pack started. Use $stoppack to stop.", token=self.token)
                def _pack():
                    while multi_running.get(f"pack_{key_suffix}", False):
                        line = random.choice(pool).replace("{mention}", f"<@{user_id}>")
                        send_msg(c_id, line, token=self.token)
                        time.sleep(0.2)
                threading.Thread(target=_pack, daemon=True).start()
                return

            if cmd_lower == "stoppack":
                multi_running[f"pack_{key_suffix}"] = False
                send_msg(c_id, "✅ Continuous pack stopped.", token=self.token)
                return

            # ========== TROLL / FAKE COMMANDS ==========
            if cmd_lower.startswith("fake_ban "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "❌ Usage: $fake_ban @user", token=self.token)
                    return
                user_id = extract_user_id_from_mention(parts[1])
                send_msg(c_id, f"🔨 <@{user_id}> has been banned from the server.\n> Reason: `Disrespecting 𝘼𝙨𝙝𝙪`", token=self.token)
                return

            if cmd_lower.startswith("fake_mute "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "❌ Usage: $fake_mute @user", token=self.token)
                    return
                user_id = extract_user_id_from_mention(parts[1])
                send_msg(c_id, f"🔇 <@{user_id}> has been muted for 7 days.\n> Reason: `Disrespecting 𝘼𝙨𝙝𝙪`", token=self.token)
                return

            if cmd_lower.startswith("fake_kick "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "❌ Usage: $fake_kick @user", token=self.token)
                    return
                user_id = extract_user_id_from_mention(parts[1])
                send_msg(c_id, f"👢 <@{user_id}> has been kicked from the server.\n> Reason: `Ran by 𝘼𝙨𝙝𝙪 🔥`", token=self.token)
                return

            if cmd_lower.startswith("fake_warn "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "❌ Usage: $fake_warn @user [reason]", token=self.token)
                    return
                user_id = extract_user_id_from_mention(parts[1])
                reason = " ".join(parts[2:]) if len(parts) > 2 else "Disrespecting 𝘼𝙨𝙝𝙪"
                send_msg(c_id, f"⚠️ <@{user_id}> has received a warning.\n> Reason: `{reason}`\n> Warned by: **𝘼𝙨𝙝𝙪 SELFBOT**", token=self.token)
                return

            if cmd_lower.startswith("rick_roll "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1]) if len(parts) > 1 else None
                mention = f"<@{user_id}>" if user_id else "@everyone"
                send_msg(c_id, f"{mention} 🎉 **FREE NITRO CLAIM — FIRST 100 ONLY!**\nhttps://discord.gift/rickroll-ashu\n||https://www.youtube.com/watch?v=dQw4w9WgXcQ||", token=self.token)
                return

            if cmd_lower.startswith("crash_dm "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "❌ Usage: $crash_dm @user", token=self.token)
                    return
                user_id = extract_user_id_from_mention(parts[1])
                bomb = ("\u200b" * 1990) + "𝘼𝙨𝙝𝙪 🔥"
                send_msg(c_id, f"💣 DM crash sent to <@{user_id}>", token=self.token)
                dm_url = f"https://discord.com/api/v9/users/@me/channels"
                dm_payload = {"recipient_id": user_id}
                dm_resp = requests.post(dm_url, headers={"Authorization": self.token, "Content-Type": "application/json"}, json=dm_payload)
                if dm_resp.status_code in [200, 201]:
                    dm_channel = dm_resp.json().get("id")
                    for _ in range(5):
                        send_msg(dm_channel, bomb, token=self.token)
                        time.sleep(0.2)
                return

            if cmd_lower.startswith("ip_logger "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1]) if len(parts) > 1 else None
                mention = f"<@{user_id}>" if user_id else "@everyone"
                fake_ip = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
                city = random.choice(['London','Mumbai','Karachi','Toronto','Sydney','Delhi','Lahore'])
                send_msg(c_id, f"{mention} yo click this https://grabify.link/ASHU\n||Logged IP: `{fake_ip}` — City: **{city}** lmaooo||", token=self.token)
                return

            if cmd_lower.startswith("countdown "):
                parts = cmd_part.split()
                count = int(parts[1]) if len(parts) > 1 else 10
                msg_text = " ".join(parts[2:]) if len(parts) > 2 else "𝘼𝙨𝙝𝙪 ON TOP 🔥"
                msg = send_msg(c_id, f"**{count}**", token=self.token)
                if msg:
                    for i in range(count - 1, 0, -1):
                        time.sleep(1)
                        send_msg(c_id, f"**{i}**", token=self.token)
                    time.sleep(1)
                    send_msg(c_id, f"💥 **{msg_text}**", token=self.token)
                return

            if cmd_lower.startswith("typing_spam "):
                parts = cmd_part.split()
                seconds = int(parts[1]) if len(parts) > 1 else 30
                send_msg(c_id, f"⌨️ Typing for {seconds}s...", token=self.token)
                end = time.time() + seconds
                while time.time() < end:
                    requests.post(f"https://discord.com/api/v9/channels/{c_id}/typing", headers={"Authorization": self.token})
                    time.sleep(5)
                return

            # ========== AUTO-REPLY (TARGET BASED) ==========
            if cmd_lower.startswith("autoreply "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "❌ Usage: $autoreply @user", token=self.token)
                    return
                user_ids = []
                for mention in parts[1:]:
                    uid = extract_user_id_from_mention(mention)
                    if uid:
                        user_ids.append(uid)
                if not user_ids:
                    send_msg(c_id, "❌ No valid user", token=self.token)
                    return
                if c_id not in AUTOREPLY_TARGETS:
                    AUTOREPLY_TARGETS[c_id] = []
                for uid in user_ids:
                    if uid not in AUTOREPLY_TARGETS[c_id]:
                        AUTOREPLY_TARGETS[c_id].append(uid)
                send_msg(c_id, f"✅ Autoreply added: {len(user_ids)} users", token=self.token)
                return

            if cmd_lower.startswith("removeautoreply "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "❌ Usage: $removeautoreply @user", token=self.token)
                    return
                mention = parts[1]
                uid = extract_user_id_from_mention(mention)
                if not uid:
                    send_msg(c_id, "❌ Invalid user", token=self.token)
                    return
                if c_id in AUTOREPLY_TARGETS and uid in AUTOREPLY_TARGETS[c_id]:
                    AUTOREPLY_TARGETS[c_id].remove(uid)
                    if not AUTOREPLY_TARGETS[c_id]:
                        del AUTOREPLY_TARGETS[c_id]
                    send_msg(c_id, f"✅ Removed {mention}", token=self.token)
                else:
                    send_msg(c_id, "ℹ️ Not in autoreply", token=self.token)
                return

            if cmd_lower == "stopautoreply":
                if c_id in AUTOREPLY_TARGETS:
                    del AUTOREPLY_TARGETS[c_id]
                    send_msg(c_id, "✅ Autoreply cleared", token=self.token)
                else:
                    send_msg(c_id, "ℹ️ No autoreply", token=self.token)
                return

            # ========== AUTO-REPLY (JSON TRIGGER BASED) ==========
            if cmd_lower.startswith("addar "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "❌ Usage: $addar trigger,response", token=self.token)
                    return
                trigger_response = " ".join(parts[1:])
                if ',' not in trigger_response:
                    send_msg(c_id, "❌ Use comma: trigger,response", token=self.token)
                    return
                trigger, response = trigger_response.split(',', 1)
                trigger = trigger.strip()
                response = response.strip()
                auto_responses[trigger] = response
                save_autoreplies(auto_responses)
                send_msg(c_id, f"✅ Auto-response added: `{trigger}` → `{response}`", token=self.token)
                return

            if cmd_lower.startswith("removear "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "❌ Usage: $removear <trigger>", token=self.token)
                    return
                trigger = " ".join(parts[1:])
                if trigger in auto_responses:
                    del auto_responses[trigger]
                    save_autoreplies(auto_responses)
                    send_msg(c_id, f"✅ Removed: `{trigger}`", token=self.token)
                else:
                    send_msg(c_id, f"❌ Not found: `{trigger}`", token=self.token)
                return

            if cmd_lower == "lister":
                if not auto_responses:
                    send_msg(c_id, "ℹ️ No auto-responses configured.", token=self.token)
                    return
                lines = "\n".join([f"`{k}` → `{v}`" for k, v in list(auto_responses.items())[:20]])
                send_msg(c_id, f"**📋 AUTO-RESPONSES:**\n{lines}", token=self.token)
                return

            # ========== AUTOREACT ==========
            if cmd_lower.startswith("autoreact "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "❌ Usage: $autoreact <emoji>", token=self.token)
                    return
                emoji = parts[1]
                AUTOREACT_EMOJIS[c_id] = emoji
                send_msg(c_id, f"✅ Autoreact set: {emoji}", token=self.token)
                return

            if cmd_lower == "stopautoreact":
                if c_id in AUTOREACT_EMOJIS:
                    del AUTOREACT_EMOJIS[c_id]
                    send_msg(c_id, "✅ Autoreact stopped", token=self.token)
                else:
                    send_msg(c_id, "ℹ️ No autoreact", token=self.token)
                return

            # ========== GC COMMANDS ==========
            if cmd_lower.startswith("gcstart "):
                parts = cmd_part.split()
                interval = float(parts[1]) if len(parts) > 1 else 0.2
                names = load_gcnames()
                if not names:
                    send_msg(c_id, "❌ gcname.txt is empty", token=self.token)
                    return
                send_msg(c_id, f"✅ GC rename started with {len(names)} names. Use $gcstop to stop.", token=self.token)
                gc_running = True
                def _gc_rename():
                    i = 0
                    while gc_running:
                        try:
                            change_gc_name(c_id, names[i % len(names)], token=self.token)
                            i += 1
                            time.sleep(interval)
                        except:
                            time.sleep(1)
                threading.Thread(target=_gc_rename, daemon=True).start()
                if not hasattr(self, 'gc_running'):
                    self.gc_running = {}
                self.gc_running[c_id] = True
                return

            if cmd_lower == "gcstop":
                if hasattr(self, 'gc_running') and c_id in self.gc_running:
                    self.gc_running[c_id] = False
                    send_msg(c_id, "✅ GC rename stopped.", token=self.token)
                else:
                    send_msg(c_id, "ℹ️ No active GC rename", token=self.token)
                return

            # ========== MULTI COMMANDS (FIXED ASYNC & LIMITS) ==========
            if cmd_lower.startswith("multispam "):
                message_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "𝘼𝙨𝙝𝙪 On Top 🔥"
                tokens = load_tokens()
                multi_running["multispam"] = True
                send_msg(c_id, f"✅ Endless Multispam started. Use $stopmulti to stop.", token=self.token)
                async def _spam(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        while multi_running.get("multispam", False):
                            try:
                                async with sess.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": message_text}) as r:
                                    if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 0.5))
                                await asyncio.sleep(0.01)
                            except: await asyncio.sleep(0.5)
                threading.Thread(target=run_async_tasks, args=([_spam(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multispamall "):
                message_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "𝘼𝙨𝙝𝙪 On Top 🔥"
                tokens = load_tokens()
                if not guild_id:
                    send_msg(c_id, "❌ Run this in a server!", token=self.token)
                    return
                r = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers={"Authorization": self.token})
                if r.status_code == 200:
                    channels = [ch['id'] for ch in r.json() if ch['type'] == 0]
                    send_msg(c_id, f"✅ Endless Multispamall across {len(channels)} channels. Use $stopmulti to stop.", token=self.token)
                    multi_running["multispamall"] = True
                    async def _spamall(tok):
                        headers = {"Authorization": tok, "Content-Type": "application/json"}
                        async with aiohttp.ClientSession() as sess:
                            while multi_running.get("multispamall", False):
                                for ch in channels:
                                    if not multi_running.get("multispamall", False): return
                                    try:
                                        async with sess.post(f"https://discord.com/api/v9/channels/{ch}/messages", headers=headers, json={"content": message_text}) as r:
                                            if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 0.5))
                                        await asyncio.sleep(0.05)
                                    except: pass
                    threading.Thread(target=run_async_tasks, args=([_spamall(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multilongspam "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                user_id = parts[1]
                tokens = load_tokens()
                mention = f"<@{user_id}>"
                multi_running["multilongspam"] = True
                send_msg(c_id, f"✅ Endless Multi Long Spam started. Use $stopmulti to stop.", token=self.token)
                async def _longspam(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        while multi_running.get("multilongspam", False):
                            msg = get_long_spam(mention)
                            try:
                                async with sess.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": msg}) as r:
                                    if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 0.5))
                                await asyncio.sleep(0.2)
                            except: pass
                threading.Thread(target=run_async_tasks, args=([_longspam(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multiwordwall "):
                parts = cmd_part.split()
                word = " ".join(parts[1:]) if len(parts) > 1 else "𝘼𝙨𝙝𝙪"
                tokens = load_tokens()
                wall = (word + " ") * (2000 // (len(word) + 1))
                multi_running["multiww"] = True
                send_msg(c_id, f"✅ Endless Multi Wordwall started. Use $stopmulti to stop.", token=self.token)
                async def _wall(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        while multi_running.get("multiww", False):
                            try:
                                async with sess.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": wall[:2000]}) as r:
                                    if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 0.5))
                                await asyncio.sleep(0.2)
                            except: pass
                threading.Thread(target=run_async_tasks, args=([_wall(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multizalgo "):
                parts = cmd_part.split()
                text = " ".join(parts[1:]) if len(parts) > 1 else "𝘼𝙨𝙝𝙪 On Top"
                tokens = load_tokens()
                multi_running["multizalgo"] = True
                send_msg(c_id, f"✅ Endless Multi Zalgo started. Use $stopmulti to stop.", token=self.token)
                async def _zalgo(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        while multi_running.get("multizalgo", False):
                            try:
                                async with sess.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": zalgo_text(text)}) as r:
                                    if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 0.5))
                                await asyncio.sleep(0.2)
                            except: pass
                threading.Thread(target=run_async_tasks, args=([_zalgo(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multieveryone"):
                tokens = load_tokens()
                multi_running["multieveryone"] = True
                send_msg(c_id, f"✅ Endless Multi @everyone started. Use $stopmulti to stop.", token=self.token)
                async def _everyone(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        while multi_running.get("multieveryone", False):
                            try:
                                async with sess.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": "@everyone 𝘼𝙨𝙝𝙪 On Top 🔥"}) as r:
                                    if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 0.5))
                                await asyncio.sleep(0.1)
                            except: pass
                threading.Thread(target=run_async_tasks, args=([_everyone(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multinuke "):
                message_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "𝘼𝙨𝙝𝙪 On Top 🔥"
                tokens = load_tokens()
                if not guild_id:
                    send_msg(c_id, "❌ Run this in a server!", token=self.token)
                    return
                r = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers={"Authorization": self.token})
                if r.status_code == 200:
                    channels = [ch['id'] for ch in r.json() if ch['type'] == 0]
                    send_msg(c_id, f"✅ ENDLESS MULTINUKE STARTED! Use $stopmulti to stop.", token=self.token)
                    multi_running["multinuke"] = True
                    async def _nuke(tok):
                        headers = {"Authorization": tok, "Content-Type": "application/json"}
                        async with aiohttp.ClientSession() as sess:
                            while multi_running.get("multinuke", False):
                                for ch in channels:
                                    if not multi_running.get("multinuke", False): return
                                    try:
                                        async with sess.post(f"https://discord.com/api/v9/channels/{ch}/messages", headers=headers, json={"content": f"@everyone {message_text}"}) as r:
                                            if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 0.5))
                                        await asyncio.sleep(0.05)
                                    except: pass
                    threading.Thread(target=run_async_tasks, args=([_nuke(t) for t in tokens],), daemon=True).start()
                return

            # ========== MULTI DM ==========
            if cmd_lower.startswith("multidm "):
                parts = cmd_part.split()
                if len(parts) < 3: return
                user_id = parts[1]
                message_text = " ".join(parts[2:])
                tokens = load_tokens()
                send_msg(c_id, f"✅ {len(tokens)} tokens DMing {user_id}...", token=self.token)

                async def _dm(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        try:
                            async with sess.post("https://discord.com/api/v9/users/@me/channels", headers=headers, json={"recipient_id": str(user_id)}) as r:
                                if r.status not in [200, 201]: return
                                ch = (await r.json()).get("id")
                            if ch: await sess.post(f"https://discord.com/api/v9/channels/{ch}/messages", headers=headers, json={"content": message_text})
                        except: pass
                threading.Thread(target=run_async_tasks, args=([_dm(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multi_massdm "):
                message_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "𝘼𝙨𝙝𝙪 On Top 🔥"
                tokens = load_tokens()
                if not guild_id:
                    send_msg(c_id, "❌ Run this in a server!", token=self.token)
                    return
                r = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/members?limit=1000", headers={"Authorization": self.token})
                if r.status_code == 200:
                    members = [m['user']['id'] for m in r.json() if not m.get('user', {}).get('bot', False)]
                    send_msg(c_id, f"✅ Mass DMing {len(members)} members... (Background Process)", token=self.token)
                    chunk_size = max(1, len(members) // max(len(tokens), 1))
                    chunks = [members[i:i+chunk_size] for i in range(0, len(members), chunk_size)]
                    async def _dm_chunk(tok, member_chunk):
                        headers = {"Authorization": tok, "Content-Type": "application/json"}
                        async with aiohttp.ClientSession() as sess:
                            for mid in member_chunk:
                                try:
                                    async with sess.post("https://discord.com/api/v9/users/@me/channels", headers=headers, json={"recipient_id": str(mid)}) as r:
                                        if r.status not in [200, 201]: continue
                                        ch = (await r.json()).get("id")
                                    if ch: await sess.post(f"https://discord.com/api/v9/channels/{ch}/messages", headers=headers, json={"content": message_text})
                                    await asyncio.sleep(0.5)
                                except: pass
                    tasks = [_dm_chunk(tokens[i % len(tokens)], chunk) for i, chunk in enumerate(chunks)]
                    threading.Thread(target=run_async_tasks, args=(tasks,), daemon=True).start()
                return

            # ========== MULTI FRIEND / BLOCK ==========
            if cmd_lower.startswith("multifriend "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                user_id = parts[1]
                tokens = load_tokens()
                send_msg(c_id, f"✅ {len(tokens)} tokens sending friend request to {user_id}...", token=self.token)
                async def _fr(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        await sess.put(f"https://discord.com/api/v9/users/@me/relationships/{user_id}", headers=headers, json={"type": 1})
                threading.Thread(target=run_async_tasks, args=([_fr(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multiblock "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                user_id = parts[1]
                tokens = load_tokens()
                send_msg(c_id, f"✅ {len(tokens)} tokens blocking {user_id}...", token=self.token)
                async def _block(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        await sess.put(f"https://discord.com/api/v9/users/@me/relationships/{user_id}", headers=headers, json={"type": 2})
                threading.Thread(target=run_async_tasks, args=([_block(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower == "multi_accept_friends":
                tokens = load_tokens()
                send_msg(c_id, f"✅ {len(tokens)} tokens accepting friend requests...", token=self.token)
                async def _accept(tok):
                    headers = {"Authorization": tok}
                    async with aiohttp.ClientSession() as sess:
                        async with sess.get("https://discord.com/api/v9/users/@me/relationships", headers=headers) as r:
                            if r.status != 200: return
                            rels = await r.json()
                        for rel in rels:
                            if rel.get("type") == 3:
                                await sess.put(f"https://discord.com/api/v9/users/@me/relationships/{rel['id']}", headers={**headers, "Content-Type": "application/json"}, json={})
                threading.Thread(target=run_async_tasks, args=([_accept(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower == "multi_del_friends":
                tokens = load_tokens()
                send_msg(c_id, f"✅ {len(tokens)} tokens removing friends...", token=self.token)
                async def _delfr(tok):
                    headers = {"Authorization": tok}
                    async with aiohttp.ClientSession() as sess:
                        async with sess.get("https://discord.com/api/v9/users/@me/relationships", headers=headers) as r:
                            if r.status != 200: return
                            rels = await r.json()
                        for rel in rels:
                            if rel.get("type") == 1:
                                await sess.delete(f"https://discord.com/api/v9/users/@me/relationships/{rel['id']}", headers=headers)
                threading.Thread(target=run_async_tasks, args=([_delfr(t) for t in tokens],), daemon=True).start()
                return

            # ========== MULTI JOIN / LEAVE ==========
            if cmd_lower.startswith("multijoin "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                invite = parts[1].split("/")[-1]
                tokens = load_tokens()
                send_msg(c_id, f"✅ {len(tokens)} tokens joining {invite}...", token=self.token)
                async def _join(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        await sess.post(f"https://discord.com/api/v9/invites/{invite}", headers=headers, json={})
                threading.Thread(target=run_async_tasks, args=([_join(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multileave "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                guild_id = parts[1]
                tokens = load_tokens()
                send_msg(c_id, f"✅ {len(tokens)} tokens leaving {guild_id}...", token=self.token)
                async def _leave(tok):
                    headers = {"Authorization": tok}
                    async with aiohttp.ClientSession() as sess:
                        await sess.delete(f"https://discord.com/api/v9/users/@me/guilds/{guild_id}", headers=headers)
                threading.Thread(target=run_async_tasks, args=([_leave(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower == "multi_leaveall":
                tokens = load_tokens()
                send_msg(c_id, f"✅ {len(tokens)} tokens leaving ALL servers...", token=self.token)
                async def _leaveall(tok):
                    headers = {"Authorization": tok}
                    async with aiohttp.ClientSession() as sess:
                        async with sess.get("https://discord.com/api/v9/users/@me/guilds", headers=headers) as r:
                            if r.status != 200: return
                            guilds = await r.json()
                        for g in guilds:
                            await sess.delete(f"https://discord.com/api/v9/users/@me/guilds/{g['id']}", headers=headers)
                threading.Thread(target=run_async_tasks, args=([_leaveall(t) for t in tokens],), daemon=True).start()
                return

            # ========== MULTI SET NICK / AVATAR / USERNAME ==========
            if cmd_lower.startswith("multi_setnick "):
                nickname = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "𝘼𝙨𝙝𝙪"
                tokens = load_tokens()
                if not guild_id:
                    send_msg(c_id, "❌ Run this in a server!", token=self.token)
                    return
                send_msg(c_id, f"✅ {len(tokens)} tokens setting nick '{nickname}'...", token=self.token)
                async def _nick(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        await sess.patch(f"https://discord.com/api/v9/guilds/{guild_id}/members/@me", headers=headers, json={"nick": nickname})
                threading.Thread(target=run_async_tasks, args=([_nick(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multi_set_avatar "):
                parts = cmd_part.split()
                filename = parts[1] if len(parts) > 1 else "avatar.png"
                if not os.path.isfile(filename): return
                tokens = load_tokens()
                with open(filename, "rb") as f: raw = f.read()
                ext = filename.rsplit(".", 1)[-1].lower()
                mime = "image/png" if ext == "png" else "image/jpeg"
                data_uri = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
                send_msg(c_id, f"✅ {len(tokens)} tokens setting avatar...", token=self.token)
                async def _avatar(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        await sess.patch("https://discord.com/api/v9/users/@me", headers=headers, json={"avatar": data_uri})
                threading.Thread(target=run_async_tasks, args=([_avatar(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multi_set_username "):
                username = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "𝘼𝙨𝙝𝙪"
                tokens = load_tokens()
                send_msg(c_id, f"✅ {len(tokens)} tokens setting username...", token=self.token)
                async def _rename(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        await sess.patch("https://discord.com/api/v9/users/@me", headers=headers, json={"username": username})
                threading.Thread(target=run_async_tasks, args=([_rename(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multi_status_set "):
                status_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "𝘼𝙨𝙝𝙪 On Top 🔥"
                tokens = load_tokens()
                send_msg(c_id, f"✅ {len(tokens)} tokens setting status...", token=self.token)
                async def _status(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    payload = {"custom_status": {"text": status_text, "emoji_name": "🔥"}}
                    async with aiohttp.ClientSession() as sess:
                        await sess.patch("https://discord.com/api/v9/users/@me/settings", headers=headers, json=payload)
                threading.Thread(target=run_async_tasks, args=([_status(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multi_delete_msgs "):
                parts = cmd_part.split()
                limit = int(parts[1]) if len(parts) > 1 else 10
                tokens = load_tokens()
                send_msg(c_id, f"✅ {len(tokens)} tokens deleting last {limit} messages...", token=self.token)
                async def _delmsgs(tok):
                    headers = {"Authorization": tok}
                    async with aiohttp.ClientSession() as sess:
                        async with sess.get("https://discord.com/api/v9/users/@me", headers=headers) as r:
                            if r.status != 200: return
                            me_id = (await r.json()).get("id")
                        async with sess.get(f"https://discord.com/api/v9/channels/{c_id}/messages?limit=100", headers=headers) as r:
                            if r.status != 200: return
                            msgs = await r.json()
                        deleted = 0
                        for msg in msgs:
                            if str(msg.get("author", {}).get("id")) == str(me_id):
                                await sess.delete(f"https://discord.com/api/v9/channels/{c_id}/messages/{msg['id']}", headers=headers)
                                deleted += 1
                                if deleted >= limit: break
                threading.Thread(target=run_async_tasks, args=([_delmsgs(t) for t in tokens],), daemon=True).start()
                return

            # ========== MULTI REACT ==========
            if cmd_lower.startswith("multireact "):
                parts = cmd_part.split()
                if len(parts) < 3: return
                msg_id = parts[1]
                emoji = parts[2]
                tokens = load_tokens()
                encoded = urllib.parse.quote(emoji)
                send_msg(c_id, f"✅ {len(tokens)} tokens reacting...", token=self.token)
                async def _react(tok):
                    headers = {"Authorization": tok}
                    async with aiohttp.ClientSession() as sess:
                        await sess.put(f"https://discord.com/api/v9/channels/{c_id}/messages/{msg_id}/reactions/{encoded}/@me", headers=headers)
                threading.Thread(target=run_async_tasks, args=([_react(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multi_reactall "):
                parts = cmd_part.split()
                emoji = parts[1] if len(parts) > 1 else "🔥"
                limit = int(parts[2]) if len(parts) > 2 else 10
                tokens = load_tokens()
                encoded = urllib.parse.quote(emoji)
                send_msg(c_id, f"✅ {len(tokens)} tokens reacting to last {limit} messages...", token=self.token)
                async def _reactall(tok):
                    headers = {"Authorization": tok}
                    async with aiohttp.ClientSession() as sess:
                        async with sess.get(f"https://discord.com/api/v9/channels/{c_id}/messages?limit={limit}", headers=headers) as r:
                            if r.status != 200: return
                            msgs_data = await r.json()
                        for msg in msgs_data:
                            await sess.put(f"https://discord.com/api/v9/channels/{c_id}/messages/{msg['id']}/reactions/{encoded}/@me", headers=headers)
                threading.Thread(target=run_async_tasks, args=([_reactall(t) for t in tokens],), daemon=True).start()
                return

            # ========== MULTI GHOST PING ==========
            if cmd_lower.startswith("multi_ghost_ping "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                user_id = extract_user_id_from_mention(parts[1])
                tokens = load_tokens()
                send_msg(c_id, f"✅ {len(tokens)} tokens ghost pinging...", token=self.token)
                async def _ghost(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        async with sess.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": f"<@{user_id}>"}) as r:
                            if r.status in [200, 201]:
                                msg_id = (await r.json()).get("id")
                                if msg_id: await sess.delete(f"https://discord.com/api/v9/channels/{c_id}/messages/{msg_id}", headers=headers)
                threading.Thread(target=run_async_tasks, args=([_ghost(t) for t in tokens],), daemon=True).start()
                return

            # ========== MULTI PACK & DROWN (ENDLESS) ==========
            if cmd_lower.startswith("multi_pack ") or cmd_lower.startswith("multi_drown "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                user_id = extract_user_id_from_mention(parts[1])
                lang = parts[2] if len(parts) > 2 else "mix"
                tokens = load_tokens()
                banks = {"hindi": hindi_drown, "hinglish": hinglish_drown, "english": english_drown, "punjabi": punjabi_lines, "urdu": urdu_lines}
                pool = banks.get(lang, hindi_drown + hinglish_drown + english_drown + punjabi_lines + urdu_lines)
                multi_running["multipack_drown"] = True
                send_msg(c_id, f"✅ Endless Multi Pack/Drown started. Use $stopmulti to stop.", token=self.token)
                async def _multipd(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        while multi_running.get("multipack_drown", False):
                            line = random.choice(pool).replace("{mention}", f"<@{user_id}>")
                            await sess.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": line})
                            await asyncio.sleep(0.2)
                threading.Thread(target=run_async_tasks, args=([_multipd(t) for t in tokens],), daemon=True).start()
                return

            # ========== MULTI TYPING ==========
            if cmd_lower.startswith("multi_typing "):
                parts = cmd_part.split()
                seconds = int(parts[1]) if len(parts) > 1 else 30
                tokens = load_tokens()
                send_msg(c_id, f"✅ {len(tokens)} tokens typing for {seconds}s...", token=self.token)
                async def _typing(tok):
                    headers = {"Authorization": tok}
                    end = time.time() + seconds
                    async with aiohttp.ClientSession() as sess:
                        while time.time() < end:
                            await sess.post(f"https://discord.com/api/v9/channels/{c_id}/typing", headers=headers)
                            await asyncio.sleep(5)
                threading.Thread(target=run_async_tasks, args=([_typing(t) for t in tokens],), daemon=True).start()
                return

            # ========== STOP MULTI ==========
            if cmd_lower == "stopmulti":
                for key in list(multi_running.keys()):
                    multi_running[key] = False
                send_msg(c_id, "✅ All endless multi commands stopped.", token=self.token)
                return

            # ========== PING / STATUS ==========
            if cmd_lower == "ping":
                start = time.time()
                requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": self.token})
                latency = round((time.time() - start) * 1000, 2)
                send_msg(c_id, f"🏓 Pong! {latency}ms", token=self.token)
                return

            if cmd_lower == "status":
                uptime = round(time.time() - START_TIME, 1)
                status_msg = (
                    f"**𝘼𝙨𝙝𝙪 SELFBOT STATUS**\n"
                    f"Uptime: {uptime}s\n"
                    f"NC: {'ON' if ACTIVE_NC_CHANNELS.get(key_suffix) else 'OFF'}\n"
                    f"Spam: {'ON' if ACTIVE_SPAM_CHANNELS.get(key_suffix) else 'OFF'}\n"
                    f"Autoreply: {len(AUTOREPLY_TARGETS.get(c_id, []))} targets\n"
                    f"Autoreact: {AUTOREACT_EMOJIS.get(c_id, 'None')}\n"
                    f"Auto-responses: {len(auto_responses)} triggers"
                )
                send_msg(c_id, status_msg, token=self.token)
                return

            # ========== ACCESS / SUDO ==========
            if cmd_lower.startswith("access "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                mention = parts[1]
                user_id = extract_user_id_from_mention(mention)
                if user_id not in SUDO_USERS:
                    SUDO_USERS.append(user_id)
                    save_sudo(SUDO_USERS)
                    send_msg(c_id, f"✅ {mention} granted access", token=self.token)
                return

            if cmd_lower.startswith("removeaccess "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                mention = parts[1]
                user_id = extract_user_id_from_mention(mention)
                if user_id in SUDO_USERS:
                    SUDO_USERS.remove(user_id)
                    save_sudo(SUDO_USERS)
                    send_msg(c_id, f"✅ {mention} removed", token=self.token)
                return

            # ========== RESTART / PREFIX ==========
            if cmd_lower == "restart":
                send_msg(c_id, "🔄 Restarting...", token=self.token)
                os.execl(sys.executable, sys.executable, *sys.argv)
                return

            if cmd_lower.startswith("prefix "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                PREFIX = parts[1]
                send_msg(c_id, f"✅ Prefix changed to `{PREFIX}`", token=self.token)
                return

    def run(self):
        while self.running:
            try:
                self.ws = websocket.WebSocketApp("wss://gateway.discord.gg/?v=9&encoding=json", on_message=self.on_message)
                self.ws.run_forever()
            except Exception as e:
                logging.error(f"Bot {self.bot_index + 1} error: {e}")
                time.sleep(5)

# ==================== LAUNCH PROCESSES ====================
def run_all_bots():
    print("=" * 55)
    print("      𝘼𝙨𝙝𝙪 SELFBOT — ULTIMATE EDITION (LIMITLESS)")
    print("=" * 55)

    if not TOKENS:
        print("No tokens configured!")
        return

    clean_tokens = [t.strip() for t in TOKENS if t and t.strip() and not t.startswith('.')]
    print(f"Owner ID: {OWNER_ID}")
    print(f"Total tokens: {len(clean_tokens)}")
    print("Verifying tokens...")

    valid_tokens = []
    for i, token in enumerate(clean_tokens):
        user_id = verify_owner_id(token)
        if user_id:
            print(f"✅ Bot {i+1} verified (ID: {user_id})")
            valid_tokens.append(token)
        else:
            print(f"❌ Bot {i+1} - INVALID TOKEN!")

    if not valid_tokens:
        print("No valid tokens. Exiting...")
        return

    print(f"\n✅ {len(valid_tokens)} valid tokens! ALL LIMITS REMOVED ⚡")
    print(f"⚡ SPAM_DELAY: {SPAM_DELAY}s")
    print(f"⚡ PARALLEL_SPAM: {PARALLEL_SPAM}")
    print(f"⚡ PARALLEL_NC: {PARALLEL_NC}\n")

    bots = []
    for i, token in enumerate(valid_tokens):
        bot = DiscordSelfBot(token, i)
        thread = threading.Thread(target=bot.run, daemon=True)
        thread.start()
        bots.append(bot)
        time.sleep(1)

    print("✅ All bots running!")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        for bot in bots:
            bot.running = False
        print("All bots stopped.")

if __name__ == "__main__":
    run_all_bots()
