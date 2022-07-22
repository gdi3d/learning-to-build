# DISCLAIMER

**This document is a work in progress and I'll be building the tutorial for all the pieces in the coming weeks along with some modifications.**

--- 
# Learning to Build

This project was created as a tutorial for people that are trying to improve their coding skills and aims to help how to go through the whole process of building an app/system from the idea to the deployment stage.

# What's is about?

This project is a simple, yet fun web app that allow you to convert YouTube videos into mp3 files.

It uses:

- Flask Framework
- Bulma CSS Framework
- Docker
- Python
- Celery
- Redis
- Crontabs
- Digital Ocean

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
   
