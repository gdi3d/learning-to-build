# DISCLAIMER

**This document is a work in progress and I'll be building the tutorial for all the pieces in the coming weeks along with some modifications.**

--- 
# Learning to Build

This project was created as a tutorial for people that are trying to improve their coding skills and aims to help how to go through the whole process of building an app/system from the idea to the deployment stage.

<video width="720" controls>
  <source src="https://user-images.githubusercontent.com/4661798/181342079-e9b51d45-33b0-4e12-819f-12a9739495e0.mp4" type="video/mp4">
</video>

### Documentation (W.I.P)

- [Fronted](docs/app/frontend.md)
- [Showing the index file](docs/app/serving-index-file.md)
- [Receiving the YouTube Link](docs/app/receiving-the-youtube-link.md)
- Download the MP3 file (soon)
- Converting the Video using Celery (soon)
- Designing Docker Images (soon)
- Designing the docker-compose.yaml file (soon)

### Overview

![Screen Code Guide](/images/screen-code-guide.png)

# What's is about?

This project is a simple, yet fun web app that allow you to convert YouTube videos into mp3 files.

It uses:

- [Flask Framework](https://flask.palletsprojects.com/en/2.1.x/)
- [Bulma CSS Framework](https://bulma.io/)
- [Docker](https://www.docker.com/get-started/)
- [Python](https://www.python.org/)
- [Celery](https://docs.celeryq.dev/en/stable/index.html)
- [Redis](https://redis.io/)
- [Linux Cronjobs](https://www.educba.com/cron-in-linux/)

The project uses a microservices architecture. What are microservices? to put it in simple terms microservices pattern is a way to split into small piece a system, and each microservice is designed to do one thing and one thing only.

> To know more about microservices and why it's used, read these articles
> 
> [https://www.geeksforgeeks.org/microservices-introduction/](https://www.geeksforgeeks.org/microservices-introduction/)  
> [https://medium.com/microservicegeeks/an-introduction-to-microservices-a3a7e2297ee0](https://medium.com/microservicegeeks/an-introduction-to-microservices-a3a7e2297ee0)  
> [https://dzone.com/articles/what-is-microservices-an-introduction-to-microserv](https://dzone.com/articles/what-is-microservices-an-introduction-to-microserv)


# How to use it

Here's a (not so beginner) guide:

1. Clone this repository in your
  
  ```
  git clone git@github.com:gdi3d/learning-to-build.git
  ```
   
2. Build the three images that composed this app  
  
  ```
  docker build -t youtubemp3_web -f docker/web/Dockerfile .
  docker build -t youtubemp3_convert -f docker/convert/Dockerfile .
  docker build -t youtubemp3_cleanup -f docker/cleanup/Dockerfile .
  ```
  
3. Create the docker volumes
   
  ```
  docker volume create converted_mp3_vol
  docker volume create redis_vol
  ```
    
4. Launch the docker compose

  ```
  docker-compose -f docker/docker-compose.yml up
  ```
  
5. Open your browser and go to [http://127.0.0.1:8080/](http://127.0.0.1:8080/) to the see the application



# Need Help or would like to learn how this is built?

Contact me at my [Linkedin](https://www.linkedin.com/in/adrianogalello/) and we can schedule a call
   
