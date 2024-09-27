from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.utils import executor
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton

import logging
import os

from config import TOKEN
import keyboards as kb
from database import Database
#from month_translate import month_translate


# задаем уровень логов
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class Form(StatesGroup):
    username = State()
    user_phone = State()
    game_button = State()
    game_description = State()
    game_image = State()
    new_message = State()

# запуск бота
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    db = Database('database.db')
    if not (db.subscriber_exists(message.from_user.id)):
        db.add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            user_firstname=message.from_user.first_name,
            user_phone = None
            )

    await bot.send_message(message.from_user.id,
				text=kb.text_menu,
				reply_markup=kb.inline_kb_menu(message.from_user.id),
				parse_mode=ParseMode.MARKDOWN)

# проверка работы бота
@dp.message_handler(commands=['work'])
async def cmd_work(message: types.Message):
    await bot.send_message(message.from_user.id, text='Да работаю я, работаю!')

# меню
@dp.message_handler(commands=['menu'])
async def cmd_menu(message: types.Message):
    print(kb.inline_kb_menu(message.from_user.id))
    await bot.send_message(message.from_user.id,
				text=kb.text_menu,
				reply_markup=kb.inline_kb_menu(message.from_user.id),
				parse_mode=ParseMode.MARKDOWN)


# назад в главное меню 
@dp.callback_query_handler(lambda c: c.data == 'btn_backmenu')
async def process_callback_button(callback_query: types.CallbackQuery):
    try:
        await callback_query.message.edit_text(
            text=kb.text_menu, 
            reply_markup=kb.inline_kb_menu(callback_query.from_user.id), 
            parse_mode=ParseMode.MARKDOWN
            )
    except:
        await callback_query.message.delete()
        await bot.send_message(
            callback_query.message.chat.id,
            text=kb.text_menu, 
            reply_markup=kb.inline_kb_menu(callback_query.from_user.id), 
            parse_mode=ParseMode.MARKDOWN
            )

# афиша
@dp.callback_query_handler(lambda c: c.data == 'btn_afisha')
async def process_callback_button(callback_query: types.CallbackQuery):
    try:
        await callback_query.message.edit_text(
            text=kb.text_afisha, 
            reply_markup=kb.inline_kb_afisha(), 
            parse_mode=ParseMode.MARKDOWN
            )
    except:    
        await callback_query.message.delete()
        await bot.send_message(
            callback_query.message.chat.id,
            text=kb.text_afisha, 
            reply_markup=kb.inline_kb_afisha(), 
            parse_mode=ParseMode.MARKDOWN
            )

# меню игры
@dp.callback_query_handler(lambda c: c.data.split('_')[1] == 'game')
async def process_callback_button(callback_query: types.CallbackQuery):
    code = callback_query.data
    text, reply_markup = kb.inline_kb_game(callback_query.from_user.id, int(code.split('_')[-1]))

    try:
        photo = types.InputMedia(media=open(f"image/game_{code.split('_')[-1]}.jpeg", 'rb'), caption=text)
        await callback_query.message.edit_media(
            media=photo,
            reply_markup=reply_markup
            )
    except:
        try:
            await callback_query.message.delete()
            
        except:
            print('cant delete message')
        photo = open(f"image/game_{code.split('_')[-1]}.jpeg", 'rb')
        await bot.send_photo(callback_query.message.chat.id, photo=photo, caption=text, reply_markup=reply_markup)
    

# игроки, записанные на игру
@dp.callback_query_handler(lambda c: c.data.split('_')[1] == 'players')
async def process_callback_button(callback_query: types.CallbackQuery):
    code = callback_query.data
    text = kb.players_text(int(code.split('_')[-1]))
    reply_markup = kb.players_keyboard(int(callback_query.from_user.id), int(code.split('_')[-1]))
    await callback_query.message.edit_caption(
            caption=text, 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN
            )
    
