from flask import Flask
# code for SQLAlchemy and database engine in sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, University, Graduate

app = Flask(__name__)

engine = create_engine('sqlite:///alumni.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/university/<int:university_id>/graduate/JSON/')
def graduatesJSON(university_id):
    return 'Route 9: This is the JSON format information of all graduates in university %s!' %university_id

@app.route('/university/<int:university_id>/graduate/<int:graduate_id>/JSON/')
def graduateJSON(university_id,graduate_id):
    return 'Route 10: This is the JSON format information of one graduate %s in university %s!' %(graduate_id, university_id)


#show all universities
@app.route('/')
@app.route('/university/')
def showUniversity():
    return "Route 1: This page will show all my university in databases!"

#create new university
@app.route('/university/new/', methods=['GET', 'POST'])
def newUniversity():
    return "Route 2: This page will be for creating new university!"

#edit a university
@app.route('/university/<int:university_id>/edit/', methods=['GET', 'POST'])
def editUniversity(university_id):
    return "Route 3: This page will be for editting a university %s!" %university_id

#delete a university
@app.route('/university/<int:university_id>/delete/', methods=['GET', 'POST'])
def deleteUniversity(university_id):
    return "Route 4: This page will be for deleting a university %s!" %university_id

#show graduates in a university
@app.route('/university/<int:university_id>/')
@app.route('/university/<int:university_id>/graduate/')
def showGraduate(university_id):
    return "Route 5: This page will show graduates in  university %s!" %university_id

#add new graduate
@app.route('/university/<int:university_id>/graduate/new/', methods=['GET', 'POST'])
def newGraduate(university_id):
    return "Route 6: This page will be for add a new graduate in university %s!" %university_id

#edit a graduate
@app.route('/university/<int:university_id>/graduate/<int:graduate_id>/edit/', methods=['GET', 'POST'])
def editGraduate(university_id, graduate_id):
    return "Route 7: This page will be for editting  a graduate %s in university %s!" % (graduate_id,university_id)

#delete a graduate
@app.route('/university/<int:university_id>/graduate/<int:graduate_id>/delete/', methods=['GET', 'POST'])
def deleteGraduate(university_id, graduate_id):
    return "Route 8: This page will be for deleting a graduate %s in university %s!" % (graduate_id,university_id)





if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9000)
