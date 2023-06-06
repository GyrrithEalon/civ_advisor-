# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 13:14:06 2023

@author: timsargent
"""
import os
import sqlite3
from dotenv import load_dotenv




load_dotenv()
CIV_GAME_DB = os.getenv('CIV_GAME_DB')
DB_TABLES = os.getenv('DB_TABLES')


class SqlConnection():
    
    def __init__ (self, CIV_GAME_DB):
        self.con = sqlite3.connect(CIV_GAME_DB)
        self.tables = self.get_all_tables()
              
    def verify_tables(self):
        cur = self.con.cursor()
        with open("sql/table_maker.sql", "r") as sql_file:
            sql_script = sql_file.read()
            cur.executescript(sql_script)
        self.tables = self.get_all_tables()
        cur.close()
        
    def get_all_tables(self):
        cur = self.con.cursor()
        res = cur.execute("SELECT name FROM sqlite_master")
        res = res.fetchall()
        returner = []
        for tup in res:
            returner.append(tup[0])
        cur.close()
        return returner
        
    def drop_table(self, table):
        cur = self.con.cursor()
        cur.execute('DROP TABLE "{}" '.format(table.replace('"', '""')))
        self.con.commit()
        cur.close()
        return 
    
    def truncate_table(self, table):
        cur = self.con.cursor()
        cur.execute('TRUNCATE TABLE "{}" '.format(table.replace('"', '""')))
        self.con.commit()
        cur.close()
        return 
    
    def insert_player(self, discord_id, civ_name):
        cur = self.con.cursor()
        try:
            cur.execute('INSERT INTO players VALUES( ? , ?)',
                        (discord_id, civ_name))
            self.con.commit()
            cur.close()
            return True
        except:
            cur.close()
            return False
    
    def update_player(self, discord_id, civ_name):
        cur = self.con.cursor()
        try:
            cur.execute('UPDATE players SET civ_name = ? WHERE discord_id = ?',
                        (civ_name, discord_id))
            self.con.commit()
            cur.close()
            return True
        except:
            cur.close()
            return False
    
    def get_discord_id(self, civ_name):
        cur = self.con.cursor()
        res = cur.execute("SELECT * FROM players WHERE civ_name = ?",(civ_name,))
        res = res.fetchone()
        cur.close()
        return res
    
    def get_civ_name(self, discord_id):
        cur = self.con.cursor()
        res = cur.execute("SELECT * FROM players WHERE discord_id = ?",(discord_id,))
        res = res.fetchone()
        cur.close()
        return res
    
    def get_all_players(self):
        cur = self.con.cursor()
        res = cur.execute("SELECT * FROM players")
        res = res.fetchall()
        cur.close()
        return res
    
    def run_test(self):
        return None