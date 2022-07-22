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

rc = redis.Redis(host='redis', decode_responses=True)

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
    cache_result = rc.get("ve_{vid}".format(vid=video_id))

    if cache_result == '404' or not valid_link:

        return APIResponse(
            data={},
            message="Video doesn't exists or it's invalid",
            message_code="VIDEO_DONT_EXISTS_INVALID",
            http_code=400
        )

    # Let's check if the video exists first
    # We can use a neat hack for this and
    # try to get one of the thumbnails of the video
    video_thumb = requests.get('https://img.youtube.com/vi/{v_id}/0.jpg'.format(v_id=video_id))
    
    if video_thumb.status_code == 404:

        # Add the result to our cache layer.
        # We can use this information in further
        # requests and prevent re-checking the
        # existence of the video in youtube
        rc.set("ve_{vid}".format(vid=video_id), video_thumb.status_code)

        return APIResponse(
            data={},
            message="Video doesn't exists",
            message_code="VIDEO_DONT_EXISTS",
            http_code=400
        )

    else:

        # to avoid name collision the filename of the file
        # will be created using a uui4
        mp3_name = str(uuid4())

        try:
            download_audio.delay(request_data['video_url'], "{}.mp3".format(mp3_name))
        except Exception as e:
            raise e
        else:
            # Now that the video has been converted
            # we add the name of the file (without the extension)
            # to our cache layer.
            # This will be used by our web api 
            # once a user tries to download the file.
            cache_key = mp3_name
            rc.setex(cache_key, settings.CACHE_DEFAULT_TTL, "ONQUEUE")

        return APIResponse(
                data={
                    'filename': mp3_name,
                },
                message="The request has been sent",
                message_code="REQUEST_SUBMITED",
                http_code=201
            )