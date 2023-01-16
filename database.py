
import sqlite3

class Database:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        
    # проверить есть ли юзер в базе
    def subscriber_exists(self, user_id):
        result = self.cursor.execute('SELECT * FROM user WHERE user_id = ?', (user_id,)).fetchall()
        return bool(len(result))

    # добавить юзера
    def add_user(self, user_id, username, user_firstname, user_phone):
        with self.connection:
            print(f'user {user_id} <{username}> added to database')
            return self.cursor.execute("INSERT INTO user (user_id, username, user_firstname, user_phone) VALUES (?,?,?,?)", (user_id, username, user_firstname, user_phone))
    
    # добавить телефон
    def add_user_phone(self, user_id, user_phone):
        with self.connection:
            print(f'user {user_id} add phone number')
            return self.cursor.execute("UPDATE user SET user_phone = ? WHERE user_id = ?", (user_phone, user_id))
    
    # изменить имя
    def user_edit_name(self, user_id, first_name):
        with self.connection:
            print(f'user {user_id} has changed first name')
            return self.cursor.execute("UPDATE user SET user_firstname = ? WHERE user_id = ?", (first_name, user_id))

    # получить всех юзеров бота
    def get_users(self):
        with self.connection:
            return self.cursor.execute("SELECT user_id FROM user").fetchall()
    
    # получить конкретного юзера
    def get_user(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM user WHERE user_id = ?", (user_id,)).fetchall()[0]
    
    # удалить юзера
    def del_game(self, user_id):
        with self.connection:
            print(f'user {user_id} deleted from database')
            return self.cursor.execute("DELETE FROM user WHERE user_id = ?", (user_id))[0]

    # добавить кнопку игры
    def add_game_button(self, button):
        with self.connection:
            return self.cursor.execute("INSERT INTO game (button) VALUES (?)", (button,))
    
    # добавить описание игры
    def add_game_description(self, description):
        with self.connection:
            return self.cursor.execute("UPDATE game SET description = ? WHERE id = (SELECT id FROM game ORDER BY id DESC LIMIT 1)", (description, ))
    
    # добавить фотографию игры
    def add_game_image(self, image):
        with self.connection:
            return self.cursor.execute("UPDATE game SET image = ? WHERE id = (SELECT id FROM game ORDER BY id DESC LIMIT 1)", (image, ))
    # получить все игры
    def get_games(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM game").fetchall()

    # получить конкретную игру
    def get_game(self, game_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM game WHERE id = ?", (game_id,)).fetchall()[0]
    
    # удалить игру
    def del_game(self, id):
        with self.connection:
            print(f'game {id} deleted from database')
            return self.cursor.execute("DELETE FROM game WHERE id = ?", (id,))

    # добавить регистрацию
    def add_registration(self, user_id, username, user_firstname, game_id, count):
        with self.connection:
            return self.cursor.execute("INSERT INTO registration (user_id, username, user_firstname, game_id, count) VALUES (?,?,?,?,?)", (user_id, username, user_firstname, game_id, count))
    
    # получить количество зарегистрированных на игру
    def get_numplayers(self, game_id):
        with self.connection:
            result = self.cursor.execute("SELECT SUM(count) FROM registration WHERE game_id = ?", (game_id,)).fetchall()[0][0]
            if bool(result):
                return result
            else:
                return 0

    # проверить регистрацию
    def registration_exists(self, user_id, game_id):
        result = self.cursor.execute('SELECT * FROM registration WHERE user_id = ? AND game_id = ?', (user_id, game_id)).fetchall()
        return bool(len(result))

    # получить все регистрации на игру
    def get_registration(self, game_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM registration WHERE game_id = ?", (game_id,)).fetchall()
    
    # получить игры, на которые зарегистрирвоан юзер
    def get_user_registration(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT button FROM game WHERE id IN (SELECT game_id FROM registration WHERE user_id = ?)", (user_id,)).fetchall()

    # удалить регистрацию
    def del_registration(self, user_id, game_id):
        with self.connection:
            print(f'user {user_id} is no longer registered for game {game_id}')
            self.cursor.execute("DELETE FROM registration WHERE user_id = ? AND game_id = ?", (user_id, game_id))

#db = Database('database.db')
#print(db.subscriber_exists(227184505))