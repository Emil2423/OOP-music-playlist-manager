# Technical Documentation - Music Playlist Manager

## 1. Architecture Overview

The application follows a **3-layer architecture** with clear separation of concerns, adhering to SOLID, GRASP, and CUPID principles.

### Architectural Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  (CLI Controller - handles user interaction via main.py)     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│  (Business Logic: SongService, PlaylistService, UserService) │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Access Layer                          │
│  (Repositories: SongRepository, PlaylistRepository, etc.)    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer (Models)                     │
│  (AudioTrack, Song, User, Playlist)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                       │
│  (DatabaseConnection, Schema, Logging)                       │
└─────────────────────────────────────────────────────────────┘
```

### Separation of Concerns

- **Models** (`src/models/`): Define core data structures and domain entities
- **Repositories** (`src/repositories/`): Handle database CRUD operations
- **Services** (`src/services/`): Implement business logic and validation
- **Controllers** (`src/controllers/`): Handle user interaction (CLI)
- **Strategies** (`src/strategies/`): Implement interchangeable algorithms

---

## 2. Database Schema

The application uses **SQLite** for data persistence with four main tables.

### Entity Relationship Diagram

```
┌───────────────┐         ┌───────────────┐
│    users      │         │    songs      │
├───────────────┤         ├───────────────┤
│ id (PK)       │         │ id (PK)       │
│ username      │         │ title         │
│ email         │         │ artist        │
│ created_at    │         │ genre         │
└───────┬───────┘         │ duration      │
        │                 │ created_at    │
        │                 └───────┬───────┘
        │                         │
        │ 1:N                     │ N:M
        │                         │
        ▼                         ▼
┌───────────────┐         ┌───────────────────┐
│   playlists   │◄────────│  playlist_songs   │
├───────────────┤         ├───────────────────┤
│ id (PK)       │         │ playlist_id (FK)  │
│ name          │         │ song_id (FK)      │
│ owner_id (FK) │         │ added_at          │
│ created_at    │         └───────────────────┘
└───────────────┘
```

### SQL Schema Definitions

```sql
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Songs table
CREATE TABLE IF NOT EXISTS songs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    genre TEXT NOT NULL,
    duration INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Playlists table
CREATE TABLE IF NOT EXISTS playlists (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Junction table for many-to-many relationship
CREATE TABLE IF NOT EXISTS playlist_songs (
    playlist_id TEXT NOT NULL,
    song_id TEXT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
);
```

---

## 3. OOP Principles Applied

### 3.1 Abstraction

**Definition:** Hiding complex implementation details and showing only essential features.

**Implementation in Project:**
- `AudioTrack` is an abstract base class that defines the common interface for all audio tracks
- `BaseRepository` is an abstract class that defines the CRUD interface for all repositories
- `DurationFormatStrategy` is an abstract base class for formatting algorithms

```python
# Example: AudioTrack abstraction
from abc import ABC, abstractmethod

class AudioTrack(ABC):
    @abstractmethod
    def get_details(self):
        """Abstract method to be implemented by subclasses"""
        pass
```

### 3.2 Encapsulation

**Definition:** Bundling data and methods that operate on that data within a single unit, restricting direct access.

**Implementation in Project:**
- All model classes use private attributes (e.g., `__title`, `__artist`)
- Access is provided through `@property` decorators for controlled access
- Validation logic is encapsulated within setter methods

```python
# Example: Song encapsulation
class Song(AudioTrack):
    def __init__(self, title, duration, artist, genre):
        self.__artist = artist  # Private attribute
        self.__genre = genre

    @property
    def artist(self):
        return self.__artist  # Controlled access
```

### 3.3 Inheritance

**Definition:** Creating new classes based on existing classes, inheriting their attributes and methods.

**Implementation in Project:**
- `Song` inherits from `AudioTrack` (base class for all audio content)
- `SongRepository`, `UserRepository`, `PlaylistRepository` inherit from `BaseRepository`
- All duration format strategies inherit from `DurationFormatStrategy`

```python
# Example: Inheritance hierarchy
class AudioTrack(ABC):  # Base class
    pass

class Song(AudioTrack):  # Derived class
    pass
```

### 3.4 Polymorphism

**Definition:** Objects of different classes responding to the same method call in different ways.

**Implementation in Project:**
- Each model class implements `__str__()` differently for display purposes
- All repositories implement the same CRUD interface but with different SQL queries
- Duration format strategies all implement `format_duration()` but produce different outputs

```python
# Example: Polymorphic behavior
class SecondsFormat(DurationFormatStrategy):
    def format_duration(self, total_seconds: int) -> str:
        return f"{total_seconds}s"

class MinutesFormat(DurationFormatStrategy):
    def format_duration(self, total_seconds: int) -> str:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}m {seconds}s"
