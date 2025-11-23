"""
TECHNICAL DOCUMENTATION
Sprint 1 - Data Layer Implementation
Music Playlist Manager Project

Author: Student B
Date: November 2025
"""

# ARCHITECTURE OVERVIEW

## Project Structure

```
OOP music player project/
├── src/
│   ├── database/                    # Data persistence layer
│   │   ├── __init__.py
│   │   ├── connection.py            # Singleton connection manager
│   │   └── schema.py                # Database schema & migrations
│   ├── repositories/                # Data access abstraction layer
│   │   ├── __init__.py
│   │   ├── base_repository.py       # Abstract base class
│   │   ├── song_repository.py       # Song CRUD operations
│   │   ├── user_repository.py       # User CRUD operations
│   │   └── playlist_repository.py   # Playlist CRUD operations
│   ├── models/                      # Domain models (Student A)
│   │   ├── audio_track.py
│   │   ├── song.py
│   │   ├── user.py
│   │   ├── playlist.py
│   │   └── __init__.py
│   ├── services/                    # Business logic
│   │   ├── track_factory.py         # Factory pattern
│   │   └── __init__.py
│   └── main.py                      # Prototype demonstrator
├── tests/
│   ├── test_core.py                 # Student A tests
│   ├── test_repositories.py         # Student B comprehensive tests
│   └── __pycache__/
├── docs/
│   ├── sprint1_b.md                 # This file
│   └── architecture.md              # Detailed architecture
└── README.md                        # Setup & run instructions
```

## Design Principles Applied

### 1. SOLID Principles

#### Single Responsibility (SRP)
- **DatabaseConnection**: Manages only connection lifecycle
- **DatabaseSchema**: Handles only schema creation and migrations
- **SongRepository**: Handles only Song CRUD operations
- **UserRepository**: Handles only User CRUD operations
- **PlaylistRepository**: Handles only Playlist CRUD operations

#### Open/Closed Principle (OCP)
- BaseRepository provides extensible interface for new repositories
- New repository types can extend without modifying existing code
- Schema can be extended with new tables without breaking existing tables

#### Liskov Substitution (LSP)
- All repositories inherit from BaseRepository
- Can substitute any concrete repository for BaseRepository type
- All repositories maintain the same interface contract

#### Interface Segregation (ISP)
- BaseRepository defines focused interface (CRUD operations)
- Repositories only implement methods relevant to their entity
- Specialized methods (read_by_artist, etc.) in specific repositories

#### Dependency Inversion (DI)
- Repositories depend on DatabaseConnection abstraction, not concrete implementation
- Repositories injected into tests with test database instance
- Allows easy swapping of database implementations

### 2. Other Design Patterns

#### Singleton Pattern
- **DatabaseConnection**: Single instance per application
- Ensures only one database connection is active
- Thread-safe initialization using __new__
- Provides global access point through getInstance pattern

#### Repository Pattern
- Abstracts data access layer
- Separates business logic from persistence
- Enables testing with mock repositories
- Encapsulates SQL queries in dedicated classes

#### Factory Pattern (Existing)
- **TrackFactory**: Creates Song objects with validation
- Centralizes object creation logic
- Validates domain constraints before persistence

### 3. OOP Principles

#### Abstraction
- BaseRepository defines abstract interface
- Concrete repositories hide SQL implementation details
- Clients work with high-level repository interface

#### Encapsulation
- Private database connection (_db) in repositories
- Private connection object (__connection) in DatabaseConnection
- Controlled access through public methods
- Protects invariants and implementation details

#### Inheritance
- All repositories inherit from BaseRepository
- Reuse common CRUD patterns
- Override/extend specific behavior

#### Polymorphism
- create(), read(), read_all() implemented differently per repository
- Same interface, different implementations
- Client code treats all repositories uniformly

## Database Schema

### Tables

