# Music Playlist Manager - Sprint 1

**Project:** Object-Oriented Programming - Music Playlist Manager  
**Course:** Faculty of Information and Computer Technologies  
**Sprint:** Sprint 1 - Data Management & Persistence Layer  
**Developer:** Student B  
**Status:** ✅ Complete  

## Overview

This is the data persistence layer implementation for the Music Playlist Manager application. It provides:

- **Database Connection Management** using Singleton pattern
- **Repository Pattern** for data access abstraction
- **CRUD Operations** for Song, User, and Playlist entities
- **Logging Infrastructure** with timestamped file output
- **Interactive CLI** demonstrating all functionality
- **Comprehensive Unit Tests** (56+ test cases, >85% coverage)

---

## Requirements

- **Python:** 3.10 or higher
- **Database:** SQLite3 (included with Python)
- **Testing:** pytest 9.0.1+

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/Emil2423/OOP-music-playlist-manager
cd OOP-music-playlist-manager/"OOP music player project"
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Project Structure

```
OOP music player project/
├── src/
│   ├── main.py                      # CLI application
│   ├── logging_config.py            # Logging setup
│   ├── models/                      # Student A's classes (READ-ONLY)
│   │   ├── audio_track.py
│   │   ├── song.py
│   │   ├── playlist.py
│   │   ├── user.py
│   │   └── services/
│   ├── database/
│   │   ├── connection.py            # Singleton connection manager
│   │   └── schema.py                # Database schema
│   └── repositories/
│       ├── base_repository.py       # Abstract base class
│       ├── song_repository.py
│       ├── user_repository.py
│       └── playlist_repository.py
├── tests/
│   ├── test_database.py
│   ├── test_song_repository.py
│   ├── test_user_repository.py
│   └── test_playlist_repository.py
├── logs/                            # Auto-generated log files
├── docs/
│   └── sprint1_student_b.md         # Technical documentation
├── music_playlist.db                # SQLite database (auto-created)
└── requirements.txt
```

---

## Quick Start

### 1. Run Interactive CLI

```bash
python -m src.main
```

**Menu Options:**
```
1. Create Song
2. View All Songs
3. Search Song by Artist
4. Search Song by Genre
5. Create User
6. View All Users
7. Find User by Username
8. Create Playlist
9. View All Playlists
10. View User's Playlists
11. Add Song to Playlist
12. View Playlist Songs
0. Exit
```

### 2. Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_song_repository.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

### 3. View Logs

Log files are automatically created in the `logs/` directory:

```bash
# View latest log file (on Windows PowerShell)
Get-Content (Get-ChildItem logs/ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -Tail 50

# On Linux/macOS
tail -f logs/app_*.log
```

---

## Example Workflows

### Workflow 1: Create and View a Song

```
1. Select "Create Song"
   - Title: "Imagine"
   - Artist: "John Lennon"
   - Genre: "Rock"
   - Duration: 183

2. Select "View All Songs"
   - See the song you just created

3. Select "Search Song by Artist"
   - Search for "John Lennon"
   - View filtered results
```

### Workflow 2: Create User and Playlist

```
1. Select "Create User"
   - Username: "john_music_lover"
   - Email: "john@example.com

2. Select "Create Playlist"
   - Name: "My Favorites"
   - Owner: Select "john_music_lover"

3. Select "View User's Playlists"
   - Username: "john_music_lover"
   - See the playlist you created

4. Select "Add Song to Playlist"
   - Select song: "Imagine"
   - Select playlist: "My Favorites"

5. Select "View Playlist Songs"
   - Select playlist: "My Favorites"
   - See "Imagine" in the playlist
```

---

## Architecture

### Layered Design

```
┌─────────────────────────────────┐
│   CLI Layer (main.py)           │
│   Interactive User Interface    │
└──────────────┬──────────────────┘
               │
┌──────────────┴──────────────────┐
│  Repository Layer               │
│  Abstract Data Access           │
│  ├── SongRepository             │
│  ├── UserRepository             │
│  └── PlaylistRepository         │
└──────────────┬──────────────────┘
               │
┌──────────────┴──────────────────┐
│  Database Layer                 │
│  ├── DatabaseConnection (Single) │
│  └── Schema Management          │
└──────────────┬──────────────────┘
               │
          SQLite3 Database
```

### Design Patterns

1. **Singleton Pattern**
   - Ensures single database connection
   - Thread-safe implementation
   - Used by: `DatabaseConnection`

2. **Repository Pattern**
   - Abstract data access logic
   - Entity-specific repositories
   - Used by: `SongRepository`, `UserRepository`, `PlaylistRepository`

3. **Dependency Injection**
   - Repositories receive database connection
   - Testable and flexible
   - Enables easy mocking

---

## Key Features

### Create Operations (Persist Data)

