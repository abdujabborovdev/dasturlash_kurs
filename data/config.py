import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# .env faylni yuklaymiz
load_dotenv(ENV_PATH, override=True)

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip().strip('"').strip("'")

# Adminlar ro'yxatini int tipida listga o'giramiz
ADMINS = [int(admin.strip()) for admin in (os.getenv("ADMINS") or "").split(",") if admin.strip()]

DATABASE_URL = (os.getenv("DATABASE_URL") or "").strip().strip('"').strip("'")

# VIP_KANAL_ID ni shu yerda .env dan o'qib, int ga o'giramiz (handlersdan import qilmaymiz!)
VIP_KANAL_ID = int((os.getenv("VIP_KANAL_ID") or "0").strip().strip('"').strip("'"))

VIP_BACKEND_ID = os.getenv("VIP_BACKEND_ID") or ""

IP = os.getenv("ip", "localhost")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida topilmadi")