#### users
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,           -- UUID from User.id
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP
)
```

#### songs
```sql
CREATE TABLE songs (
    id TEXT PRIMARY KEY,           -- UUID from Song.id
    title TEXT NOT NULL,
    duration INTEGER NOT NULL,     -- Seconds, must be > 0
    artist TEXT NOT NULL,
    genre TEXT NOT NULL,
    created_at TIMESTAMP
)
```

#### playlists
```sql
CREATE TABLE playlists (
    id TEXT PRIMARY KEY,           -- Generated UUID
    name TEXT NOT NULL,
    owner_id TEXT NOT NULL,        -- Foreign key to users
    created_at TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
)
```

#### playlist_songs (Junction Table)
```sql
CREATE TABLE playlist_songs (
    id TEXT PRIMARY KEY,           -- Generated UUID
    playlist_id TEXT NOT NULL,     -- Foreign key to playlists
    song_id TEXT NOT NULL,         -- Foreign key to songs
    position INTEGER NOT NULL,     -- Order in playlist
    added_at TIMESTAMP,
    UNIQUE(playlist_id, position),
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
)
```

### Indices
- `idx_playlists_owner_id`: Fast lookup of playlists by owner
- `idx_playlist_songs_playlist_id`: Fast lookup of songs in playlist
- `idx_playlist_songs_song_id`: Fast lookup of playlists containing song

## Connection Management

### DatabaseConnection Singleton

**Key Features:**
- Single active connection per application lifecycle
- Automatic connection pooling through SQLite
- Row factory enabled (sqlite3.Row) for dict-like access
- Context manager for cursor lifecycle management
- Automatic transaction commit/rollback
- Comprehensive error logging

**Methods:**
```python
connect()              # Establish connection
disconnect()          # Close connection
get_connection()       # Get or create connection
get_cursor()          # Context manager for cursor
execute_query()       # SELECT queries
execute_update()      # INSERT/UPDATE/DELETE
reset()               # Reset singleton (testing)
```

## Repository Layer

### BaseRepository (Abstract)

**Abstract Methods (must implement in subclasses):**
- `create(entity)` → str (entity ID)
- `read(entity_id)` → dict or None
- `read_all()` → list[dict]

**Concrete Methods (inherited by all repositories):**
- `delete(entity_id)` → bool
- `exists(entity_id)` → bool
- `update(entity_id, data)` → bool
- `_row_to_dict(row)` → dict

**Error Handling:**
- ValueError: Invalid input parameters
- RuntimeError: Database operation failures
- All exceptions logged before raising

### SongRepository

**CRUD Operations:**
- `create(song)` → song_id
- `read(song_id)` → dict
- `read_all()` → list[dict]
- `delete(song_id)` → bool

**Read Queries:**
- `read_by_artist(artist)` → list[dict]
- `read_by_genre(genre)` → list[dict]

### UserRepository

**CRUD Operations:**
- `create(user)` → user_id
- `read(user_id)` → dict
- `read_all()` → list[dict]
- `delete(user_id)` → bool

**Read Queries:**
- `read_by_username(username)` → dict or None
- `read_by_email(email)` → dict or None

### PlaylistRepository

**CRUD Operations:**
- `create(playlist)` → playlist_id
- `read(playlist_id)` → dict
- `read_all()` → list[dict]
- `delete(playlist_id)` → bool

**Specialized Operations:**
- `add_track(playlist_id, song_id)` → junction_id
- `remove_track(playlist_id, song_id)` → bool
- `get_tracks(playlist_id)` → list[dict]
- `get_total_duration(playlist_id)` → int
- `read_by_owner(owner_id)` → list[dict]

## Error Handling & Logging

### Logging Strategy

**Levels Used:**
- **DEBUG**: Detailed operation logs (read operations, cursor management)
- **INFO**: Important operations (connection established, entity created)
- **WARNING**: Unexpected situations (entity not found, deletion failed)
- **ERROR**: Operation failures with exception details

**Configuration:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Error Handling Pattern

```python
try:
    # Database operation
    result = self._db.execute_update(query, params)
    logger.info("Operation successful")
