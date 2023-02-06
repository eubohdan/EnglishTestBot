import sqlite3 as sq


def start_db():
    with sq.connect('data.db') as con:
        cur = con.cursor()
        print('[INFO] SQLite database was connected.')
        cur.execute('CREATE TABLE IF NOT EXISTS placement_test (number INTEGER, level TEXT, question TEXT, a TEXT, b TEXT, c TEXT, d TEXT, correct TEXT, rule TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER, first_name TEXT, last_name TEXT, username TEXT, score1 INTEGER, score2 INTEGER, score3 INTEGER, score4 INTEGER, reg_date TEXT, last_date TEXT)')
        cur.close()


def new_user(user_id: int, first_name: str | None, last_name: str | None, username: str | None, reg_date: str) -> None:
    with sq.connect('data.db') as con:
        cur = con.cursor()
        result = cur.execute(f'''SELECT "user_id" FROM users WHERE "user_id" = {user_id}''').fetchone()
        if result is None:
            cur.execute('INSERT INTO users (user_id, first_name, last_name, username, reg_date, last_date) VALUES (?, ?, ?, ?, ?, ?)', (user_id, first_name, last_name, username, reg_date, reg_date))
        cur.close()


def get_questions(level: int) -> dict:
    with sq.connect('data.db') as con:
        cur = con.cursor()
        result = cur.execute(f'''SELECT number, question, a, b, c, d, correct, rule, level FROM placement_test WHERE "level" = "{level}"''').fetchall()
        cur.close()
    results_dict = {}
    for i in range(len(result)):
        result[i] = [j if j is not None else 0 for j in result[i]]
        results_dict[i + 1] = {'number': i + 1, 'question': result[i][1], 'a': result[i][2], 'b': result[i][3], 'c': result[i][4], 'd': result[i][5], 'correct': result[i][6], 'rule': result[i][7], 'level': result[i][8]}
    return results_dict


def get_illustrations() -> dict:
    with sq.connect('data.db') as con:
        cur = con.cursor()
        result = cur.execute(f'''SELECT question_number, photo_id FROM illustrations''').fetchall()
        cur.close()
    result_dict = {}
    for item in result:
        result_dict[item[0]] = item[1]
    return result_dict


def set_answers(level: str, score: int, user_id: int, last_date: str) -> None:
    unit = f"score{int(level) + 1}"
    with sq.connect('data.db') as con:
        cur = con.cursor()
        cur.execute(f'''UPDATE users SET {unit} = "{score}", last_date = "{last_date}" WHERE user_id = {user_id}''')


def get_answers(level: str) -> list:
    with sq.connect('data.db') as con:
        cur = con.cursor()
        result = cur.execute(f'''SELECT correct FROM placement_test WHERE "level" = {level}''').fetchall()
        cur.close()
    return [i[0] for i in result]


def get_users_answers() -> list:
    with sq.connect('data.db') as con:
        cur = con.cursor()
        result = cur.execute(f'''SELECT user_id, score1, score2, score3, score4 FROM users''').fetchall()
        cur.close()
    return result