```python
from src.models.song import Song
from src.repositories.song_repository import SongRepository
from src.database.connection import DatabaseConnection

# Initialize
db = DatabaseConnection()
db.connect()
repo = SongRepository(db)

# Create and persist a song
song = Song(title="Imagine", artist="John Lennon", 
            genre="Rock", duration=183)
song_id = repo.create(song)
print(f"Song created with ID: {song_id}")
```

### Read Operations (Retrieve Data)

```python
# Read single song by ID
song = repo.read_by_id(song_id)
print(f"Song: {song.title} by {song.artist}")

# Read all songs
all_songs = repo.read_all()
for song in all_songs:
    print(f"- {song.title}")

# Read with filter
rock_songs = repo.read_by_genre("Rock")
print(f"Found {len(rock_songs)} rock songs")
```

### Relationship Management

```python
from src.repositories.playlist_repository import PlaylistRepository

playlist_repo = PlaylistRepository(db)

# Add song to playlist
playlist_repo.add_song_to_playlist(playlist_id, song_id)

# Get all songs in playlist
song_ids = playlist_repo.get_playlist_songs(playlist_id)
for song_id in song_ids:
    song = repo.read_by_id(song_id)
    print(f"- {song.title}")
```

### Logging

All operations are automatically logged to timestamped files:

```
logs/
├── app_2025-11-23_14-30-45.log
├── app_2025-11-23_15-22-10.log
└── app_2025-11-23_16-05-33.log
```

Log file contents:
```
2025-11-23 14:30:45 - src.database.connection - INFO - Database connection established
2025-11-23 14:30:45 - src.database.schema - INFO - Database schema initialization completed
2025-11-23 14:30:46 - src.repositories.song_repository - INFO - CREATE operation on Song (ID: abc123...)
```

---

## API Reference

### DatabaseConnection (Singleton)

```python
# Get singleton instance
db = DatabaseConnection()

# Connect to database
db.connect()

# Execute SELECT query
results = db.execute_query("SELECT * FROM songs WHERE artist = ?", ("Beatles",))

# Execute INSERT/UPDATE/DELETE
row_id = db.execute_update(
    "INSERT INTO songs (id, title, artist, genre, duration) VALUES (?, ?, ?, ?, ?)",
    (uuid.uuid4(), "Song", "Artist", "Genre", 180)
)

# Execute multiple queries in transaction
queries = [
    ("INSERT INTO songs (...) VALUES (...)", params1),
    ("INSERT INTO playlists (...) VALUES (...)", params2)
]
success = db.execute_transaction(queries)

# Close connection
db.disconnect()
```

### Repository Interface

All repositories implement this interface:

```python
class BaseRepository(ABC):
    def create(self, entity: Any) -> str:
        """Persist entity, return ID"""
        pass
    
    def read_by_id(self, entity_id: str) -> Optional[Any]:
        """Retrieve entity by ID"""
        pass
    
    def read_all(self) -> List[Any]:
        """Retrieve all entities"""
        pass
    
    def exists(self, entity_id: str) -> bool:
        """Check if entity exists"""
        pass
```

### SongRepository

```python
repo = SongRepository(db)

repo.create(song: Song) -> str                  # Create song
repo.read_by_id(song_id: str) -> Optional[Song]     # Get one song
repo.read_all() -> List[Song]                   # Get all songs
repo.exists(song_id: str) -> bool               # Check existence
repo.read_by_artist(artist: str) -> List[Song] # Filter by artist
repo.read_by_genre(genre: str) -> List[Song]   # Filter by genre
```

### UserRepository

```python
repo = UserRepository(db)

repo.create(user: User) -> str                  # Create user
repo.read_by_id(user_id: str) -> Optional[User]     # Get one user
repo.read_all() -> List[User]                   # Get all users
repo.exists(user_id: str) -> bool               # Check existence
repo.read_by_username(username: str) -> Optional[User]  # Find by username
repo.read_by_email(email: str) -> Optional[User]        # Find by email
```

### PlaylistRepository

```python
repo = PlaylistRepository(db)

repo.create(playlist: Playlist) -> str               # Create playlist
repo.read_by_id(playlist_id: str) -> Optional[Playlist]  # Get one
repo.read_all() -> List[Playlist]                    # Get all
repo.exists(playlist_id: str) -> bool                # Check existence
repo.read_by_owner_id(owner_id: str) -> List[Playlist]  # Filter by owner
repo.add_song_to_playlist(playlist_id: str, song_id: str) -> bool  # Add song
repo.get_playlist_songs(playlist_id: str) -> List[str]  # Get song IDs
```

---

## Testing

### Run Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run specific test class
pytest tests/test_song_repository.py::TestSongRepository -v

# Run specific test method
pytest tests/test_song_repository.py::TestSongRepository::test_create_song_returns_id -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Structure

Each repository has comprehensive tests:

