import sqlite3, os

if os.name != 'nt':
    app_path_divider = '/'
else:
    app_path_divider = '\\'
root_dir = os.path.dirname(__file__) + app_path_divider
db_file = root_dir + app_path_divider + 'db' + app_path_divider + 'tg_epic_sql.db'

def set_db():
    try:
        sqliteConnection = sqlite3.connect(db_file)
        cursor = sqliteConnection.cursor()
        sql_query_list = []
        sql_query_list.append('CREATE TABLE IF NOT EXISTS Subscribers (ChatID INT PRIMARY KEY)')
        sql_query_list.append('CREATE TABLE IF NOT EXISTS Current_Games (RecordID INT PRIMARY KEY, Title VARCHAR(255), Description VARCHAR(255), ImagePath VARCHAR(255), EndDate VARCHAR(255))')
        sql_query_list.append('CREATE TABLE IF NOT EXISTS Upcoming_Games (RecordID INT PRIMARY KEY, Title VARCHAR(255), Description VARCHAR(255), ImagePath VARCHAR(255), StartDate VARCHAR(255), EndDate VARCHAR(255))')
        sql_query_list.append('CREATE TABLE IF NOT EXISTS Games_Tags (RecordID INT PRIMARY KEY, Title VARCHAR(255), Tag VARCHAR(255))')
        for query in sql_query_list:
            cursor.execute(query)
        sql_query = 'SELECT name FROM sqlite_master WHERE type=\'table\';'
        cursor.execute(sql_query)
    except sqlite3.Error as e:
        print(e)
    finally:
        if sqliteConnection:
            sqliteConnection.close()

def add_subscriber(chat_id_int):
    sqliteConnection = sqlite3.connect(db_file)
    cursor = sqliteConnection.cursor()
    sql_query = f"INSERT INTO Subscribers (ChatID) VALUES ({chat_id_int})"
    cursor.execute(sql_query)
    sqliteConnection.commit()
    sqliteConnection.close()

def delete_subscriber(chat_id_int):
    sqliteConnection = sqlite3.connect(db_file)
    cursor = sqliteConnection.cursor()
    sql_query = f"DELETE FROM Subscribers WHERE ChatID = {chat_id_int}"
    cursor.execute(sql_query)
    sqliteConnection.commit()
    sqliteConnection.close()

def check_subscriber(chat_id_int):
    sqliteConnection = sqlite3.connect(db_file)
    cursor = sqliteConnection.cursor()
    sql_query = f"SELECT ChatID FROM Subscribers WHERE ChatID = {chat_id_int}"
    cursor.execute(sql_query)
    if cursor.fetchone():
        print(f"[DEBUG] chat {chat_id_int} is a subscriber")
        sqliteConnection.commit()
        sqliteConnection.close()
        return True
    else:
        print(f"[DEBUG] chat {chat_id_int} is not a subscriber")
        sqliteConnection.commit()
        sqliteConnection.close()
        return False

def get_all_subscribers():
    sqliteConnection = sqlite3.connect(db_file)
    cursor = sqliteConnection.cursor()
    check_sql_query = 'SELECT ChatID FROM Subscribers'
    cursor.execute(check_sql_query)
    sqliteConnection.commit()
    subscribers_list = []
    for chat_id in cursor:
        subscribers_list.append(chat_id[0])
    return subscribers_list

def check_games_data(title):
    sqliteConnection = sqlite3.connect(db_file)
    cursor = sqliteConnection.cursor()
    check_sql_query = 'SELECT Title FROM Current_Games'
    cursor.execute(check_sql_query)
    sqliteConnection.commit()
    existing_game_list = []
    for existing_title in cursor:
        existing_game_list.append(existing_title[0])
    if title not in existing_game_list:
        sqliteConnection.close()
        print('[INFO] games were changed')
        return True
    else:
        sqliteConnection.close()
        print('[INFO] games were not changed')
        return False

def clean_games_data():
    sqliteConnection = sqlite3.connect(db_file)
    cursor = sqliteConnection.cursor()
    check_sql_query_list = ['DELETE FROM Current_Games', 'DELETE FROM Upcoming_Games', 'DELETE FROM Games_Tags']
    for check_sql_query in check_sql_query_list:
        cursor.execute(check_sql_query)
        sqliteConnection.commit()
    sqliteConnection.close()

