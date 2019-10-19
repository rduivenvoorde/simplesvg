"""
/***************************************************************************
SimpleSvg
A QGIS plugin
Create simple SVG from current view, editable with InkScape
                             -------------------
begin                : 2011-06-16
copyright            : (C) 2011 by Richard Duivenvoorde
email                : richard@duif.net 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""


from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import QDialog, QFileDialog

from .Ui_SimpleSvg import Ui_SimpleSvg
from .mapsizer.MapSizerDialog import MapSizerDialog

# create the dialog for SimpleSvg
class SimpleSvgDialog(QDialog):
  def __init__(self, iface): 
    QDialog.__init__(self) 
    # Set up the user interface from Designer. 
    self.ui = Ui_SimpleSvg ()
    self.ui.setupUi(self)
    # little dialog for sizing map
    self.sizer = MapSizerDialog(self, iface.mapCanvas())
    self.ui.btnBrowse.clicked.connect(self.btnBrowse_clicked)


  # see http://www.riverbankcomputing.com/Docs/PyQt4/pyqt4ref.html#connecting-signals-and-slots
  # without this magic, the on_btnOk_clicked will be called two times: one clicked() and one clicked(bool checked)
  #@pyqtSignature("on_btnBrowse_clicked()")
  @pyqtSlot()
  def btnBrowse_clicked(self):
    fileName = QSettings().value('/simplesvg/lastfile')  # already unicode
    fileName, filter = QFileDialog.getSaveFileName(self, "Save as svg file", fileName, '')
    # TODO do some checks to be sure there is no extension
    self.ui.txtFileName.setText(fileName)

  #@pyqtSignature("on_btnResizeMap_clicked()")
  # show resize dialog (while hiding yourself, come back when resize dialog is closed
  def on_btnResizeMap_clicked(self):
    self.sizer.show()
    self.hide()

  def on_buttonBox_helpRequested(self):
    self.emit(SIGNAL("showHelp()") )

  def on_cbFeaturesInMapcanvasOnly_stateChanged(self):
    #print("CHANGE")
    self.emit(SIGNAL("cbFeaturesInMapcanvasOnlyChanged"), self.ui.cbFeaturesInMapcanvasOnly.isChecked())

  def getFilePath(self):
    return self.ui.txtFileName.text()

  def setFilePath(self, path):
    return self.ui.txtFileName.setText(path)

