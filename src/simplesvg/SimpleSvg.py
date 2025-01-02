
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
import pathlib
import re
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
#import pydevd_pycharm
#pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True, suspend=False)

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
    self.action = QAction(QIcon(":/plugins/simplesvg/icon.png"),  "Save as SVG", self.iface.mainWindow())
    # connect the action to the run method
    self.action.triggered.connect(self.run)

    # Add toolbar button and menu item
    self.iface.addToolBarIcon(self.action)
    self.dlg = SimpleSvgDialog(self.iface)
    self.dlg.setFilePath(self.svgFilename)
    self.dlg.showHelp.connect(self.showHelp)
    self.dlg.accepted.connect(self.writeToFile)
    self.dlg.cbFeaturesInMapcanvasOnlyChanged.connect(self.setFeaturesInMapcanvasOnly)

    # about
    self.aboutAction = QAction(QIcon(":/plugins/simplesvg/help.png"), \
                          "About", self.iface.mainWindow())
    self.aboutAction.setWhatsThis("SimpleSvg Plugin About")
    self.aboutAction.triggered.connect(self.about)
    # help
    self.helpAction = QAction(QIcon(":/plugins/simplesvg/help.png"), \
                          "Help", self.iface.mainWindow())
    self.helpAction.setWhatsThis("SimpleSvg Plugin Help")
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
      # first check IF there is a map:
      if self.iface.mapCanvas().extent().isNull():
          self.show_message_box("Error", "No map or MapCanvas yet, first create a map!")
          return
      # some filename checks:
      self.svgFilename = pathlib.Path(self.dlg.getFilePath())
      if self.dlg.getFilePath() in ("", None):
          msg = "Please provide a valid dir/path for the SVG file."
          self.show_message_box("Warning", msg)
          return
      elif not self.svgFilename.parent.exists():
        msg = "Please provide a valid name for the SVG file, INCLUDING the path."
        self.show_message_box("Warning", msg)
        return
      # NOW create a svg
      if self.svgFilename.suffix.lower() != ".svg":
          self.svgFilename = pathlib.Path(self.svgFilename).with_suffix(".svg")
      self.svgFilename = str(self.svgFilename)
      self.dlg.setFilePath(self.svgFilename)
      # save this filename in settings for later
      QSettings().setValue('/simplesvg/lastfile', self.svgFilename)
      output = self.writeSVG()
      file = open(self.svgFilename, "wb")
      #print output
      for line in output:
          #print '%s - %s' % (type(line),line)
          file.write(line.encode('utf-8'))
      file.close()
      self.show_message_box("SimpleSvg Plugin", f"Finished writing to svg file:\n{self.svgFilename}")

  def show_message_box(self, title, msg):
      QMessageBox.information(self.iface.mainWindow(), title, msg)

  def about(self):
    infoString = "Written by Richard Duivenvoorde\nEmail - richard@duif.net\n"
    infoString += "Company - http://www.webmapper.net\n"
    infoString += "Source: http://github.com/rduivenvoorde/simplesvg/"
    self.show_message_box("SimpleSvg Plugin About", infoString)

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
    self.extentAsPoly = QgsGeometry()
    self.extentAsPoly = QgsGeometry.fromRect(self.currentExtent)

    svg = ['<?xml version="1.0" standalone="no"?>\n']
    svg.append('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
    svg.append('<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox = "0 0 '+str(w)+' '+str(h)+'" version = "1.1">\n')
    svg.append('<!-- svg generated using QGIS www.qgis.org -->\n')

    # for all visible layers, from bottom to top (-1)
    for i in range (self.iface.mapCanvas().layerCount()-1, -1, -1):
        layer = self.iface.mapCanvas().layer(i)
        if layer.type() == QgsMapLayer.VectorLayer:  # 0 = vector
          svg.extend(self.writeVectorLayer(layer, False))
        elif layer.type() == QgsMapLayer.RasterLayer:  # 1 = raster
          svg.extend(self.writeRaster(layer))
        # layers like OpenLayers/OpenStreetmap/Google are plugin layer: write as raster for now
        elif layer.type() == QgsMapLayer.PluginLayer:  # 2 = plugin layer
            svg.extend(self.writeRaster(layer))

    # now vector layers with labels
    for i in range (self.iface.mapCanvas().layerCount()-1, -1, -1):
        layer = self.iface.mapCanvas().layer(i)
        if layer.type() == QgsMapLayer.VectorLayer and layer.labelsEnabled(): # only vectors have labels
            svg.extend(self.writeVectorLayer(layer, True))

    # qgis extent, usable for clipping in Inkscape
    svg.extend(self.writeExtent())
    svg.append('</svg>')
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
    if isinstance(layer.renderer(), QgsCategorizedSymbolRenderer):
      # not sure why, but... we need to do this first....:
      layer.renderer().rebuildHash()
    symbols = renderer.symbols(QgsRenderContext()) # TODO check, is this the right context?
    symbolFeatureMap = dict.fromkeys(symbols, [])
    id = self.sanitizeStr(str(layer.name()).lower())
    if labels:
        id = id + '_labels'
    svg = ['<g id="'+id+'" inkscape:groupmode="layer" inkscape:label="'+id+'"> <!-- start of layer g-element -->\n'] # start of layer g-element
    # now iterate through each feature and group by feature
    f = QgsFeature()
    feature = None
    context = QgsExpressionContext(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
    #print "1 symbols holds %s symbols" % len(symbols)
    while provider.nextFeature(f):
      feature = QgsFeature(f)
      geom = feature.geometry()

      if doCrsTransform:
        geom.transform(crsTransform)

      symbol = self.symbolForFeature(layer, feature)

      #print "feature: %s  symbol: %s rgb: %s %s %s" % (feature, symbol, symbol.color().red(), symbol.color().green(), symbol.color().blue())
      if not symbol in symbolFeatureMap or len(symbolFeatureMap[symbol])==0:
        symbolFeatureMap[symbol]=[feature]
      else:
        symbolFeatureMap[symbol].append(feature)
    # now iterate over symbols IF there are any features in this view from this layer
    if feature != None:
      id = id+'_'
      i = 0
      for symbol in symbols:
        sym = self.createSymbol(feature, symbol, layer)
        # start of symbol g-element, holds colors and stroke etc
        fill = 'fill="none"'
        if 'fill' in sym and sym['fill'] not in (None, 'none', 'None'):
          s = sym['fill']
          fill = f'fill="{self.cleanup_rgb(s)}"'
        
        if labels:  # labels !
          # TODO fix this, use color of label ??
          if False:
            # OLD
            lc = layer.label().labelAttributes().color()
            lblColor = 'rgb(%s,%s,%s)' % (lc.red(), lc.green(), lc.blue())
          else:  # labels all black for now...
            lblColor = 'rgb(0,0,0)'
          svg.append('<g stroke="none" fill="'+lblColor+'"> <!-- start of LABEL symbol -->\n')
        else:
          svg.append('<g stroke="' + self.cleanup_rgb(sym['stroke']) + '" '+ fill + ' stroke-linejoin="' + self.strokeLineJoin + '" stroke-width="' + sym['stroke-width'] +'"> <!-- start of symbol -->\n')

        for feature in symbolFeatureMap[symbol]:
          i=i+1
          if labels:
            field = layer.labeling().settings().fieldName
            labeltxt = feature[field]

          # we are going to use the features 'displayName' == 'layer.displayField()' column as node-id/label for inkscape
          # NOTE this can also be an expression:
          if not layer.displayField() == '':
            feature_label = feature[layer.displayField()]
          elif not layer.displayExpression() == '':
            context.setFeature(feature)
            feature_label = QgsExpression(layer.displayExpression()).evaluate(context)
          else:
            feature_label = ''

          if not labels:
            # feature !
            svg.extend(self.writeFeature(feature, id + str(i), self.sanitizeStr(feature_label)))
          else:
            # label !
            geom = feature.geometry().centroid()
            # centroid-method returns a NON-transformed centroid
            if doCrsTransform:
              if hasattr(geom, "transform"):
                geom.transform(crsTransform)
              else:
                QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("Cannot crs-transform geometry in your QGIS version ...\n" "Only QGIS version 1.5 and above can transform geometries on the fly\n" "As a workaround, you can try to save the layer in the destination crs (eg as shapefile) and reload that layer...\n"), QMessageBox.Ok, QMessageBox.Ok)
                break
            # actual label node
            svg.extend(self.label2svg(geom.asPoint(), id + str(i), self.symbolForFeature(layer, feature), labeltxt))
        svg.append('</g> <!-- end of symbol g -->\n') # end of symbol
    if labels:
        comment = 'label layer'
    else:
        comment = 'layer'
    svg.append(f'</g> <!-- end of {comment} g -->\n') # end of layer
    return svg

  @staticmethod
  def cleanup_rgb(color_string: str):
    """
    rgb color codes looked like:
     rgb(219,30,42,255)
    but now like:
     rgb(219,30,42,255,rgb:0.85882352941176465,0.11764705882352941,0.16470588235294117)
    or:
     0,0,0,255,rgb:0,0,0,1
    or:
     65,206,152,255,hsv:0.43611111111111112,0.68627450980392157,0.80784313725490198,1

    Inkscape wants 'rgb(r,g,b)'
    :return:
    """
    """
    Matched by match1
        rgb color codes looked like:
         'rgb(219,30,42,255)'
        but now like:
         'rgb(219,30,42,255,rgb:0.85882352941176465,0.11764705882352941,0.16470588235294117'
    Matched by match2
         '0,0,0,255,rgb:0,0,0,1'         
    """
    match1 = re.search(r'rgb\(\d+,\d+,\d+', color_string)
    match2 = re.search(r'\d+,\d+,\d+', color_string)
    if match1:
        return match1.group(0)+')'
    elif match2:
        return 'rgb('+match2.group(0)+')'
    else:
        return 'rgb(100,100,100)'

  def createSymbol(self, feature, symbol, layer):
    #print '##### symbol: %s, symbollayercount: %s' % (symbol, symbol.symbolLayerCount())
    sym={}
    if symbol.symbolLayerCount() > 1:
      QMessageBox.information(self.iface.mainWindow(), "Warning", "Layer '"+layer.name()+"' uses New Symbology, and styles with more the one Symbol Layer, only the first one will be use.")
    sl = symbol.symbolLayer(0)
    slprops = sl.properties()
    #print("symbollayer properties: %s" % slprops)
    # region/polgyons have: color_border / style_border / offset / style / color / width_border
    #  {PyQt4.QtCore.QString('color_border'): PyQt4.QtCore.QString('0,0,0,255'), PyQt4.QtCore.QString('style_border'): PyQt4.QtCore.QString('solid'), PyQt4.QtCore.QString('offset'): PyQt4.QtCore.QString('0,0'), PyQt4.QtCore.QString('style'): PyQt4.QtCore.QString('solid'), PyQt4.QtCore.QString('color'): PyQt4.QtCore.QString('0,0,255,255'), PyQt4.QtCore.QString('width_border'): PyQt4.QtCore.QString('0.26')}
    # markers/points have : color_border / offset / size / color / name / angle:
    #  {PyQt4.QtCore.QString('color_border'): PyQt4.QtCore.QString('0,0,0,255'), PyQt4.QtCore.QString('offset'): PyQt4.QtCore.QString('0,0'), PyQt4.QtCore.QString('size'): PyQt4.QtCore.QString('2'), PyQt4.QtCore.QString('color'): PyQt4.QtCore.QString('255,0,0,255'), PyQt4.QtCore.QString('name'): PyQt4.QtCore.QString('circle'), PyQt4.QtCore.QString('angle'): PyQt4.QtCore.QString('0')}
    # lines have          : color / offset / penstyle / width / use_custom_dash / joinstyle / customdash / capstyle:
    #  {PyQt4.QtCore.QString('color'): PyQt4.QtCore.QString('255,255,0,255'), PyQt4.QtCore.QString('offset'): PyQt4.QtCore.QString('0'), PyQt4.QtCore.QString('penstyle'): PyQt4.QtCore.QString('solid'), PyQt4.QtCore.QString('width'): PyQt4.QtCore.QString('0.5'), PyQt4.QtCore.QString('use_custom_dash'): PyQt4.QtCore.QString('0'), PyQt4.QtCore.QString('joinstyle'): PyQt4.QtCore.QString('bevel'), PyQt4.QtCore.QString('customdash'): PyQt4.QtCore.QString('5;2'), PyQt4.QtCore.QString('capstyle'): PyQt4.QtCore.QString('square')}
    strokekey = 'line_color'
    strokekey2 = 'outline_color'
    colorkey = 'color'
    stylekey = 'style'
    width_borderkey = 'outline_width'
    widthkey = 'width'
    line_width_key = 'line_width'
    if strokekey in slprops:
      stroke = slprops[strokekey]
      sym['stroke'] = self.cleanup_rgb(stroke)
    elif strokekey2 in slprops:
      stroke = str(slprops[strokekey2])
      sym['stroke'] = self.cleanup_rgb(stroke)
    else:
      sym['stroke'] = 'none'
    # fill color: only non line features have fill color, lines have 'none'
    geom = feature.geometry()
    if colorkey in slprops:
      fill = self.cleanup_rgb(slprops[colorkey])
      if QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.GeometryType.LineGeometry:
        sym['stroke'] = self.cleanup_rgb(fill)
      # points have fill and stroke
      sym['fill'] = self.cleanup_rgb(fill)
    # if feature is line OR when there is no brush: set fill to none
    if QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.GeometryType.LineGeometry \
       or (stylekey in slprops and slprops[stylekey] == 'no'):
      sym['fill'] = 'none'
    # pen: in QT pen can be 0
    if width_borderkey in slprops:
      sym['stroke-width'] = str(float(slprops[width_borderkey])*3.779)  # mm to pixels
    elif widthkey in slprops:
      sym['stroke-width'] = str(slprops[widthkey])
    else:
      sym['stroke-width'] = '0.40'
    if line_width_key in slprops:
        sym['stroke-width'] = str(float(slprops[line_width_key])*3.779)  # mm to pixels
    #print(sym)
    return sym

  def writeExtent(self):
    svg = ['<!-- QGIS extent for clipping, eg in Inkscape -->\n<g id="qgisviewbox" inkscape:groupmode="layer" inkscape:label="qgisviewbox" stroke="rgb(255,0,0)" stroke-width="1" fill="none" >\n']
    for ring in self.extentAsPoly.asPolygon():
        svg.append('<path d="M ')
        first = True
        for point in ring:
            pixpoint =  self.w2p(point.x(), point.y(), self.iface.mapCanvas().mapUnitsPerPixel(), self.currentExtent.xMinimum(), self.currentExtent.yMaximum())
            if not first:
                svg.append('L ')
            svg.append((str(pixpoint[0]) + ',' + str(pixpoint[1]) + ' '))
            first = False
        svg.append('" />\n')
    svg.append('</g> <!-- end of viewbox g -->\n')
    return svg

  def writeRaster(self, layer):
    # save visibility of layers
    root = QgsProject.instance().layerTreeRoot()
    visible_tree_layers = []
    layers = root.findLayers()
    for tree_layer in layers:
        if tree_layer.isVisible():
            visible_tree_layers.append(tree_layer)
            tree_layer.setItemVisibilityChecked(False)
            # if tree_layer.layerId() != layer.id():
            #     tree_layer.setItemVisibilityChecked(False)

    # force a refresh... grr all this seems not to work ????
    layer.triggerRepaint(False)
    self.iface.mapCanvas().setCachingEnabled(False)
    self.iface.mapCanvas().clearCache()
    self.iface.mapCanvas().refreshAllLayers()
    self.iface.mapCanvas().redrawAllLayers()
    self.iface.mapCanvas().refresh()

    lyrName = layer.name()
    imgName = lyrName+'.png'
    try:
        imgPath= self.svgFilename[:self.svgFilename.rfind('/')+1]
    except NameError:
        imgPath= self.svgFilename[:self.svgFilename.rfind('/')+1]
    # save image next to svg but put it in Image tag only the local filename
    self.iface.mapCanvas().saveAsImage(imgPath+imgName)
    # <image y="-7.7685061" x="27.115078" id="image3890" xlink:href="nl.png" />
    svg = ['<g id="'+lyrName+'" inkscape:groupmode="layer" inkscape:label="'+lyrName+'">\n'];
    #svg.append('<image y="0" x="0" xlink:href="'+imgPath+imgName+'" />')
    svg.append('<image y="0" x="0" xlink:href="'+imgName+'" />')
    svg.append('</g>') # end of raster layer

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
    svg = ['<text id="'+fid+'" x="'+str(xy[0])+'" y="'+str(xy[1])+'" '+inkscapeLbl+'>'+str(labelTxt)+'</text>\n']
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
    svg.append('<g id="' + fid + '" '+inkscapeLbl+'>\n')
    geom=feature.geometry()
    currentExtent=self.currentExtent
    if QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.GeometryType.PointGeometry:
        if geom.isMultipart():
            multipoint = geom.asMultiPoint()
            for point in multipoint:
              svg.extend(self.point2svg(point, currentExtent))
        else:
            svg.extend(self.point2svg(geom.asPoint(), currentExtent))
    if QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.GeometryType.PolygonGeometry: # 6 = WKBTYPE.WKBMultiPolygon:
        if geom.isMultipart():
            multipolygon = geom.asMultiPolygon() # returns a list
            for polygon in multipolygon:
              svg.extend(self.polygon2svg(feature, polygon, currentExtent))
        else:
            svg.extend(self.polygon2svg(feature, geom.asPolygon(), currentExtent))
    if QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.GeometryType.LineGeometry:
        if geom.isMultipart():
            multiline = geom.asMultiPolyline()  # returns a list
            for line in multiline:
                svg.extend(self.line2svg(feature, line, currentExtent))
        else:
            svg.extend(self.line2svg(feature, geom.asPolyline(), currentExtent))
    svg.append('</g> <!-- end feature g -->\n')
    return svg

  def point2svg(self, point, currentExtent):
    #point = feature.geometry().asPoint()
    xy =  self.w2p(point.x(), point.y(), self.iface.mapCanvas().mapUnitsPerPixel(), self.currentExtent.xMinimum(), self.currentExtent.yMaximum())
    #print(point, xy, point.x(), point.y(), self.iface.mapCanvas().mapUnitsPerPixel(), self.currentExtent.xMinimum(), self.currentExtent.yMaximum())
    # TODO take current extent into account
    svg = ['<circle cx="'+str(xy[0])+'" cy="'+str(xy[1])+'" r="5" />']
    return svg

  def symbolForFeature(self, layer, feature):
      if isinstance(layer.renderer(), QgsCategorizedSymbolRenderer):
          # not sure why, but... we need to do this first....:
          #layer.renderer().rebuildHash()
          return layer.renderer().symbolForValue2(feature[layer.renderer().classAttribute()])[0]
      elif isinstance(layer.renderer(), QgsGraduatedSymbolRenderer):
          return layer.renderer().symbolForValue(feature[layer.renderer().classAttribute()])
      else:
        return layer.renderer().symbolForFeature(feature, QgsRenderContext())

  def line2svg(self, feature, line, currentExtent):
    #print("calling line2svg...")
    linesvg = []
    svg = ''
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

