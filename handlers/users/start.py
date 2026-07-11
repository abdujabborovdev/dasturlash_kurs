from aiogram import Router,F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select
from keyboards.inline.nomer import nomer
from states.nomer import *
from keyboards.inline.kurs import *
router = Router()
from database import *
from aiogram.types import Message, ReplyKeyboardRemove,FSInputFile


@router.message(CommandStart())
async def bot_start(message: Message,state: FSMContext):
    async with async_session() as session:
        statement = select(Users).where(Users.telegram_id == message.from_user.id)
        user = await session.scalar(statement)
        if user is None:
            await state.set_state(Nomer.nomer)
            photo_file = FSInputFile("handlers/users/img_3.png")
            sent_msg = await message.answer_photo(
                photo=photo_file,
                caption="<i>Royhatdan otish uchun telefon raqamingizni\n</i> <blockquote><b><tg-emoji emoji-id='5406809207947142040'>📲</tg-emoji>Yuborish</b></blockquote>\n<i>\n<b>Tugmasi orqali yuboring</b></i>",
                parse_mode=ParseMode.HTML,
                reply_markup=nomer
            )
            await state.update_data(bot_msg_id=sent_msg.message_id)
        else:
            await state.clear()
            await message.answer_photo(
                photo=FSInputFile("handlers/users/img_4.png"),
                caption=f"""Salom, <b>{message.from_user.full_name} <tg-emoji emoji-id="5472055112702629499">👋</tg-emoji></b>

<blockquote expandable><i>Mukamal <tg-emoji emoji-id="5190498849440931467">👨‍💻</tg-emoji> Dasturlash botiga hush kelibsiz

Ozingizga keraklik darslikni qolga kiritish uchun quydagi tugmani bosing <tg-emoji emoji-id="5470177992950946662">👇</tg-emoji></i></blockquote>""",parse_mode=ParseMode.HTML,reply_markup=kurs)


@router.message(Nomer.nomer, F.contact)
async def get_contact(message: Message, state: FSMContext):
    async with async_session() as session:
        phone_number = message.contact.phone_number

        if not phone_number.startswith('+'):
            phone_number = f"+{phone_number}"

        # State xotirasidan bot yuborgan xabar ID sini olamiz
        data = await state.get_data()
        bot_msg_id = data.get("bot_msg_id")

        # 1. Bot yuborgan "Ro'yxatdan o'tish..." xabarini o'chiramiz
        if bot_msg_id:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=bot_msg_id)
            except Exception:
                pass

        # 2. Foydalanuvchi yuborgan kontakt xabarining o'zini o'chiramiz
        try:
            await message.delete()
        except Exception:
            pass

        # Bazaga saqlash jarayoni
        new_user = Users(
            nomer=phone_number,
            name=message.from_user.full_name,
            telegram_id=message.from_user.id,
            user_name=message.from_user.username
        )
        session.add(new_user)
        await session.commit()

        # Statelarni butunlay tozalaymiz
        await state.clear()
        remove_msg = await message.answer("🔄", reply_markup=ReplyKeyboardRemove())


        try:
            await remove_msg.delete()
        except Exception:
            pass

        # Faqatgina Kurslarni (Frontend / Backend) chiqarib beramiz
        await message.answer_photo(
            photo=FSInputFile("handlers/users/img_4.png"),
            caption=f"Salom, <b>{message.from_user.full_name} <tg-emoji emoji-id='5472055112702629499'>👋</tg-emoji></b>\n    \n<blockquote expandable><i>Mukamal <tg-emoji emoji-id='5190498849440931467'>👨‍💻</tg-emoji> Dasturlash botiga hush kelibsiz\n    \nOzingizga keraklik darslikni qolga kiritish uchun quydagi tugmani bosing <tg-emoji emoji-id='5470177992950946662'>👇</tg-emoji></i></blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=kurs
        )