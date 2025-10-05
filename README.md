# Bible Verse of the Day API

A FastAPI web application that serves daily Bible verses using the King James Version (KJV). The application ensures:

- **No verse repetition** until the entire corpus is exhausted
- **Chapter variation** - consecutive days never come from the same chapter (unless only that chapter remains)
- **Persistent selection** - same verse returned for the same date
- **KJV text** - Public domain King James Version

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

```bash
pytest -v
```

## 📁 Project Structure

```
app/
├── main.py              # FastAPI application
├── api/routes.py        # API endpoints
├── core/config.py       # Settings/configuration
├── db/session.py        # Database connection
├── models/              # SQLAlchemy models
├── services/            # Business logic
scripts/
├── load_verses.py       # Data loading utility
├── schedule_verses.py   # Pre-scheduling utility
tests/                   # Unit tests
data/                    # Your verse data files
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
