from fastapi import FastAPI, HTTPException
from vlr_scraper import VLRScraper

app = FastAPI(
    title="VLR API",
    description="API for scraping VLR.gg data including players, teams, and matches",
    version="1.0.0"
)

# Initialize the scraper
scraper = VLRScraper()

@app.get("/")
def read_root():
    return {"message": "VLR API - Valorant data from vlr.gg"}

@app.get("/matches")
def get_matches():
    """Get recent matches from VLR"""
    try:
        matches = scraper.get_matches()
        return {
            "success": True,
            "count": len(matches),
            "matches": matches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching matches: {str(e)}")

@app.get("/matches/{match_id}")
def get_match_details(match_id: str):
    """Get detailed information about a specific match"""
    try:
        match_url = f"{scraper.base_url}/match/{match_id}"
        match_details = scraper.get_match_details(match_url)
        
        if not match_details:
            raise HTTPException(status_code=404, detail="Match not found")
        
        return {
            "success": True,
            "match": match_details
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching match details: {str(e)}")

@app.get("/players/{region}")
def get_players(region: str):
    """Get players from a specific region (americas, emea, apac, china)"""
    valid_regions = ['americas', 'emea', 'apac', 'china']
    
    if region.lower() not in valid_regions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid region. Must be one of: {', '.join(valid_regions)}"
        )
    
    try:
        players = scraper.get_players(region)
        
        if players is None:
            raise HTTPException(status_code=404, detail=f"No players found for region: {region}")
        
        return {
            "success": True,
            "region": region,
            "count": len(players),
            "players": players
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching players: {str(e)}")

@app.get("/player/{vlr_id}")
def get_player(vlr_id: int):
    """Get detailed information about a specific player"""
    try:
        player_details = scraper.get_player(vlr_id)
        
        if not player_details:
            raise HTTPException(status_code=404, detail=f"Player with ID {vlr_id} not found")
        
        return {
            "success": True,
            "player": player_details
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching player details: {str(e)}")

@app.get("/teams/{region}")
def get_teams(region: str):
    """Get teams from a specific region (americas, emea, apac, china, global)"""
    valid_regions = ['americas', 'emea', 'apac', 'china', 'global']
    
    if region.lower() not in valid_regions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid region. Must be one of: {', '.join(valid_regions)}"
        )
    
    try:
        teams = scraper.get_teams(region)
        
        if teams is None:
            raise HTTPException(status_code=404, detail=f"No teams found for region: {region}")
        
        return {
            "success": True,
            "region": region,
            "count": len(teams),
            "teams": teams
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching teams: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "VLR API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)