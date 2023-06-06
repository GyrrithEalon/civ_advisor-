CREATE TABLE IF NOT EXISTS players (
    discord_id VARCHAR(25) UNIQUE,
    civ_name VARCHAR(25) PRIMARY KEY 
    );
    
CREATE TABLE IF NOT EXISTS games (
    game VARCHAR(20) PRIMARY KEY, 
    discord_id VARCHAR(20) NOT NULL
    );
