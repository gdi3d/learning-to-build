# Download the MP3 file

The process that converts the video into an MP3 is done using a **Celery Task** and as we [mentioned here](/app/receiving-the-youtube-link?id=_10-send-an-asynchronous-task-to-create-the-mp3), this **Task** runs asynchronously. 

!> Read [about Celery](/about-celery)

This means that when the user clicks on **Click here to download the file**, the file might not be ready yet.

![success-message](../images/index-alert-success.jpg)

Start by opening the file at `app/web/main.py` and find these lines

```
@app.route('/download-music/<video_to_mp3_id>', methods=["GET"])
def download(video_to_mp3_id):
```

You can see that the *route* decorator here has a new format compared to the [index one](/app/serving-index-file?id=the-home-index-url).

!> Remember a *route* is what allows us to create a URL for our users to use.

We want to be able to *receive* the name of the MP3 file that was generated, by our code, after the user clicked the **Convert to MP3** button.

Here's how the endpoint is formed for the **URL** `https://127.0.0.1:8080/download-music/c3f044e1`

- Endpoint: `/download-music/c3f044e1`
- The variable `<video_to_mp3_id>` get assigned the value `c3f044e1`


## The Flowchart Analysis

![Flowchart Download MP3 File](../images/flowchart-download.png)

!> Keep the file `app/web/main.py` open and read along, the comments in the file will guide you trough

### 1 User asks for the file

As mentioned above, this endpoint is the one the user will use to download the MP3, and the name of the file has been already created by our backend right after the **Convert to MP3** button was clicked.

### 2 Is the MP3 name valid

To generate the name of the MP3 we use a [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) string that looks like this

`c3f044e1-1e66-4a52-be7d-6e344fb6aec6`

!> A universally unique identifier is a 128-bit label used for information in computer systems. The term globally unique identifier is also used. When generated according to the standard methods, UUIDs are, for practical purposes, unique

!> This is a good practice if you want to prevent naming collision (which means having duplicated filenames).

**UUID** values have a well-defined mask. This means that we can validate that only valid UUID *strings* are requested to our endpoint.

!> What's an endpoint? It's a fancy way to call URL's in the context of [REST APIs](https://www.ibm.com/cloud/learn/rest-apis). Ex.: /download-music/c3f044e1-1e66-4a52-be7d-6e344fb6aec6

If someone tries to use this endpoint like this:

```
https://127.0.0.1:8080/download-music/mysuperfile
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^ -> Endpoint
https://127.0.0.1:8080/download-music/songname.mp3
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ -> Endpoint
https://127.0.0.1:8080/download-music/IwillHackYou
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ -> Endpoint
```

We can evaluate those *MP3 names* (mysuperfile, songname.mp3, IwillHackYou) and check that are not a valid **UUID** type of strings and jump to **[3 Return invalid.html response](/app/download-mp3?id=_3-return-invalidhtml-response)**.

!> MP3 names are assigned to the variable `video_to_mp3_id` in the *route* definition  
`@app.route('/download-music/<video_to_mp3_id>', methods=["GET"])`

Otherwise, we can jump to **[4 Check the Cache Layer](/app/download-mp3?id=_4-check-the-cache-layer)**

### 3 Return invalid.html response

We show the **invalid.html** page located at `app/web/templates/invalid.html`

![Invalid file](../images/invalid-html.jpg)

The code would not even try to locate the file. We already know that this is not valid.

### 4 Check the Cache Layer

Every time we *schedule* a **Celery Task** to convert the **YouTube** video into an MP3 we add a new record into our cache layer. 

This way we can check if the **UUID** (name of the mp3 file) belongs to a file that we are currently processing, or have ready to download.

!> This record on **Redis** has a TTL (time to live) value since we are not going to be storing the MP3 file forever.  
We talked about that in the section [Receiving the YouTube Link (13)](/app/receiving-the-youtube-link?id=_13-add-the-mp3-name-to-the-cache-layer)

If the **UUID** (name of the mp3 file) is not present, it means that either the file has been deleted or never existed.

!> Remember, we use the **UUID** string as the key in our cache layer

Now, if the key doesn't exist we jump to **[5 Return invalid.html response](/app/download-mp3?id=_5-return-invalidhtml-response)**. If it does, we jump to **[6 Task Finish](/app/download-mp3?id=_6-task-finish)**

### 5 Return invalid.html response

As we mentioned in **[4 Check the Cache Layer](/app/download-mp3?id=_4-check-the-cache-layer)**, if we jumped here it means that the key doesn't exist. 

So we show the **invalid.html** page located at `app/web/templates/invalid.html`

![Invalid file](../images/invalid-html.jpg)

### 6 Task Finish

Remember that we *asynchronously process our video* using a **Celery Task**. This means that the *task* could be waiting for a *worker* to be free to start converting the video into MP3.

Or maybe the video is being converted when the user makes the request.

> A *worker* is a process that executes a pre-defined function and it's triggered when a new *task* is given to it.  
> Our pre-defined function is the one at `app/convert/tasks/task.py` and the function name
> 
> ```
> @celery.task(bind=True,  
> 		autoretry_for=(Exception,),  
> 		retry_backoff=True,
> 		max_retries=3)  
> def download_audio(self, youtube_link, output_mp3_filename):  
>   
>    save_at = '{media_dir}{filename}'.format(media_dir=settings.MEDIA_DIR, filename=output_mp3_filename)
> ...
> ```

But, how do we know this?? That's covered in [Receiving the YouTube Link](/app/receiving-the-youtube-link)

We can ask our cache layer, built with **Redis**, to give us the content stored in the key with the name of the **UUID** (name of the MP3) and it will return two possible values: `ONQUEUE` or `FINISH`

If the value returned is `ONQUEUE` then we jump to **[7 Return not_ready.html response](/app/download-mp3?id=_7-return-not_readyhtml-response)**.

Otherwise jump to **[8 File exists in volume](/app/download-mp3?id=_8-file-exists-in-volume)** if it's `FINISH`

### 7 Return not_ready.html response

We inform the user that we're still converting the video

![File not ready](../images/file-not-ready.jpg)

### 8 File exists in volume

Let's start with the basics. What a hell is a volume????

In your docker-compose file `docker/docker-compose.yml` we have defined two volumes

!> Read about [Designing the docker-compose.yml](/coming-soon) for more information

```
volumes:
  converted_mp3_vol:
    external: true
  redis_vol:
    external: true
```

A *volume* is like a hard drive that we can use to preserve our data. 

This is useful because the storage (hard drive) of the containers is ephemeral.

That means that if the container crashes or gets shut down, any data that you stored on it will be lost.

We can attach/link volumes to containers. In our project, we attach the volume **converted_mp3** to two of our containers: **web** and **celery_workers**.

This way every time we create a new mp3 file we can store it inside the volume. 

That way we can be sure that if anything goes wrong, we still have the mp3 files safely stored.

Now that you know a bit more about volumes, we can move forward.

At this stage of the code, we know that the file should exist, but we also know that **sometimes things fail**. 

And that's why is a good practice to **ALWAYS** check that the file exists before trying to send it.

If the file exists in the volume, we jump to **[10 Send file](/app/download-mp3?id=_10-send-file)**, or to **[9 Return invalid.html response](/app/download-mp3?id=_9-return-invalidhtml-response)** if we can't find it.

### 9 Return invalid.html response

We know that the file is not present in our volume, so we return **invalid.html** page located at `app/web/templates/invalid.html`

![Invalid file](../images/invalid-html.jpg)


### 10 Send file

We've found the file, we can now send it to the user

```
return send_from_directory(settings.MEDIA_DIR, mp3_filename)
```
