from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import text, bold, link
import emoji

from database import Database

# общие кнопки 
back_menu_btn = InlineKeyboardButton(emoji.emojize(':arrow_left: Выйти в меню :arrow_left:', language='alias'), callback_data='btn_backmenu')
back_afisha_btn = InlineKeyboardButton(emoji.emojize(':arrow_left: Назад :arrow_left:', language='alias'), callback_data='btn_afisha')

# клавиатура меню
def inline_kb_menu(user_id):
	inline_kb_menu = InlineKeyboardMarkup(row_width=1)
	text_and_data = [
			[emoji.emojize(':city_sunrise: Афиша :city_sunrise:', language='alias'), 'btn_afisha'],
			[emoji.emojize(':night_with_stars: Профиль :night_with_stars:', language='alias'), 'btn_profile'],
			]
	row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
	inline_kb_menu.add(*row_btns)
	if user_id in [227184505, 697217427]:
		admin_button = InlineKeyboardButton('Меню администратора', callback_data = 'btn_admin')
		inline_kb_menu.row(admin_button)
	return inline_kb_menu

# клавиатура афиши
def inline_kb_afisha():
	inline_kb_afisha = InlineKeyboardMarkup(row_width=1)
	text_and_data = []
	games = Database('database.db').get_games()
	for game in games:
		text_and_data.append([game[1], 'btn_game_' + str(game[0])]) #поля button (название игры) и id 
	row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
	inline_kb_afisha.add(*row_btns)
	inline_kb_afisha.row(back_menu_btn)
	return inline_kb_afisha

# меню игры
def inline_kb_game(user_id, game_id: int):
	inline_kb_game = InlineKeyboardMarkup(row_width=2)
	db = Database('database.db')
	games = db.get_games()
	# кнопки переключения между играми
	if len(games) > 1:
		game_id_list = [game[0] for game in db.get_games()]
		
		if game_id == min(game_id_list):
			inline_kb_game.add(InlineKeyboardButton(emoji.emojize('Следующая :arrow_right:', language='alias'), callback_data = 'btn_game_' + str(game_id_list[game_id_list.index(game_id)+1])))
		
		elif game_id == max(game_id_list):
			inline_kb_game.add(InlineKeyboardButton(emoji.emojize(':arrow_left: Предыдущая', language='alias'), callback_data = 'btn_game_' + str(game_id_list[game_id_list.index(game_id)-1])))
			
		else:
			next = InlineKeyboardButton(emoji.emojize('Следующая :arrow_right:', language='alias'), callback_data = 'btn_game_' + str(game_id_list[game_id_list.index(game_id)+1]))
			previous = InlineKeyboardButton(emoji.emojize(':arrow_left: Предыдущая', language='alias'), callback_data = 'btn_game_' + str(game_id_list[game_id_list.index(game_id)-1]))
			inline_kb_game.add(previous, next)
				

	players_btn = InlineKeyboardButton(emoji.emojize(f':bust_in_silhouette: Игроки ({db.get_numplayers(game_id)}/19)', language='alias'), callback_data = 'btn_players_' + str(game_id))
	inline_kb_game.row(players_btn)
	# проверяем записан ли уже на игру
	if (db.registration_exists(user_id, game_id)):
		del_registration_btn = InlineKeyboardButton(emoji.emojize(':x: Отменить запись', language='alias'), callback_data = 'btn_delregistration_' + str(game_id))
		inline_kb_game.row(del_registration_btn)
	else:
		registration_btn = InlineKeyboardButton(emoji.emojize(':white_check_mark: Записаться', language='alias'), callback_data = 'btn_registration_' + str(game_id))
		inline_kb_game.row(registration_btn)
	
	inline_kb_game.row(back_menu_btn)
	text = db.get_game(game_id)[3]
	return text, inline_kb_game

#клавиатура регистрации
def inline_kb_registration(game_id):
	inline_kb_registration = InlineKeyboardMarkup(row_width=2)
	text_and_data = [
			['Я один', 'btn_reg1_' + game_id],
			['+ 1', 'btn_reg2_' + game_id],
			['+ 2', 'btn_reg3_' + game_id],
			['+ 3', 'btn_reg4_' + game_id],
			]
	row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
	inline_kb_registration.add(*row_btns)
	return inline_kb_registration

# кнопка назад к игре
def back_game_btn(game_id):
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton(emoji.emojize(':arrow_left: Назад :arrow_left:', language='alias'), callback_data='btn_game_' + str(game_id)))
	return keyboard

