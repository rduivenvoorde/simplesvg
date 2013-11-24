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

import platform

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from Ui_MapSizer import Ui_MapSizer

# create the dialog for SimpleSvg
class MapSizerDialog(QDialog):

    MSG_BOX_TITLE = "QGis"
    LINUX_OFFSET = 0
    WINDOWS_OFFSET = 4

    def __init__(self, parent, mapCanvas):
        QDialog.__init__(self)
        # Set up the user interface from Designer. 
        self.ui = Ui_MapSizer()
        self.ui.setupUi(self)
        self.parent = parent
        self.mapCanvas = mapCanvas
        # on diffent OS's there seems to be different offsets to be taken into account
        self.offset = 0
        if platform.system() == "Linux":
            self.offset=self.LINUX_OFFSET
        elif platform.system() == "Windows":
            self.offset=self.WINDOWS_OFFSET
        self.ui.spinBoxImageWidth.setValue(self.mapCanvas.width()-self.offset)
        self.ui.spinBoxImageHeight.setValue(self.mapCanvas.height()-self.offset)
        extent = self.mapCanvas.extent()
        self.ui.txtMinX.setText('%.6f'%(extent.xMinimum()))
        self.ui.txtMinY.setText('%.6f'%(extent.yMinimum()))
        self.ui.txtMaxX.setText('%.6f'%(extent.xMaximum()))
        self.ui.txtMaxY.setText('%.6f'%(extent.yMaximum()))

        QObject.connect(self.mapCanvas, SIGNAL("renderComplete(QPainter *)"), self.mapCanvasResize)

    @pyqtSignature("on_btnSetImageSize_clicked()")
    def on_btnSetImageSize_clicked(self):
        self.setMapCanvasSize(self.ui.spinBoxImageWidth.value(), self.ui.spinBoxImageHeight.value())

    @pyqtSignature("on_btnSetExtent_clicked()")
    def on_btnSetExtent_clicked(self):
        self.setMapCanvasExtent()

    def on_buttonBox_accepted(self):
        # not very generic, but we want the SimpleSvgDialog back...
        self.hide()
        self.parent.show()

    def on_buttonBox_rejected(self):
        # not very generic, but we want the SimpleSvgDialog back...
        self.hide()
        self.parent.show()

    def setMapCanvasExtent(self):
        #print 'SET EXTENT'
        self.mapCanvas.setExtent(QgsRectangle(float(self.ui.txtMinX.text()), float(self.ui.txtMinY.text()), float(self.ui.txtMaxX.text()), float(self.ui.txtMaxY.text())))
        self.mapCanvas.refresh()

    def mapCanvasResize(self):
        self.ui.spinBoxImageWidth.setValue(self.mapCanvas.width()-self.offset)
        self.ui.spinBoxImageHeight.setValue(self.mapCanvas.height()-self.offset)
        extent = self.mapCanvas.extent()
        self.ui.txtMinX.setText('%.6f'%(extent.xMinimum()))
        self.ui.txtMinY.setText('%.6f'%(extent.yMinimum()))
        self.ui.txtMaxX.setText('%.6f'%(extent.xMaximum()))
        self.ui.txtMaxY.setText('%.6f'%(extent.yMaximum()))

    def setMapCanvasSize(self, newWidth, newHeight):
        if QGis.QGIS_VERSION_INT < 10900:
            # on QGIS 1.8 the parent of mapCanvas == QMainWindow
            parent=self.mapCanvas.parentWidget()
        else:
            # on QGIS>2.0 there is another widget in between
            parent=self.mapCanvas.parentWidget().parentWidget()
        mapCanvas=self.mapCanvas
        # some QT magic for me, coming from maximized force a minimal layout change first
        if(parent.isMaximized()):
            QMessageBox.warning(parent, self.MSG_BOX_TITLE, ("Maximized QGIS window..\n" "QGIS window is maximized, plugin will try to de-maximize the window.\n" "If image size is still not exact what you asked for,\ntry starting plugin with non maximized window."), QMessageBox.Ok, QMessageBox.Ok)
            parent.showNormal()
        newWidth=newWidth+self.offset
        newHeight=newHeight+self.offset
        diffWidth=mapCanvas.size().width()-newWidth
        diffHeight=mapCanvas.size().height()-newHeight
        mapCanvas.resize(newWidth, newHeight)
        parent.resize(parent.size().width()-diffWidth, parent.size().height()-diffHeight)
        # HACK: there are cases where after maximizing and here demaximizing the size of the parent is not
        # in sync with the actual size, giving a small error in the size setting
        # we do the resizing again, this fixes this small error then ....
        if newWidth <> mapCanvas.size().width() or newHeight <> mapCanvas.size().height():
            diffWidth=mapCanvas.size().width()-newWidth
            diffHeight=mapCanvas.size().height()-newHeight
            mapCanvas.resize(newWidth, newHeight)
            parent.resize(parent.size().width()-diffWidth, parent.size().height()-diffHeight)


