
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from imagemapplugingui import ImageMapPluginGui

# initialize Qt resources from file
import imagemapplugin_rc


class ImageMapPlugin:

  MSG_BOX_TITLE = "QGis Image Map Plugin"

  def __init__(self, iface):
    # save reference to the QGIS interface
    self.iface = iface
    self.filesPath = "/home/richard/temp/1"

  def initGui(self):
    # create action that will start plugin configuration
    self.action = QAction(QIcon(":/imagemapicon.xpm"), "Image Map", self.iface.mainWindow())
    self.action.setWhatsThis("Configuration for Image Map plugin")
    QObject.connect(self.action, SIGNAL("activated()"), self.run)
    # add toolbar button and menu item
    self.iface.addToolBarIcon(self.action)
    self.iface.addPluginToMenu("&Html Image Map Plugin", self.action)
    #self.iface.pluginMenu().insertAction(self.action)
    # connect to signal renderComplete which is emitted when canvas rendering is done
    QObject.connect(self.iface.mapCanvas(), SIGNAL("renderComplete(QPainter *)"), self.renderTest)

  def unload(self):
    # remove the plugin menu item and icon
    self.iface.removePluginMenu("&Html Image Map Plugin",self.action)
    self.iface.removeToolBarIcon(self.action)
    # disconnect form signal of the canvas
    QObject.disconnect(self.iface.mapCanvas(), SIGNAL("renderComplete(QPainter *)"), self.renderTest)

  def run(self):
    # check if current active layer is a polygon layer:
    layer =  self.iface.activeLayer()
    if layer == None:
        #print "Uhm, no active layer, make one polygon layer active"
        QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("No active layer found\n" "Please make one (multi)polygon or point layer active\n" "by choosing a layer in the legend"), QMessageBox.Ok, QMessageBox.Ok)
        return
    # don't know if this is possible / needed
    if not layer.isValid():
        #print "uhm, layer not valid, no active layer?"
        QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("No VALID layer found\n" "Please make one (multi)polygon or point layer active\n" "by choosing a layer in the legend"), QMessageBox.Ok, QMessageBox.Ok)
        return
    self.provider = layer.dataProvider()
    self.currentExtent = self.iface.mapCanvas().extent()
    if not(self.provider.geometryType() == QGis.WKBPolygon or self.provider.geometryType() == QGis.WKBMultiPolygon or self.provider.geometryType() == QGis.WKBPoint):
        print "Wrong geometrytype, only polygons (3) allowed, but is: %s" % self.provider.geometryType()
        QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("Wrong geometrytype, only (multi)polygons and points can be used.\n" "Please make one (multi)polygon or point layer active\n" "by choosing a layer in the legend"), QMessageBox.Ok, QMessageBox.Ok)
        return

    # we need the fields of the active layer to show in the attribute combobox in the gui:
    fields = self.provider.fields()
    attrFields = []
    for (i, field) in fields.iteritems():
      attrFields.append(field.name().trimmed())
    # construct gui (using these fields)
    flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
    # construct gui: if available reuse this one
    if hasattr(self, 'imageMapPlugin') == False:
        self.imageMapPluginGui = ImageMapPluginGui(self.iface.mainWindow(), flags)
    self.imageMapPluginGui.setAttributeFields(attrFields)
    self.layerAttr = attrFields
    self.selectedFeaturesOnly = False # default all features in current Extent
    # poging om een SIGNAL te vangen
    QObject.connect(self.imageMapPluginGui, SIGNAL("getFilesPath(QString)"), self.setFilesPath)
    QObject.connect(self.imageMapPluginGui, SIGNAL("onHrefAttributeSet(QString)"), self.onHrefAttributeFieldSet)
    QObject.connect(self.imageMapPluginGui, SIGNAL("onClickAttributeSet(QString)"), self.onClickAttributeFieldSet)
    QObject.connect(self.imageMapPluginGui, SIGNAL("onMouseOverAttributeSet(QString)"), self.onMouseOverAttributeFieldSet)
    QObject.connect(self.imageMapPluginGui, SIGNAL("getCbkBoxSelectedOnly(bool)"), self.setSelectedOnly)
    QObject.connect(self.imageMapPluginGui, SIGNAL("go(QString)"), self.go)
    # remember old path's in this session:
    self.imageMapPluginGui.setFilesPath(self.filesPath)
    self.imageMapPluginGui.show()

  def go(self, foo):
    filename = self.filesPath + ".svg"
    imgfilename = self.filesPath + ".png"
    # check if path is writable: ?? TODO
    #if not os.access(filename, os._OK):
    #  QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("Unable to write file with this name.\n" "Please choose a valid filename and a writable directory."))
    #  return
    # check if file(s) excist:
    if os.path.isfile(filename) or os.path.isfile(imgfilename):
        if QMessageBox.question(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("There is already a filename with this name.\n" "Continue?"), QMessageBox.Cancel, QMessageBox.Ok) <> QMessageBox.Ok:
            return
    # else: everthing ok: start writing img and html
    try:
        if len(self.filesPath)==0:
            raise IOError
        file = open(filename, "w")
        xml = self.writeXml()
        file.writelines(xml)
        file.close()
        self.iface.mapCanvas().saveAsImage(imgfilename)
        msg = "Files successfully saved to:\n" + self.filesPath
        QMessageBox.information(self.iface.mainWindow(), self.MSG_BOX_TITLE, ( msg ), QMessageBox.Ok)
        self.imageMapPluginGui.hide()
    except IOError:
        QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("No valid path or filename.\n" "Please give or browse a valid filename."), QMessageBox.Ok, QMessageBox.Ok)

  def writeXml(self):
    HEAD_HTML = \
    """
    <html>
        <head>
            <script>
                function mapOnMouseOver(str){document.getElementById("mousemovemessage").innerHTML=str; }
                function mapOnClick(str){alert(str);}
            </script>
        </head>
        <body>
        <div id="mousemovemessage"></div><br/>
        <img src=\"""" + str(self.filesPath+".png") + """\" border="0" ismap="1" usemap="#mapmap" >
        <map name="mapmap"> """
    TAIL_HTML = \
    """
        </map>
        </body>
    </html> """
    HEAD_SVG = \
    """<?xml version="1.0" standalone="no"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg viewBox = "0 0 800 800" version = "1.1"> """
    TAIL_SVG = \
    """   </svg> """

    HEAD = HEAD_SVG
    TAIL = TAIL_SVG

    # create a holder for retrieving features from the provider
    feature = QgsFeature();
    # NOTE: this already only returns the features in current view
    currentExtent = self.currentExtent
    # keep the current extent as a Geometry to be able to do some 'contains' tests later
    # ?? construct one first (get a pointer??)
    self.extentAsPoly = QgsGeometry()
    self.extentAsPoly = QgsGeometry.fromRect(currentExtent)
    # select features within current extent,
    #   with  ALL attributes, WITHIN currentExtent, WITH geom, AND using Intersect instead of bbox
    self.provider.select(self.provider.attributeIndexes(), currentExtent, True, True)
    # get a list of all selected features ids
    selectedFeaturesIds = self.iface.activeLayer().selectedFeaturesIds()
    # set max progress bar to number of features (not very accurate with a lot of huge multipolygons)
    #self.imageMapPluginGui.setProgressBarMax(self.iface.activeLayer().featureCount())
    # or run over all features in current selection, just to determine the number of... (should be simpler ...)
    count = 0
    while self.provider.nextFeature(feature):
        count = count + 1
    self.imageMapPluginGui.setProgressBarMax(count)
    progressValue = 0
    # it seems that a postgres provider is on the end of file now
    # we do the select again to set the pointer/cursor to 0 again ?
    self.provider.select(self.provider.attributeIndexes(), currentExtent, True, True)
    # dit moet ook werken???
