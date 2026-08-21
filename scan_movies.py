
#!/usr/bin/env python3

import os
import re
import json
import shutil
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path


# ============================================================
# KONFIGURASI
# ============================================================

MOVIES_DIR = Path("/run/media/cimot/cimot/MOVIES")
TV_DIR = Path("/run/media/cimot/cimot/TV SERIES")

# ------------------------------------------------------------
# PILIH SALAH SATU AUTENTIKASI TMDB
#
# 1. API Read Access Token
#    biasanya diawali eyJ...
#
# ATAU
#
# 2. API Key v3
# ------------------------------------------------------------

TMDB_READ_TOKEN = os.getenv("TMDB_TOKEN", "").strip()

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()


# Bahasa metadata
LANGUAGE = "id-ID"

# Bahasa fallback jika metadata Indonesia kosong
FALLBACK_LANGUAGE = "en-US"

# Ukuran poster TMDB
POSTER_SIZE = "w780"

# Ukuran clear logo
LOGO_SIZE = "w500"

# Lewati folder yang sudah memiliki metadata.json
SKIP_EXISTING = True

# Jika True, metadata lama akan dibuat ulang
FORCE_RESCAN = False

# Ekstensi video yang dikenali
VIDEO_EXTENSIONS = {
    ".mkv",
    ".mp4",
    ".avi",
    ".mov",
    ".m4v",
    ".webm",
    ".ts",
    ".mpeg",
    ".mpg",
}


# ============================================================
# OUTPUT
# ============================================================

def line():
    print("=" * 70)


def print_error(message):
    print(f"ERROR: {message}")


def print_warning(message):
    print(f"WARNING: {message}")


# ============================================================
# TMDB REQUEST
# ============================================================

def tmdb_request(endpoint, params=None, language=None):
    """
    Request ke TMDB API v3.

    Mendukung:
    - TMDB Read Access Token
    - API Key v3
    """

    if params is None:
        params = {}

    if language:
        params["language"] = language

    headers = {
        "Accept": "application/json",
        "User-Agent": "MovieLibraryScanner/1.0",
    }

    # API Read Access Token
    if TMDB_READ_TOKEN:
        headers["Authorization"] = (
            f"Bearer {TMDB_READ_TOKEN}"
        )

    # API Key v3
    elif TMDB_API_KEY:
        params["api_key"] = TMDB_API_KEY

    else:
        print_error(
            "TMDB_TOKEN atau TMDB_API_KEY belum diatur."
        )
        return None

    query = urllib.parse.urlencode(params)

    url = (
        f"https://api.themoviedb.org/3"
        f"{endpoint}"
    )

    if query:
        url += f"?{query}"

    request = urllib.request.Request(
        url,
        headers=headers,
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=20,
        ) as response:

            data = response.read()

            return json.loads(
                data.decode("utf-8")
            )

    except urllib.error.HTTPError as error:

        print(
            f"TMDB HTTP: {error.code}"
        )

        try:
            body = error.read().decode(
                "utf-8",
                errors="replace",
            )

            print(body)

        except Exception:
            pass

        return None

    except urllib.error.URLError as error:

        print_error(
            f"Koneksi TMDB gagal: {error.reason}"
        )

        return None

    except Exception as error:

        print_error(
            f"TMDB request gagal: {error}"
        )

        return None


# ============================================================
# DOWNLOAD FILE
# ============================================================

def download_file(url, destination):
    """
    Download file ke destination.
    """

    destination = Path(destination)

    try:

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "MovieLibraryScanner/1.0"
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=60,
        ) as response:

            with open(destination, "wb") as output:

                shutil.copyfileobj(
                    response,
                    output,
                )

        return True

    except Exception as error:

        print_error(
            f"Gagal download {destination.name}: {error}"
        )

        return False


# ============================================================
# FIND VIDEO
# ============================================================

