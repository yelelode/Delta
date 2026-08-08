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

# ==================== CONFIGS ====================
NC_DELAY = 0.005
SPAM_DELAY = 0.05
PARALLEL_SPAM = 5
PARALLEL_NC = 3

# ==================== NC LIST (UPDATED WITH SPECIAL PATTERNS) ====================
NC_LIST = [
    "{target} á´›á´‡Ê€Éª á´á´‹á´„ ÊŸá´¡á´…á´‡ á´„Êœxá´…-ð’«ð’«ð’«ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥",
    "{target} á´›á´‡Ê€Éª á´á´€á´€ á´‹á´€ Ê™Êœá´sá´…á´€-ð’«ð’«ð’«ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥",
    "{target} á´›á´‡Ê€Éª Ê™Êœá´‡É´ á´‹á´€ ÊŸá´œÉ´á´…-ð’«ð’«ð’«ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥",
    "{target} á´›á´‡Ê€Éª Ê™á´‡Êœá´‡É´ á´‹Éª á´€É´á´‹Êœ-ð’«ð’«ð’«ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥ð’«ð’«ð’«ðŸ”¥",
]

# ==================== SPAM MESSAGES ====================
SPAM_MESSAGES = [
    "# ð“†© ðŸ”¸ð“†ª ##ð˜¼ð™¨ð™ð™ª#ð™Šð™£ ð™ð™¤ð™¥ #ð—¥É´ï¼¤lâƒ ð—–á´‡ #ð—Ÿá´€ï¼¤á´„á´‡ #Éªð—¦ #sð—˜ #ð—§á´‡ð—­ #ð—§á´ #á´‹ð—¢ #ð—”á´á´á´€ #ð—–Êœð—¨á´…ð‘‡Éª #ð—›á´€ð—œIâƒ ",
    "# ð“†©ðŸˆ¸ð“†ª ##ð˜¼ð™¨ð™ð™ª#ð™Šð™£ ð™ð™¤ð™¥ #ð—¥É´ï¼¤lâƒ ð—–á´‡ #ð—Ÿá´€ï¼¤á´„á´‡ #Éªð—¦ #sð—˜ #ð—§á´‡ð—­ #ð—§á´ #á´‹ð—¢ #ð—”á´á´á´€ #ð—–Êœð—¨á´…ð‘‡Éª #ð—›á´€ð—œIâƒ ",
]

# ==================== REPLY TEXTS (UPDATED WITH NEW LINES) ====================
REPLY_TEXTS = [
    "ð–á´ Ê™ÊœÉª á´‹Êá´€ á´…ÉªÉ´ á´›Êœá´‡ á´Šá´€Ê™ á´›Ê€Ê á´á´€á´€ á´á´œá´ŠÊœá´‡ ð€á´˜É´á´€ ð‚Êœá´œá´› ðƒá´‡á´›Éª á´›ÊœÉª ðŸ’”",
    "ð€á´¡á´€á´¢ ðÉªá´„Êœá´‡ ð†á´œÊŸá´€á´€á´ ðŸ¤¢",
    "ð“Ê€Ê ðŒá´€á´€ É´á´‡ ð‚Êœá´œá´…É´á´‡ ðŒá´€Éª É¢á´ÊŸá´… ðŒá´‡á´…á´€ÊŸ ð‰á´‡á´‡á´›á´€ ðŸ‘‘",
    "ð“á´‡Ê€Éª ðŒá´€á´€ á´‹Éª ð‚Êœá´œá´› ðŒá´‡ ðŒá´‡Ê€á´€ ð‹á´œÉ´á´… ðŸ–•",
    "ðÊœá´êœ±á´€á´…Éªá´‹á´‡ ð€á´˜É´Éª ðá´‡Êœá´‡É´ ð‚Êœá´œá´…á´€ ðŸ–•",
    # ========== NEW AUTO-REPLY LINES (ADDED) ==========
    "ð˜¾ð™ð™–ð™¡ð™©ð™ž ð™ð™–ð™ž ð™œð™–ð™™ð™ž ð™˜ð™ð™–ð™¡ð™©ð™– ð™ð™–ð™ž ð™œð™ð™¤ð™™ð™– ð™™ð™–ð™¡ð™™ð™ª ð™ ð™®ð™– ð™–ð™–ð™¥ð™ ð™š ð™œð™–ð™£ð™™ ð™¢ð™š ð™¡ð™–ð™¬ð™™ð™–",
    "ð˜¼ð™–ð™ ð™ ð™ ð™®ð™– ð™¢ð™–ð™§ð™©ð™ž ð™ð™–ð™ž ð™¢ð™–ð™§ ð™™ð™š ð™©ð™–ð™¡ð™¬ð™–ð™§ ð™–ð™–ð™œð™–ð™§ ð™ ð™–ð™§ð™©ð™ž ð™ð™–ð™ž ð™¨ð™–ð™˜ð™˜ð™ð™– ð™¥ð™®ð™–ð™§ ð™©ð™¤ ð™ ð™ð™¤ð™¡ ð™™ð™š ð™¨ð™–ð™¡ð™«ð™–ð™§",
    "ð˜¼ð™–ð™¤ ð™ ð™ªð™˜ð™ ð™ ð™ð™šð™¡ð™©ð™š ð™ð™–ð™ž ð™–ð™–ð™¥ ð™©ð™–ð™£ð™œ ð™ªð™©ð™ð™–ð™¤ ð™ð™–ð™¢ ð™¥ð™šð™¡ð™©ð™š ð™ð™–ð™ž",
    "ð™©ð™šð™§ð™ž ð™¢ð™–ð™– ð™  ð™—ð™ð™¤ð™¨ð™™ð™š ð™¢ð™–ð™ž ð™ˆð˜¿ð™ƒ ð˜¾ð™ƒð˜¼ð™‰ð˜¼ ð™ˆð˜¼ð™Žð˜¼ð™‡ð˜¼ ð™™ð™–ð™–ð™¡ ð™  ð™©ð™šð™§ð™š ð™—ð™–ð™–ð™¥ ð™ ð™¤ ð™«ð™¤ ð™¨ð™¥ð™žð™˜ð™® ð™—ð™ð™¤ð™¨ð™™ð™– ð™ ð™ð™žð™¡ð™– ð™™ð™ªð™£ð™œð™– ðŸ¥µðŸ¤®",
]

# ==================== LONG SPAM TEMPLATES ====================
LONG_SPAM_TEMPLATES = [
    "{target} ð˜¼ð™¨ð™ð™ª ð‘ð”ðð’ ð˜ðŽð” " * 150,
    "{target} ð“ð„ð‘ðˆ ðŒð€ð€ ðŠð€ ðð‡ðŽð’ðƒð€ " * 150,
    "{target} ðð„ð‡ð„ð ðŠð„ ð‹ð€ð”ðƒð„ " * 150,
    "{target} ðŒð€ðƒð€ð‘ð‚ð‡ðŽðƒ " * 150,
    "{target} ðð‡ðŽð’ðƒðˆðŠð„ " * 150,
    "{target} ð‚ð‡ð”ð“ðˆð˜ð€ " * 150,
    "{target} ð†ð€ððƒð” " * 150,
    "{target} ðŠð”ð“ð“ð„ ðŠðˆ ð€ð”ð‹ð€ðƒ " * 150,
    "{target} ð“ð„ð‘ðˆ ðŒð”ðŒðŒð˜ ðƒðˆ ð…ð”ðƒðƒðˆ " * 150,
    "{target} ð“ð„ð‘ðˆ ðð„ð‡ð„ð ðƒðˆ ð€ððŠð‡ " * 150,
    "{target} ð‹ + ð‘ð€ð“ðˆðŽ + ðŒð€ð‹ðƒ + ð‚ðŽðð„ " * 100,
    "{target} ð†ð„ð“ ðƒð”ðð€ð˜ð€ ðð˜ ð˜¼ð™¨ð™ð™ª " * 120,
    "{target} ð“ð” ð‡ð€ð‘ ð‚ð‡ð”ðŠð€ ð‡ð€ðˆ " * 140,
    "{target} ð€ð”ðŠð€ð“ ðŒð„ðˆð ð‘ð„ð‡ " * 150,
    "{target} ð˜¼ð™¨ð™ð™ª ðŽð ð“ðŽð " * 150,
]

def get_long_spam(target_mention):
    template = random.choice(LONG_SPAM_TEMPLATES)
    base = template.replace("{target}", target_mention)
    if len(base) > 2000:
        base = base[:1997] + "..."
    return base

