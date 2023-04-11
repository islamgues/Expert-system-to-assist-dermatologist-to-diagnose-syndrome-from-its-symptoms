from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QListWidgetItem, QDesktopWidget
from pyke import knowledge_engine, goal

import time

# Compile and load .krb files in same directory that I'm in (recursively).
engine = knowledge_engine.engine(__file__)

allSymptoms1 = goal.compile('knowledge.disease_symptom($_disease, $sym1,symptom,disease)')
symptomsNumber = goal.compile('knowledge.disease_sym_number($disease, $symNumber)')
symptompsForAsking = goal.compile('knowledge.disease_symptom($disease, $sym1,symptom,disease)')
fc_goal = goal.compile('knowledge.how_related($disease, $symptom, $relationship)')

symptomsList = []  # for adding symptoms to interface list
diseaseList = []  # used for comparison
diseasesResult = []  # used to show found diseases
diseasesResultWihAccuracy = []
symptompsForAskingList = []


# interface code

class Ui_diagnosisWindow(object):
    def setupUi(self, diagnosisWindow):

        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)

        screen = QDesktopWidget().screenGeometry()
        screenHeight = screen.height()
        screenWidth = screen.width()
        print("Screen size:", screen.width(), "x", screen.height())

        diagnosisWindow.setObjectName("diagnosisWindow")
        diagnosisWindow.resize(int(screenWidth * 98 / 100), int(screenHeight * 90 / 100))
        diagnosisWindow.setWhatsThis("")
        diagnosisWindow.setStyleSheet("background-image:url(resources/background.jpg)")
        diagnosisWindow.setWindowIcon(QIcon("resources/icon.png"))

        self.centralwidget = QtWidgets.QWidget(diagnosisWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.diagnoseButton = QtWidgets.QPushButton(self.centralwidget)
        self.diagnoseButton.setGeometry(
            QtCore.QRect(int(screenWidth * 78 / 100), int(screenHeight * 55 / 100), int(screenWidth * 10 / 100),
                         int(screenHeight * 7 / 100)))
        self.diagnoseButton.setObjectName("diagnoseButton")
        self.diagnoseButton.clicked.connect(self.diagnoseButtonclick)
        self.diagnoseButton.setStyleSheet("border-radius: 10px;border:3px solid black;")
        # self.diagnoseButton.setStyleSheet("QPushButton:hover { background-color:blue; border: 3px solid #c2c2c2;};border-radius: 10px;border:3px solid black;")
        self.diagnoseButton.setFont(font)
        self.diagnoseButton.setStyleSheet("""
            #diagnoseButton {
                border: 3px solid black;
                border-radius: 5px;
                color: white;
                font-weight: bold;
            }
            #diagnoseButton:hover {
                background-color: green;
                border: 3px solid green;
                border-radius:15px;
            }
            """)

        self.clearButton = QtWidgets.QPushButton(self.centralwidget)
        self.clearButton.setGeometry(
            QtCore.QRect(int(screenWidth * 62 / 100), int(screenHeight * 55 / 100), int(screenWidth * 10 / 100),
                         int(screenHeight * 7 / 100)))
        self.clearButton.setObjectName("clearButton")
        self.clearButton.clicked.connect(self.clearButtonClick)
        self.clearButton.setStyleSheet("""
                    #clearButton {
                        border: 3px solid black;
                        border-radius: 5px;
                        color: white;
                        font-weight: bold;
                    }
                    #clearButton:hover {
                        background-color: green;
                        border-radius:15px;
                        transition: background-color 0.5s ease-out;
                        border: 3px solid red;

                    }
                    """)
        self.clearButton.setFont(font)

        self.yesButton = QtWidgets.QPushButton(self.centralwidget)
        self.yesButton.setGeometry(
            QtCore.QRect(int(screenWidth * 62 / 100), int(screenHeight * 80 / 100), int(screenWidth * 10 / 100),
                         int(screenHeight * 7 / 100)))
        self.yesButton.setObjectName("yesButton")
        self.yesButton.clicked.connect(self.yesButtonClick)
        #self.yesButton.setStyleSheet("border-radius: 10px;border:3px solid black;")
        self.yesButton.setFont(font)
        self.yesButton.setStyleSheet("""
            #yesButton {
                border: 3px solid black;
                border-radius: 10px;
                color: white;
                font-weight: bold;
            }
            #yesButton:hover {
                background-color: green;
                border: 3px solid green;
                border-radius:15px;
            }
            """)

        self.noButton = QtWidgets.QPushButton(self.centralwidget)
        self.noButton.setGeometry(
            QtCore.QRect(int(screenWidth * 78 / 100), int(screenHeight * 80 / 100), int(screenWidth * 10 / 100),
                         int(screenHeight * 7 / 100)))
        self.noButton.setObjectName("noButton")
        self.noButton.clicked.connect(self.noButtonClick)
        #self.noButton.setStyleSheet("border-radius: 10px;border:3px solid black;")
        self.noButton.setFont(font)
        self.noButton.setStyleSheet("""
                    #noButton {
                        border: 3px solid black;
                        border-radius: 10px;
                        color: white;
                        font-weight: bold;
                    }
                    #noButton:hover {
                        background-color: green;
                        border: 3px solid red;
                        border-radius:15px;
                    }
                    """)

        self.interfaceQuestions = QtWidgets.QTextEdit(self.centralwidget)
        self.interfaceQuestions.setGeometry(
            QtCore.QRect(int(screenWidth * 53 / 100), int(screenHeight * 70 / 100), int(screenWidth * 42 / 100),
                         int(screenHeight * 7 / 100)))
        self.interfaceQuestions.setObjectName("interfaceQuestions")
        # self.noButton.clicked.connect(self.noButtonClick)
        self.interfaceQuestions.setStyleSheet("border-radius: 10px;border:3px solid black;")
        self.interfaceQuestions.setFont(font)

        self.interfaceSymptomsList = QtWidgets.QListWidget(self.centralwidget)
        self.interfaceSymptomsList.setGeometry(
            QtCore.QRect(int(screenWidth * 5 / 100), int(screenHeight * 9 / 100), int(screenWidth * 42 / 100),
                         int(screenHeight * 51 / 100)))
        self.interfaceSymptomsList.setFont(font)
        self.interfaceSymptomsList.setObjectName("interfaceSymptomsList")
        self.interfaceSymptomsList.itemClicked.connect(self.OnClickSymptomItem)
        self.interfaceSymptomsList.setStyleSheet("border-radius: 10px;border:3px solid black;")

        # list selected symptoms
        self.interfaceSelectedSymptomsList = QtWidgets.QListWidget(self.centralwidget)
        self.interfaceSelectedSymptomsList.setGeometry(
            QtCore.QRect(int(screenWidth * 53 / 100), int(screenHeight * 1 / 100), int(screenWidth * 42 / 100),
                         int(screenHeight * 51 / 100)))
        self.interfaceSelectedSymptomsList.setFont(font)
        self.interfaceSelectedSymptomsList.setObjectName("interfaceSelectedSymptomsList")
        self.interfaceSelectedSymptomsList.setMinimumWidth(self.interfaceSelectedSymptomsList.sizeHintForColumn(50))
        self.interfaceSelectedSymptomsList.itemClicked.connect(self.onClickSelectedSymptomsItem)
        self.interfaceSelectedSymptomsList.setStyleSheet("border-radius: 10px;border:3px solid black;")

        self.interfaceDiagnosisResultList = QtWidgets.QListWidget(self.centralwidget)
        self.interfaceDiagnosisResultList.setGeometry(
            QtCore.QRect(int(screenWidth * 5 / 100), int(screenHeight * 62 / 100), int(screenWidth * 42 / 100),
                         int(screenHeight * 26 / 100)))
        self.interfaceDiagnosisResultList.setFont(font)
        self.interfaceDiagnosisResultList.setObjectName("interfaceDiagnosisResultList ")
        self.interfaceDiagnosisResultList.setMinimumWidth(self.interfaceDiagnosisResultList.sizeHintForColumn(50))
        self.interfaceDiagnosisResultList.setStyleSheet("border-radius: 10px;border:3px solid black;")

        # add symptoms to list with checkboxes
        for sym in symptomsList:
            matching_items = self.interfaceSymptomsList.findItems(sym, QtCore.Qt.MatchExactly)
            if not matching_items:
                symItem = QtWidgets.QListWidgetItem(sym, self.interfaceSymptomsList)
                symItem.setFlags(symItem.flags() | Qt.ItemIsUserCheckable)
                symItem.setCheckState(Qt.Unchecked)

        # self.interfaceSymptomsList.itemChanged.connect(self.OnClickSymptomItem)

        self.Searchbar = QtWidgets.QLineEdit(self.centralwidget)
        self.Searchbar.setFont(font)
        self.Searchbar.setGeometry(
            QtCore.QRect(int(screenWidth * 5 / 100), int(screenHeight * 1 / 100), int(screenWidth * 42 / 100),
                         int(screenHeight * 6 / 100)))
        self.Searchbar.setWhatsThis("")
        self.Searchbar.setObjectName("SearchBar")
        self.Searchbar.setPlaceholderText("Search...")
        self.Searchbar.textChanged.connect(self.filter_list)
        self.Searchbar.setStyleSheet("border-radius: 10px;border:3px solid black;")

        diagnosisWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(diagnosisWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 894, 22))
        self.menubar.setObjectName("menubar")
        diagnosisWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(diagnosisWindow)
        self.statusbar.setObjectName("statusbar")
        diagnosisWindow.setStatusBar(self.statusbar)

        self.retranslateUi(diagnosisWindow)
        QtCore.QMetaObject.connectSlotsByName(diagnosisWindow)

    def filter_list(self, text):
        # filter the items in the QListWidget based on the user input
        for i in range(self.interfaceSymptomsList.count()):
            item = self.interfaceSymptomsList.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def OnClickSymptomItem(self, seletedItem):

        matching_items = self.interfaceSelectedSymptomsList.findItems(seletedItem.text(), QtCore.Qt.MatchContains)

        if len(matching_items) != 0:
            for matching_item in matching_items:
                self.interfaceSelectedSymptomsList.takeItem(self.interfaceSelectedSymptomsList.row(matching_item))
            seletedItem.setCheckState(Qt.Unchecked)

        else:

            symItem = QListWidgetItem(seletedItem.text(), self.interfaceSelectedSymptomsList)
            symItem.setFlags(symItem.flags() | Qt.ItemIsUserCheckable)
            symItem.setCheckState(Qt.Checked)
            seletedItem.setCheckState(Qt.Checked)

        matching_items.clear()

    def onClickSelectedSymptomsItem(self, item):
        self.interfaceSelectedSymptomsList.takeItem(self.interfaceSelectedSymptomsList.row(item))
        matching_items = self.interfaceSymptomsList.findItems(item.text(), QtCore.Qt.MatchContains)
        for matching_item in matching_items:
            matching_item.setCheckState(Qt.Unchecked)

    def diagnoseButtonclick(self):
        self.interfaceDiagnosisResultList.clear()
        diseasesResultWihAccuracy.clear()
        symptompsForAskingList.clear()

        for i in range(self.interfaceSelectedSymptomsList.count()):
            item = self.interfaceSelectedSymptomsList.item(i)
            fc_test(item.text())
        for dis in diseasesResult:
            with symptomsNumber.prove(engine, disease=dis) as gen3:
                for vars, plan in gen3:
                    accuracy = float(format(100 * diseaseList.count(dis) / int(vars['symNumber']), ".2f"))
                    diseasesResultWihAccuracy.append((dis, accuracy))

                    # print(100*diseaseList.count(dis)/int(vars['symNumber']))

        sortedDiseaseResult = sorted(diseasesResultWihAccuracy, key=lambda x: x[1], reverse=True)
        for item in sortedDiseaseResult:
            label = f"{item[0]} - {item[1]}%"
            self.interfaceDiagnosisResultList.addItem(label)

        # adding symptoms for making questions
        for dis in diseasesResultWihAccuracy:
            with symptompsForAsking.prove(engine, disease=dis[0]) as gen3:
                for vars, plan in gen3:
                    symptompsForAskingList.append(vars['sym1'])

        # select only the unchecked symptoms
        for indexOfCheckedDisease in range(self.interfaceSelectedSymptomsList.count()):
            if symptompsForAskingList.count(self.interfaceSelectedSymptomsList.item(indexOfCheckedDisease).text()) != 0:
                symptompsForAskingList.remove(self.interfaceSelectedSymptomsList.item(indexOfCheckedDisease).text())

        print(symptompsForAskingList)
        self.interfaceQuestions.setText(symptompsForAskingList[0])
        diseaseList.clear()  # to avoid repetation when calc accuracy
        diseasesResult.clear()
        self.diagnoseButton.setEnabled(False)

    def yesButtonClick(self):
        print()
        for symptom in symptomsList:
            print()

    def noButtonClick(self):
        print()

    def clearButtonClick(self):
        for i in range(self.interfaceSymptomsList.count()):
            self.interfaceSymptomsList.item(i).setCheckState(Qt.Unchecked)
        self.interfaceSelectedSymptomsList.clear()
        self.Searchbar.clear()
        self.interfaceDiagnosisResultList.clear()
        symptompsForAskingList.clear()
        self.diagnoseButton.setEnabled(True)
        self.interfaceQuestions.clear()

    def retranslateUi(self, diagnosisWindow):
        _translate = QtCore.QCoreApplication.translate
        diagnosisWindow.setWindowTitle(_translate("diagnosisWindow", "RareDiagnosis"))
        self.diagnoseButton.setText(_translate("diagnosisWindow", "Diagnose"))
        self.clearButton.setText(_translate("diagnosisWindow", "Clear"))
        self.yesButton.setText(_translate("diagnosisWindow", "Yes"))
        self.noButton.setText(_translate("diagnosisWindow", "No"))


# interface code end here


# adding symptoms to interface list

def addingSymptoms():
    with allSymptoms1.prove(engine) as gen1:
        for vars, plan in gen1:
            symptomsList.append(vars['sym1'])


def fc_test(symptom):
    '''
        This function runs the forward-chaining example (fc_example.krb).
    '''

    with fc_goal.prove(engine, symptom=symptom) as gen:
        for vars, plan in gen:
            diseaseList.append(vars['disease'])
            if diseasesResult.count(vars['disease']) == 0:
                diseasesResult.append(vars['disease'])


# main
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    # engine preparing begin
    engine.reset()  # Allows us to run tests multiple times.
    start_time = time.time()
    engine.activate('fc_example')  # Runs all applicable forward-chaining rules.
    fc_end_time = time.time()
    fc_time = fc_end_time - start_time
    # engine preparing end
    addingSymptoms()
    print(len(symptomsList))
    ui = Ui_diagnosisWindow()
    ui.setupUi(MainWindow)
    MainWindow.showMaximized()
    sys.exit(app.exec_())
