import json
import os
from datetime import datetime, timedelta
from playerdb import PlayerDB
from table2ascii import table2ascii as t2a

class Game():
    def __init__(self, name, active_player, turn_number, last_updated, game_note=""):
        self.name = str(name)
        self.active_player = str(active_player)
        self.turn_number = str(turn_number)
        self.last_updated = str(last_updated)
        self.game_note = str(game_note)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'active_player': self.active_player,
            'turn_number': self.turn_number,
            'last_updated': self.last_updated,
            'game_note': self.game_note
        }

    @classmethod
    def from_dict(cls, name, data):
        return cls(name, data['active_player'], data['turn_number'], data['last_updated'], data['game_note'])

    def is_stale(self, stale_timer=36) -> bool:
        stale_timer = timedelta(hours=stale_timer)
        age = datetime.now() - datetime.strptime(self.last_updated, '%Y-%m-%dT%H:%M:%S.%f')
        return age > stale_timer
    
    def age_formated(self) -> str:   
        delta = datetime.now() - datetime.strptime(self.last_updated, '%Y-%m-%dT%H:%M:%S.%f')
        if delta < timedelta(seconds=60):
            #under a min
            return "<1m"
        elif delta < timedelta(hours=1):
            #under an hour, show min
            return str(divmod(delta.seconds, 60)[0]) + "m"
        elif delta < timedelta(days=1):
            #under a day, show hour
            return str(divmod(delta.seconds, 3600)[0]) + "h"
        else:
            #Show Days
            return str(delta.days) + "d"
        
    def data_formated(self) -> list:
        return [self.name, self.active_player, self.turn_number, self.age_formated()]

class GameDB():
    def __init__(self, file_path: str): 
        self.file_path = file_path
        self.games = self.load_games()

    def __str__(self):
        return self.make_table()

    def load_games(self) -> dict:
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                return {name: Game.from_dict(name, game_data) for name, game_data in data.items()}
        return {}

    def save_games(self) -> None:
        with open(self.file_path, 'w') as file:
            json.dump({name: game.to_dict() for name, game in self.games.items()}, file, indent=4)

    def add_game(self, name, active_player, turn_number, game_note="") -> None:
        if name not in self.games:
            self.games[name] = Game(str(name), str(active_player), str(turn_number), datetime.now().isoformat(), str(game_note))
            self.save_games()

    def update_game(self, name, active_player=None, turn_number=None, game_note=None) -> None:
        if name in self.games:
            game = self.games[name]
            if active_player is not None:
                game.active_player = str(active_player)
            if turn_number is not None:
                game.turn_number = str(turn_number)
            if game_note is not None:
                game.game_note = str(game_note)
            game.last_updated = datetime.now().isoformat()
            self.save_games()

    def update_note_game(self, name, game_note) -> None:
        if name in self.games:
            game = self.games[name]
            game.game_note = str(game_note)
            self.save_games()

    def remove_game(self, name) -> None:
        if name in self.games:
            del self.games[name]
            self.save_games()

    def get_game(self, name) -> Game:
        return self.games.get(name)

    def get_all_games(self) -> dict:
        return self.games
    
    def get_all_games_formated(self) -> list:
        return [game.data_formated() for game in self.games.values()]
    
    def make_table(self, game_list:list = None, column_widths: list = []) -> str:
        if game_list is None:
            game_list = self.get_all_games_formated()
        if len(column_widths) == 4:
            for game in game_list:
                for i in range(4):
                    game[i] = game[i][:column_widths[i]]   
        return t2a(header=["Game", "Player", "Turn", "Age"], body=game_list, column_widths=column_widths)

    def get_stale_games(self, stale_timer=36) -> list:
        return [game for game in self.games.values() if game.is_stale(stale_timer)]
    
    def get_games_with_notes(self) -> list:
        return [game for game in self.games.values() if len(game.game_note) > 0]
        
    def ping_gen(self, game_name, playerDB: PlayerDB) -> str:        
    # Generate ping
        game = self.get_game(game_name)
        discord_id = playerDB.get_discord_id_by_name(game.active_player)
        if discord_id == None:
            message = "**{}** Update! Turn {} for {}".format(game_name, 
                                                            str(game.turn_number), 
                                                            str(game.active_player))
        else:
            message = "<@{}>, Turn {} for {}".format(str(discord_id), 
                                                    str(game.turn_number), 
                                                    str(game_name))
        if game.game_note != "":
            message = "{}\nNote: {}".format(message,game.game_note)
            
        return message