except sqlite3.DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise RuntimeError(f"Operation failed: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise RuntimeError(f"Operation failed: {e}")
```

## Transaction Management

### ACID Compliance

**Atomicity**: Context manager in DatabaseConnection ensures all-or-nothing
**Consistency**: Database constraints (NOT NULL, CHECK, UNIQUE, FK)
**Isolation**: SQLite default isolation level
**Durability**: SQLite persists to disk by default

**Transaction Flow:**
```
1. cursor = db.get_cursor()     # Context manager enter
2. cursor.execute(...)           # Execute query
3. [implicit ROLLBACK if error]  # Auto rollback on exception
4. connection.commit()           # Auto commit on success
5. cursor.close()                # Context manager exit
```

## Testing Strategy

### Test Coverage

**Unit Tests:** 30+ test cases covering:
- CRUD operations for each repository
- Error scenarios (invalid input, non-existent entities)
- Special queries (by artist, by genre, by owner, etc.)
- Transaction handling and rollback

**Integration Tests:** End-to-end workflows
- Create user → create songs → create playlist → add tracks → read all
- Verify all operations work together
- Test data integrity

**Fixtures:**
- `temp_db`: Creates isolated temp database per test
- `song_repo`, `user_repo`, `playlist_repo`: Fresh instances per test
- Automatic cleanup after each test

### Running Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=src

# Run specific test file
pytest tests/test_repositories.py -v

# Run specific test class
pytest tests/test_repositories.py::TestSongRepository -v

# Run with verbose output
pytest tests/test_repositories.py -vv
```

**Expected Coverage:** 85%+ of repository code

## Integration with Student A

### Model Compatibility

**Existing Models (Student A):**
- `AudioTrack`: Abstract base class (immutable after creation)
- `Song`: Extends AudioTrack with artist and genre
- `Playlist`: Container for tracks with owner validation
- `User`: Container for playlists with unique ID

**Integration Points:**
1. Song objects created by TrackFactory are persisted by SongRepository
2. User objects created directly are persisted by UserRepository
3. Playlist objects created with owner_id are persisted by PlaylistRepository
4. Database stores UUIDs generated by models
5. Read operations reconstruct model data from database

### No Breaking Changes

- All existing tests pass unchanged
- Models remain immutable (properties are read-only)
- Factory pattern preserved for Song creation
- User/Playlist classes unchanged

## Performance Considerations

### Indexing Strategy

**Indices Created:**
- `playlists(owner_id)`: For quick user playlist lookup
- `playlist_songs(playlist_id)`: For quick track retrieval
- `playlist_songs(song_id)`: For cross-reference queries

### Query Optimization

**Efficient Patterns:**
- Use WHERE clauses to filter at database level
- ORDER BY created_at DESC for default ordering
- JOINs in playlist_songs queries instead of N+1 queries
- COUNT(*) for existence checks

### Scalability

**Future Enhancements:**
- Connection pooling for concurrent access
- Prepared statements for parameterized queries
- Query result caching for frequently accessed data
- Pagination for large result sets

## Security Considerations

### SQL Injection Prevention

**All queries use parameterized statements:**
```python
# SAFE - uses parameterized query
cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))

# NOT SAFE - never do this
cursor.execute(f"SELECT * FROM songs WHERE id = {song_id}")
```

### Data Validation

**Input validation in all repositories:**
- Non-empty strings required
- Positive duration required for songs
- User/playlist IDs must not be empty
- Type checking (isinstance) for model objects

### Foreign Key Constraints

**Database enforces referential integrity:**
- Cannot add track with non-existent song_id
- Cannot create playlist with non-existent owner_id
- Cascade delete when user deleted (removes all their playlists)

## Future Enhancements (Sprint 2+)

### UPDATE Operations
- Modify song metadata (title, artist, genre)
- Update playlist information
- Update user information

### Advanced Queries
- Search by partial title/artist
- Pagination support
- Date range filters
- Sorting options (by duration, date, etc.)

### Batch Operations
- Bulk insert songs
- Bulk create playlists
- Bulk add tracks

### Caching Layer
- Cache frequently accessed songs
- Cache user playlists
- Invalidation strategy

### Analytics
- Most played songs
- User activity tracking
- Playlist popularity metrics

---

**Document Version:** 1.0
**Last Updated:** November 23, 2025
**Status:** Sprint 1 Complete
