from dateutil import relativedelta
from datetime import date
import pickle

familyData_filename = "familyData.dat"


class Person:
    def __init__(self, id, name, DOB, gender, parentId):
        self.id: int = id
        self.name: str = name
        self.DOB: date = DOB
        self.gender: str = gender
        self.parentId: int = parentId

    def get_age(self):
        return relativedelta.relativedelta(date.today(), self.DOB).years


class Parent:
    def __init__(self, id, fatherId, motherId, DOM):
        self.id: int = id
        self.fatherId: int = fatherId
        self.motherId: int = motherId
        self.DOM: date = DOM

    def get_marriage_years(self):
        return relativedelta.relativedelta(date.today(), self.DOM).years


class Family:
    def __init__(self):
        self.persons = 0
        self.parents = 0
        self.personData: [Person] = []
        self.parentData: [Parent] = []

    def add_root(self):
        self.personData.append(Person(0, "ROOT", date.min, "", -1))
        self.parentData.append(Parent(0, 0, 0, date.min))

    def add_person(self, name, dob, gender, parentId):
        self.persons += 1
        self.personData.append(Person(self.persons, name, dob, gender, parentId))

    def add_parent(self, fatherId, motherId, dom):
        self.parents += 1
        self.parentData.append(Parent(self.parents, fatherId, motherId, dom))


def write_familyData(family):
    with open(familyData_filename, "wb") as familyFile:
        pickle.dump(family, familyFile)


def load_familyData():
    with open(familyData_filename, "rb") as familyFile:
        return pickle.load(familyFile)
