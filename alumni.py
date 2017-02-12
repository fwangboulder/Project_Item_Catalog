#! /usr/bin/env python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import University, Base, Graduate

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


# Graduates for Stanford University
university1 = University(name="Stanford University")

session.add(university1)
session.commit()

graduate1 = Graduate(
    name="David Xu",
    major="Computer Science",
    company="Google",
    graduate_year="2010",
    university=university1)

session.add(graduate1)
session.commit()


graduate2 = Graduate(
    name="Tim Wang",
    major="Chemistry",
    company="Facebook",
    graduate_year="2008",
    university=university1)

session.add(graduate2)
session.commit()

graduate3 = Graduate(
    name="Will Zhao",
    major="Physics",
    company="LinkedIn",
    graduate_year="2003",
    university=university1)

session.add(graduate3)
session.commit()

graduate4 = Graduate(
    name="Will Qian",
    major="Physics",
    company="Amazon",
    graduate_year="2001",
    university=university1)

session.add(graduate4)
session.commit()

graduate5 = Graduate(
    name="Will Sun",
    major="Computer Science",
    company="Huawei",
    graduate_year="1998",
    university=university1)

session.add(graduate5)
session.commit()

# Graduates for Harvard University
university1 = University(name="Harvard University")

session.add(university1)
session.commit()

graduate1 = Graduate(
    name="David Xu",
    major="Computer Science",
    company="Google",
    graduate_year="2010",
    university=university1)

session.add(graduate1)
session.commit()


graduate2 = Graduate(
    name="Tim Wang",
    major="Chemistry",
    company="Facebook",
    graduate_year="2008",
    university=university1)

session.add(graduate2)
session.commit()

graduate3 = Graduate(
    name="Will Zhao",
    major="Physics",
    company="LinkedIn",
    graduate_year="2003",
    university=university1)

session.add(graduate3)
session.commit()

graduate4 = Graduate(
    name="Will Qian",
    major="Physics",
    company="Amazon",
    graduate_year="2001",
    university=university1)

session.add(graduate4)
session.commit()

graduate5 = Graduate(
    name="Will Sun",
    major="Computer Science",
    company="Huawei",
    graduate_year="1998",
    university=university1)

session.add(graduate5)
session.commit()

print "added graduates!"
