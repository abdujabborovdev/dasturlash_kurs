from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from states.check import *
from aiogram.types import InputMediaPhoto, FSInputFile
from data.config import *
from keyboards.inline.kurs import *

from database import async_session, Users
from sqlalchemy import select

router = Router()
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@router.callback_query(F.data == "tolov_qildim")
async def tolov_frontend(call: CallbackQuery, state: FSMContext):
    await call.answer()
    rasm = FSInputFile("handlers/users/img_1.png")
    await state.set_state(Check.chek)


    bosh_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Bosh menu", callback_data="bosh_menu", icon_custom_emoji_id='5255703720078879038')]
    ])
    await call.message.edit_media(
        media=InputMediaPhoto(
            media=rasm,
            caption="<b>Tolov haqida chekingizni<tg-emoji emoji-id='5208575215738573162'>🧾</tg-emoji>\n"
                    "Rasm yokida pdf Formatda yuboring<tg-emoji emoji-id='5470177992950946662'>👇</tg-emoji></b>",
            parse_mode=ParseMode.HTML
        ),
        reply_markup=bosh_menu
    )

@router.message((F.photo | F.document), Check.chek)
async def tolov_frontend(message: Message, state: FSMContext):
    user_data = await state.get_data()
    kurs_nomi = user_data.get("kurs_nomi", "Noma'lum")
    await state.update_data(chek=message.photo)
    if message.photo:
        file_id = message.photo[-1].file_id
        is_photo = True
    else:
        file_id = message.document.file_id
        is_photo = False

    user_id = message.from_user.id
    full_name = message.from_user.full_name

    # 🔄 YANGILANISH: Foydalanuvchi chek yuborgan zahoti bazadagi statusni 'pending' holatiga qaytaramiz
    async with async_session() as session:
        result = await session.execute(select(Users).where(Users.telegram_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.status = "pending"
            await session.commit()

    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"accept_{user_id}_{kurs_nomi}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"reject_{user_id}_{kurs_nomi}")
        ]
    ])

    caption_text = (
        f"🔔 <b>Yangi to'lov cheki keldi!</b>\n\n"
        f"📚 <b>Kurs:</b> {kurs_nomi}\n"  # Adminga qaysi kursligi chiqadi
        f"👤 Foydalanuvchi: {full_name}\n"
        f"🆔 ID: {user_id}"
    )

    for admin_id in ADMINS:
        try:
            if is_photo:
                await message.bot.send_photo(chat_id=admin_id, photo=file_id, caption=caption_text,
                                             reply_markup=admin_keyboard, parse_mode="HTML")
            else:
                await message.bot.send_document(chat_id=admin_id, document=file_id, caption=caption_text,
                                                reply_markup=admin_keyboard, parse_mode="HTML")
        except Exception as e:
            print(f"Adminga ({admin_id}) yuborishda xatolik yuz berdi: {e}")

    await state.clear()
    await message.answer(
        "Rahmat! Chekingiz adminga yuborildi. Tekshiruvdan so'ng sizga VIP kanal havolasi yuboriladi. ⏳")


import os
from database import async_session, Users, Payments


