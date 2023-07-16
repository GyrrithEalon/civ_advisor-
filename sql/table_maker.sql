CREATE TABLE IF NOT EXISTS players (
    discord_id VARCHAR(25) UNIQUE,
    civ_name VARCHAR(25) PRIMARY KEY 
    );
    
CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_name VARCHAR(150) NOT NULL, 
    civ_name VARCHAR(50) NOT NULL,
    turn_number INTEGER NOT NULL
    );

CREATE TABLE IF NOT EXISTS game_note (
    game_id INTEGER UNIQUE,
    note VARCHAR(25) PRIMARY KEY 
    );