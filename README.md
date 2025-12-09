# Single Source of Truth

 * https://www.youtube.com/watch?v=JFO_HLa0UMc

# OOP Music Playlist Manager

A command-line interface (CLI) application for managing music playlists, songs, and users. This project demonstrates Object-Oriented Programming (OOP) principles, database interaction using SQLite, and repository patterns.

## Features

- **Song Management**: Create, view, and search for songs by artist or genre.
- **User Management**: Create and view users.
- **Playlist Management**: Create playlists, add songs to playlists, and view playlists for specific users.
- **Data Persistence**: Uses SQLite database to store application data.

## Project Structure

```
OOP music player project/
├── docs/               # Documentation files
├── src/                # Source code
│   ├── database/       # Database connection and schema
│   ├── models/         # Data models (Song, User, Playlist)
│   ├── repositories/   # Data access layer (Repositories)
│   ├── services/       # Business logic services
│   ├── main.py         # Application entry point
│   └── logging_config.py # Logging configuration
└── tests/              # Unit tests
```

## Prerequisites

- Python 3.x

## Installation

1. Clone the repository or download the source code.
2. Navigate to the project root directory.
3. Install dependencies (optional, for testing):
   ```bash
   pip install pytest
   ```

## Usage

Follow the on-screen prompts to interact with the application.

## Running Tests

The project uses `pytest` for testing. To run the tests:

1. Ensure `pytest` is installed 
2. Run the tests from the root directory:
   ```bash
   python -m pytest
   ```

## Logging

Application logs are stored in the `logs/` directory.