#    unieken = self.getUniqueValues( self.provider, self.hrefAttributeIndex )
#    for uniek in unieken:
#        print "- %s - %s - %s" % (type(uniek) , uniek.typeName(), uniek.toString() )
    self.provider.rewind()
    
    xml = ['']
    # html plus some rudimentary javascript to show off the mouse click and mouse over
    xml.append(HEAD)
    # now iterate through each feature
    while self.provider.nextFeature(feature):
      progressValue = progressValue+1
      self.imageMapPluginGui.setProgressBarValue(progressValue)
      # if checkbox 'selectedFeaturesOnly' is checked: check if this feature is selected
      if self.selectedFeaturesOnly and feature.id() not in selectedFeaturesIds:
        # print "skipping %s " % feature.id()
        None
      else:
        geom = feature.geometry()
        xml.append('<g>')
        # print "GeomType: %s" % geom.wkbType()
        if geom.wkbType() == QGis.WKBPoint: # 1 = WKBPoint
            buffer = self.iface.mapCanvas().mapUnitsPerPixel()*10 # (plusminus 20pixel areas)
            #print "buffer ok..."
            polygon = geom.buffer(buffer,0).asPolygon()
            xml.append(self.polygon2xml(feature, polygon, currentExtent))
        if geom.wkbType() == QGis.WKBPolygon: # 3 = WKBTYPE.WKBPolygon:
            polygon = geom.asPolygon()  # returns a list
            xml.append(self.polygon2xml(feature, polygon, currentExtent))
        if geom.wkbType() == QGis.WKBMultiPolygon: # 6 = WKBTYPE.WKBMultiPolygon:
            multipolygon = geom.asMultiPolygon() # returns a list
            for polygon in multipolygon:
              xml.append(self.polygon2xml(feature, polygon, currentExtent))
    
        xml.append('</g>')
    xml.append(TAIL)
    return xml

  def polygon2xml(self, feature, polygon, currentExtent):
    xml = ''
    for ring in polygon:
      # for given ring in feature, IF al least on point on ring is in currentExtent
      # generate a string like:
      # <area shape=polygon href='xxx' onClick="mapOnClick('yyy')" onMouseOver="mapOnMouseOver('zzz')  coords=519,-52,519,..,-52,519,-52>
      htm = '           <area shape="polygon" '
      if self.imageMapPluginGui.isHrefChecked():
          htm = htm + 'href="' + feature.attributeMap()[self.hrefAttributeIndex].toString() + '" '
      if self.imageMapPluginGui.isOnClickChecked():
          # escape ' and " because the will collapse as javascript parameter
          param = feature.attributeMap()[self.onClickAttributeIndex].toString()
          htm = htm + 'onClick="mapOnClick(\'' + self.jsEscapeString(param) + '\')" '
      if self.imageMapPluginGui.isOnMouseOverChecked():
          # escape ' and " because the will collapse as javascript parameter
          param = feature.attributeMap()[self.onMouseOverAttributeIndex].toString()
          htm = htm + 'onMouseOver="mapOnMouseOver(\'' + self.jsEscapeString(param) + '\')" '
      htm = htm + ' coords="'

      htm = '<polygon fill="green" stroke="black" stroke-width="1" points="'

      lastPixel=[0,0]
      insideExtent = False
      coordCount = 0
      for point in ring:
          # NOT WORKING ????
          #pixpoint = m2p.transform(point.x(), point.y())
          #print m2p.transform(point.x(), point.y())
          # this should be easier to do? Check if all points if this ring are withing current extent, only if true add to html
          if self.extentAsPoly.contains(point):
              insideExtent = True
          pixpoint =  self.w2p(point.x(), point.y(), 
                  self.iface.mapCanvas().mapUnitsPerPixel(),
                  currentExtent.xMinimum(), currentExtent.yMaximum())
          if lastPixel<>pixpoint:
              coordCount = coordCount +1
              #htm += (str(pixpoint[0]) + ',' + str(pixpoint[1]) + ',')
              htm += (str(pixpoint[0]) + ',' + str(pixpoint[1]) + ' ')
              lastPixel = pixpoint
      #htm.remove(len(htm)-1,len(htm))
      htm = htm[0:-1] # remove last character (possible comma)
      # if at least ONE pixel of this ring is in current view extent, return the area-string, otherwise return an empty string
      if not insideExtent:
          #print "RING FULLY OUTSIDE EXTENT: %s " % ring
          None
      else:
          # check if there are more then 2 coords: very small polygons on current map can have coordinates
          # which if rounded to pixels all come to the same pixel, resulting in just ONE x,y coordinate
          # we skip these
          if coordCount < 2:
              #print "Ring contains just one pixel coordinate pair: skipping"
              None
          else:
              #htm += '">\n'
              htm += '"/>\n'
              xml += htm
    return xml

  def renderTest(self, painter):
    # Get canvas dimensions
    self.canvaswidth = painter.device().width()
    self.canvasheight = painter.device().height()

  def setFilesPath(self, filesPathQString):
    self.filesPath = filesPathQString

  def onHrefAttributeFieldSet(self, attributeFieldQstring):
    self.hrefAttributeField = attributeFieldQstring
    self.hrefAttributeIndex = self.provider.fieldNameIndex(attributeFieldQstring)

  def onClickAttributeFieldSet(self, attributeFieldQstring):
    self.onClickAttributeField = attributeFieldQstring
    self.onClickAttributeIndex = self.provider.fieldNameIndex(attributeFieldQstring)

  def onMouseOverAttributeFieldSet(self, attributeFieldQstring):
    self.onMouseOverAttributeField = attributeFieldQstring
    self.onMouseOverAttributeIndex = self.provider.fieldNameIndex(attributeFieldQstring)

  def setSelectedOnly(self, selectedOnlyBool):
    print "selectedFeaturesOnly: %s" % selectedOnlyBool
    self.selectedFeaturesOnly = selectedOnlyBool


  # NOT WORKING ????
  # pixpoint = m2p.transform(point.x(), point.y())
  # print m2p.transform(point.x(), point.y())
  # so for now: a custom 'world2pixel' method
  def w2p(self, x, y, mupp, minx, maxy):
    pixX = (x - minx)/mupp
    pixY = (y - maxy)/mupp
    return [int(pixX), int(-pixY)]



  # escape ' and " so string can be safely used as string javascript argument
  def jsEscapeString(self, str):
    return str.replace("'", "\\'").replace('"', '\"')

  # Return all unique values in field based on field index
  def getUniqueValues( self, provider, index ):
    allAttrs = provider.attributeIndexes()    
    provider.select( allAttrs )
    f = QgsFeature()
    values = []
    check = []
    while provider.nextFeature( f ):
      if not f.attributeMap()[ index ].toString() in check:
        values.append( f.attributeMap()[ index ] )
        check.append( f.attributeMap()[ index ].toString() )
    return values

