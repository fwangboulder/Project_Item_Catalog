# Project_Item_Catalog
Project 5 Udacity Full Stack Developer Nanodegree

#Project Overview

Develop an application that provides a list of items within a variety of
categories as well as provide a user registration and authentication system.
Registered users will have the ability to post, edit and delete their items.

This alumni app provides alumni information for different universities currently
working in different companies. It will be good to check where graduates go and
if you need a refer for a job. Easy to find them! You can login with your google
account or facebook account and add more information if you want.

Key words: Flask, RESTful web application, OAuth authentication, HTTP, Bootstrap,
            Python, CSS, HTML

Achievement:

    1. Efficiently interacting with data is the backbone upon which performant web applications are built

    2. Properly implementing authentication mechanisms and appropriately mapping HTTP methods to CRUD operations are core features of a properly secured web application
#How to run it?

    1. $ git clone https://github.com/fwangboulder/Project_Item_Catalog.git

    2. $ cd Project_Item_catalog
        make sure you have installed Vagrant and VirtualBox (conceptual overview: https://www.youtube.com/watch?v=djnqoEO2rLc)
        check for success installation by checking the version
          $vagrant --version
        more detailed about vagrant test: https://github.com/fwangboulder/Project_Tournament_Results
    3. $ vagrant up
       $ vagrant ssh
    4. $ cd /vagrant
       $ ls
          view files you have.
    5. $python project.py

    6. Open your browser: http://localhost:9000


    7. Before you login, you can only view all the university and graduates.

    8. After you login with your google account, you can play with create, edit and delete functions.

    9. Want to view JSON format data?
        View all universities: http://localhost:9000/university/JSON
        View all graduates for university #1: http://localhost:9000/university/1/graduate/JSON/
        View one graduate: http://localhost:9000/university/1/graduate/1/JSON/
