import os
import psycopg2
from dotenv import load_dotenv

def get_db_connection():
    """
    Connects to the PostgreSQL database using credentials from .env
    """ 
    load_dotenv(dotenv_path='../.env') 
    
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("✅ Database connection successful.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

def init_database():
    """
    Initializes the database by running the schema.sql file.
    This will create all the necessary tables.
    """
    conn = get_db_connection()
    if conn is None:
        print("Could not connect to database. Aborting initialization.")
        return

    try:
        with conn.cursor() as cursor:
            with open('../sql/schema.sql', 'r') as f:
                sql_script = f.read()
            cursor.execute(sql_script)
            conn.commit()
            print("✅ Database tables created successfully from schema.sql.")

    except (psycopg2.Error, IOError) as e:
        print(f"Error initializing database: {e}")
        conn.rollback()

    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

def get_or_create_team(conn, team_name, team_abbr, is_playoff=False):
    """
    Finds a team by abbreviation. If it doesn't exist, creates it.
    Returns the team's primary key (team_id).
    """
    with conn.cursor() as cursor:
        cursor.execute("SELECT team_id FROM teams WHERE team_abbreviation = %s", (team_abbr,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            print(f"    Adding new team to DB: {team_name}")
            cursor.execute(
                """
                INSERT INTO teams (team_name, team_abbreviation, is_playoff_team) 
                VALUES (%s, %s, %s) 
                RETURNING team_id
                """,
                (team_name, team_abbr, is_playoff)
            )
            team_id = cursor.fetchone()[0]
            conn.commit() 
            return team_id

def get_or_create_player(conn, player_name, position, team_id):
    """
    Finds a player by name and team. If they don't exist, creates them.
    Returns the player's primary key (player_id).
    """
    with conn.cursor() as cursor:
        cursor.execute("SELECT player_id FROM players WHERE player_name = %s AND team_id = %s", (player_name, team_id))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            print(f"      Adding new player to DB: {player_name}")
            cursor.execute(
                """
                INSERT INTO players (player_name, position, team_id) 
                VALUES (%s, %s, %s) 
                RETURNING player_id
                """,
                (player_name, position, team_id)
            )
            player_id = cursor.fetchone()[0]
            conn.commit()
            return player_id

def add_regular_season_stats(conn, player_id, season_year, stats_dict):
    """
    Adds a player's regular season stats to the database.
    Uses ON CONFLICT to avoid duplicates if run multiple times.
    """
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                """
                INSERT INTO regular_season_stats (
                    player_id, season_year, avg_points, avg_assists, 
                    avg_offensive_rebounds, avg_defensive_rebounds, 
                    avg_steals, avg_blocks
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (player_id, season_year) DO NOTHING;
                """,
                (
                    player_id, season_year, stats_dict['points'], stats_dict['assists'],
                    stats_dict['offensive_rebounds'], stats_dict['defensive_rebounds'],
                    stats_dict['steals'], stats_dict['blocks']
                )
            )
        except Exception as e:
            print(f"Error inserting reg stats for player_id {player_id}: {e}")
            conn.rollback()


def add_playoff_stats(conn, player_id, season_year, stats_dict):
    """
    Adds a player's playoff stats to the database.
    Uses ON CONFLICT to avoid duplicates.
    """
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                """
                INSERT INTO playoff_stats (
                    player_id, season_year, avg_points, avg_assists, 
                    avg_offensive_rebounds, avg_defensive_rebounds, 
                    avg_steals, avg_blocks
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (player_id, season_year) DO NOTHING;
                """,
                (
                    player_id, season_year, stats_dict['points'], stats_dict['assists'],
                    stats_dict['offensive_rebounds'], stats_dict['defensive_rebounds'],
                    stats_dict['steals'], stats_dict['blocks']
                )
            )
        except Exception as e:
            print(f"    Error inserting playoff stats for player_id {player_id}: {e}")
            conn.rollback()
                   
if __name__ == "__main__":
    print("Running database initialization...")
    init_database()