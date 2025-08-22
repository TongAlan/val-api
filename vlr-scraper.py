import sys
import requests
from bs4 import BeautifulSoup
import time
import random
import json
from datetime import datetime
import os
import csv

# Bidirectional mapper class for efficient lookups
class CSVMapper:
      """
      Bidirectional mapper for CSV files with integer-string pairs.
      """
      def __init__(self):
          
          self.int_to_string = {}
          self.string_to_int = {}
          self._load_csv("/home/alanwsl/projects/val-api/resources/vlr_playerid_playerign.csv")

      def _load_csv(self, csv_file_path):
          if not os.path.exists(csv_file_path):
              raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

          with open(csv_file_path, 'r', encoding='utf-8') as file:
              reader = csv.reader(file)
              next(reader)  # Skip header row

              for row in reader:
                  if len(row) >= 2:
                      try:
                          key = int(row[0])
                          value = row[1].strip()
                          self.int_to_string[key] = value
                          self.string_to_int[value] = key
                      except ValueError:
                          continue

      def get_string(self, integer_key):
          """Get string by integer key"""
          return self.int_to_string.get(integer_key)

      def get_integer(self, string_key):
          """Get integer by string key"""
          return self.string_to_int.get(string_key)
      

class VLRScraper:
    def __init__(self):
        self.base_url = "https://www.vlr.gg"
        self.session = requests.Session()
        
        # Simple user agents pool
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]
    
    def get_page(self, url):
        """Fetch a web page with browser-like headers"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def get_matches(self):
        """Scrape matches from VLR matches page"""
        url = f"{self.base_url}/matches"
        soup = self.get_page(url)
        
        if not soup:
            return []
        
        matches = []
        
        # Look for match containers - these selectors will need adjustment
        # based on VLR's actual HTML structure
        match_containers = soup.find_all('div', class_='wf-card')
        
        for container in match_containers:
            try:
                match_data = {}
                
                # Extract match link
                match_link = container.find('a', href=True)
                if match_link:
                    match_data['url'] = self.base_url + match_link['href']
                    match_data['match_id'] = match_link['href'].split('/')[-1]
                
                # Extract team names
                team_elements = container.find_all('div', class_='text-of')
                if len(team_elements) >= 2:
                    match_data['team1'] = team_elements[0].get_text(strip=True)
                    match_data['team2'] = team_elements[1].get_text(strip=True)
                
                # Extract score
                score_element = container.find('div', class_='match-item-score')
                if score_element:
                    match_data['score'] = score_element.get_text(strip=True)
                else:
                    match_data['score'] = "TBD"
                
                # Extract tournament info
                tournament_element = container.find('div', class_='match-item-event-series')
                if tournament_element:
                    match_data['tournament'] = tournament_element.get_text(strip=True)
                
                # Extract time/status
                time_element = container.find('div', class_='match-item-time')
                if time_element:
                    match_data['time'] = time_element.get_text(strip=True)
                
                if match_data:  # Only add if we found some data
                    matches.append(match_data)
                    
            except Exception as e:
                print(f"Error parsing match: {e}")
                continue
        
        return matches
    
    def get_match_details(self, match_url):
        """Get detailed information about a specific match"""
        soup = self.get_page(match_url)
        
        if not soup:
            return None
        
        match_details = {}
        
        try:
            # Extract detailed match information
            # These selectors will need to be updated based on actual HTML
            
            # Match title/teams
            header = soup.find('div', class_='match-header')
            if header:
                teams = header.find_all('div', class_='wf-title-med')
                if len(teams) >= 2:
                    match_details['team1'] = teams[0].get_text(strip=True)
                    match_details['team2'] = teams[1].get_text(strip=True)
            
            # Match maps and scores
            maps_section = soup.find('div', class_='vm-stats-gamesnav')
            if maps_section:
                maps = []
                map_elements = maps_section.find_all('div', class_='vm-stats-gamesnav-item')
                for map_elem in map_elements:
                    map_name = map_elem.find('div', class_='map')
                    score = map_elem.find('div', class_='score')
                    if map_name and score:
                        maps.append({
                            'map': map_name.get_text(strip=True),
                            'score': score.get_text(strip=True)
                        })
                match_details['maps'] = maps
            
            # Tournament information
            breadcrumb = soup.find('div', class_='match-header-event')
            if breadcrumb:
                match_details['tournament'] = breadcrumb.get_text(strip=True)
            
        except Exception as e:
            print(f"Error parsing match details: {e}")
        
        return match_details
    
    def get_players(self, region):
        """Scrape players from VLR event stats page"""
        match region.lower():
            case 'americas':
                url = "https://www.vlr.gg/event/stats/2501/vct-2025-americas-stage-2"
            case 'emea':
                url = "https://www.vlr.gg/event/stats/2498/vct-2025-emea-stage-2"
            case 'apac':
                url = "https://www.vlr.gg/event/stats/2500/vct-2025-pacific-stage-2"
            case 'china':
                url = "https://www.vlr.gg/event/stats/2499/vct-2025-china-stage-2"
            case _:
                return None
        
        soup = self.get_page(url)
        if not soup:
            return None
            
        # Add player scraping logic here
        player_rows = soup.find_all('tr')
        players = []   
        for row in player_rows:
        # Find the player cell
            player_cell = row.find('td', class_='mod-player mod-a')

            if player_cell:
                # Extract the player link
                player_link = player_cell.find('a')

                if player_link:
                    # Get the href attribute and extract player ID
                    href = player_link.get('href')
                    if href and '/player/' in href:
                        # Extract ID from URL like "/player/36245/n4rrate"
                        player_id = href.split('/player/')[1].split('/')[0]

                        # Get player name from the div with font-weight: 700
                        name_div = player_link.find('div', style=lambda x: x and 'font-weight: 700' in x)
                        if name_div:
                            player_name = name_div.text.strip()

                            players.append({
                                "id": player_id,
                                "name": player_name
                            })

        # Sort alphabetically by in-game name (case insensitive)
        sorted_players = sorted(players, key=lambda x: x["name"].upper())

        # Print the results
        for i, player in enumerate(sorted_players, 1):
            players.append({
                "id": player["id"],
                "name": player["name"]
            })
        
        full_players_list = []
        for player in sorted_players:
            player_id = int(player['id'])
            player_details = self.get_player(player_id)
            if player_details:
                full_players_list.extend(player_details)
        return full_players_list
    
        # player_cell = soup.find('td', class_='mod-player mod-a')
        # player_link = player_cell.find('a', href=True)
        # player_url = player_link['href']  # "/player/36245/n4rrate"
        # player_id = player_url.split('/')[2]  # "36245"
        # print(player_cell)
        

    
    def get_player(self, vlr_id):
        """Get detailed information about a specific player"""
        csvmap = CSVMapper()
        player_ign = csvmap.get_string(vlr_id)
        if not player_ign:
            print(f"Player IGN '{player_ign}' not found in CSV mapping.")
            return None 
        url = f"{self.base_url}/player/{vlr_id}/{player_ign}"
        soup = self.get_page(url)
        player_details = []

        if not soup: 
            return None
        
        player_ign = soup.find('h1', class_='wf-title')
        if player_ign:
            player_ign = player_ign.get_text(strip=True)
        else:
            player_ign = "Unknown Player"
    
        
        player_name = soup.find("h2", class_="player-real-name")
        if player_name:
            player_name = player_name.get_text(strip=True)
        else:
            player_name = "Unknown"
        
        # Extract total winnings - usually the first/largest dollar amount
        money_elements = soup.find_all(string=lambda text: text and "$" in text and text.strip().startswith("$"))
        winnings = "Unknown"
        
        if money_elements:
            # The total winnings is typically the first or largest amount
            potential_winnings = []
            for elem in money_elements:
                elem_text = elem.strip()
                if elem_text.startswith("$") and "," in elem_text:  
                    potential_winnings.append(elem_text)
            
            if potential_winnings:
                # Take the first one, which is usually the total
                winnings = potential_winnings[0]
            else:
                # Fallback to the first dollar amount
                winnings = money_elements[0].strip()
        
        # top 3 most played agents in the last 60 days
        agents_table = soup.find('table', class_='wf-table')
        if agents_table:
            agents_selection = agents_table.find_all('tr')[1:4]  # Get first 3 rows
        else:
            agents_selection = []
        main_agents = []
        for agent in agents_selection:
            cols = agent.find_all('td')
            img = cols[0].find('img')
            if img:
                agent_name = img.get('alt', 'Unknown Agent')
                main_agents.append(agent_name)

        # current team
        team_div = soup.find('div', style=lambda x: x and 'font-weight: 500' in x)
        if team_div:
            team_name = team_div.get_text(strip=True)  # Gets "Cloud9"
        else:
            team_name = "Unknown"
        
        # get player origin country
        flag = soup.find('i', class_=lambda x: x and 'flag' in x)
        if flag:
            country = flag.parent.get_text(strip=True)  
        else:
            country = "Unknown"

        player_details.append({
            'vlr_id': vlr_id,
            'ign': player_ign,
            'url': url,
            'name': player_name,
            'country': country,
            'current_team': team_name,
            'winnings': winnings,
            'main_agents_last_60_days': main_agents
        })

        return player_details


    
    def get_teams(self):
        """Scrape teams from VLR rankings page"""
        url = f"{self.base_url}/rankings"
        soup = self.get_page(url)
        
        if not soup:
            return []
        
        teams = []
        
        # Look for team rankings
        team_rows = soup.find_all('tr')
        
        for row in team_rows:
            try:
                team_data = {}
                
                # Team name and link
                team_link = row.find('a', href=lambda x: x and '/team/' in x)
                if team_link:
                    team_data['name'] = team_link.get_text(strip=True)
                    team_data['url'] = self.base_url + team_link['href']
                    team_data['team_id'] = team_link['href'].split('/')[-2]  # Extract team ID
                
                # Team country
                flag = row.find('img', class_='flag')
                if flag:
                    team_data['country'] = flag.get('alt', 'Unknown')
                
                # Ranking
                rank_elem = row.find('td', class_='rank-item-rank-num')
                if rank_elem:
                    team_data['rank'] = rank_elem.get_text(strip=True)
                
                if team_data:
                    teams.append(team_data)
                    
            except Exception as e:
                print(f"Error parsing team: {e}")
                continue
        
        return teams
    
    def get_team_details(self, team_url):
        """Get detailed information about a specific team"""
        soup = self.get_page(team_url)
        
        if not soup:
            return None
        
        team_details = {}
        
        try:
            # Team name
            team_name = soup.find('h1', class_='wf-title')
            if team_name:
                team_details['name'] = team_name.get_text(strip=True)
            team_tag = soup.find('h2', class_='wf-title team-header-tag')
            if team_tag:
                team_details['tag'] = team_tag.get_text(strip=True)
            
        
                
            
            # Recent matches
            recent_matches = soup.find('div', class_='wf-card')
            if recent_matches:
                matches = []
                match_items = recent_matches.find_all('a', href=lambda x: x and '/match/' in x)[:5]
                for match in match_items:
                    matches.append({
                        'url': self.base_url + match['href'],
                        'text': match.get_text(strip=True)
                    })
                team_details['recent_matches'] = matches
            
        except Exception as e:
            print(f"Error parsing team details: {e}")
        
        return team_details
    
    def sleep(self):
        """Add delay between requests to be respectful"""
        time.sleep(random.uniform(1, 2))

# Example usage and testing
def main():
    scraper = VLRScraper()
    
    print("🎮 VLR.gg Scraper Starting...\n")
    
    # Test scraping matches
    print("📅 Fetching recent matches...")
    matches = scraper.get_matches()
    print(f"Found {len(matches)} matches")
    
    for i, match in enumerate(matches[:3]):  # Show first 3 matches
        print(f"\nMatch {i+1}:")
        for key, value in match.items():
            print(f"  {key}: {value}")
    
    scraper.sleep()
    
    # Test scraping teams
    print("\n🏆 Fetching team rankings...")
    teams = scraper.get_teams()
    print(f"Found {len(teams)} teams")
    
    for i, team in enumerate(teams[:5]):  # Show top 5 teams
        print(f"\nTeam {i+1}:")
        for key, value in team.items():
            print(f"  {key}: {value}")
    
    # Test getting detailed info (if we found a team)
    if teams and len(teams) > 0:
        scraper.sleep()
        print(f"\n🔍 Getting details for {teams[1]['name']}...")
        team_details = scraper.get_team_details(teams[1]['url'])
        if team_details:
            print("Team details:")
            for key, value in team_details.items():
                print(f"  {key}: {value}")

if __name__ == "__main__":
    # main()
    scraper = VLRScraper()
    # arg1 = int(sys.argv[1])  # Convert to integer
    # player = scraper.get_player(arg1)
    # print(json.dumps(player, indent=2))
    # regions: americas, emea, apac, china
    players = scraper.get_players('emea')
    print(json.dumps(players, indent=2))
    



    