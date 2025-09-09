# HarmWatch - Enhanced Social Media Harm Detection System

HarmWatch is a comprehensive social media harm detection system that combines batch analysis with real-time monitoring capabilities. This enhanced version merges features from the original HarmWatch project with real-time streaming, URL analysis, and enhanced classification patterns.

## 🚀 Features

### Core Features (Original HarmWatch)
- **Batch CSV Analysis**: Upload and analyze CSV files containing social media posts
- **Privacy-Aware Processing**: Automatic ID anonymization and data cleaning
- **Multiple Harm Categories**: Detection of cyberbullying, hate speech, misinformation, scams, and more
- **Data Export**: CSV export and SQLite storage options
- **HTML Report Generation**: Comprehensive analysis reports

### New Real-Time Features (Merged from CyberShield)
- **Live WebSocket Streaming**: Real-time data ingestion and monitoring
- **URL Analysis**: Extract and analyze content from social media URLs
- **Enhanced Classification**: More comprehensive pattern matching with risk scoring
- **Real-Time Dashboard**: Live charts and monitoring interface
- **Bridge Server**: FastAPI-based server for data ingestion

## 🏗️ Architecture

```
harmwatch_starter/
├── app/
│   ├── app.py                 # Main batch analysis interface
│   ├── classify.py            # Enhanced classification engine
│   ├── bridge.py              # Real-time WebSocket bridge server
│   ├── url_analyzer.py        # URL content extraction utility
│   ├── simulate_ingest.py     # Data ingestion simulator
│   ├── pages/
│   │   └── 1_Live_Dashboard.py # Real-time monitoring interface
│   ├── preprocess.py          # Text preprocessing utilities
│   ├── report.py              # HTML report generation
│   └── storage.py             # Database operations
├── data/
│   └── sample_posts.csv       # Sample data for testing
└── requirements.txt            # Python dependencies
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd harmwatch_starter
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python -c "import streamlit, fastapi, websockets; print('All dependencies installed!')"
   ```

## 🚀 Usage

### 1. Batch Analysis (Original Feature)

Run the main application for batch CSV analysis:

```bash
cd app
streamlit run app.py
```

Upload a CSV file with at least a `text` column and analyze for harmful content.

### 2. Real-Time Monitoring (New Feature)

#### Start the Bridge Server
```bash
cd app
python bridge.py
```

The bridge server will start on `http://localhost:8000` and provide:
- WebSocket endpoint: `ws://localhost:8000/stream`
- HTTP ingestion endpoint: `http://localhost:8000/ingest`
- Health check: `http://localhost:8000/health`

#### Start the Live Dashboard
```bash
cd app
streamlit run app.py
```

Navigate to "🔄 Live Dashboard" in the sidebar to access real-time monitoring.

#### Simulate Data Ingestion
```bash
cd app
python simulate_ingest.py
```

This will send sample posts to the bridge server for testing.

### 3. URL Analysis

Use the live dashboard to analyze individual URLs:
1. Enter a social media URL (Twitter, Instagram, YouTube, etc.)
2. The system will extract text content
3. Analyze for harmful content using enhanced patterns
4. Display risk assessment and metadata

## 🔧 Configuration

### Environment Variables
- `HARMWATCH_WS`: WebSocket URL for real-time streaming (default: `ws://localhost:8000/stream`)

### Bridge Server Settings
- Host: `0.0.0.0` (configurable in `bridge.py`)
- Port: `8000` (configurable in `bridge.py`)
- CORS: Enabled for all origins

## 📊 Enhanced Classification

The merged system includes comprehensive pattern matching for:

- **Scam/Phishing**: Prize scams, verification requests, urgent actions
- **Hacking/Exploit**: CVE references, exploit code, security vulnerabilities
- **Hate Speech**: Discriminatory language, slurs, dehumanizing terms
- **Cyberbullying**: Personal attacks, harassment, threats
- **Misinformation**: Conspiracy theories, fake news, hoaxes
- **Privacy Risk**: Personal information requests, doxxing
- **Mental Health**: Self-harm, suicidal ideation, depression

### Risk Scoring
- **Low Risk**: Score 1-2
- **Medium Risk**: Score 3-4
- **High Risk**: Score 5+

## 🔌 API Endpoints

### Bridge Server (`http://localhost:8000`)

- `GET /health` - Server health and client count
- `POST /ingest` - Ingest new data for real-time streaming
- `WebSocket /stream` - Real-time data stream

### Data Format for Ingestion
```json
{
  "text": "Post content to analyze",
  "source": "twitter",
  "author": "username",
  "platform": "Twitter",
  "url": "https://twitter.com/user/status/123",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 📈 Real-Time Dashboard Features

- **Live Feed**: Real-time display of incoming posts
- **Risk Overview**: Live charts showing risk level distribution
- **Category Analysis**: Real-time category breakdown
- **Platform Monitoring**: Track posts by social media platform
- **Export Options**: Download live data as CSV

## 🧪 Testing

### Sample Data
Use the included `data/sample_posts.csv` for testing batch analysis.

### Real-Time Testing
1. Start the bridge server
2. Run the data ingestion simulator
3. Monitor the live dashboard for real-time updates

## 🔒 Privacy & Security

- **ID Anonymization**: Automatic hashing of user identifiers
- **Data Cleaning**: Removal of sensitive information
- **Local Processing**: All analysis happens locally
- **No Data Storage**: Real-time data is not permanently stored

## 🚨 Troubleshooting

### Common Issues

1. **Bridge Server Won't Start**
   - Check if port 8000 is available
   - Verify FastAPI and uvicorn are installed

2. **WebSocket Connection Failed**
   - Ensure bridge server is running
   - Check WebSocket URL configuration

3. **URL Analysis Fails**
   - Verify internet connection
   - Check if URL is accessible
   - Some sites may block automated requests

### Logs
- Bridge server logs appear in the terminal
- Streamlit logs show in the browser console
- Check for connection errors and dependency issues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and research purposes. Always respect platform policies and user privacy.

## 🙏 Acknowledgments

- Original HarmWatch project for batch analysis framework
- CyberShield Live project for real-time streaming concepts
- Streamlit for the web interface framework
- FastAPI for the bridge server implementation

---

**Note**: This system is designed for research and educational purposes. Always comply with platform terms of service and respect user privacy when analyzing social media content.
