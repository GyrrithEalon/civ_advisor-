import json
import os
from table2ascii import table2ascii as t2a

class Player:
    def __init__(self, discord_id: str, name: str):
        self.discord_id = str(discord_id)
        self.name = str(name)

    def __str__(self):
        return f"{self.discord_id} {self.name}"
    
    def to_list(self):
        return [self.discord_id, self.name]

class PlayerDB():
    def __init__(self, file_path:str):
        self.file_path = file_path
        self.players = self.load_players()

    def __str__(self):
        return self.make_table()

    def load_players(self) -> dict:
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                return {str(discord_id): Player(str(discord_id), str(name)) for discord_id, name in data.items()}
        return {}

    def save_players(self) -> None:
        with open(self.file_path, 'w') as file:
            json.dump({str(discord_id): str(player.name) for discord_id, player in self.players.items()}, file, indent=4)

    def add_player(self, discord_id: str, name: str):
        if discord_id not in self.players:
            self.players[str(discord_id)] = Player(str(discord_id), str(name))
            self.save_players()

    def remove_player(self, discord_id:str):
        if discord_id in self.players:
            del self.players[discord_id]
            self.save_players()

    def update_player(self, discord_id:str, name:str):
        if discord_id in self.players:
            self.players[discord_id].name = name
            self.save_players()

    def get_all_players(self)->dict:
        return self.players

    def get_name_by_discord_id(self, discord_id:str) -> str:
        try:
            return self.players[discord_id].name
        except:
            return None

    def get_discord_id_by_name(self, name:str) -> str:
        for discord_id, player in self.players.items():
            if player.name == name:
                return player.discord_id
        return None

    def make_table(self):
        data = [player.to_list() for player in self.players.values()]
        return t2a(header=["Discord ID", "Name"], body=data, column_widths=None)