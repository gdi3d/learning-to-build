# Showing the Index File

As mentioned in the [Getting Started](/README?id=what39s-it-about) the backend is built using [Flask Framework](https://flask.palletsprojects.com/en/2.1.x/)

If you're new to Flask o Frameworks please take a moment to read the documentation since I won't go into details about this subject.

## The Home / Index URL

Start by opening the file at `app/web/main.py`

You'll see a few *imports*, *variables* and then you'll see this code

```
@app.route('/', methods=["GET"])
def home():
    return render_template('index.html')
```

This is what gets executed when you open the web at [http://127.0.0.1:8080/](http://127.0.0.1:8080/)

!> Remember that http://127.0.0.1:8080 means that you are running the code on your machine (localhost)

> See the section **How to use it** first at [Getting Started](/README)

The first line, it's called a [decorator](https://www.programiz.com/python-programming/decorator) and creates a **route** (an URL address) that when visited triggers the function **home()** in our example.

!> You can use any name on the function. It has no relationship with the URL address.

The first argument that this function takes is `/`. That's the route we want to define. This is the *home* or *index* of the web.

The second parameter is `methods=["GET"]`. This is related to how requests can be made to an URL. We just want to allow GET requests because we only need to show the **index.html** and nothing more.

> About HTTP methods: [https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)

And to show the **index.html** we use the function `render_template`. 

We're using the [template system](https://flask.palletsprojects.com/en/2.1.x/quickstart/#rendering-templates) that comes with **Flask** to process our **index.html** and returning it to the browser.

## Comments

In this case, our backend only acts as a **Web Server** since we're only showing an HTML file.

We could replace that code and use for example [Nginx](https://nginx.org/en/) to serve the **index.html**.

By doing so, we could use our backend to act as a *pure* [Rest API](https://www.ibm.com/cloud/learn/rest-apis) 

But for learning purposes, the current design works just fine.