def update_current_game_data(title,description,image_path,end_offer_date):
    sqliteConnection = sqlite3.connect(db_file)
    cursor = sqliteConnection.cursor()
    sql_query = 'INSERT INTO Current_Games (Title,Description,EndDate,ImagePath) VALUES (?, ?, ?, ?)'
    data_tuple = (title, description, end_offer_date, image_path)
    cursor.execute(sql_query, data_tuple)
    sqliteConnection.commit()
    sqliteConnection.close()

def update_upcoming_game_data(title,description,image_path,start_offer_date,end_offer_date):
    sqliteConnection = sqlite3.connect(db_file)
    cursor = sqliteConnection.cursor()
    sql_query = 'INSERT INTO Upcoming_Games (Title,Description,StartDate,EndDate,ImagePath) VALUES (?, ?, ?, ?, ?)'
    data_tuple = (title, description, start_offer_date, end_offer_date, image_path)
    cursor.execute(sql_query, data_tuple)
    sqliteConnection.commit()
    sqliteConnection.close()

def update_game_tags(title,tag_list):
    sqliteConnection = sqlite3.connect(db_file)
    cursor = sqliteConnection.cursor()
    for tag in tag_list:
        sql_query = 'INSERT INTO Games_Tags (Title,Tag) VALUES (?, ?)'
        data_tuple = (title, tag)
        cursor.execute(sql_query, data_tuple)
        sqliteConnection.commit()
    sqliteConnection.close()

def get_current_game_data():
    sqliteConnection = sqlite3.connect(db_file)
    game_cursor = sqliteConnection.cursor()
    game_sql_query = 'SELECT Title, Description, ImagePath, EndDate FROM Current_Games'
    game_cursor.execute(game_sql_query)
    sqliteConnection.commit()
    image_list = []
    game_data_list = []
    for game in game_cursor:
        image_list.append(game[2])
        tag_list = []
        tag_cursor = sqliteConnection.cursor()
        tag_sql_query = f"SELECT Tag FROM Games_Tags WHERE Title = \'{game[0]}\'"
        tag_cursor.execute(tag_sql_query)
        for tag in tag_cursor:
            tag_list.append(tag[0])
        game_data = {'Title': game[0], 'Description': game[1], 'EndDate': game[3], 'Tag': tag_list}
        game_data_list.append(game_data)
    sqliteConnection.commit()
    sqliteConnection.close()
    return game_data_list, image_list

def get_upcoming_game_data():
    sqliteConnection = sqlite3.connect(db_file)
    game_cursor = sqliteConnection.cursor()
    game_sql_query = 'SELECT Title, Description, ImagePath, StartDate, EndDate FROM Upcoming_Games'
    game_cursor.execute(game_sql_query)
    sqliteConnection.commit()
    image_list = []
    game_data_list = []
    for game in game_cursor:
        image_list.append(game[2])
        tag_list = []
        tag_cursor = sqliteConnection.cursor()
        tag_sql_query = f"SELECT Tag FROM Games_Tags WHERE Title = \'{game[0]}\'"
        tag_cursor.execute(tag_sql_query)
        for tag in tag_cursor:
            tag_list.append(tag[0])
        game_data = {'Title': game[0], 'Description': game[1], 'StartDate': game[3], 'EndDate': game[4], 'Tag': tag_list}
        game_data_list.append(game_data)
    sqliteConnection.commit()
    sqliteConnection.close()
    return game_data_list, image_list

def print_data():
    print('[DEBUG] current games:')
    sqliteConnection = sqlite3.connect(db_file)
    cursor = sqliteConnection.cursor()
    check_sql_query = 'SELECT Title FROM Current_Games'
    cursor.execute(check_sql_query)
    sqliteConnection.commit()
    for title in cursor:
        print(f'  {title[0]}')
    print('[DEBUG] upcoming games:')
    sqliteConnection = sqlite3.connect(db_file)
    cursor = sqliteConnection.cursor()
    check_sql_query = 'SELECT Title FROM Upcoming_Games'
    cursor.execute(check_sql_query)
    sqliteConnection.commit()
    for title in cursor:
        print(f'  {title[0]}')