# удаление игроков
@dp.callback_query_handler(lambda c: c.data.split('_')[1] == 'deleteplayer')
async def process_callback_button(callback_query: types.CallbackQuery):
    code = callback_query.data
    print(code)
    game_id = int(code.split('_')[-1])
    if len(code.split('_')) > 3:
        game_id = int(code.split('_')[-2])
        Database('database.db').del_registration(
            user_id=int(code.split('_')[-1]), 
            game_id=game_id
        )
        
    text, reply_markup = kb.delete_players_keyboard(game_id)
    await callback_query.message.edit_caption(
            caption=text, 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN
            )
    
# меню регистрация
@dp.callback_query_handler(lambda c: c.data.split('_')[1] == 'registration')
async def process_callback_button(callback_query: types.CallbackQuery):
    code = callback_query.data

    await callback_query.message.edit_caption(
        caption=kb.registration_text, 
        reply_markup=kb.inline_kb_registration(code.split('_')[-1]), 
        parse_mode=ParseMode.MARKDOWN
        )

# записаться на игру
@dp.callback_query_handler(lambda c: c.data.split('_')[1][:-1] == 'reg')
async def process_callback_button(callback_query: types.CallbackQuery):
    code = callback_query.data
    #добавить регистрацию
    Database('database.db').add_registration(
        user_id=callback_query.from_user.id, 
        username=callback_query.from_user.username, 
        user_firstname=callback_query.from_user.first_name, 
        game_id=int(code.split('_')[-1]), 
        count=int(code.split('_')[1][-1])
        )

    text, reply_markup = kb.inline_kb_game(
        user_id=callback_query.from_user.id,
        game_id=int(code.split('_')[-1])
        )
    await callback_query.message.edit_caption(
        caption = f"{text}", 
        reply_markup = reply_markup
        )


@dp.callback_query_handler(lambda c: 'delregistration' in c.data)
async def process_callback_button(callback_query: types.CallbackQuery):
    code = callback_query.data
    # удалить регистрацию
    Database('database.db').del_registration(
        user_id=callback_query.from_user.id, 
        game_id=int(code.split('_')[-1]))

    text, reply_markup = kb.inline_kb_game(
        user_id = callback_query.from_user.id,
        game_id=int(code.split('_')[-1])
        )
    
    await callback_query.message.edit_caption(
        caption=f"{text}", 
        reply_markup=reply_markup, 
        )

# профиль
@dp.callback_query_handler(lambda c: c.data == 'btn_profile')
async def process_callback_button(callback_query: types.CallbackQuery):
    print(callback_query)
    code = callback_query.data
    text, reply_markup = kb.inline_kb_profile(callback_query.from_user.id)
    await callback_query.message.edit_text(
            text=text, 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN
            )

# меняем имя
@dp.callback_query_handler(lambda c: c.data == 'btn_changename')
async def process_callback_button(callback_query: types.CallbackQuery):
    await Form.username.set()
    await callback_query.message.edit_text(text='Введите ваше имя:')

# получаем имя
@dp.message_handler(state=Form.username)
async def process_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['username'] = message.text
    await state.finish()
    Database('database.db').user_edit_name(message.from_user.id, data['username'])

    text, reply_markup = kb.inline_kb_profile(message.from_user.id)
    
    await bot.send_message(
            message.from_user.id,
            text=text, 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN
            )

# меняем номер
@dp.callback_query_handler(lambda c: c.data == 'btn_addnumber')
async def process_callback_button(callback_query: types.CallbackQuery):
    await Form.user_phone.set()
    await callback_query.message.edit_text(text='Введите номер телефона:')

# получаем номер
@dp.message_handler(state=Form.user_phone)
async def process_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_phone'] = message.text
    await state.finish()
    Database('database.db').add_user_phone(message.from_user.id, data['user_phone'])

    text, reply_markup = kb.inline_kb_profile(message.from_user.id)
    
    await bot.send_message(
            message.from_user.id,
            text=text, 
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
            )

# меню администратора
@dp.callback_query_handler(lambda c: c.data == 'btn_admin')
async def process_callback_button(callback_query: types.CallbackQuery):
    text, reply_markup = kb.inline_kb_admin()
    await callback_query.message.edit_text(
            text=text, 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN
            )

