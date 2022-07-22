import os

MEDIA_DIR = os.getenv('VIDEOSVC_MEDIA_DIR', '/data/')

CACHE_DEFAULT_TTL = 60*60*3 # 3 hour