import sqlite3


class BotDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()

    def user_exists(self, id_user):
        result = self.cur.execute("SELECT `id` FROM `users` WHERE `id` = ?", (id_user,))
        return bool(len(result.fetchall()))
    
    def rule_exists(self, id_user):
        result = self.cur.execute("SELECT `rule` FROM `users` WHERE `id` = ?", (id_user,))
        return result.fetchone()[0] != None

    def add_new_message_text(self, name):
        self.cur.execute("INSERT INTO `message_texts` (`name`) VALUES (?)", (name,))
        return self.conn.commit()

    def add_new_reason(self, id_user: str, reason: str, id_owner_reason: str, date: str, num):
        self.cur.execute("INSERT INTO `history_reasons` (id, reason, owner_reason, date, num) VALUES (?, ?, ?, ?, ?)", (id_user, reason, id_owner_reason, date, num))
        return self.conn.commit()


    def add_new_button_text(self, name):
        self.cur.execute("INSERT INTO `button_texts` (`name`) VALUES (?)", (name,))
        return self.conn.commit()

    def add_user(self, id_user):
        self.cur.execute("INSERT INTO `users` (`id`) VALUES (?)", (id_user,))
        return self.conn.commit()

    def add(self, key, where, meaning, table="users", num=0):
        query = f"SELECT {key} FROM {table} WHERE {where} = ?"
        result = self.cur.execute(query, (meaning,))
        query = f"UPDATE {table} SET {key} = ? WHERE {where} = ?"
        self.cur.execute(query, (num + result.fetchone()[0], meaning))
        return self.conn.commit()

    def get(self, key, where, meaning, table="users"):
        result = self.cur.execute(
            f"SELECT {key} FROM '{table}' WHERE {where} = ?", (meaning,)
        )
        return result.fetchone()[0]

    def get_all(self, key, table="users"):
        result = self.cur.execute(f"""SELECT {key} FROM {table}""")
        result = list(map(lambda x: x[0], result.fetchall()))
        return result

    def get_alls(self, keys, table="users"):
        result = self.cur.execute(f"""SELECT {keys} FROM {table}""")
        return result.fetchall()

    def get_alls_with_order(self, keys, order, table="users"):
        result = self.cur.execute(
            f"""SELECT {keys} FROM {table} ORDER BY {order} DESC"""
        )
        return result.fetchall()

    def delete(self, where, meaning, table="users"):
        self.cur.execute(f"DELETE FROM {table} WHERE {where} = ?", (meaning,))
        return self.conn.commit()

    def update(self, key, where, meaning, data, table="users"):
        self.cur.execute(
            f'UPDATE {table} SET {key} = "{data}" WHERE {where} = ?', (meaning,)
        )
        return self.conn.commit()

    def close(self, conn):
        conn.close()


flow_db = BotDB("flow.db")
