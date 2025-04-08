from flask import Flask, request, send_from_directory, make_response
from flask import render_template
from convert.tasks.task import download_audio
from web.api_response import APIResponse
from uuid import uuid4
from web import settings

import redis
import os
import requests
import re

app = Flask(__name__)

rc = redis.Redis(host=settings.REDIS_SVC_HOST, decode_responses=True)

@app.route('/', methods=["GET"])
def home():
    return render_template('index.html')

@app.route('/download-music/<video_to_mp3_id>', methods=["GET"])
def download(video_to_mp3_id):

    # Always a good idea to sanitize data
    # validate video_to_mp3_id is an uuid
    regex = re.compile(r"^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$")

    if not re.fullmatch(regex, video_to_mp3_id):
        return render_template('invalid.html')

    # Check in our cache if we have
    # a task for this video
    video_status_cache = rc.get(video_to_mp3_id)
    
    if not video_status_cache:
        return render_template('invalid.html')

    elif video_status_cache == settings.TASK_QUEUED_STATUS_CODE:
        return render_template('not_ready.html')
        
    else:
        mp3_filename = "{filename}.mp3".format(filename=video_to_mp3_id)

        f = os.path.isfile("{fullpath}{filename}".format(fullpath=settings.MEDIA_DIR, filename=mp3_filename))

        if f:
            return send_from_directory(settings.MEDIA_DIR, mp3_filename)
        else:
            return render_template('invalid.html')


@app.route('/submit', methods=["POST"])
def submit():
    request_data = request.get_json()

    # validate link url
    regex = r"^(https?\:\/\/)?((www\.)?youtube\.com|youtu\.be)\/.+$"
    valid_link = re.match(regex, request_data['video_url'])
        
    video_id = request_data['video_url'][-11:]

    # Ask the cache if this video was previously
    # submited.
    # Our cache layer keeps a record of videos that
    # were submited to convert but don't exists 
    # in youtube to help us improve
    # peformance and save bandwith if that same video
    # is requested again in the future
    cache_result = rc.get(settings.CACHE_VIDEO_ID_KEY.format(vid=video_id))

    if cache_result == settings.CACHE_VIDEO_ID_DONT_EXISTS_CODE or not valid_link:

        app.logger.debug("Video ID '{}' doesn't exists, or an invalid link was given".format(video_id))

        return APIResponse(
            data={},
            message="Video doesn't exists or it's invalid",
            message_code="VIDEO_DONT_EXISTS_INVALID",
            http_code=400
        )

    if not cache_result:

        app.logger.debug("Video ID '{}' is not present in the cache yet.\r\nChecking with YouTube to see if it exists".format(video_id))

        # Let's check if the video exists first
        # We can use a neat hack for this and
        # try to get one of the thumbnails of the video
        video_thumb = requests.get('https://img.youtube.com/vi/{v_id}/0.jpg'.format(v_id=video_id))
        
        # Video not found
        if video_thumb.status_code == 404:

            app.logger.debug("YouTube says the video ID '{}' doesn't exists!".format(video_id))

            # Add the result to our cache layer.
            # We can use this information in further
            # requests and prevent re-checking the
            # existence of the video in youtube
            rc.set(settings.CACHE_VIDEO_ID_KEY.format(vid=video_id), settings.CACHE_VIDEO_ID_DONT_EXISTS_CODE)
            app.logger.debug("Saving this video ID '{}' as non-existing in our cache (404)".format(video_id))

            return APIResponse(
                data={},
                message="Video doesn't exists",
                message_code="VIDEO_DONT_EXISTS",
                http_code=400
            )

        # Video found
        elif video_thumb.status_code == 200:

            app.logger.debug("Video '{}' found in YouTube".format(video_id))
            # Add the result to our cache layer.
            # We can use this information in further
            # requests and prevent re-checking the
            # existence of the video in youtube
            rc.set(settings.CACHE_VIDEO_ID_KEY.format(vid=video_id), settings.CACHE_VIDEO_ID_EXISTS_CODE)
            
            app.logger.debug("Saving this video ID '{}' as existing in our cache (200)".format(video_id))
        
        # Something happend!!
        else:

            raise Exception("Error trying to get YouTube thumb. HTTP code: {}".format(video_thumb.status_code))

        # Our cache might have been updated by the code above
        # we need to update the result for the rest of the code
        # to work properly
        cache_result = rc.get(settings.CACHE_VIDEO_ID_KEY.format(vid=video_id))

    if cache_result == settings.CACHE_VIDEO_ID_EXISTS_CODE:

        # to avoid name collision the filename of the file
        # will be created using a uui4
        mp3_name = str(uuid4())

        try:
            download_audio.delay(request_data['video_url'], "{}".format(mp3_name))
            
            app.logger.debug("Sending the task to download the video ID '{}'".format(video_id))
        except Exception as e:
            raise e
        else:
            # Now that the video has been converted
            # we add the name of the file (without the extension)
            # to our cache layer.
            # This will be used by our web api 
            # once a user tries to download the file.
            cache_key = mp3_name
            rc.setex(cache_key, settings.CACHE_DEFAULT_TTL, settings.TASK_QUEUED_STATUS_CODE)
            
            app.logger.debug("Saving in our cache the status of the task to convert video ID '{video_id}' under the cache key name '{cache_key}'".format(video_id=video_id, cache_key=cache_key))

        return APIResponse(
                data={
                    'filename': mp3_name,
                },
                message="The request has been sent",
                message_code="REQUEST_SUBMITED",
                http_code=201
            )
    
    else:

        return APIResponse(
                data={},
                message="Video doesn't exists",
                message_code="VIDEO_DONT_EXISTS",
                http_code=400
            )
