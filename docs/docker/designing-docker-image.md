# DISCLAIMER <!-- {docsify-ignore} -->

This documentation is a work in progress

---

# Designing the Dockerfile

One of the concepts you need to know about Docker is *images*

> Docker images are the basis of containers. An Image is an ordered collection of root filesystem changes and the corresponding execution parameters for use within a container runtime. An image typically contains a union of layered filesystems stacked on top of each other. An image does not have state and it never changes.
> 
> Source: [https://docs.docker.com/glossary/](https://docs.docker.com/glossary/)

Pretty clear, right? 😅

Docker images are the way you *packetize* your microservice so you can deploy it anywhere you want without having to worry about what OS is running, what version, dependencies, etc.

Is like *compiling* your code and including all the dependencies inside of it.

For that image to *run* as a *container* you only need the *docker engine* running on that box.

Inside the *docker image* you have everything you need to run your app. All the dependencies, libraries, and binary necessaries.

![Docker Stack Diagram](../images/docker-stack-diagram.png)

!> A docker container **is not a Virtual Machine (VM)**, is lighter and shares resources with the *host os*

That *image* is built by defining a file called **Dockerfile**

> A Dockerfile is a text document that contains all the commands you would normally execute manually in order to build a Docker image. Docker can build images automatically by reading the instructions from a Dockerfile.

Inside the directory `docker` you can find the `Dockerfile` for our three services:

- **Web** Our front and backend (`docker/web/Dockerfile`)
- **Convert** Where the *Celery* task is placed and from where we launch our *workers* (`docker/convert/Dockerfile`)
- **Cleanup** It's the service that will delete the MP3 files after 8 hours (`docker/cleanup/Dockerfile`)

We've covered this services at [Architecture](/docker/architecture) section.

!> Here's a good tutorial covering a lot of topics on docker [https://www.tutorialspoint.com/docker/index.htm](https://www.tutorialspoint.com/docker/index.htm)

## App

Open the file `docker/web/Dockerfile`

```dockerfile
FROM python:3.8-alpine

RUN apk upgrade -U \ 
    && apk --no-cache add ca-certificates

# crate a non-root user	
# and set workdir
ARG DF_USER=youtubemp3
ARG DF_UID=1000
ENV SF_USER ${DF_USER}
ENV SF_UID ${DF_UID}
ENV HOME /app
ENV PYTHONPATH ${HOME}
ENV PATH ${PATH}:${HOME}/.local/bin

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${SF_UID} \
    ${SF_USER}

RUN mkdir /data && chown ${SF_USER} /data
# This dir should be the mounting point
WORKDIR ${HOME}
COPY app/web ${HOME}/web
COPY app/convert ${HOME}/convert
COPY docker/web/requirements.txt requirements.txt

USER root
RUN chown -R ${SF_USER}:${SF_USER} ${HOME}
RUN chmod 777 ${HOME}

USER ${SF_USER}

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN rm requirements.txt

CMD [ "waitress-serve", "--listen=*:8080", "web.main:app" ]
```


As you can see a lot is going on. But don't be afraid isn't that difficult.

`FROM python:3.8-alpine` Every docker image start with a *base* image. This is what the **FROM** command does. In our case, we're telling docker that our starting point for the image will be the [python:3.8-alpine](https://hub.docker.com/_/python/tags). As you can see the image name has three parts **python**:**3.8**-**alpine**.

The first part tells us that we want a base image for running python. This means that it will include all the necessary software to run python successfully.

Then we have the notation `:` that indicates the tag/version. In our case, we're using a python image that will run python version 3.8.

And lastly, we define the OS that we want `alpine`. Alpine is a minimal Linux distribution.

As a general rule of thumb, when you're creating your docker image, you want to install **ONLY** what you need for your software to run.

This is one of the many good practices that will also help you create a more *secure* container. 

By reducing the number of libraries available on the container we reduce the risk of exploits that could be used by an attacker.

It also helps reduce the size of the image, and that's quite desirable in your CI/CD pipeline (we will cover this later on)

`RUN apk upgrade -U && apk --no-cache add ca-certificates` This will upgrade the OS and then install SSL certificate authorities.


```dockerfile
# crate a non-root user	
# and set workdir
ARG DF_USER=youtubemp3
ARG DF_UID=1000
ENV SF_USER ${DF_USER}
ENV SF_UID ${DF_UID}
ENV HOME /app
ENV PYTHONPATH ${HOME}
ENV PATH ${PATH}:${HOME}/.local/bin

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${SF_UID} \
    ${SF_USER}
```

Another best practice for security is **NEVER RUN YOUR PROCESS AS ROOT INSIDE A CONTAINER**. That's why we're creating a non-root user in this part of the code.

We also define a few env vars that will be used later on.

```dockerfile
RUN mkdir /data && chown ${SF_USER} /data
# This dir should be the mounting point
WORKDIR ${HOME}
COPY app/web ${HOME}/web
COPY app/convert ${HOME}/convert
COPY docker/web/requirements.txt requirements.txt
```

The first line creates a new directory called `data` that's where we are going to mount the *converted_mp3_vol* volume. We covered what a volume is at [Backend](/app/backend?id=_8-file-exists-in-volume) section.

After that, we copy the *app* and *convert* service code into our container alongside with the `requirements.txt` file that contains all the necessary packages for our *app* service to run.

Notice that we are copying the files of the *convert* service into the *app* image. But why? is because *app* needs to be able to *schedule* the task to convert the video and needs access to the code to be able to do that.

```python
# at app/web/main.py

try:
	download_audio.delay(request_data['video_url'], "{}.mp3".format(mp3_name))
            
	app.logger.debug("Sending the task to download the video ID '{}'".format(video_id))
except Exception as e:
	raise e
```

The function `download_audio` is located at the *convert* service. And to use it we need to import it `from convert.tasks.task import download_audio` and that's why we need to include it in our image.

That's covered at [Backend](/app/backend?id=_10-send-an-asynchronous-task-to-create-the-mp3) section

```dockerfile
USER root
RUN chown -R ${SF_USER}:${SF_USER} ${HOME}
RUN chmod 777 ${HOME}

USER ${SF_USER}
```

As user **root** to change the ownership of the *home* directory from *root* to the non-root user we've created called `youtubemp3`.

And after that's ready finally change and stay executing commands as the non-root user `youtubemp3`

```dockerfile
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN rm requirements.txt
```

Now we install all the python libraries that our *app* service needs and then remove the `requirements.txt` file since we no longer need it in our container image.

```dockerfile
CMD [ "waitress-serve", "--listen=*:8080", "web.main:app" ]
```

This last command is the one that will be always executed when our container launches. [waitress-serve](https://docs.pylonsproject.org/projects/waitress/en/latest/) is the process that will launch the python file to make our *app* service available and ready to receive requests.
