# Database Schema

The application uses SQLite for data persistence. The database consists of four main tables: `users`, `songs`, `playlists`, and `playlist_songs`.

## Tables

### 1. users
Stores user information.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | TEXT | PRIMARY KEY | Unique identifier for the user (UUID) |
| `username` | TEXT | UNIQUE, NOT NULL | User's username |
| `email` | TEXT | UNIQUE, NOT NULL | User's email address |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when the user was created |

### 2. songs
Stores song/audio track information.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | TEXT | PRIMARY KEY | Unique identifier for the song (UUID) |
| `title` | TEXT | NOT NULL | Title of the song |
| `artist` | TEXT | NOT NULL | Artist of the song |
| `genre` | TEXT | NOT NULL | Genre of the song |
| `duration` | INTEGER | NOT NULL | Duration of the song in seconds |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when the song was added |

### 3. playlists
Stores playlist information.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | TEXT | PRIMARY KEY | Unique identifier for the playlist (UUID) |
| `name` | TEXT | NOT NULL | Name of the playlist |
| `owner_id` | TEXT | NOT NULL, FOREIGN KEY | ID of the user who owns the playlist |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when the playlist was created |

**Foreign Keys:**
- `owner_id` references `users(id)` (ON DELETE CASCADE)

### 4. playlist_songs
Junction table for the many-to-many relationship between playlists and songs.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `playlist_id` | TEXT | NOT NULL, FOREIGN KEY | ID of the playlist |
| `song_id` | TEXT | NOT NULL, FOREIGN KEY | ID of the song |
| `added_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when the song was added to the playlist |

**Primary Key:** `(playlist_id, song_id)`

**Foreign Keys:**
- `playlist_id` references `playlists(id)` (ON DELETE CASCADE)
- `song_id` references `songs(id)` (ON DELETE CASCADE)
