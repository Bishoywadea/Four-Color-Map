# This file is part of the Four Color Map game.
# Copyright (C) 2025 Bishoy Wadea
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


class Config:

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60

    COLORS = {
        'BACKGROUND': (70, 130, 180),  # Steel blue
        'UNCOLORED': (200, 200, 255),  # Light blue-gray
        'BORDER': (0, 0, 0),           # Black
        'UI_BACKGROUND': (240, 240, 240),  # Light gray
        'TEXT': (0, 0, 0),             # Black
        'BUTTON_HOVER': (220, 220, 220),  # Light gray
        'HELP_BUTTON': (200, 200, 200),
        'HELP_PANEL': (240, 240, 240, 230),  # Semi-transparent
        'HELP_TEXT': (0, 0, 0),
    }

    UI_HEIGHT = 80
    COLOR_BUTTON_SIZE = 50
    BUTTON_MARGIN = 10

    BORDER_WIDTH = 2
    REGION_HOVER_ALPHA = 50

    DEFAULT_ZOOM = 1.0
    MIN_ZOOM = 0.5
    MAX_ZOOM = 10.0
    ZOOM_SPEED = 0.1

    DEFAULT_GAME_COLORS = [
        (255, 99, 71),   # Red/Tomato
        (100, 149, 237),  # Blue/Cornflower
        (255, 215, 0),   # Gold
        (50, 205, 50)    # Green/Lime
    ]

    # Current game colors (can be customized)
    GAME_COLORS = DEFAULT_GAME_COLORS.copy()

    HELP_BUTTON_RADIUS = 20
    HELP_PANEL_WIDTH = 400
    HELP_PANEL_HEIGHT = 300
    HELP_TEXT_MARGIN = 20

    @staticmethod
    def reset_colors():
        """Reset colors to defaults."""
        Config.GAME_COLORS = Config.DEFAULT_GAME_COLORS.copy()
