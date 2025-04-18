import os

MEDIA_DIR = os.getenv('VIDEOSVC_MEDIA_DIR', '/data/')

CACHE_DEFAULT_TTL = 60*60 # 1 hour
TASK_QUEUED_STATUS_CODE = "ONQUEUE"
TASK_FINISH_STATUS_CODE = "FINISH"

CACHE_VIDEO_ID_KEY = "ve_{vid}"
CACHE_VIDEO_ID_DONT_EXISTS_CODE = '404'
CACHE_VIDEO_ID_EXISTS_CODE = '200'

# default broker
BROKER_URL = os.getenv('BROKER_URL', 'redis://redis:6379')

# cache layer and/or broker
REDIS_SVC_HOST = os.getenv('REDIS_SVC_HOST', 'redis')