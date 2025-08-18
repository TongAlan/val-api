import requests
from bs4 import BeautifulSoup
import time
import random
import json
from datetime import datetime

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
            
            # Players
            players_section = soup.find('div', class_='team-roster')
            if players_section:
                players = []
                player_cards = players_section.find_all('div', class_='team-roster-item')
                for card in player_cards:
                    player_link = card.find('a', href=lambda x: x and '/player/' in x)
                    if player_link:
                        player_name = player_link.get_text(strip=True)
                        player_url = self.base_url + player_link['href']
                        players.append({
                            'name': player_name,
                            'url': player_url
                        })
                team_details['players'] = players
            
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
        print(f"\n🔍 Getting details for {teams[0]['name']}...")
        team_details = scraper.get_team_details(teams[0]['url'])
        if team_details:
            print("Team details:")
            for key, value in team_details.items():
                print(f"  {key}: {value}")

if __name__ == "__main__":
    main()