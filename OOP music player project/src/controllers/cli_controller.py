"""CLI Controller for music playlist manager.

This controller handles all user interaction through the command-line interface,
coordinating between user input and the service layer.

Design Principles:
- GRASP Controller: Handles system events from the UI
- Single Responsibility: Only handles CLI interaction logic
- Dependency Inversion: Depends on service abstractions
"""

import logging
from services.user_service import UserService
from services.song_service import SongService
from services.playlist_service import PlaylistService
from strategies.sorting_strategies import (
    SortByNameStrategy,
    SortByArtistStrategy,
    SortByDurationStrategy,
    SortByGenreStrategy,
    PlaylistSorter
)
from strategies.filter_strategies import (
    FilterByGenreStrategy,
    FilterByArtistStrategy,
    FilterByDurationRangeStrategy,
    FilterByTitleContainsStrategy,
    CompositeFilterStrategy,
    SongFilter
)
from exceptions.custom_exceptions import (
    EntityNotFoundError,
    ValidationError,
    DuplicateEntityError,
    DatabaseError,
    AuthorizationError
)

logger = logging.getLogger(__name__)


class CLIController:
    """Controller class for CLI-based user interaction.
    
    Handles all menu display, user input processing, and
    coordination with service layer for business operations.
    """
    
    def __init__(self, user_service=None, song_service=None, playlist_service=None):
        """Initialize CLI controller with services.
        
        Args:
            user_service: UserService instance
            song_service: SongService instance
            playlist_service: PlaylistService instance
        """
        self.user_service = user_service or UserService()
        self.song_service = song_service or SongService()
        self.playlist_service = playlist_service or PlaylistService()
        self.running = True
        logger.info("CLIController initialized")
    
    def format_duration(self, seconds):
        """Format duration from seconds to mm:ss format.
        
        Args:
            seconds (int): Duration in seconds
            
        Returns:
            str: Formatted duration string (e.g., "3:45")
        """
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}:{secs:02d}"
    
    def display_main_menu(self):
        """Display the main menu."""
        print("\n" + "=" * 60)
        print("       MUSIC PLAYLIST MANAGER - Sprint 2")
        print("=" * 60)
        print("\n  SONGS")
        print("    1.  Create Song")
        print("    2.  View All Songs")
        print("    3.  Search Songs")
        print("    4.  Update Song")
        print("    5.  Delete Song")
        print("\n  USERS")
        print("    6.  Create User")
        print("    7.  View All Users")
        print("    8.  Find User")
        print("    9.  Update User")
        print("    10. Delete User")
        print("\n  PLAYLISTS")
        print("    11. Create Playlist")
        print("    12. View All Playlists")
        print("    13. View Playlist Details")
        print("    14. Update Playlist")
        print("    15. Delete Playlist")
        print("    16. Add Song to Playlist")
        print("    17. Remove Song from Playlist")
        print("\n  ADVANCED FEATURES")
        print("    18. Sort Songs")
        print("    19. Filter Songs")
        print("\n    0.  Exit")
        print("-" * 60)
    
    def get_input(self, prompt, required=True):
        """Get user input with optional validation.
        
        Args:
            prompt: Input prompt to display
            required: If True, empty input is rejected
            
        Returns:
            str: User input (stripped)
        """
        while True:
            value = input(prompt).strip()
            if value or not required:
                return value
            print("  ❌ This field is required")
    
    def get_int_input(self, prompt, min_val=None, max_val=None):
        """Get integer input with optional range validation.
        
        Args:
            prompt: Input prompt
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            int: Valid integer input
        """
        while True:
            try:
                value = int(input(prompt).strip())
                if min_val is not None and value < min_val:
                    print(f"  ❌ Value must be at least {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"  ❌ Value must be at most {max_val}")
                    continue
                return value
            except ValueError:
                print("  ❌ Please enter a valid number")
    
    def select_from_list(self, items, display_func, prompt="Select number"):
        """Display a list and let user select an item.
        
        Args:
            items: List of items to choose from
            display_func: Function to display each item
            prompt: Selection prompt
            
        Returns:
            Selected item or None if cancelled
        """
        if not items:
            return None
        
        for i, item in enumerate(items, 1):
            print(f"  {i}. {display_func(item)}")
        
        print(f"  0. Cancel")
        
        choice = self.get_int_input(f"\n{prompt}: ", 0, len(items))
        if choice == 0:
            return None
        return items[choice - 1]
    
    # ==================== SONG OPERATIONS ====================
    
    def create_song(self):
        """Handle song creation."""
        logger.info("User initiated song creation")
        print("\n--- Create New Song ---")
        try:
            title = self.get_input("Title: ")
            artist = self.get_input("Artist: ")
            genre = self.get_input("Genre: ")
            minutes = self.get_int_input("Duration - Minutes: ", min_val=0)
            seconds = self.get_int_input("Duration - Seconds: ", min_val=0, max_val=59)
            duration = minutes * 60 + seconds
            
            if duration < 1:
                print("\n❌ Error: Duration must be at least 1 second")
                return
            
            song = self.song_service.create_song(title, artist, genre, duration)
            logger.info(f"Song created successfully via CLI: id={song.id}, title='{song.title}'")
            print(f"\n✅ Song created successfully!")
            print(f"   ID: {song.id}")
            print(f"   {song.title} by {song.artist} ({self.format_duration(song.duration)})")
            
        except (ValidationError, DatabaseError) as e:
            logger.warning(f"Song creation failed: {e.message}")
            print(f"\n❌ Error: {e.message}")
    
    def view_all_songs(self):
        """Display all songs."""
        logger.debug("User viewing all songs")
        print("\n--- All Songs ---")
        songs = self.song_service.get_all_songs()
        
        if not songs:
            print("No songs in database")
            return
        
        print(f"\nTotal: {len(songs)} songs\n")
        for i, song in enumerate(songs, 1):
            print(f"{i}. {song.title}")
            print(f"   Artist: {song.artist} | Genre: {song.genre} | Duration: {self.format_duration(song.duration)}")
    
    def search_songs(self):
        """Search songs by various criteria."""
        logger.info("User initiated song search")
        print("\n--- Search Songs ---")
        print("  1. By Artist")
        print("  2. By Genre")
        print("  3. By Title (keyword)")
        print("  0. Cancel")
        
        choice = self.get_int_input("Select: ", 0, 3)
        
        if choice == 0:
            return
        
        try:
            if choice == 1:
                artist = self.get_input("Artist name: ")
                songs = self.song_service.get_songs_by_artist(artist)
            elif choice == 2:
                genre = self.get_input("Genre: ")
                songs = self.song_service.get_songs_by_genre(genre)
            else:
                query = self.get_input("Search keyword: ")
                songs = self.song_service.search_songs(query)
            
            if not songs:
                print("\nNo songs found")
                return
            
            print(f"\nFound {len(songs)} songs:\n")
            for i, song in enumerate(songs, 1):
                print(f"{i}. {song.title} by {song.artist}")
                print(f"   Genre: {song.genre} | Duration: {self.format_duration(song.duration)}")
                
        except ValidationError as e:
            print(f"\n❌ Error: {e.message}")
    
    def update_song(self):
        """Update an existing song."""
        logger.info("User initiated song update")
        print("\n--- Update Song ---")
        songs = self.song_service.get_all_songs()
        
        if not songs:
            print("No songs to update")
            return
        
        print("\nSelect song to update:")
        song = self.select_from_list(
            songs,
            lambda s: f"{s.title} by {s.artist}",
            "Select song"
        )
        
        if not song:
            return
        
        print(f"\nUpdating: {song.title}")
        print("(Press Enter to keep current value)\n")
        
        new_title = input(f"Title [{song.title}]: ").strip() or None
        new_artist = input(f"Artist [{song.artist}]: ").strip() or None
        new_genre = input(f"Genre [{song.genre}]: ").strip() or None
        
        print(f"Duration [{self.format_duration(song.duration)}]:")
        mins_input = input(f"  Minutes [{song.duration // 60}]: ").strip()
        secs_input = input(f"  Seconds [{song.duration % 60}]: ").strip()
        
        new_duration = None
        if mins_input or secs_input:
            mins = int(mins_input) if mins_input else song.duration // 60
            secs = int(secs_input) if secs_input else song.duration % 60
            new_duration = mins * 60 + secs
        
        try:
            updated = self.song_service.update_song(
                song.id, new_title, new_artist, new_genre, new_duration
            )
            logger.info(f"Song updated successfully via CLI: id={updated.id}, title='{updated.title}'")
            print(f"\n✅ Song updated successfully!")
            print(f"   {updated.title} by {updated.artist}")
            
        except (ValidationError, EntityNotFoundError, DatabaseError) as e:
            logger.warning(f"Song update failed: {e.message}")
            print(f"\n❌ Error: {e.message}")
    
    def delete_song(self):
        """Delete a song."""
        logger.info("User initiated song deletion")
        print("\n--- Delete Song ---")
        songs = self.song_service.get_all_songs()
        
        if not songs:
            print("No songs to delete")
            return
        
        print("\nSelect song to delete:")
        song = self.select_from_list(
            songs,
            lambda s: f"{s.title} by {s.artist}",
            "Select song"
        )
        
        if not song:
            return
        
        confirm = input(f"\nDelete '{song.title}'? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Cancelled")
            return
        
        try:
            self.song_service.delete_song(song.id)
            logger.info(f"Song deleted successfully via CLI: id={song.id}, title='{song.title}'")
            print(f"\n✅ Song deleted successfully!")
            
        except (EntityNotFoundError, DatabaseError) as e:
            logger.warning(f"Song deletion failed: {e.message}")
            print(f"\n❌ Error: {e.message}")
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self):
        """Handle user creation."""
        logger.info("User initiated user creation")
        print("\n--- Create New User ---")
        try:
            username = self.get_input("Username: ")
            email = self.get_input("Email: ")
            
            user = self.user_service.create_user(username, email)
            logger.info(f"User created successfully via CLI: id={user.id}, username='{user.username}'")
            print(f"\n✅ User created successfully!")
            print(f"   ID: {user.id}")
            print(f"   Username: {user.username.title()}")
            
        except (ValidationError, DuplicateEntityError, DatabaseError) as e:
            logger.warning(f"User creation failed: {e.message}")
            print(f"\n❌ Error: {e.message}")
    
    def view_all_users(self):
        """Display all users."""
        print("\n--- All Users ---")
        users = self.user_service.get_all_users()
        
        if not users:
            print("No users in database")
            return
        
        print(f"\nTotal: {len(users)} users\n")
        for i, user in enumerate(users, 1):
            print(f"{i}. {user.username.title()}")
            print(f"   Email: {user.email}")
            print(f"   ID: {user.id}")
    
    def find_user(self):
        """Find a user by username."""
        print("\n--- Find User ---")
        username = self.get_input("Username: ")
        
        try:
            user = self.user_service.get_user_by_username(username)
            print(f"\n✅ User found:")
            print(f"   Username: {user.username.title()}")
            print(f"   Email: {user.email}")
            print(f"   ID: {user.id}")
            
        except EntityNotFoundError as e:
            print(f"\n❌ {e.message}")
    
    def update_user(self):
        """Update an existing user."""
        logger.info("User initiated user update")
        print("\n--- Update User ---")
        users = self.user_service.get_all_users()
        
        if not users:
            print("No users to update")
            return
        
        print("\nSelect user to update:")
        user = self.select_from_list(
            users,
            lambda u: f"{u.username.title()} ({u.email})",
            "Select user"
        )
        
        if not user:
            return
        
        print(f"\nUpdating: {user.username.title()}")
        print("(Press Enter to keep current value)\n")
        
        new_username = input(f"Username [{user.username.title()}]: ").strip() or None
        new_email = input(f"Email [{user.email}]: ").strip() or None
        
        try:
            updated = self.user_service.update_user(user.id, new_username, new_email)
            logger.info(f"User updated successfully via CLI: id={updated.id}, username='{updated.username}'")
            print(f"\n✅ User updated successfully!")
            print(f"   Username: {updated.username.title()}")
            
        except (ValidationError, DuplicateEntityError, EntityNotFoundError, DatabaseError) as e:
            logger.warning(f"User update failed: {e.message}")
            print(f"\n❌ Error: {e.message}")
    
    def delete_user(self):
        """Delete a user."""
        logger.info("User initiated user deletion")
        print("\n--- Delete User ---")
        users = self.user_service.get_all_users()
        
        if not users:
            print("No users to delete")
            return
        
        print("\nSelect user to delete:")
        user = self.select_from_list(
            users,
            lambda u: f"{u.username.title()} ({u.email})",
            "Select user"
        )
        
        if not user:
            return
        
        confirm = input(f"\nDelete user '{user.username.title()}'? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Cancelled")
            return
        
        try:
            self.user_service.delete_user(user.id)
            logger.info(f"User deleted successfully via CLI: id={user.id}, username='{user.username}'")
            print(f"\n✅ User deleted successfully!")
            
        except (EntityNotFoundError, DatabaseError) as e:
            logger.warning(f"User deletion failed: {e.message}")
            print(f"\n❌ Error: {e.message}")
    
    # ==================== PLAYLIST OPERATIONS ====================
    
    def create_playlist(self):
        """Handle playlist creation."""
        logger.info("User initiated playlist creation")
        print("\n--- Create New Playlist ---")
        
        users = self.user_service.get_all_users()
        if not users:
            print("❌ No users exist. Create a user first.")
            return
        
        name = self.get_input("Playlist name: ")
        
        print("\nSelect owner:")
        owner = self.select_from_list(
            users,
            lambda u: u.username.title(),
            "Select user"
        )
        
        if not owner:
            return
        
        try:
            playlist = self.playlist_service.create_playlist(name, owner.id)
            logger.info(f"Playlist created successfully via CLI: id={playlist.id}, name='{playlist.name}'")
            print(f"\n✅ Playlist created successfully!")
            print(f"   Name: {playlist.name}")
            print(f"   ID: {playlist.id}")
            
        except (ValidationError, EntityNotFoundError, DatabaseError) as e:
            logger.warning(f"Playlist creation failed: {e.message}")
            print(f"\n❌ Error: {e.message}")
    
    def view_all_playlists(self):
        """Display all playlists."""
        print("\n--- All Playlists ---")
        playlists = self.playlist_service.get_all_playlists()
        
        if not playlists:
            print("No playlists in database")
            return
        
        print(f"\nTotal: {len(playlists)} playlists\n")
        for i, playlist in enumerate(playlists, 1):
            try:
                owner = self.user_service.get_user_by_id(playlist.owner_id)
                owner_name = owner.username.title()
            except:
                owner_name = "Unknown"
            songs = self.playlist_service.get_playlist_songs(playlist.id)
            song_count = len(songs)
            print(f"{i}. {playlist.name}")
            print(f"   Owner: {owner_name} | Songs: {song_count}")
    
    def view_playlist_details(self):
        """View detailed playlist information with songs."""
        print("\n--- Playlist Details ---")
        playlists = self.playlist_service.get_all_playlists()
        
        if not playlists:
            print("No playlists in database")
            return
        
        print("\nSelect playlist:")
        playlist = self.select_from_list(
            playlists,
            lambda p: p.name,
            "Select playlist"
        )
        
        if not playlist:
            return
        
        try:
            songs = self.playlist_service.get_playlist_songs(playlist.id)
            try:
                owner = self.user_service.get_user_by_id(playlist.owner_id)
                owner_name = owner.username.title()
            except:
                owner_name = "Unknown"
            
            print(f"\n{'=' * 40}")
            print(f"Playlist: {playlist.name}")
            print(f"Owner: {owner_name}")
            print(f"Total Songs: {len(songs)}")
            
            if songs:
                total_duration = sum(s.duration for s in songs)
                print(f"Total Duration: {self.format_duration(total_duration)}")
                print(f"{'=' * 40}")
                print("\nTracks:")
                for i, song in enumerate(songs, 1):
                    print(f"  {i}. {song.title} - {song.artist} ({self.format_duration(song.duration)})")
            else:
                print(f"{'=' * 40}")
                print("\nNo songs in this playlist")
                
        except EntityNotFoundError as e:
            print(f"\n❌ Error: {e.message}")
    
    def update_playlist(self):
        """Update a playlist."""
        logger.info("User initiated playlist update")
        print("\n--- Update Playlist ---")
        playlists = self.playlist_service.get_all_playlists()
        
        if not playlists:
            print("No playlists to update")
            return
        
        print("\nSelect playlist to update:")
        playlist = self.select_from_list(
            playlists,
            lambda p: p.name,
            "Select playlist"
        )
        
        if not playlist:
            return
        
        print(f"\nUpdating: {playlist.name}")
        new_name = input(f"New name [{playlist.name}]: ").strip() or None
        
        if not new_name:
            print("No changes made")
            return
        
        try:
            updated = self.playlist_service.update_playlist(playlist.id, new_name)
            logger.info(f"Playlist updated successfully via CLI: id={updated.id}, name='{updated.name}'")
            print(f"\n✅ Playlist updated to: {updated.name}")
            
        except (ValidationError, EntityNotFoundError, DatabaseError) as e:
            logger.warning(f"Playlist update failed: {e.message}")
            print(f"\n❌ Error: {e.message}")
    
    def delete_playlist(self):
        """Delete a playlist."""
        logger.info("User initiated playlist deletion")
        print("\n--- Delete Playlist ---")
        playlists = self.playlist_service.get_all_playlists()
        
        if not playlists:
            print("No playlists to delete")
            return
        
        print("\nSelect playlist to delete:")
        playlist = self.select_from_list(
            playlists,
            lambda p: p.name,
            "Select playlist"
        )
        
        if not playlist:
            return
        
        confirm = input(f"\nDelete playlist '{playlist.name}'? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Cancelled")
            return
        
        try:
            self.playlist_service.delete_playlist(playlist.id)
            logger.info(f"Playlist deleted successfully via CLI: id={playlist.id}, name='{playlist.name}'")
            print(f"\n✅ Playlist deleted successfully!")
            
        except (EntityNotFoundError, DatabaseError) as e:
            logger.warning(f"Playlist deletion failed: {e.message}")
            print(f"\n❌ Error: {e.message}")
    
    def add_song_to_playlist(self):
        """Add a song to a playlist."""
        logger.info("User initiated adding song to playlist")
        print("\n--- Add Song to Playlist ---")
        
        playlists = self.playlist_service.get_all_playlists()
        songs = self.song_service.get_all_songs()
        
        if not playlists:
            print("❌ No playlists exist")
            return
        if not songs:
            print("❌ No songs exist")
            return
        
        print("\nSelect playlist:")
        playlist = self.select_from_list(playlists, lambda p: p.name, "Select playlist")
        if not playlist:
            return
        
        print("\nSelect song to add:")
        song = self.select_from_list(
            songs,
            lambda s: f"{s.title} by {s.artist}",
            "Select song"
        )
        if not song:
            return
        
        try:
            self.playlist_service.add_song_to_playlist(playlist.id, song.id)
            logger.info(f"Song added to playlist via CLI: song_id={song.id}, playlist_id={playlist.id}")
            print(f"\n✅ Added '{song.title}' to '{playlist.name}'")
            
        except (EntityNotFoundError, DatabaseError) as e:
            logger.warning(f"Failed to add song to playlist: {e.message}")
            print(f"\n❌ Error: {e.message}")
    
    def remove_song_from_playlist(self):
        """Remove a song from a playlist."""
        logger.info("User initiated removing song from playlist")
        print("\n--- Remove Song from Playlist ---")
        
        playlists = self.playlist_service.get_all_playlists()
        if not playlists:
            print("❌ No playlists exist")
            return
        
        print("\nSelect playlist:")
        playlist = self.select_from_list(playlists, lambda p: p.name, "Select playlist")
        if not playlist:
            return
        
        songs = self.playlist_service.get_playlist_songs(playlist.id)
        if not songs:
            print(f"\n❌ No songs in '{playlist.name}'")
            return
        
        print("\nSelect song to remove:")
        song = self.select_from_list(
            songs,
            lambda s: f"{s.title} by {s.artist}",
            "Select song"
        )
        if not song:
            return
        
        try:
            self.playlist_service.remove_song_from_playlist(playlist.id, song.id)
            logger.info(f"Song removed from playlist via CLI: song_id={song.id}, playlist_id={playlist.id}")
            print(f"\n✅ Removed '{song.title}' from '{playlist.name}'")
            
        except (EntityNotFoundError, DatabaseError) as e:
            logger.warning(f"Failed to remove song from playlist: {e.message}")
            print(f"\n❌ Error: {e.message}")
    
    # ==================== STRATEGY PATTERN DEMOS ====================
    
    def sort_songs_demo(self):
        """Demonstrate sorting strategies."""
        logger.info("User initiated sort songs feature")
        print("\n--- Sort Songs ---")
        
        songs = self.song_service.get_all_songs()
        if not songs:
            print("No songs to sort")
            return
        
        print("\nSelect sorting strategy:")
        print("  1. Sort by Title (A-Z)")
        print("  2. Sort by Title (Z-A)")
        print("  3. Sort by Artist (A-Z)")
        print("  4. Sort by Duration (Shortest first)")
        print("  5. Sort by Duration (Longest first)")
        print("  6. Sort by Genre")
        print("  0. Cancel")
        
        choice = self.get_int_input("Select: ", 0, 6)
        if choice == 0:
            return
        
        sorter = PlaylistSorter()
        
        strategies = {
            1: SortByNameStrategy(reverse=False),
            2: SortByNameStrategy(reverse=True),
            3: SortByArtistStrategy(reverse=False),
            4: SortByDurationStrategy(reverse=False),
            5: SortByDurationStrategy(reverse=True),
            6: SortByGenreStrategy(reverse=False)
        }
        
        sorter.set_strategy(strategies[choice])
        logger.info(f"User applied sorting strategy: {sorter.strategy_name}")
        sorted_songs = sorter.sort(songs)
        
        print(f"\n📊 Sorted using: {sorter.strategy_name}")
        print("-" * 40)
        
        for i, song in enumerate(sorted_songs, 1):
            print(f"{i}. {song.title}")
            print(f"   Artist: {song.artist} | Genre: {song.genre} | Duration: {self.format_duration(song.duration)}")
    
    def filter_songs_demo(self):
        """Demonstrate filtering strategies."""
        logger.info("User initiated filter songs feature")
        print("\n--- Filter Songs ---")
        
        songs = self.song_service.get_all_songs()
        if not songs:
            print("No songs to filter")
            return
        
        print("\nSelect filter type:")
        print("  1. Filter by Genre")
        print("  2. Filter by Artist")
        print("  3. Filter by Duration Range")
        print("  4. Filter by Title (keyword)")
        print("  5. Combined Filter (multiple criteria)")
        print("  0. Cancel")
        
        choice = self.get_int_input("Select: ", 0, 5)
        if choice == 0:
            return
        
        song_filter = SongFilter()
        
        if choice == 1:
            genre = self.get_input("Genre to filter: ")
            song_filter.set_strategy(FilterByGenreStrategy(genre, exact=False))
            
        elif choice == 2:
            artist = self.get_input("Artist to filter: ")
            song_filter.set_strategy(FilterByArtistStrategy(artist, exact=False))
            
        elif choice == 3:
            min_dur = self.get_int_input("Minimum duration (minutes, 0 for none): ", 0)
            max_dur = self.get_int_input("Maximum duration (minutes, 0 for none): ", 0)
            song_filter.set_strategy(FilterByDurationRangeStrategy(
                min_dur * 60 if min_dur > 0 else None,
                max_dur * 60 if max_dur > 0 else None
            ))
            
        elif choice == 4:
            keyword = self.get_input("Title keyword: ")
            song_filter.set_strategy(FilterByTitleContainsStrategy(keyword))
            
        elif choice == 5:
            print("\nBuilding combined filter...")
            composite = CompositeFilterStrategy()
            
            genre = input("Genre (or Enter to skip): ").strip()
            if genre:
                composite.add_filter(FilterByGenreStrategy(genre, exact=False))
            
            artist = input("Artist (or Enter to skip): ").strip()
            if artist:
                composite.add_filter(FilterByArtistStrategy(artist, exact=False))
            
            min_dur = input("Min duration in minutes (or Enter to skip): ").strip()
            max_dur = input("Max duration in minutes (or Enter to skip): ").strip()
            if min_dur or max_dur:
                composite.add_filter(FilterByDurationRangeStrategy(
                    int(min_dur) * 60 if min_dur else None,
                    int(max_dur) * 60 if max_dur else None
                ))
            
            song_filter.set_strategy(composite)
        
        filtered = song_filter.apply(songs)
        logger.info(f"User applied filter strategy: {song_filter.strategy_name}, matched {len(filtered)}/{len(songs)} songs")
        
        print(f"\n🔍 Filter: {song_filter.strategy_name}")
        print(f"   Matched: {len(filtered)}/{len(songs)} songs")
        print("-" * 40)
        
        if filtered:
            for i, song in enumerate(filtered, 1):
                print(f"{i}. {song.title}")
                print(f"   Artist: {song.artist} | Genre: {song.genre} | Duration: {self.format_duration(song.duration)}")
        else:
            print("No songs match the filter criteria")
    
    # ==================== MAIN LOOP ====================
    
    def run(self):
        """Main application loop."""
        actions = {
            "1": self.create_song,
            "2": self.view_all_songs,
            "3": self.search_songs,
            "4": self.update_song,
            "5": self.delete_song,
            "6": self.create_user,
            "7": self.view_all_users,
            "8": self.find_user,
            "9": self.update_user,
            "10": self.delete_user,
            "11": self.create_playlist,
            "12": self.view_all_playlists,
            "13": self.view_playlist_details,
            "14": self.update_playlist,
            "15": self.delete_playlist,
            "16": self.add_song_to_playlist,
            "17": self.remove_song_from_playlist,
            "18": self.sort_songs_demo,
            "19": self.filter_songs_demo,
        }
        
        while self.running:
            self.display_main_menu()
            choice = input("Select option: ").strip()
            
            if choice == "0":
                logger.info("User exiting application")
                print("\nGoodbye! 👋")
                self.running = False
            elif choice in actions:
                logger.info(f"User selected menu option: {choice}")
                try:
                    actions[choice]()
                except KeyboardInterrupt:
                    print("\n\nOperation cancelled")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    print(f"\n❌ Unexpected error: {e}")
            else:
                print("\n❌ Invalid option. Please try again.")
