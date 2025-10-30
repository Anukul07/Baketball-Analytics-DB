from curl_cffi.requests import Session
from bs4 import BeautifulSoup 
import time

class StatsScraper:
    """
    Scrapes team and player data from basketball-reference.com
    using curl_cffi to impersonate a browser.
    """
    def __init__(self, base_url="https://www.basketball-reference.com"):
        self.base_url = base_url
        self.session = Session(impersonate="chrome110")
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        })

    def _fetch_page(self, url):
        """(Private) Fetches HTML with error handling and a polite delay."""
        try:
            time.sleep(1) 
            response = self.session.get(url, timeout=10)
            response.raise_for_status() 
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_playoff_teams(self, season_year=2025):
        """
        Scrapes Level 1: The main NBA standings page.
        (This function is correct and finds visible tables)
        """
        print(f"Scraping Standings page for {season_year} playoff teams...")
        standings_url = f"{self.base_url}/leagues/NBA_{season_year}.html"
        
        html = self._fetch_page(standings_url)
        if not html:
            return [] 

        soup = BeautifulSoup(html, 'html.parser')
        playoff_teams = []
        
        table_ids = ['confs_standings_E', 'confs_standings_W']
        tables = soup.find_all('table', id=table_ids)
        
        if not tables:
            print("Error: Could not find standings tables.")
            return []
                
        for table in tables:
            for row in table.find('tbody').find_all('tr'):
                team_cell = row.find('th', {'data-stat': 'team_name'})
                if not team_cell:
                    continue
                
                if team_cell.text.strip().endswith('*'):
                    team_link_tag = team_cell.find('a')
                    
                    if team_link_tag:
                        team_name = team_link_tag.text
                        team_url_suffix = team_link_tag['href']
                        team_abbr = team_url_suffix.split('/')[2]
                        
                        team_data = {
                            'name': team_name,
                            'abbr': team_abbr,
                            'url': self.base_url + team_url_suffix
                        }
                        playoff_teams.append(team_data)
                        
        print(f"Found {len(playoff_teams)} playoff teams.")
        return playoff_teams
    
    # --- THIS FUNCTION WAS CORRECT (BUT HAD A TYPO I'VE FIXED) ---
    def get_player_links(self, team_roster_url):
        """
        Scrapes Level 2: A team's roster page.
        """
        print(f"  Scraping Roster page: {team_roster_url}")
        html = self._fetch_page(team_roster_url)
        if not html:
            return

        soup = BeautifulSoup(html, 'html.parser')
        
        # --- Do a direct find for the table ---
        table = soup.find('table', id='roster')
        
        if not table:
            print(f"    Could not find roster table on page.")
            return

        for row in table.find('tbody').find_all('tr'):
            player_cell = row.find('td', {'data-stat': 'player'})
            if not player_cell:
                continue
            
            player_link = player_cell.find('a')
            
            # --- THE FIX WAS HERE: 'pos' is lowercase in the HTML ---
            position_cell = row.find('td', {'data-stat': 'pos'}) 
            
            if player_link and position_cell:
                player_data = {
                    'name': player_link.text,
                    'url': self.base_url + player_link['href'],
                    'position': position_cell.text
                }
                yield player_data # Use 'yield' to return all players

    # --- ADD THIS NEW HELPER FUNCTION ---
    def _parse_stats_table(self, table_soup):
        """
        (Private) Helper to parse a "Per Game" or "Playoffs Per Game" table.
        Returns a dictionary where:
        key = player_name
        value = {stats_dictionary}
        """
        player_stats_map = {}
        if not table_soup:
            return player_stats_map # Return empty map if no table (e.g., no playoffs)

        for row in table_soup.find('tbody').find_all('tr'):
            player_cell = row.find('td', {'data-stat': 'name_display'})
            # We skip rows that aren't player rows
            if not player_cell or not player_cell.find('a'):
                continue 
            
            player_name = player_cell.text.strip()
            
            # Helper to safely find and convert stats
            def get_stat(stat_name):
                cell = row.find('td', {'data-stat': stat_name})
                # Use 'or 0' to handle empty strings (like for a player with 0 blocks)
                return float(cell.text or 0) if cell else 0.0

            stats = {
                'points': get_stat('pts_per_g'),
                'assists': get_stat('ast_per_g'),
                'offensive_rebounds': get_stat('orb_per_g'),
                'defensive_rebounds': get_stat('drb_per_g'),
                'steals': get_stat('stl_per_g'),
                'blocks': get_stat('blk_per_g')
            }
            player_stats_map[player_name] = stats
            
        return player_stats_map

    # --- ADD THIS NEW MAIN SCRAPING FUNCTION ---
    def scrape_team_stats(self, team_page_url):
        """
        Scrapes Level 3: The stats tables from the team page.
        
        Returns:
        (reg_stats_map, playoff_stats_map)
        """
        print(f"  Scraping Stats tables from: {team_page_url}")
        html = self._fetch_page(team_page_url)
        if not html:
            return {}, {} # Return two empty dicts

        soup = BeautifulSoup(html, 'html.parser')

        # --- 1. Get Regular Season Stats ---
        # We find the table that is *not* commented out
        reg_table_soup = soup.find('table', id='per_game_stats')
        reg_stats_map = self._parse_stats_table(reg_table_soup)

        # --- 2. Get Playoff Stats ---
        # The playoff table is ALSO visible, just in a different div
        playoff_table_soup = soup.find('table', id='per_game_stats_post')
        playoff_stats_map = self._parse_stats_table(playoff_table_soup)
        
        return reg_stats_map, playoff_stats_map