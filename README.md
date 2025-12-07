# Single Source of Truth

 * https://www.youtube.com/watch?v=JFO_HLa0UMc

# OOP Music Playlist Manager

A command-line interface (CLI) application for managing music playlists, songs, and users. This project demonstrates Object-Oriented Programming (OOP) principles, design patterns, and database interaction using SQLite.

## Features

### Core Functionality (Sprint 1)
- **Song Management**: Create, view, search, update, and delete songs with title, artist, genre, and duration
- **User Management**: Create, view, search, update, and delete users with username and email
- **Playlist Management**: Create playlists, add/remove songs, view playlist details with owner association
- **Data Persistence**: SQLite database with proper schema and relationships

### Advanced Features (Sprint 2)
- **Strategy Pattern Implementation**:
  - **Duration Formatting**: Display durations in seconds, minutes, hours, or compact format
  - **Sorting**: Sort songs by title, artist, duration, genre, or date added (ascending/descending)
  - **Filtering**: Filter songs by genre, artist, duration range, title substring, or combine multiple filters
- **Composite Pattern**: Combine multiple filters with AND logic for complex queries
- **Enhanced CLI**: Intuitive menu system with 19+ operations

## Design Principles

This project demonstrates:
- **OOP Principles**: Abstraction, Encapsulation, Inheritance, Polymorphism
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **GRASP Principles**: Creator, Controller, High Cohesion, Low Coupling, Information Expert
- **Design Patterns**: Repository, Singleton, Factory, Strategy, Composite

## Project Structure

```
OOP music player project/
├── docs/                       # Comprehensive documentation
│   ├── architecture.md         # Technical architecture and design patterns
│   ├── database_schema.md      # Database schema documentation
│   └── user_guide.md          # User manual with examples
├── src/                        # Source code
│   ├── controllers/            # CLI controller (presentation layer)
│   ├── database/               # Database connection and schema
│   ├── models/                 # Domain models (Song, User, Playlist, AudioTrack)
│   ├── repositories/           # Data access layer (Repository pattern)
│   ├── services/               # Business logic services
│   ├── strategies/             # Strategy pattern implementations
│   │   ├── duration_format_strategies.py
│   │   ├── sorting_strategies.py
│   │   └── filter_strategies.py
│   ├── exceptions/             # Custom exception classes
│   ├── main.py                 # Application entry point
│   └── logging_config.py       # Logging configuration
├── tests/                      # Comprehensive unit tests
├── logs/                       # Application logs
└── requirements.txt            # Python dependencies
```

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

## Installation

1. Clone the repository or download the source code.
2. Navigate to the project root directory:
   ```powershell
   cd OOP-music-playlist-manager
   ```
3. Install dependencies:
   ```powershell
   pip install -r "OOP music player project/requirements.txt"
   ```

## Usage

### Running the Application

Navigate to the source directory and run:
```powershell
cd "OOP music player project\src"
python main.py
```

The application will:
1. Create the SQLite database (`music_playlist.db`) on first run
2. Initialize all required tables
3. Display an interactive menu with 19+ operations

### Main Menu Options

**Songs (1-5)**
- Create, view, search, update, and delete songs

**Users (6-10)**  
- Create, view, search, update, and delete users

**Playlists (11-17)**
- Create playlists, manage playlist contents, view details

**Advanced Features (18-19)**
- Sort songs by multiple criteria (title, artist, duration, genre, date)
- Filter songs with single or combined filters (genre, artist, duration, title)

Follow the on-screen prompts to interact with the application. See `docs/user_guide.md` for detailed usage scenarios and examples.

## Running Tests

The project uses `pytest` for comprehensive unit testing with coverage reporting.

### Run All Tests
```powershell
cd "OOP music player project"
python -m pytest tests/ -v
```

### Run with Coverage Report
```powershell
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

### Run Specific Test File
```powershell
python -m pytest tests/test_services.py -v
```

Test coverage includes:
- Core functionality (CRUD operations)
- Database operations and schema
- All strategy implementations (duration, sorting, filtering)
- Repository pattern implementations
- Service layer business logic

## Logging

Application logs are automatically stored in the `logs/` directory with timestamps:
```
logs/app_YYYY-MM-DD_HH-MM-SS.log
```

Logs include:
- DEBUG: Detailed operation traces
- INFO: Successful operations
- WARNING: Validation issues
- ERROR: Database and system failures

## Documentation

Comprehensive documentation is available in the `docs/` folder:
- **`architecture.md`**: Technical architecture, OOP principles, design patterns, class responsibilities
- **`database_schema.md`**: Complete database schema with ERD and table definitions
- **`user_guide.md`**: Step-by-step user manual with real-world scenarios and examples

## Technologies Used

- **Python 3.10+**: Core programming language
- **SQLite3**: Embedded database (built-in)
- **pytest**: Testing framework
- **pytest-cov**: Test coverage reporting
- **logging**: Built-in logging module

## Key Features Demonstrated

### Architecture
- **3-Layer Architecture**: Presentation, Service, Data Access layers
- **Repository Pattern**: Abstracted data access with `BaseRepository`
- **Singleton Pattern**: Single database connection instance
- **Factory Pattern**: Object creation with validation (`TrackFactory`)
- **Strategy Pattern**: Interchangeable algorithms (formatting, sorting, filtering)
- **Composite Pattern**: Combined filters with AND logic

### OOP Principles
- **Abstraction**: Abstract base classes (`AudioTrack`, `BaseRepository`, `Strategy` classes)
- **Encapsulation**: Private attributes with property decorators
- **Inheritance**: Clear class hierarchies (Song → AudioTrack, repositories → BaseRepository)
- **Polymorphism**: Unified interfaces with different implementations

## Support

For detailed usage instructions, see `docs/user_guide.md`  
For technical details, see `docs/architecture.md`  
For database information, see `docs/database_schema.md`

Check application logs in `logs/` for debugging information.
