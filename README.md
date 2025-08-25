# VLR API 🎮

A RESTful API that scrapes and serves Valorant esports data from VLR.gg, providing comprehensive information about professional players, teams, and matches.

## 🎯 Project Objective

This project aims to democratize access to Valorant esports data by providing a clean, structured API interface for VLR.gg content. Perfect for developers building fantasy leagues, statistics dashboards, or analytical tools for the Valorant competitive scene.

## 🚀 Tech Stack

- **Backend Framework**: FastAPI (Python)
- **Web Scraping**: BeautifulSoup4 + Requests
- **Data Processing**: Python standard libraries
- **Server**: Uvicorn ASGI server
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## 📋 Prerequisites

- Python 3.8+
- pip package manager

## 🛠️ Local Setup & Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd val-api
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the API server**
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the API**
   - API Base URL: `http://localhost:8000`
   - Interactive Documentation: `http://localhost:8000/docs`
   - ReDoc Documentation: `http://localhost:8000/redoc`

## 📚 API Endpoints

### Core Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `GET` | `/` | API welcome message | None |
| `GET` | `/health` | Health check endpoint | None |

### Players

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `GET` | `/players/{region}` | Get players by region | `region`: americas, emea, apac, china |
| `GET` | `/player/{vlr_id}` | Get specific player details | `vlr_id`: VLR player ID |

### Teams

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `GET` | `/teams/{region}` | Get teams by region | `region`: americas, emea, apac, china, global |

## 📄 Example API Responses

### Get Players by Region
```bash
curl http://localhost:8000/players/americas
```

```json
{
  "success": true,
  "region": "americas",
  "count": 50,
  "players": [
    {
      "vlr_id": 36245,
      "ign": "n4rrate",
      "name": "John Smith",
      "country": "United States",
      "current_team": "Sentinels",
      "winnings": "$125,000",
      "main_agents_last_60_days": ["Jett", "Raze", "Reyna"]
    }
  ]
}
```

### Get Teams by Region
```bash
curl http://localhost:8000/teams/americas
```

```json
{
  "success": true,
  "region": "americas",
  "count": 10,
  "teams": [
    {
      "name": "Sentinels",
      "tag": "SEN",
      "region": "americas",
      "total_winnings": "$500,000",
      "url": "https://www.vlr.gg/team/2/sentinels",
      "roster": {
        "players": [
          {
            "vlr_id": 1234,
            "ign": "TenZ",
            "name": "Tyson Ngo",
            "country": "Canada",
            "is_captain": false,
            "is_active": true
          }
        ],
        "staff": []
      }
    }
  ]
}
```

## 🔧 Project Structure

```
val-api/
├── main.py              # FastAPI application
├── vlr_scraper.py       # Core scraping logic
├── requirements.txt     # Python dependencies
├── resources/           # Data resources
│   └── vlr_playerid_playerign.csv
└── README.md           # This file
```

## 🚦 Development

The API includes automatic request rate limiting and user-agent rotation to ensure respectful scraping practices. All endpoints return standardized JSON responses with success status and error handling.

## ⚠️ Important Notes

- This project is for educational and research purposes
- Respects VLR.gg's terms of service with appropriate delays between requests
- Data accuracy depends on VLR.gg's website structure and availability

## 🤝 Contributing

Feel free to submit issues and pull requests to improve the API functionality or add new endpoints.

---
