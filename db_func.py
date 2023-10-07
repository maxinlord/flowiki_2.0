
import sqlite3
from utils import is_float, to_str, get_date_now


class BotDB:

    def __init__(self, db_file: str):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()

    # Проверяем, есть ли юзер в базе
    def user_exists(self, id_user: int | str):

        result = self.cur.execute("SELECT `id` \
                                  FROM `users` \
                                  WHERE `id` = ?", (id_user,))
        return bool(len(result.fetchall()))

    def add_new_text(self, unique_value: str):
        self.cur.execute("INSERT INTO `message_texts` \
                         (`name`) VALUES (?)", (unique_value,))
        return self.conn.commit()

    def add_new_button(self, unique_value: str):
        self.cur.execute("INSERT INTO `button_texts` \
                         (`name`) VALUES (?)", (unique_value,))
        return self.conn.commit()

    def add_user(self, id_user: int | str):  # Добавляем юзера в базу
        date = get_date_now()
        self.cur.execute("INSERT INTO `users` \
                         (`id`, 'date_reg') VALUES (?, ?)", (id_user, date))
        return self.conn.commit()

    # Добавляем любое значение к числу в БД
    def add_value(self, key: str, 
                  where: str, 
                  meaning: str, 
                  table: str = 'users', 
                  value: str | int | float = 0):

        result = self.cur.execute(f"SELECT {key}\
                                    FROM {table}\
                                    WHERE {where} = ?", (meaning,))
        self.cur.execute(f"UPDATE {table} \
                           SET {key} = ? \
                           WHERE {where} = ?", (value + result.fetchone()[0], meaning))
        return self.conn.commit()

    def get_value(self, key: str, where: str, meaning: str, table: str = 'users'):

        result = self.cur.execute(f"SELECT {key} \
                                    FROM {table} \
                                    WHERE {where} = ?", (meaning,))
        return result.fetchone()[0]

    def get_all_line_key(self, key: str, 
                         table: str = 'users', 
                         order: str = None, 
                         sort_by: str = 'DESC'):
        query = f"SELECT {key} \
                  FROM {table}"
        if order is not None:
            query += f" ORDER BY {order} {sort_by}"
        result = self.cur.execute(query).fetchall()
        keys_list = key.split(',')
        if len(keys_list) == 1:
            return list(map(lambda x: x[0], result))
        result_list = []
        for piece in result:
            piece_dict = {keys_list[ind]: particle for ind,
                          particle in enumerate(piece)}
            result_list.append(piece_dict)
        return result_list

    def delete(self, where: str, meaning: str, table: str = 'users'):
        self.cur.execute(f'DELETE FROM {table} \
                           WHERE {where} = ?', (meaning,))
        return self.conn.commit()

    def update_value(self, key: str, 
                     where: str, 
                     meaning: str, 
                     table: str = 'users', 
                     value: str | int | float = ''):
        self.cur.execute(f'UPDATE {table} \
                           SET {key} = "{value}" \
                           WHERE {where} = ?', (meaning,))
        return self.conn.commit()

    def close(self, conn):
        conn.close()
    

