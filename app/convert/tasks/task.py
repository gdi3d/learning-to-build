from celery import Celery
from flask import Flask
from convert import settings

import youtube_dl
import redis
import os

rc = redis.Redis(host='redis', decode_responses=True)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['broker_url']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

flask_app = Flask(__name__)
flask_app.config.update(
    broker_url='redis://redis:6379',
    result_backend=None,
    task_soft_time_limit=60*4,
    task_time_limit=60*6
)
celery = make_celery(flask_app)

@celery.task(bind=True, 
            autoretry_for=(Exception,),
            retry_backoff=True,
            max_retries=3)
def download_audio(self, youtube_link, output_mp3_filename):
   
    save_at = '{media_dir}{filename}'.format(media_dir=settings.MEDIA_DIR, filename=output_mp3_filename)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg-location': './usr/bin',
        'outtmpl': save_at,
        'keepvideo': 'False'
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_link])    

    # A small hack to keep to change the
    # modification date of the file to today
    # We need this in order to safely cleanup
    # old files withe cleanup service 
    # and avoid filling up our disk.
    # This is because youtubeDL uses the original
    # file date, but we don't need it
    os.utime(save_at, (os.path.getatime(save_at), os.path.getatime(save_at)))

    # Now that the video has been converted
    # we add the name of the file (without the extension)
    # to our cache layer.
    # This will be used by our web api 
    # once a user tries to download the file.
    cache_key = output_mp3_filename[:-4]
    rc.setex(cache_key, settings.CACHE_DEFAULT_TTL, "FINISH")