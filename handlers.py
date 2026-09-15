import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from database import get_db, Point
from keyboards import get_categories_kb, get_districts_kb, get_point_actions_kb, get_admin_approval_kb

router = Router()
ADMIN_ID = int(os.getenv("ADMIN_ID"))

class SuggestState(StatesGroup):
    name = State()
    address = State()
    rules = State()
    photo = State()

# --- Основной поток ---
@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "Привет! 👋 Я помогу найти, куда отдать вещи за 10 секунд.\n\n"
        "Выберите категорию вещей:",
        reply_markup=get_categories_kb()
    )

@router.callback_query(F.data.startswith("cat_"))
async def process_category(call: CallbackQuery):
    category = call.data.split("_")[1]
    await call.message.edit_text(
        "Отлично! Теперь выберите ваш район:",
        reply_markup=get_districts_kb(category)
    )

@router.callback_query(F.data.startswith("dist_"))
async def process_district(call: CallbackQuery):
    _, district, category = call.data.split("_")
    
    # Запрос к БД
    async for session in get_db():
        stmt = select(Point).where(
            Point.category == category,
            Point.district == district,
            Point.is_active == True
        )
        result = await session.execute(stmt)
        points = result.scalars().all()
        
        if not points:
            await call.message.edit_text(
                f"😕 В районе «{district}» пока нет проверенных точек для этой категории.\n\n"
                "Но вы можете стать первым, кто предложит точку!",
                reply_markup=get_point_actions_kb("", 0)
            )
            return

        # Показываем первую найденную точку (для MVP)
        point = points[0]
        text = (
            f"📍 *{point.name}*\n\n"
            f"🏠 *Адрес:* {point.address}\n"
            f"🕒 *Часы:* {point.hours or 'Уточняйте на месте'}\n"
            f"⚠️ *Важно:* {point.rules or 'Стандартные правила приёма'}\n\n"
            f"✅ Точка проверена нашей командой."
        )
        await call.message.edit_text(
            text, 
            parse_mode="Markdown",
            reply_markup=get_point_actions_kb(point.address, point.id)
        )

@router.callback_query(F.data == "start_over")
async def restart(call: CallbackQuery):
    await call.message.edit_text("Выберите категорию вещей:", reply_markup=get_categories_kb())

# --- Поток предложения новой точки (FSM) ---
@router.callback_query(F.data == "suggest_new")
async def start_suggest(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("💡 Отличная инициатива! Как называется эта точка/фонд?")
    await state.set_state(SuggestState.name)

@router.message(SuggestState.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📍 Напишите точный адрес (улица, дом):")
    await state.set_state(SuggestState.address)

@router.message(SuggestState.address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("📝 Есть ли особые правила? (например, 'только чистое', 'пн-пт 10-18'). Если нет, напишите 'нет'.")
    await state.set_state(SuggestState.rules)

@router.message(SuggestState.rules)
async def process_rules(message: Message, state: FSMContext):
    await state.update_data(rules=message.text)
    await message.answer("📸 Пришлите фото точки или входа в неё (или напишите 'пропустить', чтобы отправить без фото).")
    await state.set_state(SuggestState.photo)

@router.message(SuggestState.photo)
async def process_photo(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    
    # Формируем сообщение для админа
    admin_text = (
        f"🆕 *Новая точка от пользователя!* \n"
        f"👤 ID: {message.from_user.id}\n"
        f"📌 Название: {data['name']}\n"
        f"📍 Адрес: {data['address']}\n"
        f"📝 Правила: {data['rules']}"
    )
    
    if message.photo:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=admin_text,
            parse_mode="Markdown",
            reply_markup=get_admin_approval_kb(0) # В MVP ID=0, в проде нужно сохранять в БД и получать реальный ID
        )
    else:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="Markdown",
            reply_markup=get_admin_approval_kb(0)
        )
    
    await message.answer("🎉 Спасибо! Ваша заявка отправлена администратору на проверку. Мы обновим базу в течение 24 часов.")
    await state.clear()
    await message.answer("Вернуться в главное меню:", reply_markup=get_categories_kb())