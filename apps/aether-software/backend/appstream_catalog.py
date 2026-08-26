#!/usr/bin/env python3
"""
AetherOS AppStream Software Catalog
Curated catalog of high-quality desktop applications across 7 main categories with
descriptions, screenshots, developer info, licenses, permissions, and sizes.
"""

from typing import List, Dict, Any, Optional

CATEGORIES = [
    "Featured",
    "Internet & Web",
    "Development & Tools",
    "Productivity & Office",
    "Graphics & Photography",
    "Audio & Video",
    "System & Utilities",
    "Games & Entertainment"
]

CATALOG_APPS: List[Dict[str, Any]] = [
    # 1. Internet & Web
    {
        "id": "org.mozilla.firefox",
        "package": "firefox",
        "name": "Firefox Web Browser",
        "summary": "Fast, private, and customizable web browser built for security",
        "description": "Mozilla Firefox is a free and open-source web browser developed by Mozilla. Features tracking protection, tab grouping, hardware accelerated video rendering, and an extensive extension ecosystem.",
        "category": "Internet & Web",
        "icon": "firefox",
        "developer": "Mozilla Corporation",
        "license": "MPL-2.0",
        "homepage": "https://www.mozilla.org/firefox",
        "version": "128.0.3",
        "backend": "apt",
        "download_size_mb": 65.2,
        "installed_size_mb": 210.0,
        "permissions": ["Network Access", "Wayland Display", "Audio Output/Input", "Camera & Microphone"],
        "dependencies": ["libc6", "libgtk-3-0", "libpipewire-0.3-0"],
        "screenshots": [
            "https://raw.githubusercontent.com/flathub/org.mozilla.firefox/master/screenshot1.png",
            "https://raw.githubusercontent.com/flathub/org.mozilla.firefox/master/screenshot2.png"
        ],
        "featured": True
    },
    {
        "id": "org.mozilla.thunderbird",
        "package": "thunderbird",
        "name": "Thunderbird Mail & Calendar",
        "summary": "Full-featured email, calendar, and address book client",
        "description": "Thunderbird is a free email application that's easy to set up and customize. Supports OpenPGP end-to-end encryption, multi-account management, feeds, and calendar scheduling.",
        "category": "Internet & Web",
        "icon": "thunderbird",
        "developer": "Mozilla Foundation",
        "license": "MPL-2.0",
        "homepage": "https://www.thunderbird.net",
        "version": "128.1.0",
        "backend": "apt",
        "download_size_mb": 58.4,
        "installed_size_mb": 185.0,
        "permissions": ["Network Access", "Wayland Display", "Filesystem: Documents"],
        "dependencies": ["libc6", "libnss3"],
        "screenshots": [],
        "featured": False
    },

    # 2. Audio & Video
    {
        "id": "org.videolan.VLC",
        "package": "vlc",
        "name": "VLC Media Player",
        "summary": "Universal multimedia player for all video and audio formats",
        "description": "VLC is a free and open-source cross-platform multimedia player and framework that plays most multimedia files as well as DVDs, Audio CDs, VCDs, and various streaming protocols without external codec packs.",
        "category": "Audio & Video",
        "icon": "vlc",
        "developer": "VideoLAN Project",
        "license": "GPL-2.0+",
        "homepage": "https://www.videolan.org/vlc",
        "version": "3.0.21",
        "backend": "flatpak",
        "download_size_mb": 42.8,
        "installed_size_mb": 115.0,
        "permissions": ["Wayland Display", "Audio Output (PipeWire/PulseAudio)", "Removable Storage", "Network Access"],
        "dependencies": ["ffmpeg", "libplacebo", "alsa-lib"],
        "screenshots": [
            "https://images.videolan.org/vlc/screenshots/3.0/vlc-3.0-p1.jpg"
        ],
        "featured": True
    },
    {
        "id": "com.obsproject.Studio",
        "package": "obs-studio",
        "name": "OBS Studio",
        "summary": "Live streaming and high-performance video recording software",
        "description": "Free and open source software for video recording and live streaming. Capture from Wayland screens, webcams, audio interfaces, and compose professional multi-source broadcasts.",
        "category": "Audio & Video",
        "icon": "com.obsproject.Studio",
        "developer": "OBS Project",
        "license": "GPL-2.0+",
        "homepage": "https://obsproject.com",
        "version": "30.2.2",
        "backend": "flatpak",
        "download_size_mb": 95.0,
        "installed_size_mb": 260.0,
        "permissions": ["Wayland PipeWire Screen Cast", "Audio Input/Output", "Camera Devices", "Hardware GPU Encoding (VA-API/NVENC)"],
        "dependencies": ["pipewire", "ffmpeg", "libva"],
        "screenshots": [],
        "featured": True
    },

    # 3. Development & Tools
    {
        "id": "com.visualstudio.code",
        "package": "code",
        "name": "Visual Studio Code",
        "summary": "Modern code editor with integrated Git, debugging, and extensions",
        "description": "VS Code is a lightweight but powerful source code editor which runs on your desktop and is available for Linux. It comes with built-in support for JavaScript, TypeScript, Python, C++, Rust, and a rich ecosystem of extensions.",
        "category": "Development & Tools",
        "icon": "code",
        "developer": "Microsoft / Open Source Community",
        "license": "MIT",
        "homepage": "https://code.visualstudio.com",
        "version": "1.92.0",
        "backend": "flatpak",
        "download_size_mb": 88.0,
        "installed_size_mb": 310.0,
        "permissions": ["Full Home Directory Access", "Terminal & Shell Execution", "Network Access", "Wayland Display"],
        "dependencies": ["git", "curl", "node"],
        "screenshots": [],
        "featured": True
    },
    {
        "id": "org.neovim.nvim",
        "package": "neovim",
        "name": "Neovim",
        "summary": "Hyperextensible Vim-based text editor built for high speed",
        "description": "Neovim is a refactor of Vim to aggressively enable new applications; improve user experience with modern GUIs; enable asynchronous plugins and embedded Lua scripting.",
        "category": "Development & Tools",
        "icon": "nvim",
        "developer": "Neovim Team",
        "license": "Apache-2.0",
        "homepage": "https://neovim.io",
        "version": "0.10.1",
        "backend": "apt",
        "download_size_mb": 7.5,
        "installed_size_mb": 24.0,
        "permissions": ["Terminal Execution"],
        "dependencies": ["libc6", "libluajit-5.1-2"],
        "screenshots": [],
        "featured": False
    },

    # 4. Graphics & Photography
    {
        "id": "org.gimp.GIMP",
        "package": "gimp",
        "name": "GIMP Image Manipulation Program",
        "summary": "Professional photo editing, image composition, and graphic design",
        "description": "GIMP is a cross-platform image editor. Whether you are a graphic designer, photographer, illustrator, or scientist, GIMP provides you with sophisticated tools to get your job done.",
        "category": "Graphics & Photography",
        "icon": "gimp",
        "developer": "GIMP Development Team",
        "license": "GPL-3.0+",
        "homepage": "https://www.gimp.org",
        "version": "2.10.38",
        "backend": "apt",
        "download_size_mb": 35.0,
        "installed_size_mb": 140.0,
        "permissions": ["Wayland Display", "Drawing Tablet (Wacom/Huion)", "Filesystem: Pictures"],
        "dependencies": ["libgegl-0.4-0", "libbabl-0.1-0", "libgtk-3-0"],
        "screenshots": [],
        "featured": True
    },
    {
        "id": "org.inkscape.Inkscape",
        "package": "inkscape",
        "name": "Inkscape Vector Graphics",
        "summary": "Vector graphics editor using the standard SVG format",
        "description": "Inkscape is professional quality vector graphics software which runs on Linux. Used by design professionals and hobbyists worldwide for creating a wide variety of graphics such as illustrations, icons, logos, diagrams, and maps.",
        "category": "Graphics & Photography",
        "icon": "org.inkscape.Inkscape",
        "developer": "Inkscape Project",
        "license": "GPL-3.0+",
        "homepage": "https://inkscape.org",
        "version": "1.3.2",
        "backend": "flatpak",
        "download_size_mb": 72.0,
        "installed_size_mb": 245.0,
        "permissions": ["Wayland Display", "Filesystem Access"],
        "dependencies": ["libgtkmm-3.0"],
        "screenshots": [],
        "featured": False
    },

    # 5. Productivity & Office
    {
        "id": "org.libreoffice.LibreOffice",
        "package": "libreoffice",
        "name": "LibreOffice Office Suite",
        "summary": "Full productivity suite including Writer, Calc, Impress, and Draw",
        "description": "LibreOffice is a powerful and free office suite. Its clean interface and feature-rich tools help you unleash your creativity and enhance your productivity. Fully compatible with Microsoft Office docx, xlsx, and pptx formats.",
        "category": "Productivity & Office",
        "icon": "libreoffice-main",
        "developer": "The Document Foundation",
        "license": "MPL-2.0",
        "homepage": "https://www.libreoffice.org",
        "version": "24.2.5",
        "backend": "apt",
        "download_size_mb": 180.0,
        "installed_size_mb": 580.0,
        "permissions": ["Filesystem Access", "Printing (CUPS)", "Wayland Display"],
        "dependencies": ["libreoffice-core", "libreoffice-writer", "libreoffice-calc"],
        "screenshots": [],
        "featured": True
    },

    # 6. System & Utilities
    {
        "id": "htop",
        "package": "htop",
        "name": "HTOP System Monitor",
        "summary": "Interactive real-time process viewer and system resource monitor",
        "description": "htop is a cross-platform interactive process viewer. It is a text-mode application (for console or X terminals) and requires ncurses.",
        "category": "System & Utilities",
        "icon": "htop",
        "developer": "Hisham Muhammad / htop dev team",
        "license": "GPL-2.0+",
        "homepage": "https://htop.dev",
        "version": "3.3.0",
        "backend": "apt",
        "download_size_mb": 0.2,
        "installed_size_mb": 0.5,
        "permissions": ["Process Read Access"],
        "dependencies": ["libncursesw6"],
        "screenshots": [],
        "featured": False
    },

    # 7. Games & Entertainment
    {
        "id": "com.valvesoftware.Steam",
        "package": "steam-installer",
        "name": "Steam Gaming Client",
        "summary": "Digital distribution platform with thousands of Linux & Proton games",
        "description": "Steam is the ultimate destination for playing, discussing, and creating games. Access thousands of native Linux games or run Windows games seamlessly with Proton/Wine.",
        "category": "Games & Entertainment",
        "icon": "steam",
        "developer": "Valve Corporation",
        "license": "Proprietary / Freeware",
        "homepage": "https://store.steampowered.com",
        "version": "1.0.0.79",
        "backend": "flatpak",
        "download_size_mb": 35.0,
        "installed_size_mb": 95.0,
        "permissions": ["GPU Direct Rendering (Vulkan/OpenGL)", "Game Controller Access", "Network Access", "Audio Output"],
        "dependencies": ["vulkan-tools", "mesa-vulkan-drivers"],
        "screenshots": [],
        "featured": True
    }
]

class AppStreamCatalog:
    @staticmethod
    def get_all_apps() -> List[Dict[str, Any]]:
        return list(CATALOG_APPS)

    @staticmethod
    def get_featured_apps() -> List[Dict[str, Any]]:
        return [app for app in CATALOG_APPS if app.get("featured", False)]

    @staticmethod
    def get_by_category(category: str) -> List[Dict[str, Any]]:
        if category == "Featured":
            return AppStreamCatalog.get_featured_apps()
        return [app for app in CATALOG_APPS if app["category"] == category]

    @staticmethod
    def search(query: str) -> List[Dict[str, Any]]:
        q = query.lower().strip()
        results = []
        for app in CATALOG_APPS:
            if (q in app["name"].lower() or 
                q in app["summary"].lower() or 
                q in app.get("description", "").lower() or 
                q in app["id"].lower() or 
                q in app.get("package", "").lower()):
                results.append(app)
        return results

    @staticmethod
    def get_app(app_id_or_pkg: str) -> Optional[Dict[str, Any]]:
        for app in CATALOG_APPS:
            if app["id"] == app_id_or_pkg or app.get("package") == app_id_or_pkg:
                return app
        return None
