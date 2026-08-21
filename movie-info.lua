
local license = [[
MIT License

Copyright (c) 2026 Hartono

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO REGARDING THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
]]

-- ============================================================
local mp = require("mp")
local utils = require("mp.utils")

-- ============================================================
-- CONFIGURATION
-- ============================================================

local LOGO_ID = 7
local POSTER_ID = 8
local AUTO_HIDE_DELAY = 10

-- CLEAR LOGO CONFIG
local LOGO_LEFT = 0.02
local LOGO_TOP  = 0.03
local LOGO_MAX_WIDTH = 0.24
local LOGO_MAX_HEIGHT = 0.14
local GENRE_GAP = 20
local GENRE_FONT_SIZE = 36

-- CLOCK / END TIME CONFIG (POJOK KANAN ATAS)
local CLOCK_RIGHT_MARGIN = 40
local CLOCK_TOP_MARGIN = 10
local CLOCK_NOW_FONT_SIZE = 75
local CLOCK_END_FONT_SIZE = 36
local CLOCK_GAP_Y = 58 -- Mengatur jarak vertikal antara Jam dan END (agar rapat)

-- POSTER CONFIG
local POSTER_LEFT = 0.04
local POSTER_TOP  = 0.14
local POSTER_MAX_HEIGHT = 0.70
local POSTER_MAX_WIDTH = 0.50

-- INFO TEXT CONFIG
local INFO_GAP = 35
local TITLE_FONT_SIZE = 56
local META_FONT_SIZE = 40
local GENRE_INFO_FONT_SIZE = 38
local OVERVIEW_FONT_SIZE = 37

-- ============================================================
-- STATE & CACHE
-- ============================================================

local info_visible = false
local logo_visible = false
local poster_visible = false

local ass_overlay = mp.create_osd_overlay("ass-events")

local logo_raw_file = nil
local poster_raw_file = nil

local logo_x, logo_y, logo_w, logo_h = 0, 0, 0, 0
local poster_x, poster_y, poster_w, poster_h = 0, 0, 0, 0

local cached_metadata = nil
local cached_metadata_path = nil

local auto_hide_timer = nil

-- ============================================================
-- HELPER ESCAPE ASS
-- ============================================================

local function ass_escape(text)
    if not text then return "" end
    text = tostring(text)
    text = text:gsub("\\", "\\\\"):gsub("{", "\\{"):gsub("}", "\\}")
    return text
end

-- ============================================================
-- READ & LOAD METADATA
-- ============================================================

local function read_file(path)
    local file = io.open(path, "r")
    if not file then return nil end
    local data = file:read("*a")
    file:close()
    return data
end

local function get_movie_folder()
    local path = mp.get_property("path")
    if not path then return nil end
    return path:match("^(.*)/[^/]+$")
end

local function load_metadata()
    local folder = get_movie_folder()
    if not folder then return nil end

    if cached_metadata and cached_metadata_path == folder then
        return cached_metadata
    end

    local season_meta_path = folder .. "/season_metadata.json"
    local data = read_file(season_meta_path)
    local is_season = true

    if not data then
        local main_meta_path = folder .. "/metadata.json"
        data = read_file(main_meta_path)
        is_season = false

        if not data then
            local parent_folder = folder:match("^(.*)/[^/]+$")
            if parent_folder then
                main_meta_path = parent_folder .. "/metadata.json"
                data = read_file(main_meta_path)
            end
        end
    end

    -- SYARAT UTAMA: Jika metadata tidak ada, kembalikan nil
    if not data then return nil end

    local metadata, err = utils.parse_json(data)
    if not metadata then
        mp.msg.error("Invalid metadata JSON: " .. tostring(err))
        return nil
    end

    if is_season then
        local show = metadata.show_title or metadata.title or "Unknown"
        local s_name = metadata.season_name or metadata.name or ("Season " .. tostring(metadata.season_number or ""))
        
        metadata.title = ass_escape(show) .. "\\N{\\fs36}" .. ass_escape(s_name)
        metadata.is_formatted_title = true
        metadata.year = metadata.air_date and metadata.air_date:sub(1, 4) or ""
    else
        metadata.title = ass_escape(metadata.title or "Unknown")
        metadata.is_formatted_title = true
        metadata.year = metadata.first_air_date and metadata.first_air_date:sub(1, 4) or metadata.year or ""
    end

    metadata.folder = folder
    cached_metadata = metadata
    cached_metadata_path = folder

    return metadata
