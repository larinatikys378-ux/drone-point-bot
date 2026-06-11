import asyncio
import time
import random
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import BotCommand

# Твой токен бота
API_TOKEN = '8681694729:AAG8uit8QTLl7Fp67ZRESsVMNramA7RRpcc'

# ТАЙМЕР ОЖИДАНИЯ — 1 ЧАС (3600 секунд)
COOLDOWN_TIME = 3600

# ID картинок, сохраненные на серверах Телеграма
SHAHED_FILE_ID = 'AgACAgIAAxkBAAMXainBBzERwbsziSL9LF6wH5cqqTIAAp0iaxu4BlFJ5pS3UlZ5Q78BAAMCAAN4AAM7BA'
FAB_FILE_ID = 'AgACAgIAAxkBAAM9ainYzsnOC1wnasdIPQJK4iHzTaIAAnwfaxtqFFFJj0NY-Cl6h5IBAAMCAAN5AAM7BA'
HORNET_FILE_ID = 'AgACAgIAAxkBAAM9ainYzsnOC1wnasdIPQJK4iHzTaIAAnwfaxtqFFFJj0NY-Cl6h5IBAAMCAAN5AAM7BA'

# Файл на телефоне, где сохраняется прогресс игроков
STATS_FILE = 'bot_stats.json'

# Чистый запуск бота без прокси-серверов
bot = Bot(token=API_TOKEN, default=DefaultBotProperties())
dp = Dispatcher()

# Установка меню команд (/start и /mystats) в левом нижнем углу чата
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/mystats", description="Посмотреть свой инвентарь и профиль")
    ]
    await bot.set_my_commands(main_menu_commands)

# Загрузка статистики игроков из файла JSON
def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

# Сохранение статистики игроков в файл JSON
def save_stats(stats):
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения файла: {e}")

user_cooldowns = {}
user_stats = load_stats()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "👋 Привет! Я готов выдавать карточки Drone Point.\n\n"
        "🤖 Чтобы получить карточку, просто напиши мне кодовое слово:\n"
        "👉 **дрон**, **бпла** или **беспилотник**.\n\n"
        "📊 Посмотреть свой инвентарь можно через команду /mystats",
        parse_mode="Markdown"
    )

@dp.message(Command("mystats"))
async def show_stats(message: types.Message):
    try:
        user_id = str(message.from_user.id) if message.from_user else str(message.chat.id)
        
        if user_id not in user_stats:
            await bot.send_message(
                chat_id=message.chat.id, 
                text="📊 У тебя пока пустой профиль. Напиши кодовое слово!", 
                reply_to_message_id=message.message_id
            )
            return
            
        data = user_stats[user_id]
        total_rolls = data.get("total_rolls", 0)
        inventory = data.get("inventory", {})
        
        shahed_count = inventory.get("Shahed-136", 0)
        fab_count = inventory.get("ФАБ с УМПК", 0)
        hornet_count = inventory.get("БПЛА Hornet", 0)
        
        stats_text = (
            f"📊 **Твой игровой профиль Drone Point:**\n\n"
            f"⚪ `Использовано попыток:` {total_rolls}\n\n"
            f"📦 **Твой инвентарь карточек:**\n"
            f"✈️ Shahed-136: {shahed_count} шт.\n"
            f"💥 ФАБ с УМПК: {fab_count} шт.\n"
            f"🐝 БПЛА Hornet: {hornet_count} шт."
        )
        await bot.send_message(
            chat_id=message.chat.id, 
            text=stats_text, 
            parse_mode="Markdown", 
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        print(f"Ошибка в команде /mystats: {e}")

# Получение ID картинок (для администратора)
@dp.message(lambda message: message.photo)
async def get_any_photo_id(message: types.Message):
    photo_id = message.photo[-1].file_id
    await message.reply(f"<code>{photo_id}</code>", parse_mode="HTML")

# Выдача карточек по триггерам «дрон», «бпла», «беспилотник»
@dp.message(lambda message: message.text and any(word in message.text.lower() for word in ["дрон", "бпла", "беспилотник"]))
async def get_card(message: types.Message):
    try:
        if not message.from_user:
            return
            
        user_id_raw = message.from_user.id
        user_id = str(user_id_raw)
        current_time = time.time()
        
        # Проверка кулдауна (1 час)
        if user_id_raw in user_cooldowns:
            last_time = user_cooldowns[user_id_raw]
            time_passed = current_time - last_time
            if time_passed < COOLDOWN_TIME:
                hours_left = int((COOLDOWN_TIME - time_passed) // 3600)
                minutes_left = int(((COOLDOWN_TIME - time_passed) % 3600) // 60)
                await bot.send_message(
                    chat_id=message.chat.id, 
                    text=f"⏳ Подожди, следующая карточка будет доступна через {hours_left} ч. {minutes_left} мин.",
                    reply_to_message_id=message.message_id
                )
                return

        user_cooldowns[user_id_raw] = current_time
        
        # Рандом карточек: 75% Редкие, 25% Сверхредкие
        pool = random.choices(["rare", "super_rare"], weights=[75, 25], k=1)[0]
        if pool == "super_rare":
            chosen_card = {
                "id": "БПЛА Hornet",
                "photo": HORNET_FILE_ID,
                "caption": "Вам выпал....\n\n🐝 **БПЛА Hornet!**\nСверхредкая 🔵 карточка."
            }
        else:
            rare_pool = [
                {"id": "Shahed-136", "photo": SHAHED_FILE_ID, "caption": "Вам выпал....\n\n✈️ **Shahed-136!**\nРедкая 🟢 карточка."},
                {"id": "ФАБ с УМПК", "photo": FAB_FILE_ID, "caption": "Вам выпал....\n\n💥 **ФАБ с УМПК!**\nРедкая 🟢 карточка."}
            ]
            chosen_card = random.choice(rare_pool)
            
        card_name = chosen_card["id"]
        
        # Обновление инвентаря игрока
        if user_id not in user_stats:
            user_stats[user_id] = {"total_rolls": 0, "inventory": {}}
            
        user_stats[user_id]["total_rolls"] += 1
        if card_name not in user_stats[user_id]["inventory"]:
            user_stats[user_id]["inventory"][card_name] = 0
        user_stats[user_id]["inventory"][card_name] += 1
        
        save_stats(user_stats)
        
        # Отправка фото карточки
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=chosen_card["photo"],
            caption=chosen_card["caption"],
            parse_mode="Markdown",
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        print(f"🛑 Ошибка при выдаче карточки: {e}", flush=True)

# Главная функция запуска
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await set_main_menu(bot)
    print("🚀 Бот Drone Point успешно запущен через основную сеть!", flush=True)
    print("💡 Убедись, что на телефоне включен VPN, иначе запросы до Телеграма не дойдут.", flush=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
