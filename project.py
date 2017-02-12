from flask import Flask, render_template,request,redirect,jsonify,url_for
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


    return "Route 4: This page will be for deleting a university %s!" %university_id

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
        return redirect(url_for('showGraduate',university_id=university_id))
    else:
        return render_template('deleteGraduate.html',graduate=graduate)
    #return "Route 8: This page will be for deleting a graduate %s in university %s!" % (graduate_id,university_id)





if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9000)
