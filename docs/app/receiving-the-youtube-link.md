# Receiving the YouTube Link

Our fronted doesn't do a lot of things, it just needs to receive a **YouTube** URL and send it to our backend.

We've already seen how this is done in [The Frontend](/app/frontend?id=javascript) **Javascript** section.

## Backend Endpoint

!> What's an endpoint? It's a fancy way to call URL's in the context of [REST API's](https://www.ibm.com/cloud/learn/rest-apis)

In our application, this endpoint is `http://127.0.0.1:8080/submit` 

Open the file at `app/main.py` and look for the code that starts with `@app.route('/submit', methods=["POST"])`

Let's see the first two lines

```
@app.route('/submit', methods=["POST"])
```

We use the *route* decorator to define our endpoint and we're only going to accept requests of type **POST**.

!> Remember a *route* is what allows us to create a URL for our users to use.

```
request_data = request.get_json()
```

We need to talk about the **request** object.

> You can read the docs here: [https://werkzeug.palletsprojects.com/en/2.2.x/wrappers/#werkzeug.wrappers.Request](https://werkzeug.palletsprojects.com/en/2.2.x/wrappers/#werkzeug.wrappers.Request) 

This *object* has all the information that the browser sends when the user makes the request to the endpoint.

> Translation: When the user hits the button **Convert to MP3** in our frontend, the javascript function associated with that button sends an HTTP Request to our endpoint `http://127.0.0.1:8080/submit` with the link that the user wants to convert to MP3 and some extra information that the browser *always* sends by default.

In our project, we're only interested in the *payload* sent by the javascript file. 

That's the `const data = ...` in the first line.

```
const data = { video_url:  document.getElementsByName('video_url')[0].value };

fetch('http://127.0.0.1:8080/submit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  ....
```

As you can see, the `body` is our `payload`. These two words are interchangeable but most of the time we use the word *payload* to talk about the information needed by the endpoint to work.

To access the *payload* in our backend, we use `request.get_json()` and that's because the data in the *payload* is encoded in [JSON](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON) format.

!> That's what the line `JSON.stringify(data)` does in the javascript file. It encodes the javascript object *const data* into a JSON

## About The Cache Layer

Before we start analyzing the flowchart, we need to talk about the cache layer.

We're using a cache layer in our backend to do a few things.

But what's a cache? A cache solution to store frequently accessed data somewhere to improve performance by avoiding accessing it directly from the source.

In our project, the cache layer is built using **[Redis](https://redis.io/)**, an *in-memory* database.

**Redis** is a *key-value* database. This means that you only have two fields:

- Key: An index, like a variable, where you store information
- Value: The data that you want to store

```
redis_connection.set('video_id', 'p9kdDet7G14')            
```

In this example we are storing the value **p9kdDet7G14** inside the key **video_id**

The cool thing about having an *in-memory* database is that it's super fast.

The bad thing is that you need *memory*, RAM to be more precise, and that should be taken into account.

In most cases, **Redis** will be running in a separate machine so the RAM is fully dedicated to the service.

Now that you know a little bit more about Cache and **Redis**, you might be wondering why and where are we using them. 

**Why?** Because we want to reduce the number of calls we make to YouTube to check if a video exists or not.

**Where?** Every time a new video is sent to our backend, and also to track the status of our **convert to mp3** task.

This is useful when you have a lot of traffic since there are more chances to have a *cache hit* in that scenario.

> This project is only for learning, but cache layer design is quite common in systems with high volume traffic and it's something you should take into consideration when you're designing your app.

## Flowchart

![FlowChart Submit Endpoint](../images/flowchart-submit-endpoint.png)

*The numbers in the flowchart don't necessarily indicate steps, it is just for making the documentation easier*

### 1 The Entrypoint

Our frontend, as mentioned above, will be sending the information to the endpoint `/submit`

### 2 Check Valid URL and Cache Layer

We make two checks here:

**Check if the video is cached**

If the video ID (Ex.: Given https://www.youtube.com/watch?v=p9kdDet7G14, the video ID is *p9kdDet7G14*) is already present in the cache and with a value has. If it's 404, it means that the video doesn't exist on YouTube.

**Is a valid YouTube Video?**

Check if the URL given is a valid YouTube URL.

If one of these conditions is **TRUE**, jump to **[3 Return Error](/app/receiving-the-youtube-link?id=_3-return-error)**

If the result is **FALSE**, jump to **[4 URL in cache](/app/receiving-the-youtube-link?id=_4-url-in-cache)**

### 3 Return Error

Abort the process and return an error with HTTP 400.

The javascript will see that and show an error to the user.

!> Check [The Frontend](/app/frontend?id=javascript) **Javascript** section

### 4 URL in cache

The URL, or video ID to be precise, is present on the cache?

- If **True** (*cache hit*), jump to 10
- If **False**, jump to 5

### 5 Video exists on YouTube

We make a call to the **YouTube Thumbs** service 

```
video_thumb = requests.get('https://img.youtube.com/vi/{v_id}/0.jpg'.format(v_id=video_id))
```

This is a *hack* to check if a video exists or not on **YouTube**

If it does exist, we jump to **[8 Video Exists](/app/receiving-the-youtube-link?id=_8-video-exists)**, if not, we jump to **[6 Store in Cache non-existing Video ID](/app/receiving-the-youtube-link?id=_6-store-in-cache-non-existing-video-id)**

### 6 Store in Cache non-existing Video ID

Since the video doesn't exist on **YouTube** and we want to reduce the number of calls we make. We store the video ID in the cache.

```
rc.set(settings.CACHE_VIDEO_ID_KEY.format(vid=video_id), settings.CACHE_VIDEO_ID_DONT_EXISTS_CODE)
```

Where `settings.CACHE_VIDEO_ID_KEY` is the *key* we use to identify the record on **Redis** 

!> `CACHE_VIDEO_ID_KEY = "ve_{vid}"` from file `app/web/settings.py`

And if we replace the variable, it would look like this

```
# Given URL https://www.youtube.com/watch?v=p9kdDet7G14

rc.set("ve_{vid}".format(vid= p9kdDet7G14), '404')

# or fully replaced
rc.set("ve_p9kdDet7G14", '404')
```

### 7 Return Error

Since the video doesn't exist, we need to return an error.

```
return APIResponse(
    data={},
    message="Video doesn't exists",
    message_code="VIDEO_DONT_EXISTS",
    http_code=400
)
```

This will be caught by our javascript function as described on the [The Frontend](/app/frontend?id=javascript) **Javascript** section.

### 8 Video Exists

Now we know that the video exists (this happened in **[5 Video exists on YouTube](/app/receiving-the-youtube-link?id=_5-video-exists-on-youtube)**), we store the video ID in our cache layer and flag it as an existent video.

```
rc.set(settings.CACHE_VIDEO_ID_KEY.format(vid=video_id), settings.CACHE_VIDEO_ID_EXISTS_CODE)

# Or replacing variables, if the video URL is https://www.youtube.com/watch?v=p9kdDet7G14 

rc.set("ve_p9kdDet7G14", '200')
```

### 9 Reload our cache values

At this point, we've added a new entry to our cache layer. 

This means that we need to update the variable that stores information about our cache status.

### 10 Send an asynchronous task to create the MP3

Our code uses **[Celery](https://docs.celeryq.dev/en/stable/index.html)** to help us create **Tasks** that run *decoupled* from our main code. 

This allows us to create a scalable and efficient app. 

!> We will talk more about celery later on.

At this stage, we call our **Celery Task** and send the video URL that we want to download and convert to MP3. 

This process *schedules* a task and the task might not run right away since it's attached to a *queue* with a pool of *workers* (functions).

The *workers* in that pool might be running other **Tasks**, but once a *worker* is released our request will be processed.

### 11 Check if Task has been enqueued

If the **scheduling** process is successful, we store it in our cache (**[13 Add the MP3 name to the cache layer](/app/receiving-the-youtube-link?id=_13-add-the-mp3-name-to-the-cache-layer)**).

### 12 Unable to schedule the task

If something went wrong, we return an error. 

The javascript function will show that error to the user.

### 13 Add the MP3 name to the cache layer

Store the name that the MP3 file will have once is finished

```
cache_key = mp3_name
rc.setex(cache_key, settings.CACHE_DEFAULT_TTL, settings.TASK_QUEUED_STATUS_CODE)
```

Notice the variable `settings.CACHE_DEFAULT_TTL` and the use of `rc.setex`. 

What this does is set an expiration time for the key. Meaning that after *N* seconds that key will be automatically deleted from our cache.

But why?, Imagine that the **task** fails and we can't create that MP3. We don't want that key to exist forever in our cache. 

So if after `settings.CACHE_DEFAULT_TTL` (set to 1 hour) the mp3 is not created, that key will be deleted and when the user tries to download the file, we can tell the user to try again.

### 14 Return 201

The request has been made and everything is ok. 

The javascript will tell the user where the mp3 will be available in a few minutes. 
