# map_data.py
from config import Config

def get_level_1():
    """Level 1: Simple 6-region map."""
    center_x = Config.SCREEN_WIDTH // 2
    center_y = Config.SCREEN_HEIGHT // 2
    
    regions_data = [
        {
            'id': 0,
            'name': 'Region A',
            'points': [
                (center_x - 150, center_y - 100),
                (center_x - 50, center_y - 120),
                (center_x, center_y - 50),
                (center_x - 70, center_y),
                (center_x - 130, center_y - 20)
            ],
            'neighbors': [1, 2]
        },
        {
            'id': 1,
            'name': 'Region B', 
            'points': [
                (center_x - 50, center_y - 120),
                (center_x + 50, center_y - 110),
                (center_x + 70, center_y - 40),
                (center_x, center_y - 50)
            ],
            'neighbors': [0, 2, 3]
        },
        {
            'id': 2,
            'name': 'Region C',
            'points': [
                (center_x - 70, center_y),
                (center_x, center_y - 50),
                (center_x + 70, center_y - 40),
                (center_x + 30, center_y + 40),
                (center_x - 50, center_y + 50)
            ],
            'neighbors': [0, 1, 3, 4]
        },
        {
            'id': 3,
            'name': 'Region D',
            'points': [
                (center_x + 50, center_y - 110),
                (center_x + 150, center_y - 100),
                (center_x + 170, center_y - 20),
                (center_x + 70, center_y - 40)
            ],
            'neighbors': [1, 2, 5]
        },
        {
            'id': 4,
            'name': 'Region E',
            'points': [
                (center_x - 50, center_y + 50),
                (center_x + 30, center_y + 40),
                (center_x + 50, center_y + 120),
                (center_x - 30, center_y + 130)
            ],
            'neighbors': [2, 5]
        },
        {
            'id': 5,
            'name': 'Region F',
            'points': [
                (center_x + 70, center_y - 40),
                (center_x + 170, center_y - 20),
                (center_x + 150, center_y + 80),
                (center_x + 30, center_y + 40)
            ],
            'neighbors': [3, 4]
        }
    ]
    
    return regions_data

def get_level_2():
    """Level 2: Star-shaped map with 9 regions."""
    center_x = 400
    center_y = 250
    
    regions_data = [
        # Center region
        {
            'id': 0,
            'name': 'Center',
            'points': [
                (center_x - 40, center_y - 40),
                (center_x + 40, center_y - 40),
                (center_x + 40, center_y + 40),
                (center_x - 40, center_y + 40)
            ],
            'neighbors': [1, 2, 3, 4, 5, 6, 7, 8]
        },
        # Top point
        {
            'id': 1,
            'name': 'North',
            'points': [
                (center_x - 40, center_y - 40),
                (center_x, center_y - 150),
                (center_x + 40, center_y - 40)
            ],
            'neighbors': [0, 2, 8]
        },
        # Top-right
        {
            'id': 2,
            'name': 'NorthEast',
            'points': [
                (center_x + 40, center_y - 40),
                (center_x + 120, center_y - 80),
                (center_x + 80, center_y)
            ],
            'neighbors': [0, 1, 3]
        },
        # Right point
        {
            'id': 3,
            'name': 'East',
            'points': [
                (center_x + 40, center_y - 40),
                (center_x + 80, center_y),
                (center_x + 40, center_y + 40),
                (center_x + 150, center_y)
            ],
            'neighbors': [0, 2, 4]
        },
        # Bottom-right
        {
            'id': 4,
            'name': 'SouthEast',
            'points': [
                (center_x + 40, center_y + 40),
                (center_x + 80, center_y),
                (center_x + 120, center_y + 80)
            ],
            'neighbors': [0, 3, 5]
        },
        # Bottom point
        {
            'id': 5,
            'name': 'South',
            'points': [
                (center_x + 40, center_y + 40),
                (center_x, center_y + 150),
                (center_x - 40, center_y + 40)
            ],
            'neighbors': [0, 4, 6]
        },
        # Bottom-left
        {
            'id': 6,
            'name': 'SouthWest',
            'points': [
                (center_x - 40, center_y + 40),
                (center_x - 120, center_y + 80),
                (center_x - 80, center_y)
            ],
            'neighbors': [0, 5, 7]
        },
        # Left point
        {
            'id': 7,
            'name': 'West',
            'points': [
                (center_x - 40, center_y + 40),
                (center_x - 80, center_y),
                (center_x - 40, center_y - 40),
                (center_x - 150, center_y)
            ],
            'neighbors': [0, 6, 8]
        },
        # Top-left
        {
            'id': 8,
            'name': 'NorthWest',
            'points': [
                (center_x - 40, center_y - 40),
                (center_x - 80, center_y),
                (center_x - 120, center_y - 80)
            ],
            'neighbors': [0, 7, 1]
        }
    ]
    
    return regions_data

# Keep the old function for compatibility
def get_sample_map():
    return get_level_1()

# Level information
LEVELS = [
    {
        'id': 1,
        'name': 'Simple Map',
        'description': '6 regions - Easy',
        'data_func': get_level_1
    },
    {
        'id': 2,
        'name': 'Star Map',
        'description': '9 regions - Medium',
        'data_func': get_level_2
    }
]