```

---

## 4. Design Patterns

### 4.1 Repository Pattern

**Purpose:** Abstracts data access logic, providing a clean interface for CRUD operations.

**Implementation:**
- `BaseRepository` defines the abstract interface
- Concrete repositories (`SongRepository`, `UserRepository`, `PlaylistRepository`) implement specific database operations
- Services depend on repository abstractions, not concrete implementations

### 4.2 Singleton Pattern

**Purpose:** Ensures only one instance of `DatabaseConnection` exists throughout the application.

**Implementation:**
```python
class DatabaseConnection:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 4.3 Factory Pattern

**Purpose:** Creates objects without specifying the exact class, providing flexibility.

**Implementation:**
- `TrackFactory` creates `Song` objects with validation
- `DurationFormatFactory` creates format strategy instances by name

```python
class TrackFactory:
    @staticmethod
    def create_song(title, duration, artist, genre):
        if duration < 0:
            raise ValueError("Duration cannot be negative")
        return Song(title, duration, artist, genre)
```

### 4.4 Strategy Pattern (Sprint 2 Addition)

**Purpose:** Defines families of interchangeable algorithms for different operations.

**Implementation:**

#### Duration Format Strategies
- `DurationFormatStrategy` is the abstract base class
- Concrete strategies: `SecondsFormat`, `MinutesFormat`, `HoursFormat`, `CompactFormat`
- Allows runtime selection of duration display format

```python
# Usage example
from strategies.duration_format_strategies import DurationFormatFactory

fmt = DurationFormatFactory.get_format("hours")
formatted = fmt.format_duration(3661)  # "1h 1m 1s"
```

#### Sorting Strategies
- `SortStrategy` is the abstract base class
- Concrete strategies:
  - `SortByNameStrategy` - Sort by title/name (A-Z or Z-A)
  - `SortByArtistStrategy` - Sort by artist name
  - `SortByDurationStrategy` - Sort by duration (shortest/longest first)
  - `SortByGenreStrategy` - Sort by genre
  - `SortByDateAddedStrategy` - Sort by creation date
- All support reverse order via `reverse` parameter

```python
# Usage example
from strategies.sorting_strategies import SortByArtistStrategy

sorter = SortByArtistStrategy(reverse=False)
sorted_songs = sorter.sort(songs)
```

#### Filter Strategies
- `FilterStrategy` is the abstract base class
- Concrete strategies:
  - `FilterByGenreStrategy` - Filter by genre (exact or partial match)
  - `FilterByArtistStrategy` - Filter by artist name
  - `FilterByDurationRangeStrategy` - Filter by min/max duration
  - `FilterByTitleContainsStrategy` - Filter by title substring
  - `CompositeFilterStrategy` - Combine multiple filters with AND logic
- Supports complex filtering scenarios through composition

```python
# Usage example
from strategies.filter_strategies import FilterByGenreStrategy, CompositeFilterStrategy

# Single filter
rock_filter = FilterByGenreStrategy("Rock")
rock_songs = rock_filter.filter(songs)

# Combined filters
combined = CompositeFilterStrategy([
    FilterByGenreStrategy("Rock"),
    FilterByDurationRangeStrategy(180, 300)
])
filtered = combined.filter(songs)
```

