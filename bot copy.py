from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton

import asyncio
from datetime import datetime
import logging

from config import TOKEN
import keyboards as kb
from database import Database
#from month_translate import month_translate


# задаем уровень логов
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# проверка работы бота
@dp.message_handler(commands=['work'])
async def cmd_sendqw(message: types.Message):
    await bot.send_message(message.from_user.id, text='Да работаю я, работаю!')

# меню
@dp.message_handler(commands=['menu'])
async def cmd_sendqw(message: types.Message):
    await bot.send_message(message.from_user.id,
				text=kb.text_menu,
				reply_markup=kb.inline_kb_menu(),
				parse_mode=ParseMode.MARKDOWN)

# обработчик кнопок
@dp.callback_query_handler(lambda c: c.data.startswith('btn'))
async def process_callback_button(callback_query: types.CallbackQuery):
    code = callback_query.data
    print('user ' + callback_query.from_user.username + ' opened ' + code)

    # назад в главное меню 
    if code == 'btn_back_menu':
        await callback_query.message.edit_text(
            text=kb.text_menu, 
            reply_markup=kb.inline_kb_menu(), 
            parse_mode=ParseMode.MARKDOWN
            )

	# афиша
    if code == 'btn_afisha':
        await callback_query.message.edit_text(
            text=kb.text_afisha, 
            reply_markup=kb.inline_kb_afisha(), 
            parse_mode=ParseMode.MARKDOWN
            )

    # меню игры
    if code.split('_')[1] == 'game':
        text, reply_markup = kb.inline_kb_game(callback_query.from_user.id, int(code.split('_')[-1]))
        await callback_query.message.edit_text(
            text=text, 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN
            )

    # игроки, записанные на игру
    if code.split('_')[1] == 'players':
        text = kb.players_text(int(code.split('_')[-1]))
        await callback_query.message.edit_text(
            text=text, 
            reply_markup=kb.back_game_btn(int(code.split('_')[-1])), 
            parse_mode=ParseMode.MARKDOWN
            )
    
    # меню регистрация
    if code.split('_')[1] == 'registration':
        await callback_query.message.edit_text(
            text=kb.registration_text, 
            reply_markup=kb.inline_kb_registration(code.split('_')[-1]), 
            parse_mode=ParseMode.MARKDOWN
            )
    # записаться на игру
    if code.split('_')[1][:-1] == 'reg':
        text, reply_markup = kb.inline_kb_game_1(int(code.split('_')[-1]))
        await callback_query.message.edit_text(
            text = text, 
            reply_markup = reply_markup, 
            parse_mode=ParseMode.MARKDOWN
            )
        Database().add_registration(callback_query.from_user.id, callback_query.from_user.username, callback_query.from_user.first_name, int(code.split('_')[-1]), int(code.split('_')[1][-1]))
'''     
    # выписаться из игры
    if code.split('_')[1] == 'delregistration':
        Database().del_registration(callback_query.from_user.id, code.split('_')[-1])
        text, reply_markup = kb.inline_kb_game_2(int(code.split('_')[-1]))
        await callback_query.message.edit_text(
            text=text, 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN
            )
'''

@dp.callback_query_handler(lambda c: 'delregistration' in c.data)
async def process_callback_button(callback_query: types.CallbackQuery):
    code = callback_query.data
    print('user ' + callback_query.from_user.username + ' opened ' + code)

    
    text, reply_markup = kb.inline_kb_game_2(int(code.split('_')[-1]))
    await callback_query.message.edit_text(
        text=text, 
        reply_markup=reply_markup, 
        parse_mode=ParseMode.MARKDOWN
        )
    Database().del_registration(callback_query.from_user.id, code.split('_')[-1])

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
