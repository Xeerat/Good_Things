from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_categories_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👕 Одежда", callback_data="cat_clothes"))
    builder.row(InlineKeyboardButton(text="📚 Книги", callback_data="cat_books"))
    builder.row(InlineKeyboardButton(text="💻 Техника", callback_data="cat_tech"))
    builder.row(InlineKeyboardButton(text="🍲 Еда", callback_data="cat_food"))
    return builder.as_markup()

def get_districts_kb(category: str) -> InlineKeyboardMarkup:
    # В MVP список районов захардкожен. В будущем можно тянуть из БД: SELECT DISTINCT district FROM points
    districts = ["Центр", "Северный", "Южный", "Западный", "Восточный"]
    builder = InlineKeyboardBuilder()
    for d in districts:
        builder.row(InlineKeyboardButton(text=d, callback_data=f"dist_{d}_{category}"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="start_over"))
    return builder.as_markup()

def get_point_actions_kb(address: str, point_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Универсальная ссылка, которая откроет приложение карт на телефоне или браузер на ПК
    import urllib.parse
    encoded_addr = urllib.parse.quote(address)
    builder.row(InlineKeyboardButton(text="📍 Открыть в Яндекс.Картах", url=f"https://yandex.ru/maps/?text={encoded_addr}"))
    builder.row(InlineKeyboardButton(text="💡 Предложить новую точку", callback_data="suggest_new"))
    builder.row(InlineKeyboardButton(text="🔄 Найти другую", callback_data="start_over"))
    return builder.as_markup()

def get_admin_approval_kb(point_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Одобрить", callback_data=f"admin_approve_{point_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{point_id}")
    )
    return builder.as_markup()