# выложить новую игру
@dp.callback_query_handler(lambda c: c.data == 'btn_newgame')
async def process_callback_button(callback_query: types.CallbackQuery):
    code = callback_query.data
    text = 'Введите название игры для отображания на кнопке'
    await Form.game_button.set()
    await callback_query.message.edit_text(
            text=text, 
            parse_mode=ParseMode.MARKDOWN
            )

# получаем кнопку игры
@dp.message_handler(state=Form.game_button)
async def process_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['game_button'] = message.text
    Database('database.db').add_game_button(data['game_button'])

    await state.finish()
    text = 'Введите описание игры для отображания в меню игры'
    await Form.game_description.set()
    await bot.send_message(
            message.from_user.id,
            text=text, 
            parse_mode=ParseMode.MARKDOWN
            )

# получаем описание игры
@dp.message_handler(state=Form.game_description)
async def process_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['game_description'] = message.text
    Database('database.db').add_game_description(data['game_description'])
    await state.finish()

    text = 'Отправьте изображение афиши'
    await Form.game_image.set()
    await bot.send_message(
            message.from_user.id,
            text=text, 
            parse_mode=ParseMode.MARKDOWN
            )

# получаем афишу
@dp.message_handler(content_types=["photo"], state=Form.game_image)
async def get_image(message, state: FSMContext):
    db = Database('database.db')
    game_id = db.get_games()[-1][0]
    await message.photo[-1].download(destination_file=f'image/game_{game_id}.jpeg')
    db.add_game_image(f'game_{game_id}')
    await state.finish()
    text, reply_markup = kb.inline_kb_admin()
    await bot.send_message(
            message.from_user.id,
            text=text + '\n\n Новая игра опубликована.', 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN
            )

# отправить сообщение всем юзерам
@dp.callback_query_handler(lambda c: c.data == 'btn_sendmessage')
async def process_callback_button(callback_query: types.CallbackQuery):
    text = 'Введите текст сообщения'
    await Form.new_message.set()
    await callback_query.message.edit_text(
            text=text, 
            parse_mode=ParseMode.MARKDOWN
            )

# получаем текст сообщения для рассылки
@dp.message_handler(state=Form.new_message)
async def process_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['message'] = message.text
    
    #await state.finish()
    text = data['message']
    reply_markup = kb.inline_sendmessage()
    await bot.send_message(
            message.from_user.id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
            )

# Рассылка сообщения
@dp.callback_query_handler(lambda c: c.data == 'btn_aceptsending', state=Form.new_message)
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        text = data['message']


    for user_id in Database('database.db').get_users():
        try:
            await bot.send_message(
                user_id[0],
                text=text
            )
        except:
            continue
    await state.finish()

    text, reply_markup = kb.inline_kb_admin()
    await bot.send_message(
            callback_query.from_user.id,
            text=text + '\n\n Сообщение отправлено пользователям.',
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN
            )

# Отмена рассылки сообщения
@dp.callback_query_handler(lambda c: c.data == 'btn_denysending', state=Form.new_message)
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    text, reply_markup = kb.inline_kb_admin()
    await bot.send_message(
            callback_query.from_user.id,
            text=text + '\n\n Сообщение не разослано.', 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN
            )

# выбор игры для удаления
@dp.callback_query_handler(lambda c: c.data == 'btn_delgame')
async def process_callback_button(callback_query: types.CallbackQuery):
    text, reply_markup = kb.inline_kb_delgame()
    await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
            )

# удаление игры
@dp.callback_query_handler(lambda c: 'delgame' in c.data)
async def process_callback_button(callback_query: types.CallbackQuery):
    code = callback_query.data
    game_id = code.split('_')[-1]
    Database('database.db').del_game(int(game_id))
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'image/game_{game_id}.jpeg')
    os.remove(path)

    text, reply_markup = kb.inline_kb_admin()
    await callback_query.message.edit_text(
            text=text + '\n\nИгра успешно удалена.',
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
            )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
