# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_SimpleSvg.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SimpleSvg(object):
    def setupUi(self, SimpleSvg):
        SimpleSvg.setObjectName("SimpleSvg")
        SimpleSvg.resize(695, 533)
        self.gridLayout = QtWidgets.QGridLayout(SimpleSvg)
        self.gridLayout.setObjectName("gridLayout")
        self.txtHeading = QtWidgets.QLabel(SimpleSvg)
        self.txtHeading.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        font.setPointSize(24)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.txtHeading.setFont(font)
        self.txtHeading.setAlignment(QtCore.Qt.AlignCenter)
        self.txtHeading.setObjectName("txtHeading")
        self.gridLayout.addWidget(self.txtHeading, 0, 2, 1, 2)
        self.btnResizeMap = QtWidgets.QPushButton(SimpleSvg)
        self.btnResizeMap.setObjectName("btnResizeMap")
        self.gridLayout.addWidget(self.btnResizeMap, 2, 2, 1, 2)
        self.txtFileName = QtWidgets.QLineEdit(SimpleSvg)
        self.txtFileName.setText("")
        self.txtFileName.setObjectName("txtFileName")
        self.gridLayout.addWidget(self.txtFileName, 4, 2, 1, 1)
        self.btnBrowse = QtWidgets.QPushButton(SimpleSvg)
        self.btnBrowse.setObjectName("btnBrowse")
        self.gridLayout.addWidget(self.btnBrowse, 4, 3, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(SimpleSvg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Help|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 4)
        self.label = QtWidgets.QLabel(SimpleSvg)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/plugins/simplesvg/inkscape.png"))
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 5, 1)
        self.textEdit = QtWidgets.QTextEdit(SimpleSvg)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 1, 2, 1, 2)
        self.cbFeaturesInMapcanvasOnly = QtWidgets.QCheckBox(SimpleSvg)
        self.cbFeaturesInMapcanvasOnly.setChecked(True)
        self.cbFeaturesInMapcanvasOnly.setObjectName("cbFeaturesInMapcanvasOnly")
        self.gridLayout.addWidget(self.cbFeaturesInMapcanvasOnly, 3, 2, 1, 1)

        self.retranslateUi(SimpleSvg)
        self.buttonBox.accepted.connect(SimpleSvg.accept)
        self.buttonBox.rejected.connect(SimpleSvg.reject)
        QtCore.QMetaObject.connectSlotsByName(SimpleSvg)

    def retranslateUi(self, SimpleSvg):
        _translate = QtCore.QCoreApplication.translate
        SimpleSvg.setWindowTitle(_translate("SimpleSvg", "SimpleSvg"))
        self.txtHeading.setText(_translate("SimpleSvg", "SimpleSvg Plugin"))
        self.btnResizeMap.setText(_translate("SimpleSvg", "Resize Map or Set Extent"))
        self.btnBrowse.setText(_translate("SimpleSvg", "Browse"))
        self.textEdit.setHtml(_translate("SimpleSvg", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Cantarell\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-weight:600;\">SimpleSvg is a plugin which tries to save the current map as SVG.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\';\">It tries to use plain svg, only adding some inkscape specific attributes to make it possible to use \'layers\' in inkscape, and grouping svg-elements in a \'QGIS\'-way: </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\';\">that is a layer in one group, and every class of a classification in it\'s own group.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\';\">Labels and Id\'s within a layer have same name as in QGIS making it possible to select all elements within a class or group or element later in InkScape</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\';\">For rasters it will take a screenshot of the layer and make an image-element with an external link to the screenshot.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\';\">For lines and polygons it tries to save both pen and symbol style.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\';\">For Points it can only save a point as a small colored circle. </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\';\">Note: plugin uses screen (pixel) coordinates for svg coordinates. Default to ONLY use the objects that are in current map window. Uncheck checkbox below to have ALL your vector objects (at current scale). NOT working for raster data.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\';\">WARNING: this will retrieve ALL objects from your vector data providers!</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\';\">Please sent further ideas and requests to </span><span style=\" font-family:\'Sans Serif\'; font-style:italic;\">Richard Duivenvoorde:  richard@duif.net</span></p></body></html>"))
        self.cbFeaturesInMapcanvasOnly.setText(_translate("SimpleSvg", "Only features in current mapview (uncheck to have ALL)"))

from .resources import *
