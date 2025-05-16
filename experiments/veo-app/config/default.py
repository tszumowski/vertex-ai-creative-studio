import os 
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(override=True)


@dataclass
class Default:
    """ Defaults class"""
    # Gemini
    PROJECT_ID: str = os.environ.get("PROJECT_ID")
    LOCATION: str = os.environ.get("LOCATION", "us-central1")
    MODEL_ID: str = os.environ.get("MODEL_ID", "gemini-2.0-flash")
    INIT_VERTEX: bool = True

    # Collections
    GENMEDIA_FIREBASE_DB: str = os.environ.get("GENMEDIA_FIREBASE_DB", "(default)")
    GENMEDIA_COLLECTION_NAME: str = os.environ.get("GENMEDIA_COLLECTION_NAME", "genmedia")

    # Veo
    VEO_MODEL_ID: str = os.environ.get("VEO_MODEL_ID", "veo-2.0-generate-001")
    VEO_EXP_MODEL_ID: str = os.environ.get("VEO_EXP_MODEL_ID", "veo-2.0-generate-exp")
    VEO_PROJECT_ID: str = os.environ.get("VEO_PROJECT_ID", PROJECT_ID)
    GENMEDIA_BUCKET: str = os.environ.get("GENMEDIA_BUCKET", f"{PROJECT_ID}-assets")
    VIDEO_BUCKET: str = os.environ.get("VIDEO_BUCKET", f"{PROJECT_ID}-assets/videos")
    IMAGE_BUCKET: str = os.environ.get("IMAGE_BUCKET", f"{PROJECT_ID}-assets/images")
    
    # Lyria
    LYRIA_MODEL_VERSION: str = os.environ.get("LYRIA_MODEL_VERSION","lyria-base-001")
    LYRIA_PROJECT_ID: str = os.environ.get("LYRIA_PROJECT_ID", PROJECT_ID)
    MEDIA_BUCKET: str = os.environ.get("MEDIA_BUCKET", f"{PROJECT_ID}-assets")
    



# page_json = [
#     {"id": 0, "display": "Home", "icon": "home", "route": "/"},
#     {"id": 1,  "display": "Veo", "icon": "movie_filter", "route": "/veo"},
#     {"id": 2, "display": "Portraits", "icon": "portrait", "route": "/motion_portraits"},
#     {"id": 3, "display": "Lyria", "icon": "music_note", "route": "/lyria"},
#     #{"id": 3, "display": "Imagen", "icon": "image", "route": "/imagen"},
#     {"id": 5, "display": "Library", "icon": "perm_media", "route": "/library"},
#     {
#         "id": 10,
#         "display": "Settings",
#         "icon": "settings",
#         "route": "/config",
#         "align": "bottom",
#     },
# ]

PAGES = [
    {"id": 0, "display": "Home", "icon": "home", "route": "/"},
    {"id": 1, "display": "Veo", "icon": "movie_filter", "route": "/veo"},
    {"id": 2, "display": "Portraits", "icon": "portrait", "route": "/motion_portraits"},
]

if Default.LYRIA_PROJECT_ID is not None:
    PAGES.append({"id": 3, "display": "Lyria", "icon": "music_note", "route": "/lyria"})

PAGES.extend([
    #{"id": 3, "display": "Imagen", "icon": "image", "route": "/imagen"}, # This ID might conflict if Lyria is also 3
    {"id": 5, "display": "Library", "icon": "perm_media", "route": "/library"},
    {
        "id": 10,
        "display": "Settings",
        "icon": "settings",
        "route": "/config",
        "align": "bottom",
    },
])