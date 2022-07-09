from pathlib import Path
import sys

from PyQt6.QtWidgets import *
from PyQt6.uic import load_ui

from familytree import *


class GraphTree(QWidget):
    pass


class Window(QMainWindow):
    personAddButton: QPushButton
    personRemoveButton: QPushButton
    personUpdateButton: QPushButton
    parentAddButton: QPushButton
    parentRemoveButton: QPushButton
    parentUpdateButton: QPushButton

    personMsg: QLabel
    parentMsg: QLabel

    personTableWidget: QTableWidget
    parentTableWidget: QTableWidget

    nameLineEdit: QLineEdit
    dOBEdit: QDateEdit
    maleRadioButton: QRadioButton
    femaleRadioButton: QRadioButton
    parentIDLineEdit: QLineEdit

    fatherIDLineEdit: QLineEdit
    motherIDLineEdit: QLineEdit
    dOMEdit: QDateEdit

    saveButton: QPushButton
    treeGraphButton: QPushButton

    def __init__(self, uiFile):
        super().__init__()
        load_ui.loadUi(uiFile, self)
        self.initialize()

    @staticmethod
    def personTableFill(tableWidget: QTableWidget, persons: [Person]):
        tableWidget.setRowCount(len(persons))
        for index, person in enumerate(persons):
            tableWidget.setItem(index, 0, QTableWidgetItem(str(person.id)))
            tableWidget.setItem(index, 1, QTableWidgetItem(person.name))
            tableWidget.setItem(index, 2, QTableWidgetItem(person.DOB.strftime("%d-%m-%Y")))
            tableWidget.setItem(index, 3, QTableWidgetItem(person.gender))
            tableWidget.setItem(index, 4, QTableWidgetItem(str(person.parentId)))

    @staticmethod
    def parentTableFill(tableWidget: QTableWidget, parents: [Parent]):
        tableWidget.setRowCount(len(parents))
        for index, parent in enumerate(parents):
            tableWidget.setItem(index, 0, QTableWidgetItem(str(parent.id)))
            tableWidget.setItem(index, 1, QTableWidgetItem(str(parent.fatherId)))
            tableWidget.setItem(index, 2, QTableWidgetItem(str(parent.motherId)))
            tableWidget.setItem(index, 3, QTableWidgetItem(parent.DOM.strftime("%d-%m-%Y")))

    def refreshTable(self, object):
        if object is Person:
            self.personTableFill(self.personTableWidget, family.personData)
        elif object is Parent:
            self.parentTableFill(self.parentTableWidget, family.parentData)

    def initialize(self):
        self.refreshTable(Person)
        self.refreshTable(Parent)

        self.personAddButton.clicked.connect(self.personAdd)
        self.personRemoveButton.clicked.connect(self.personRemove)
        self.personUpdateButton.clicked.connect(self.personUpdate)
        self.parentAddButton.clicked.connect(self.parentAdd)
        self.parentRemoveButton.clicked.connect(self.parentRemove)
        self.parentUpdateButton.clicked.connect(self.parentUpdate)
        self.saveButton.clicked.connect(self.save)
        self.treeGraphButton.clicked.connect(self.treeGraph)

    @staticmethod
    def tableRemoveItems(tableWidget: QTableWidget, Objects: [object]):
        for Range in tableWidget.selectedRanges():
            for i in range(Range.topRow(), Range.bottomRow() + 1):
                Objects.pop(i)

    def personFieldValid(self):
        if not self.nameLineEdit.text() or not self.parentIDLineEdit.text():
            self.personMsg.setText("Empty Field(s) Found.")
            return False
        if len(self.nameLineEdit.text()) < 3:
            self.personMsg.setText("Name must be 3 or more character.")
            return False
        if not self.parentIDLineEdit.text().isnumeric():
            self.personMsg.setText("Parent ID must be numeric.")
            return False
        return True

    def personAdd(self):
        if not self.personFieldValid():
            return
        family.add_person(self.nameLineEdit.text(), self.dOBEdit.date().toPyDate(),
                          0 if self.maleRadioButton.isChecked() else 1, int(self.parentIDLineEdit.text()))
        self.refreshTable(Person)
        self.clearPersonFields()

    def personRemove(self):
        if not self.personTableWidget.selectedRanges():
            return
        self.tableRemoveItems(self.personTableWidget, family.personData)
        self.refreshTable(Person)

    def personUpdate(self):
        if not self.personFieldValid():
            return
        ranges = self.personTableWidget.selectedRanges()
        if not ranges:
            return
        person = family.personData[ranges[0].topRow()]
        person.name = self.nameLineEdit.text()
        person.DOB = self.dOBEdit.date().toPyDate()
        person.gender = 0 if self.maleRadioButton.isChecked() else 1
        person.parentId = int(self.parentIDLineEdit.text())
        self.refreshTable(Person)

    def parentFieldValid(self):
        if not self.fatherIDLineEdit.text() or not self.motherIDLineEdit.text():
            self.parentMsg.setText("Empty Field(s) Found.")
            return False
        if not self.fatherIDLineEdit.text().isnumeric():
            self.parentMsg.setText("Father ID must be numeric.")
            return False
        if not self.motherIDLineEdit.text().isnumeric():
            self.parentMsg.setText("Father ID must be numeric.")
            return False
        return True

    def parentAdd(self):
        if not self.parentFieldValid():
            return
        family.add_parent(int(self.fatherIDLineEdit.text()),
                          int(self.motherIDLineEdit.text()), self.dOMEdit.date().toPyDate())
        self.refreshTable(Parent)
        self.clearParentFields()

    def parentRemove(self):
        if not self.parentTableWidget.selectedRanges():
            return
        self.tableRemoveItems(self.parentTableWidget, family.parentData)
        self.refreshTable(Parent)

    def parentUpdate(self):
        if not self.parentFieldValid():
            return
        ranges = self.parentTableWidget.selectedRanges()
        if not ranges:
            return
        parent = family.parentData[ranges[0].topRow()]
        parent.fatherId = int(self.fatherIDLineEdit.text())
        parent.motherId = int(self.motherIDLineEdit.text())
        parent.DOM = self.dOMEdit.date().toPyDate()
        self.refreshTable(Parent)

    def clearParentFields(self):
        self.fatherIDLineEdit.clear()
        self.motherIDLineEdit.clear()
        self.dOMEdit.setDate(date(2000, 1, 1))

    def clearPersonFields(self):
        self.nameLineEdit.clear()
        self.parentIDLineEdit.clear()
        self.dOBEdit.setDate(date(2000, 1, 1))
        self.maleRadioButton.setChecked(True)

    def treeGraph(self):
        pass

    @staticmethod
    def save():
        write_familyData(family)


if __name__ == "__main__":
    if not Path(familyData_filename).exists():
        family = FamilyData()
        family.add_root()
        write_familyData(family)

    family: FamilyData = load_familyData()

    app = QApplication(sys.argv)

    window = Window("main-window.ui")
    window.show()

    app.exit(app.exec())
