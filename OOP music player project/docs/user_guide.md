# User Guide - Music Playlist Manager

## Table of Contents

1. [Installation](#1-installation)
2. [Running the Application](#2-running-the-application)
3. [Using the CLI Menu](#3-using-the-cli-menu)
4. [Sample Usage Scenarios](#4-sample-usage-scenarios)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

### Setup Steps

1. **Clone or download the project:**
   ```bash
   git clone <repository-url>
   cd OOP-music-playlist-manager
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python --version
   pytest --version
   ```

### Dependencies

The project uses minimal external dependencies:
- `pytest` - For running unit tests
- `pytest-cov` - For test coverage reports

All other functionality uses Python's built-in modules (sqlite3, logging, etc.).

---

## 2. Running the Application

### Starting the CLI

Navigate to the project directory and run:

```bash
cd "OOP music player project/src"
python main.py
```

### First Run

On first run, the application will:
1. Create the SQLite database (`music_playlist.db`)
2. Initialize all required tables
3. Display the main menu

### Database Location

The database file is stored at:
```
OOP-music-playlist-manager/music_playlist.db
```

---

## 3. Using the CLI Menu

### Main Menu

When you start the application, you'll see:

```
============================================================
       MUSIC PLAYLIST MANAGER - Sprint 2
============================================================

  SONGS
    1.  Create Song
    2.  View All Songs
    3.  Search Songs
    4.  Update Song
    5.  Delete Song

  USERS
    6.  Create User
    7.  View All Users
    8.  Find User
    9.  Update User
    10. Delete User

  PLAYLISTS
    11. Create Playlist
    12. View All Playlists
    13. View Playlist Details
    14. Update Playlist
    15. Delete Playlist
    16. Add Song to Playlist
    17. Remove Song from Playlist

  ADVANCED FEATURES
    18. Sort Songs
    19. Filter Songs

    0.  Exit
------------------------------------------------------------
Enter your choice (0-19):
```

### Menu Options Explained

#### Songs (Options 1-5)

| Option | Description |
|--------|-------------|
| 1. Create Song | Add a new song with title, artist, genre, and duration |
| 2. View All Songs | Display list of all songs in the database |
| 3. Search Songs | Find songs by title, artist, or genre |
| 4. Update Song | Modify an existing song's details |
| 5. Delete Song | Remove a song from the database |

#### Users (Options 6-10)

| Option | Description |
|--------|-------------|
| 6. Create User | Register a new user with username and email |
| 7. View All Users | Display list of all registered users |
| 8. Find User | Search for a user by username or email |
| 9. Update User | Modify an existing user's details |
| 10. Delete User | Remove a user (and their playlists) |

#### Playlists (Options 11-17)

| Option | Description |
|--------|-------------|
| 11. Create Playlist | Create a new playlist for a user |
| 12. View All Playlists | Display list of all playlists |
| 13. View Playlist Details | Show playlist info and songs |
| 14. Update Playlist | Change playlist name |
| 15. Delete Playlist | Remove a playlist |
| 16. Add Song to Playlist | Add an existing song to a playlist |
| 17. Remove Song from Playlist | Remove a song from a playlist |

#### Advanced Features (Options 18-19)

| Option | Description |
|--------|-------------|
| 18. Sort Songs | Sort songs by title, artist, duration, genre, or date added (ascending/descending) |
| 19. Filter Songs | Filter songs by genre, artist, duration range, title substring, or combine multiple filters |

---

## 4. Sample Usage Scenarios

### Scenario 1: Creating Your First Playlist

**Step 1: Create a User**
```
Enter your choice: 6

--- Create New User ---
Username: john_doe
Email: john@example.com

✅ User created successfully!
   ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
   Username: john_doe
```

**Step 2: Add Some Songs**
```
Enter your choice: 1

--- Create New Song ---
Title: Bohemian Rhapsody
Artist: Queen
Genre: Rock
Duration - Minutes: 5
Duration - Seconds: 54

✅ Song created successfully!
   ID: s1s2s3s4-s5s6-7890-song-123456789012
   Bohemian Rhapsody by Queen (5:54)
```

Repeat for more songs:
```
Enter your choice: 1
Title: Hotel California
Artist: Eagles
Genre: Rock
Duration - Minutes: 6
Duration - Seconds: 30

✅ Song created successfully!
```

**Step 3: Create a Playlist**
```
Enter your choice: 11

--- Create New Playlist ---
Playlist Name: Classic Rock Hits

Available Users:
  1. john_doe (john@example.com)
Select user number: 1

✅ Playlist created successfully!
   ID: p1p2p3p4-p5p6-7890-play-123456789012
   Name: Classic Rock Hits
```

**Step 4: Add Songs to Playlist**
```
Enter your choice: 16

--- Add Song to Playlist ---

Available Playlists:
  1. Classic Rock Hits (john_doe)
Select playlist: 1

Available Songs:
  1. Bohemian Rhapsody by Queen (5:54)
  2. Hotel California by Eagles (6:30)
Select song to add: 1

✅ Song added to playlist successfully!
```

**Step 5: View Playlist Details**
```
Enter your choice: 13

--- Playlist Details ---

Select playlist:
  1. Classic Rock Hits
Choice: 1

========================================
Playlist: Classic Rock Hits
Owner: john_doe
Total Songs: 1
Total Duration: 5:54
========================================

Songs:
  1. Bohemian Rhapsody by Queen (5:54) [Rock]
```

---

### Scenario 2: Updating a Song

```
Enter your choice: 4

--- Update Song ---

Available Songs:
  1. Bohemian Rhapsody by Queen (5:54) [Rock]
  2. Hotel California by Eagles (6:30) [Rock]
Select song to update: 1

Current details:
  Title: Bohemian Rhapsody
  Artist: Queen
  Genre: Rock
  Duration: 5:54

What would you like to update?
  1. Title
  2. Artist
  3. Genre
  4. Duration
  0. Cancel
Choice: 3

Enter new genre (current: Rock): Progressive Rock

✅ Song updated successfully!
```

---

### Scenario 3: Sorting and Filtering Songs

**Sorting Songs:**

The application provides multiple sorting options:

```
Enter your choice: 18

--- Sort Songs ---

Sort by:
  1. Title (A-Z)
  2. Title (Z-A)
  3. Artist (A-Z)
  4. Artist (Z-A)
  5. Duration (Shortest first)
  6. Duration (Longest first)
  7. Genre (A-Z)
  8. Genre (Z-A)
  9. Date Added (Newest first)
  10. Date Added (Oldest first)
Choice: 5

Sorted Songs (by duration, ascending):
  1. Yesterday by Beatles (2:05) [Pop]
  2. Imagine by John Lennon (3:03) [Rock]
  3. Bohemian Rhapsody by Queen (5:54) [Rock]
  4. Hotel California by Eagles (6:30) [Rock]
```

**Available Sorting Strategies:**
- **By Title** - Alphabetical by song title (A-Z or Z-A)
- **By Artist** - Alphabetical by artist name (A-Z or Z-A)
- **By Duration** - By song length (shortest/longest first)
- **By Genre** - Alphabetical by genre (A-Z or Z-A)
- **By Date Added** - By creation timestamp (newest/oldest first)

**Filtering Songs:**

The application provides powerful filtering options:

```
Enter your choice: 19

--- Filter Songs ---

Filter by:
  1. Genre
  2. Artist
  3. Duration Range
  4. Title Contains
  5. Combined Filters
Choice: 3

Enter minimum duration (seconds): 180
Enter maximum duration (seconds): 360

Filtered Songs (Duration: 180-360 seconds):
  1. Yesterday by Beatles (2:05)
  2. Imagine by John Lennon (3:03)
  3. Bohemian Rhapsody by Queen (5:54)

Found 3 matching songs.
```

**Available Filter Strategies:**
- **By Genre** - Filter by exact or partial genre match
- **By Artist** - Filter by exact or partial artist name match
- **By Duration Range** - Filter by minimum and maximum duration
- **By Title Contains** - Filter by substring in song title
- **Combined Filters** - Apply multiple filters simultaneously (AND logic)

**Combined Filter Example:**
```
Enter your choice: 19
Filter by: 5 (Combined Filters)

How many filters to apply? 2

Filter 1 - Select type:
  1. Genre
  2. Artist
  3. Duration Range
Choice: 1
Enter genre: Rock

Filter 2 - Select type:
  1. Genre
  2. Artist
  3. Duration Range
Choice: 3
Enter minimum duration (seconds): 300
Enter maximum duration (seconds): 400

Filtered Songs (Rock genre AND 300-400 seconds):
  1. Bohemian Rhapsody by Queen (5:54)
  2. Hotel California by Eagles (6:30)
```

---

### Scenario 4: Deleting a Playlist

```
Enter your choice: 15

--- Delete Playlist ---

Available Playlists:
  1. Classic Rock Hits (john_doe) - 2 songs
  2. Workout Mix (john_doe) - 5 songs
Select playlist to delete: 1

⚠️  Warning: This will permanently delete the playlist and remove all song associations.
Are you sure? (yes/no): yes

✅ Playlist deleted successfully!
```

---

## 5. Troubleshooting

### Common Issues

#### Issue: "Database not found"
**Solution:** The database is created automatically on first run. Make sure you're running from the correct directory:
```bash
cd "OOP music player project/src"
python main.py
```

#### Issue: "Import error" when running tests
**Solution:** Run pytest from the project root with proper path:
```bash
cd "OOP music player project"
python -m pytest tests/ -v
```

#### Issue: "User not found" when creating playlist
**Solution:** You must create a user first (option 6) before creating a playlist.

#### Issue: "Song already in playlist"
**Solution:** Each song can only be added once to a playlist. Check if it's already there using "View Playlist Details" (option 13).

### Running Tests

To run all tests:
```bash
cd "OOP music player project"
python -m pytest tests/ -v
```

To run with coverage report:
```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

### Log Files

Application logs are stored in:
```
OOP-music-playlist-manager/logs/app_YYYY-MM-DD_HH-MM-SS.log
```

Check logs for detailed error information if something goes wrong.

---

## Quick Reference

| Action | Menu Option |
|--------|-------------|
| Create a song | 1 |
| Create a user | 6 |
| Create a playlist | 11 |
| Add song to playlist | 16 |
| View playlist with songs | 13 |
| Sort songs | 18 |
| Filter songs | 19 |
| Exit application | 0 |

---

## Support

For issues or questions, check the `docs/architecture.md` file for technical details or review the log files in the `logs/` directory.
