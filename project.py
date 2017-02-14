from flask import Flask, render_template,request,redirect,jsonify,url_for, flash
# code for SQLAlchemy and database engine in sessionmaker
from sqlalchemy import create_engine,asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, University, Graduate
##############################
#*****************************
#New Imports for Authentication And Authorization
from flask import session as login_session
import random, string

#*****************************
#Import for GConnect
#create a flow object form the clientssecrets JSON file,
#which stores your client ID, client secret and other OAuth 2.0 praameters
#if no such module: $ pip install --upgrade oauth2client
from oauth2client.client import flow_from_clientsecrets
#use FlowExchangeError method catch the error trying to exchange an
#authorization code for an access token.

from oauth2client.client import FlowExchangeError
import httplib2
#json module provides an API for converting in memory Python objects
#to a serialized representation
import json
#make_response method converts the return value from a function
#into a real response object that can be sent off to client
from flask import make_response
#requests is an Apache 2.0 licensed HTTP library
import requests
#**************************************************

app = Flask(__name__)

###################################
#Download JSON:https://console.developers.google.com/apis/credentials?project=restaurant-menu-app-158420
#Rename it to client_secrets.json
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "alumni app"
#####################################

engine = create_engine('sqlite:///alumni.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Create a state token to prevent request foregery
#Store it in the session for later validation
@app.route('/login')
def showLogin():
    state=''.join(random.choice(string.ascii_uppercase+string.digits) \
    for i in xrange(32))
    login_session['state']=state
    #return 'The current session state is %s' %login_session['state']
    #after create the login.html in templates, now render it
    return render_template('login.html', STATE=state)

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
    result = json.loads(h.request(url, 'GET')[1])
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
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
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

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# ##################################
# #Disconnect- revoke a current user's token and reset the login_session
# @app.route('/gdisconnect')
# def gdisconnect():
#     access_token = login_session.get['access_token']
#     print 'In gdisconnect access token is %s', access_token
#     print 'User name is: '
#     print login_session['username']
#     if access_token is None:
#         print 'Access Token is None'
#     	response = make_response(json.dumps('Current user not connected.'), 401)
#     	response.headers['Content-Type'] = 'application/json'
#     	return response
#     url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session.get['access_token']
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[0]
#     print 'result is '
#     print result
#     if result['status'] == '200':
#         del login_session['access_token']
#     	del login_session['gplus_id']
#     	del login_session['username']
#     	del login_session['email']
#     	del login_session['picture']
#     	response = make_response(json.dumps('Successfully disconnected.'), 200)
#     	response.headers['Content-Type'] = 'application/json'
#     	return response
#     else:
#
#     	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
#     	response.headers['Content-Type'] = 'application/json'
#     	return response
#
#
####################################
##################################
#Disconnect- revoke a current user's token and reset the login_session
@app.route('/gdisconnect')
def gdisconnect():
    #only disconnect a connected user.
    credentials= login_session.get('credentials')
    if credentials is None:
        response=make_response(json.dumps('Current user not connected.'),401)
        response.headers['Content-Type']='application/json'
        return response
    #Execute HTTP GET request to revoke current token.
    #access_token = login_session['access_token']
    access_token=credentials.access_token
    #print 'In gdisconnect access token is %s', access_token
    #print 'User name is: '
    #print login_session['username']
    #if access_token is None:
        #print 'Access Token is None'
    	#response = make_response(json.dumps('Current user not connected.'), 401)
    	#response.headers['Content-Type'] = 'application/json'
    	#return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    #print 'result is '
    #print result
    if result['status'] == '200':
        #reset the user's session
        #del login_session['access_token']
        del login_session['credentials']
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:
        #For whatever reason, the given token was invalid
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response


###################################
################################
#
# engine = create_engine('sqlite:///alumni.db')
# Base.metadata.bind = engine
#
# DBSession = sessionmaker(bind=engine)
# session = DBSession()
################################


################################


@app.route('/university/<int:university_id>/graduate/JSON/')
def graduatesJSON(university_id):
    university=session.query(University).filter_by(id=university_id).one()
    graduates=session.query(Graduate).filter_by(university_id=university_id).all()
    return jsonify(graduates=[i.serialize for i in graduates])

    #return 'Route 9: This is the JSON format information of all graduates in university %s!' %university_id

@app.route('/university/<int:university_id>/graduate/<int:graduate_id>/JSON/')
def graduateJSON(university_id,graduate_id):
    graduate=session.query(Graduate).filter_by(id=graduate_id).one()
    return jsonify(graduate=graduate.serialize)

    #return 'Route 10: This is the JSON format information of one graduate %s in university %s!' %(graduate_id, university_id)
@app.route('/university/JSON/')
def universityJSON():
    universities=session.query(University).all()
    return jsonify(universities=[i.serialize for i in universities])

    #return 'Route 11: This is the JSON format information all universities!'


#show all universities
@app.route('/')
@app.route('/university/')
def showUniversity():
    universities=session.query(University).all()
    return render_template('universities.html',universities=universities)
    #return "Route 1: This page will show all my university in databases!"

#create new university
@app.route('/university/new/', methods=['GET', 'POST'])
def newUniversity():

    if request.method=='POST':
        if request.form['name']:
            university=University(name=request.form['name'])
            session.add(university)
            session.commit()
        return redirect(url_for('showUniversity'))
    else:
        return render_template('newUniversity.html')
    #return "Route 2: This page will be for creating new university!"

#edit a university
@app.route('/university/<int:university_id>/edit/', methods=['GET', 'POST'])
def editUniversity(university_id):
    university=session.query(University).filter_by(id=university_id).one()
    print request.method
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
    #return "Route 3: This page will be for editting a university %s!" %university_id

#delete a university
@app.route('/university/<int:university_id>/delete/', methods=['GET', 'POST'])
def deleteUniversity(university_id):

    university=session.query(University).filter_by(id=university_id).one()
    if request.method=='POST':
        session.delete(university)
        session.commit()

        return redirect(url_for('showUniversity'))
    else:
        return render_template('deleteUniversity.html',university=university)


    #return "Route 4: This page will be for deleting a university %s!" %university_id

#show graduates in a university
@app.route('/university/<int:university_id>/')
@app.route('/university/<int:university_id>/graduate/')
def showGraduate(university_id):
    university=session.query(University).filter_by(id=university_id).one()
    graduates=session.query(Graduate).filter_by(university_id=university_id).all()
    return render_template('graduates.html',graduates=graduates,university=university)

    #return "Route 5: This page will show graduates in  university %s!" %university_id

#add new graduate
@app.route('/university/<int:university_id>/graduate/new/', methods=['GET', 'POST'])
def newGraduate(university_id):
    if request.method=='POST':
        graduate=Graduate(
            name=request.form['name'],
            company=request.form['company'],
            email=request.form['email'],
            major=request.form['major'],
            graduate_year=request.form['graduate_year'],
            university_id=university_id)
        session.add(graduate)
        session.commit()
        flash("new graduate profile created!")
        return redirect(url_for("showGraduate",university_id=university_id))
    else:
        return render_template('newGraduate.html',university_id=university_id)

    #return "Route 6: This page will be for add a new graduate in university %s!" %university_id

#edit a graduate
@app.route('/university/<int:university_id>/graduate/<int:graduate_id>/edit/', methods=['GET', 'POST'])
def editGraduate(university_id, graduate_id):
    graduate=session.query(Graduate).filter_by(id=graduate_id).one()
    if request.method=='POST':
        if request.form['name']:
            graduate.name=request.form['name']
        if request.form['company']:
            graduate.company=request.form['company']
        if request.form['email']:
            graduate.email=request.form['email']
        if request.form['major']:
            graduate.major=request.form['major']
        if request.form['graduate_year']:
            graduate.graduate_year=request.form['graduate_year']
        session.add(graduate)
        session.commit()
        flash("Graduate profile has been edited!")
        return redirect(url_for('showGraduate',university_id=university_id))
    else:
        return render_template('editGraduate.html',university_id=university_id,graduate_id=graduate_id,graduate=graduate)
    #return "Route 7: This page will be for editting  a graduate %s in university %s!" % (graduate_id,university_id)

#delete a graduate
@app.route('/university/<int:university_id>/graduate/<int:graduate_id>/delete/', methods=['GET', 'POST'])
def deleteGraduate(university_id, graduate_id):
    graduate=session.query(Graduate).filter_by(id=graduate_id).one()
    if request.method=='POST':
        session.delete(graduate)
        session.commit()
        flash("Graduate profile has been deleted!")
        return redirect(url_for('showGraduate',university_id=university_id))
    else:
        return render_template('deleteGraduate.html',graduate=graduate)
    #return "Route 8: This page will be for deleting a graduate %s in university %s!" % (graduate_id,university_id)





if __name__ == '__main__':
    app.secret_key='super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=9000)