end

-- ============================================================
-- GET IMAGE SIZE & CONVERT BGRA
-- ============================================================

local function get_image_size(path)
    local result = utils.subprocess({
        args = { "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", path },
        cancellable = false
    })
    if result.status ~= 0 then return nil, nil end
    local w, h = result.stdout:match("(%d+)x(%d+)")
    return tonumber(w), tonumber(h)
end

local function create_bgra(source, width, height, id, name)
    local runtime = os.getenv("XDG_RUNTIME_DIR") or "/tmp"
    local filename = runtime .. "/mpv-" .. name .. "-" .. tostring(id) .. ".bgra"

    if utils.file_info(filename) then
        return filename
    end

    local result = utils.subprocess({
        args = {
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", source,
            "-vf", string.format("scale=%d:%d:flags=lanczos", width, height),
            "-pix_fmt", "bgra", "-f", "rawvideo", filename
        },
        cancellable = false
    })

    if result.status ~= 0 then
        mp.msg.error("FFmpeg gagal membuat BGRA: " .. name)
        return nil
    end

    return filename
end

-- ============================================================
-- REMOVE LOGO & POSTER
-- ============================================================

local function remove_logo()
    if logo_visible then
        mp.commandv("overlay-remove", tostring(LOGO_ID))
        logo_visible = false
    end
end

local function remove_poster()
    if poster_visible then
        mp.commandv("overlay-remove", tostring(POSTER_ID))
        poster_visible = false
    end
end

local function cleanup_files()
    if logo_raw_file then
        os.remove(logo_raw_file)
        logo_raw_file = nil
    end
    if poster_raw_file then
        os.remove(poster_raw_file)
        poster_raw_file = nil
    end
end

-- ============================================================
-- SHOW CLEAR LOGO & HEADER INFO (JAM TERMASUK DI SINI)
-- ============================================================

local function find_clearlogo(folder)
    local path = folder .. "/clearlogo.png"
    if utils.file_info(path) then return path end

    local parent_folder = folder:match("^(.*)/[^/]+$")
    if parent_folder then
        path = parent_folder .. "/clearlogo.png"
        if utils.file_info(path) then return path end
    end
    return nil
end

local function show_logo(metadata)
    if logo_visible or not metadata then return end

    local png_path = find_clearlogo(metadata.folder)
    if not png_path then return end

    if not logo_raw_file then
        local original_w, original_h = get_image_size(png_path)
        local video_w = mp.get_property_number("video-params/w")
        local video_h = mp.get_property_number("video-params/h")
        if not original_w or not video_w then return end

        local max_w = math.floor(video_w * LOGO_MAX_WIDTH)
        local max_h = math.floor(video_h * LOGO_MAX_HEIGHT)
        local scale = math.min(max_w / original_w, max_h / original_h)

        local target_w = math.floor(original_w * scale)
        local target_h = math.floor(original_h * scale)
        local raw_w, raw_h = target_w * 2, target_h * 2

        logo_raw_file = create_bgra(png_path, raw_w, raw_h, LOGO_ID, "clearlogo")
        if not logo_raw_file then return end

        logo_x = math.floor(video_w * LOGO_LEFT)
        logo_y = math.floor(video_h * LOGO_TOP)
        logo_w, logo_h = target_w, target_h
    end

    mp.commandv(
        "overlay-add", tostring(LOGO_ID), tostring(logo_x), tostring(logo_y),
        logo_raw_file, "0", "bgra", tostring(logo_w * 2), tostring(logo_h * 2),
        tostring(logo_w * 8), tostring(logo_w), tostring(logo_h)
    )
    logo_visible = true
end

