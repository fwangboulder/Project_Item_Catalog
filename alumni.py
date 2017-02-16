#! /usr/bin/env python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import University, Base, Graduate, User

engine = create_engine('sqlite:///alumni.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
user1 = User(
    name="Fang Wang",
    email="fwangboulder@gmail.com",
    picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user1)
session.commit()
# Graduates for Stanford University
university1 = University(name="Stanford University", user=user1)

session.add(university1)
session.commit()

graduate1 = Graduate(
    name="David Xu",
    major="Computer Science",
    company="Google",
    graduate_year="2010",
    email='davidxu@gmail.com',
    university=university1,
    user=user1)

session.add(graduate1)
session.commit()


graduate2 = Graduate(
    name="Tim Wang",
    major="Chemistry",
    company="Facebook",
    graduate_year="2008",
    email='timwang@gmail.com',
    university=university1,
    user=user1)

session.add(graduate2)
session.commit()

graduate3 = Graduate(
    name="Will Zhao",
    major="Physics",
    company="LinkedIn",
    graduate_year="2003",
    email='willzhao@gmail.com',
    university=university1,
    user=user1)

session.add(graduate3)
session.commit()

graduate4 = Graduate(
    name="Will Qian",
    major="Physics",
    company="Amazon",
    graduate_year="2001",
    email='willqian@gmail.com',
    university=university1,
    user=user1)

session.add(graduate4)
session.commit()

graduate5 = Graduate(
    name="Will Sun",
    major="Computer Science",
    company="Huawei",
    graduate_year="1998",
    email='willsun@gmail.com',
    university=university1,
    user=user1)


session.add(graduate5)
session.commit()

# Graduates for Harvard University
university1 = University(name="Harvard University", user=user1)

session.add(university1)
session.commit()

graduate1 = Graduate(
    name="David Xu",
    major="Computer Science",
    company="Google",
    graduate_year="2010",
    email='david.xu@gmail.com',
    university=university1,
    user=user1)

session.add(graduate1)
session.commit()


graduate2 = Graduate(
    name="Tim Wang",
    major="Chemistry",
    company="Facebook",
    graduate_year="2008",
    email='tim.wang@gmail.com',
    university=university1,
    user=user1)

session.add(graduate2)
session.commit()

graduate3 = Graduate(
    name="Will Zhao",
    major="Physics",
    company="LinkedIn",
    graduate_year="2003",
    email='will.zhao@gmail.com',
    university=university1,
    user=user1)

session.add(graduate3)
session.commit()

graduate4 = Graduate(
    name="Will Qian",
    major="Physics",
    company="Amazon",
    graduate_year="2001",
    email='will.qian@gmail.com',
    university=university1,
    user=user1)

session.add(graduate4)
session.commit()

graduate5 = Graduate(
    name="Will Sun",
    major="Computer Science",
    company="Huawei",
    graduate_year="1998",
    email='will.sun@gmail.com',
    university=university1,
    user=user1)

session.add(graduate5)
session.commit()

print "added graduates!"