@router.callback_query(F.data.startswith("accept_"))
async def accept_payment(call: CallbackQuery):
    # 1. Callback datani ajratib olish
    data_parts = call.data.split("_")
    user_id = int(data_parts[1])
    kurs_turi_raw = data_parts[2] if len(data_parts) > 2 else "Frontend"

    # 2. .env dan IDlarni va kurs narxini aniqlash
    # Eslatma: .env faylingizda kalitlar aynan shunday nomlangan bo'lishi kerak
    backend_id = os.getenv("VIP_BACKEND_ID")
    frontend_id = os.getenv("VIP_KANAL_ID")

    if "Backend" in kurs_turi_raw:
        target_channel_id = backend_id
        kurs_turi = "Backend"
        narx = 54900
    else:
        target_channel_id = frontend_id
        kurs_turi = "Frontend"
        narx = 74900

    # 3. Bazaga yozish (Users statusini yangilash va Payments ga qo'shish)
    try:
        async with async_session() as session:
            # Statusni yangilash
            result = await session.execute(select(Users).where(Users.telegram_id == user_id))
            user = result.scalar_one_or_none()
            if user:
                user.status = "approved"

            # To'lovni bazaga qo'shish (Statistika uchun)
            new_payment = Payments(
                telegram_id=user_id,
                course_name=kurs_turi,
                amount=narx,
                channel_id=str(target_channel_id)
            )
            session.add(new_payment)
            await session.commit()
    except Exception as e:
        await call.answer(f"Bazaga yozishda xatolik: {str(e)}", show_alert=True)
        return

    # 4. Kanalga 1 martalik havola yaratish va yuborish
    if not target_channel_id:
        await call.answer(f"❌ Xatolik: {kurs_turi} kanal ID si topilmadi!", show_alert=True)
        return

    try:
        invite_link = await call.bot.create_chat_invite_link(
            chat_id=int(target_channel_id),
            member_limit=1,
            name=f"User {user_id} uchun {kurs_turi} maxsus"
        )

        await call.bot.send_message(
            chat_id=user_id,
            text=f"🎉 <b>To'lovingiz tasdiqlandi!</b>\n\nQuyidagi havola orqali <b>{kurs_turi} VIP</b> kanaliga a'zo bo'ling. Havola faqat <b>1 marta</b> kirish uchun amal qiladi:\n\n{invite_link.invite_link}",
            parse_mode="HTML"
        )

        # Admin panelidagi xabarni yangilash
        await call.message.edit_caption(
            caption=call.message.caption + f"\n\n🟢 <b>{call.from_user.full_name} tomonidan tasdiqlandi, {kurs_turi} havolasi yuborildi!</b>",
            reply_markup=None
        )
        await call.answer(f"To'lov tasdiqlandi va {kurs_turi} havolasi yuborildi!", show_alert=True)

    except Exception as e:
        await call.answer(f"Xatolik yuz berdi: {str(e)}", show_alert=True)

@router.callback_query(F.data.startswith("reject_"))
async def reject_payment(call: CallbackQuery):
    # 🎯 YANGILANISH: Rad etish tugmasi uchun ham ma'lumotlarni moslashtiramiz
    data_parts = call.data.split("_")
    user_id = int(data_parts[1])
    kurs_turi = data_parts[2] if len(data_parts) > 2 else "Frontend"

    async with async_session() as session:
        result = await session.execute(select(Users).where(Users.telegram_id == user_id))
        user = result.scalar_one_or_none()

        if user:
            if user.status != "pending":
                await call.answer("❌ Bu chekka oldin javob berilgan!", show_alert=True)
                await call.message.edit_reply_markup(reply_markup=None)
                return

            user.status = "rejected"
            await session.commit()

    try:
        await call.bot.send_message(
            chat_id=user_id,
            text="❌ <b>Siz yuborgan to'lov cheki tasdiqlanmadi.</b>\n\nAgar adashgan bo'lsangiz, qaytadan to'g'ri chekni yuborishga urinib ko'ring yoki adminga murojaat qiling.",
            parse_mode="HTML"
        )

        await call.message.edit_caption(
            caption=call.message.caption + f"\n\n🔴 <b>{call.from_user.full_name} tomonidan {kurs_turi} kursi to'lovi rad etildi!</b>",
            reply_markup=None
        )
        await call.answer("To'lov bekor qilindi!", show_alert=True)

    except Exception as e:
        await call.answer(f"Xatolik: {str(e)}", show_alert=True)


@router.callback_query(F.data == 'bosh_menu')
async def bosh_menu(call: CallbackQuery):
    await call.answer()

    photo = FSInputFile("handlers/users/img_4.png")

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=f"Salom, <b>{call.from_user.full_name}</b> <tg-emoji emoji-id='5472055112702629499'>👋</tg-emoji>\n\n"
                    f"<blockquote expandable><i>Mukamal <tg-emoji emoji-id='5190498849440931467'>🥷</tg-emoji> Dasturlash botiga hush kelibsiz</i>\n\n"
                    f"Ozingizga keraklik darslikni golga kiritish uchun quydagi tugmani bosing <tg-emoji emoji-id='5470177992950946662'>👇</tg-emoji></bzlockquote>",
            parse_mode=ParseMode.HTML
        ),
        reply_markup=kurs
    )