# ==================== DROWN LISTS ====================
hindi_drown = [
    "à¤¤à¥‚ à¤¬à¥‡à¤•à¤¾à¤° à¤¹à¥ˆ {mention} ðŸ’€",
    "à¤¤à¥‡à¤°à¥€ à¤®à¤¾à¤ à¤•à¤¾ à¤­à¥‹à¤¸à¤¡à¤¼à¤¾ {mention}",
    "à¤¤à¥‚ à¤—à¤§à¤¾ à¤¹à¥ˆ {mention} ðŸ«",
    "à¤¤à¥‡à¤°à¥€ à¤¬à¤¹à¤¨ à¤•à¥€ à¤†à¤à¤– {mention}",
    "à¤¤à¥‚ à¤ªà¥ˆà¤¦à¤¾ à¤¹à¥€ à¤¨à¤¹à¥€à¤‚ à¤¹à¥‹à¤¨à¤¾ à¤šà¤¾à¤¹à¤¿à¤ à¤¥à¤¾ {mention}",
    "à¤¤à¥‡à¤°à¥€ à¤”à¤•à¤¾à¤¤ à¤¨à¤¹à¥€à¤‚ à¤¹à¥ˆ {mention} â˜ ï¸",
    "à¤¤à¥‚ à¤¹à¤¾à¤° à¤šà¥à¤•à¤¾ à¤¹à¥ˆ {mention} ðŸ”¥",
    "à¤¬à¤‚à¤¦ à¤•à¤° à¤®à¥à¤à¤¹ à¤…à¤ªà¤¨à¤¾ {mention} ðŸ—‘ï¸",
    "à¤¤à¥‚ à¤à¤• à¤¨à¤¿à¤•à¤®à¥à¤®à¤¾ à¤¹à¥ˆ {mention} ðŸ˜‚",
    "ð˜¼ð™¨ð™ð™ª runs you {mention} ðŸ’¯",
]

hinglish_drown = [
    "Teri maa ka bhosda {mention} ðŸ’€",
    "Madarchod {mention}",
    "Bhosdike {mention} ðŸ«",
    "Chutiya hai tu {mention}",
    "Behen ke laude {mention}",
    "Aukaat mein reh {mention} ðŸ”¥",
    "ð˜¼ð™¨ð™ð™ª runs you {mention} ðŸ’¯",
    "Loser hai tu {mention} ðŸ˜‚",
    "Band kar apna munh {mention} ðŸ—‘ï¸",
    "Kutta saala {mention} â˜ ï¸",
]

english_drown = [
    "You're trash {mention} ðŸ’€",
    "You're a loser {mention}",
    "ð˜¼ð™¨ð™ð™ª runs you {mention} ðŸ”¥",
    "You're worthless {mention} ðŸ—‘ï¸",
    "Stay mad {mention} ðŸ˜‚",
    "Get ratio'd {mention} ðŸ’¯",
    "You lost {mention} â˜ ï¸",
    "Nobody likes you {mention}",
    "Cope harder {mention} ðŸ˜ˆ",
    "L + ratio + mald {mention} ðŸ«",
]

punjabi_lines = [
    "à¨¬à©‡ à¨šà©à©±à¨ª à¨•à¨° à¨œà¨¾ à¨“à¨‡ {mention} ðŸ’€",
    "à¨¤à©ˆà¨¨à©‚à©° à¨•à©‹à¨ˆ à¨¨à¨¹à©€à¨‚ à¨ªà©à©±à¨›à¨¦à¨¾ {mention} ðŸ—‘ï¸",
    "à¨¤à©‚à©° à¨œà¨¿à©±à¨¤ à¨¨à¨¹à©€à¨‚ à¨¸à¨•à¨¦à¨¾ à¨¸à¨¾à¨¡à©‡ à¨¤à©‹à¨‚ {mention} ðŸ”¥",
    "à¨ªà¨¾à¨—à¨² à¨œà¨¿à¨¹à¨¾ à¨¬à©°à¨¦à¨¾ à¨¹à©ˆà¨‚ à¨¤à©‚à©° {mention} ðŸ˜‚",
    "à¨ˆà¨Ÿà¨°à¨¨à¨² à¨¨à©‡ à¨¤à©ˆà¨¨à©‚à©° à¨¡à©à¨¬à©‹à¨‡à¨† {mention} â˜ ï¸",
    "à¨œà¨¾à¨¹ à¨“à¨¥à©‡ à¨¨à©±à¨¸ {mention} ðŸ˜ˆ",
    "à¨¤à©‡à¨°à©€ à¨•à©‹à¨ˆ à¨”à¨•à¨¾à¨¤ à¨¨à¨¹à©€à¨‚ {mention} ðŸ’¯",
    "à¨°à©‹à¨£à¨¾ à¨¬à©°à¨¦ à¨•à¨° {mention} ðŸ¤¡",
    "à¨®à¨¾à¨‚ à¨¨à©‚à©° à¨ªà©à©±à¨› à¨•à©‡ à¨† {mention}",
    "à¨˜à¨° à¨šà¨²à¨¾ à¨œà¨¾ à¨šà©à©±à¨ªà¨šà¨¾à¨ª {mention} ðŸŒŠ",
]

