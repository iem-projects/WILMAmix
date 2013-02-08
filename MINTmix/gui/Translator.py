#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013, IOhannes m zmölnig, IEM

# This file is part of MINTmix
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MINTmix.  If not, see <http://www.gnu.org/licenses/>.

import locale, os
from PySide.QtCore import QTranslator, QLibraryInfo

class Translator:

  def __init__(self, oApp):
    try:
      # Install the appropriate editor translation file
      sLocale = locale.getdefaultlocale()[0]
      oTranslator = QTranslator()
      path=os.path.join('i18n', sLocale)
      if oTranslator.load(path):
        oApp.installTranslator(oTranslator)
        print "translator: OK"
        
##      # Install the appropriate Qt translation file
##      oTranslatorQt = QTranslator()
##      print 'qt_' + sLocale, QLibraryInfo.location(QLibraryInfo.TranslationsPath)
##      if oTranslatorQt.load('qt_' + sLocale, QLibraryInfo.location(QLibraryInfo.TranslationsPath)):
##        oApp.installTranslator(oTranslatorQt)
          
    except Exception, oEx:
      print "translator: ",oEx
      pass
