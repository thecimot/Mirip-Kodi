
Mirip-Kodi (Media Library Scanner & MPV OSD Overlay)This project is an integrated, Kodi-style automated media library system consisting of two main components:scan_movies: A Python-based automated script to scan movie/TV series directories and download metadata and images from TMDB.  movie-info.lua: A Lua script for the MPV video player that reads scanned metadata and displays it as an interactive OSD interface (posters, synopses, genres, and a digital clock).  Key FeaturesAutomated Scanning: Recursively reads Movie and TV Series folders.  TMDB Integration: Automatically downloads media information and synopses in Indonesian (id-ID).  Asset Optimization: Downloads movie posters and compresses/sharpens clear logos (clearlogo.png) using Pillow.  Kodi-Style MPV Interface: Displays overlay posters, ratings, genre lists, cleanly wrapped synopses, a real-time clock, and an estimated movie completion time.  Smart Visibility: Information automatically appears when paused or on mouse movement, and auto-hides during playback.  System RequirementsBefore starting the installation, make sure your Linux system meets the following requirements:Operating System: Linux / Unix-based (The script reads external media directory paths like /run/media/...).  Python: Version 3.x or newer.  Media Player: MPV Player installed on your system.  System Utilities: ffmpeg and ffprobe (Standard on Linux; required by the MPV script for image processing).  Python DependenciesThe scanner script requires the third-party Pillow library to process images. Install it via your terminal:  Bashpip install Pillow
Environment Configuration (.bashrc)This script requires TMDB API authentication to function. It is recommended to use a TMDB Read Access Token (v4 auth) added to your .bashrc file.  How to Get a Free TMDB Token:Go to the official The Movie Database (TMDB) website and log into your account.  Click your profile icon in the top right corner and select Settings.  On the left sidebar, click the API tab.  Click the Create link under the "Request an API Key" section and select Developer.  Fill out the application details (you can set the application name to Mirip-Kodi and the URL to your GitHub repository).  After accepting the terms, locate the API Read Access Token (v4 auth) section (a long string of characters) and copy the entire token.  Exporting the Token to Your System:Run the following commands in your terminal to save the token into your Linux environment configuration:Bash# Add TMDB Token to .bashrc
echo 'export TMDB_TOKEN="your_v4_read_access_token_here"' >> ~/.bashrc

# Reload terminal configuration to apply changes immediately
source ~/.bashrc
Note: Replace "your_v4_read_access_token_here" with the actual v4 token copied from your TMDB dashboard before executing the command.  Installation StepsFollow these terminal commands to install the global scanner and MPV script side-by-side:1. Clone the RepositoryBashgit clone https://github.com/thecimot/Mirip-Kodi
cd Mirip-Kodi
2. Install the Scanner Script (scan_movies) System-WideTo execute the script globally from anywhere in your terminal without typing the .py extension:Bash# Create local bin folder if it does not exist
mkdir -p ~/.local/bin

# Copy the main scanner file
cp scan_movies ~/.local/bin/

# Grant execution permissions
chmod +x ~/.local/bin/scan_movies
Ensure ~/.local/bin is added to your system's $PATH variable in .bashrc.3. Customizing Configuration (scan_movies)You can customize media directory paths and language settings directly within the scan_movies script. Open the file in a text editor like Nano:  Bashnano ~/.local/bin/scan_movies
Locate the configuration section near the top of the file and adjust the parameters:a. Specify Media DirectoriesUpdate the paths inside Path("...") to match your local or external media storage paths:Python# ============================================================
# DIRECTORY CONFIGURATION
# ============================================================

MOVIES_DIR = Path("/run/media/cimot/cimot/MOVIES")
TV_DIR = Path("/run/media/cimot/cimot/TV SERIES")
b. Set Language PreferencesBy default, the script prioritizes Indonesian metadata with an English fallback if missing. You can modify these ISO 639-1 language codes as needed:  PythonPRIMARY_LANGUAGE = "id-ID"      # Primary metadata language (Indonesian)
FALLBACK_LANGUAGE = "en-US"     # Fallback language if primary is missing
Save changes by pressing Ctrl + O, hit Enter, and exit Nano with Ctrl + X.4. Install MPV Interface (movie-info.lua)Copy the Lua script directly into your MPV scripts directory:Bash# Create MPV scripts directory if it does not exist
mkdir -p ~/.config/mpv/scripts

# Copy OSD script
cp movie-info.lua ~/.config/mpv/scripts/
UsageScanning Media FilesRun the global command in your terminal to automatically process images and JSON metadata:Bashscan_movies
Viewing Metadata in MPVPlay a video file using MPV. The mini-OSD will display automatically on mouse movement or pause. To toggle the full panel (Poster and Synopsis), use these shortcuts:  = Key (Equal Sign)  Right-Click inside the MPV player window  Screenshotsa. Clear logo, genres, and digital clock display upon mouse movement and auto-hide after 10 seconds (default).
  b. Poster, rating, and synopsis toggle on Right-Click and hide upon second Right-Click.
  Sample Folder IncludedThe repository contains a sample movie folder with pre-generated metadata and posters to verify that movie-info.lua functions correctly inside MPV.  HAPPY WATCHING!LicenseDistributed under the MIT License. See code headers for copyright details by Hartono (2026).  
