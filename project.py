##########################################
# Project 5: Item Catalog
# Date Started: 01/30/2017
# Date Completed: 02/16/2017
# Submitted by: Fang Wang
##########################################

########################## Media File ########################
# Description: This is the main file creating the web app
##############################################################

#! /usr/bin/env python

from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for, flash
# code for SQLAlchemy and database engine in sessionmaker
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, University, Graduate, User
##############################
# use Flask Login Decorator
from functools import wraps
#*****************************
# New Imports for Authentication And Authorization
from flask import session as login_session
import random
import string

#*****************************
# Import for GConnect
# create a flow object form the clientssecrets JSON file,
# which stores your client ID, client secret and other OAuth 2.0 praameters
# if no such module: $ pip install --upgrade oauth2client
from oauth2client.client import flow_from_clientsecrets
# use FlowExchangeError method catch the error trying to exchange an
# authorization code for an access token.

from oauth2client.client import FlowExchangeError
import httplib2
# json module provides an API for converting in memory Python objects
# to a serialized representation
import json
# make_response method converts the return value from a function
# into a real response object that can be sent off to client
from flask import make_response
# requests is an Apache 2.0 licensed HTTP library
import requests
#**************************************************

app = Flask(__name__)

###################################
# Rename it to client_secrets.json
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "alumni app"
#####################################

engine = create_engine('sqlite:///alumni.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a state token to prevent request foregery
# Store it in the session for later validation


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for i in xrange(32))
    login_session['state'] = state
    # return 'The current session state is %s' %login_session['state']
    # after create the login.html in templates, now render it
    return render_template('login.html', STATE=state)
#################################
# declare login decorator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function
#################################


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)

    h = httplib2.Http()
    # To make sure this project will work for anyone using python 2.xx or 3.x.x
    # convert h.request(url,'get')[1] (bytes) to string.
    result = json.loads(h.request(url, 'GET')[1].decode("utf8"))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # check to see if the user_id is in the ;login_session
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' "style = "width: 300px; height: 300px;border-radius:
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# ##################################

####################################
# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).all()
    return user[0].id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

##################################
# Disconnect- revoke a current user's token and reset the login_session


@app.route('/gdisconnect')
def gdisconnect():
    # only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke current token.
    #access_token = login_session['access_token']
    access_token = credentials.access_token
    # print 'In gdisconnect access token is %s', access_token
    # print 'User name is: '
    # print login_session['username']
    # if access_token is None:
    # print 'Access Token is None'
    #response = make_response(json.dumps('Current user not connected.'), 401)
    #response.headers['Content-Type'] = 'application/json'
    # return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # print 'result is '
    # print result
    # del login_session['credentials']
    # del login_session['gplus_id']
    # del login_session['username']
    # del login_session['email']
    # del login_session['picture']
    if result['status'] == '200':
        # reset the user's session
        #del login_session['access_token']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


###################################
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fbclientsecrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fbclientsecrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode("utf8")

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode("utf8")
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode("utf8")
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; \
    border-radius: 150px;-webkit-border-radius: 150px;  \
    -moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1].decode("utf8")
    return "you have been logged out"


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for("showUniversity"))
    else:
        flash("You were not logged in to begin with!")
        return redirect(url_for("showUniversity"))


################################


################################


@app.route('/university/<int:university_id>/graduate/JSON/')
def graduatesJSON(university_id):
    university = session.query(University).filter_by(id=university_id).one()
    graduates = session.query(Graduate).filter_by(
        university_id=university_id).all()
    return jsonify(graduates=[i.serialize for i in graduates])

    # return 'Route 9: This is the JSON format information of all graduates in
    # university %s!' %university_id


@app.route('/university/<int:university_id>/graduate/<int:graduate_id>/JSON/')
def graduateJSON(university_id, graduate_id):
    graduate = session.query(Graduate).filter_by(id=graduate_id).one()
    return jsonify(graduate=graduate.serialize)

    # return 'Route 10: This is the JSON format information of one graduate %s
    # in university %s!' %(graduate_id, university_id)


@app.route('/university/JSON/')
def universityJSON():
    universities = session.query(University).all()
    return jsonify(universities=[i.serialize for i in universities])

    # return 'Route 11: This is the JSON format information all universities!'


# show all universities
@app.route('/')
@app.route('/university/')
def showUniversity():

    universities = session.query(University).all()
    # check if username is in login_session.
    if 'username' not in login_session:
        return render_template(
            'publicuniversities.html',
            universities=universities)
    else:
        return render_template('universities.html', universities=universities)
    # return "Route 1: This page will show all my university in databases!"

# create new university


@app.route('/university/new/', methods=['GET', 'POST'])
# used the decorator function, replace the login check code.
@login_required
def newUniversity():
    # if 'username' not in login_session:
    #    return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            university = University(
                name=request.form['name'],
                user_id=login_session['user_id'])
            session.add(university)
            session.commit()
        return redirect(url_for('showUniversity'))
    else:
        return render_template('newUniversity.html')
    # return "Route 2: This page will be for creating new university!"

# edit a university