| Test File | Test Cases | Coverage |
|-----------|-----------|----------|
| test_database.py | 10 | Connection, transactions, constraints |
| test_song_repository.py | 15 | CRUD, filters, special characters |
| test_user_repository.py | 13 | CRUD, uniqueness, search |
| test_playlist_repository.py | 18 | CRUD, relationships, separation |
| **Total** | **56+** | **~85%** |

---

## Database Schema

### Schema Diagram

```sql
users
├── id (TEXT, PRIMARY KEY)
├── username (TEXT, UNIQUE)
├── email (TEXT, UNIQUE)
└── created_at (TIMESTAMP)

songs
├── id (TEXT, PRIMARY KEY)
├── title (TEXT)
├── artist (TEXT)
├── genre (TEXT)
├── duration (INTEGER)
└── created_at (TIMESTAMP)

playlists
├── id (TEXT, PRIMARY KEY)
├── name (TEXT)
├── owner_id (TEXT, FK → users.id)
└── created_at (TIMESTAMP)

playlist_songs
├── playlist_id (TEXT, FK → playlists.id)
├── song_id (TEXT, FK → songs.id)
├── added_at (TIMESTAMP)
└── PRIMARY KEY (playlist_id, song_id)
```

### Foreign Key Constraints

- Referential integrity enforced
- ON DELETE CASCADE for automatic cleanup
- Foreign key constraints enabled (`PRAGMA foreign_keys = ON`)

---

## Code Quality

### Standards Applied

- ✅ **PEP 8**: Style guide compliance
- ✅ **Type Hints**: Complete type annotations
- ✅ **Docstrings**: Google style documentation
- ✅ **Error Handling**: Comprehensive exception handling
- ✅ **Logging**: File-based operation tracking
- ✅ **Security**: Parameterized queries (SQL injection safe)

### Metrics

- **Code Coverage**: 85%+
- **Test Count**: 56+ unit tests
- **Documentation**: 100% of classes and public methods
- **Complexity**: O(n) or O(1) operations only

---

## Troubleshooting

### Database Already Locked

**Problem:** "database is locked" error

**Solution:** 
```bash
# Delete corrupted database
rm music_playlist.db

# Restart application - will create fresh database
python -m src.main
```

### Import Errors

**Problem:** "ModuleNotFoundError: No module named 'src'"

**Solution:**
```bash
# Ensure you're in the project root directory
# (same directory as src/ folder)
cd "OOP music player project"

# Run from project root
python -m src.main
```

### Tests Fail

**Problem:** Tests show import errors

**Solution:**
```bash
# Ensure pytest is installed
pip install pytest

# Run tests from project root
cd "OOP music player project"
pytest tests/ -v
```

### Log File Not Created

**Problem:** No logs/ directory created

**Solution:**
```bash
# Create logs directory manually
mkdir logs

# Application should create log files on next run
python -m src.main
```

---

## Performance Notes

### Current Performance
- Single database connection (Singleton pattern)
- In-memory queries on small datasets (<10,000 records)
- Suitable for development and testing

### Future Optimizations (Sprint 2)
- Add database indices on frequently queried columns
- Implement connection pooling for concurrent access
- Add query result caching
- Optimize relationship queries

---

## Security

### SQL Injection Protection
All database queries use parameterized statements:
```python
# ✓ Safe - parameterized query
query = "SELECT * FROM songs WHERE artist = ?"
results = db.execute_query(query, ("'; DROP TABLE songs; --",))

# ❌ Unsafe - string interpolation
query = f"SELECT * FROM songs WHERE artist = '{artist}'"
```

### Input Validation
- CLI validates user input before database operations
- Entity type checking before persistence
- Email format validation for user creation

### Error Handling
- Exceptions don't expose sensitive information
- Errors logged to file, not displayed to user
- User-friendly error messages in CLI

---

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all public methods
- Add docstrings to new methods
- Keep methods focused (Single Responsibility)

### Testing
- Write tests for new features
- Target >80% code coverage
- Use descriptive test names
- Test both happy path and error cases

### Documentation
- Update README for new features
- Add docstrings with examples
- Update ARCHITECTURE section for design changes

---

## Support

For issues or questions:

1. Check logs in `logs/` directory for error details
2. Review test cases in `tests/` for usage examples
3. Read docstrings in relevant module
4. Check technical documentation: `docs/sprint1_student_b.md`

---

## License

This project is part of the coursework for Python OOP course at the Faculty of Information and Computer Technologies.

---

## Status

- **Sprint 1:** ✅ Complete
  - ✅ Database connection (Singleton)
  - ✅ Repository pattern implementation
  - ✅ CRUD operations (Create & Read)
  - ✅ Logging infrastructure
  - ✅ Unit tests (56+, 85% coverage)
  - ✅ CLI prototype
  - ✅ Documentation

- **Sprint 2:** ⏳ Planned
  - Update operations
  - Delete operations
  - Advanced filtering
  - Performance optimization
  - API layer (REST/GraphQL)

---

**Last Updated:** November 23, 2025  
**Version:** 1.0.0
