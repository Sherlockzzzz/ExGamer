import random
import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor


API_TOKEN = '6927487057:AAFJ0pdIuRQdYuvQ6LNfZK6lAHcKmO6fjLQ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Теперь добавляем кнопку "Казино" в главное меню
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"coins": 0, "level": 1, "nickname": message.from_user.username, "solved_problems": 0}

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Заработать", callback_data='earn'),
        InlineKeyboardButton("Профиль", callback_data='profile'),
        InlineKeyboardButton("Магазин", callback_data='store'),
        InlineKeyboardButton("Казино(В разработке)", callback_data='casino')  # Добавляем кнопку "Казино" в главное меню
    )

    await message.reply("Привет! Добро пожаловать в игру. Выберите действие:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'earn')
async def earn_coins(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    level = user_data[user_id]["level"]

    num1 = random.randint(1, level * 10)
    num2 = random.randint(1, level * 10)
    answer = num1 + num2

    message_text = f"Решите пример: {num1} + {num2} = ?"
    
    # Удаляем предыдущее сообщение перед отправкой нового
    if user_data[user_id].get("last_message_id"):
        await bot.delete_message(chat_id=user_id, message_id=user_data[user_id]["last_message_id"])
    
    msg = await bot.send_message(chat_id=user_id, text=message_text)
    user_data[user_id]["last_message_id"] = msg.message_id
    user_data[user_id]["current_answer"] = answer

@dp.message_handler(content_types=types.ContentType.TEXT)
async def check_answer(message: types.Message):
    user_id = message.from_user.id
    if "current_answer" not in user_data.get(user_id, {}):
        return

    selected_answer = int(message.text)
    correct_answer = user_data[user_id]["current_answer"]

    if selected_answer == correct_answer:
        user_data[user_id]["coins"] += user_data[user_id]["level"]
        user_data[user_id]["solved_problems"] += 1
        await message.reply(f"Правильно! Вы заработали {user_data[user_id]['level']} монет. "
                            f"Ваш текущий счет: {user_data[user_id]['coins']} 😊")
        
        # Удаляем предыдущее сообщение
        if user_data[user_id].get("last_message_id"):
            await bot.delete_message(chat_id=user_id, message_id=user_data[user_id]["last_message_id"])
        
        # Добавляем кнопку "Заработать" после правильного ответа
        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton("Заработать", callback_data='earn'))
        msg = await bot.send_message(chat_id=user_id, text="Выберите действие:", reply_markup=keyboard)
        user_data[user_id]["last_message_id"] = msg.message_id
    else:
        await message.reply("Неправильно. Попробуйте еще раз. 😔")

        # Удаляем предыдущее сообщение
        if user_data[user_id].get("last_message_id"):
            await bot.delete_message(chat_id=user_id, message_id=user_data[user_id]["last_message_id"])
        
        # При неправильном ответе предлагаем новый пример
        level = user_data[user_id]["level"]
        num1 = random.randint(1, level * 10)
        num2 = random.randint(1, level * 10)
        answer = num1 + num2
        message_text = f"Новый пример: {num1} + {num2} = ?"
        msg = await bot.send_message(chat_id=user_id, text=message_text)
        user_data[user_id]["last_message_id"] = msg.message_id
        user_data[user_id]["current_answer"] = answer

admins = {123456789}  # Замените на реальные ID администраторов бота
user_data = {}



@dp.callback_query_handler(lambda c: c.data == 'casino')
async def enter_casino(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    print("Пользователь", user_id, "вошел в казино.")
    await bot.send_message(chat_id=user_id, text="Добро пожаловать в казино! ",
                           reply_markup=create_casino_menu())

def create_casino_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Орел", callback_data='flip_coin_head'),
        InlineKeyboardButton("Решка", callback_data='flip_coin_tail'),
        InlineKeyboardButton("Назад", callback_data='back_to_main_menu')
    )
    return keyboard

@dp.callback_query_handler(lambda c: c.data in ['flip_coin_head', 'flip_coin_tail'])
async def flip_coin(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    print("Пользователь", user_id, "выбрал игру 'Орел и Решка'.")
    choice = callback_query.data.split('_')[2]  # Извлекаем выбор пользователя: 'head' или 'tail'

    # Отправляем сообщение с запросом о размере ставки
    await bot.send_message(chat_id=user_id, text="Введите размер вашей ставки (в монетах):",
                           reply_markup=types.ForceReply())

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_bet(message: types.Message):
    user_id = message.from_user.id
    if message.reply_to_message and message.reply_to_message.text == "Введите размер вашей ставки (в монетах):":
        bet_amount = int(message.text)
        user_balance = user_data[user_id]["coins"]

        if bet_amount > user_balance:
            await bot.send_message(chat_id=user_id, text="У вас недостаточно монет для ставки.")
            return

        # Извлекаем выбор пользователя из текста сообщения
        choice = message.reply_to_message.reply_markup.inline_keyboard[0][0].text
        if choice not in ['Орел', 'Решка']:
            await bot.send_message(chat_id=user_id, text="Ошибка выбора. Пожалуйста, выберите Орел или Решка.")
            return

        # Здесь можно реализовать бросок монеты и проверить результат
        result = random.choice(['Орел', 'Решка'])  # Случайный выбор между "Орел" и "Решка"

        if choice == result:
            user_data[user_id]["coins"] += bet_amount  # При выигрыше удваиваем ставку
            await bot.send_message(chat_id=user_id, text=f"Поздравляем! Вы угадали! Ваш баланс: {user_data[user_id]['coins']} монет. 🎉")
        else:
            user_data[user_id]["coins"] -= bet_amount
            await bot.send_message(chat_id=user_id, text=f"К сожалению, вы проиграли. Ваш баланс: {user_data[user_id]['coins']} монет. 😔")

@dp.callback_query_handler(lambda c: c.data == 'back_to_main_menu')
async def back_to_main_menu(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await bot.send_message(chat_id=user_id, text="Возвращаемся в главное меню.",
                           reply_markup=create_main_menu())

def create_main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Заработать", callback_data='earn'),
        InlineKeyboardButton("Профиль", callback_data='profile'),
        InlineKeyboardButton("Магазин", callback_data='store'),
        InlineKeyboardButton("Казино", callback_data='casino')
    )
    return keyboard

def create_main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Заработать", callback_data='earn'),
        InlineKeyboardButton("Профиль", callback_data='profile'),
        InlineKeyboardButton("Магазин", callback_data='store'),
        InlineKeyboardButton("Казино", callback_data='casino')
    )
    return keyboard


@dp.message_handler(commands=['casino'])
async def enter_casino_command(message: types.Message):
    user_id = message.from_user.id
    # Здесь также может быть логика для входа пользователя в казино
    await bot.send_message(chat_id=user_id, text="Добро пожаловать в казино! Выберите игру или действие.")


def apply_upgrade(user_id, earnings):
    upgrades = user_data[user_id].get("upgrades", {})
    multiplier = upgrades.get("multiplier", 1)  # Получаем множитель улучшения, если есть, иначе 1
    return earnings * multiplier



@dp.callback_query_handler(lambda c: c.data == 'profile')
async def view_profile(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    nickname = user_data[user_id]["nickname"]
    balance = user_data[user_id]["coins"]
    solved_problems = user_data[user_id]["solved_problems"]
    
    # Используем HTML-теги для моноширинного шрифта
    profile_text = f"<b>Ник-нейм:</b> {nickname}\n<b>Айди:</b> <code>{user_id}</code>\n<b>Баланс:</b> {balance}\n<b>Кол-во решенных примеров:</b> {solved_problems}"
    await bot.send_message(chat_id=user_id, text=profile_text, parse_mode='HTML')



@dp.message_handler(commands=['pay'])
async def pay_coins(message: types.Message):
    user_id = message.from_user.id
    try:
        # Разбираем аргументы команды
        _, target_user, amount = message.text.split()
        target_user_id = int(target_user[1:])  # Убираем "@" из упоминания пользователя
        amount = int(amount)

        # Проверяем, достаточно ли монет у пользователя
        if user_data[user_id]["coins"] < amount:
            await message.reply("У вас недостаточно монет для перевода.")
            return

        # Переводим монеты другому пользователю
        user_data[user_id]["coins"] -= amount
        user_data[target_user_id]["coins"] += amount

        await message.reply(f"Вы успешно перевели {amount} монет пользователю {target_user}."
                            f"Ваш текущий баланс: {user_data[user_id]['coins']}")
    except ValueError:
        await message.reply("Неправильный формат команды. Используйте /pay @username amount")


@dp.message_handler(commands=['banbot'])
async def ban_bot(message: types.Message):
    admin_id = message.from_user.id
    if admin_id not in admins:
        await message.reply("Вы не являетесь администратором.")
        return

    try:
        _, target_user, ban_time = message.text.split()
        target_user_id = int(target_user[1:])  # Убираем "@" из упоминания пользователя
        ban_time = int(ban_time)

        # Заблокировать пользователя в боте
        await bot.restrict_chat_member(message.chat.id, target_user_id, until_date=time.time() + ban_time)

        await message.reply(f"Пользователь {target_user} заблокирован в боте на {ban_time} секунд.")
    except ValueError:
        await message.reply("Неправильный формат команды. Используйте /banbot @username ban_time")


@dp.message_handler(commands=['mute'])
async def mute_user(message: types.Message):
    admin_id = message.from_user.id
    if admin_id not in admins:
        await message.reply("Вы не являетесь администратором.")
        return

    try:
        _, target_user, mute_time = message.text.split()
        target_user_id = int(target_user[1:])  # Убираем "@" из упоминания пользователя
        mute_time = int(mute_time)

        # Дать пользователю мут в чате
        await bot.restrict_chat_member(message.chat.id, target_user_id, until_date=time.time() + mute_time)

        await message.reply(f"Пользователь {target_user} получил мут в чате на {mute_time} секунд.")
    except ValueError:
        await message.reply("Неправильный формат команды. Используйте /mute @username mute_time")


@dp.message_handler(commands=['givemoney'])
async def give_money(message: types.Message):
    admin_id = message.from_user.id
    if admin_id not in admins:
        await message.reply("Вы не являетесь администратором.")
        return

    try:
        _, target_user, amount = message.text.split()
        target_user_id = int(target_user[1:])  # Убираем "@" из упоминания пользователя
        amount = int(amount)

        # Выдать монеты пользователю
        user_data[target_user_id]["coins"] += amount

        await message.reply(f"Вы успешно выдали {amount} монет пользователю {target_user}."
                            f"Текущий баланс пользователя: {user_data[target_user_id]['coins']}")
    except ValueError:
        await message.reply("Неправильный формат команды. Используйте /givemoney @username amount")

@dp.callback_query_handler(lambda c: c.data == 'store')
async def view_store(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Улучшения", callback_data='improvements'),
        InlineKeyboardButton("Автомобили", callback_data='cars'),
        InlineKeyboardButton("Дома", callback_data='houses'),
        InlineKeyboardButton("Донат", callback_data='donate')
    )

    await bot.send_message(chat_id=callback_query.from_user.id, text="[В РАЗРАБОТКЕ] Выберите категорию товаров: ", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'improvements')
async def view_improvements(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("x2 (500 монет)", callback_data='x2'),
        InlineKeyboardButton("x3 (1500 монет)", callback_data='x3'),
        InlineKeyboardButton("x10 (11000 монет)", callback_data='x10'),
        InlineKeyboardButton("x100 (115000 монет)", callback_data='x100')
    )


    await bot.send_message(chat_id=user_id, text="Выберите улучшение:", reply_markup=keyboard)
@dp.message_handler(commands=['id'])
async def get_user_id(message: types.Message):
    admin_id = message.from_user.id
    if admin_id not in admins:
        await message.reply("Вы не являетесь администратором.")
        return

    try:
        _, target_user = message.text.split()
        target_user_id = int(target_user[1:])  # Убираем "@" из упоминания пользователя
        await message.reply(f"ID пользователя {target_user}: {target_user_id}")
    except ValueError:
        await message.reply("Неправильный формат команды. Используйте /id @username")

@dp.message_handler(content_types=types.ContentType.TEXT, commands=['users'])
async def show_users(message: types.Message):
    admin_id = message.from_user.id
    if admin_id not in admins:
        await message.reply("Вы не являетесь администратором.")
        return

    users_info = []
    for user_id, user_info in user_data.items():
        nickname = user_info.get("nickname", "")
        tag = f"@{user_info.get('nickname', '')}" if user_info.get('nickname') else ""
        users_info.append(f"{nickname} | {tag} | {user_id}")

    users_list = "\n".join(users_info)
    await message.reply("Список пользователей:\n" + users_list)


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
