from pathlib import Path
import sys

from PyQt6.QtWidgets import *
from PyQt6.uic import load_ui
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from familytree import *


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

    saveDataButton: QPushButton
    treeGraphButton: QPushButton
    saveTreeButton: QPushButton

    def __init__(self, uiFile):
        super().__init__()
        load_ui.loadUi(uiFile, self)
        self.treeWindow = QMainWindow()
        self.treeWindow.setWindowTitle("Tree Graph")
        self.initialize()

    @staticmethod
    def personTableFill(tableWidget: QTableWidget, persons: [Person]):
        tableWidget.setRowCount(len(persons))
        for index, person in enumerate(persons):
            tableWidget.setItem(index, 0, QTableWidgetItem(str(person.id)))
            tableWidget.setItem(index, 1, QTableWidgetItem(person.name))
            if index != 0:
                tableWidget.setItem(index, 2, QTableWidgetItem(person.DOB.strftime("%d-%m-%Y")))
                tableWidget.setItem(index, 3, QTableWidgetItem("Male" if person.gender == 0 else "Female"))
                tableWidget.setItem(index, 4, QTableWidgetItem(str(person.parentId)))

    @staticmethod
    def parentTableFill(tableWidget: QTableWidget, parents: [Parent]):
        tableWidget.setRowCount(len(parents))
        for index, parent in enumerate(parents):
            tableWidget.setItem(index, 0, QTableWidgetItem(str(parent.id)))
            tableWidget.setItem(index, 1, QTableWidgetItem(str(parent.fatherId)))
            tableWidget.setItem(index, 2, QTableWidgetItem(str(parent.motherId)))
            if index != 0:
                tableWidget.setItem(index, 3, QTableWidgetItem(parent.DOM.strftime("%d-%m-%Y")))

    def refreshTable(self, Object):
        if Object is Person:
            self.personTableFill(self.personTableWidget, family.personData)
        elif Object is Parent:
            self.parentTableFill(self.parentTableWidget, family.parentData)

    def clearWarning(self):
        self.personMsg.clear()
        self.parentMsg.clear()

    def initialize(self):
        self.refreshTable(Person)
        self.refreshTable(Parent)

        self.personAddButton.clicked.connect(self.personAdd)
        self.personRemoveButton.clicked.connect(self.personRemove)
        self.personUpdateButton.clicked.connect(self.personUpdate)
        self.parentAddButton.clicked.connect(self.parentAdd)
        self.parentRemoveButton.clicked.connect(self.parentRemove)
        self.parentUpdateButton.clicked.connect(self.parentUpdate)
        self.saveDataButton.clicked.connect(self.saveData)
        self.treeGraphButton.clicked.connect(self.treeGraph)
        self.saveTreeButton.clicked.connect(self.saveTree)

        self.treeWindow.setCentralWidget(FigureCanvasQTAgg(plt.figure()))

    def tableRemoveItems(self, tableWidget: QTableWidget, Objects: [object]):
        for Range in tableWidget.selectedRanges():
            for i in range(Range.topRow(), Range.bottomRow() + 1):
                obj = Objects[i]
                if type(obj) is Person:
                    if obj.id == 0:
                        self.personMsg.setText("ROOT Person cannot be removed.")
                        return
                    if obj.familyId != -1:
                        self.personMsg.setText(f"{obj.name} cannot be removed, it should not be parent.")
                        return
                    else:
                        FamilyData.parentById(family, obj.parentId).children -= 1
                        Objects.pop(i)
                elif type(obj) is Parent:
                    if obj.id == 0:
                        self.parentMsg.setText("ROOT Parent cannot be removed.")
                        return
                    if obj.children != 0:
                        self.parentMsg.setText(f"Parent(id={obj.id}) cannot be removed, it should not have children.")
                        return
                    else:
                        FamilyData.personById(family, obj.fatherId).familyId = -1
                        FamilyData.personById(family, obj.motherId).familyId = -1
                        Objects.pop(i)

    def personFieldValid(self):
        name = self.nameLineEdit.text()
        parentId = self.parentIDLineEdit.text()
        if not name or not parentId:
            msg = "Empty Field(s) Found."
        elif len(name) < 3:
            msg = "Name must be 3 or more character."
        elif not parentId.isnumeric():
            msg = "Parent ID must be numeric."
        elif not FamilyData.parentById(family, int(parentId)):
            msg = "Parent ID does not exist."
        else:
            return True
        self.personMsg.setText(msg)
        return False

    def personAdd(self):
        self.clearWarning()
        if not self.personFieldValid():
            return
        family.add_person(self.nameLineEdit.text(), self.dOBEdit.date().toPyDate(),
                          0 if self.maleRadioButton.isChecked() else 1, int(self.parentIDLineEdit.text()))
        self.refreshTable(Person)
        self.clearPersonFields()

    def personRemove(self):
        self.clearWarning()
        if not self.personTableWidget.selectedRanges():
            self.personMsg.setText("No Person selected.")
            return
        self.tableRemoveItems(self.personTableWidget, family.personData)
        self.refreshTable(Person)

    def personUpdate(self):
        self.clearWarning()
        ranges = self.personTableWidget.selectedRanges()
        if not ranges:
            self.personMsg.setText("No Person selected.")
            return
        if not self.personFieldValid():
            return
        person = family.personData[ranges[0].topRow()]
        person.name = self.nameLineEdit.text()
        person.DOB = self.dOBEdit.date().toPyDate()
        person.gender = 0 if self.maleRadioButton.isChecked() else 1
        person.parentId = int(self.parentIDLineEdit.text())
        self.refreshTable(Person)

    def parentFieldValid(self):
        fatherId = self.fatherIDLineEdit.text()
        motherId = self.motherIDLineEdit.text()
        if not fatherId or not motherId:
            self.parentMsg.setText("Empty Field(s) Found.")
            return False
        mother = FamilyData.personById(family, int(motherId))
        father = FamilyData.personById(family, int(fatherId))
        if not fatherId.isnumeric():
            msg = "Father ID must be numeric."
        elif not father:
            msg = "Father ID does not exist."
        elif father.gender != 0:
            msg = "Father ID person is not Male."
        elif not motherId.isnumeric():
            msg = "Mother ID must be numeric."
        elif not mother:
            msg = "Mother ID does not exist."
        elif mother.gender != 1:
            msg = "Mother ID person is not Female."
        else:
            return True
        self.parentMsg.setText(msg)
        return False

    def parentAdd(self):
        self.clearWarning()
        if not self.parentFieldValid():
            return
        family.add_parent(int(self.fatherIDLineEdit.text()),
                          int(self.motherIDLineEdit.text()), self.dOMEdit.date().toPyDate())
        self.refreshTable(Parent)
        self.clearParentFields()

    def parentRemove(self):
        self.clearWarning()
        if not self.parentTableWidget.selectedRanges():
            self.parentMsg.setText("No Parent selected.")
            return
        self.tableRemoveItems(self.parentTableWidget, family.parentData)
        self.refreshTable(Parent)

    def parentUpdate(self):
        self.clearWarning()
        ranges = self.parentTableWidget.selectedRanges()
        if not ranges:
            self.parentMsg.setText("No Parent selected.")
            return
        if not self.parentFieldValid():
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

    @staticmethod
    def updateTree():
        plt.clf()
        Tree(FamilyTree(family).families)

    def treeGraph(self):
        self.updateTree()
        self.treeWindow.show()

    def saveTree(self):
        self.updateTree()
        plt.savefig(fig_filename, dpi=500)

    @staticmethod
    def saveData():
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
