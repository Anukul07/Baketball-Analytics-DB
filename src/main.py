import importlib
import scraper
importlib.reload(scraper)

from scraper import StatsScraper
import database as db
import time

def main():
    print("--- Starting ETL Pipeline ---")
    
    SEASON_YEAR = 2025 
    SEASON_ID_STRING = "2024-25" 
    
    scraper = StatsScraper()

    conn = db.get_db_connection()
    if conn is None:
        print("Could not connect to database. Exiting.")
        return
        
    playoff_teams = scraper.get_playoff_teams(SEASON_YEAR)

    if not playoff_teams:
        print("Could not find any playoff teams. Exiting.")
        conn.close()
        return
        
    print(f"Found {len(playoff_teams)} playoff teams.")
    
    for team in playoff_teams:
        print(f"\nProcessing team: {team['name']} ({team['abbr']})")
        
        team_id = db.get_or_create_team(
            conn, 
            team_name=team['name'], 
            team_abbr=team['abbr'], 
            is_playoff=True
        )

        player_generator = scraper.get_player_links(team['url'])
        if not player_generator:
            print(f"Could not find roster for {team['abbr']}. Skipping team.")
            continue
            
        roster_map = {} 
        
        for player in player_generator:
            player_id = db.get_or_create_player(
                conn,
                player_name=player['name'],
                position=player['position'],
                team_id=team_id
            )
            roster_map[player['name']] = player_id
            
        print(f"Processed {len(roster_map)} players.")

        print(f"Fetching stats for {team['abbr']}...")
        reg_stats_map, playoff_stats_map = scraper.scrape_team_stats(team['url'])
        
        for player_name, stats in reg_stats_map.items():
            if player_name in roster_map:
                player_id = roster_map[player_name]
                db.add_regular_season_stats(
                    conn, player_id, SEASON_ID_STRING, stats
                )

        for player_name, stats in playoff_stats_map.items():
            if player_name in roster_map:
                player_id = roster_map[player_name]
                db.add_playoff_stats(
                    conn, player_id, SEASON_ID_STRING, stats
                )
        
        try:
            conn.commit()
            print(f"Successfully saved all data for {team['abbr']}.")
        except Exception as e:
            print(f"Error committing data for team {team['abbr']}: {e}")
            conn.rollback()
    
    print("\n--- ETL Pipeline Complete ---")
    conn.close()
    print("Database connection closed.")

if __name__ == "__main__":
    main()