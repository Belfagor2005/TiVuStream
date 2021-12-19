#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
****************************************
*        coded by Lululla              *
*                                      *
*             01/12/2021               *
****************************************
Info http://t.me/tivustream
'''
# from __future__ import print_function
from . import _
# from Components.HTMLComponent import *
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ConfigList import *
from Components.Console import Console as iConsole
from Components.Input import Input
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap, MultiPixmap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.SelectionList import SelectionList
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.ServiceList import ServiceList
from Components.Sources.List import List
from Components.Sources.Progress import Progress
from Components.Sources.Source import Source
from Components.Sources.StaticText import StaticText
from Components.config import *
from Plugins.Extensions.TivuStream.getpics import GridMain
from Plugins.Extensions.TivuStream.getpics import getpics
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.InfoBar import InfoBar
from Screens.InfoBar import MoviePlayer
from Screens.InfoBarGenerics import InfoBarShowHide, InfoBarSubtitleSupport, InfoBarSummarySupport, \
	InfoBarNumberZap, InfoBarMenu, InfoBarEPG, InfoBarSeek, InfoBarMoviePlayerSummarySupport, \
	InfoBarAudioSelection, InfoBarNotifications, InfoBarServiceNotifications
from Screens.InputBox import InputBox
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.PluginBrowser import PluginBrowser
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop, Standby
from Screens.VirtualKeyBoard import VirtualKeyBoard
from ServiceReference import ServiceReference
from Tools.Directories import SCOPE_PLUGINS
from Tools.Directories import resolveFilename, fileExists, copyfile, pathExists
from Tools.Downloader import downloadWithProgress
from Tools.LoadPixmap import LoadPixmap
from enigma import *
from enigma import RT_HALIGN_CENTER, RT_VALIGN_CENTER
from enigma import RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import eListbox, eListboxPythonMultiContent 
from enigma import eTimer
from enigma import ePicLoad, gPixmapPtr
from enigma import gFont
from enigma import eServiceCenter
from enigma import eServiceReference
from enigma import eSize, ePicLoad
from enigma import iServiceInformation
from enigma import loadPNG 
from enigma import quitMainloop
from enigma import iPlayableService 
from os.path import splitext
from sys import version_info
from twisted.web.client import downloadPage, getPage, error
from xml.dom import Node, minidom
import base64
import glob
import os
import random
import re
import shutil
import ssl
import sys
import time

import six
try:
    from Plugins.Extensions.TivuStream.Utils import *
except:
    from . import Utils

PY3 = sys.version_info.major >= 3
print('Py3: ',PY3)
if PY3:
        import http.client
        from http.client import HTTPConnection, CannotSendRequest, BadStatusLine, HTTPException
        from urllib.error import URLError, HTTPError
        from urllib.request import urlopen, Request
        from urllib.parse import urlparse
        from urllib.parse import parse_qs, urlencode, quote
        unicode = str; unichr = chr; long = int
        PY3 = True
else:
# if os.path.exists('/usr/lib/python2.7'):
        from httplib import HTTPConnection, CannotSendRequest, BadStatusLine, HTTPException
        from urllib2 import urlopen, Request, URLError, HTTPError
        from urlparse import urlparse, parse_qs
        from urllib import urlencode, quote
        import httplib
        import six
try:
    import io
except:
    import StringIO
try:
    import http.cookiejar
except:
    import cookielib
try:
    import httplib
except:
    import http.client

if sys.version_info >= (2, 7, 9):
	try:
		import ssl
		sslContext = ssl._create_unverified_context()
	except:
		sslContext = None
# try:
    # _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
    # pass
# else:
    # ssl._create_default_https_context = _create_unverified_https_context

try:
    from OpenSSL import SSL
    from twisted.internet import ssl
    from twisted.internet._sslverify import ClientTLSOptions
    sslverify = True
except:
    sslverify = False

if sslverify:
    class SNIFactory(ssl.ClientContextFactory):
        def __init__(self, hostname=None):
            self.hostname = hostname

        def getContext(self):
            ctx = self._contextFactory(self.method)
            if self.hostname:
                ClientTLSOptions(self.hostname, ctx)
            return ctx

def ssl_urlopen(url):
	if sslContext:
		return urlopen(url, context=sslContext)
	else:
		return urlopen(url)

try:
	from Plugins.Extensions.tmdb import tmdb
	is_tmdb = True
except Exception:
	is_tmdb = False

try:
	from Plugins.Extensions.IMDb.plugin import main as imdb
	is_imdb = True
except Exception:
	is_imdb = False

#changelog 18.12.2021
currversion = '3.0'
Version = currversion + ' - 12.12.2021'
title_plug = '..:: TivuStream Revolution V. %s ::..' % Version
name_plug = 'TivuStream Revolution'
Credits = 'Info http://t.me/tivustream'
Maintainer2 = 'Maintener @Lululla'
dir_enigma2 = '/etc/enigma2/'
service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/".format('TivuStream'))
res_plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/".format('TivuStream'))
#================
# def add_skin_font():
    # font_path = plugin_path + 'res/fonts/'
    # addFont(font_path + 'verdana_r.ttf', 'OpenFont1', 100, 1)
    # addFont(font_path + 'verdana_r.ttf', 'OpenFont2', 100, 1)

modechoices = [
                ("4097", _("ServiceMp3(4097)")),
                ("1", _("Hardware(1)")),
                ]

if os.path.exists("/usr/bin/gstplayer"):
    modechoices.append(("5001", _("Gstreamer(5001)")))
if os.path.exists("/usr/bin/exteplayer3"):
    modechoices.append(("5002", _("Exteplayer3(5002)")))
if os.path.exists("/usr/sbin/streamlinksrv"):
    modechoices.append(("5002", _("Streamlink(5002)")))
if os.path.exists("/usr/bin/apt-get"):
    modechoices.append(("8193", _("eServiceUri(8193)")))

sessions = []
config.plugins.TivuStream                        = ConfigSubsection()
config.plugins.TivuStream.autoupd                = ConfigYesNo(default=True)
config.plugins.TivuStream.pthm3uf                = ConfigDirectory(default='/media/hdd/movie')
try:
    from Components.UsageConfig import defaultMoviePath
    downloadpath = defaultMoviePath()
    config.plugins.TivuStream.pthm3uf  = ConfigDirectory(default=downloadpath)
except:
    if os.path.exists("/usr/bin/apt-get"):
        config.plugins.TivuStream.pthm3uf  = ConfigDirectory(default='/media/hdd/movie')
# config.plugins.TivuStream.code                   = ConfigNumber(default = 1234)
config.plugins.TivuStream.code                   = ConfigText(default = "1234")
config.plugins.TivuStream.bouquettop             = ConfigSelection(default='Bottom', choices=['Bottom', 'Top'])
config.plugins.TivuStream.server                 = ConfigSelection(default='CORVOBOYS', choices=['PATBUWEB', 'CORVOBOYS'])
config.plugins.TivuStream.services               = ConfigSelection(default='4097', choices=modechoices)
config.plugins.TivuStream.cachefold              = ConfigDirectory(default='/media/hdd/')
config.plugins.TivuStream.strtext                = ConfigYesNo(default=True)
config.plugins.TivuStream.strtmain               = ConfigYesNo(default=True)
config.plugins.TivuStream.thumb                  = ConfigYesNo(default=False)
config.plugins.TivuStream.thumbpic               = ConfigYesNo(default=False)

global Path_Movies
Path_Movies             = str(config.plugins.TivuStream.pthm3uf.value) + "/"
if Path_Movies.endswith("\/\/") is True:
    Path_Movies = Path_Movies[:-1]
print('patch movies: ', Path_Movies)

tvstrvl = config.plugins.TivuStream.cachefold.value + "tivustream"
tmpfold = config.plugins.TivuStream.cachefold.value + "tivustream/tmp"
picfold = config.plugins.TivuStream.cachefold.value + "tivustream/pic"

if not os.path.exists(tvstrvl):
    os.system("mkdir " + tvstrvl)
if not os.path.exists(tmpfold):
    os.system("mkdir " + tmpfold)
if not os.path.exists(picfold):
    os.system("mkdir " + picfold)

def server_ref():
    global server, host, upd_fr_txt, upd_nt_txt
    server = ''
    host = ''
    TEST1 = 'aHR0cHM6Ly9wYXRidXdlYi5jb20='
    ServerS1 = b64decoder(TEST1)
    data_s1 = 'L2lwdHYv' #
    FTP_1 = b64decoder(data_s1)
    TEST2 = 'aHR0cDovL2NvcnZvbmUuYWx0ZXJ2aXN0YS5vcmc='
    ServerS2 = b64decoder(TEST2)
    data_s2 = 'L2lwdHYv' #
    FTP_2 = b64decoder(data_s2)
    if config.plugins.TivuStream.server.value == 'PATBUWEB' :
        host = ServerS1
        server = ServerS1 + FTP_1
    else:
        host = ServerS2
        server = ServerS2 + FTP_2
    upd_fr_txt = ('%splugin/update.txt' % server)
    # upd_nt_txt = ('%se2liste/list.txt' % server)
    tex = 'aHR0cDovL3RpdnVzdHJlYW0ud2Vic2l0ZS9pb3MvbGlzdC50eHQ='
    upd_nt_txt = b64decoder(tex)
    return server, host, upd_fr_txt
server_ref()
nnewtv = 'aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocA=='
servernew = b64decoder(nnewtv)
nnewm3u = 'aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbC5waHA/cD01JnVhPVRpVnVTdHJlYW0mZj0x'
servernewm3u = b64decoder(nnewm3u)
estm3u = 'aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL2ZoLnBocA=='
m3uest = b64decoder(estm3u)

global pngori, skin_path
nasarandom = "http://patbuweb.com/back-tvstream/"
imgjpg = ("nasa1.jpg", "nasa2.jpg", "nasa3.jpg")
pngori = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/nasa3.jpg".format('TivuStream'))
png = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/setting.png".format('TivuStream'))
pngx = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/setting2.png".format('TivuStream'))
if isFHD():
    skin_path= resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/skins/fhd/".format('TivuStream'))
else:
    skin_path= resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/skins/hd/".format('TivuStream'))
if DreamOS():
    skin_path=skin_path + 'dreamOs/'

# class tvList(MenuList):
    # def __init__(self, list):
        # MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        # self.l.setFont(0, gFont('OpenFont2', 20))
        # self.l.setFont(1, gFont('OpenFont2', 22))
        # self.l.setFont(2, gFont('OpenFont2', 24))
        # self.l.setFont(3, gFont('OpenFont2', 26))
        # self.l.setFont(4, gFont('OpenFont2', 28))
        # self.l.setFont(5, gFont('OpenFont2', 30))
        # self.l.setFont(6, gFont('OpenFont2', 32))
        # self.l.setFont(7, gFont('OpenFont2', 34))
        # self.l.setFont(8, gFont('OpenFont2', 36))
        # self.l.setFont(9, gFont('OpenFont2', 40))
        # if isFHD():
            # self.l.setItemHeight(50)
        # else:
            # self.l.setItemHeight(50)


class tvList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if isFHD():
            self.l.setItemHeight(50)
            textfont=int(34)
            self.l.setFont(0, gFont('Regular', textfont))
        else:
            self.l.setItemHeight(50)
            textfont=int(22)
            self.l.setFont(0, gFont('Regular', textfont))

def tvListEntry(name,png):
    res = [name]
    png = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/setting.png".format('TivuStream'))
    if isFHD():
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 10), size=(34, 25), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1900, 50), font=0, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 10), size=(34, 25), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=0, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res
    
def m3ulistEntry(download):
    res = [download]
    white = 16777215
    yellow = 16776960
    green = 3828297
    col = 16777215
    backcol = 0
    blue = 4282611429
    pngx = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/setting2.png".format('TivuStream'))
    if isFHD():
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 10), size=(34, 25), png=loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1900, 50), font=0, text=download, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 10), size=(34, 25), png=loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=0, text=download, color = 0xa6d1fe, flags=RT_HALIGN_LEFT| RT_VALIGN_CENTER)) 
    return res

def m3ulist(data, list):
    icount = 0
    mlist = []
    for line in data:
        name = data[icount]
        mlist.append(m3ulistEntry(name))
        icount = icount + 1
    list.setList(mlist)

class TvInfoBarShowHide():
    """ InfoBar show/hide control, accepts toggleShow and hide actions, might start
    fancy animations. """
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3

    def __init__(self):
        self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"], {"toggleShow": self.toggleShow,
         "hide": self.hide}, 0)
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        self.hideTimer.start(5000, True)
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(self.doTimerHide)
        except:
            self.hideTimer.callback.append(self.doTimerHide)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

    def serviceStarted(self):
        if self.execing:
            if config.usage.show_infobar_on_zap.value:
                self.doShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            idx = config.usage.infobar_timeout.index
            if idx:
                self.hideTimer.start(idx * 1500, True)

    def __onHide(self):
        self.__state = self.STATE_HIDDEN

    def doShow(self):
        self.show()
        self.startHideTimer()

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()

    def toggleShow(self):
        if self.__state == self.STATE_SHOWN:
            self.hide()
            self.hideTimer.stop()
        elif self.__state == self.STATE_HIDDEN:
            self.show()

    def lockShow(self):
        self.__locked = self.__locked + 1
        if self.execing:
            self.show()
            self.hideTimer.stop()

    def unlockShow(self):
        self.__locked = self.__locked - 1
        if self.execing:
            self.startHideTimer()

    def debug(obj, text = ""):
        print(text + " %s\n" % obj)




Panel_list = [
 ('LIVE TUTTI'),
 ('TOP ITALIA'),
 ('SPORT ITALIA'),
 ('SPORT LIVE'),
 ('SPORT ESTERI'),
 ('MUSICA'),
 ('NEWS'),
 ('ESTERO'),
 # ('ESTERO2'),
 ('REGIONALI'),
 ('RELAX'),

 ('MOVIE TUTTI'),
 ('SERIE'),
 ('SERIE TV: 0-9'),
 ('SERIE TV: A-E'),
 ('SERIE TV: F-K'),
 ('SERIE TV: L-R'),
 ('SERIE TV: S-Z'),
 ('FILM'),
 ('FILM RECENTI'),
 ('FILM: 0-9'),
 ('FILM: A-F'),
 ('FILM: G-L'),
 ('FILM: M-R'),
 ('FILM: S-Z'),
 ('FILM IN VERSIONE ORIGINALE'),

 ('RADIO TUTTI'),
 ('RADIO ITALIA'),
 ('RADIO INT'),
 ('DASH RADIO'),

 ('LIVE XXX'),
 ('MOVIE XXX')]

class OpenScript(Screen):
    def __init__(self, session):
        self.session = session
        skin = skin_path + '/OpenScript.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self.setup_title = _('Channel List')
        self['list'] = tvList([])
        self.icount = 0
        server_ref()
        # tivustream = ''
        # estero = ''
        self['listUpdate'] = Label()
        self['title'] = Label(_(title_plug))
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['infoc2'] = Label('%s' % Credits)
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Reload Bouquet'))
        self['key_yellow'] = Button(_('Delete Bouquet'))
        self["key_blue"] = Button(_("Player"))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'MenuActions', 'TimerEditActions'],
         {'ok': self.messagerun,
         'file': self.M3uPlay,
         'menu': self.scsetup,
         'red': self.close,
         'green': self.messagereload,
         'info': self.close,
         'yellow': self.messagedellist,
         'blue': self.M3uPlay,
         'back': self.close,
         'cancel': self.close}, -1)
        self.onFirstExecBegin.append(self.checkList)
        self.onLayoutFinish.append(self.updateMenuList)

    def checkList(self):
        OnclearMem()
        self.icount = 0
        self['listUpdate'].setText(_('Check List Update wait please...'))
        self.timer = eTimer()
        self.timer.start(500, 1)
        if DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.read)
        else:
            self.timer.callback.append(self.read)

    def read(self):
        try:
            destr = plugin_path + 'list.txt'
            # onserver2 = six.ensure_str(upd_nt_txt)
            onserver2 = upd_nt_txt
            with open(destr, 'w') as f:
                content = ReadUrl2(onserver2)
                # content = six.ensure_str(content)
                f.write(content)
            self['listUpdate'].setText(content)
        except Exception as ex:
            print(ex)

    def updateMenuList(self):
        self.menu_list = []
        for x in self.menu_list:
                del self.menu_list[0]
        list = []
        idx = 0
        png = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/setting.png".format('TivuStream'))
        for x in Panel_list:
            list.append(tvListEntry(x, png))
            self.menu_list.append(x)
            idx += 1
        self['list'].setList(list)

    def okRun(self, result):
        if result:
            self.keyNumberGlobalCB(self['list'].getSelectedIndex())

    def keyNumberGlobalCB(self, idx):
        global namex
        namex = ''
        sel = self.menu_list[idx]
        if sel == ("LIVE TUTTI"):
                namex = "livetutti"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTEmdD0w"
        elif sel == ("TOP ITALIA"):
                namex = "topitalia"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTEmdD0x"
        elif sel == ("SPORT ITALIA"):
                namex = "sportitalia"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTEmdD0y"
        elif sel == ("SPORT LIVE"):
                namex = "sportlive"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTEmdD0z"
        elif sel == ("SPORT ESTERI"):
                namex = "sportesteri"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTEmdD00"
        elif sel == ("MUSICA"):
                namex = "musica"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTEmdD01"
        elif sel == ("NEWS"):
                namex = "news"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTEmdD02"
        elif sel == ("ESTERO"):
                namex = "estero"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTEmdD03"
        elif sel == ("REGIONALI"):
                namex = "regionali"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTEmdD04"
        elif sel == ("RELAX"):
                namex = "relax"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTEmdD05"

        elif sel == ("MOVIE TUTTI"):
                namex = "movietutti"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0w"
        elif sel == ("SERIE"):
                namex = "serie"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0xMA=="
        elif sel == ("SERIE TV: 0-9"):
                namex = "serietv09"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0xMQ=="
        elif sel == ("SERIE TV: A-E"):
                namex = "serietvae"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0xMg=="
        elif sel == ("SERIE TV: F-K"):
                namex = "serietvfk"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0xMw=="
        elif sel == ("SERIE TV: L-R"):
                namex = "serietvlr"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0xNA=="
        elif sel == ("SERIE TV: S-Z"):
                namex = "serietvsz"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0xNQ=="
        elif sel == ("FILM"):
                namex = "film"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0yMA=="
        elif sel == ("FILM RECENTI"):
                namex = "filmrecenti"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0yMQ=="
        elif sel == ("FILM: 0-9"):
                namex = "film09"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0yMg=="
        elif sel == ("FILM: A-F"):
                namex = "filmaf"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0yMw=="
        elif sel == ("FILM: G-L"):
                namex = "filmgl"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0yNA=="
        elif sel == ("FILM: M-R"):
                namex = "filmmr"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0yNQ=="
        elif sel == ("FILM: S-Z"):
                namex = "filmsz"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0yNg=="
        elif sel == ("FILM IN VERSIONE ORIGINALE"):
                namex = "movieoriginal"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTImdD0yNw=="

        elif sel == ("RADIO TUTTI"):
                namex = "radiotutti"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTMmdD0w"
        elif sel == ("RADIO ITALIA"):
                namex = "radioitalia"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTMmdD0x"
        elif sel == ("RADIO INT"):
                namex = "radioint"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTMmdD0y"
        elif sel == ("DASH RADIO"):
                namex = "dashradio"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTMmdD0z"

        elif sel == ("LIVE XXX"):
                namex = "livexxx"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTU="
        elif sel == ("MOVIE XXX"):
                namex = "moviexxx"
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocD9wPTQ="

        elif sel == ("="):
                namex = "=="
                lnk = "aHR0cDovL3BhdGJ1d2ViLmNvbS9waHBfZmlsdGVyL3RzbEVuLnBocA=="
        else:
                self.mbox = self.session.open(openMessageBox, _('Bouquet not installed'), openMessageBox.TYPE_ERROR, timeout=4)
                return
        self.instal_listTv(namex, lnk)


    def instal_listTv(self, namex, lnk):
        name = namex
        lnk = b64decoder(lnk)
        print('link  : ', lnk)
        pin = 2808
        pin2 = str(config.plugins.TivuStream.code.value)
        bouquet = 'bouquets.tv'
        groupname = 'userbouquet.tivustream.tv'
        bouquetTvString = '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + str(groupname) + '" ORDER BY bouquet\n'
        dirgroupname = ('/etc/enigma2/%s' % groupname)
        if name == '==' :
            self.mbox = self.session.open(openMessageBox, _('CONNECTION ERROR OR UNKNOWN'), openMessageBox.TYPE_ERROR, timeout=4)
            return
        else:
            if name == 'livexxx' or name == 'moviexxx':
                if str(config.plugins.TivuStream.code.value) != str(pin):
                    self.mbox = self.session.open(openMessageBox, _('You are not allowed!'), openMessageBox.TYPE_INFO, timeout=8)
                    return
                else:
                    print('pass xxx')
                    pass
            if 'radio' in name :
                bqtname = 'subbouquet.tivustream.%s.radio' % name
                number = '2'
            else:
                bqtname = 'subbouquet.tivustream.%s.tv' % name
                number = '1'
            in_bouquets = 0
            linetv =0
            if os.path.exists('/etc/enigma2/%s' % bqtname):
                os.remove('/etc/enigma2/%s' % bqtname)
            if not os.path.exists('/etc/enigma2/userbouquet.tivustream.tv'):
                filename = '/etc/enigma2/userbouquet.tivustream.tv'
                with open(filename, 'a+') as f:
                    nameString = "#NAME tivustream.com"
                    if nameString not in f:
                        f.write(nameString + '\r\n')
            os.system('chmod 0644 /etc/enigma2/userbouquet.tivustream.tv' )
            namebqt = ('/etc/enigma2/%s' % bqtname)
            try:
                with open(namebqt, 'w') as f:
                    content = ReadUrl2(lnk)
                    # content = six.ensure_str(content)
                    print('Resp 2: ', content)
                    f.write(content)
                    os.system('sleep 5')
                    f.close()
            except Exception as ex:
                print(ex)
            self.mbox = self.session.open(openMessageBox, _('Check out the favorites list ...'), openMessageBox.TYPE_INFO, timeout=5)
            x = open ('/etc/enigma2/bouquets.tv', 'r')
            for line in x:
                if bouquetTvString in line:
                    linetv = 1
            if linetv == 0:
                new_bouquet = open('/etc/enigma2/new_bouquets.tv', 'w')
                file_read = open('/etc/enigma2/%s' % bouquet).readlines()
                if config.plugins.TivuStream.bouquettop.value == 'Top':
                    new_bouquet.write('#NAME User - bouquets (TV)\n')
                    new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.terrestrial.tv" ORDER BY bouquet\n')
                    for line in file_read:
                        if line.startswith("#NAME"):
                            continue
                        new_bouquet.write(line)
                    new_bouquet.close()
                elif config.plugins.TivuStream.bouquettop.value == 'Bottom':
                    for line in file_read:
                        new_bouquet.write(line)
                    new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + groupname + '" ORDER BY bouquet\n')
                    new_bouquet.close()
                os.system('cp -rf /etc/enigma2/bouquets.tv /etc/enigma2/backup_bouquets.tv')
                os.system('mv -f /etc/enigma2/new_bouquets.tv /etc/enigma2/bouquets.tv')
                os.system('chmod 0644 /etc/enigma2/%s' %groupname )
            z = open(dirgroupname)
            for line in z:
                if bqtname in line:
                    in_bouquets = 1
            if in_bouquets == 0:
                with open(dirgroupname, 'a+' ) as f:
                    bouquetTvString = ('#SERVICE 1:7:%s:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % (number, bqtname))
                    if bouquetTvString not in f:
                        f.write(bouquetTvString)
                        f.close()
            self.mbox = self.session.open(openMessageBox, _('Shuffle Favorite List in Progress') + '\n' + _('Wait please ...'), openMessageBox.TYPE_INFO, timeout=5)
            eDVBDB.getInstance().reloadServicelist()
            eDVBDB.getInstance().reloadBouquets()
            return

    def messagerun(self):
        self.session.openWithCallback(self.messagerun2, openMessageBox, _('Install the selected list?'), openMessageBox.TYPE_YESNO)

    def messagerun2(self, result):
        if result:
            self.session.openWithCallback(self.okRun, openMessageBox, _('Installation in progress') + '\n' + _('Wait please ...'), openMessageBox.TYPE_INFO, timeout=3)

    def messagereload(self):
        self.session.openWithCallback(self.reloadSettings, openMessageBox, _('Shuffle Favorite List in Progress') + '\n' + _('Wait please ...'), openMessageBox.TYPE_INFO, timeout=5)

    def reloadSettings(self, result):
        if result:
           ReloadBouquets()

    def messagedellist(self):
        self.session.openWithCallback(self.deletelist, openMessageBox, _('ATTENTION') + ':\n' + _('Delete TiVuStream Revolution channel lists') + ' ?', openMessageBox.TYPE_YESNO)

    def deletelist(self, result):
        if result:
            for file in os.listdir('/etc/enigma2/'):
                if file.startswith('userbouquet.tivustream') or file.startswith('subbouquet.tivustream'):
                    file = '/etc/enigma2/' + file
                    if os.path.exists(file):
                        os.remove(file)
                        os.system("sed -i '/userbouquet.tivustream/d' /etc/enigma2/bouquets.tv")
                    radio = '/etc/enigma2/subbouquet.tivustream_radio.radio'
                    if os.path.exists(radio):
                        os.remove(radio)
                        os.system("sed -i '/subbouquet.tivustream/d' /etc/enigma2/bouquets.radio")
            self.mbox = self.session.open(openMessageBox, _('TiVuStream Revolution channel lists successfully deleted'), openMessageBox.TYPE_INFO, timeout=4)
            ReloadBouquets()

    def M3uPlay(self):
        tivustream = 'tivustream'
        self.session.open(OpenM3u)

    def scsetup(self):
        self.session.open(OpenConfig)

class OpenM3u(Screen):
    def __init__(self, session):
        self.session = session
        skin = skin_path + '/OpenM3u.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        # f.close()
        Screen.__init__(self, session)
        self.list = []
        self['list'] = tvList([])
        global srefInit
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        srefInit = self.initialservice
        self['title'] = Label(_(title_plug))
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['infoc2'] = Label('%s' % Credits)
        self['path'] = Label(_('Folder path %s') % Path_Movies)
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Convert ExtePlayer3'))
        self['key_yellow'] = Button(_('Convert Gstreamer'))
        self["key_blue"] = Button(_("Remove"))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'MenuActions', 'TimerEditActions'],
        {
         'file': self.crea_bouquet5002,
         'green': self.crea_bouquet5002,
         'blue': self.message1,
         'yellow': self.crea_bouquet,
         'cancel': self.cancel,
         'ok': self.runList}, -2)
        self.convert = False
        self.name = Path_Movies
        # self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        try:
            destx = Path_Movies + 'tivustream.m3u'
            with open(destx, 'w') as f:
                content = ReadUrl2(servernewm3u)
                content = six.ensure_str(content)
                print('Resp 1: ', content)
                f.write(content)
                os.system('sleep 5')
                f.close()
        except Exception as ex:
            print(ex)
            print('Exception exit : ', ex)
        self.onLayoutFinish.append(self.openList)

    def scsetup(self):
        self.session.openWithCallback(self.close, OpenConfig)

    def openList(self):
        self.names = []
        self.Movies = []
        path = self.name
        AA = ['.m3u']
        for root, dirs, files in os.walk(path):
            for name in files:
                for x in AA:
                    if not x in name:
                        continue
                    self.names.append(name)
                    self.Movies.append(root +'/'+name)
        pass
        m3ulist(self.names, self['list'])

    def runList(self):
        idx = self["list"].getSelectionIndex()
        namem3u = self.names[idx]
        urlm3u = self.Movies[idx]
        path = urlparse(urlm3u).path
        ext = splitext(path)[1]
        if idx == -1 or None:
            return
        else:
            name = path
            if '.m3u' in name :
                self.session.open(M3uPlay, name)
                return
            else:
                return

    def message1(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            self.session.openWithCallback(self.callMyMsg1, openMessageBox, _("Do you want to remove?"), openMessageBox.TYPE_YESNO)

    def callMyMsg1(self, result):
        if result:
            idx = self['list'].getSelectionIndex()
            path = self.Movies[idx]
            dom = path
            if fileExists(dom):
                os.remove(dom)
            self.session.open(openMessageBox, dom +' has been successfully deleted\nwait time to refresh the list...', openMessageBox.TYPE_INFO, timeout=5)
            del self.Movies[idx]
            del self.names[idx]
            self.onShown.append(self.openList)

    def crea_bouquet(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            self.create_bouquet()
            return

    def crea_bouquet5002(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            self.create_bouquet5002()
            return

    def create_bouquet5002(self):
        idx = self['list'].getSelectionIndex()
        self.convert = True
        name = self.names[idx]
        pth = Path_Movies #self.name
        if not os.path.exists(pth):
            self.mbox = self.session.open(openMessageBox, _('Check in your Config Plugin - Path Movie'), openMessageBox.TYPE_INFO, timeout=5)
            return
        bqtname = 'userbouquet.%s.tv' % name
        desk_tmp = ''
        in_bouquets = 0
        if os.path.isfile('/etc/enigma2/%s' % bqtname):
            os.remove('/etc/enigma2/%s' % bqtname)
        with open('/etc/enigma2/%s' % bqtname, 'w') as outfile:
            outfile.write('#NAME %s\r\n' % name.capitalize())
            for line in open(pth + '%s' % name):
                if line.startswith('http://') or line.startswith('https'):
                    outfile.write('#SERVICE 5002:0:1:1:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                    outfile.write('#DESCRIPTION %s' % desk_tmp)
                elif line.startswith('#EXTINF'):
                    desk_tmp = '%s' % line.split(',')[-1]
                elif '<stream_url><![CDATA' in line:
                    outfile.write('#SERVICE 5002:0:1:1:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
                    outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                elif '<title>' in line:
                    if '<![CDATA[' in line:
                        desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                    else:
                        desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]
            outfile.close()
        self.mbox = self.session.open(openMessageBox, _('Check out the favorites list ...'), openMessageBox.TYPE_INFO, timeout=5)
        if os.path.isfile('/etc/enigma2/bouquets.tv'):
            for line in open('/etc/enigma2/bouquets.tv'):
                if bqtname in line:
                    in_bouquets = 1
            if in_bouquets == 0:
                if os.path.isfile('/etc/enigma2/%s' % bqtname) and os.path.isfile('/etc/enigma2/bouquets.tv'):
                    remove_line('/etc/enigma2/bouquets.tv', bqtname)
                    with open('/etc/enigma2/bouquets.tv', 'a') as outfile:
                        outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % bqtname)
                        outfile.close()
        self.mbox = self.session.open(openMessageBox, _('Shuffle Favorite List in Progress') + '\n' + _('Wait please ...'), openMessageBox.TYPE_INFO, timeout=5)
        ReloadBouquets()

    def create_bouquet(self):
        idx = self['list'].getSelectionIndex()
        self.convert = True
        name = self.names[idx]
        pth = Path_Movies #self.name
        if not os.path.exists(pth):
            self.mbox = self.session.open(openMessageBox, _('Check in your Config Plugin - Path Movie'), openMessageBox.TYPE_INFO, timeout=5)
            return
        bqtname = 'userbouquet.%s.tv' % name
        # self.iConsole = iConsole()
        desk_tmp = ''
        in_bouquets = 0
        if os.path.isfile('/etc/enigma2/%s' % bqtname):
                os.remove('/etc/enigma2/%s' % bqtname)
        with open('/etc/enigma2/%s' % bqtname, 'w') as outfile:
            outfile.write('#NAME %s\r\n' % name.capitalize())
            for line in open(pth + '%s' % name):
                if line.startswith('http://') or line.startswith('https'):
                    outfile.write('#SERVICE 4097:0:1:1:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                    outfile.write('#DESCRIPTION %s' % desk_tmp)
                elif line.startswith('#EXTINF'):
                    desk_tmp = '%s' % line.split(',')[-1]
                elif '<stream_url><![CDATA' in line:
                    outfile.write('#SERVICE 4097:0:1:1:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
                    outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                elif '<title>' in line:
                    if '<![CDATA[' in line:
                        desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                    else:
                        desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]
            outfile.close()
        self.mbox = self.session.open(openMessageBox, _('Check out the favorites list ...'), openMessageBox.TYPE_INFO, timeout=5)
        if os.path.isfile('/etc/enigma2/bouquets.tv'):
            for line in open('/etc/enigma2/bouquets.tv'):
                if bqtname in line:
                    in_bouquets = 1

            if in_bouquets == 0:
                if os.path.isfile('/etc/enigma2/%s' % bqtname) and os.path.isfile('/etc/enigma2/bouquets.tv'):
                    remove_line('/etc/enigma2/bouquets.tv', bqtname)
                    with open('/etc/enigma2/bouquets.tv', 'a') as outfile:
                        outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % bqtname)
                        outfile.close()
        self.mbox = self.session.open(openMessageBox, _('Shuffle Favorite List in Progress') + '\n' + _('Wait please ...'), openMessageBox.TYPE_INFO, timeout=5)
        ReloadBouquets()

    def cancel(self):
        if self.convert == False:
            self.close()
        else:
            self.close()

class M3uPlay(Screen):
    def __init__(self, session, name):
        self.session = session
        skin = skin_path + '/M3uPlay.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        # f.close()
        Screen.__init__(self, session)
        self.list = []
        self['list'] = tvList([])
        self['title'] = Label(_(title_plug))
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['infoc2'] = Label('%s' % Credits)
        service = config.plugins.TivuStream.services.value
        self['service'] = Label(_('Service Reference used %s') % service)
        self['live'] = Label('')
        self['live'].setText('')
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Download'))
        self['key_yellow'] = Button(_('Add Stream to Bouquet'))
        self["key_blue"] = Button(_("Search"))
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.pin = False
        global search_ok
        self.search = ''
        search_ok = False
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'TimerEditActions', 'InfobarInstantRecord'], {'red': self.cancel,
         'green': self.runRec,
         'cancel': self.cancel,
         'yellow': self.AdjUrlFavo,
         "blue": self.search_m3u,
         "rec": self.runRec,
         "instantRecord": self.runRec,
         "ShortRecord": self.runRec,
         'ok': self.runChannel}, -2)
        self.name = name
        # self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.playList)

    def search_m3u(self):
        text = ''
        self.session.openWithCallback(
            self.filterM3u,
            VirtualKeyBoard,
            title = _("Filter this category..."),
            text=self.search)

    def filterM3u(self, result):
        if result:
            self.names = []
            self.urls = []
            self.pics = []
            pic = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/default.png".format('TivuStream'))
            search = result
            try:
                if fileExists(self.name):
                    f1 = open(self.name, "r+")
                    fpage = f1.read()
                    ##EXTINF:-1 group-title="SERIE TV: A-E" tvg-logo="https://patbuweb.com/tivustream/logos/logo.png",[COLOR red]-- UNDER MAINTENANCE --[/COLOR]
                    ##EXTINF:-1 tvg-ID="Rai 1 HD" tvg-name="Rai 1 HD" tvg-logo="" group-title="Top Italia",Rai 1 HD
                    ##EXTINF:-1,Primafila 1
                    regexcat = "EXTINF.*?,(.*?)\\n(.*?)\\n"
                    # if 'tvg-logo' in fpage:
                        # print('Tvg-logo in fpage is True1 ---')
                        # regexcat = 'EXTINF.*?tvg-logo="(.*?)".*?,(.*?)\\n(.*?)\\n'
                    match = re.compile(regexcat, re.DOTALL).findall(fpage)
                    for  name, url in match:
                        if str(search).lower() in name.lower():
                            global search_ok
                            search_ok = True
                            url = url.replace(" ", "")
                            url = url.replace("\\n", "")
                            # if pic:
                               # pic = pic
                            self.names.append(name)
                            self.urls.append(url)
                            self.pics.append(pic)
                    if search_ok == True:
                        m3ulist(self.names, self["list"])
                        self["live"].setText('N.' + str(len(self.names)) + " Stream")
                        search_ok = False
                        self.playList()
            except:
                pass
        else:
            self.playList()

    def runRec(self):
        global urlm3u, namem3u
        idx = self["list"].getSelectionIndex()
        namem3u = self.names[idx]
        urlm3u = self.urls[idx]
        if idx == -1 or None:
            return
        if self.downloading == True:
            self.session.open(openMessageBox, _('You are already downloading!!!'), openMessageBox.TYPE_INFO, timeout=5)
        else:
            if '.mp4' in urlm3u or '.mkv' in urlm3u or '.flv' in urlm3u or '.avi' in urlm3u :
                self.downloading = True
                self.session.openWithCallback(self.download_m3u, openMessageBox, _("DOWNLOAD VIDEO?" ) , type=openMessageBox.TYPE_YESNO, timeout = 10, default = False)
            else:
                self.downloading = False
                self.session.open(openMessageBox, _('Only VOD Movie allowed or not .ext Filtered!!!'), openMessageBox.TYPE_INFO, timeout=5)

    def download_m3u(self, result):
        if result:
            global in_tmp
            OnclearMem()
            if self.downloading == True:
                selection = str(self['list'].getCurrent()) ######?????????
                idx = self["list"].getSelectionIndex()
                namem3u = self.names[idx]
                urlm3u = self.urls[idx]
                path = urlparse(urlm3u).path
                ext = splitext(path)[1]
                fileTitle = re.sub(r'[\<\>\:\"\/\\\|\?\*\[\]]', '_', namem3u)
                fileTitle = re.sub(r' ', '_', fileTitle)
                fileTitle = re.sub(r'_+', '_', fileTitle)
                fileTitle = fileTitle.replace("(", "_").replace(")", "_").replace("#", "").replace("+", "_").replace("\'", "_").replace("'", "_").replace("!", "_").replace("&", "_")
                fileTitle = fileTitle.lower() + ext
                in_tmp = Path_Movies + fileTitle
                self.download = downloadWithProgress(urlm3u, in_tmp)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.check).addErrback(self.showError)
            else:
                self.downloading = False
                self.session.open(openMessageBox, _('Download Failed!!!'), openMessageBox.TYPE_INFO, timeout=5)
                pass

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def check(self, fplug):
        OnclearMem()
        checkfile = in_tmp
        if os.path.exists(checkfile):
            self.downloading = False
            self['progresstext'].text = ''
            self.progclear = 0
            self['progress'].setValue(self.progclear)
            self["progress"].hide()

    def showError(self, error):
        OnclearMem()
        self.downloading = False
        self.session.open(openMessageBox, _('Download Failed!!!'), openMessageBox.TYPE_INFO, timeout=5)

    def playList(self):
        global search_ok
        search_ok = False
        self.names = []
        self.urls = []
        self.pics = []
        pic = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/default.png".format('TivuStream'))
        
        try:
            if fileExists(self.name):
                f1 = open(self.name, 'r+')
                fpage = f1.read()
                # fpage.seek(0)

                if "#EXTM3U" and 'tvg-logo' in fpage:
                    print('tvg-logo in fpage: True')
                    regexcat = 'EXTINF.*?tvg-logo="(.*?)".*?,(.*?)\\n(.*?)\\n'
                    match = re.compile(regexcat, re.DOTALL).findall(fpage)
                    for pic, name, url in match:
                            url = url.replace(' ', '')
                            url = url.replace('\\n', '')
                            # # url = url.replace('https', 'http')
                            # if pic:
                            pic = pic
                            self.names.append(name)
                            self.urls.append(url)
                            self.pics.append(pic)

                # elif "#EXTM3U" in fpage:
                else:
                        regexcat = '#EXTINF.*?,(.*?)\\n(.*?)\\n'
                        match = re.compile(regexcat, re.DOTALL).findall(fpage)
                        for name, url in match:
                                url = url.replace(' ', '')
                                url = url.replace('\\n', '')
                                # # url = url.replace('https', 'http')
                                # if pic:
                                pic = pic
                                self.names.append(name)
                                self.urls.append(url)
                                self.pics.append(pic)
    #####################################################################################
    #self.onShown.append(self.openTest)
                if config.plugins.TivuStream.thumb.value == True:
                    self.gridmaint = eTimer()
                    self.gridmaint.start(3000, True)
                    try:
                        self.gridmaint_conn = self.gridmaint.timeout.connect(self.gridpic)
                    except:
                        self.gridmaint.callback.append(self.gridpic)
                    # self.session.open(GridMain, self.names, self.urls, self.pics)
    #####################################################################################
                else:
                    m3ulist(self.names, self['list'])

                self["live"].setText('N.' + str(len(self.names)) + " Stream")

            else:
                self.session.open(openMessageBox, _('File Unknow!!!'), openMessageBox.TYPE_INFO, timeout=5)

        except Exception as ex:
            print('error exception: ', ex)

    def gridpic(self):

        self.session.open(GridMain, self.names, self.urls, self.pics)
        self.close()

    def runChannel(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            self.pin = True
            if config.ParentalControl.configured.value:
                a = '+18', 'adult', 'hot', 'porn', 'sex', 'xxx'
                if any(s in str(self.names[idx]).lower() for s in a):
                    self.allow2()
                else:
                    self.pin = True
                    self.pinEntered2(True)
            else:
                self.pin = True
                self.pinEntered2(True)

    def allow2(self):
        from Screens.InputBox import PinInput
        self.session.openWithCallback(self.pinEntered2, PinInput, pinList = [config.ParentalControl.setuppin.value], triesEntry = config.ParentalControl.retries.servicepin, title = _("Please enter the parental control pin code"), windowTitle = _("Enter pin code"))

    def pinEntered2(self, result):
        if not result:
            self.pin = False
            self.session.open(openMessageBox, _("The pin code you entered is wrong."), type=openMessageBox.TYPE_ERROR, timeout=5)
        self.runChannel2()

    def runChannel2(self):
        if self.pin is False:
            return
        else:
            idx = self['list'].getSelectionIndex()
            name = self.names[idx]
            url = self.urls[idx]
            self.session.open(M3uPlay2, name, url)
            return

    def play2(self):
        if os.path.exists("/usr/sbin/streamlinksrv"):
            idx = self['list'].getSelectionIndex()
            name = self.names[idx]
            url = self.urls[idx]
            url = url.replace(':', '%3a')
            print('In revolution url =', url)
            ref = '5002:0:1:0:0:0:0:0:0:0:' + 'http%3a//127.0.0.1%3a8088/' + str(url)
            sref = eServiceReference(ref)
            print('SREF: ', sref)
            sref.setName(name)
            self.session.open(M3uPlay2, name, sref)
            self.close()
        else:
            self.session.open(MessageBox, _('Install Streamlink first'), MessageBox.TYPE_INFO, timeout=5)

    def AdjUrlFavo(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            url = self.urls[idx]
            self.session.open(AddIpvStream, name, url)
            return

    def cancel(self):
        if search_ok == True:
            self.playList()
        else:
            self.session.nav.stopService()
            self.session.nav.playService(srefInit)
            self.close()

# class M3uPlay2(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarAudioSelection, TvInfoBarShowHide):#,InfoBarSubtitleSupport
class M3uPlay2(
    InfoBarBase,
    InfoBarMenu,
    InfoBarSeek,
    InfoBarAudioSelection,
    InfoBarSubtitleSupport,
    InfoBarNotifications,
    TvInfoBarShowHide,
    Screen
):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True
    screen_timeout = 5000

    def __init__(self, session, name, url):
        global SREF, streaml
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = 'MoviePlayer'
        title = name
        streaml = False

        for x in InfoBarBase, \
                InfoBarMenu, \
                InfoBarSeek, \
                InfoBarAudioSelection, \
                InfoBarSubtitleSupport, \
                InfoBarNotifications, \
                TvInfoBarShowHide:
            x.__init__(self)
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self['actions'] = ActionMap(['MoviePlayerActions',
         'MovieSelectionActions',
         'MediaPlayerActions',
         'EPGSelectActions',
         'MediaPlayerSeekActions',
         'SetupActions',
         'ColorActions',
         'InfobarShowHideActions',
         'InfobarActions',
         'InfobarSeekActions'], {'leavePlayer': self.cancel,
         'epg': self.showIMDB,
         'info': self.showinfo,
         # 'info': self.cicleStreamType,
         'tv': self.cicleStreamType,
         'stop': self.cancel,
         'cancel': self.cancel,
         'back': self.cancel}, -1)
        self.allowPiP = False
        self.service = None
        service = None
        self.pcip = 'None'
        self.icount = 0
        self.desc = desc
        self.url = url
        self.name = decodeHtml(name)
        self.state = self.STATE_PLAYING
        SREF = self.session.nav.getCurrentlyPlayingServiceReference()
        if '8088' in str(self.url):
            self.onFirstExecBegin.append(self.slinkPlay)
        else:
            self.onFirstExecBegin.append(self.cicleStreamType)
        self.onClose.append(self.cancel)
    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: _('4:3 Letterbox'),
         1: _('4:3 PanScan'),
         2: _('16:9'),
         3: _('16:9 always'),
         4: _('16:10 Letterbox'),
         5: _('16:10 PanScan'),
         6: _('16:9 Letterbox')}[aspectnum]

    def setAspect(self, aspect):
        map = {0: '4_3_letterbox',
         1: '4_3_panscan',
         2: '16_9',
         3: '16_9_always',
         4: '16_10_letterbox',
         5: '16_10_panscan',
         6: '16_9_letterbox'}
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        temp = int(self.getAspect())
        temp = temp + 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)

    def showinfo(self):
        debug = True
        sTitle = ''
        sServiceref = ''
        try:
            servicename, serviceurl = getserviceinfo(sref)
            if servicename != None:
                sTitle = servicename
            else:
                sTitle = ''
            if serviceurl != None:
                sServiceref = serviceurl
            else:
                sServiceref = ''
            currPlay = self.session.nav.getCurrentService()
            sTagCodec = currPlay.info().getInfoString(iServiceInformation.sTagCodec)
            sTagVideoCodec = currPlay.info().getInfoString(iServiceInformation.sTagVideoCodec)
            sTagAudioCodec = currPlay.info().getInfoString(iServiceInformation.sTagAudioCodec)
            message = 'stitle:' + str(sTitle) + '\n' + 'sServiceref:' + str(sServiceref) + '\n' + 'sTagCodec:' + str(sTagCodec) + '\n' + 'sTagVideoCodec:' + str(sTagVideoCodec) + '\n' + 'sTagAudioCodec: ' + str(sTagAudioCodec)
            self.mbox = self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        except:
            pass
        return

    def showIMDB(self):
        TMDB = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TMDB'))
        IMDb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('IMDb'))
        if os.path.exists(TMDB):
            from Plugins.Extensions.TMBD.plugin import TMBD
            text_clear = self.name

            text = charRemove(text_clear)
            self.session.open(TMBD, text, False)
        elif os.path.exists(IMDb):
            from Plugins.Extensions.IMDb.plugin import IMDB
            text_clear = self.name

            text = charRemove(text_clear)
            HHHHH = text
            self.session.open(IMDB, HHHHH)

        else:
            text_clear = self.name
            self.session.open(MessageBox, text_clear, MessageBox.TYPE_INFO)

    def slinkPlay(self, url):
        name = self.name
        ref = "{0}:{1}".format(url.replace(":", "%3A"), name.replace(":", "%3A"))
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def openPlay(self, servicetype, url):
        name = self.name

        ref = "{0}:0:0:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3A"), name.replace(":", "%3A"))
        print('reference:   ', ref)
        if streaml == True:
            url = 'http://127.0.0.1:8088/' + str(url)
            ref = "{0}:0:1:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3A"), name.replace(":", "%3A"))
            print('streaml reference:   ', ref)
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def cicleStreamType(self):
        global streml
        streaml = False
        from itertools import cycle, islice
        self.servicetype = str(config.plugins.TivuStream.services.value) #+':0:1:0:0:0:0:0:0:0:'#  '4097'
        print('servicetype1: ', self.servicetype)
        url = str(self.url)
        if str(os.path.splitext(self.url)[-1]) == ".m3u8":
            if self.servicetype == "1":
                self.servicetype = "4097"
        currentindex = 0
        streamtypelist = ["4097"]
        # if "youtube" in str(self.url):
            # self.mbox = self.session.open(MessageBox, _('For Stream Youtube coming soon!'), MessageBox.TYPE_INFO, timeout=5)
            # return
        if isStreamlinkAvailable():
            streamtypelist.append("5002") #ref = '5002:0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + url
            streaml = True
        if os.path.exists("/usr/bin/gstplayer"):
            streamtypelist.append("5001")
        if os.path.exists("/usr/bin/exteplayer3"):
            streamtypelist.append("5002")
        if os.path.exists("/usr/bin/apt-get"):
            streamtypelist.append("8193")
        for index, item in enumerate(streamtypelist, start=0):
            if str(item) == str(self.servicetype):
                currentindex = index
                break
        nextStreamType = islice(cycle(streamtypelist), currentindex + 1, None)
        self.servicetype = str(next(nextStreamType))
        print('servicetype2: ', self.servicetype)
        self.openPlay(self.servicetype, url)

    def up(self):
        pass

    def down(self):
        self.up()

    def doEofInternal(self, playing):
        self.close()

    def __evEOF(self):
        self.end = True

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback != None:
            self.infoCallback()
        return

    def showAfterSeek(self):
        if isinstance(self, TvInfoBarShowHide):
            self.doShow()

    def cancel(self):
        if os.path.isfile('/tmp/hls.avi'):
            os.remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(SREF)
        if self.pcip != 'None':
            url2 = 'http://' + self.pcip + ':8080/requests/status.xml?command=pl_stop'
            resp = urlopen(url2)
        if not self.new_aspect == self.init_aspect:
            try:
                self.setAspect(self.init_aspect)
            except:
                pass
        streaml = False
        self.close()

    def leavePlayer(self):
        self.close()

class AddIpvStream(Screen):
    def __init__(self, session, name, url):
        self.session = session
        skin = skin_path + '/AddIpvStream.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self['title'] = Label(_(title_plug))
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['infoc2'] = Label('%s' % Credits)
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Ok'))
        self['key_yellow'] = Button(_(''))
        self["key_yellow"].hide()
        self["key_blue"] = Button(_(''))
        self["key_blue"].hide()
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.keyOk,
         'cancel': self.keyCancel,
         'green': self.keyOk,
         'red': self.keyCancel}, -2)
        self['statusbar'] = Label()
        self.list = []
        self['menu'] = MenuList([])
        self.mutableList = None
        self.servicelist = ServiceList(None)
        self.onLayoutFinish.append(self.createTopMenu)
        self.namechannel = name
        self.urlchannel = url
        return

    def initSelectionList(self):
        self.list = []
        self['menu'].setList(self.list)

    def createTopMenu(self):
        self.setTitle(_('Add Stream IPTV'))
        self.initSelectionList()
        self.list = []
        tmpList = []
        self.list = self.getBouquetList()
        self['menu'].setList(self.list)
        self['statusbar'].setText(_('Select the Bouquet and press OK to add'))

    def getBouquetList(self):
        self.service_types = service_types_tv
        if config.usage.multibouquet.value:
            self.bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
        else:
            self.bouquet_rootstr = '%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet' % self.service_types
        self.bouquet_root = eServiceReference(self.bouquet_rootstr)
        bouquets = []
        serviceHandler = eServiceCenter.getInstance()
        if config.usage.multibouquet.value:
            list = serviceHandler.list(self.bouquet_root)
            if list:
                while True:
                    s = list.getNext()
                    if not s.valid():
                        break
                    if s.flags & eServiceReference.isDirectory:
                        info = serviceHandler.info(s)
                        if info:
                            bouquets.append((info.getName(s), s))
                return bouquets
        else:
            info = serviceHandler.info(self.bouquet_root)
            if info:
                bouquets.append((info.getName(self.bouquet_root), self.bouquet_root))
            return bouquets
        return None

    def keyOk(self):
        if len(self.list) == 0:
            return
        self.name = ''
        self.url = ''
        self.session.openWithCallback(self.addservice, VirtualKeyBoard, title=_('Enter Name'), text=self.namechannel)

    def addservice(self, res):
        if res:
            self.url = res
            str = '4097:0:0:0:0:0:0:0:0:0:%s:%s' % (quote(self.url), quote(self.name))
            ref = eServiceReference(str)
            self.addServiceToBouquet(self.list[self['menu'].getSelectedIndex()][1], ref)
            self.close()

    def addServiceToBouquet(self, dest, service = None):
        mutableList = self.getMutableList(dest)
        if mutableList != None:
            if service is None:
                return
            if not mutableList.addService(service):
                mutableList.flushChanges()
        return

    def getMutableList(self, root = eServiceReference()):
        if self.mutableList != None:
            return self.mutableList
        else:
            serviceHandler = eServiceCenter.getInstance()
            if not root.valid():
                root = self.getRoot()
            list = root and serviceHandler.list(root)
            if list != None:
                return list.startEdit()
            return
            return

    def getRoot(self):
        return self.servicelist.getRoot()

    def keyCancel(self):
        self.close()


class OpenConfig(Screen, ConfigListScreen):
        def __init__(self, session):
            skin = skin_path + '/OpenConfig.xml'
            f = open(skin, 'r')
            self.skin = f.read()
            f.close()
            Screen.__init__(self, session)
            self.setup_title = _("TiVuStream Config")
            self.onChangedEntry = [ ]
            self.session = session
            info = '***'
            self['title'] = Label(_(title_plug))
            self['Maintainer2'] = Label('%s' % Maintainer2)
            self['infoc2'] = Label('%s' % Credits)
            self['key_red'] = Button(_('Exit'))
            self['key_green'] = Button(_('Save'))
            self['key_yellow'] = Button(_('Update'))
            self["key_blue"] = Button(_(''))
            self["key_blue"].hide()
            self['text'] = Label(info)
            self["description"] = Label(_(''))
            self.cbUpdate = False
            self['actions'] = ActionMap(["SetupActions", "ColorActions", "VirtualKeyboardActions"  ], {
                'cancel': self.extnok,
                "red": self.extnok,
                "green": self.cfgok,
                'yellow': self.msgupdt1,
                'showVirtualKeyboard': self.KeyText,
                'ok': self.Ok_edit,
            }, -2)
            self.list = []
            ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
            self.createSetup()
            self.onLayoutFinish.append(self.checkUpdate)
            self.onLayoutFinish.append(self.layoutFinished)
            if self.setInfo not in self['config'].onSelectionChanged:
                self['config'].onSelectionChanged.append(self.setInfo)

        def checkUpdate(self):
            try:
                fp = ''
                destr = plugin_path + 'update.txt'
                fp = ReadUrl2(upd_fr_txt)
                fp = six.ensure_str(fp)
                with open(destr, 'w') as f:
                    f.write(fp)
                    f.close()
                with open(destr, 'r') as fp:
                    count = 0
                    fp.seek(0)
                    s1 = fp.readline()
                    s2 = fp.readline()
                    s3 = fp.readline()
                    s1 = s1.strip()
                    s2 = s2.strip()
                    s3 = s3.strip()
                    self.link = s2
                    self.version = s1
                    self.info = s3
                    fp.close()
                    if s1 <= currversion:
                        self.cbUpdate = False
                        print("Update False =", s1)
                        self['text'].setText(_('Version: ') + currversion + '\n'+ _('No updates!') + '\n' + _('if you like it you can make a free donation') + '\n' + _('www.paypal.me/TivuStream'))
                    else:
                        self.cbUpdate = True
                        print("Update True =", s1)
                        updatestr = (_('Version: ') + currversion + '\n' + _('Last update ') + s1 + ' ' + _('available!') + '\n' + _('ChangeLog:') + self.info)
                        self['text'].setText(updatestr)
            except:
                self.cbUpdate = False
                self['text'].setText(_('No updates available') + '\n' + _('No internet connection or server OFF') + '\n' + _('Please try again later or change SERVER to config menu.'))
            self.timerx = eTimer()
            self.timerx.start(100, 1)
            if DreamOS():
                self.timerx_conn = self.timerx.timeout.connect(self.msgupdt2)
            else:
                self.timerx.callback.append(self.msgupdt2)

        def layoutFinished(self):
            self.setTitle(self.setup_title)

        def createSetup(self):
            self.editListEntry = None
            self.list = []
            self.list.append(getConfigListEntry(_('Server:'), config.plugins.TivuStream.server))
            self.list.append(getConfigListEntry(_('Auto Update Plugin:'), config.plugins.TivuStream.autoupd))
            self.list.append(getConfigListEntry(_('Personal Password:'), config.plugins.TivuStream.code))
            self.list.append(getConfigListEntry(_('IPTV bouquets location '), config.plugins.TivuStream.bouquettop))
            self.list.append(getConfigListEntry(_('Player folder List <.m3u>:'), config.plugins.TivuStream.pthm3uf))
            self.list.append(getConfigListEntry(_('Services Player Reference type'), config.plugins.TivuStream.services))
            self.list.append(getConfigListEntry(_('Show thumpics?'), config.plugins.TivuStream.thumb))
            if config.plugins.TivuStream.thumb.value == True:
                self.list.append(getConfigListEntry(_('Download thumpics?'), config.plugins.TivuStream.thumbpic))
            self.list.append(getConfigListEntry(_('Folder Cache for Thumbpics:'), config.plugins.TivuStream.cachefold))
            self.list.append(getConfigListEntry(_('Link in Extensions Menu:'), config.plugins.TivuStream.strtext))
            self.list.append(getConfigListEntry(_('Link in Main Menu:'), config.plugins.TivuStream.strtmain))
            self['config'].list = self.list
            self["config"].setList(self.list)
            self.setInfo()

        def setInfo(self):
            entry = str(self.getCurrentEntry())
            if entry == _('Server:'):
                self['description'].setText(_("Configure Server for Update Service and List"))
                return
            if entry == _('Auto Update Plugin:'):
                self['description'].setText(_("Set Automatic Update Plugin Version"))
                return
            if entry == _('Personal Password:'):
                self['description'].setText(_("Enter the password to download Lists XXX Adults"))
                return
            if entry == _('IPTV bouquets location '):
                self['description'].setText(_("Configure position of the bouquets of the converted lists"))
                return
            if entry == _('Player folder List <.m3u>:'):
                self['description'].setText(_("Folder path containing the .m3u files"))
                return
            if entry == _('Services Player Reference type'):
                self['description'].setText(_("Configure Service Player Reference"))
                return
            if entry == _('Show thumpics?'):
                self['description'].setText(_("Show Thumbpics ? Enigma restart required"))
                return
            if entry == _('Download thumpics?'):
                self['description'].setText(_("Download thumpics in Player M3U (is very Slow)?"))
                return
            if entry == _('Folder Cache for Thumbpics:'):
                self['description'].setText(_("Configure position folder for temporary Thumbpics"))
                return
            if entry == _('Link in Extensions Menu:'):
                self['description'].setText(_("Show Plugin in Extensions Menu"))
                return
            if entry == _('Link in Main Menu:'):
                self['description'].setText(_("Show Plugin in Main Menu"))
            return

        def changedEntry(self):
            sel = self['config'].getCurrent()
            for x in self.onChangedEntry:
                x()
            try:
                if isinstance(self['config'].getCurrent()[1], ConfigEnableDisable) or isinstance(self['config'].getCurrent()[1], ConfigYesNo) or isinstance(self['config'].getCurrent()[1], ConfigSelection):
                    self.createSetup()
            except:
                pass

        def getCurrentEntry(self):
            return self['config'].getCurrent() and self['config'].getCurrent()[0] or ''

        def getCurrentValue(self):
            return self['config'].getCurrent() and str(self['config'].getCurrent()[1].getText()) or ''

        def createSummary(self):
            from Screens.Setup import SetupSummary
            return SetupSummary

        def Ok_edit(self):
            ConfigListScreen.keyOK(self)
            sel = self['config'].getCurrent()[1]
            if sel and sel == config.plugins.TivuStream.pthm3uf:
                self.setting = 'pthm3uf'
                self.openDirectoryBrowser(config.plugins.TivuStream.pthm3uf.value)
            elif sel and sel == config.plugins.TivuStream.cachefold:
                self.setting = 'cachefold'
                self.openDirectoryBrowser(config.plugins.TivuStream.cachefold.value)
            else:
                pass

        def openDirectoryBrowser(self, path):
            try:
                self.session.openWithCallback(
                 self.openDirectoryBrowserCB,
                 LocationBox,
                 windowTitle=_('Choose Directory:'),
                 text=_('Choose Directory'),
                 currDir=str(path),
                 bookmarks=config.movielist.videodirs,
                 autoAdd=False,
                 editDir=True,
                 inhibitDirs=['/bin', '/boot', '/dev', '/home', '/lib', '/proc', '/run', '/sbin', '/sys', '/var'],
                 minFree=15)
            except Exception as ex:
                print(ex)

        def openDirectoryBrowserCB(self, path):
            if path != None:
                if self.setting == 'pthm3uf':
                    config.plugins.TivuStream.pthm3uf.setValue(path)
                elif self.setting == 'cachefold':
                    config.plugins.TivuStream.cachefold.setValue(path)
            return

        def cfgok(self):
            self.save()

        def save(self):
            if not os.path.exists(config.plugins.TivuStream.pthm3uf.value):
                self.mbox = self.session.open(openMessageBox, _('M3u list folder not detected!'), openMessageBox.TYPE_INFO, timeout=4)
                return
            if self['config'].isChanged():
                for x in self['config'].list:
                    x[1].save()
                server_ref()
                config.plugins.TivuStream.server.save()
                configfile.save()
                plugins.clearPluginList()
                plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
                self.mbox = self.session.open(openMessageBox, _('Settings saved correctly!'), openMessageBox.TYPE_INFO, timeout=5)
                self.close()
            else:
             self.close()

        def VirtualKeyBoardCallback(self, callback = None):
            if callback != None and len(callback):
                self["config"].getCurrent()[1].setValue(callback)
                self["config"].invalidate(self["config"].getCurrent())

        def KeyText(self):
            sel = self['config'].getCurrent()
            if sel:
                self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)

        def cancelConfirm(self, result):
            if not result:
                return
            for x in self['config'].list:
                x[1].cancel()
            self.close()

        def extnok(self):
            if self['config'].isChanged():
                self.session.openWithCallback(self.cancelConfirm, openMessageBox, _('Really close without saving the settings?'))
            else:
                self.close()

        def msgupdt2(self):
            if self.cbUpdate == False:
                return
            if config.plugins.TivuStream.autoupd.value == False:
                return
            self.session.openWithCallback(self.runupdate, openMessageBox, _('New Online Version!') + '\n\n' + _('Update Plugin to Version %s ?\nPlease Restart GUI Required!' % self.version), openMessageBox.TYPE_YESNO)

        def msgupdt1(self):
            if self.cbUpdate == False:
                return
            self.session.openWithCallback(self.runupdate, openMessageBox, _('Update Plugin ?'), openMessageBox.TYPE_YESNO)

        def runupdate(self, result):
            if result:
                com = self.link
                dom = 'Last version ' + self.version
                os.system('wget %s -O /tmp/tivustream.tar > /dev/null' % com)
                os.system('sleep 3')
                self.session.open(OpenConsole, _('Update Plugin: %s') % dom, ['tar -xvf /tmp/tivustream.tar -C /'], closeOnSuccess=False) #finishedCallback=self.ipkrestrt, closeOnSuccess=False)

        def ipkrestrt(self):
            epgpath = '/media/hdd/epg.dat'
            epgbakpath = '/media/hdd/epg.dat.bak'
            if os.path.exists(epgbakpath):
                os.remove(epgbakpath)
            if os.path.exists(epgpath):
                copyfile(epgpath, epgbakpath)
            self.session.open(TryQuitMainloop, 3)

class OpenConsole(Screen):
    # def __init__(self, session, title = None, cmdlist = None, finishedCallback = None, closeOnSuccess = False):
    def __init__(self, session, title="Console", cmdlist=None, finishedCallback=None, closeOnSuccess=False,endstr=''):
        self.session = session
        skin = skin_path + '/OpenConsole.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self.endstr = endstr
        self['text'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.cancel,
         'back': self.cancel,
         "blue": self.restartenigma,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown}, -1)
        self.cmdlist = cmdlist
        self.container = eConsoleAppContainer()
        self.run=0
        try:
            self.container.appClosed.append(self.runFinished)
            self.container.dataAvail.append(self.dataAvail)
        except:
            self.appClosed_conn=self.container.appClosed.connect(self.runFinished)
            self.dataAvail_conn=self.container.dataAvail.connect(self.dataAvail)
        self.onLayoutFinish.append(self.startRun)

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        self['text'].setText(_('Executing in run:') + '\n\n')
        if self.container.execute(self.cmdlist[self.run]):
            self.runFinished(-1)

    def runFinished(self, retval):
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]):
                self.runFinished(-1)
        else:
            str=self["text"].getText()
            if not retval and self.endstr.startswith("Swapping"):
               str += _("\n\n"+self.endstr)
            else:
               str += _("Execution finished!!\n")
            self["text"].setText(str)
            self["text"].lastPage()
            # if self.finishedCallback != None:
                # self.finishedCallback(retval)
            # if not retval and self.closeOnSuccess:
            self.cancel()

    def dataAvail(self, data):
        if PY3:
            data = data.decode("utf-8")
        try:
            self["text"].setText(self["text"].getText() + data)
        except:
            trace_error()
        return
        if self["text"].getText().endswith("Do you want to continue? [Y/n] "):
            msg=self.session.openWithCallback(self.processAnswer, MessageBox, _("Additional packages must be installed. Do you want to continue?"), MessageBox.TYPE_YESNO)

    def processAnswer(self, retval):
        if retval:
            self.container.write("Y",1)
        else:
            self.container.write("n",1)
        self.dataSent_conn=self.container.dataSent.connect(self.processInput)

    def processInput(self, retval):
        self.container.sendEOF()

    def restartenigma(self):
        self.session.open(TryQuitMainloop, 3)

    def cancel(self):
        if self.run == len(self.cmdlist):
            self.close()
            try:
                self.appClosed_conn=None
                self.dataAvail_conn=None
            except:
                self.container.appClosed.remove(self.runFinished)
                self.container.dataAvail.remove(self.dataAvail)

class openMessageBox(Screen):
    TYPE_YESNO = 0
    TYPE_INFO = 1
    TYPE_WARNING = 2
    TYPE_ERROR = 3
    TYPE_MESSAGE = 4

    def __init__(self, session, text, type = TYPE_YESNO, timeout = -1, close_on_any_key = False, default = True, enable_input = True, msgBoxID = None, picon = None, simple = False, list = [], timeout_default = None):
        self.type = type
        self.session = session
        skin = skin_path + '/OpenMessageBox.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self.msgBoxID = msgBoxID
        self['text'] = Label(text)
        self['Text'] = StaticText(text)
        self['selectedChoice'] = StaticText()
        self.text = text
        self.close_on_any_key = close_on_any_key
        self.timeout_default = timeout_default
        self['ErrorPixmap'] = Pixmap()
        self['QuestionPixmap'] = Pixmap()
        self['InfoPixmap'] = Pixmap()
        self['WarningPixmap'] = Pixmap()
        self.timerRunning = False
        self.initTimeout(timeout)
        picon = picon or type
        if picon != self.TYPE_ERROR:
                self['ErrorPixmap'].hide()
        if picon != self.TYPE_YESNO:
                self['QuestionPixmap'].hide()
        if picon != self.TYPE_INFO:
                self['InfoPixmap'].hide()
        if picon != self.TYPE_WARNING:
                self['WarningPixmap'].hide()
        self.title = self.type < self.TYPE_MESSAGE and [_('Question'),
         _('Information'),
         _('Warning'),
         _('Error')][self.type] or _('Message')
        if type == self.TYPE_YESNO:
            if list:
                self.list = list
            elif default == True:
                self.list = [(_('Yes'), True), (_('No'), False)]
            else:
                self.list = [(_('No'), False), (_('Yes'), True)]
        else:
            self.list = []
        self['list'] = MenuList(self.list)

        if self.list:
            self['selectedChoice'].setText(self.list[0][0])
        else:
            self['list'].hide()
        if enable_input:
            self['actions'] = ActionMap(['MsgBoxActions', 'DirectionActions'], {'cancel': self.cancel,
             'ok': self.ok,
             'alwaysOK': self.alwaysOK,
             'up': self.up,
             'down': self.down,
             'left': self.left,
             'right': self.right,
             'upRepeated': self.up,
             'downRepeated': self.down,
             'leftRepeated': self.left,
             'rightRepeated': self.right}, -1)
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(self.title)

    def initTimeout(self, timeout):
        self.timeout = timeout
        if timeout > 0:
            self.timer = eTimer()
            if DreamOS():
                self.timer_conn = self.timer.timeout.connect(self.timerTick)
            else:
                self.timer.callback.append(self.timerTick)
            self.onExecBegin.append(self.startTimer)
            self.origTitle = None
            if self.execing:
                self.timerTick()
            else:
                self.onShown.append(self.__onShown)
            self.timerRunning = True
        else:
            self.timerRunning = False
        return

    def __onShown(self):
        self.onShown.remove(self.__onShown)
        self.timerTick()

    def startTimer(self):
            self.timer.start(1000)

    def stopTimer(self):
        if self.timerRunning:
            del self.timer
            self.onExecBegin.remove(self.startTimer)
            self.setTitle(self.origTitle)
            self.timerRunning = False

    def timerTick(self):
        if self.execing:
            self.timeout -= 1
            if self.origTitle is None:
                self.origTitle = self.instance.getTitle()
            self.setTitle(self.origTitle + ' (' + str(self.timeout) + ')')
            if self.timeout == 0:
                self.timer.stop()
                self.timerRunning = False
                self.timeoutCallback()
        return

    def timeoutCallback(self):
        if self.timeout_default != None:
            self.close(self.timeout_default)
        else:
            self.ok()
        return

    def cancel(self):
        self.close(False)

    def ok(self):
        if self.list:
            self.close(self['list'].getCurrent()[1])
        else:
            self.close(True)

    def alwaysOK(self):
        self.close(True)

    def up(self):
        self.move(self['list'].instance.moveUp)

    def down(self):
        self.move(self['list'].instance.moveDown)

    def left(self):
        self.move(self['list'].instance.pageUp)

    def right(self):
        self.move(self['list'].instance.pageDown)

    def move(self, direction):
        if self.close_on_any_key:
            self.close(True)
        self['list'].instance.moveSelection(direction)
        if self.list:
            self['selectedChoice'].setText(self['list'].getCurrent()[0])
        self.stopTimer()

    def __repr__(self):
        return str(type(self)) + '(' + self.text + ')'

class plgnstrt(Screen):
    def __init__(self, session):
        self.session = session
        skin = skin_path + '/Plgnstrt.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self["poster"] = Pixmap()
        self["poster"].hide()
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        # self['text'] = ScrollLabel()
        self['text'] = StaticText()
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions', 'ColorActions', 'SetupActions'], {'ok': self.clsgo,
         'cancel': self.clsgo,
         'back': self.clsgo,
         'red': self.clsgo,
         # 'up': self['text'].pageUp,
         # 'down': self['text'].pageDown,
         # 'left': self['text'].pageUp,
         # 'right': self['text'].pageDown,
         'green': self.clsgo}, -1)
        # self.onShown.append(self.checkDwnld)
        self.onFirstExecBegin.append(self.loadDefaultImage)
        # self.onLayoutFinish.append(self.image_downloaded)
        self.onLayoutFinish.append(self.checkDwnld)

    def decodeImage(self, pngori):
        pixmaps = pngori
        if DreamOS():
            self['poster'].instance.setPixmap(gPixmapPtr())
        else:
            self['poster'].instance.setPixmap(None)
        # self['poster'].hide()
        sc = AVSwitch().getFramebufferScale()
        self.picload = ePicLoad()
        size = self['poster'].instance.size()
        self.picload.setPara((size.width(),
         size.height(),
         sc[0],
         sc[1],
         False,
         1,
         '#FF000000'))
        ptr = self.picload.getData()
        if DreamOS():
            if self.picload.startDecode(pixmaps, False) == 0:
                ptr = self.picload.getData()
        else:
            if self.picload.startDecode(pixmaps, 0, 0, False) == 0:
                ptr = self.picload.getData()
        if ptr != None:
            self['poster'].instance.setPixmap(ptr)
            self['poster'].show()
        else:
            print('no cover.. error')
        return

    def image_downloaded(self):
        pngori = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/nasa3.jpg".format('TivuStream'))
        if os.path.exists(pngori):
            print('image pngori: ',pngori)
            try:
                self.decodeImage(pngori)
            except Exception as ex:
                print(ex)
                pass
            except:
                pass

    def loadDefaultImage(self, failure=None):
        import random
        print("*** failure *** %s" % failure)
        # if self["poster"].instance:
        global pngori
        # self.png = '/usr/lib/enigma2/python/Plugins/Extensions/TivuStream/res/pics/nasa3.jpg'
        fldpng = '/usr/lib/enigma2/python/Plugins/Extensions/TivuStream/res/pics/'
        npj = random.choice(imgjpg)
        pngori = fldpng + npj
        self.decodeImage(pngori)

    def checkDwnld(self):
        self.icount = 0
        self['text'].setText(_('\n\n\nCheck Connection wait please...'))
        self.timer = eTimer()
        self.timer.start(1500, 1)
        if DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.OpenCheck)
        else:
            self.timer.callback.append(self.OpenCheck)

    def getinfo(self):
        continfo = _("==========       WELCOME     ============\n")
        continfo += _("=========     SUPPORT ON:   ============\n")
        continfo += _("+WWW.TIVUSTREAM.COM - WWW.CORVOBOYS.COM+\n")
        continfo += _("http://t.me/tivustream\n\n")
        continfo += _("========================================\n")
        continfo += _("NOTA BENE:\n")
        continfo += _("Le liste create ad HOC contengono indirizzi liberamente e gratuitamente\n")
        continfo += _("trovati in rete e non protetti da sottoscrizione o abbonamento.\n")
        continfo += _("Il server di riferimento strutturale ai progetti rilasciati\n")
        continfo += _("non e' fonte di alcun stream/flusso.\n")
        continfo += _("Assolutamente VIETATO utilizzare queste liste senza autorizzazione.\n")
        continfo += _("========================================\n")
        continfo += _("DISCLAIMER: \n")
        continfo += _("The lists created at HOC contain addresses freely and freely found on\n")
        continfo += _("the net and not protected by subscription or subscription.\n")
        continfo += _("The structural reference server for projects released\n")
        continfo += _("is not a source of any stream/flow.\n")
        continfo += _("Absolutely PROHIBITED to use this lists without authorization\n")
        continfo += _("========================================\n")
        return continfo

    def OpenCheck(self):
        try:
            self['text'].setText(self.getinfo())
        except:
            self['text'].setText(_('\n\n' + 'Error downloading News!'))

    def error(self, error):
        self['text'].setText(_('\n\n' + 'Server Off !') + '\n' + _('check SERVER in config'))


    def clsgo(self):
        self.session.openWithCallback(self.close, OpenScript)

def checks():
    from Plugins.Extensions.revolution.Utils import checkInternet
    checkInternet()
    chekin= False
    if checkInternet():
        chekin = True
        return True

def main(session, **kwargs):
    if checks:
        # add_skin_font()
        if PY3:
            session.open(OpenScript)
        else:
            session.open(plgnstrt)
    else:
        session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)

def cfgmain(menuid):
    if menuid == 'mainmenu':
        return [('TiVuStream Revolution',
         main,
         'TiVuStream Revolution',
         44)]
    else:
        return []

def Plugins(**kwargs):
    icona = 'logo.png'
    if not DreamOS():
        icona = skin_path + '/logo.png'
    extDescriptor = PluginDescriptor(name=name_plug, description=_(title_plug), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon=icona, fnc=main)
    mainDescriptor = PluginDescriptor(name=name_plug, description=_(title_plug), where=PluginDescriptor.WHERE_MENU, icon=icona, fnc=cfgmain)
    result = [PluginDescriptor(name=name_plug, description=_(title_plug), where=[PluginDescriptor.WHERE_PLUGINMENU], icon=icona, fnc=main)]
    if config.plugins.TivuStream.strtext.value:
        result.append(extDescriptor)
    if config.plugins.TivuStream.strtmain.value:
        result.append(mainDescriptor)
    return result

