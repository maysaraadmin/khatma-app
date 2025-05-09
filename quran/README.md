# Quran App

This app provides Quran functionality for the Khatma project, including Quran reading, recitation, and search capabilities.

## Features

- Complete Quran text with Arabic and translation
- Quran recitation audio
- Quran search functionality
- Bookmarking system
- Reading settings (font size, night mode, etc.)
- Juz (part) and Surah (chapter) navigation

## Models

The app defines the following models:

- **QuranPart**: Represents a Juz' (part) of the Quran
- **Surah**: Represents a Surah (chapter) of the Quran
- **Ayah**: Represents an Ayah (verse) of the Quran
- **QuranReciter**: Represents a Quran reciter
- **ReciterSurah**: Represents a Surah recited by a specific reciter
- **QuranRecitation**: Represents a specific recitation of a Surah or Ayah
- **QuranTranslation**: Represents a translation of the Quran
- **QuranBookmark**: Represents a user's bookmark in the Quran
- **QuranReadingSettings**: Represents a user's Quran reading settings

## Views

The app provides the following views:

- **quran_home**: Main Quran view showing reciters and surahs
- **surah_list**: View for listing all Surahs
- **surah_detail**: View for displaying a specific Surah
- **juz_list**: View for listing all Juz' (parts)
- **juz_detail**: View for displaying a specific Juz' (part)
- **reciter_list**: View for listing all Quran reciters
- **reciter_detail**: View for displaying a specific reciter's details and recitations
- **search_quran**: View for searching the Quran
- **bookmark_ayah**: View for bookmarking an ayah
- **bookmarks_list**: View for listing user's bookmarks
- **delete_bookmark**: View for deleting a bookmark
- **reading_settings**: View for managing user's Quran reading settings
- **update_last_read**: AJAX view for updating last read position
- **continue_reading**: View for continuing from last read position
- **list_reciters**: View for listing available Quran reciters
- **reciter_surahs**: View for displaying surahs available for a specific reciter
- **quran_part_view**: View for displaying a specific Quran part for reading
- **khatma_quran_chapters**: View for displaying Quran chapters for Khatma selection

## Services

The app provides the following service functions:

- **get_quran_home_data**: Get data for the Quran home page
- **get_surah_detail**: Get detailed information about a surah
- **get_part_detail**: Get detailed information about a Quran part (juz)
- **get_reciter_detail**: Get detailed information about a reciter
- **update_reading_settings**: Update user's Quran reading settings
- **search_quran**: Search the Quran for text

## URLs

The app defines the following URL patterns:

- `/`: Quran home page
- `surah/`: List of all Surahs
- `surah/<int:surah_number>/`: Detail view of a specific Surah
- `juz/`: List of all Juz' (parts)
- `juz/<int:part_number>/`: Detail view of a specific Juz' (part)
- `part/<int:part_number>/`: Display a specific Quran part for reading
- `reciters/`: List of all Quran reciters
- `reciters/<int:reciter_id>/`: Detail view of a specific reciter
- `reciters/<str:reciter_name>/`: Display surahs available for a specific reciter
- `search/`: Search the Quran
- `bookmark/<int:surah_number>/<int:ayah_number>/`: Bookmark an ayah
- `bookmarks/`: List of user's bookmarks
- `bookmarks/delete/<int:bookmark_id>/`: Delete a bookmark
- `settings/`: Manage Quran reading settings
- `update-last-read/`: Update last read position
- `continue-reading/`: Continue from last read position
- `chapters/`: Display Quran chapters for Khatma selection

## Forms

The app defines the following forms:

- **QuranBookmarkForm**: Form for creating and editing bookmarks
- **QuranReadingSettingsForm**: Form for managing reading settings
- **QuranSearchForm**: Form for searching the Quran
- **ReciterFilterForm**: Form for filtering reciters

## Templates

The app uses the following templates:

- **quran_home.html**: Main Quran page
- **surah_list.html**: List of all Surahs
- **surah_detail.html**: Detail view of a specific Surah
- **juz_list.html**: List of all Juz' (parts)
- **juz_detail.html**: Detail view of a specific Juz' (part)
- **reciter_list.html**: List of all Quran reciters
- **reciter_detail.html**: Detail view of a specific reciter
- **search.html**: Search the Quran
- **bookmark_form.html**: Form for creating and editing bookmarks
- **bookmarks_list.html**: List of user's bookmarks
- **delete_bookmark.html**: Confirm deletion of a bookmark
- **reading_settings.html**: Manage Quran reading settings
- **reciter_surahs.html**: Display surahs available for a specific reciter
- **part_view.html**: Display a specific Quran part for reading
- **khatma_chapters.html**: Display Quran chapters for Khatma selection

## Static Files

The app uses the following static files:

- **css/quran.css**: Styles for Quran display
- **js/quran.js**: JavaScript for Quran functionality
- **js/audio-player.js**: JavaScript for audio player functionality
- **img/quran-bg.jpg**: Background image for Quran pages