def find_video(folder):
    """
    Cari file video pertama secara rekursif.

    Folder TV kadang memiliki struktur:

    Breaking Bad/
        Season 01/
            episode.mkv
    """

    videos = []

    try:

        for path in folder.rglob("*"):

            if not path.is_file():
                continue

            if path.suffix.lower() in VIDEO_EXTENSIONS:

                videos.append(path)

    except Exception as error:

        print_error(
            f"Gagal membaca folder: {error}"
        )

        return None

    if not videos:
        return None

    videos.sort()

    return videos[0]


# ============================================================
# CLEAN NAME
# ============================================================

def normalize_name(text):
    """
    Ubah:

    Dune.Part.Two.2024
    →
    Dune Part Two 2024
    """

    text = str(text)

    # Ganti separator umum menjadi spasi
    text = re.sub(
        r"[._]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# REMOVE BRACKETED RELEASE TAGS
# ============================================================

def remove_release_brackets(text):
    """
    Hapus tag seperti:

    [1080p]
    [BluRay]
    [YTS MX]
    [TGx]

    tetapi jangan terlalu agresif.
    """

    text = re.sub(
        r"\[[^\]]+\]",
        " ",
        text,
    )

    return text


# ============================================================
# RELEASE KEYWORDS
# ============================================================

RELEASE_PATTERNS = [

    # Resolution
    r"\b\d{3,4}p\b",
    r"\b2160p\b",
    r"\b1440p\b",
    r"\b1080p\b",
    r"\b720p\b",
    r"\b480p\b",

    # Source
    r"\bBluRay\b",
    r"\bBDRip\b",
    r"\bBRRip\b",
    r"\bWEBRip\b",
    r"\bWEB-DL\b",
    r"\bWEB DL\b",
    r"\bWEB\b",
    r"\bHDTV\b",
    r"\bDVDRip\b",
    r"\bDVD\b",
    r"\bAMZN\b",
    r"\bNF\b",
    r"\bPCOK\b",
    r"\bDS4K\b",
    r"\bMA\b",

    # Codec
    r"\bx264\b",
    r"\bx265\b",
    r"\bH\.?264\b",
    r"\bH\.?265\b",
    r"\bHEVC\b",
    r"\bAV1\b",
    r"\bAVC\b",
    r"\b10bit\b",
    r"\b8bit\b",

    # Audio
    r"\bAAC\b",
    r"\bAC3\b",
    r"\bEAC3\b",
    r"\bDDP?\b",
    r"\bDDP\d+(?:\.\d+)?\b",
    r"\bDTS(?:-HD)?\b",
    r"\bTRUEHD\b",
    r"\bATMOS\b",
    r"\bFLAC\b",
    r"\bOPUS\b",
    r"\bMP3\b",
    r"\b6CH\b",
    r"\b2CH\b",
    r"\b5\s*1\b",
    r"\b7\s*1\b",

    # Misc release
    r"\bCOMPLETE\b",
    r"\bUNCUT\b",
    r"\bREPACK\b",
    r"\bPROPER\b",
    r"\bREMUX\b",
    r"\bINTERNAL\b",
    r"\bEXTENDED\b",
    r"\bLIMITED\b",
    r"\bDUAL-AUDIO\b",
    r"\bMULTI\d*\b",

    # Language
    r"\bINDONESIAN\b",
    r"\bIND\b",
    r"\bENG\b",
    r"\bGER\b",
    r"\bSPA\b",
    r"\bKOR\b",
    r"\bJPN\b",
    r"\bITA\b",
    r"\bFRE\b",
    r"\bRUS\b",
    r"\bCHINESE\b",
]


# ============================================================
# REMOVE RELEASE INFORMATION
# ============================================================

def remove_release_info(text):
    """
    Bersihkan informasi release.

    Contoh:

    28 Days Later 2002 1080p BluRay DDP5 1 x265

    menjadi:

    28 Days Later 2002
    """

    # Hilangkan [TAG]
    text = remove_release_brackets(text)

    # Hapus bagian setelah release group
    #
    # Contoh:
    #
    # x265-PSA
    # x265-KONTRAST
    # HEVC-PSA
    #
    text = re.sub(
        r"-(?:GalaxyRG\d*|PSA|KONTRAST|MeGusta|"
        r"YTS(?:MX)?|RAV1NE|Asiimov|"
        r"Saon-nAV1gator|dAV1nci|"
        r"HETeam|AMBER|SAMPA)"
        r".*$",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    # Hapus setiap release keyword
    for pattern in RELEASE_PATTERNS:

        text = re.sub(
            pattern,
            " ",
            text,
            flags=re.IGNORECASE,
        )

    # Bersihkan tanda - yang tersisa
    text = re.sub(
        r"\s*-\s*",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# EXTRACT YEAR
# ============================================================

def extract_year(text):
    """
    Cari tahun film.

    1900-2099
    """

    match = re.search(
        r"(?<!\d)"
        r"(19\d{2}|20\d{2})"
        r"(?!\d)",
        text,
    )

    if match:
        return match.group(1)

    return None


# ============================================================
# EXTRACT TV SEASON
# ============================================================

def extract_season(text):
    """
    Cari:

    S01
    Season 1
    SEASON 01
    """

    patterns = [

        r"\bS(\d{1,2})\b",

        r"\bSeason\s*(\d{1,2})\b",

        r"\bSEASON\s*(\d{1,2})\b",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:

            return int(
                match.group(1)
            )

    return None


# ============================================================
# EXTRACT TITLE
# ============================================================

def extract_title(raw_name, media_type):
    """
    Menghasilkan:

    title
    year
    season
    """

    # Normalisasi awal
    text = normalize_name(raw_name)

    # Hilangkan extension jika ikut terbaca
    text = re.sub(
        r"\.[A-Za-z0-9]{2,4}$",
        "",
        text,
    )

    # Tahun dari nama asli
    year = extract_year(text)

    # Season TV
    season = None

    if media_type == "tv":

        season = extract_season(text)

    # --------------------------------------------------------
    # STOP TITLE PADA TAHUN
    #
    # 28 Days Later (2002) 1080p
    # ↓
    # 28 Days Later
    # --------------------------------------------------------

    year_match = re.search(
        r"(?<!\d)"
        r"(19\d{2}|20\d{2})"
        r"(?!\d)",
        text,
    )

    if year_match:

        before_year = (
            text[:year_match.start()]
        )

        after_year = (
            text[year_match.end():]
        )

        # Jika sebelum tahun masih punya judul,
        # kita gunakan bagian sebelum tahun.
        if before_year.strip():

            text = before_year

        else:

            text = (
                before_year
                + " "
                + after_year
            )

    # --------------------------------------------------------
    # TV:
    #
    # Fool Me Once S01
    # ↓
    # Fool Me Once
    #
    # From Season 3
    # ↓
    # From
    # --------------------------------------------------------

    if media_type == "tv":

        text = re.split(
            r"\bS\d{1,2}(?:E\d{1,2})?\b",
            text,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]

        text = re.split(
            r"\bSeason\s*\d{1,2}\b",
            text,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]

    # Bersihkan release info
    text = remove_release_info(text)

    # Bersihkan tanda kurung rusak
    text = text.replace("(", " ")
    text = text.replace(")", " ")
    text = text.replace("[", " ")
    text = text.replace("]", " ")

    # Bersihkan apostrophe aneh
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    # Buang kata kosong di akhir
    text = text.strip(
        " -_."
    )

    return (
        text,
        year,
        season,
    )


# ============================================================
# SEARCH TMDB
# ============================================================

def search_tmdb(title, year, media_type):
    """
    Cari media di TMDB.
    """

    endpoint = (
        "/search/movie"
        if media_type == "movie"
        else "/search/tv"
    )

    params = {
        "query": title,
        "include_adult": "false",
    }

    if year:

        if media_type == "movie":

            params["year"] = year

        else:

            params[
                "first_air_date_year"
            ] = year

    result = tmdb_request(
        endpoint,
        params=params,
        language=LANGUAGE,
    )

    if not result:
        return None

    results = result.get(
        "results",
        [],
    )

    if results:

        return results[0]

    return None


# ============================================================
# SEARCH WITH FALLBACK
# ============================================================

def search_media(title, year, media_type):

    print("Mencari di TMDB...")

    # Pertama dengan tahun
    if year:

        result = search_tmdb(
            title,
            year,
            media_type,
        )

        if result:
            return result

        print(
            "Pencarian dengan tahun gagal."
        )

    # Kedua tanpa tahun
    print(
        "Mencoba tanpa tahun..."
    )

    result = search_tmdb(
        title,
        None,
        media_type,
    )

    if result:
        return result

    # Fallback bahasa Inggris
    print(
        "Mencoba metadata bahasa Inggris..."
    )

    endpoint = (
        "/search/movie"
        if media_type == "movie"
        else "/search/tv"
    )

    params = {
        "query": title,
        "include_adult": "false",
    }

    result_data = tmdb_request(
        endpoint,
        params=params,
        language=FALLBACK_LANGUAGE,
    )

    if result_data:

        results = result_data.get(
            "results",
            [],
        )

        if results:
            return results[0]

    return None


# ============================================================
# GET DETAILS
# ============================================================

def get_details(tmdb_id, media_type):

    endpoint = (
        f"/movie/{tmdb_id}"
        if media_type == "movie"
        else f"/tv/{tmdb_id}"
    )

    return tmdb_request(
        endpoint,
        params={},
        language=LANGUAGE,
    )


# ============================================================
# GET FALLBACK DETAILS
# ============================================================

def get_details_fallback(
    tmdb_id,
    media_type,
):

    endpoint = (
        f"/movie/{tmdb_id}"
        if media_type == "movie"
        else f"/tv/{tmdb_id}"
    )

    return tmdb_request(
        endpoint,
        params={},
        language=FALLBACK_LANGUAGE,
    )


# ============================================================
# GET LOGO
# ============================================================

def get_clearlogo(
    tmdb_id,
    media_type,
):

    endpoint = (
        f"/movie/{tmdb_id}/images"
        if media_type == "movie"
        else f"/tv/{tmdb_id}/images"
    )

    images = tmdb_request(
        endpoint,
        params={},
        language=None,
    )

    if not images:
        return None

    logos = images.get(
        "logos",
        [],
    )

    if not logos:
        return None

    # Prioritas Indonesia
    preferred_languages = [

        "id",
        "en",
        None,
    ]

    for language in preferred_languages:

        for logo in logos:

            if (
                logo.get("iso_639_1")
                == language
            ):

                file_path = logo.get(
                    "file_path"
                )

                if file_path:
                    return file_path

    # Kalau tidak ada, ambil logo pertama
    return logos[0].get(
        "file_path"
    )


# ============================================================
# BUILD METADATA
# ============================================================

def build_metadata(
    details,
    media_type,
    detected_year,
    detected_season,
):

    if media_type == "movie":

        title = (
            details.get("title")
            or details.get(
                "original_title"
            )
            or "Unknown"
        )

        release_date = (
            details.get(
                "release_date"
            )
            or ""
        )

    else:

        title = (
            details.get("name")
            or details.get(
                "original_name"
            )
            or "Unknown"
        )

        release_date = (
            details.get(
                "first_air_date"
            )
            or ""
        )

    year = detected_year

    if not year and release_date:

        match = re.match(
            r"(\d{4})",
            release_date,
        )

        if match:

            year = match.group(1)

    genres = []

    for genre in details.get(
        "genres",
        [],
    ):

        name = genre.get(
            "name"
        )

        if name:

            genres.append(name)

    metadata = {

        "tmdb_id":
            details.get("id"),

        "media_type":
            media_type,

        "title":
            title,

        "original_title":
            (
                details.get(
                    "original_title"
                )
                if media_type == "movie"
                else details.get(
                    "original_name"
                )
            ),

        "year":
            year or "",

        "release_date":
            release_date,

        "vote_average":
            details.get(
                "vote_average",
                0,
            ),

        "vote_count":
            details.get(
                "vote_count",
                0,
            ),

        "genres":
            genres,

        "overview":
            details.get(
                "overview",
                ""
            ),

        "tagline":
            details.get(
                "tagline",
                ""
            ),

        "poster_path":
            details.get(
                "poster_path"
            ),

        "backdrop_path":
            details.get(
                "backdrop_path"
            ),

        "season":
            detected_season,

        "number_of_seasons":
            (
                details.get(
                    "number_of_seasons"
                )
                if media_type == "tv"
                else None
            ),

        "number_of_episodes":
            (
                details.get(
                    "number_of_episodes"
                )
                if media_type == "tv"
                else None
            ),

    }

    return metadata


# ============================================================
# WRITE METADATA
# ============================================================

def write_metadata(
    folder,
    metadata,
):

    path = (
        folder
        / "metadata.json"
    )

    try:

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as output:

            json.dump(
                metadata,
                output,
                ensure_ascii=False,
                indent=4,
            )

        return True

    except Exception as error:

        print_error(
            f"Gagal menulis metadata.json: {error}"
        )

        return False


# ============================================================
# PROCESS FOLDER
# ============================================================

def process_folder(
    folder,
    media_type,
):

    line()

    print(
        f"Folder : {folder.name}"
    )

    metadata_file = (
        folder
        / "metadata.json"
    )

    if (
        SKIP_EXISTING
        and metadata_file.exists()
        and not FORCE_RESCAN
    ):

        print(
            "Status : metadata.json sudah ada, dilewati."
        )

        return

    # --------------------------------------------------------
    # Cari video
    # --------------------------------------------------------

    video = find_video(folder)

    if video:

        print(
            f"Video  : {video.name}"
        )

        raw_name = video.stem

    else:

        print(
            "Video  : tidak ditemukan"
        )

        # Tetap gunakan nama folder
        raw_name = folder.name

    # --------------------------------------------------------
    # Parse title
    # --------------------------------------------------------

    title, year, season = extract_title(
        raw_name,
        media_type,
    )

    # Jika hasil dari nama video jelek,
    # coba nama folder
    folder_title, folder_year, folder_season = (
        extract_title(
            folder.name,
            media_type,
        )
    )

    if (
        len(folder_title)
        > 0
        and (
            len(folder_title)
            < len(title)
            or not title
        )
    ):

        title = folder_title

    if not year:
        year = folder_year

    if not season:
        season = folder_season

    print(
        f"Judul  : {title or '-'}"
    )

    print(
        f"Tahun  : {year or '-'}"
    )

    if media_type == "tv":

        print(
            f"Season : "
            f"{season if season else '-'}"
        )

    if not title:

        print_error(
            "Judul tidak dapat dikenali."
        )

        return

    # --------------------------------------------------------
    # Search TMDB
    # --------------------------------------------------------

    search_result = search_media(
        title,
        year,
        media_type,
    )

    if not search_result:

        print(
            "Media tidak ditemukan."
        )

        return

    tmdb_id = search_result.get(
        "id"
    )

    if not tmdb_id:

        print(
            "TMDB ID tidak ditemukan."
        )

        return

    print(
        f"TMDB ID : {tmdb_id}"
    )

    # --------------------------------------------------------
    # Get details Indonesia
    # --------------------------------------------------------

    details = get_details(
        tmdb_id,
        media_type,
    )

    # --------------------------------------------------------
    # Fallback English
    # --------------------------------------------------------

    if not details:

        print(
            "Metadata Indonesia gagal, "
            "mencoba English..."
        )

        details = get_details_fallback(
            tmdb_id,
            media_type,
        )

    if not details:

        print(
            "Gagal mengambil detail media."
        )

        return

    # --------------------------------------------------------
    # Jika overview Indonesia kosong,
    # ambil overview English
    # --------------------------------------------------------

    if not details.get("overview"):

        fallback_details = (
            get_details_fallback(
                tmdb_id,
                media_type,
            )
        )

        if (
            fallback_details
            and fallback_details.get(
                "overview"
            )
        ):

            details["overview"] = (
                fallback_details[
                    "overview"
                ]
            )

    # --------------------------------------------------------
    # Build metadata
    # --------------------------------------------------------

    metadata = build_metadata(
        details,
        media_type,
        year,
        season,
    )

    if write_metadata(
        folder,
        metadata,
    ):

        print(
            "metadata.json dibuat."
        )

    # --------------------------------------------------------
    # Download poster
    # --------------------------------------------------------

    poster_path = (
        details.get(
            "poster_path"
        )
    )

    if poster_path:

        poster_url = (
            "https://image.tmdb.org/t/p/"
            f"{POSTER_SIZE}"
            f"{poster_path}"
        )

        poster_file = (
            folder
            / "poster.jpg"
        )

        print(
            "Download poster..."
        )

        if download_file(
            poster_url,
            poster_file,
        ):

            print(
                "poster.jpg berhasil dibuat."
            )

    else:

        print_warning(
            "Poster tidak tersedia."
        )

    # --------------------------------------------------------
    # Download clearlogo
    # --------------------------------------------------------

    print(
        "Mencari clear logo..."
    )

    logo_path = get_clearlogo(
        tmdb_id,
        media_type,
    )

    if logo_path:

        logo_url = (
            "https://image.tmdb.org/t/p/"
            f"{LOGO_SIZE}"
            f"{logo_path}"
        )

        logo_file = (
            folder
            / "clearlogo.png"
        )

        if download_file(
            logo_url,
            logo_file,
        ):

            print(
                "clearlogo.png berhasil dibuat."
            )

    else:

        print_warning(
            "Clear logo tidak tersedia."
        )

    print(
        f"SELESAI: "
        f"{metadata['title']}"
    )


# ============================================================
# SCAN DIRECTORY
# ============================================================

def scan_directory(
    root,
    media_type,
):

    line()

    if media_type == "movie":

        print(
            "SCAN MOVIES"
        )

    else:

        print(
            "SCAN TV SERIES"
        )

    print(root)

    line()

    if not root.exists():

        print_error(
            f"Folder tidak ditemukan: {root}"
        )

        return

    folders = sorted(
        [
            path
            for path in root.iterdir()
            if path.is_dir()
        ],
        key=lambda path:
            path.name.lower(),
    )

    print(
        f"Ditemukan {len(folders)} folder."
    )

    for folder in folders:

        process_folder(
            folder,
            media_type,
        )


# ============================================================
# MAIN
# ============================================================

def main():

    line()

    print(
        "             MOVIE LIBRARY SCANNER"
    )

    line()

    print()

    print(
        f"FILM : {MOVIES_DIR}"
    )

    print(
        f"TV   : {TV_DIR}"
    )

    print()

    # Cek autentikasi
    if (
        not TMDB_READ_TOKEN
        and not TMDB_API_KEY
    ):

        print_error(
            "TMDB_TOKEN atau TMDB_API_KEY belum diatur."
        )

        print()

        print(
            "Contoh menggunakan Read Access Token:"
        )

        print()

        print(
            "export TMDB_TOKEN='TOKEN_KAMU'"
        )

        return

    # Scan movies
    scan_directory(
        MOVIES_DIR,
        "movie",
    )

    # Scan TV
    scan_directory(
        TV_DIR,
        "tv",
    )

    print()

    line()

    print(
        "SCAN SELESAI"
    )

    line()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()
