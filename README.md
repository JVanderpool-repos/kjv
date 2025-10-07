# Bible Verse of the Day

A Python application that provides daily Bible verses from the King James Version (KJV), featuring both a web API and desktop GUI interface. The application ensures no verse is repeated until all verses have been displayed and avoids consecutive days from the same chapter.

## Features

### Core Functionality
- **Daily Verse Selection**: Automatic selection of a unique verse for each day
- **No Repeats**: Ensures no verse is repeated until all verses have been used
- **Chapter Variation**: Avoids consecutive days from the same book/chapter when possible
- **King James Version**: Uses only KJV text for copyright compliance

### Interfaces
- **Web API**: RESTful API with FastAPI framework
- **Desktop GUI**: Tkinter-based graphical user interface
- **Unified Launcher**: Single entry point for both interfaces

## Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)

### Setup
1. Clone or download the project
2. Navigate to the project directory
3. Run the unified launcher (it will handle dependency installation):
```bash
python launch.py
```

Alternatively, install dependencies manually:
```bash
# Create virtual environment (optional but recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install the application with GUI dependencies
pip install -e .[gui]
```

## Usage

### Quick Start
The easiest way to start the application is using the unified launcher:
```bash
python launch.py
```

This will:
1. Check and install any missing dependencies
2. Launch the desktop GUI interface
3. Automatically start the backend API server when needed

### Desktop GUI
The GUI provides a complete interface with:
- **Main Window**: Display daily verse with navigation controls
- **Verse Manager**: Advanced management with statistics and data loading
- **Settings**: API configuration and database path settings
- **Server Management**: Start/stop the backend API server

Features:
- Display today's verse or random verses
- View verse statistics and database information
- Load additional verses from CSV files
- Schedule future verses
- Manage API server integration

### Web API
Start the API server directly:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

#### Endpoints
- `GET /health` - Health check
- `GET /verse/today` - Get today's assigned verse
- `GET /verse/random` - Get a random verse

#### API Response Format
```json
{
  "book": "John",
  "chapter": 3,
  "verse": 16,
  "text_kjv": "For God so loved the world...",
  "reference": "John 3:16"
}
```

## ⚖️ Licensing

**KJV text** is in the public domain and can be freely used and distributed.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install the application
pip install -e .[dev]
```

### 2. Prepare Your Data
Create a CSV file with columns: `book,chapter,verse,text_kjv`

Example (`data/verses.csv`):
```csv
book,chapter,verse,text_kjv
Genesis,1,1,In the beginning God created the heaven and the earth.
Genesis,1,2,And the earth was without form and void; and darkness was upon the face of the deep...
```

### 3. Load Verses
```bash
python -m scripts.load_verses data/verses.csv
```

### 4. Start the Server
```bash
uvicorn app.main:app --reload
```

Visit: http://127.0.0.1:8000/verse/today

## 📊 API Endpoints

- **GET `/health`** - Health check
- **GET `/verse/today`** - Today's verse (consistent for the date)
- **GET `/verse/random`** - Random verse (for development)

Example response:
```json
{
  "date": "2025-10-05",
  "reference": "Genesis 1:1",
  "kjv": "In the beginning God created the heaven and the earth."
}
```

## 🗓️ Pre-scheduling Verses

Generate upcoming selections:
```bash
python -m scripts.schedule_verses --start 2025-01-01 --days 365 --out schedule.csv
```

Options:
- `--overwrite` - Replace existing dates in range
- `--start` - Start date (YYYY-MM-DD)
- `--days` - Number of days to schedule
- `--out` - Output CSV path

## ⚙️ Configuration

Create `.env` file (optional):
```env
DATABASE_URL=sqlite:///./bible.db
TIMEZONE=UTC
SEED=12345
```

## 🧪 Testing

The application includes a comprehensive test suite covering all components:

### Quick Testing
```bash
# Run all tests
python -m pytest

# Run specific test categories
python run_tests.py --api          # API functionality tests
python run_tests.py --gui          # GUI component tests  
python run_tests.py --database     # Database tests
python run_tests.py --integration  # Integration tests

# Run tests with coverage
python run_tests.py --coverage

# Skip slow tests
python run_tests.py --fast
```

### Test Structure
- `tests/test_api.py` - API endpoints and services
- `tests/test_gui.py` - GUI components and imports
- `tests/test_database.py` - Database connectivity and operations
- `tests/test_integration.py` - End-to-end integration tests
- `tests/test_selection.py` - Verse selection algorithm tests

### Test Features
- **40 comprehensive tests** covering all functionality
- **Mocked GUI tests** that work without display
- **In-memory database tests** for isolation
- **Integration tests** with real database
- **API server startup/shutdown tests**
- **Import and dependency validation**

## 📁 Project Structure

```
bible/
├── app/                    # FastAPI application
│   ├── main.py            # Application entry point
│   ├── api/routes.py      # API endpoints
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── db/                # Database configuration
├── gui/                   # Desktop GUI application
│   ├── main.py           # Main GUI window
│   └── manager.py        # Advanced verse management
├── scripts/              # Utility scripts
│   ├── load_verses.py    # Data loading utility
│   └── schedule_verses.py # Pre-scheduling utility
├── tests/                # Comprehensive test suite
│   ├── test_api.py       # API functionality tests
│   ├── test_gui.py       # GUI component tests
│   ├── test_database.py  # Database tests
│   ├── test_integration.py # Integration tests
│   └── test_selection.py # Selection algorithm tests
├── data/                 # Sample data files
├── launch.py            # Unified launcher
├── run_tests.py         # Test runner utility
└── pyproject.toml       # Project configuration
```

## 🔄 Selection Algorithm

1. Check if today's verse already selected → return if exists
2. Get list of unused verses
3. Exclude verses from same chapter as yesterday (if alternatives exist)
4. Randomly select from remaining pool
5. Persist selection with current date

When all verses are exhausted, the system raises an error. You can then reset the daily_selections table or implement rotation logic.

## 📈 Production Deployment

For production use:
1. Use PostgreSQL instead of SQLite
2. Set up proper environment variables
3. Use a process manager (PM2, systemd)
4. Configure reverse proxy (nginx)
5. Enable HTTPS
6. Set up monitoring and logging

## 📜 License

MIT License - See project metadata for details.

---

**KJV text is public domain and free to use.**
