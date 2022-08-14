# Converting the Video Using Celery

We talked briefly about celery in [Download the MP3 file](/app/download-mp3.md) section about *workers*, *pool of workers*, *scheduled tasks*, etc.

We are now going to dive a little bit deeper into the **Celery** world since it's something that you are going to be using a lot. 

Even if you don't use **Celery**, the same concepts will apply to other libraries and to the idea of how to build scalable systems.

What's celery anyway?

> Celery is a simple, flexible, and reliable distributed system to process vast amounts of messages while providing operations with the tools required to maintain such a system.
> 
> It’s a task queue with focus on real-time processing, while also supporting task scheduling.
>
> Source: [https://docs.celeryq.dev/en/stable/getting-started/introduction.html](https://docs.celeryq.dev/en/stable/getting-started/introduction.html)

Or in a nutshell:

A system that allows you to execute medium or long-running *tasks* (functions) in the backend by sending a *message* with the *task* that we want to run.

## The procrastination way

!> TL;DR let your video transformation happen in an *asynchronous* way and notify the user when it's ready.

When you're working with medium/long process tasks like extracting audio from a video, you don't want to do it in a *synchronic way* or *right away*.

Let's take a real-world example:

You take your phone to the repair shop. They ask you what's wrong, you leave the phone and come back a few days to pick it up.

That's an *asynchronous* task. The technician can keep on working on the other phones until he's free to fix yours while you wait at home.

The *synchronic* way would require you to stay inside the shop holding your phone in your hand until the technician is free to help you. You'll be there for hours o days just waiting.

That's a pretty bad user experience.

Now let's see our app flow:

1. The user send us a YouTube URL
2. The back run some validations
3. The back converts the video into an MP3 file

One of the most important things while developing apps is to avoid *locking* the user into a screen after clicking on something.

You already see this every day in other apps. When you upload a video to any platform, you only get *locked* on the same screen while the video is being uploaded from your computer to the server.

This is because a file transfer is being made and can't be aborted to continue.

But once the file has been uploaded to the server, you can keep on using the platform as usual and will get notified when the video is ready or published.

This is an *asynchronous* process. Meaning that you no longer need to wait for something to finish to do something else.

The way to design these processes is by using a *broker* and a *queue* to process *tasks*.

There are a few components to analyze

1. **Producers** apps/systems that generate requests for tasks
2. **Consumers** functions that process those tasks
3. **Broker** a system that receives *messages* and *routes* those messages into *queues*
4. **Queues** a system that *stores* the *messages* that will be sent to the *consumers* by the queue. In this case the *consumers* could ask for messages when they are free, or the **queue** could *push* the message on [*pub/sub* pattern](https://ably.com/blog/pub-sub-pattern-examples) (in the pub/sub pattern *consumers* are named *subscribers*)

!> Our app doesn't notify us about the video being ready because the project will be a little more complex. But it could be a nice feature for the next version.

## Flow Diagram

![Scheduling Celery Task](../images/schedule-celery-task-graph.png)

This is the flow that our app follows to convert the video into an mp3

1. The user enters the **YouTube URL** and clicks **Download as MP3**
2. The **YouTube URL** is sent to the *backend* where our *producer* talks to **Celery** (using the *download.delay(...)* command) to schedule the task.
3. That *scheduling* procedure sends a *message* to **Redis**, which acts as a *Broker and Message Queue* at the same time, and stays there waiting.
4. When one of the workers in the *pool* it's free, meaning it's not doing anything, it will automatically ask the *queue* if there are any new messages and start processing our new message.  
  1. We use the tool [youtube-dl](https://github.com/ytdl-org/youtube-dl) to convert the video to MP3
5. The worker runs the task and saves the MP3 to the *convert\_mp3\_vol* volume defined in our *docker-compose.yaml*

!> Did you notice?, we're using **Redis** as a cache layer and a broker & queue system 😎.

!> For a more advanced broker and queue system you can check [RabbitMQ](https://www.rabbitmq.com/)