local function render_header_osd(metadata)
    local w, h = mp.get_osd_size()
    if w == 0 or h == 0 then return end

    ass_overlay.res_x = w
    ass_overlay.res_y = h

    local ass_parts = {}

    -- Render Genre (jika ada logo)
    if metadata and metadata.genres then
        local genres = ass_escape(table.concat(metadata.genres, " / "))
        if genres ~= "" and logo_visible then
            local genre_x = logo_x + logo_w + GENRE_GAP
            local genre_y = logo_y + math.floor(logo_h / 2)
            
            table.insert(ass_parts, string.format("{\\an4\\pos(%d,%d)\\fs%d\\bord1\\shad1}%s", genre_x, genre_y, GENRE_FONT_SIZE, genres))
        end
    end

    -- Render Jam & Estimasi Selesai (Posisi Vertikal Dihitung Terpisah Agar Rapat)
    local now_time = os.date("%H:%M")
    local time_remaining = mp.get_property_number("time-remaining")

    local clock_x = w - CLOCK_RIGHT_MARGIN
    local clock_y = CLOCK_TOP_MARGIN

    local clock_str = string.format("{\\an9\\pos(%d,%d)\\bord1\\shad1}{\\fs%d\\b1}%s", clock_x, clock_y, CLOCK_NOW_FONT_SIZE, now_time)

    if time_remaining and time_remaining > 0 then
        local finish_timestamp = os.time() + math.floor(time_remaining)
        local finish_time = os.date("%H:%M", finish_timestamp)
        local end_y = clock_y + CLOCK_GAP_Y
        
        clock_str = clock_str .. string.format("\n{\\an9\\pos(%d,%d)\\bord1\\shad1}{\\fs%d\\b0\\a&H40&}Ends at : %s", clock_x, end_y, CLOCK_END_FONT_SIZE, finish_time)
    end

    table.insert(ass_parts, clock_str)

    ass_overlay.data = table.concat(ass_parts, "\n")
    ass_overlay:update()
end

local function show_header()
    if info_visible then return end

    -- VALIDASI KETAT: Periksa keberadaan metadata json terlebih dahulu
    local metadata = load_metadata()
    if not metadata then
        return -- Jangan tampilkan jam/logo jika metadata tidak ada
    end

    show_logo(metadata)
    render_header_osd(metadata)
end

local function hide_header()
    remove_logo()
    ass_overlay:remove()
end

-- ============================================================
-- SHOW POSTER & FULL INFO
-- ============================================================

local function find_poster(folder)
    for _, name in ipairs({"poster.jpg", "poster.png", "poster.webp"}) do
        local path = folder .. "/" .. name
        if utils.file_info(path) then return path end
    end

    local parent_folder = folder:match("^(.*)/[^/]+$")
    if parent_folder then
        for _, name in ipairs({"poster.jpg", "poster.png", "poster.webp"}) do
            local path = parent_folder .. "/" .. name
            if utils.file_info(path) then return path end
        end
    end

    return nil
end

local function show_poster(metadata)
    if poster_visible then return true end

    local poster_path = find_poster(metadata.folder)
    if not poster_path then return false end

    local video_w = mp.get_property_number("video-params/w")
    local video_h = mp.get_property_number("video-params/h")
    if not video_w or not video_h then return false end

    poster_x = math.floor(video_w * POSTER_LEFT)
    poster_y = math.floor(video_h * POSTER_TOP)

    if not poster_raw_file then
        local original_w, original_h = get_image_size(poster_path)
        if not original_w then return false end

        local max_w = math.floor(video_w * POSTER_MAX_WIDTH)
        local max_h = math.floor(video_h * POSTER_MAX_HEIGHT)
        local scale = math.min(max_w / original_w, max_h / original_h)

        local target_w = math.floor(original_w * scale)
        local target_h = math.floor(original_h * scale)
        local raw_w, raw_h = target_w * 2, target_h * 2

        poster_raw_file = create_bgra(poster_path, raw_w, raw_h, POSTER_ID, "poster")
        if not poster_raw_file then return false end

        poster_w, poster_h = target_w, target_h
    end

    mp.commandv(
        "overlay-add", tostring(POSTER_ID), tostring(poster_x), tostring(poster_y),
        poster_raw_file, "0", "bgra", tostring(poster_w * 2), tostring(poster_h * 2),
        tostring(poster_w * 8), tostring(poster_w), tostring(poster_h)
    )
    poster_visible = true
    return true
