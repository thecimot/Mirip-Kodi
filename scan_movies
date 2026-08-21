#!/usr/bin/env python3

import os
import re
import json
import shutil
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from PIL import Image, ImageFilter


# ============================================================
# KONFIGURASI DIREKTORI
# ============================================================

MOVIES_DIR = Path("/run/media/cimot/cimot/MOVIES")
TV_DIR = Path("/run/media/cimot/cimot/TV SERIES")

# ------------------------------------------------------------
# AUTENTIKASI TMDB
# ------------------------------------------------------------
TMDB_READ_TOKEN = os.getenv("TMDB_TOKEN", "").strip()
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()

PRIMARY_LANGUAGE = "id-ID"
FALLBACK_LANGUAGE = "en-US"

POSTER_SIZE = "w780"
LOGO_SIZE = "original"

# Kontrol penimpaan file
SKIP_EXISTING = True
FORCE_RESCAN = False


# ============================================================
# HELPER OUTPUT
# ============================================================

def line():
    print("=" * 70)


def print_error(message):
    print(f"ERROR: {message}")


def print_warning(message):
    print(f"WARNING: {message}")


# ============================================================
# IMAGE PROCESSING (FIX DEPRECATION WARNING)
# ============================================================

def process_clearlogo(file_path):
    try:
        with Image.open(file_path) as img:
            img = img.convert("RGBA")
            clean_img = img.copy()

            width, height = clean_img.size
            if width > 3000 or height > 3000:
                new_size = (width // 2, height // 2)
                clean_img = clean_img.resize(new_size, Image.Resampling.LANCZOS)

            sharpened_img = clean_img.filter(ImageFilter.SHARPEN)
            sharpened_img.save(file_path, "PNG", optimize=True)
        return True
    except Exception as error:
        print_warning(f"Gagal memproses logo {file_path.name}: {error}")
        return False


def process_all_existing_logos(root_dir):
    root_path = Path(root_dir)
    if not root_path.exists():
        return

    print(f"Memproses & menajamkan semua clearlogo.png di {root_path}...")
    count = 0
    for logo_file in root_path.rglob("clearlogo.png"):
        if process_clearlogo(logo_file):
            count += 1
    print(f"Selesai! Berhasil memproses {count} file clearlogo.png.")


# ============================================================
# TMDB REQUEST WITH SYNOPSIS FALLBACK & DOWNLOAD
# ============================================================

def tmdb_request(endpoint, params=None, language=None):
    if params is None:
        params = {}

    if language:
        params["language"] = language

    headers = {
        "Accept": "application/json",
        "User-Agent": "MovieLibraryScanner/1.0",
    }

    if TMDB_READ_TOKEN:
        headers["Authorization"] = f"Bearer {TMDB_READ_TOKEN}"
    elif TMDB_API_KEY:
        params["api_key"] = TMDB_API_KEY
    else:
        print_error("TMDB_TOKEN atau TMDB_API_KEY belum diatur.")
        return None

    query = urllib.parse.urlencode(params)
    url = f"https://api.themoviedb.org/3{endpoint}"
    if query:
        url += f"?{query}"

    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as error:
        print_error(f"TMDB request gagal ({endpoint}): {error}")
        return None


def fetch_details_with_id_synopsis(endpoint):
    details_id = tmdb_request(endpoint, language=PRIMARY_LANGUAGE)
    if not details_id:
        return tmdb_request(endpoint, language=FALLBACK_LANGUAGE)

    if not details_id.get("overview") or details_id.get("overview").strip() == "":
        details_en = tmdb_request(endpoint, language=FALLBACK_LANGUAGE)
        if details_en and details_en.get("overview"):
            details_id["overview"] = details_en["overview"]

    return details_id


def download_file(url, destination):
    destination = Path(destination)
    if SKIP_EXISTING and destination.exists() and not FORCE_RESCAN:
        print(f"      File {destination.name} sudah ada, dilewati.")
        return True

    try:
        request = urllib.request.Request(url, headers={"User-Agent": "MovieLibraryScanner/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            with open(destination, "wb") as output:
                shutil.copyfileobj(response, output)
        return True
    except Exception as error:
        print_error(f"Gagal download {destination.name}: {error}")
        return False


# ============================================================
# EXTRACT TITLE, YEAR & SEASON
# ============================================================

def normalize_name(text):
    text = str(text)
    text = re.sub(r"[._]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_movie_info(folder_name):
    text = normalize_name(folder_name)
    
    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
    year = year_match.group(1) if year_match else None
    
    if year_match:
        title = text[:year_match.start()].strip()
    else:
        scene_junk = r"\b(1080p|720p|2160p|4k|bluray|webrip|web-dl|hdrip|x265|x264|hevc|10bit|aac|ddp\d?|galaxyrg\d*|yts|asimov|tgx)\b"
        title = re.split(scene_junk, text, flags=re.IGNORECASE)[0]
    
    title = re.sub(r"[\(\[\{\)\]\}]", "", title).strip(" -_.")
    return title, year


def extract_season_number(text):
    match = re.search(r"\bS(\d{1,2})\b|\bSeason\s*(\d{1,2})\b", text, re.IGNORECASE)
    if match:
        return int(match.group(1) or match.group(2))
    return None


def clean_tv_title(raw_name):
    text = normalize_name(raw_name)
    text = re.split(r"\b(S\d{1,2}|Season\s*\d{1,2})\b", text, flags=re.IGNORECASE)[0]
    text = re.sub(r"(?<!\d)(19\d{2}|20\d{2})(?!\d)", " ", text)
    return text.strip(" -_.")


def search_movie(title, year=None):
    print(f"Mencari Movie '{title}' ({year or 'Tahun N/A'}) di TMDB...")
    endpoint = "/search/movie"
    params = {"query": title, "include_adult": "false"}
    if year:
        params["year"] = year

    res = tmdb_request(endpoint, params=params, language=PRIMARY_LANGUAGE)
    if res and res.get("results"):
        return res["results"][0]

    res = tmdb_request(endpoint, params=params, language=FALLBACK_LANGUAGE)
    if res and res.get("results"):
        return res["results"][0]

    return None


def search_tv_show(title):
    print(f"Mencari TV Show '{title}' di TMDB...")
    endpoint = "/search/tv"

    res = tmdb_request(endpoint, params={"query": title, "include_adult": "false"}, language=PRIMARY_LANGUAGE)
    if res and res.get("results"):
        return res["results"][0]

    res = tmdb_request(endpoint, params={"query": title, "include_adult": "false"}, language=FALLBACK_LANGUAGE)
    if res and res.get("results"):
        return res["results"][0]

    return None


def get_clearlogo(tmdb_id, is_movie=True, season_num=None):
    if is_movie:
        endpoint = f"/movie/{tmdb_id}/images"
    else:
        endpoint = f"/tv/{tmdb_id}/season/{season_num}/images" if season_num is not None else f"/tv/{tmdb_id}/images"

    images = tmdb_request(endpoint)

    if not is_movie and (not images or "logos" not in images or not images["logos"]) and season_num is not None:
        images = tmdb_request(f"/tv/{tmdb_id}/images")

    if not images or "logos" not in images or not images["logos"]:
        return None

    logos = [l for l in images["logos"] if not l.get("file_path", "").lower().endswith(".svg")]
    if not logos:
        return None

    for lang in ["id", "en", None]:
        matching = [l for l in logos if l.get("iso_639_1") == lang]
        if matching:
            matching.sort(key=lambda x: x.get("width", 0), reverse=True)
            return matching[0].get("file_path")

    logos.sort(key=lambda x: x.get("width", 0), reverse=True)
    return logos[0].get("file_path")


# ============================================================
# MODULE 1: SCAN MOVIES
# ============================================================

def process_movie_folder(movie_folder):
    line()
    print(f"Processing Movie Folder: {movie_folder.name}")

    meta_file = movie_folder / "metadata.json"
    poster_file = movie_folder / "poster.jpg"
    logo_file = movie_folder / "clearlogo.png"

    if SKIP_EXISTING and meta_file.exists() and poster_file.exists() and logo_file.exists() and not FORCE_RESCAN:
        print("  Status: Semua metadata & gambar sudah lengkap, dilewati.")
        return

    clean_title, year = extract_movie_info(movie_folder.name)
    search_result = search_movie(clean_title, year)

    if not search_result:
        print_error(f"  Movie '{clean_title}' tidak ditemukan di TMDB.")
        return

    tmdb_id = search_result.get("id")
    details = fetch_details_with_id_synopsis(f"/movie/{tmdb_id}")

    if not details:
        print_error(f"  Gagal mengambil detail Movie ID {tmdb_id}")
        return

    genres = [g.get("name") for g in details.get("genres", [])]

    if not (SKIP_EXISTING and meta_file.exists() and not FORCE_RESCAN):
        metadata = {
            "tmdb_id": tmdb_id,
            "media_type": "movie",
            "title": details.get("title") or clean_title,
            "original_title": details.get("original_title"),
            "year": details.get("release_date", "")[:4] if details.get("release_date") else year,
            "release_date": details.get("release_date"),
            "vote_average": details.get("vote_average", 0),
            "genres": genres,
            "overview": details.get("overview", ""),
            "runtime": details.get("runtime"),
        }
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        print("  metadata.json dibuat.")

    if details.get("poster_path") and not (SKIP_EXISTING and poster_file.exists() and not FORCE_RESCAN):
        poster_url = f"https://image.tmdb.org/t/p/{POSTER_SIZE}{details['poster_path']}"
        download_file(poster_url, poster_file)

    if not (SKIP_EXISTING and logo_file.exists() and not FORCE_RESCAN):
        logo_path = get_clearlogo(tmdb_id, is_movie=True)
        if logo_path:
            logo_url = f"https://image.tmdb.org/t/p/{LOGO_SIZE}{logo_path}"
            if download_file(logo_url, logo_file):
                process_clearlogo(logo_file)


def scan_movies(root_dir):
    line()
    print("SCANNING MOVIES DIRECTORY:", root_dir)
    line()

    if not root_dir.exists():
        print_error(f"Direktori MOVIES tidak ditemukan: {root_dir}")
        return

    for path in sorted(root_dir.iterdir()):
        if path.is_dir():
            process_movie_folder(path)


# ============================================================
# MODULE 2: SCAN TV SERIES
# ============================================================

def process_tv_season(season_folder, tmdb_id, season_num, main_title, show_genres, main_overview=""):
    print(f"  └── Processing Season Folder: {season_folder.name} (Season {season_num})")

    season_meta_file = season_folder / "season_metadata.json"
    poster_file = season_folder / "poster.jpg"
    logo_file = season_folder / "clearlogo.png"

    if SKIP_EXISTING and season_meta_file.exists() and poster_file.exists() and logo_file.exists() and not FORCE_RESCAN:
        print("      Status: Metadata & Gambar Season sudah lengkap, dilewati.")
        return

    endpoint = f"/tv/{tmdb_id}/season/{season_num}"
    season_details = fetch_details_with_id_synopsis(endpoint)

    if not season_details:
        print_warning(f"      Gagal mengambil detail untuk Season {season_num}")
        return

    season_name_tmdb = season_details.get("name") or f"Season {season_num}"

    overview = season_details.get("overview", "").strip()
    if not overview:
        overview = main_overview

    if not (SKIP_EXISTING and season_meta_file.exists() and not FORCE_RESCAN):
        metadata = {
            "tmdb_id": tmdb_id,
            "show_title": main_title,
            "season_number": season_num,
            "season_name": season_name_tmdb,
            "title": main_title,
            "genres": show_genres,
            "overview": overview,
            "air_date": season_details.get("air_date", ""),
            "poster_path": season_details.get("poster_path"),
            "episodes_count": len(season_details.get("episodes", [])),
        }
        with open(season_meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        print("      season_metadata.json dibuat.")

    poster_path = season_details.get("poster_path")
    if poster_path and not (SKIP_EXISTING and poster_file.exists() and not FORCE_RESCAN):
        poster_url = f"https://image.tmdb.org/t/p/{POSTER_SIZE}{poster_path}"
        download_file(poster_url, poster_file)

    if not (SKIP_EXISTING and logo_file.exists() and not FORCE_RESCAN):
        logo_path = get_clearlogo(tmdb_id, is_movie=False, season_num=season_num)
        if logo_path:
            logo_url = f"https://image.tmdb.org/t/p/{LOGO_SIZE}{logo_path}"
            if download_file(logo_url, logo_file):
                process_clearlogo(logo_file)


def scan_tv_series(root_dir):
    line()
    print("SCANNING TV SERIES RECURSIVELY:", root_dir)
    line()

    if not root_dir.exists():
        print_error(f"Direktori TV SERIES tidak ditemukan: {root_dir}")
        return

    tmdb_cache = {}

    for path in sorted(root_dir.iterdir()):
        if not path.is_dir():
            continue

        clean_title = clean_tv_title(path.name)
        season_num_direct = extract_season_number(path.name)

        if not clean_title:
            continue

        if clean_title not in tmdb_cache:
            search_result = search_tv_show(clean_title)
            if not search_result:
                print_error(f"Serial '{clean_title}' tidak ditemukan di TMDB.")
                continue

            tmdb_id = search_result.get("id")
            details = fetch_details_with_id_synopsis(f"/tv/{tmdb_id}")

            main_title = clean_title
            show_genres = []
            main_overview = ""

            if details:
                main_title = details.get("name") or clean_title
                show_genres = [g.get("name") for g in details.get("genres", [])]
                main_overview = details.get("overview", "").strip()

            tmdb_cache[clean_title] = {
                "tmdb_id": tmdb_id,
                "main_title": main_title,
                "genres": show_genres,
                "main_overview": main_overview,
                "details": details
            }
        
        show_info = tmdb_cache[clean_title]

        if season_num_direct is not None:
            line()
            print(f"Folder Season Langsung: {path.name}")
            process_tv_season(
                path, 
                show_info["tmdb_id"], 
                season_num_direct, 
                show_info["main_title"], 
                show_info["genres"],
                show_info["main_overview"]
            )
        else:
            line()
            print(f"Folder Induk Serial: {path.name}")
            main_meta_file = path / "metadata.json"
            main_poster = path / "poster.jpg"
            main_logo = path / "clearlogo.png"

            if show_info["details"]:
                if not (SKIP_EXISTING and main_meta_file.exists() and not FORCE_RESCAN):
                    main_metadata = {
                        "tmdb_id": show_info["tmdb_id"],
                        "media_type": "tv",
                        "title": show_info["main_title"],
                        "original_title": show_info["details"].get("original_name"),
                        "first_air_date": show_info["details"].get("first_air_date"),
                        "vote_average": show_info["details"].get("vote_average", 0),
                        "genres": show_info["genres"],
                        "overview": show_info["main_overview"],
                    }
                    with open(main_meta_file, "w", encoding="utf-8") as f:
                        json.dump(main_metadata, f, ensure_ascii=False, indent=4)

                if show_info["details"].get("poster_path") and not (SKIP_EXISTING and main_poster.exists() and not FORCE_RESCAN):
                    download_file(f"https://image.tmdb.org/t/p/{POSTER_SIZE}{show_info['details']['poster_path']}", main_poster)

                if not (SKIP_EXISTING and main_logo.exists() and not FORCE_RESCAN):
                    logo_path = get_clearlogo(show_info["tmdb_id"], is_movie=False)
                    if logo_path:
                        if download_file(f"https://image.tmdb.org/t/p/{LOGO_SIZE}{logo_path}", main_logo):
                            process_clearlogo(main_logo)

            for subfolder in path.iterdir():
                if subfolder.is_dir():
                    s_num = extract_season_number(subfolder.name)
                    if s_num is not None:
                        process_tv_season(
                            subfolder, 
                            show_info["tmdb_id"], 
                            s_num, 
                            show_info["main_title"], 
                            show_info["genres"],
                            show_info["main_overview"]
                        )


# ============================================================
# MAIN SCANNER
# ============================================================

def main():
    line()
    print("             MEDIA LIBRARY SCANNER (CLEAN LOG RUN)")
    line()

    if not TMDB_READ_TOKEN and not TMDB_API_KEY:
        print_error("TMDB_TOKEN atau TMDB_API_KEY belum diatur di sistem Anda.")
        return

    scan_movies(MOVIES_DIR)
    scan_tv_series(TV_DIR)

    line()
    print("PROSES SCAN SELESAI!")
    line()


if __name__ == "__main__":
    main()
