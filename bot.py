import time
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from env import TOKEN

bot = Bot(TOKEN)
storage = MemoryStorage()  # Инициализация хранилища FSM
dp = Dispatcher(bot=bot, storage=storage)  # Передача хранилища в диспетчер

voice = {'femail': "Акылай", "male": "Актан"}

class UserState(StatesGroup):
    CHOOSING = State()


# Инициализация словаря для хранения выбора пользователя
memory = {}


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    logging.info(f'{user_id} {time.asctime()}')

    # Создаем кнопки с командами /male и /femail
    keyboard = types.InlineKeyboardMarkup()
    male_button = types.InlineKeyboardButton(text="Актан", callback_data="male")
    femail_button = types.InlineKeyboardButton(text="Акылай", callback_data="femail")
    keyboard.row(male_button, femail_button)

    await message.reply(f"Салам, {user_name} !!!!!\nҮндү тандаңыз:", reply_markup=keyboard)
    await UserState.CHOOSING.set()


@dp.callback_query_handler(lambda callback_query: True, state=UserState.CHOOSING)
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    # Получаем выбор пользователя по коллбэк-данным (callback_data)
    user_choice = callback_query.data
    user_id = callback_query.from_user.id
    memory[user_id] = user_choice

    # Завершаем состояние пользователя и отвечаем сообщением
    await state.finish()
    await bot.send_message(callback_query.from_user.id,
                           f"Сиз {voice[user_choice]}дын үнүн тандадыңыз.\nТекст жазыңыз:")


@dp.message_handler(commands=['male', 'femail'], state=UserState.CHOOSING)
async def choose_handler(message: types.Message, state: FSMContext):
    user_choice = message.get_command()[1:]  # Убираем слеш (/) из команды
    user_id = message.from_user.id
    memory[user_id] = user_choice

    # Завершаем состояние пользователя и отвечаем сообщением
    await state.finish()
    await message.reply(
        f"Сиз {voice[user_choice]}дын үнүн тандадыңыз.\nТекст жазыңыз:")


@dp.message_handler(state=None)
async def message_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    chosen_command = memory.get(user_id)
    if chosen_command == 'femail':
        audio_path = 'femail/audio.wav'
    else:
        audio_path = 'male/audio.wav'
    audio = types.InputFile(audio_path)
    await bot.send_audio(chat_id=user_id, audio=audio)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