@app.route('/university/<int:university_id>/edit/', methods=['GET', 'POST'])
# used the decorator function, replace the login check code.
@login_required
def editUniversity(university_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    university = session.query(University).filter_by(id=university_id).one()
    if university.user_id != login_session['user_id']:
        # return """<script> function myFunction()
        # {alert('Not allowed to edit university created by others');}
        # </script>
        # <body onload='myFunction()'>
        # """
        flash("You are not allowed to edit university created by others! \
        Please create new university!")
        return redirect(url_for('showUniversity'))

    if request.method == 'POST':
        if request.form['name']:
            university.name = request.form['name']
        session.add(university)
        session.commit()
        return redirect(url_for('showUniversity'))
    else:
        return render_template(
            'editUniversity.html',
            university=university)
    # return "Route 3: This page will be for editting a university %s!"
    # %university_id

# delete a university


@app.route('/university/<int:university_id>/delete/', methods=['GET', 'POST'])
# used the decorator function, replace the login check code.
@login_required
def deleteUniversity(university_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    university = session.query(University).filter_by(id=university_id).one()
    if university.user_id != login_session['user_id']:
        # return """<script> function myFunction()
        # {alert('Not allowed to delete this university.
        # Please create your own for delete.');}
        # </script>
        # <body onload='myFunction()'>
        # """
        flash("You are not allowed to delete university created by others! \
        Please create new university!")
        return redirect(url_for('showUniversity'))
    if request.method == 'POST':
        session.delete(university)
        session.commit()

        return redirect(url_for('showUniversity'))
    else:
        return render_template('deleteUniversity.html', university=university)

    # return "Route 4: This page will be for deleting a university %s!"
    # %university_id

# show graduates in a university


@app.route('/university/<int:university_id>/')
@app.route('/university/<int:university_id>/graduate/')
def showGraduate(university_id):
    university = session.query(University).filter_by(id=university_id).one()
    graduates = session.query(Graduate).filter_by(
        university_id=university_id).all()
    # protect each graduate based on whoever create it.
    creator = getUserInfo(university.user_id)
    if 'username' not in login_session or creator.id != login_session[
            'user_id']:
        return render_template(
            'publicgraduates.html',
            graduates=graduates,
            university=university,
            creator=creator)
    else:
        return render_template(
            'graduates.html',
            graduates=graduates,
            university=university,
            creator=creator)

    # return "Route 5: This page will show graduates in  university %s!"
    # %university_id

# add new graduate


@app.route(
    '/university/<int:university_id>/graduate/new/',
    methods=[
        'GET',
        'POST'])
# used the decorator function, replace the login check code.
@login_required
def newGraduate(university_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    university = session.query(University).filter_by(id=university_id).one()
    if university.user_id != login_session['user_id']:
        # return """<script> function myFunction()
        # {alert('Not allowed to add graduate to this university.
        # Please create your university for add.');}
        # </script>
        # <body onload='myFunction()'>
        # """
        flash("You are not allowed to add graduate to university \
        created by others! Please create new university!")
        return redirect(url_for("showUniversity"))
    if request.method == 'POST':
        graduate = Graduate(
            name=request.form['name'],
            company=request.form['company'],
            email=request.form['email'],
            major=request.form['major'],
            graduate_year=request.form['graduate_year'],
            university_id=university_id,
            user_id=university.user_id)
        session.add(graduate)
        session.commit()
        flash("new graduate profile created!")
        return redirect(url_for("showGraduate", university_id=university_id))
    else:
        return render_template('newGraduate.html', university_id=university_id)

    # return "Route 6: This page will be for add a new graduate in university
    # %s!" %university_id

# edit a graduate


@app.route(
    '/university/<int:university_id>/graduate/<int:graduate_id>/edit/',
    methods=[
        'GET',
        'POST'])
# used the decorator function, replace the login check code.
@login_required
def editGraduate(university_id, graduate_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    graduate = session.query(Graduate).filter_by(id=graduate_id).one()
    university = session.query(University).filter_by(id=university_id).one()
    # if university.user_id!=login_session['user_id']:
    #     # return """<script> function myFunction()
    #     # {alert('Not allowed to edit this graduate.
    # Please create your own for edit.');}
    #     # </script>
    #     # <body onload='myFunction()'>
    #     # """
    #     flash("You are not allowed to edit graduate created by others!")
    #     return redirect(url_for("showGraduate", university_id=university_id))
    if request.method == 'POST':
        if request.form['name']:
            graduate.name = request.form['name']
        if request.form['company']:
            graduate.company = request.form['company']
        if request.form['email']:
            graduate.email = request.form['email']
        if request.form['major']:
            graduate.major = request.form['major']
        if request.form['graduate_year']:
            graduate.graduate_year = request.form['graduate_year']
        session.add(graduate)
        session.commit()
        flash("Graduate profile has been edited!")
        return redirect(url_for('showGraduate', university_id=university_id))
    else:
        return render_template(
            'editGraduate.html',
            university_id=university_id,
            graduate_id=graduate_id,
            graduate=graduate)
    # return "Route 7: This page will be for editting  a graduate %s in
    # university %s!" % (graduate_id,university_id)

# delete a graduate


@app.route(
    '/university/<int:university_id>/graduate/<int:graduate_id>/delete/',
    methods=[
        'GET',
        'POST'])
# used the decorator function, replace the login check code.
@login_required
def deleteGraduate(university_id, graduate_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    university = session.query(University).filter_by(id=university_id).one()
    graduate = session.query(Graduate).filter_by(id=graduate_id).one()
    # if university.user_id!=login_session['user_id']:
    #     # return """<script> function myFunction()
    #     # {alert('Not allowed to delete this graduate.
    # Please create your own for edit.');}
    #     # </script>
    #     # <body onload='myFunction()'>
    #     # """
    #     flash("You are not allowed to delete graduate created by others!")
    #     return redirect(url_for("showGraduate", university_id=university_id))
    if request.method == 'POST':
        session.delete(graduate)
        session.commit()
        flash("Graduate profile has been deleted!")
        return redirect(url_for('showGraduate', university_id=university_id))
    else:
        return render_template('deleteGraduate.html', graduate=graduate)
    # return "Route 8: This page will be for deleting a graduate %s in
    # university %s!" % (graduate_id,university_id)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=9000)