urdu_lines = [
    "Ø¨Û’ ØºØ§Ø¦Ø¨ ÛÙˆ Ø¬Ø§ ÛŒÛØ§Úº Ø³Û’ {mention} ðŸ’€",
    "ØªØ¬Ú¾ Ø³Û’ Ú©ÙˆØ¦ÛŒ Ù†ÛÛŒÚº ÚˆØ±ØªØ§ {mention} ðŸ˜‚",
    "Ø§ÛŒÙ¹Ø±Ù†Ù„ Ù†Û’ ØªØ¬Ú¾Û’ Ø®ØªÙ… Ú©Ø± Ø¯ÛŒØ§ {mention} ðŸ”¥",
    "ØªÙˆ ÛÙ…ÛŒØ´Û ÛØ§Ø±ØªØ§ ÛÛ’ {mention} â˜ ï¸",
    "Ø¨Ú©ÙˆØ§Ø³ Ø¨Ù†Ø¯ Ú©Ø± {mention} ðŸ—‘ï¸",
    "ØªÛŒØ±ÛŒ Ù…Ø§Úº Ø±Ùˆ Ø±ÛÛŒ ÛÛ’ ØªÛŒØ±ÛŒ ÙˆØ¬Û Ø³Û’ {mention} ðŸ’€",
    "Ù†Ú©Ù„ Ø¬Ø§ ÛŒÛØ§Úº Ø³Û’ {mention} ðŸ¤¡",
    "ØªØ¬Ú¾ Ù…ÛŒÚº Ú©ÙˆØ¦ÛŒ Ø¯Ù… Ù†ÛÛŒÚº {mention} ðŸ˜ˆ",
    "Ø§ÛŒÙ¹Ø±Ù†Ù„ Ù¾Ø± Ø¢Ù†Û’ Ú©ÛŒ Ø¬Ø±Ø£Øª ÛÛ’ ØªØ¬Ú¾Û’ {mention} ðŸ’¯",
    "Ú†Ù¾ ÛÙˆ Ø¬Ø§ Ø§Ø¨ {mention} ðŸŒŠ",
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
        return ["ð˜¼ð™¨ð™ð™ª ðŽð ð“ðŽð", "ð˜¼ð™¨ð™ð™ª ð‘ð”ðð’ ð”"]

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
            retry_after = response.json().get("retry_after", 2.0)
            time.sleep(retry_after)
        return response
    except:
        return None

def send_long_menu(c_id, text, token):
    """
    Auto-Chunking Logic: Agar Help menu 2000 characters se lamba ho, 
    to ye use safely split karke sequential messages mein send kar deta hai.
    """
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
        time.sleep(0.4)

def change_gc_name(g_id, name, token=None):
    if not token:
        return None
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        response = requests.patch(f"https://discord.com/api/v9/channels/{g_id}", headers=headers, json={"name": name})
        if response.status_code == 429:
            retry_after = response.json().get("retry_after", 2.0)
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

# ==================== WORKERS ====================
def nc_worker(g_id, target_mention, token=None):
    key = f"{g_id}_{token[:10] if token else ''}"
    while ACTIVE_NC_CHANNELS.get(key, False):
        try:
            base_line = random.choice(NC_LIST)
            new_text = base_line.replace("{target}", target_mention)
            if len(new_text) > 100:
                new_text = new_text[:100]
            change_gc_name(g_id, new_text, token)
            time.sleep(NC_DELAY)
        except Exception as e:
            logging.error(f"NC error: {e}")
            time.sleep(0.5)

def spam_worker(c_id, target_mention, token=None):
    key = f"{c_id}_{token[:10] if token else ''}"
    count = 0
    while ACTIVE_SPAM_CHANNELS.get(key, False):
        for msg_template in SPAM_MESSAGES:
            if not ACTIVE_SPAM_CHANNELS.get(key, False):
                break
            msg = msg_template.replace("##ð˜¼ð™¨ð™ð™ª#ð™Šð™£ ð™ð™¤ð™¥", target_mention)
            msg = msg.replace("ð˜¼ð™¨ð™ð™ª#ð™Šð™£ ð™ð™¤ð™¥", target_mention)
            send_msg(c_id, msg, token=token)
            count += 1
            if count % 100 == 0:
                logging.info(f"ðŸ“¤ {count} messages sent")
            time.sleep(SPAM_DELAY)

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
            print(f"âœ… Bot {self.bot_index + 1} Connected")

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
âš¡ â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• âš¡
               ð˜¼ð™¨ð™ð™ª  ð™Žð™šð™¡ð™›ð™—ð™¤ð™©  ð™‘ðŸ®  â€”  ð™ð™¡ð™©ð™žð™¢ð™–ð™©ð™š  ð™ˆð™šð™£ð™ª
       ðŸ‘‘ Owner: Ashu | System Status: Active ðŸ‘‘
âš¡ â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• âš¡

[ 1. SPAM MODES â€” SINGLE TOKEN ]
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
â€¢ $spam @user
  â””â”€ Kaam: Specific user ko mention karke fast parallel spam karta hai.
  â””â”€ Chalu: $spam @user
  â””â”€ Roke: $stopspam

â€¢ $spammm <text>
  â””â”€ Kaam: Multi-line (Exact 40 lines per message) fast repeat text spam.
  â””â”€ Chalu: $spammm Text Here
  â””â”€ Roke: $spamoff

â€¢ $nc @user
  â””â”€ Kaam: Group Chat / Channel ka naam fast rename karke user ko spam karta hai.
  â””â”€ Chalu: $nc @user
  â””â”€ Roke: $stopnc

â€¢ $spamall <msg>
  â””â”€ Kaam: Server ke saare text channels mein ek sath spam karta hai.
  â””â”€ Chalu: $spamall Ashu On Top
  â””â”€ Roke: $stopspamall

â€¢ $longspam @user
  â””â”€ Kaam: 2000 character lambe heavy text paragraphs bhej kar channel flood karta hai.
  â””â”€ Chalu: $longspam @user
  â””â”€ Roke: $stoplongspam

â€¢ $wordwall <word>
  â””â”€ Kaam: Ek hi lafz/word ka 2000-char lamba wall bana kar spam karta hai.
  â””â”€ Chalu: $wordwall ASHU
  â””â”€ Roke: $stopwordwall

â€¢ $zalgo <text>
  â””â”€ Kaam: Corrupted Zalgo/Glitchy fonts ka use karke spam karta hai.
  â””â”€ Chalu: $zalgo Hello World
  â””â”€ Roke: $stopzalgo

â€¢ $repeat_spam <text>
  â””â”€ Kaam: Infinite loop mein same message repeat bhejta rehta hai.
  â””â”€ Chalu: $repeat_spam Hello
  â””â”€ Roke: $stoprepeat

â€¢ $counter_spam <prefix>
  â””â”€ Kaam: Message ke aage 1, 2, 3 numbers count karke spam karta hai.
  â””â”€ Chalu: $counter_spam Count
  â””â”€ Roke: $stopcounter

â€¢ $edit_spam <msg>
  â””â”€ Kaam: Pehle msg bhejta hai fir use baar-baar edit karke spam bypass karta hai.
  â””â”€ Chalu: $edit_spam Bypass
  â””â”€ Roke: $stopeditspam

â€¢ $invis
  â””â”€ Kaam: Complete invisible/blank characters ka spam karta hai.
  â””â”€ Chalu: $invis
  â””â”€ Roke: $stopinvis

â€¢ $nitro_spam
  â””â”€ Kaam: Fake Nitro gift links generate karke continuous flood karta hai.
  â””â”€ Chalu: $nitro_spam
  â””â”€ Roke: $stopnitro


[ 2. MULTI-TOKEN COMMANDS â€” ALL BOTS ]
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
â€¢ $multispam <msg>
  â””â”€ Kaam: Saare added tokens ek saath current channel mein spam karenge.
  â””â”€ Chalu: $multispam Ashu Gang
  â””â”€ Roke: $stopmulti

â€¢ $multispamall <msg>
  â””â”€ Kaam: Saare tokens server ke saare channels mein spam karte hain.
  â””â”€ Chalu: $multispamall Ashu Multi
  â””â”€ Roke: $stopmulti

â€¢ $multinuke <msg>
  â””â”€ Kaam: Saare tokens @everyone tag ke sath saare channels mein nuke spam karenge.
  â””â”€ Chalu: $multinuke Server Down
  â””â”€ Roke: $stopmulti

â€¢ $multidm <user_id> <msg>
  â””â”€ Kaam: Saare tokens target user ke Personal DM mein message bhejenge.
  â””â”€ Chalu: $multidm 123456789 Hi
  â””â”€ Roke: Automatic (Task Complete hone par)

â€¢ $multi_massdm <msg>
  â””â”€ Kaam: Server ke har ek member ko saare tokens se DM spam karta hai.
  â””â”€ Chalu: $multi_massdm Check this
  â””â”€ Roke: Automatic

â€¢ $multijoin <invite_code>
  â””â”€ Kaam: Saare tokens ek saath server join karenge.
  â””â”€ Chalu: $multijoin discord.gg/xyz
  â””â”€ Roke: Automatic

â€¢ $multileave <guild_id>
  â””â”€ Kaam: Saare tokens specified server se leave kar denge.
  â””â”€ Chalu: $multileave 987654321
  â””â”€ Roke: Automatic

â€¢ $multi_leaveall
  â””â”€ Kaam: Saare tokens unke saare joined servers se leave ho jayenge.
  â””â”€ Chalu: $multi_leaveall
  â””â”€ Roke: Automatic

â€¢ $multifriend / $multiblock <user_id>
  â””â”€ Kaam: Target ID ko saare tokens se Mass Friend Request / Block bhejta hai.
  â””â”€ Chalu: $multifriend ID / $multiblock ID
  â””â”€ Roke: Automatic

â€¢ $multi_setnick <name>
  â””â”€ Kaam: Server mein saare tokens ka Nickname change kar deta hai.
  â””â”€ Chalu: $multi_setnick Ashu
  â””â”€ Roke: Automatic

â€¢ $multireact <msg_id> <emoji>
  â””â”€ Kaam: Ek specific message par saare tokens se emoji reaction dilwata hai.
  â””â”€ Chalu: $multireact 11223344 ðŸ”¥
  â””â”€ Roke: Automatic


[ 3. DROWN & PACK MODES â€” FLOODING ]
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
â€¢ $drown_hindi / $drown_hinglish / $drown_english / $drown_mix @user
  â””â”€ Kaam: Selected bhasha (Language) mein targeted non-stop abuse flood karta hai.
  â””â”€ Chalu: $drown_hinglish @user
  â””â”€ Roke: $stopdrown

â€¢ $continuous_pack @user <lang>
  â””â”€ Kaam: Continuous loop mein heavy pack/abuse dialogue lines bhejta hai.
  â””â”€ Chalu: $continuous_pack @user hindi
  â””â”€ Roke: $stoppack

â€¢ $hindi_pack / $hinglish_pack / $punjabi_pack / $urdu_pack / $god_pack @user
  â””â”€ Kaam: Pre-defined 10-20 heavy regional pack lines single shot mein send karta hai.
  â””â”€ Chalu: $god_pack @user
  â””â”€ Roke: Automatic (Lines complete hone par)


[ 4. AUTO-REPLY & SYSTEM SETTINGS ]
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
â€¢ $autoreply @user
  â””â”€ Kaam: Targeted user jab bhi message karega, bot use automatic roast/reply dega.
  â””â”€ Chalu: $autoreply @user
  â””â”€ Roke: $removeautoreply @user  YA  $stopautoreply

â€¢ $addar <trigger>,<response>
  â””â”€ Kaam: Custom word trigger par auto-response set karta hai (e.g. hi -> hello).
  â””â”€ Chalu: $addar hi,hello
  â””â”€ Roke: $removear hi

â€¢ $autoreact <emoji>
  â””â”€ Kaam: Channel ke saare aane wale new messages par automatic emoji react karega.
  â””â”€ Chalu: $autoreact ðŸ”¥
  â””â”€ Roke: $stopautoreact

â€¢ $gcstart <delay>
  â””â”€ Kaam: Group Chat ka name gcname.txt se padh kar continuous fast rename karega.
  â””â”€ Chalu: $gcstart 0.5
  â””â”€ Roke: $gcstop

â€¢ $prefix <new_prefix>
  â””â”€ Kaam: Self-bot ka command prefix change karta hai.
  â””â”€ Chalu: $prefix !
  â””â”€ Roke: Automatic

â€¢ $access @user / $removeaccess @user
  â””â”€ Kaam: Dusre user ko bot commands chalane ki Sudo permission deta/hata-ta hai.
  â””â”€ Chalu: $access @user
  â””â”€ Roke: $removeaccess @user

â€¢ $ping / $status / $restart
  â””â”€ Kaam: Bot ki latency (speed), active status, ya bot ko restart karne ke liye.
  â””â”€ Chalu: $ping / $status / $restart

âš¡ â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• âš¡
             ðŸ”¥  ð˜¼ð™¨ð™ð™ª  ð™Šð™£  ð™ð™¤ð™¥  â€”  ð™ð™ªð™¡ð™¡  ð˜¾ð™¤ð™£ð™©ð™§ð™¤ð™¡  ðŸ”¥
âš¡ â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• âš¡
"""
                send_long_menu(c_id, full_help, token=self.token)
                return

            # ========== OTHER HELP MENUS ==========
            if cmd_lower == "general" or cmd_lower == "gnrl":
                send_msg(c_id, """**```fix
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
   âš™ï¸  ð˜¼ð™¨ð™ð™ª  |  GENERAL COMMANDS
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
  â€¢ help / h           â€” Full help index
  â€¢ general / gnrl     â€” This menu
  â€¢ spamhelp / sh      â€” Spam commands menu
  â€¢ multihelp / mh     â€” Multi-token menu
  â€¢ drownhelp / dh     â€” Drown/pack menu
  â€¢ trollhelp / th     â€” Troll/fake menu
  â€¢ autoreplyhelp / arh â€” Auto-reply menu
  â€¢ gchelp / gch       â€” Group chat menu

  â€¢ ping               â€” Check latency
  â€¢ status             â€” Bot status
  â€¢ restart            â€” Restart bot
  â€¢ prefix <p>         â€” Change prefix
  â€¢ access @user       â€” Give sudo access
  â€¢ removeaccess @user â€” Remove sudo access

  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        â˜ ï¸  ð˜¼ð™¨ð™ð™ª On Top  â˜ ï¸
```**""", token=self.token)
                return

            if cmd_lower == "spamhelp" or cmd_lower == "sh":
                send_msg(c_id, """**```fix
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
   ðŸ’¥  ð˜¼ð™¨ð™ð™ª  |  SPAM COMMANDS
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
  SINGLE TOKEN SPAM
  â€¢ spam @user          â€” Start spam in channel (+stopspam)
  â€¢ nc @user            â€” Nickname change spam (+stopnc)
  â€¢ spamall <msg>       â€” Spam in all channels (+stopspamall)
  â€¢ invis <count>       â€” Invisible char spam (+stopinvis)
  â€¢ nitro_spam <count>  â€” Fake nitro links spam (+stopnitro)
  â€¢ zalgo <count> <t>   â€” Zalgo text (+stopzalgo)
  â€¢ repeat_spam <msg>   â€” Infinite repeat spam (+stoprepeat)
  â€¢ counter_spam <pre>  â€” Auto-counter spam (+stopcounter)
  â€¢ longspam @u <cnt>   â€” 2000-char spam (+stoplongspam)
  â€¢ wordwall <word>     â€” 2000-char word wall (+stopwordwall)
  â€¢ edit_spam <msg>     â€” Edit-spam bypass (+stopeditspam)
  â€¢ spammm <msg>        â€” Fast 0.05s spam (+spamoff)

  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        â˜ ï¸  ð˜¼ð™¨ð™ð™ª On Top  â˜ ï¸
```**""", token=self.token)
                return

            if cmd_lower == "multihelp" or cmd_lower == "mh":
                send_msg(c_id, """**```fix
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
   ðŸŒ  ð˜¼ð™¨ð™ð™ª  |  MULTI-TOKEN COMMANDS
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
  SPAM
  â€¢ multispam <msg>      â€” All tokens spam channel
  â€¢ multispamall <msg>   â€” All tokens spam all channels
  â€¢ multilongspam <id>   â€” All tokens long spam
  â€¢ multiwordwall <word> â€” All tokens word wall
  â€¢ multizalgo <cnt> <t> â€” All tokens zalgo spam
  â€¢ multieveryone <cnt>  â€” All tokens @everyone

  DM / FRIENDS
  â€¢ multidm <id> <msg>   â€” All tokens DM user
  â€¢ multi_massdm <msg>   â€” All tokens DM all members
  â€¢ multifriend <id>     â€” All tokens friend request
  â€¢ multiblock <id>      â€” All tokens block user
  â€¢ multi_accept_friends â€” All tokens accept friend reqs
  â€¢ multi_del_friends    â€” All tokens remove friends

  SERVER
  â€¢ multijoin <invite>   â€” All tokens join server
  â€¢ multileave <gid>     â€” All tokens leave server
  â€¢ multi_leaveall       â€” All tokens leave ALL servers
  â€¢ multi_setnick <name> â€” All tokens set nickname
  â€¢ multi_set_avatar <f> â€” All tokens set avatar
  â€¢ multi_set_username <n> â€” All tokens set username
  â€¢ multi_status_set <t> â€” All tokens set status
  â€¢ multi_delete_msgs <n> â€” All tokens delete own msgs

  OTHER
  â€¢ multireact <id> <e>  â€” All tokens react
  â€¢ multi_reactall <e>   â€” All tokens react last 10 msgs
  â€¢ multi_ghost_ping @u  â€” All tokens ghost ping
  â€¢ multi_pack @u <l>    â€” All tokens abuse pack
  â€¢ multi_drown <id> <l> â€” All tokens drown
  â€¢ multi_typing <secs>  â€” All tokens typing indicator
  â€¢ multinuke <msg>      â€” All tokens nuke server

  â€¢ stopmulti            â€” Stop all multi commands

  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        â˜ ï¸  ð˜¼ð™¨ð™ð™ª On Top  â˜ ï¸
```**""", token=self.token)
                return

            if cmd_lower == "drownhelp" or cmd_lower == "dh":
                send_msg(c_id, """**```fix
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
   ðŸ’€  ð˜¼ð™¨ð™ð™ª  |  DROWN / PACK COMMANDS
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
  SINGLE TOKEN
  â€¢ drown_hindi @u       â€” Hindi abuse flood
  â€¢ drown_hinglish @u    â€” Hinglish abuse flood
  â€¢ drown_english @u     â€” English abuse flood
  â€¢ drown_mix @u         â€” Mixed language flood
  â€¢ hindi_pack @u        â€” Hindi pack
  â€¢ hinglish_pack @u     â€” Hinglish pack
  â€¢ punjabi_pack @u      â€” Punjabi pack
  â€¢ urdu_pack @u         â€” Urdu pack
  â€¢ mix_all_pack @u      â€” All languages mix
  â€¢ god_pack @u          â€” All languages combined
  â€¢ continuous_pack @u   â€” Endless pack (+stoppack)
  â€¢ stoppack             â€” Stop continuous pack
  â€¢ stopdrown            â€” Stop any drown

  MULTI TOKEN
  â€¢ multi_pack @u <lang>  â€” All tokens pack
  â€¢ multi_drown <id>      â€” All tokens drown

  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        â˜ ï¸  ð˜¼ð™¨ð™ð™ª On Top  â˜ ï¸
```**""", token=self.token)
                return

            if cmd_lower == "trollhelp" or cmd_lower == "th":
                send_msg(c_id, """**```fix
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
   ðŸŽ­  ð˜¼ð™¨ð™ð™ª  |  TROLL / FAKE COMMANDS
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
  FAKE ACTIONS
  â€¢ fake_ban @u          â€” Fake ban announcement
  â€¢ fake_mute @u         â€” Fake mute announcement
  â€¢ fake_kick @u         â€” Fake kick announcement
  â€¢ fake_warn @u         â€” Fake warning DM

  TROLL CONTENT
  â€¢ rick_roll @u         â€” Disguised rick roll
  â€¢ crash_dm @u          â€” Invisible char DM bomb
  â€¢ ip_logger @u         â€” Fake IP logger
  â€¢ countdown [n] [msg]  â€” Countdown then message
  â€¢ typing_spam [secs]   â€” Keep typing indicator

  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        â˜ ï¸  ð˜¼ð™¨ð™ð™ª On Top  â˜ ï¸
```**""", token=self.token)
                return

            if cmd_lower == "autoreplyhelp" or cmd_lower == "arh":
                send_msg(c_id, """**```fix
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
   ðŸ”„  ð˜¼ð™¨ð™ð™ª  |  AUTO-REPLY COMMANDS
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
  TARGET BASED
  â€¢ autoreply @user      â€” Auto-reply to user
  â€¢ removeautoreply @user â€” Remove auto-reply
  â€¢ stopautoreply        â€” Clear all auto-replies

  TRIGGER BASED (JSON file)
  â€¢ addar trigger,resp   â€” Add auto-response
  â€¢ removear <trigger>   â€” Remove auto-response
  â€¢ lister               â€” List all auto-responses

  REACTIONS
  â€¢ autoreact <emoji>    â€” Auto-react with emoji
  â€¢ stopautoreact        â€” Stop auto-react

  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        â˜ ï¸  ð˜¼ð™¨ð™ð™ª On Top  â˜ ï¸
```**""", token=self.token)
                return

            if cmd_lower == "gchelp" or cmd_lower == "gch":
                send_msg(c_id, """**```fix
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
   ðŸ’¬  ð˜¼ð™¨ð™ð™ª  |  GROUP CHAT COMMANDS
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
  â€¢ gcstart [interval]   â€” Auto-rename GC (gcname.txt)
  â€¢ gcstop               â€” Stop auto-rename
  â€¢ gc_mass_add          â€” Add all friends to GC
  â€¢ gc_invite_spam [n]   â€” Spam in GC
  â€¢ set_gc_icon [file]   â€” Change GC icon

  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        â˜ ï¸  ð˜¼ð™¨ð™ð™ª On Top  â˜ ï¸
```**""", token=self.token)
                return

            # ========== SPAM COMMANDS ==========
            if cmd_lower.startswith("spam "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "âŒ Usage: $spam @user", token=self.token)
                    return
                mention = parts[1]
                ACTIVE_SPAM_CHANNELS[key_suffix] = True
                for i in range(PARALLEL_SPAM):
                    threading.Thread(target=spam_worker, args=(c_id, mention, self.token), daemon=True).start()
                send_msg(c_id, f"âœ… Spam started (x{PARALLEL_SPAM} parallel)", token=self.token)
                return

            if cmd_lower == "stopspam":
                ACTIVE_SPAM_CHANNELS[key_suffix] = False
                send_msg(c_id, "âœ… Spam stopped", token=self.token)
                return

            # ========== $SPAMMM â€” MULTI-LINE REPEAT SPAM (EXACT 40 TIMES) ==========
            if cmd_lower.startswith("spammm "):
                spammingss = True
                if len(cmd_part.split()) > 1:
                    base_text = " ".join(cmd_part.split()[1:])
                else:
                    base_text = "Garv tmkb me lun daalke fyter bnadunga usko ðŸ¤£ðŸ”¥"
                
                lines_count = 40
                msg_text = (base_text + "\n") * lines_count
                
                if len(msg_text) > 2000:
                    msg_text = msg_text[:1997] + "..."
                
                send_msg(c_id, f"âœ… Spammm started (40 lines/msg). Use $spamoff to stop.", token=self.token)
                def _spam_fast():
                    while spammingss:
                        send_msg(c_id, msg_text, token=self.token)
                        time.sleep(0.05)
                threading.Thread(target=_spam_fast, daemon=True).start()
                return

            if cmd_lower == "spamoff":
                spammingss = False
                send_msg(c_id, "âœ… Spammm stopped.", token=self.token)
                return

            # ========== NC ==========
            if cmd_lower.startswith("nc "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "âŒ Usage: $nc @user", token=self.token)
                    return
                mention = parts[1]
                ACTIVE_NC_CHANNELS[key_suffix] = True
                for i in range(PARALLEL_NC):
                    threading.Thread(target=nc_worker, args=(c_id, mention, self.token), daemon=True).start()
                send_msg(c_id, f"âœ… NC started (x{PARALLEL_NC} parallel)", token=self.token)
                return

            if cmd_lower == "stopnc":
                ACTIVE_NC_CHANNELS[key_suffix] = False
                send_msg(c_id, "âœ… NC stopped", token=self.token)
                return

            # ========== UNLIMITED SPAMALL ==========
            if cmd_lower.startswith("spamall "):
                multi_running[f"spamall_{key_suffix}"] = True
                msg_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "ð˜¼ð™¨ð™ð™ª On Top ðŸ”¥"
                if not guild_id:
                    send_msg(c_id, "âŒ Run this in a server!", token=self.token)
                    return
                r = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers={"Authorization": self.token})
                if r.status_code == 200:
                    channels = [ch['id'] for ch in r.json() if ch['type'] == 0]
                    send_msg(c_id, f"âœ… Endless Spamall across {len(channels)} channels. Use $stopspamall to end.", token=self.token)
                    def _spamall():
                        while multi_running.get(f"spamall_{key_suffix}", False):
                            for ch in channels:
                                if not multi_running.get(f"spamall_{key_suffix}", False): break
                                send_msg(ch, msg_text, token=self.token)
                                time.sleep(0.1)
                    threading.Thread(target=_spamall, daemon=True).start()
                return

            if cmd_lower == "stopspamall":
                multi_running[f"spamall_{key_suffix}"] = False
                send_msg(c_id, "âœ… Spamall stopped", token=self.token)
                return

            # ========== UNLIMITED LONG SPAM ==========
            if cmd_lower.startswith("longspam "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                mention = parts[1]
                multi_running[f"longspam_{key_suffix}"] = True
                send_msg(c_id, f"âœ… Endless Longspam started. Use $stoplongspam to end.", token=self.token)
                def _longspam_loop():
                    while multi_running.get(f"longspam_{key_suffix}", False):
                        msg = get_long_spam(mention)
                        send_msg(c_id, msg, token=self.token)
                        time.sleep(0.5)
                threading.Thread(target=_longspam_loop, daemon=True).start()
                return

            if cmd_lower == "stoplongspam":
                multi_running[f"longspam_{key_suffix}"] = False
                send_msg(c_id, "âœ… Longspam stopped.", token=self.token)
                return

            # ========== UNLIMITED WORDWALL ==========
            if cmd_lower.startswith("wordwall "):
                parts = cmd_part.split()
                word = " ".join(parts[1:]) if len(parts) > 1 else "ð˜¼ð™¨ð™ð™ª"
                wall = (word + " ") * (2000 // (len(word) + 1))
                multi_running[f"wordwall_{key_suffix}"] = True
                send_msg(c_id, f"âœ… Endless Wordwall started. Use $stopwordwall to end.", token=self.token)
                def _ww_loop():
                    while multi_running.get(f"wordwall_{key_suffix}", False):
                        send_msg(c_id, wall[:2000], token=self.token)
                        time.sleep(0.5)
                threading.Thread(target=_ww_loop, daemon=True).start()
                return

            if cmd_lower == "stopwordwall":
                multi_running[f"wordwall_{key_suffix}"] = False
                send_msg(c_id, "âœ… Wordwall stopped.", token=self.token)
                return

            # ========== UNLIMITED ZALGO SPAM ==========
            if cmd_lower.startswith("zalgo "):
                parts = cmd_part.split()
                text = " ".join(parts[1:]) if len(parts) > 1 else "ð˜¼ð™¨ð™ð™ª On Top"
                multi_running[f"zalgo_{key_suffix}"] = True
                send_msg(c_id, f"âœ… Endless Zalgo started. Use $stopzalgo to end.", token=self.token)
                def _zalgo_loop():
                    while multi_running.get(f"zalgo_{key_suffix}", False):
                        send_msg(c_id, zalgo_text(text), token=self.token)
                        time.sleep(0.5)
                threading.Thread(target=_zalgo_loop, daemon=True).start()
                return

            if cmd_lower == "stopzalgo":
                multi_running[f"zalgo_{key_suffix}"] = False
                send_msg(c_id, "âœ… Zalgo spam stopped.", token=self.token)
                return

            # ========== REPEAT SPAM ==========
            if cmd_lower.startswith("repeat_spam "):
                msg_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "ð˜¼ð™¨ð™ð™ª On Top ðŸ”¥"
                multi_running[f"repeat_{key_suffix}"] = True
                send_msg(c_id, f"âœ… Repeat spam started. Use $stoprepeat to stop.", token=self.token)
                def _repeat():
                    while multi_running.get(f"repeat_{key_suffix}", False):
                        send_msg(c_id, msg_text, token=self.token)
                        time.sleep(0.2)
                threading.Thread(target=_repeat, daemon=True).start()
                return

            if cmd_lower == "stoprepeat":
                multi_running[f"repeat_{key_suffix}"] = False
                send_msg(c_id, "âœ… Repeat spam stopped.", token=self.token)
                return

            # ========== COUNTER SPAM ==========
            if cmd_lower.startswith("counter_spam "):
                prefix_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "ð˜¼ð™¨ð™ð™ª"
                multi_running[f"counter_{key_suffix}"] = True
                send_msg(c_id, f"âœ… Counter spam started. Use $stopcounter to stop.", token=self.token)
                def _counter():
                    i = 1
                    while multi_running.get(f"counter_{key_suffix}", False):
                        send_msg(c_id, f"{prefix_text} `#{i}`", token=self.token)
                        i += 1
                        time.sleep(0.15)
                threading.Thread(target=_counter, daemon=True).start()
                return

            if cmd_lower == "stopcounter":
                multi_running[f"counter_{key_suffix}"] = False
                send_msg(c_id, "âœ… Counter spam stopped.", token=self.token)
                return

            # ========== EDIT SPAM ==========
            if cmd_lower.startswith("edit_spam "):
                msg_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "ð˜¼ð™¨ð™ð™ª On Top ðŸ”¥"
                phrases = [
                    msg_text,
                    "ð„ð­ðžð«ð§ðšð¥ ð‘ð®ð§ð¬ ð” ðŸ”¥",
                    "ðð¨ð›ð¨ðð² ð‚ðšð§ ð’ð­ð¨p ð”ð¬",
                    "ð˜¼ð™¨ð™ð™ª ð†ðšð§ð  ðŸ’€",
                ]
                multi_running[f"edit_{key_suffix}"] = True
                send_msg(c_id, f"âœ… Edit spam started. Use $stopeditspam to stop.", token=self.token)
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
                                    time.sleep(0.3)
                                except: pass
                threading.Thread(target=_edit_loop, daemon=True).start()
                return

            if cmd_lower == "stopeditspam":
                multi_running[f"edit_{key_suffix}"] = False
                send_msg(c_id, "âœ… Edit spam stopped.", token=self.token)
                return

            # ========== INVISIBLE SPAM ==========
            if cmd_lower == "invis":
                invis = "\u200b" * 500
                multi_running[f"invis_{key_suffix}"] = True
                send_msg(c_id, f"âœ… Endless Invis started. Use $stopinvis to end.", token=self.token)
                def _invis_loop():
                    while multi_running.get(f"invis_{key_suffix}", False):
                        send_msg(c_id, invis, token=self.token)
                        time.sleep(0.3)
                threading.Thread(target=_invis_loop, daemon=True).start()
                return

            if cmd_lower == "stopinvis":
                multi_running[f"invis_{key_suffix}"] = False
                send_msg(c_id, "âœ… Invis spam stopped.", token=self.token)
                return

            # ========== NITRO SPAM ==========
            if cmd_lower == "nitro_spam":
                chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                multi_running[f"nitro_{key_suffix}"] = True
                send_msg(c_id, f"âœ… Endless Fake Nitro started. Use $stopnitro to end.", token=self.token)
                def _nitro_loop():
                    while multi_running.get(f"nitro_{key_suffix}", False):
                        code = ''.join(random.choices(chars, k=16))
                        send_msg(c_id, f"ðŸŽ‰ **FREE NITRO** https://discord.gift/{code}", token=self.token)
                        time.sleep(0.5)
                threading.Thread(target=_nitro_loop, daemon=True).start()
                return
                
            if cmd_lower == "stopnitro":
                multi_running[f"nitro_{key_suffix}"] = False
                send_msg(c_id, "âœ… Nitro spam stopped.", token=self.token)
                return

            # ========== DROWN COMMANDS ==========
            def start_drown(pool, user_id):
                multi_running[f"drown_{key_suffix}"] = True
                send_msg(c_id, f"âœ… Endless Drown started. Use $stopdrown to stop.", token=self.token)
                def _drown_loop():
                    while multi_running.get(f"drown_{key_suffix}", False):
                        line = random.choice(pool).replace("{mention}", f"<@{user_id}>")
                        send_msg(c_id, line, token=self.token)
                        time.sleep(0.3)
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
                send_msg(c_id, "âœ… Drown stopped.", token=self.token)
                return

            # ========== PACK COMMANDS ==========
            if cmd_lower.startswith("hindi_pack "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1])
                for line in hindi_drown[:10]:
                    send_msg(c_id, line.replace("{mention}", f"<@{user_id}>"), token=self.token)
                    time.sleep(0.3)
                return

            if cmd_lower.startswith("hinglish_pack "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1])
                for line in hinglish_drown[:10]:
                    send_msg(c_id, line.replace("{mention}", f"<@{user_id}>"), token=self.token)
                    time.sleep(0.3)
                return

            if cmd_lower.startswith("punjabi_pack "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1])
                for line in punjabi_lines[:10]:
                    send_msg(c_id, line.replace("{mention}", f"<@{user_id}>"), token=self.token)
                    time.sleep(0.3)
                return

            if cmd_lower.startswith("urdu_pack "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1])
                for line in urdu_lines[:10]:
                    send_msg(c_id, line.replace("{mention}", f"<@{user_id}>"), token=self.token)
                    time.sleep(0.3)
                return

            if cmd_lower.startswith("mix_all_pack "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1])
                all_lines = hindi_drown + hinglish_drown + english_drown + punjabi_lines + urdu_lines
                random.shuffle(all_lines)
                for line in all_lines[:15]:
                    send_msg(c_id, line.replace("{mention}", f"<@{user_id}>"), token=self.token)
                    time.sleep(0.3)
                return

            if cmd_lower.startswith("god_pack "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1])
                all_lines = hindi_drown + hinglish_drown + english_drown + punjabi_lines + urdu_lines
                random.shuffle(all_lines)
                for line in all_lines[:20]:
                    send_msg(c_id, line.replace("{mention}", f"<@{user_id}>"), token=self.token)
                    time.sleep(0.3)
                return

            if cmd_lower.startswith("continuous_pack "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                user_id = extract_user_id_from_mention(parts[1])
                lang = parts[2] if len(parts) > 2 else "mix"
                banks = {"hindi": hindi_drown, "hinglish": hinglish_drown, "english": english_drown, "punjabi": punjabi_lines, "urdu": urdu_lines}
                pool = banks.get(lang, hindi_drown + hinglish_drown + english_drown + punjabi_lines + urdu_lines)
                multi_running[f"pack_{key_suffix}"] = True
                send_msg(c_id, f"âœ… Continuous pack started. Use $stoppack to stop.", token=self.token)
                def _pack():
                    while multi_running.get(f"pack_{key_suffix}", False):
                        line = random.choice(pool).replace("{mention}", f"<@{user_id}>")
                        send_msg(c_id, line, token=self.token)
                        time.sleep(0.3)
                threading.Thread(target=_pack, daemon=True).start()
                return

            if cmd_lower == "stoppack":
                multi_running[f"pack_{key_suffix}"] = False
                send_msg(c_id, "âœ… Continuous pack stopped.", token=self.token)
                return

            # ========== TROLL / FAKE COMMANDS ==========
            if cmd_lower.startswith("fake_ban "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "âŒ Usage: $fake_ban @user", token=self.token)
                    return
                user_id = extract_user_id_from_mention(parts[1])
                send_msg(c_id, f"ðŸ”¨ <@{user_id}> has been banned from the server.\n> Reason: `Disrespecting ð˜¼ð™¨ð™ð™ª`", token=self.token)
                return

            if cmd_lower.startswith("fake_mute "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "âŒ Usage: $fake_mute @user", token=self.token)
                    return
                user_id = extract_user_id_from_mention(parts[1])
                send_msg(c_id, f"ðŸ”‡ <@{user_id}> has been muted for 7 days.\n> Reason: `Disrespecting ð˜¼ð™¨ð™ð™ª`", token=self.token)
                return

            if cmd_lower.startswith("fake_kick "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "âŒ Usage: $fake_kick @user", token=self.token)
                    return
                user_id = extract_user_id_from_mention(parts[1])
                send_msg(c_id, f"ðŸ‘¢ <@{user_id}> has been kicked from the server.\n> Reason: `Ran by ð˜¼ð™¨ð™ð™ª ðŸ”¥`", token=self.token)
                return

            if cmd_lower.startswith("fake_warn "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "âŒ Usage: $fake_warn @user [reason]", token=self.token)
                    return
                user_id = extract_user_id_from_mention(parts[1])
                reason = " ".join(parts[2:]) if len(parts) > 2 else "Disrespecting ð˜¼ð™¨ð™ð™ª"
                send_msg(c_id, f"âš ï¸ <@{user_id}> has received a warning.\n> Reason: `{reason}`\n> Warned by: **ð˜¼ð™¨ð™ð™ª SELFBOT**", token=self.token)
                return

            if cmd_lower.startswith("rick_roll "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1]) if len(parts) > 1 else None
                mention = f"<@{user_id}>" if user_id else "@everyone"
                send_msg(c_id, f"{mention} ðŸŽ‰ **FREE NITRO CLAIM â€” FIRST 100 ONLY!**\nhttps://discord.gift/rickroll-ashu\n||https://www.youtube.com/watch?v=dQw4w9WgXcQ||", token=self.token)
                return

            if cmd_lower.startswith("crash_dm "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "âŒ Usage: $crash_dm @user", token=self.token)
                    return
                user_id = extract_user_id_from_mention(parts[1])
                bomb = ("\u200b" * 1990) + "ð˜¼ð™¨ð™ð™ª ðŸ”¥"
                send_msg(c_id, f"ðŸ’£ DM crash sent to <@{user_id}>", token=self.token)
                dm_url = f"https://discord.com/api/v9/users/@me/channels"
                dm_payload = {"recipient_id": user_id}
                dm_resp = requests.post(dm_url, headers={"Authorization": self.token, "Content-Type": "application/json"}, json=dm_payload)
                if dm_resp.status_code in [200, 201]:
                    dm_channel = dm_resp.json().get("id")
                    for _ in range(5):
                        send_msg(dm_channel, bomb, token=self.token)
                        time.sleep(0.3)
                return

            if cmd_lower.startswith("ip_logger "):
                parts = cmd_part.split()
                user_id = extract_user_id_from_mention(parts[1]) if len(parts) > 1 else None
                mention = f"<@{user_id}>" if user_id else "@everyone"
                fake_ip = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
                city = random.choice(['London','Mumbai','Karachi','Toronto','Sydney','Delhi','Lahore'])
                send_msg(c_id, f"{mention} yo click this https://grabify.link/ASHU\n||Logged IP: `{fake_ip}` â€” City: **{city}** lmaooo||", token=self.token)
                return

            if cmd_lower.startswith("countdown "):
                parts = cmd_part.split()
                count = int(parts[1]) if len(parts) > 1 else 10
                msg_text = " ".join(parts[2:]) if len(parts) > 2 else "ð˜¼ð™¨ð™ð™ª ON TOP ðŸ”¥"
                msg = send_msg(c_id, f"**{count}**", token=self.token)
                if msg:
                    for i in range(count - 1, 0, -1):
                        time.sleep(1)
                        send_msg(c_id, f"**{i}**", token=self.token)
                    time.sleep(1)
                    send_msg(c_id, f"ðŸ’¥ **{msg_text}**", token=self.token)
                return

            if cmd_lower.startswith("typing_spam "):
                parts = cmd_part.split()
                seconds = int(parts[1]) if len(parts) > 1 else 30
                send_msg(c_id, f"âŒ¨ï¸ Typing for {seconds}s...", token=self.token)
                end = time.time() + seconds
                while time.time() < end:
                    requests.post(f"https://discord.com/api/v9/channels/{c_id}/typing", headers={"Authorization": self.token})
                    time.sleep(5)
                return

            # ========== AUTO-REPLY (TARGET BASED) ==========
            if cmd_lower.startswith("autoreply "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "âŒ Usage: $autoreply @user", token=self.token)
                    return
                user_ids = []
                for mention in parts[1:]:
                    uid = extract_user_id_from_mention(mention)
                    if uid:
                        user_ids.append(uid)
                if not user_ids:
                    send_msg(c_id, "âŒ No valid user", token=self.token)
                    return
                if c_id not in AUTOREPLY_TARGETS:
                    AUTOREPLY_TARGETS[c_id] = []
                for uid in user_ids:
                    if uid not in AUTOREPLY_TARGETS[c_id]:
                        AUTOREPLY_TARGETS[c_id].append(uid)
                send_msg(c_id, f"âœ… Autoreply added: {len(user_ids)} users", token=self.token)
                return

            if cmd_lower.startswith("removeautoreply "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "âŒ Usage: $removeautoreply @user", token=self.token)
                    return
                mention = parts[1]
                uid = extract_user_id_from_mention(mention)
                if not uid:
                    send_msg(c_id, "âŒ Invalid user", token=self.token)
                    return
                if c_id in AUTOREPLY_TARGETS and uid in AUTOREPLY_TARGETS[c_id]:
                    AUTOREPLY_TARGETS[c_id].remove(uid)
                    if not AUTOREPLY_TARGETS[c_id]:
                        del AUTOREPLY_TARGETS[c_id]
                    send_msg(c_id, f"âœ… Removed {mention}", token=self.token)
                else:
                    send_msg(c_id, "â„¹ï¸ Not in autoreply", token=self.token)
                return

            if cmd_lower == "stopautoreply":
                if c_id in AUTOREPLY_TARGETS:
                    del AUTOREPLY_TARGETS[c_id]
                    send_msg(c_id, "âœ… Autoreply cleared", token=self.token)
                else:
                    send_msg(c_id, "â„¹ï¸ No autoreply", token=self.token)
                return

            # ========== AUTO-REPLY (JSON TRIGGER BASED) ==========
            if cmd_lower.startswith("addar "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "âŒ Usage: $addar trigger,response", token=self.token)
                    return
                trigger_response = " ".join(parts[1:])
                if ',' not in trigger_response:
                    send_msg(c_id, "âŒ Use comma: trigger,response", token=self.token)
                    return
                trigger, response = trigger_response.split(',', 1)
                trigger = trigger.strip()
                response = response.strip()
                auto_responses[trigger] = response
                save_autoreplies(auto_responses)
                send_msg(c_id, f"âœ… Auto-response added: `{trigger}` â†’ `{response}`", token=self.token)
                return

            if cmd_lower.startswith("removear "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "âŒ Usage: $removear <trigger>", token=self.token)
                    return
                trigger = " ".join(parts[1:])
                if trigger in auto_responses:
                    del auto_responses[trigger]
                    save_autoreplies(auto_responses)
                    send_msg(c_id, f"âœ… Removed: `{trigger}`", token=self.token)
                else:
                    send_msg(c_id, f"âŒ Not found: `{trigger}`", token=self.token)
                return

            if cmd_lower == "lister":
                if not auto_responses:
                    send_msg(c_id, "â„¹ï¸ No auto-responses configured.", token=self.token)
                    return
                lines = "\n".join([f"`{k}` â†’ `{v}`" for k, v in list(auto_responses.items())[:20]])
                send_msg(c_id, f"**ðŸ“‹ AUTO-RESPONSES:**\n{lines}", token=self.token)
                return

            # ========== AUTOREACT ==========
            if cmd_lower.startswith("autoreact "):
                parts = cmd_part.split()
                if len(parts) < 2:
                    send_msg(c_id, "âŒ Usage: $autoreact <emoji>", token=self.token)
                    return
                emoji = parts[1]
                AUTOREACT_EMOJIS[c_id] = emoji
                send_msg(c_id, f"âœ… Autoreact set: {emoji}", token=self.token)
                return

            if cmd_lower == "stopautoreact":
                if c_id in AUTOREACT_EMOJIS:
                    del AUTOREACT_EMOJIS[c_id]
                    send_msg(c_id, "âœ… Autoreact stopped", token=self.token)
                else:
                    send_msg(c_id, "â„¹ï¸ No autoreact", token=self.token)
                return

            # ========== GC COMMANDS ==========
            if cmd_lower.startswith("gcstart "):
                parts = cmd_part.split()
                interval = float(parts[1]) if len(parts) > 1 else 0.5
                names = load_gcnames()
                if not names:
                    send_msg(c_id, "âŒ gcname.txt is empty", token=self.token)
                    return
                send_msg(c_id, f"âœ… GC rename started with {len(names)} names. Use $gcstop to stop.", token=self.token)
                gc_running = True
                def _gc_rename():
                    i = 0
                    while gc_running:
                        try:
                            change_gc_name(c_id, names[i % len(names)], token=self.token)
                            i += 1
                            time.sleep(interval)
                        except:
                            time.sleep(2)
                threading.Thread(target=_gc_rename, daemon=True).start()
                if not hasattr(self, 'gc_running'):
                    self.gc_running = {}
                self.gc_running[c_id] = True
                return

            if cmd_lower == "gcstop":
                if hasattr(self, 'gc_running') and c_id in self.gc_running:
                    self.gc_running[c_id] = False
                    send_msg(c_id, "âœ… GC rename stopped.", token=self.token)
                else:
                    send_msg(c_id, "â„¹ï¸ No active GC rename", token=self.token)
                return

            # ========== MULTI COMMANDS (FIXED ASYNC & LIMITS) ==========
            if cmd_lower.startswith("multispam "):
                message_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "ð˜¼ð™¨ð™ð™ª On Top ðŸ”¥"
                tokens = load_tokens()
                multi_running["multispam"] = True
                send_msg(c_id, f"âœ… Endless Multispam started. Use $stopmulti to stop.", token=self.token)
                async def _spam(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        while multi_running.get("multispam", False):
                            try:
                                async with sess.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": message_text}) as r:
                                    if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 2))
                                await asyncio.sleep(0.1)
                            except: await asyncio.sleep(1)
                threading.Thread(target=run_async_tasks, args=([_spam(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multispamall "):
                message_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "ð˜¼ð™¨ð™ð™ª On Top ðŸ”¥"
                tokens = load_tokens()
                if not guild_id:
                    send_msg(c_id, "âŒ Run this in a server!", token=self.token)
                    return
                r = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers={"Authorization": self.token})
                if r.status_code == 200:
                    channels = [ch['id'] for ch in r.json() if ch['type'] == 0]
                    send_msg(c_id, f"âœ… Endless Multispamall across {len(channels)} channels. Use $stopmulti to stop.", token=self.token)
                    multi_running["multispamall"] = True
                    async def _spamall(tok):
                        headers = {"Authorization": tok, "Content-Type": "application/json"}
                        async with aiohttp.ClientSession() as sess:
                            while multi_running.get("multispamall", False):
                                for ch in channels:
                                    if not multi_running.get("multispamall", False): return
                                    try:
                                        async with sess.post(f"https://discord.com/api/v9/channels/{ch}/messages", headers=headers, json={"content": message_text}) as r:
                                            if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 2))
                                        await asyncio.sleep(0.15)
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
                send_msg(c_id, f"âœ… Endless Multi Long Spam started. Use $stopmulti to stop.", token=self.token)
                async def _longspam(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        while multi_running.get("multilongspam", False):
                            msg = get_long_spam(mention)
                            try:
                                async with sess.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": msg}) as r:
                                    if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 2))
                                await asyncio.sleep(0.5)
                            except: pass
                threading.Thread(target=run_async_tasks, args=([_longspam(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multiwordwall "):
                parts = cmd_part.split()
                word = " ".join(parts[1:]) if len(parts) > 1 else "ð˜¼ð™¨ð™ð™ª"
                tokens = load_tokens()
                wall = (word + " ") * (2000 // (len(word) + 1))
                multi_running["multiww"] = True
                send_msg(c_id, f"âœ… Endless Multi Wordwall started. Use $stopmulti to stop.", token=self.token)
                async def _wall(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        while multi_running.get("multiww", False):
                            try:
                                async with sess.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": wall[:2000]}) as r:
                                    if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 2))
                                await asyncio.sleep(0.5)
                            except: pass
                threading.Thread(target=run_async_tasks, args=([_wall(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multizalgo "):
                parts = cmd_part.split()
                text = " ".join(parts[1:]) if len(parts) > 1 else "ð˜¼ð™¨ð™ð™ª On Top"
                tokens = load_tokens()
                multi_running["multizalgo"] = True
                send_msg(c_id, f"âœ… Endless Multi Zalgo started. Use $stopmulti to stop.", token=self.token)
                async def _zalgo(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        while multi_running.get("multizalgo", False):
                            try:
                                async with sess.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": zalgo_text(text)}) as r:
                                    if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 2))
                                await asyncio.sleep(0.5)
                            except: pass
                threading.Thread(target=run_async_tasks, args=([_zalgo(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multieveryone"):
                tokens = load_tokens()
                multi_running["multieveryone"] = True
                send_msg(c_id, f"âœ… Endless Multi @everyone started. Use $stopmulti to stop.", token=self.token)
                async def _everyone(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        while multi_running.get("multieveryone", False):
                            try:
                                async with sess.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": "@everyone ð˜¼ð™¨ð™ð™ª On Top ðŸ”¥"}) as r:
                                    if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 2))
                                await asyncio.sleep(0.4)
                            except: pass
                threading.Thread(target=run_async_tasks, args=([_everyone(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multinuke "):
                message_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "ð˜¼ð™¨ð™ð™ª On Top ðŸ”¥"
                tokens = load_tokens()
                if not guild_id:
                    send_msg(c_id, "âŒ Run this in a server!", token=self.token)
                    return
                r = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers={"Authorization": self.token})
                if r.status_code == 200:
                    channels = [ch['id'] for ch in r.json() if ch['type'] == 0]
                    send_msg(c_id, f"âœ… ENDLESS MULTINUKE STARTED! Use $stopmulti to stop.", token=self.token)
                    multi_running["multinuke"] = True
                    async def _nuke(tok):
                        headers = {"Authorization": tok, "Content-Type": "application/json"}
                        async with aiohttp.ClientSession() as sess:
                            while multi_running.get("multinuke", False):
                                for ch in channels:
                                    if not multi_running.get("multinuke", False): return
                                    try:
                                        async with sess.post(f"https://discord.com/api/v9/channels/{ch}/messages", headers=headers, json={"content": f"@everyone {message_text}"}) as r:
                                            if r.status == 429: await asyncio.sleep((await r.json()).get("retry_after", 2))
                                        await asyncio.sleep(0.1)
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
                send_msg(c_id, f"âœ… {len(tokens)} tokens DMing {user_id}...", token=self.token)

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
                message_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "ð˜¼ð™¨ð™ð™ª On Top ðŸ”¥"
                tokens = load_tokens()
                if not guild_id:
                    send_msg(c_id, "âŒ Run this in a server!", token=self.token)
                    return
                r = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/members?limit=1000", headers={"Authorization": self.token})
                if r.status_code == 200:
                    members = [m['user']['id'] for m in r.json() if not m.get('user', {}).get('bot', False)]
                    send_msg(c_id, f"âœ… Mass DMing {len(members)} members... (Background Process)", token=self.token)
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
                                    await asyncio.sleep(1.2)
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
                send_msg(c_id, f"âœ… {len(tokens)} tokens sending friend request to {user_id}...", token=self.token)
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
                send_msg(c_id, f"âœ… {len(tokens)} tokens blocking {user_id}...", token=self.token)
                async def _block(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        await sess.put(f"https://discord.com/api/v9/users/@me/relationships/{user_id}", headers=headers, json={"type": 2})
                threading.Thread(target=run_async_tasks, args=([_block(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower == "multi_accept_friends":
                tokens = load_tokens()
                send_msg(c_id, f"âœ… {len(tokens)} tokens accepting friend requests...", token=self.token)
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
                send_msg(c_id, f"âœ… {len(tokens)} tokens removing friends...", token=self.token)
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
                send_msg(c_id, f"âœ… {len(tokens)} tokens joining {invite}...", token=self.token)
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
                send_msg(c_id, f"âœ… {len(tokens)} tokens leaving {guild_id}...", token=self.token)
                async def _leave(tok):
                    headers = {"Authorization": tok}
                    async with aiohttp.ClientSession() as sess:
                        await sess.delete(f"https://discord.com/api/v9/users/@me/guilds/{guild_id}", headers=headers)
                threading.Thread(target=run_async_tasks, args=([_leave(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower == "multi_leaveall":
                tokens = load_tokens()
                send_msg(c_id, f"âœ… {len(tokens)} tokens leaving ALL servers...", token=self.token)
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
                nickname = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "ð˜¼ð™¨ð™ð™ª"
                tokens = load_tokens()
                if not guild_id:
                    send_msg(c_id, "âŒ Run this in a server!", token=self.token)
                    return
                send_msg(c_id, f"âœ… {len(tokens)} tokens setting nick '{nickname}'...", token=self.token)
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
                send_msg(c_id, f"âœ… {len(tokens)} tokens setting avatar...", token=self.token)
                async def _avatar(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        await sess.patch("https://discord.com/api/v9/users/@me", headers=headers, json={"avatar": data_uri})
                threading.Thread(target=run_async_tasks, args=([_avatar(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multi_set_username "):
                username = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "ð˜¼ð™¨ð™ð™ª"
                tokens = load_tokens()
                send_msg(c_id, f"âœ… {len(tokens)} tokens setting username...", token=self.token)
                async def _rename(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        await sess.patch("https://discord.com/api/v9/users/@me", headers=headers, json={"username": username})
                threading.Thread(target=run_async_tasks, args=([_rename(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multi_status_set "):
                status_text = " ".join(cmd_part.split()[1:]) if len(cmd_part.split()) > 1 else "ð˜¼ð™¨ð™ð™ª On Top ðŸ”¥"
                tokens = load_tokens()
                send_msg(c_id, f"âœ… {len(tokens)} tokens setting status...", token=self.token)
                async def _status(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    payload = {"custom_status": {"text": status_text, "emoji_name": "ðŸ”¥"}}
                    async with aiohttp.ClientSession() as sess:
                        await sess.patch("https://discord.com/api/v9/users/@me/settings", headers=headers, json=payload)
                threading.Thread(target=run_async_tasks, args=([_status(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multi_delete_msgs "):
                parts = cmd_part.split()
                limit = int(parts[1]) if len(parts) > 1 else 10
                tokens = load_tokens()
                send_msg(c_id, f"âœ… {len(tokens)} tokens deleting last {limit} messages...", token=self.token)
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
                send_msg(c_id, f"âœ… {len(tokens)} tokens reacting...", token=self.token)
                async def _react(tok):
                    headers = {"Authorization": tok}
                    async with aiohttp.ClientSession() as sess:
                        await sess.put(f"https://discord.com/api/v9/channels/{c_id}/messages/{msg_id}/reactions/{encoded}/@me", headers=headers)
                threading.Thread(target=run_async_tasks, args=([_react(t) for t in tokens],), daemon=True).start()
                return

            if cmd_lower.startswith("multi_reactall "):
                parts = cmd_part.split()
                emoji = parts[1] if len(parts) > 1 else "ðŸ”¥"
                limit = int(parts[2]) if len(parts) > 2 else 10
                tokens = load_tokens()
                encoded = urllib.parse.quote(emoji)
                send_msg(c_id, f"âœ… {len(tokens)} tokens reacting to last {limit} messages...", token=self.token)
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
                send_msg(c_id, f"âœ… {len(tokens)} tokens ghost pinging...", token=self.token)
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
                send_msg(c_id, f"âœ… Endless Multi Pack/Drown started. Use $stopmulti to stop.", token=self.token)
                async def _multipd(tok):
                    headers = {"Authorization": tok, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as sess:
                        while multi_running.get("multipack_drown", False):
                            line = random.choice(pool).replace("{mention}", f"<@{user_id}>")
                            await sess.post(f"https://discord.com/api/v9/channels/{c_id}/messages", headers=headers, json={"content": line})
                            await asyncio.sleep(0.5)
                threading.Thread(target=run_async_tasks, args=([_multipd(t) for t in tokens],), daemon=True).start()
                return

            # ========== MULTI TYPING ==========
            if cmd_lower.startswith("multi_typing "):
                parts = cmd_part.split()
                seconds = int(parts[1]) if len(parts) > 1 else 30
                tokens = load_tokens()
                send_msg(c_id, f"âœ… {len(tokens)} tokens typing for {seconds}s...", token=self.token)
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
                send_msg(c_id, "âœ… All endless multi commands stopped.", token=self.token)
                return

            # ========== PING / STATUS ==========
            if cmd_lower == "ping":
                start = time.time()
                requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": self.token})
                latency = round((time.time() - start) * 1000, 2)
                send_msg(c_id, f"ðŸ“ Pong! {latency}ms", token=self.token)
                return

            if cmd_lower == "status":
                uptime = round(time.time() - START_TIME, 1)
                status_msg = (
                    f"**ð˜¼ð™¨ð™ð™ª SELFBOT STATUS**\n"
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
                    send_msg(c_id, f"âœ… {mention} granted access", token=self.token)
                return

            if cmd_lower.startswith("removeaccess "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                mention = parts[1]
                user_id = extract_user_id_from_mention(mention)
                if user_id in SUDO_USERS:
                    SUDO_USERS.remove(user_id)
                    save_sudo(SUDO_USERS)
                    send_msg(c_id, f"âœ… {mention} removed", token=self.token)
                return

            # ========== RESTART / PREFIX ==========
            if cmd_lower == "restart":
                send_msg(c_id, "ðŸ”„ Restarting...", token=self.token)
                os.execl(sys.executable, sys.executable, *sys.argv)
                return

            if cmd_lower.startswith("prefix "):
                parts = cmd_part.split()
                if len(parts) < 2: return
                PREFIX = parts[1]
                send_msg(c_id, f"âœ… Prefix changed to `{PREFIX}`", token=self.token)
                return

    def run(self):
        while self.running:
            try:
                self.ws = websocket.WebSocketApp("wss://gateway.discord.gg/?v=9&encoding=json", on_message=self.on_message)
                self.ws.run_forever()
            except Exception as e:
                logging.error(f"Bot {self.bot_index + 1} error: {e}")
                time.sleep(5)

# ==================== LAUNCH ====================
def run_all_bots():
    print("=" * 55)
    print("      ð˜¼ð™¨ð™ð™ª SELFBOT â€” ULTIMATE EDITION (LIMITLESS)")
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
            print(f"âœ… Bot {i+1} verified (ID: {user_id})")
            valid_tokens.append(token)
        else:
            print(f"âŒ Bot {i+1} - INVALID TOKEN!")

    if not valid_tokens:
        print("No valid tokens. Exiting...")
        return

    print(f"\nâœ… {len(valid_tokens)} valid tokens! ALL LIMITS REMOVED âš¡")
    print(f"âš¡ SPAM_DELAY: {SPAM_DELAY}s")
    print(f"âš¡ PARALLEL_SPAM: {PARALLEL_SPAM}")
    print(f"âš¡ PARALLEL_NC: {PARALLEL_NC}\n")

    bots = []
    for i, token in enumerate(valid_tokens):
        bot = DiscordSelfBot(token, i)
        thread = threading.Thread(target=bot.run, daemon=True)
        thread.start()
        bots.append(bot)
        time.sleep(1)

    print("âœ… All bots running!")
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
