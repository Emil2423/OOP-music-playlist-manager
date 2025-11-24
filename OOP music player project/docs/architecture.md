# Application Architecture

The application follows a layered architecture with a clear separation of concerns, adhering to SOLID principles.

## Layers

1.  **Presentation Layer (CLI)**: Handles user interaction (`main.py`).
2.  **Service Layer**: Contains business logic (e.g., `services/track_factory.py`).
3.  **Data Access Layer (Repositories)**: Handles database interactions (`repositories/`).
4.  **Domain Layer (Models)**: Defines the core data structures (`models/`).
5.  **Infrastructure Layer**: Handles database connection and logging (`database/`, `logging_config.py`).

## Design Patterns

-   **Repository Pattern**: Used to abstract data access logic. `BaseRepository` defines the interface, and concrete repositories (`SongRepository`, `UserRepository`, `PlaylistRepository`) implement it.
-   **Singleton Pattern**: Used for `DatabaseConnection` to ensure a single database connection instance.
-   **Factory Pattern**: Used in `services/track_factory.py` to create track objects.

## Components

### Models (`src/models/`)

-   `AudioTrack`: Base class for audio tracks.
-   `Song`: Inherits from `AudioTrack`, adds artist and genre.
-   `User`: Represents a user of the system.
-   `Playlist`: Represents a collection of songs owned by a user.

### Repositories (`src/repositories/`)

-   `BaseRepository`: Abstract base class defining CRUD operations (`create`, `get_by_id`, `get_all`, `update`, `delete`).
-   `SongRepository`: Handles `Song` persistence.
-   `UserRepository`: Handles `User` persistence.
-   `PlaylistRepository`: Handles `Playlist` persistence.

### Services (`src/services/`)

-   `TrackFactory`: Responsible for creating instances of tracks.

## Database

The application uses SQLite. The `DatabaseConnection` class manages the connection, and `schema.py` handles table creation.
