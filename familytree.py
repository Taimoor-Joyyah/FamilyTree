from dateutil import relativedelta
from datetime import date
import networkx as nx
import pickle

familyData_filename = "familyData.dat"
fig_filename = "fig.png"


class Person:
    def __init__(self, ID, name, DOB, gender, parentId):
        self.id: int = ID
        self.name: str = name
        self.DOB: date = DOB
        self.gender: int = gender  # 0 - Male, 1 - Female
        self.parentId: int = parentId
        self.familyId: int = -1

    def __str__(self):
        return self.name

    def get_age(self):
        return relativedelta.relativedelta(date.today(), self.DOB).years


class Parent:
    def __init__(self, ID, fatherId, motherId, DOM, rootLevel):
        self.id: int = ID
        self.fatherId: int = fatherId
        self.motherId: int = motherId
        self.DOM: date = DOM
        self.children: int = 0
        self.rootLevel = rootLevel

    def get_marriage_years(self):
        return relativedelta.relativedelta(date.today(), self.DOM).years


class FamilyData:
    def __init__(self):
        self.persons = 0
        self.parents = 0
        self.personData: [Person] = []
        self.parentData: [Parent] = []

    def add_root(self):
        self.personData.append(Person(0, "ROOT", date.min, 0, -1))
        self.parentData.append(Parent(0, 0, 0, date.min, 0))

    def add_person(self, name, dob, gender, parentId):
        self.persons += 1
        self.personData.append(Person(self.persons, name, dob, gender, parentId))
        self.parentById(parentId).children += 1

    def add_parent(self, fatherId, motherId, dom):
        self.parents += 1

        fatherRL = self.parentById(self.personById(fatherId).parentId).rootLevel
        motherRL = self.parentById(self.personById(motherId).parentId).rootLevel
        rootLevel = (fatherRL if fatherRL > motherRL else motherRL) + 1

        self.parentData.append(Parent(self.parents, fatherId, motherId, dom, rootLevel))

        self.personById(fatherId).familyId = self.parents
        self.personById(motherId).familyId = self.parents

    def personById(self, personId) -> Person:
        for person in self.personData:
            if person.id == personId:
                return person

    def parentById(self, parentId) -> Parent:
        for parent in self.parentData:
            if parent.id == parentId:
                return parent


def write_familyData(family):
    with open(familyData_filename, "wb") as familyFile:
        pickle.dump(family, familyFile)


def load_familyData():
    with open(familyData_filename, "rb") as familyFile:
        return pickle.load(familyFile)


class Family:
    def __init__(self, parent, family: FamilyData):
        self.father: Person = FamilyData.personById(family, parent.fatherId)
        self.mother: Person = FamilyData.personById(family, parent.motherId)
        self.children: [Person] = []
        self.rootLevel: int = parent.rootLevel
        self.familyId: int = parent.id

        for person in family.personData:
            if person.parentId == parent.id:
                self.children.append(person)

    def __str__(self):
        return f"Family {self.familyId}"


class FamilyTree:
    def __init__(self, family: FamilyData):
        self.families: [Family] = []

        for parent in family.parentData:
            self.families.append(Family(parent, family))

        self.families.sort(key=lambda x: x.rootLevel)


class Tree:
    def __init__(self, families: [Family]):
        edgeList = []
        for family in families:
            for child in family.children:
                edgeList.append([family, child])
            edgeList.append([family.father, family])
            edgeList.append([family.mother, family])

        graph = nx.DiGraph()
        graph.clear()
        graph.add_edges_from(edgeList)
        pos = nx.spring_layout(graph, k=1)

        nx.draw_networkx_edges(graph, pos, alpha=0.4, min_target_margin=5, min_source_margin=5)
        nx.draw_networkx_nodes(graph, pos, edgecolors='b', node_size=20, node_color="r")
        nx.draw_networkx_labels(graph, pos, font_size=8, verticalalignment="bottom")
