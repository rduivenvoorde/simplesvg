# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_SimpleSvg.ui'
#
# Created: Tue Apr 15 21:33:34 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SimpleSvg(object):
    def setupUi(self, SimpleSvg):
        SimpleSvg.setObjectName(_fromUtf8("SimpleSvg"))
        SimpleSvg.resize(678, 530)
        self.gridLayout = QtGui.QGridLayout(SimpleSvg)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.txtHeading = QtGui.QLabel(SimpleSvg)
        self.txtHeading.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        font.setPointSize(24)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.txtHeading.setFont(font)
        self.txtHeading.setAlignment(QtCore.Qt.AlignCenter)
        self.txtHeading.setObjectName(_fromUtf8("txtHeading"))
        self.gridLayout.addWidget(self.txtHeading, 0, 2, 1, 2)
        self.btnResizeMap = QtGui.QPushButton(SimpleSvg)
        self.btnResizeMap.setObjectName(_fromUtf8("btnResizeMap"))
        self.gridLayout.addWidget(self.btnResizeMap, 2, 2, 1, 2)
        self.txtFileName = QtGui.QLineEdit(SimpleSvg)
        self.txtFileName.setText(_fromUtf8(""))
        self.txtFileName.setObjectName(_fromUtf8("txtFileName"))
        self.gridLayout.addWidget(self.txtFileName, 4, 2, 1, 1)
        self.btnBrowse = QtGui.QPushButton(SimpleSvg)
        self.btnBrowse.setObjectName(_fromUtf8("btnBrowse"))
        self.gridLayout.addWidget(self.btnBrowse, 4, 3, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(SimpleSvg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 4)
        self.label = QtGui.QLabel(SimpleSvg)
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/simplesvg/inkscape.png")))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 1, 5, 1)
        self.textEdit = QtGui.QTextEdit(SimpleSvg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.gridLayout.addWidget(self.textEdit, 1, 2, 1, 2)
        self.cbFeaturesInMapcanvasOnly = QtGui.QCheckBox(SimpleSvg)
        self.cbFeaturesInMapcanvasOnly.setChecked(True)
        self.cbFeaturesInMapcanvasOnly.setObjectName(_fromUtf8("cbFeaturesInMapcanvasOnly"))
        self.gridLayout.addWidget(self.cbFeaturesInMapcanvasOnly, 3, 2, 1, 1)

        self.retranslateUi(SimpleSvg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SimpleSvg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SimpleSvg.reject)
        QtCore.QMetaObject.connectSlotsByName(SimpleSvg)

    def retranslateUi(self, SimpleSvg):
        SimpleSvg.setWindowTitle(_translate("SimpleSvg", "SimpleSvg", None))
        self.txtHeading.setText(_translate("SimpleSvg", "SimpleSvg Plugin", None))
        self.btnResizeMap.setText(_translate("SimpleSvg", "Resize Map or Set Extent", None))
        self.btnBrowse.setText(_translate("SimpleSvg", "Browse", None))
        self.textEdit.setHtml(_translate("SimpleSvg", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Cantarell\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:600;\">SimpleSvg is a plugin which tries to save the current map as SVG.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:10pt;\">It tries to use plain svg, only adding some inkscape specific attributes to make it possible to use \'layers\' in inkscape, and grouping svg-elements in a \'QGIS\'-way: </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:10pt;\">that is a layer in one group, and every class of a classification in it\'s own group.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:10pt;\">Labels and Id\'s within a layer have same name as in QGIS making it possible to select all elements within a class or group or element later in InkScape</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:10pt;\">For rasters it will take a screenshot of the layer and make an image-element with an external link to the screenshot.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:10pt;\">For lines and polygons it tries to save both pen and symbol style.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:10pt;\">For Points it can only save a point as a small colored circle. </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:10pt;\">Note: plugin uses screen (pixel) coordinates for svg coordinates. Default to ONLY use the objects that are in current map window. Uncheck checkbox below to have ALL your vector objects (at current scale). NOT working for raster data.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:10pt;\">WARNING: this will retrieve ALL objects from your vector data providers!</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:10pt;\">Please sent further ideas and requests to </span><span style=\" font-family:\'Sans Serif\'; font-size:10pt; font-style:italic;\">Richard Duivenvoorde:  richard@duif.net</span></p></body></html>", None))
        self.cbFeaturesInMapcanvasOnly.setText(_translate("SimpleSvg", "Only features in current mapview (uncheck to have ALL)", None))

import resources_rc