# меню игроки
def players_text(game_id):
	players = Database('database.db').get_registration(game_id)
	if len(players) < 1:
		text = 'На данную игру еще никто не зарегистрировался'
	else:
		text = f'На данный момент зарегистрировались:\n\n'
		counter = 1
		for player in players:
			if player[5] == 1:
				text += f'{str(counter)}. ' +  link(player[3], f'https://t.me/{player[2]}') + ' \n'
				counter += 1
			else:
				text += f'{str(counter)}. ' + link(player[3], f'https://t.me/{player[2]}') + f' + {player[5] - 1} \n'
				counter += 1
	return text

# профиль игрока
def inline_kb_profile(user_id):
	db = Database('database.db')
	user = db.get_user(user_id)
	if user[4] == None:
		phone = 'не указан'
	else:
		phone = str(user[4])

	games = db.get_user_registration(user_id)
	if bool(games):
		user_games = ''
		counter = 1
		for game in games:
			user_games += f'{counter}.' + game[0] + '\n'
			counter +=1

		text_profile = text(bold('ПРОФИЛЬ ИГРОКА'),
			f'Ваше имя: {user[3]}',
			f'Номер телефона: {phone}',
			'\nИгры, на которые вы записаны:\n' + user_games,
			sep='\n')
	else:
		text_profile = text(bold('ПРОФИЛЬ ИГРОКА'),
			f'Ваше имя: {user[3]}',
			f'Номер телефона: {phone}',
			'Чтобы зарегистрироваться на игру перейдите в меню "Афиша"',
			sep='\n\n')
	inline_kb_profile = InlineKeyboardMarkup(row_width=1)
	text_and_data = [
			['Изменить имя', 'btn_changename'],
			['Изменить номер телефона', 'btn_addnumber'],
			]

	row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
	inline_kb_profile.add(*row_btns)
	inline_kb_profile.row(back_menu_btn)
	return text_profile, inline_kb_profile

# меню администратора
def inline_kb_admin():
	inline_kb_admin = InlineKeyboardMarkup(row_width=1)
	text_and_data = [
		['Разослать сообщение', 'btn_sendmessage'],
		['Выложить новую игру', 'btn_newgame'],
		['Удалить игру', 'btn_delgame'],
		]
	row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
	inline_kb_admin.add(*row_btns)
	inline_kb_admin.row(back_menu_btn)
	text_admin = text(bold('МЕНЮ АДМИНИСТРАТОРА'))
	return text_admin, inline_kb_admin

# проверка сообщения перед отправкой
def inline_sendmessage():
	inline_kb_sendmessage = InlineKeyboardMarkup(row_width=1)
	btn_send = InlineKeyboardButton(emoji.emojize(':white_check_mark: Отправить :white_check_mark:', language='alias'), callback_data = 'btn_aceptsending')
	btn_deny = InlineKeyboardButton(emoji.emojize(':x: Отменить :x:', language='alias'), callback_data = 'btn_denysending')
	inline_kb_sendmessage.row(btn_send)
	inline_kb_sendmessage.row(btn_deny)
	return inline_kb_sendmessage

# меню выборы игры для удаления
def inline_kb_delgame():
	inline_kb_delgame = InlineKeyboardMarkup(row_width=1)
	text_and_data = []
	games = Database('database.db').get_games()
	for game in games:
		text_and_data.append([game[1], 'btn_delgame_' + str(game[0])]) #поля button (название игры) и id 
	row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
	inline_kb_delgame.add(*row_btns)
	admin_button = InlineKeyboardButton(emoji.emojize(':arrow_left: Назад :arrow_left:', language='alias'), callback_data = 'btn_admin')
	inline_kb_delgame.row(admin_button)
	text = 'Выберите игру, которую нужно удалить'
	return text, inline_kb_delgame


text_menu = text(bold('МЕНЮ'),
			'Добро пожаловать в клуб мафии.',
			'Открой "Афишу", чтобы узнать о ближайших играх.',
			'Открой "Профиль", чтобы просмотреть свой профиль.',
			'Да проснётся город!', sep='\n')

text_afisha = text(bold('АФИША'),
			'Здесь вы можете посмотреть список ближайших игр',
			'Выбери игру, чтобы посмотреть подробности', sep='\n')

registration_text = text('Вы будете один или с друзьями?', 
			'Выберите один из вариантов:', sep='\n')