import sqlite3
import pandas as pd

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

result = cursor.execute('SELECT * FROM user').fetchall()
df = pd.DataFrame(result).drop(columns = [0],axis = 1)
df.columns = ['user_id', 'username', 'name', 'phone_number']
df.to_excel('users.xlsx')