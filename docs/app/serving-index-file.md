# DISCLAIMER
**This document is a work in progress**

---

# Showing the Index File

As mentioned in the [README.md](../../README.md) the backend is built using [Flask Framework](https://flask.palletsprojects.com/en/2.1.x/)

If you're new to Flask o Frameworks please take a moment to read the documentation since I won't go into details about this subject.

## The Home / Index URL

Start by opening the file at `app/web/main.py`

You'll see a few imports and variables sets and then you'll see this code

```
@app.route('/', methods=["GET"])
def home():
    return render_template('index.html')
```

This is what gets executed when you open the web at [http://127.0.0.1:8080/](http://127.0.0.1:8080/)

> See the section **How to use it** first at [README.md](../../README.md)

The first line, it's called a [decorator](https://www.programiz.com/python-programming/decorator) and creates a **route** (an URL address) that when visited triggers the function **home()** in our example.

> You can use any name on the function. It has no relationship with the URL address.

You can see the first argument that this function takes is `/` this is the route that we want to define. And in our case, this is the home or index of your web.

The second parameter is `methods=["GET"]`. This is related to how requests can be made to an URL. We just want to allow GET requests to be made, because we only need to show the user our **index.html** and nothing more.

> About Http methods: [https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)

Then we have the function. We're using the [template system](https://flask.palletsprojects.com/en/2.1.x/quickstart/#rendering-templates) that comes with **Flask** to process our **index.html** and returning the result.

## Comments

In this case, our backend only acts as a **Web Server** since we're only showing an html file.

We could replace this function and use, for ex., an [nginx](https://nginx.org/en/) to serve the **index.html**.

By doing so, we could use our backend to act as a *pure* [Rest API](https://www.ibm.com/cloud/learn/rest-apis) 

But for learning purposes, I believe that the current design works just fine.