DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS regular_season_stats CASCADE;
DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS playoff_stats CASCADE;

CREATE TABLE teams(
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    team_abbreviation VARCHAR(10) UNIQUE,
    is_playoff_team BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE players(
    player_id SERIAL PRIMARY KEY,
    player_name VARCHAR(255) NOT NULL,
    position VARCHAR(50),
    team_id INTEGER REFERENCES teams(team_id),
    UNIQUE(player_id, team_id)
);

CREATE TABLE regular_season_stats (
    stat_id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(player_id),
    season_year VARCHAR(10) NOT NULL,
    avg_points REAL DEFAULT 0,
    avg_assists REAL DEFAULT 0,
    avg_offensive_rebounds REAL DEFAULT 0,
    avg_defensive_rebounds REAL DEFAULT 0,
    avg_steals REAL DEFAULT 0,
    avg_blocks REAL DEFAULT 0,
    UNIQUE(player_id, season_year) 
);

CREATE TABLE playoff_stats (
    stat_id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(player_id),
    season_year VARCHAR(10) NOT NULL,
    avg_points REAL DEFAULT 0,
    avg_assists REAL DEFAULT 0,
    avg_offensive_rebounds REAL DEFAULT 0,
    avg_defensive_rebounds REAL DEFAULT 0,
    avg_steals REAL DEFAULT 0,
    avg_blocks REAL DEFAULT 0,
    UNIQUE(player_id, season_year) 
);