import sqlite3
import inspect
import os.path

    # if the table isnt created then create it and need only be ran once

def create_player_table(team_name):
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))
    print("DB Path :" + path)
    conn = sqlite3.connect(path + '/team_database.db')
    c = conn.cursor()
    c.execute(
        f'CREATE TABLE IF NOT EXISTS {team_name}(player_name TEXT, steam TEXT, bm TEXT)')
    conn.commit()
    c.close()
    conn.close()

    # add dynamic data to the player table

def add_player_data(team, player_name, steam='Null', bm='Null'):
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))
    conn = sqlite3.connect(path + '/team_database.db')
    c = conn.cursor()
    c.execute(f"INSERT INTO {team} (player_name, steam, bm) VALUES (?, ?, ?)",
              (player_name, steam, bm))
    print(f"Successfully added player to {team}'s team")
    conn.commit()
    c.close()
    conn.close()
    
def lookup_team(team):
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))
    conn = sqlite3.connect(path + '/team_database.db')
    c = conn.cursor()
    players = []
    players = c.execute(f"SELECT * FROM  {team}").fetchall()
    conn.commit()
    c.close()
    conn.close()
    return players

def get_teams():
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))
    conn = sqlite3.connect(path + '/team_database.db')
    c = conn.cursor()
    teams = []
    teams = c.execute("""SELECT name FROM sqlite_master  
  WHERE type='table';""").fetchall()
    conn.commit()
    c.close()
    conn.close()
    return teams

def count_rows(team):
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))
    conn = sqlite3.connect(path + '/team_database.db')
    c = conn.cursor()
    rows = 0
    rows = len(c.execute(f"SELECT * FROM {team}").fetchall())
    conn.commit()
    c.close()
    conn.close()
    return rows