---

## 5. Key Classes and Responsibilities

### Models

| Class | Responsibility |
|-------|----------------|
| `AudioTrack` | Abstract base class for all audio content; defines common interface |
| `Song` | Represents a music track with title, artist, genre, and duration |
| `User` | Represents a system user with username and email |
| `Playlist` | Collection of songs owned by a user |

### Repositories

| Class | Responsibility |
|-------|----------------|
| `BaseRepository` | Defines abstract CRUD interface for all repositories |
| `SongRepository` | Handles Song entity persistence and retrieval |
| `UserRepository` | Handles User entity persistence and retrieval |
| `PlaylistRepository` | Handles Playlist persistence and song associations |

### Services

| Class | Responsibility |
|-------|----------------|
| `SongService` | Business logic for song management, validation |
| `UserService` | Business logic for user management, validation |
| `PlaylistService` | Business logic for playlist operations |
| `TrackFactory` | Creates validated track instances |

### Strategies

| Class | Responsibility |
|-------|----------------|
| `DurationFormatStrategy` | Abstract base for duration formatting |
| `SecondsFormat` | Formats duration as total seconds (e.g., "354s") |
| `MinutesFormat` | Formats as minutes:seconds (e.g., "5m 54s") |
| `HoursFormat` | Formats as hours:minutes:seconds (e.g., "1h 1m 1s") |
| `CompactFormat` | Compact duration format (e.g., "5:54") |
| `SortStrategy` | Abstract base for sorting algorithms |
| `SortByNameStrategy` | Sort items by title/name alphabetically |
| `SortByArtistStrategy` | Sort songs by artist name |
| `SortByDurationStrategy` | Sort songs by duration |
| `SortByGenreStrategy` | Sort songs by genre |
| `SortByDateAddedStrategy` | Sort songs by creation timestamp |
| `FilterStrategy` | Abstract base for filtering algorithms |
| `FilterByGenreStrategy` | Filter songs by genre (exact or partial) |
| `FilterByArtistStrategy` | Filter songs by artist name |
| `FilterByDurationRangeStrategy` | Filter songs by duration range (min-max) |
| `FilterByTitleContainsStrategy` | Filter songs by title substring |
| `CompositeFilterStrategy` | Combine multiple filters with AND logic |

---

## 6. SOLID Principles Applied

| Principle | Application |
|-----------|-------------|
| **Single Responsibility** | Each class has one job (e.g., `SongRepository` only handles song persistence) |
| **Open/Closed** | New strategies can be added without modifying existing code |
| **Liskov Substitution** | All repositories can be used interchangeably through `BaseRepository` interface |
| **Interface Segregation** | Small, focused interfaces (e.g., repositories only expose necessary CRUD methods) |
| **Dependency Inversion** | Services depend on repository abstractions, not concrete implementations |

---

## 7. GRASP Principles Applied

| Principle | Application |
|-----------|-------------|
| **Creator** | `TrackFactory` creates `Song` objects; repositories create domain objects from database rows |
| **Controller** | `CLIController` handles system events and coordinates use cases |
| **High Cohesion** | Each class contains related functionality (e.g., all song operations in `SongService`) |
| **Low Coupling** | Minimal dependencies between layers; services only know about repositories |
| **Information Expert** | Classes that own data are responsible for operations on it |

---

## 8. Exception Handling

The application uses custom exceptions for clear error communication:

| Exception | Use Case |
|-----------|----------|
| `ValidationError` | Invalid input data (empty fields, out-of-range values) |
| `EntityNotFoundError` | Requested entity doesn't exist in database |
| `DuplicateEntityError` | Attempting to create duplicate (e.g., same username) |
| `DatabaseError` | General database operation failures |
| `AuthorizationError` | User not authorized for operation |

---

## 9. Logging

The application uses Python's `logging` module with:
- Log files stored in `logs/` directory with timestamps
- DEBUG level for detailed tracing
- INFO level for successful operations
- WARNING level for validation issues
- ERROR level for database failures
