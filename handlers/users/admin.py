import asyncio
from datetime import date
from sqlalchemy import select, func
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode

# O'zingizning database faylingizdan import qilasiz (yo'lini tekshirib oling)
from database import async_session, Users, Payments

router = Router()

# =====================================================================
# KEYBOARDLAR VA STATUSLAER
# =====================================================================
admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Moliyaviy Statistika", callback_data="admin_stats")],
    [InlineKeyboardButton(text="🚫 Foydalanuvchini Kanaldan Haydash", callback_data="admin_kick_user")],
    [InlineKeyboardButton(text="📢 Hammaga Xabar Yuborish", callback_data="admin_broadcast")]
])

back_to_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Admin Panelga qaytish", callback_data="back_to_admin")]
])


class AdminStates(StatesGroup):
    wait_user_id = State()
    wait_broadcast_msg = State()


# =====================================================================
# HANDLERLAR
# =====================================================================

@router.message(F.text == "/admin")
async def open_admin_panel(message: Message):
    await message.answer("🛠 <b>Admin panelga xush kelibsiz!</b>\nKerakli bo'limni tanlang:", reply_markup=admin_menu,
                         parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "back_to_admin")
async def back_admin(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    await call.message.edit_text("🛠 <b>Admin panelga xush kelibsiz!</b>\nKerakli bo'limni tanlang:",
                                 reply_markup=admin_menu, parse_mode=ParseMode.HTML)


# 1. MOLIYAVIY STATISTIKA (SQLAlchemy yordamida)
# 1. STATISTIKA (Foydalanuvchilar soni bilan birga)
@router.callback_query(F.data == "admin_stats")
async def show_statistics(call: CallbackQuery):
    from datetime import date
    async with async_session() as session:
        today = date.today()

        # 1. Jami foydalanuvchilar soni
        user_count_res = await session.execute(select(func.count(Users.id)))
        total_users = user_count_res.scalar() or 0

        # 2. Moliyaviy statistika
        daily = await session.execute(select(func.sum(Payments.amount)).where(Payments.created_at == today))
        backend_res = await session.execute(select(func.sum(Payments.amount)).where(Payments.course_name == 'backend'))
        frontend_res = await session.execute(
            select(func.sum(Payments.amount)).where(Payments.course_name == 'frontend'))

        daily_sum = daily.scalar() or 0
        back_sum = backend_res.scalar() or 0
        front_sum = frontend_res.scalar() or 0

    text = (
        "<b>📊 Umumiy Statistika:</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {total_users} ta\n\n"
        "💰 <b>Moliyaviy Tushumlar:</b>\n"
        f"📅 Kunlik tushum: {daily_sum:,} so'm\n"
        f"🐍 Python Backend: {back_sum:,} so'm\n"
        f"💻 Frontend darslik: {front_sum:,} so'm"
    )
    await call.message.edit_text(text, reply_markup=back_to_admin, parse_mode=ParseMode.HTML)

# 2. USERNI ID ORQALI KANAL DAN CHIQQARISH (KICK)
@router.callback_query(F.data == "admin_kick_user")
async def start_kick(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(
        "👤 Kanaldan chiqarmoqchi bo'lgan foydalanuvchining <b>Telegram ID</b> raqamini kiriting:",
        parse_mode=ParseMode.HTML, reply_markup=back_to_admin)
    await state.set_state(AdminStates.wait_user_id)


@router.message(AdminStates.wait_user_id)
async def process_kick_user(message: Message, state: FSMContext):
    user_id_input = message.text.strip()

    if not user_id_input.isdigit():
        await message.answer("⚠️ Xato! Faqat raqamlardan iborat Telegram ID kiriting:")
        return

    target_user_id = int(user_id_input)

    async with async_session() as session:
        # Oxirgi sotib olgan kursi va kanalini tekshiramiz
        stmt = select(Payments).where(Payments.telegram_id == target_user_id).order_by(Payments.id.desc()).limit(1)
        res = await session.execute(stmt)
        payment_data = res.scalar_one_or_none()

        if not payment_data:
            await message.answer("🔍 Bu ID bo'yicha to'lov qilgan foydalanuvchi bazadan topilmadi.",
                                 reply_markup=back_to_admin)
            await state.clear()
            return

        channel_id = payment_data.channel_id
        course_name = payment_data.course_name

        try:
            # Telegram kanaldan kick qilish va bandan yechish
            await message.bot.ban_chat_member(chat_id=int(channel_id), user_id=target_user_id)
            await message.bot.unban_chat_member(chat_id=int(channel_id), user_id=target_user_id)

            # Bazadan ushbu to'lov ruxsatini o'chiramiz
            await session.delete(payment_data)
            await session.commit()

            await message.answer(
                f"✅ Foydalanuvchi (ID: {target_user_id}) <b>{course_name.upper()}</b> kursi kanalidan muvaffaqiyatli chiqarildi!",
                parse_mode=ParseMode.HTML, reply_markup=back_to_admin)
            await state.clear()
        except Exception as e:
            await message.answer(f"❌ Xatolik yuz berdi: {e}\nBot kanalda admin ekanligini tekshiring.",
                                 reply_markup=back_to_admin)
            await state.clear()


# 3. BOT ORQALI HAMMAGA XABAR YUBORISH (BROADCAST)
@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text("📝 Hammaga yuborilishi kerak bo'lgan xabarni kiriting:", reply_markup=back_to_admin)
    await state.set_state(AdminStates.wait_broadcast_msg)


@router.message(AdminStates.wait_broadcast_msg)
async def send_broadcast(message: Message, state: FSMContext):
    async with async_session() as session:
        # Barcha foydalanuvchilarning telegram_id'larini olamiz
        stmt = select(Users.telegram_id)
        res = await session.execute(stmt)
        all_users = res.scalars().all()

    if not all_users:
        await message.answer("⚠️ Bazada foydalanuvchilar mavjud emas.", reply_markup=back_to_admin)
        await state.clear()
        return

    status_message = await message.answer("⏳ Xabar barcha foydalanuvchilarga yuborilmoqda...")
    success_count = 0

    for u_id in all_users:
        try:
            await message.copy_to(chat_id=u_id)
            success_count += 1
            await asyncio.sleep(0.05)  # Flood limit uchun
        except Exception:
            pass

    await status_message.delete()
    await message.answer(
        f"📢 Xabar tarqatish yakunlandi!\n✅ <b>{success_count}</b> ta foydalanuvchiga muvaffaqiyatli yetkazildi.",
        parse_mode=ParseMode.HTML, reply_markup=back_to_admin)
    await state.clear()

