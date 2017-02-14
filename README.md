# Project_Item_Catalog
Project 5 Udacity Full Stack Developer Nanodegree

**Project Overview**

Develop an application that provides a list of items within a variety of
categories as well as provide a user registration and authentication system.
Registered users will have the ability to post, edit and delete their items.

Key words: Flask, RESTful web application, OAuth authentication, HTTP, Bootstrap, CSS

**Achievement:**

    1. Efficiently interacting with data is the backbone upon which performant web applications are built

    2. Properly implementing authentication mechanisms and appropriately mapping HTTP methods to CRUD operations are core features of a properly secured web application

**How to run it?**

    1. $ git clone https://github.com/fwangboulder/Project_Item_Catalog.git
    2. Go to templates folder. type in your own client ID in login.html file
          Don't have your client ID and do not know how to get it?
          Read the last paragraph of this file: https://github.com/fwangboulder/DailyCodePractice/blob/master/framework/AuthenticationAuthorization/README.md

    3. Download your ClientID JSON file and rename it as client_secrets.json, store
        it in the same folder as project.py file.

    4. $python project.py

    5. http://localhost:9000/login

    6. If you see an error about JSON serializable. update your versions of Flask.

      ```
      $pip install werkzeug==0.8.3

      $pip install flask==0.9

      $pip install Flask-Login==0.1.3

      Note: If you get a permissions error, you will need to include sudo at the beginning of each command. That should look like this: sudo pip install flask==0.9

      ```
    7. try to play with app and logout it
