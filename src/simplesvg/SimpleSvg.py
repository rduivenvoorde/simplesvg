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

BUGS:

"""

import os.path
# Import the PyQt and QGIS libraries
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import *
# Initialize Qt resources from file resources.py
#import resources_rc
# Import the code for the dialogs
from .SimpleSvgDialog import SimpleSvgDialog

SVG_TYPE_PATH = 1
SVG_TYPE_SHAPE = 2

# next:
# using short notation ?
# using styles instead of inline stuff ? Mmm, apparently no css-style implementation in inkscape yet ...??
# see if it's possible to use world coordinates instead of pixels
# make 'skipping abundant points' an option
# adding raster layers als inline images


# http://www.carto.net/papers/svg/samples/
# uit: http://www.carto.net/papers/svg/samples/viewbox.shtml
# image includen:
#<g id="relief">
#   <image transform="matrix(0.876704, 0, 0, 0.8767, -2357.76, 1302.27)" x="0" y="-1472" width="5258" height="2642" xlink:href="x_austria_relief.png"/>
#</g>

# style definities
#<defs>
#  <style type="text/css">
#   <![CDATA[
#    .str7 {stroke:#1F1A17;stroke-width:3}
#    .str4 {stroke:#0093DD;stroke-width:3}
#    .str5 {stroke:#0093DD;stroke-width:4}
#    .str3 {stroke:#0093DD;stroke-width:5}
#    .str2 {stroke:#0093DD;stroke-width:6}
#    .str1 {stroke:#0093DD;stroke-width:8}
#    .str6 {stroke:#ee9090;stroke-width:14}
#    .str0 {stroke:#DA251D;stroke-width:21}
#    .fil0 {fill:none}
#    .fil2 {fill:#1F1A17}
#    .fil1 {fill:#C4E5FA}
#    .fil3 {fill:#FFFFFF}
#    .fnt1 {font-weight:normal;font-size:125px;font-family:'Arial';text-rendering:optimizeLegibility;}
#    .fnt0 {font-weight:normal;font-size:139px;font-family:'Arial';text-decoration:underline;text-rendering:optimizeLegibility;}
#   ]]>
#  </style>
# </defs>
  
# short notation
# <path class="fil0 str6" d="M113 1084c2,9 14,23 4,29 -10,5 -28,-14 -39,-9 -11,5 -8,21 -12,31"/>

# (point) symbols
# http://www.carto.net/papers/svg/samples/symbol.shtml


# pycharm debugging
# COMMENT OUT BEFORE PACKAGING !!!
#import pydevd
#pydevd.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True, suspend=False)

class SimpleSvg:

  MSG_BOX_TITLE = "QGIS SimpleSvg Plugin "

  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface
    self.svgFilename = QSettings().value('/simplesvg/lastfile', '')
    self.svgType = SVG_TYPE_PATH
    self.strokeLineJoin = 'round' # miter, round, bevel
    # normal usage: current scale, only the features which touch current mapcanvas
    # if setting this false, ALL features will be taken from the dataprovider
    # and rendered as vectors, NOTE: not working for raster layers !
    self.featuresInMapcanvasOnly = True

  def initGui(self):
      # Create action that will start plugin configuration
    self.action = QAction(QIcon(":/plugins/simplesvg/icon.png"), \
            "Save as SVG", self.iface.mainWindow())
    # connect the action to the run method
    self.action.triggered.connect(self.run)

    # Add toolbar button and menu item
    self.iface.addToolBarIcon(self.action)
    self.dlg = SimpleSvgDialog(self.iface)
    self.dlg.setFilePath(self.svgFilename)
    # TODO
    #QObject.connect(self.dlg, SIGNAL("showHelp()"), self.showHelp)
    #QObject.connect(self.dlg, SIGNAL("accepted()"), self.writeToFile)
    self.dlg.accepted.connect(self.writeToFile)
    #TODO
    #QObject.connect(self.dlg, SIGNAL("cbFeaturesInMapcanvasOnlyChanged"), self.setFeaturesInMapcanvasOnly)

    # about
    self.aboutAction = QAction(QIcon(":/plugins/simplesvg/help.png"), \
                          "About", self.iface.mainWindow())
    self.aboutAction.setWhatsThis("SimpleSvg Plugin About")
    #QObject.connect(self.aboutAction, SIGNAL("activated()"), self.about)
    self.aboutAction.triggered.connect(self.about)
    # help
    self.helpAction = QAction(QIcon(":/plugins/simplesvg/help.png"), \
                          "Help", self.iface.mainWindow())
    self.helpAction.setWhatsThis("SimpleSvg Plugin Help")
    #QObject.connect(self.helpAction, SIGNAL("activated()"), self.showHelp)
    self.helpAction.triggered.connect(self.showHelp)
    if hasattr(self.iface, "addPluginToWebMenu" ):
        self.iface.addPluginToWebMenu("&Save as SVG", self.action)
        self.iface.addPluginToWebMenu("&Save as SVG", self.aboutAction)
        self.iface.addPluginToWebMenu("&Save as SVG", self.helpAction)
    else:
        self.iface.addPluginToMenu("&Save as SVG", self.action)
        self.iface.addPluginToMenu("&Save as SVG", self.aboutAction)
        self.iface.addPluginToMenu("&Save as SVG", self.helpAction)

  def setFeaturesInMapcanvasOnly(self, checked):
    if not checked:
        QMessageBox.information(self.dlg, "Warning", "Be carefull: unchecking this, means QGIS is going to fetch ALL objects from your data.\nHandle with care for big datasets.")
    self.featuresInMapcanvasOnly = checked

  def showHelp(self):
    docFile = os.path.join(os.path.dirname(__file__), "docs","index.html")
    QDesktopServices.openUrl( QUrl("file:" + docFile) )

  def writeToFile(self):
      self.svgFilename = self.dlg.getFilePath()
      # save this filename in settings for later
      QSettings().setValue('/simplesvg/lastfile', self.svgFilename)
      output = self.writeSVG()
      file = open(self.svgFilename, "wb")
      #print output
      for line in output:
          #print '%s - %s' % (type(line),line)
          file.write(line.encode('utf-8'))
      file.close()
      QMessageBox.information(self.iface.mainWindow(), \
              "SimpleSvg Plugin", "Finished writing to svg")

  def about(self):
    infoString = "Written by Richard Duivenvoorde\nEmail - richard@duif.net\n"
    infoString += "Company - http://www.webmapper.net\n"
    infoString += "Source: http://github.com/rduivenvoorde/simplesvg/"
    QMessageBox.information(self.iface.mainWindow(), \
              "SimpleSvg Plugin About", infoString)

  def unload(self):
    # Remove the plugin menu item and icon
    if hasattr ( self.iface, "addPluginToWebMenu" ):
        self.iface.removePluginWebMenu("&Save as SVG",self.action)
        self.iface.removePluginWebMenu("&Save as SVG",self.helpAction)
        self.iface.removePluginWebMenu("&Save as SVG",self.aboutAction)
    else:
        self.iface.removePluginMenu("&Save as SVG",self.action)
        self.iface.removePluginMenu("&Save as SVG",self.helpAction)
        self.iface.removePluginMenu("&Save as SVG",self.aboutAction)

    self.iface.removeToolBarIcon(self.action)

    #QObject.disconnect(self.aboutAction, SIGNAL("activated()"), self.about)
    self.aboutAction.triggered.disconnect(self.about)
    # TODO
    #QObject.disconnect(self.helpAction, SIGNAL("activated()"), self.showHelp)
    self.action.triggered.disconnect(self.run)
    self.dlg.accepted.connect(self.writeToFile)

  # run method that performs all the real work
  def run(self):
    self.dlg.show()

  def writeSVG(self):
    # determine extent for later use (only write geoms that are at least partially contained)
    self.currentExtent = self.iface.mapCanvas().extent()
    w=self.iface.mapCanvas().size().width()
    h=self.iface.mapCanvas().size().height()
    # keep the current extent as a Geometry to be able to do some 'contains' tests later
    self.extentAsPoly = QgsGeometry();
    self.extentAsPoly = QgsGeometry.fromRect(self.currentExtent);

    svg = [u'<?xml version="1.0" standalone="no"?>\n']
    svg.append(u'<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
    svg.append(u'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox = "0 0 '+str(w)+' '+str(h)+'" version = "1.1">\n')
    svg.append(u'<!-- svg generated using QGIS www.qgis.org -->\n')

    # for all visible layers, from bottom to top (-1)
    for i in range (self.iface.mapCanvas().layerCount()-1, -1, -1):
        layer = self.iface.mapCanvas().layer(i)
        if layer.type() == QgsMapLayer.VectorLayer:  # 0 vector
            svg.extend(self.writeVectorLayer(layer, False))
          # TODO REMOVE CLEAN: old renderer stuff
          # if self.isRendererV2(layer):
          #   #QMessageBox.information(self.iface.mainWindow(), "Warning", "New Symbology layer found for layer '"+layer.name()+"'\n\nThe plugin cannot handle layer(s) which use 'New Symbology' yet.\n\nThis layer will be ignored in export.\n\nPlease change symbology of these layer(s) to 'Old Symbology' if you want this layer in svg.")
          #   #pass
          #   svg.extend(self.writeVectorLayer(layer, False))
          # # else: # old symbology
          # #   svg.extend(self.writeVectorLayer(layer, False))
        elif layer.type() == QgsMapLayer.RasterLayer:  # 1 raster
            svg.extend(self.writeRaster(layer))
        # layers like OpenLayers/OpenStreetmap/Google are plugin layer: write as raster for now
        elif layer.type() == QgsMapLayer.PluginLayer:  # 2 plugin layer
            svg.extend(self.writeRaster(layer))

    # now layers with labels
    # TODO Make labels work again
    # for i in range (self.iface.mapCanvas().layerCount()-1, -1, -1):
    #     layer = self.iface.mapCanvas().layer(i)
    #     if layer.type() == QgsMapLayer.VectorLayer:  # 0 vector
    #         lblSettings = QgsPalLayerSettings()
    #         lblSettings.readFromLayer(layer)
    #     #TODO: fix this if layer.type()==0 and layer.hasLabelsEnabled(): # only vectors have labels
    #     if layer.type() == QgsMapLayer.VectorLayer and lblSettings.enabled: # only vectors have labels
    #         svg.extend(self.writeVectorLayer(layer, True))

    # qgis extent, usable for clipping in Inkscape
    svg.extend(self.writeExtent())
    svg.append(u'</svg>')
    return svg

  def isRendererV2(self, layer):
      # TODO CHECK
      return layer.type() == QgsMapLayer.VectorLayer
      # return (layer.type() == QgsMapLayer.VectorLayer and hasattr(layer, 'isUsingRendererV2') and layer.isUsingRendererV2()) \
      #        or (layer.type() == QgsMapLayer.VectorLayer and not hasattr(layer, 'isUsingRendererV2') and ('rendererV2' in dir(layer)))

  def isRendererV2SIP2(self, layer):
      # TODO CHECK
      return layer.type() == QgsMapLayer.VectorLayer
      #return (layer.type() == QgsMapLayer.VectorLayer and not hasattr(layer, 'isUsingRendererV2') and ('rendererV2' in dir(layer)))

  def writeVectorLayer(self, layer, labels=False):
    # in case of 'on the fly projection' 
    # AND 
    # different crs's for mapCanvas/project and layer we have to reproject stuff
    destinationCrs = self.iface.mapCanvas().mapSettings().destinationCrs()
    layerCrs = layer.crs()
    if self.featuresInMapcanvasOnly:
        mapCanvasExtent = self.iface.mapCanvas().extent()
    else:
        mapCanvasExtent = layer.extent()
    #print 'destination crs: %s:' % destinationCrs.toProj4()
    #print 'layer crs:       %s:' % layerCrs.toProj4()
    doCrsTransform = False
    if not destinationCrs == layerCrs:
      # we have to transform the mapCanvasExtent to the data/layer Crs to be able
      # to retrieve the features from the data provider
      # but ONLY if we are working with on the fly projection
      # (because in that case we just 'fly' to the raw coordinates from data)
      if self.featuresInMapcanvasOnly:
        crsTransform = QgsCoordinateTransform(destinationCrs, layerCrs, QgsProject.instance())
        mapCanvasExtent = crsTransform.transformBoundingBox(mapCanvasExtent)
      # we have to have a transformer to do the transformation of the geometries
      # to the mapcanvas crs ourselves:
      crsTransform = QgsCoordinateTransform(layerCrs, destinationCrs, QgsProject.instance())
      doCrsTransform = True

    # TODO MAKE LABELS WORK
    #lblSettings = QgsPalLayerSettings()
    #lblSettings.readFromLayer(layer)

    # select features within current extent,
    #   with  ALL attributes, WITHIN currentExtent, WITH geom, AND using Intersect instead of bbox
    # we are going to group all features by their symbol so in svg we can group them in a <g> tag with the symbol style
    provider = layer.getFeatures( QgsFeatureRequest().setFilterRect(mapCanvasExtent))
    renderer = layer.renderer()
    if str(renderer.type()) not in ("singleSymbol", "categorizedSymbol", "graduatedSymbol"):
      QMessageBox.information(self.iface.mainWindow(), "Warning", "New Symbology layer found for layer '"+layer.name()+"'\n\nThis layer uses a Renderer/Style which cannot be used with this plugin.\n\nThis layer will be ignored in export.")
      return ""
    symbols = renderer.symbols(QgsRenderContext()) # TODO check, is this the right context?
    symbolFeatureMap = dict.fromkeys(symbols, [])
    id=self.sanitizeStr(str(layer.name()).lower())
    if labels:
        id=id+'_labels'
    svg = [u'<g id="'+id+'" inkscape:groupmode="layer" inkscape:label="'+id+'">\n']; # start of layer g-element
    # now iterate through each feature and group by feature
    f = QgsFeature()
    feature = None
    #print "1 symbols holds %s symbols" % len(symbols)
    while provider.nextFeature(f):
      feature = QgsFeature(f)
      geom = feature.geometry()
      layerCrs = layer.crs()

      if doCrsTransform:
        if hasattr(geom, "transform"):
          geom.transform(crsTransform)
        else:
          QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("Cannot crs-transform geometry in your QGIS version ...\n" "Only QGIS version 1.5 and above can transform geometries on the fly\n" "As a workaround, you can try to save the layer in the destination crs (eg as shapefile) and reload that layer...\n"), QMessageBox.Ok, QMessageBox.Ok)
          break

      symbol = self.symbolForFeature(layer, feature)
      #print "feature: %s  symbol: %s rgb: %s %s %s" % (feature, symbol, symbol.color().red(), symbol.color().green(), symbol.color().blue())
      # Continous Color does NOT have all symbols, but ONLY start and end color
      # that's why we do some extra stuff here...
      # ONLY needed for Old Symbology (which have 'name()' and not 'type()')
      if hasattr(renderer, 'name') and renderer.name() == "Continuous Color":
        symbols.append(symbol)
        if symbol in symbolFeatureMap:
            symbolFeatureMap[symbol]=[feature]
        else:
            symbolFeatureMap.update({symbol:[feature]})
      else:
        if not symbol in symbolFeatureMap or len(symbolFeatureMap[symbol])==0:
          symbolFeatureMap[symbol]=[feature]
        else:
          symbolFeatureMap[symbol].append(feature)
    # now iterate over symbols IF there are any features in this view from this layer
    if feature != None:
      id=id+'_'
      i=0
      for symbol in symbols:
        sym = self.createSymbol(feature, symbol, layer)
        # start of symbol g-element, holds colors and stroke etc
        if not labels:
          fill = ''
          if 'fill' in sym:
            fill = 'fill="' + sym['fill'] + '"'
          svg.append(u'<g stroke="' + sym['stroke'] + '" '+ fill + ' stroke-linejoin="' + self.strokeLineJoin + '" stroke-width="' + sym['stroke-width'] +'">\n')
        else:
          # TODO fix this, use color of label ??
          if False:
            lc = layer.label().labelAttributes().color()
            lblColor = u'rgb(%s,%s,%s)' % (lc.red(), lc.green(), lc.blue())
          else:  # labels all black for now...
            lblColor = u'rgb(0,0,0)'
          svg.append(u'<g stroke="none" fill="'+lblColor+'">\n')
        for feature in symbolFeatureMap[symbol]:
          i=i+1
          # labeltxt is used both for the real labels, AND for the inkscape-label attributes of g and txt elements
          # TODO fix this
          # if lblSettings.enabled:
          #   labeltxt = self.sanitizeStr(feature[lblSettings.fieldName])
          # else:
          #   #labeltxt = self.sanitizeStr(layer.label().fieldValue(0, feature)) # only first field for now.
          #   #labeltxt = self.sanitizeStr(unicode(feature.fields().field(0)))
          #   labeltxt = self.sanitizeStr('')
          labeltxt = self.sanitizeStr('')  # TODO: temp until labels fixed

          if not labels:
              # we are going to use the 'displayName' == 'layer.displayField()' column as node-id/labelfor inkscape
              feature_label = self.sanitizeStr(feature[layer.displayField()])
              svg.extend(self.writeFeature(feature, id+str(i), feature_label))
          if labels:
            geom = feature.geometry().centroid()
            # centroid-method returns a NON-transformed centroid
            if doCrsTransform:
              if hasattr(geom, "transform"):
                geom.transform(crsTransform)
              else:
                QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("Cannot crs-transform geometry in your QGIS version ...\n" "Only QGIS version 1.5 and above can transform geometries on the fly\n" "As a workaround, you can try to save the layer in the destination crs (eg as shapefile) and reload that layer...\n"), QMessageBox.Ok, QMessageBox.Ok)
                break
            # actual label node
            svg.extend(self.label2svg(geom.asPoint(), id+str(i), self.symbolForFeature(layer, feature), labeltxt))
        svg.append(u'</g>\n'); # end of symbol
    svg.append(u'</g>\n'); # end of layer
    return svg

  # TODO REMOVE ??? as this is 1.8 symbols stuff
  # def symbol(self, feature, symbol):
  #   sym={}
  #   sc = symbol.color()
  #   sym['stroke'] = u'rgb(%s,%s,%s)' % (sc.red(), sc.green(), sc.blue())
  #   # fill color: only non line features have fill color, lines have 'none'
  #   geom = feature.geometry()
  #   if geom.wkbType() in (QgsWkbTypes.WKBLineString, QgsWkbTypes.WKBLineString25D, QgsWkbTypes.WKBMultiLineString, QgsWkbTypes.WKBMultiLineString25D):
  #     sym['fill'] = u'none'
  #   else:
  #     f = symbol.fillColor()
  #     sym['fill'] = u'rgb(%s,%s,%s)' % (f.red(), f.green(), f.blue())
  #   # pen: in QT pen can be 0
  #   if symbol.pen().width() < 1:
  #     sym['stroke-width'] = u'0.5'
  #   else:
  #     sym['stroke-width'] = str(symbol.pen().width())
  #   return sym

  def createSymbol(self, feature, symbol, layer):
    #print '##### symbol: %s, symbollayercount: %s' % (symbol, symbol.symbolLayerCount())
    sym={}
    if symbol.symbolLayerCount() > 1:
      QMessageBox.information(self.iface.mainWindow(), "Warning", "Layer '"+layer.name()+"' uses New Symbology, and styles with more the one Symbol Layer, only the first one will be use.")
    sl = symbol.symbolLayer(0)
    slprops = sl.properties()
    #print("symbollayer properties: %s" % slprops)
    # region/polgyons have: color_border / style_border / offset / style / color / width_border
    #  {PyQt4.QtCore.QString(u'color_border'): PyQt4.QtCore.QString(u'0,0,0,255'), PyQt4.QtCore.QString(u'style_border'): PyQt4.QtCore.QString(u'solid'), PyQt4.QtCore.QString(u'offset'): PyQt4.QtCore.QString(u'0,0'), PyQt4.QtCore.QString(u'style'): PyQt4.QtCore.QString(u'solid'), PyQt4.QtCore.QString(u'color'): PyQt4.QtCore.QString(u'0,0,255,255'), PyQt4.QtCore.QString(u'width_border'): PyQt4.QtCore.QString(u'0.26')}
    # markers/points have : color_border / offset / size / color / name / angle:
    #  {PyQt4.QtCore.QString(u'color_border'): PyQt4.QtCore.QString(u'0,0,0,255'), PyQt4.QtCore.QString(u'offset'): PyQt4.QtCore.QString(u'0,0'), PyQt4.QtCore.QString(u'size'): PyQt4.QtCore.QString(u'2'), PyQt4.QtCore.QString(u'color'): PyQt4.QtCore.QString(u'255,0,0,255'), PyQt4.QtCore.QString(u'name'): PyQt4.QtCore.QString(u'circle'), PyQt4.QtCore.QString(u'angle'): PyQt4.QtCore.QString(u'0')}
    # lines have          : color / offset / penstyle / width / use_custom_dash / joinstyle / customdash / capstyle:
    #  {PyQt4.QtCore.QString(u'color'): PyQt4.QtCore.QString(u'255,255,0,255'), PyQt4.QtCore.QString(u'offset'): PyQt4.QtCore.QString(u'0'), PyQt4.QtCore.QString(u'penstyle'): PyQt4.QtCore.QString(u'solid'), PyQt4.QtCore.QString(u'width'): PyQt4.QtCore.QString(u'0.5'), PyQt4.QtCore.QString(u'use_custom_dash'): PyQt4.QtCore.QString(u'0'), PyQt4.QtCore.QString(u'joinstyle'): PyQt4.QtCore.QString(u'bevel'), PyQt4.QtCore.QString(u'customdash'): PyQt4.QtCore.QString(u'5;2'), PyQt4.QtCore.QString(u'capstyle'): PyQt4.QtCore.QString(u'square')}
    strokekey = u'line_color'
    strokekey2 = u'outline_color'
    colorkey = u'color'
    stylekey = u'style'
    width_borderkey = u'width_border'
    widthkey = u'width'
    if strokekey in slprops:
      stroke = slprops[strokekey]
      sym['stroke'] = u'rgb(%s)' % (stroke[:stroke.rfind(',')])
    elif strokekey2 in slprops:
      stroke = str(slprops[strokekey2])
      sym['stroke'] = u'rgb(%s)' % (stroke[:stroke.rfind(',')])
    else:
      sym['stroke'] = u'none'
    # fill color: only non line features have fill color, lines have 'none'
    geom = feature.geometry()
    if colorkey in slprops:
      fill = str(slprops[colorkey])
      if QgsWkbTypes.geometryType(geom.wkbType())  == QgsWkbTypes.GeometryType.LineGeometry:
        sym['stroke'] = u'rgb(%s)' % (fill[:fill.rfind(',')])
      # points have fill and stroke
      sym['fill'] = u'rgb(%s)' % (fill[:fill.rfind(',')])
    # if feature is line OR when there is no brush: set fill to none
    if QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.GeometryType.LineGeometry \
       or (stylekey in slprops and slprops[stylekey] == 'no'):
      sym['fill'] = u'none'
    # pen: in QT pen can be 0
    if width_borderkey in slprops:
      sym['stroke-width'] = str(slprops[width_borderkey])
    elif widthkey in slprops:
      sym['stroke-width'] = str(slprops[widthkey])
    else:
      sym['stroke-width'] = u'0.40'
    #print(sym)
    return sym


  def writeExtent(self):
    svg = [u'<!-- QGIS extent for clipping, eg in Inkscape -->\n<g id="qgisviewbox" inkscape:groupmode="layer" inkscape:label="qgisviewbox" stroke="rgb(255,0,0)" stroke-width="1" fill="none" >\n']
    for ring in self.extentAsPoly.asPolygon():
        svg.append(u'<path d="M ')
        first = True
        for point in ring:
            pixpoint =  self.w2p(point.x(), point.y(), self.iface.mapCanvas().mapUnitsPerPixel(), self.currentExtent.xMinimum(), self.currentExtent.yMaximum())
            if not first:
                svg.append(u'L ')
            svg.append((str(pixpoint[0]) + ',' + str(pixpoint[1]) + ' '))
            first = False
        svg.append(u'" />\n')
    svg.append(u'</g>')
    return svg


  def writeRaster(self, layer):

    # hide all layers except 'layer' and save as png image in current directory
    # TODO maybe inline it in svg?

    # TODO CLEANUP
    # visibleList=self.iface.mapCanvas().layers()
    # legend = self.iface.legendInterface()
    # # set all layers invisible EXCEPT layer
    # for lyr in visibleList:
    #   if lyr != layer:
    #     legend.setLayerVisible(lyr, False)

    # save visibility of layers
    root = QgsProject.instance().layerTreeRoot()
    visible_tree_layers = []
    layers = root.findLayers()
    for tree_layer in layers:
        if tree_layer.isVisible():
            visible_tree_layers.append(tree_layer)
            if tree_layer.layerId() != layer.id():
                tree_layer.setItemVisibilityChecked(False)

    lyrName = layer.name()
    imgName = lyrName+'.png'
    try:
        imgPath= self.svgFilename[:self.svgFilename.rfind('/')+1]
    except NameError:
        imgPath= self.svgFilename[:self.svgFilename.rfind('/')+1]
    # save image next to svg but put it in Image tag only the local filename
    self.iface.mapCanvas().saveAsImage(imgPath+imgName)
    # <image y="-7.7685061" x="27.115078" id="image3890" xlink:href="nl.png" />
    svg = [u'<g id="'+lyrName+'" inkscape:groupmode="layer" inkscape:label="'+lyrName+'">\n'];
    #svg.append('<image y="0" x="0" xlink:href="'+imgPath+imgName+'" />')
    svg.append(u'<image y="0" x="0" xlink:href="'+imgName+'" />')
    svg.append(u'</g>') # end of raster layer

    # now set earlier visible layers back to visible
    for tl in visible_tree_layers:
        tl.setItemVisibilityChecked(True)
    return svg

  def label2svg(self, point, fid, symbol, labelTxt):
    # <g> <text x="262.08704" y="523.79077">abc</text> </g>
    #point = feature.geometry().centroid().asPoint()
    xy =  self.w2p(point.x(), point.y(), self.iface.mapCanvas().mapUnitsPerPixel(), self.currentExtent.xMinimum(), self.currentExtent.yMaximum())
    inkscapeLbl = ''
    if len(labelTxt)>0:
        inkscapeLbl = 'inkscape:label="'+labelTxt+'_lbl'+'"'
    svg = [u'<text id="'+fid+'" x="'+str(xy[0])+'" y="'+str(xy[1])+'" '+inkscapeLbl+'>'+str(labelTxt)+'</text>\n']
    return svg

  def sanitizeStr(self, string):
    # TODO: find the right way to do this
    return str(string).replace(' ','_').replace('/','_').replace(',','_').replace('.','_')

  def writeFeature(self, feature, fid, labelTxt):
    svg = []
    # <g>-element set's style attributes
    inkscapeLbl = ''
    if len(labelTxt)>0:
        inkscapeLbl = 'inkscape:label="'+str(labelTxt)+'"'
    svg.append(u'<g id="' + fid + '" '+inkscapeLbl+'>\n')
    geom=feature.geometry()
    currentExtent=self.currentExtent

    # instead of checking if geom is multiple-type or not, just assume it:
    # TODO: CLEANUP
    # if geom.wkbType() == QgsWkbTypes.GeometryType.PointGeometry: # 1 = WKBPoint
    #     point = geom.asPoint()
    #     svg.extend(self.point2svg(point, currentExtent))
    if QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.GeometryType.PointGeometry:
        multipoint = geom.asMultiPoint()
        for point in multipoint:
          svg.extend(self.point2svg(point, currentExtent))
    # if geom.wkbType() in (QgsWkbTypes.WKBPolygon, QgsWkbTypes.WKBPolygon25D): # 3 = WKBTYPE.WKBPolygon:
    #     polygon = geom.asPolygon()  # returns a list
    #     svg.extend(self.polygon2svg(feature, polygon, currentExtent))
    if QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.GeometryType.PolygonGeometry: # 6 = WKBTYPE.WKBMultiPolygon:
        multipolygon = geom.asMultiPolygon() # returns a list
        for polygon in multipolygon:
          svg.extend(self.polygon2svg(feature, polygon, currentExtent))
    # if geom.wkbType() in (QgsWkbTypes.WKBLineString, QgsWkbTypes.WKBLineString25D): # 6 = WKBTYPE.WKBLineString:
    #     line = geom.asPolyline()  # returns a list of points
    #     svg.extend(self.line2svg(feature, line, currentExtent))
    if QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.GeometryType.LineGeometry:
        multiline = geom.asMultiPolyline()  # returns a list
        for line in multiline:
            svg.extend(self.line2svg(feature, line, currentExtent))
    svg.append(u'</g>\n');
    return svg

  def point2svg(self, point, currentExtent):
    #point = feature.geometry().asPoint()
    xy =  self.w2p(point.x(), point.y(), self.iface.mapCanvas().mapUnitsPerPixel(), self.currentExtent.xMinimum(), self.currentExtent.yMaximum())
    #print(point, xy, point.x(), point.y(), self.iface.mapCanvas().mapUnitsPerPixel(), self.currentExtent.xMinimum(), self.currentExtent.yMaximum())
    # TODO take current extent into account
    svg = ['<circle cx="'+str(xy[0])+'" cy="'+str(xy[1])+'" r="5" />']
    return svg

  def symbolForFeature(self, layer, feature):
      return layer.renderer().symbolForFeature(feature, QgsRenderContext())
    # TODO REMOVE: old stuff for old symbolisation ??
    # if self.isRendererV2(layer):
    #     return layer.rendererV2().symbolForFeature(feature)
    # else:
    #   # symbolForFeatures seems not to work for Old Symbology?? Do it ourselves:
    #   # OLD symbolisation:
    #   #   Graduated Symbol: every symbol has BOTH upper and lower bound/value
    #   #   Unique Value: every symbol has BOTH upper and lower value
    #   #   Continues Color: HAS lower(==value) but NO upper value, BUT has just two symbols: MIN and MAX color, see http://doc.qgis.org/head/qgscontinuouscolorrenderer_8cpp-source.html
    #   #   Single Simbol: just one symbol, return it
    #   renderer = layer.renderer()
    #   #print "renderer.name(): %s" % renderer.name()
    #   default = None
    #   if renderer.name() == "Single Symbol":   # there is just one symbol: return it
    #     return renderer.symbols(QgsRenderContext())[0]
    #   if renderer.name() == "Continuous Color":
    #     #pass  # already done, should not come here !!
    #     minSymbol = renderer.symbols(QgsRenderContext())[0]
    #     minValue = (minSymbol.lowerValue()).toDouble()[0]  # we know Continuous Color only works with numeric attributes
    #     minRed = minSymbol.fillColor().red()
    #     minGreen = minSymbol.fillColor().green()
    #     minBlue = minSymbol.fillColor().blue()
    #     maxSymbol = renderer.symbols(QgsRenderContext())[1]
    #     maxValue = (maxSymbol.lowerValue()).toDouble()[0]  # we know Continuous Color only works with numeric attributes
    #     maxRed = maxSymbol.fillColor().red()
    #     maxGreen = maxSymbol.fillColor().green()
    #     maxBlue = maxSymbol.fillColor().blue()
    #     # create new symbol and set RGB according to calculation in http://doc.qgis.org/head/qgscontinuouscolorrenderer_8cpp-source.html
    #     symbol = QgsSymbol(minSymbol) # copy
    #     value = (feature.attributeMap()[renderer.classificationAttributes()[0]]).toDouble()[0]  # we know Continuous Color only works with numeric attributes
    #     if (maxValue - minValue) != 0:
    #       red = int ( maxRed * ( value - minValue ) / ( maxValue - minValue ) + minRed * ( maxValue - value ) / ( maxValue - minValue ) )
    #       green = int ( maxGreen * ( value - minValue ) / ( maxValue - minValue ) + minGreen * ( maxValue - value ) / ( maxValue - minValue ) )
    #       blue =  int ( maxBlue * ( value - minValue ) / ( maxValue - minValue ) + minBlue * ( maxValue - value ) / ( maxValue - minValue ) )
    #     else:
    #       red = minRed
    #       green = minGreen
    #       blue = minBlue
    #     newFillColor = QColor(red, green, blue)
    #     symbol.setFillColor(newFillColor)
    #     if renderer.drawPolygonOutline():
    #       # always black
    #       color = QColor(0,0,0)
    #       symbol.setColor(color)
    #     else:
    #       symbol.setColor(newFillColor)
    #     return symbol
    #   # else loop over symbols to find the current symbol for this feature
    #   # value can be string or numbers...
    #   value = (feature.attributeMap()[renderer.classificationAttributes()[0]]).toString()
    #   for symbol in renderer.symbols(QgsRenderContext()):
    #     lower = symbol.lowerValue()
    #     upper = symbol.upperValue()
    #     #print "lower: %s upper: %s value: %s notlower %s, notupper %s, value==lower %s, value=upper %s, str(value)[0].isdigit() %s" % (lower, upper, value, (not lower), (not upper), (value == lower), (value == upper), str(value)[0].isdigit())
    #     if not lower and not upper:
    #         # 'default value' given for default in Unique Value
    #         default = symbol
    #     # Unique Value symbols have the value in both upper and lower value (if values are string!)
    #     elif (value == lower and value == upper):
    #       return symbol
    #     # Unique Value symbols for numbers do not have an upper
    #     elif str(value)[0].isdigit() and not upper and float(value) == float(symbol.lowerValue()):
    #       return symbol
    #     # Graduated Classifications have lower AND uppervalues AND values are always numbers
    #     elif str(value)[0].isdigit() and upper and lower and (float(value) >= float(symbol.lowerValue()) and float(value) <= float(symbol.upperValue())):
    #       #print "Graduated Classification:  %s between %s and %s " % (value, symbol.lowerValue(), symbol.upperValue())
    #       return symbol
    #     #else:
    #     #  print "NEXT..."
    #   #print "RETURNING DEFAULT!!"
    #   return default

  def line2svg(self, feature, line, currentExtent):
    #print("calling line2svg...")
    linesvg = []
    svg = u''
    if self.svgType == SVG_TYPE_PATH:
      svg += '<path d="M '
    else:  # SVG_TYPE_SHAPE
      svg += '<polyline points="'
    lastPixel=[0,0]
    insideExtent = False
    coordCount = 0
    for point in line:
      if self.extentAsPoly.contains(point) or not self.featuresInMapcanvasOnly:
        insideExtent = True
      pixpoint =  self.w2p(point.x(), point.y(), self.iface.mapCanvas().mapUnitsPerPixel(), currentExtent.xMinimum(), currentExtent.yMaximum())
      #print(pixpoint)
      if lastPixel != pixpoint:
        coordCount = coordCount +1
        if self.svgType==SVG_TYPE_PATH and coordCount>1:
          svg += 'L '
        svg += (str(pixpoint[0]) + ',' + str(pixpoint[1]) + ' ')
        lastPixel = pixpoint
    # if at least ONE pixel of this ring is in current view extent, return the area-string, otherwise return an empty string
    if not insideExtent:
      #print("SKIPPING: Ring fully outside extent...?")
      pass
    else:
      # check if there are more then 2 coords: very small polygons on current map can have coordinates
      # which if rounded to pixels all come to the same pixel, resulting in just ONE x,y coordinate
      # we skip these
      if coordCount < 2:
        #print("SKIPPING: Line contains just one pixel coordinate pair")
        pass
      else:
        svg += '"/>\n'
        linesvg.append(svg)
        #print(linesvg)
    return linesvg

  # SHAPE-svg
  #  <polygon stroke="rgb(0,0,0)" fill="rgb(234,102,228)" stroke-width="1" points="439,238 445,230 ... 439,238"/>
  #     or
  #  <polygon points="439,238 445,230 ... 439,238"/>
  # PATH-svg
  #  <g stroke="rgb(0,0,0)" fill="rgb(234,102,228)" stroke-width="1" ><path d="M 439 238 L 445 220 ... L 439 238" /> </g>
  def polygon2svg(self, feature, polygon, currentExtent):
    #print "calling polygon2svg..."
    polygonsvg = ['']
    for ring in polygon:
      svg = ''
      if self.svgType == SVG_TYPE_PATH:
        svg += '<path d="M '
      else:  # SVG_TYPE_SHAPE
        svg = '<polygon points="'
      lastPixel=[0,0]
      insideExtent = False
      coordCount = 0
      for point in ring:
          if self.extentAsPoly.contains(point) or not self.featuresInMapcanvasOnly:
              insideExtent = True
          pixpoint =  self.w2p(point.x(), point.y(), self.iface.mapCanvas().mapUnitsPerPixel(), currentExtent.xMinimum(), currentExtent.yMaximum())
          if lastPixel != pixpoint:
            coordCount = coordCount +1
            if self.svgType==SVG_TYPE_PATH and coordCount>1:
              svg += 'L '
            svg += (str(pixpoint[0]) + ',' + str(pixpoint[1]) + ' ')
            lastPixel = pixpoint
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
              svg += '" />\n'
              polygonsvg.append(svg)
    return polygonsvg

  # NOT WORKING ????
  # pixpoint = m2p.transform(point.x(), point.y())
  # print m2p.transform(point.x(), point.y())
  # so for now: a custom 'world2pixel' method
  def w2p(self, x, y, mupp, minx, maxy):
    pixX = (x - minx)/mupp
    pixY = (y - maxy)/mupp
    return [int(pixX), int(-pixY)]



#class SvgFeatureRenderer2:
#
#    def __init__(self, graphic, feature, symbol):
#        self.graphic = graphic
#        self.feature = feature
#        self.symbol = symbol
#
#    def render(self):
#        # this one is for renderv2 only
#        # for now only symbollayer[0]
#        if symbol.symbolLayerCount()>1:
#            print "TOO MUCH SYMBOLLAYERS... ONLY SYMBOLS WITH ONE SYMBOLLAYER ALLOWED"
#            return
#        props = symbol.symbolLayer(0)
#        print props['color']
#        print u'rgb('++')'
#        # conclusion: no internal or external styles, styles as attributes either in group g-elements OR in individual path-elements
#
#    def renderLayer(self):
#        pass
#
#    def renderFeature(self, feature):
#        pass
#
#    def renderGeometry(self, feature):
#        pass
#
#    def renderSymbol(selfi, symbol):
#        pass

