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
 This script initializes the plugin, making it known to QGIS.
"""
def name():
  return "SimpleSvg"
def description():
  return "Create simple SVG from current view, editable with Inkscape"
def version():
  return "Version 0.6"
def qgisMinimumVersion():
  return "1.0"
def classFactory(iface):
  # load SimpleSvg class from file SimpleSvg
  from SimpleSvg import SimpleSvg
  return SimpleSvg(iface)