end

local function wrap_text(text, max_chars)
    if not text then return "" end
    local result, line = {}, ""
    for word in tostring(text):gmatch("%S+") do
        if #line == 0 then line = word
        elseif #line + #word + 1 <= max_chars then line = line .. " " .. word
        else table.insert(result, line); line = word end
    end
    if #line > 0 then table.insert(result, line) end
    return table.concat(result, "\\N")
end

local function show_info()
    remove_logo()

    local metadata = load_metadata()
    if not metadata then
        mp.osd_message("Metadata JSON tidak ditemukan", 2)
        return
    end

    local width, height = mp.get_osd_size()
    ass_overlay.res_x, ass_overlay.res_y = width, height

    local poster_ok = show_poster(metadata)
    local text_x = poster_ok and (poster_x + poster_w + INFO_GAP) or math.floor(width * 0.08)
    local text_y = poster_ok and poster_y or math.floor(height * POSTER_TOP)

    local title = metadata.is_formatted_title and metadata.title or ass_escape(metadata.title or "Unknown")
    local year = tostring(metadata.year or "")
    local rating = tonumber(metadata.vote_average) or 0
    local genres = ass_escape(metadata.genres and table.concat(metadata.genres, " • ") or "")
    local overview = ass_escape(metadata.overview or "")

    local available_width = width - text_x - math.floor(width * 0.05)
    local max_chars = math.max(35, math.floor(available_width / (OVERVIEW_FONT_SIZE * 0.55)))
    overview = wrap_text(overview, max_chars)

    local panel = string.format(
        "{\\an7\\pos(%d,%d)}{\\fs%d\\b1\\bord2\\shad2}%s\\N{\\fs%d\\b0\\bord1\\shad1}%s  •  ⭐ %.1f/10\\N{\\fs%d}%s\\N\\N{\\fs%d\\q2\\bord1\\shad1}%s",
        text_x, text_y, TITLE_FONT_SIZE, title, META_FONT_SIZE, year, rating, GENRE_INFO_FONT_SIZE, genres, OVERVIEW_FONT_SIZE, overview
    )

    ass_overlay.data = panel
    ass_overlay:update()
    info_visible = true
end

local function hide_info()
    remove_poster()
    ass_overlay:remove()
    info_visible = false
end

local function toggle_info()
    if info_visible then hide_info() else show_info() end
end

mp.add_key_binding("=", "movie-info-key", toggle_info)
mp.add_forced_key_binding("MBTN_RIGHT", "movie-info-mouse", toggle_info)

-- ============================================================
-- AUTO VISIBILITY CONTROLLER
-- ============================================================

local function request_show_header()
    if info_visible then return end
    show_header()

    if auto_hide_timer then auto_hide_timer:kill() end

    local paused = mp.get_property_native("pause")
    if not paused then
        auto_hide_timer = mp.add_timeout(AUTO_HIDE_DELAY, function()
            if not info_visible then hide_header() end
        end)
    end
end

mp.observe_property("mouse-pos", "native", function(_, val)
    if val then request_show_header() end
end)

mp.observe_property("user-data/osc/visibility", "native", function(_, val)
    if val == 1 then request_show_header()
    elseif val == 0 then if not info_visible then hide_header() end end
end)

mp.observe_property("pause", "bool", function() request_show_header() end)

-- ============================================================
-- EVENT HANDLERS
-- ============================================================

mp.register_event("file-loaded", function()
    info_visible = false
    remove_logo()
    remove_poster()
    cleanup_files()
    ass_overlay:remove()
    cached_metadata = nil
    cached_metadata_path = nil

    request_show_header()
end)

mp.register_event("shutdown", function()
    remove_logo()
    remove_poster()
    cleanup_files()
    ass_overlay:remove()
end)

mp.msg.info("movie-info.lua (metadata check enabled) loaded")
