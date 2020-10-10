#"****************************************"
#"*      coded by Lululla                 *"
#"*             skin by MMark             *"
#"*             18/09/2020                *"
#"****************************************"
# from . import _
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ConfigList import *
from Components.Console import Console as iConsole
from Components.HTMLComponent import *
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
from Components.ServiceList import ServiceList
from Components.Sources.List import List
from Components.Sources.Progress import Progress
from Components.Sources.Source import Source
from Components.Sources.StaticText import StaticText
from Components.config import *
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.InfoBar import MoviePlayer, InfoBar
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
from twisted.web.client import downloadPage, getPage, error
from xml.dom import Node, minidom
import Components.PluginComponent
import base64
import os, re, sys, glob
import time
import socket
import ssl
from os.path import splitext
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarAudioSelection, InfoBarSubtitleSupport, InfoBarNotifications, InfoBarMenu
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase

global isDreamOS
isDreamOS = False
PY3 = sys.version_info.major >= 3

if PY3:
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
    from urllib.parse import urlparse
    from urllib.parse import urlencode, quote

else:
    from urllib2 import urlopen, Request
    from urllib2 import URLError, HTTPError
    from urlparse import urlparse
    from urllib import urlencode, quote
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

def checkStr(txt):
    # convert variable to type str both in Python 2 and 3
    if PY3:
        # Python 3
        if type(txt) == type(bytes()):
            txt = txt.decode('utf-8')
    else:
        #Python 2
        if type(txt) == type(unicode()):
            txt = txt.encode('utf-8')
    return txt


try:
    from enigma import eMediaDatabase
    isDreamOS = True
except:
    isDreamOS = False

try:
    from enigma import eDVBDB
except ImportError:
    eDVBDB = None

#changelog 10.10.2020
currversion      = '2.7'
Version          = currversion + ' - 14.10.2020'
Credits          = 'Info http://t.me/tivustream'
Maintainer2      = 'Maintener @Lululla'
plugin_path      = '/usr/lib/enigma2/python/Plugins/Extensions/TivuStream/'
dir_enigma2      = '/etc/enigma2/'
service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'

#================
def add_skin_font():
        font_path = plugin_path + 'res/fonts/'
        addFont(font_path + 'verdana_r.ttf', 'OpenFont1', 100, 1)
        addFont(font_path + 'verdana_r.ttf', 'OpenFont2', 100, 1)

def checkInternet():
        try:
            # response=urlopen("http://google.com", None, 5)
            response = checkStr(urlopen("http://google.com", None, 5))
            response.close()
        except HTTPError:
            return False
        except URLError:
            return False
        except socket.timeout:
            return False


def ReloadBouquet():
                if eDVBDB:
                        eDVBDB.getInstance().reloadBouquets()
                else:
                        os.system('wget -qO - http://127.0.0.1/web/servicelistreload?mode=2 > /dev/null 2>&1 &')

def OnclearMem():
        try:
                os.system("sync")
                os.system("echo 1 > /proc/sys/vm/drop_caches")
                os.system("echo 2 > /proc/sys/vm/drop_caches")
                os.system("echo 3 > /proc/sys/vm/drop_caches")
        except:
                pass

def make_request(url):
    try:
            req = Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0')
            # response = urlopen(req)
            response = checkStr(urlopen(req))
            link = response.read()
            response.close()
            print("link =", link)
            return link
    except:
        e = URLError #, e:
        print('We failed to open "%s".' % url)
        if hasattr(e, 'code'):
            print('We failed with error code - %s.' % e.code)
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)

def isExtEplayer3Available():
        return os.path.isfile(eEnv.resolve('$bindir/exteplayer3'))

def isStreamlinkAvailable():
        return os.path.isdir(eEnv.resolve('/usr/lib/python2.7/site-packages/streamlink'))

modechoices = [
                ("Default", _("IPTV(4097)")),
                ("Dvb", _("Dvb(1)")),
                ("eServiceUri", _("eServiceUri(8193)")),
            ]

if os.path.exists("/usr/bin/gstplayer"):
                        modechoices.append(("Gstreamer", _("Gstreamer(5001)")))
if os.path.exists("/usr/bin/exteplayer3"):
                        modechoices.append(("Exteplayer3", _("Exteplayer3(5002)")))

sessions = []
config.plugins.TivuStream                                = ConfigSubsection()
config.plugins.TivuStream.autoupd                = ConfigYesNo(default=True)
config.plugins.TivuStream.pthm3uf                = ConfigDirectory(default='/media/hdd/movie')
# config.plugins.TivuStream.code                   = ConfigInteger(limits=(0, 9999), default=1234)
config.plugins.TivuStream.code                   = ConfigNumber(default = 1234)
config.plugins.TivuStream.bouquettop             = ConfigSelection(default='Bottom', choices=['Bottom', 'Top'])
config.plugins.TivuStream.server                 = ConfigSelection(default='CORVOBOYS', choices=['PATBUWEB', 'CORVOBOYS'])
config.plugins.TivuStream.services               = ConfigSelection(default='Default', choices=modechoices)
config.plugins.TivuStream.strtext                = ConfigYesNo(default=True)
config.plugins.TivuStream.strtmain               = ConfigYesNo(default=True)

global Path_Movies
Path_Movies             = str(config.plugins.TivuStream.pthm3uf.value) + "/"
if Path_Movies.endswith("//") is True:
        Path_Movies = Path_Movies[:-1]

def server_ref():
        global server, host, upd_fr_txt, nt_upd_lnk,upd_nt_txt
        server = ''
        host = ''
        TEST1 = 'aHR0cDovL3BhdGJ1d2ViLmNvbQ=='
        ServerS1 = base64.b64decode(TEST1)
        data_s1 = 'L2lwdHYv' #
        FTP_1 = base64.b64decode(data_s1)
        TEST2 = 'aHR0cDovL2NvcnZvbmUuYWx0ZXJ2aXN0YS5vcmc='
        ServerS2 = base64.b64decode(TEST2)
        data_s2 = 'L2lwdHYv' #
        FTP_2 = base64.b64decode(data_s2)
        if config.plugins.TivuStream.server.value == 'PATBUWEB' :
                host = ServerS1
                server = ServerS1 + FTP_1
        else:
                host = ServerS2
                server = ServerS2 + FTP_2
        upd_fr_txt = ('%splugin/update.txt' % server)
        # upd_nt_txt = ('%se2liste/list.txt' % server)
        tex = 'aHR0cDovL3RpdnVzdHJlYW0ud2Vic2l0ZS9pb3MvbGlzdC50eHQ='
        upd_nt_txt = base64.b64decode(tex)
        nt_upd_lnk = ('wget %se2liste/note.txt -O /tmp/note.txt > /dev/null' % server)
        return server, host, upd_fr_txt, nt_upd_lnk
server_ref()
nnewtv = 'aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA='
servernew = base64.b64decode(nnewtv)
nnewm3u = 'aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2wucGhwP3A9NSZ1YT1UaVZ1U3RyZWFtJmY9MQ=='
servernewm3u = base64.b64decode(nnewm3u)
estm3u = 'aHR0cDovL3RpdnVzdHJlYW0uY29tL2ZoLnBocA=='
m3uest = base64.b64decode(estm3u)


global skin_path
skin_path = plugin_path
HD = getDesktop(0).size()
if HD.width() > 1280:
        if isDreamOS:
                skin_path = plugin_path + '/res/skins/fhd/dreamOs/'
        else:
                skin_path = plugin_path + '/res/skins/fhd/'
else:
        if isDreamOS:
                skin_path = plugin_path + '/res/skins/hd/dreamOs/'
        else:
                skin_path = plugin_path + '/res/skins/hd/'


def remove_line(filename, what):
        if os.path.isfile(filename):
                file_read = open(filename).readlines()
                file_write = open(filename, 'w')
                for line in file_read:
                        if what not in line:
                                file_write.write(line)
                file_write.close()



def m3ulistEntry(download):
        res = [download]
        white = 16777215
        yellow = 16776960
        green = 3828297
        col = 16777215
        backcol = 0
        blue = 4282611429
        png = '/usr/lib/enigma2/python/Plugins/Extensions/TivuStream/res/pics/setting2.png'
        if HD.width() > 1280:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(png)))
                res.append(MultiContentEntryText(pos=(60, 0), size=(1200, 50), font=7, text=download, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
        else:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 6), size=(34, 25), png=loadPNG(png)))
                res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=1, text=download, color = 0xa6d1fe, flags=RT_HALIGN_LEFT))# | RT_VALIGN_CENTER
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

class tvList(MenuList):

        def __init__(self, list):
                MenuList.__init__(self, list, False, eListboxPythonMultiContent)
                self.l.setFont(0, gFont('OpenFont2', 20))
                self.l.setFont(1, gFont('OpenFont2', 22))
                self.l.setFont(2, gFont('OpenFont2', 24))
                self.l.setFont(3, gFont('OpenFont2', 26))
                self.l.setFont(4, gFont('OpenFont2', 28))
                self.l.setFont(5, gFont('OpenFont2', 30))
                self.l.setFont(6, gFont('OpenFont2', 32))
                self.l.setFont(7, gFont('OpenFont2', 34))
                self.l.setFont(8, gFont('OpenFont2', 36))
                self.l.setFont(9, gFont('OpenFont2', 40))
                if HD.width() > 1280:
                        self.l.setItemHeight(50)
                else:
                        self.l.setItemHeight(40)

def tvListEntry(name,png):
        res = [name]
        png = '/usr/lib/enigma2/python/Plugins/Extensions/TivuStream/res/pics/setting.png'
        if HD.width() > 1280:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(png)))
                res.append(MultiContentEntryText(pos=(60, 0), size=(1200, 50), font=7, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
        else:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 4), size=(34, 25), png=loadPNG(png)))
                res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=1, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT))# | RT_VALIGN_CENTER
        return res


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
                self['title'] = Label(_('..:: TiVuStream Revolution V. %s ::..' % Version))
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
                if isDreamOS:
                    self.timer_conn = self.timer.timeout.connect(self.read)
                else:
                    self.timer.callback.append(self.read)

        def read(self):
                try:
                    destr = plugin_path + 'list.txt'
                    onserver2 = str(upd_nt_txt)
                    with open(destr, 'w') as f:
                            content = make_request(onserver2)
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
                png = '/usr/lib/enigma2/python/Plugins/Extensions/TivuStream/res/pics/setting.png'
                for x in Panel_list:
                        list.append(tvListEntry(x,png))
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
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0xJnQ9MA=="
                elif sel == ("TOP ITALIA"):
                        namex = "topitalia"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0xJnQ9MQ=="
                elif sel == ("SPORT ITALIA"):
                        namex = "sportitalia"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0xJnQ9Mg=="
                elif sel == ("SPORT LIVE"):
                        namex = "sportlive"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0xJnQ9Mw=="
                elif sel == ("SPORT ESTERI"):
                        namex = "sportesteri"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0xJnQ9NA=="
                elif sel == ("MUSICA"):
                        namex = "musica"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0xJnQ9NQ=="
                elif sel == ("NEWS"):
                        namex = "news"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0xJnQ9Ng=="
                elif sel == ("ESTERO"):
                        namex = "estero"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0xJnQ9Nw=="
                # elif sel == ("ESTERO2"):
                        # namex = "estero2"
                        # lnk = ""
                        # # self.M3uPlay2()
                elif sel == ("REGIONALI"):
                        namex = "regionali"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0xJnQ9OA=="
                elif sel == ("RELAX"):
                        namex = "relax"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0xJnQ9OQ=="

                elif sel == ("MOVIE TUTTI"):
                        namex = "movietutti"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MA=="
                elif sel == ("SERIE"):
                        namex = "serie"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MTA="
                elif sel == ("SERIE TV: 0-9"):
                        namex = "serietv09"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MTE="
                elif sel == ("SERIE TV: A-E"):
                        namex = "serietvae"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MTI="
                elif sel == ("SERIE TV: F-K"):
                        namex = "serietvfk"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MTM="
                elif sel == ("SERIE TV: L-R"):
                        namex = "serietvlr"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MTQ="
                elif sel == ("SERIE TV: S-Z"):
                        namex = "serietvsz"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MTU="
                elif sel == ("FILM"):
                        namex = "film"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MjA="
                elif sel == ("FILM RECENTI"):
                        namex = "filmrecenti"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MjE="
                elif sel == ("FILM: 0-9"):
                        namex = "film09"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MjI="
                elif sel == ("FILM: A-F"):
                        namex = "filmaf"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MjM="
                elif sel == ("FILM: G-L"):
                        namex = "filmgl"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MjQ="
                elif sel == ("FILM: M-R"):
                        namex = "filmmr"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MjU="
                elif sel == ("FILM: S-Z"):
                        namex = "filmsz"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9MjY="
                elif sel == ("FILM IN VERSIONE ORIGINALE"):
                        namex = "movieoriginal"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0yJnQ9Mjc="

                elif sel == ("RADIO TUTTI"):
                        namex = "radiotutti"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0zJnQ9MA=="
                elif sel == ("RADIO ITALIA"):
                        namex = "radioitalia"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0zJnQ9MQ=="
                elif sel == ("RADIO INT"):
                        namex = "radioint"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0zJnQ9Mg=="
                elif sel == ("DASH RADIO"):
                        namex = "dashradio"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD0zJnQ9Mw=="

                elif sel == ("LIVE XXX"):
                        namex = "livexxx"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD01"
                elif sel == ("MOVIE XXX"):
                        namex = "moviexxx"
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA/cD00"

                elif sel == ("="):
                        namex = "=="
                        lnk = "aHR0cHM6Ly90aXZ1c3RyZWFtLmNvbS90c2xFbi5waHA="
                else:
                        self.mbox = self.session.open(openMessageBox, _('Bouquet not installed'), openMessageBox.TYPE_ERROR, timeout=4)
                        return
                # if namex == ("estero2"):
                    # self.M3uPlay2(namex)
                    # return
                # else:
                self.instal_listTv(namex,lnk)


        def instal_listTv(self, namex, lnk):
                name = namex
                # if namex == ("estero2"):
                    # self.M3uPlay2(namex)
                    # return
                lnk = lnk
                pin = 2808
                pin2 = int(config.plugins.TivuStream.code.value)
                groupname = 'userbouquet.tivustream.tv'
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
                    groupname = 'userbouquet.tivustream.tv'
                    bouquet = 'bouquets.tv'
                    if 'radio' in name :
                        bqtname = 'subbouquet.%s.radio' % name
                        number = '2'
                    else:
                        bqtname = 'subbouquet.%s.tv' % name
                        number = '1'
                    in_bouquets = 0
                    linetv =0
                    if os.path.isfile('/etc/enigma2/%s' % bqtname):
                            os.remove('/etc/enigma2/%s' % bqtname)
                    if not os.path.isfile('/etc/enigma2/userbouquet.tivustream.tv'):
                        filename = '/etc/enigma2/userbouquet.tivustream.tv'
                        with open(filename, 'a+') as f:
                            nameString = "#NAME tivustream.com"
                            if nameString not in f:
                                f.write(nameString + '\r\n')

                    os.system('chmod 0644 /etc/enigma2/userbouquet.tivustream.tv' )
                    namebqt = ('/etc/enigma2/%s' % bqtname)
                    # onserver = str(servernew) + lnk
                    lnk = base64.b64decode(lnk)
                    onserver = lnk

                    with open(namebqt, 'w') as f:
                            content = make_request(onserver)
                            # ##DESCRIPTION [COLOR lime]---LAST UPDATE 01-10-2020 H. 19.10---[/COLOR]
                            # regexcat = "DESCRIPTION [(.*?]).*?([.*?])\\n"
                            # match = re.compile(regexcat, re.DOTALL).findall(content)
                            # for color, color2 in match:
                                # color = color.replace(color, "").replace("[", "").replace("]")
                                # color2 = color2.replace(color, "")
                                # color2 = color2.replace("[", "").replace("]")
                            f.write(content)

                    self.mbox = self.session.open(openMessageBox, _('Check out the favorites list ...'), openMessageBox.TYPE_INFO, timeout=5)
                    with open('/etc/enigma2/bouquets.tv', 'a+') as f:
                        bouquetTvString = '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + groupname + '" ORDER BY bouquet\n'
                        if bouquetTvString not in f:
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
                    dirgroupname = ('/etc/enigma2/%s' % groupname)

                    for line in open(dirgroupname):
                        if bqtname in line:
                            linetv = 1
                        else:
                            with open(dirgroupname, 'a+' ) as f:
                                bouquetTvString = ('#SERVICE 1:7:%s:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % (number, bqtname))
                                if bouquetTvString not in f:
                                    f.write(bouquetTvString)

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
            self.session.openWithCallback(self.reloadSettings, openMessageBox, _('Shuffle Favorite List in Progress') + '\n' + _('Wait please ...'), openMessageBox.TYPE_INFO, timeout=10)

        def reloadSettings(self, result):
            if result:
               ReloadBouquet()

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
                        ReloadBouquet()

        def M3uPlay(self):
                tivustream = 'tivustream'
                self.session.open(OpenM3u)

        # def M3uPlay2(self,namex):
                # self.session.open(OpenM3u,namex)

        def scsetup(self):
                self.session.open(OpenConfig)

class OpenM3u(Screen):
        def __init__(self, session):
                self.session = session
                skin = skin_path + '/OpenM3u.xml'
                f = open(skin, 'r')
                self.skin = f.read()
                f.close()
                Screen.__init__(self, session)
                self.list = []
                self['list'] = tvList([])
                global srefInit
                self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
                srefInit = self.initialservice
                self['title'] = Label(_('..:: TiVuStream Revolution V. %s ::..' % Version))
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
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()

                # if namex == 'estero2':
                    # try:
                        # cmd66 = 'rm -f ' + Path_Movies + 'estero.m3u'
                        # os.system(cmd66)
                        # destx = self.name + 'estero.m3u'
                        # onserver2 = str(m3uest)
                        # with open(destx, 'w') as f:
                            # content = make_request(onserver2)
                            # f.write(content)
                    # except Exception as ex:
                        # print(ex)
                # else:

                try:
                        cmd66 = 'rm -f ' + Path_Movies + 'tivustream.m3u'
                        os.system(cmd66)
                        destx = self.name + 'tivustream.m3u'
                        onserver2 = str(servernewm3u)
                        with open(destx, 'w') as f:
                            content = make_request(onserver2)
                            f.write(content)
                except Exception as ex:
                        print(ex)
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
                # selection = str(self['list'].getCurrent())
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
                        self.session.openWithCallback(self.callMyMsg1,openMessageBox,_("Do you want to remove?"), openMessageBox.TYPE_YESNO)

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
                        pth = self.name
                        bqtname = 'userbouquet.%s.tv' % name
                        self.iConsole = iConsole()
                        desk_tmp = hls_opt = ''
                        in_bouquets = 0
                        if os.path.isfile('/etc/enigma2/%s' % bqtname):
                                os.remove('/etc/enigma2/%s' % bqtname)
                        with open('/etc/enigma2/%s' % bqtname, 'w') as outfile:
                                outfile.write('#NAME %s\r\n' % name.capitalize())
                                for line in open(pth + '/%s' % name):
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
                                if in_bouquets != 0:
                                        if os.path.isfile('/etc/enigma2/%s' % bqtname) and os.path.isfile('/etc/enigma2/bouquets.tv'):
                                                remove_line('/etc/enigma2/bouquets.tv', bqtname)
                                                with open('/etc/enigma2/bouquets.tv', 'a') as outfile:
                                                        outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % bqtname)
                                                        outfile.close()
                        self.mbox = self.session.open(openMessageBox, _('Shuffle Favorite List in Progress') + '\n' + _('Wait please ...'), openMessageBox.TYPE_INFO, timeout=5)
                        ReloadBouquet()

        def create_bouquet(self):
                        idx = self['list'].getSelectionIndex()
                        self.convert = True
                        name = self.names[idx]
                        pth = self.name
                        bqtname = 'userbouquet.%s.tv' % name
                        self.iConsole = iConsole()
                        desk_tmp = hls_opt = ''
                        in_bouquets = 0
                        if os.path.isfile('/etc/enigma2/%s' % bqtname):
                                os.remove('/etc/enigma2/%s' % bqtname)
                        with open('/etc/enigma2/%s' % bqtname, 'w') as outfile:
                                outfile.write('#NAME %s\r\n' % name.capitalize())
                                for line in open(pth + '/%s' % name):
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

                                if in_bouquets != 0:
                                        if os.path.isfile('/etc/enigma2/%s' % bqtname) and os.path.isfile('/etc/enigma2/bouquets.tv'):
                                                remove_line('/etc/enigma2/bouquets.tv', bqtname)
                                                with open('/etc/enigma2/bouquets.tv', 'a') as outfile:
                                                        outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % bqtname)
                                                        outfile.close()
                        self.mbox = self.session.open(openMessageBox, _('Shuffle Favorite List in Progress') + '\n' + _('Wait please ...'), openMessageBox.TYPE_INFO, timeout=5)
                        ReloadBouquet()

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
                f.close()
                Screen.__init__(self, session)
                self.list = []
                self['list'] = tvList([])
                self['title'] = Label(_('..:: TiVuStream Revolution V. %s ::..' % Version))
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
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
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
                        search = result
                        try:
                                if fileExists(self.name):
                                        f1 = open(self.name, "r+")
                                        fpage = f1.read()
                                        regexcat = "EXTINF.*?,(.*?)\\n(.*?)\\n"
                                        match = re.compile(regexcat, re.DOTALL).findall(fpage)
                                        for name, url in match:
                                                if str(search).lower() in name.lower():
                                                                global search_ok
                                                                search_ok = True
                                                                url = url.replace(" ", "")
                                                                url = url.replace("\\n", "")
                                                                self.names.append(name)
                                                                self.urls.append(url)
                                        if search_ok == True:
                                                m3ulist(self.names, self["list"])
                                                self["live"].setText('N.' + str(len(self.names)) + " Stream")
                                        else:
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

        def showError(self, error):
                        OnclearMem()
                        self.downloading = False
                        self.session.open(openMessageBox, _('Download Failed!!!'), openMessageBox.TYPE_INFO, timeout=5)

        def playList(self):
                global search_ok
                search_ok = False
                self.names = []
                self.urls = []
                try:
                        if fileExists(self.name):
                                f1 = open(self.name, 'r+')
                                fpage = f1.read()
                                regexcat = 'EXTINF.*?,(.*?)\\n(.*?)\\n'
                                match = re.compile(regexcat, re.DOTALL).findall(fpage)
                                for name, url in match:
                                        url = url.replace(' ', '')
                                        url = url.replace('\\n', '')
                                        url = url.replace('https', 'http')
                                        self.names.append(name)
                                        self.urls.append(url)
                                m3ulist(self.names, self['list'])
                                self["live"].setText('N.' + str(len(self.names)) + " Stream")
                except Exception as ex:
                        print(ex)

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


class M3uPlay2(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarAudioSelection, TvInfoBarShowHide,InfoBarSubtitleSupport):
        STATE_IDLE = 0
        STATE_PLAYING = 1
        STATE_PAUSED = 2
        ENABLE_RESUME_SUPPORT = True
        ALLOW_SUSPEND = True

        def __init__(self, session, name, url):
                Screen.__init__(self, session)
                self.skinName = 'MoviePlayer'
                title = 'Play Stream'
                self['list'] = MenuList([])
                InfoBarMenu.__init__(self)
                InfoBarNotifications.__init__(self)
                InfoBarBase.__init__(self, steal_current_service=True)
                TvInfoBarShowHide.__init__(self)
                InfoBarSubtitleSupport.__init__(self)
                InfoBarAudioSelection.__init__(self)
                self['actions'] = ActionMap(['WizardActions',
                 'MoviePlayerActions',
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
                 'info': self.showIMDB,
                 'stop': self.leavePlayer,
                 'cancel': self.cancel,
                 'back': self.cancel}, -1)
                self.allowPiP = False
                self.service = None
                service = None
                InfoBarSeek.__init__(self, actionmap='InfobarSeekActions')
                url = url.replace(':', '%3a')
                self.url = url
                self.name = name
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                self.state = self.STATE_PLAYING
                self.onLayoutFinish.append(self.openPlay)
                self.onClose.append(self.cancel)


        def showIMDB(self):
                if '.mp4' in self.url or '.mkv' in self.url or '.flv' in self.url or '.avi' in self.url:
                        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/TMBD/plugin.pyo"):
                                from Plugins.Extensions.TMBD.plugin import TMBD
                                text_clear = self.name
                                text = charRemove(text_clear)
                                self.session.open(TMBD, text, False)
                        elif os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/IMDb/plugin.pyo"):
                                from Plugins.Extensions.IMDb.plugin import IMDB
                                text_clear = self.name
                                text = charRemove(text_clear)
                                HHHHH = text
                                self.session.open(IMDB, HHHHH)
                        else:
                                text_clear = self.name
                                self.session.open(openMessageBox, text_clear, openMessageBox.TYPE_INFO)
                else:
                        self.session.open(openMessageBox, _('Only VOD Movie allowed or not .ext Filtered!!!'), openMessageBox.TYPE_INFO, timeout=9)

        def openPlay(self):
                url = str(self.url)
                ref = '4097:0:1:0:0:0:0:0:0:0:' + url
                if config.plugins.TivuStream.services.value == 'Gstreamer':
                                ref = '5001:0:1:0:0:0:0:0:0:0:' + url
                elif config.plugins.TivuStream.services.value == 'Exteplayer3':
                                ref = '5002:0:1:0:0:0:0:0:0:0:' + url
                elif config.plugins.TivuStream.services.value == 'eServiceUri':
                                # ref = '8193:0:1:0:0:0:0:0:0:0:yt%3a//' + url + '<videoid>'
                                ref = '8193:0:1:0:0:0:0:0:0:0:' + url
                elif config.plugins.TivuStream.services.value == 'Dvb':
                                ref = '1:0:1:0:0:0:0:0:0:0:' + url
                else:
                        if config.plugins.TivuStream.services.value == 'Iptv':
                                ref = '4097:0:1:0:0:0:0:0:0:0:' + url
                sref = eServiceReference(ref)
                sref.setName(self.name)
                self.session.nav.stopService()
                self.session.nav.playService(sref)

        def keyNumberGlobal(self, number):
                self['text'].number(number)

        def cancel(self):
                self.session.nav.stopService()
                self.session.nav.playService(srefInit)
                self.close()

        def ok(self):
                if self.shown:
                        self.hideInfobar()
                else:
                        self.showInfobar()

        def keyLeft(self):
                self['text'].left()

        def keyRight(self):
                self['text'].right()

        def showVideoInfo(self):
                if self.shown:
                        self.hideInfobar()
                if self.infoCallback is not None:
                        self.infoCallback()
                return

        def showAfterSeek(self):
                if isinstance(self, TvInfoBarShowHide):
                        self.doShow()

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
                self['title'] = Label(_('..:: TiVuStream Revolution V. %s by Lululla ::..' % Version))
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
                if mutableList is not None:
                        if service is None:
                                return
                        if not mutableList.addService(service):
                                mutableList.flushChanges()
                return

        def getMutableList(self, root = eServiceReference()):
                if self.mutableList is not None:
                        return self.mutableList
                else:
                        serviceHandler = eServiceCenter.getInstance()
                        if not root.valid():
                                root = self.getRoot()
                        list = root and serviceHandler.list(root)
                        if list is not None:
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
                self['title'] = Label(_('..:: TiVuStream Revolution V. %s ::..' % Version))
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
                self["setupActions"] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions', 'VirtualKeyboardActions', 'ActiveCodeActions'],
                {
                                "red": self.extnok,
                                "cancel": self.extnok,
                                'yellow': self.msgupdt1,
                                "green": self.cfgok,
                                "left": self.keyLeft,
                                "right": self.keyRight,
                                'showVirtualKeyboard': self.KeyText,
                                "ok": self.Ok_edit
                }, -1)
                self.list = []
                ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
                self.createSetup()
                self.onLayoutFinish.append(self.checkUpdate)
                self.onLayoutFinish.append(self.layoutFinished)

        def checkUpdate(self):
                # server_ref()
                try:
                        fp = ''
                        destr = plugin_path + 'update.txt'
                        req = Request(upd_fr_txt)
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0')
                        # fp = urlopen(req)
                        fp = checkStr(urlopen(req))
                        fp = fp.read()
                        print("fp3 =", fp)

                        with open(destr, 'w') as f:
                            f.write(fp)
                            f.close
                        with open(destr, 'r') as fp:
                            count = 0
                            self.labeltext = ''
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
                if isDreamOS:
                        self.timerx_conn = self.timerx.timeout.connect(self.msgupdt2)
                else:
                        self.timerx.callback.append(self.msgupdt2)

        def layoutFinished(self):
                self.setTitle(self.setup_title)

        def createSetup(self):
                self.editListEntry = None
                self.list = []
                self.list.append(getConfigListEntry(_('Server:'), config.plugins.TivuStream.server, _("Server selection")))
                self.list.append(getConfigListEntry(_('Auto Update Plugin:'), config.plugins.TivuStream.autoupd, _("Automatic plugin update")))
                self.list.append(getConfigListEntry(_('Personal Password:'), config.plugins.TivuStream.code, _("Enter the password to download Lists XXX Adults")))
                self.list.append(getConfigListEntry(_('IPTV bouquets location '), config.plugins.TivuStream.bouquettop, _("Configure position of the bouquets of the converted lists")))
                self.list.append(getConfigListEntry(_('Player folder List <.m3u>:'), config.plugins.TivuStream.pthm3uf, _("Folder path containing the .m3u files")))
                self.list.append(getConfigListEntry(_('Services Player Reference type'), config.plugins.TivuStream.services, _("Configure Service Player Reference")))
                self.list.append(getConfigListEntry(_('Link in Extensions Menu:'), config.plugins.TivuStream.strtext, _("Show Plugin in Extensions Menu")))
                self.list.append(getConfigListEntry(_('Link in Main Menu:'), config.plugins.TivuStream.strtmain, _("Show Plugin in Main Menu")))
                self['config'].list = self.list
                self["config"].setList(self.list)

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

        def keyLeft(self):
                ConfigListScreen.keyLeft(self)
                self.createSetup()

        def keyRight(self):
                ConfigListScreen.keyRight(self)
                self.createSetup()

        def Ok_edit(self):
                ConfigListScreen.keyOK(self)
                sel = self['config'].getCurrent()[1]
                if sel and sel == config.plugins.TivuStream.pthm3uf:
                        self.setting = 'pthm3uf'
                        self.openDirectoryBrowser(config.plugins.TivuStream.pthm3uf.value)
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
                except Exception as e:
                        print(ex)

        def openDirectoryBrowserCB(self, path):
                if path is not None:
                        if self.setting == 'pthm3uf':
                                config.plugins.TivuStream.pthm3uf.setValue(path)
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
                if callback is not None and len(callback):
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
                self.session.openWithCallback(self.runupdate, openMessageBox, _('New Online Version!') + '\n\n' + _('Update Plugin to Version %s ?' % self.version), openMessageBox.TYPE_YESNO)

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
                        self.session.open(OpenConsole, _('Update Plugin: %s') % dom, ['tar -xvf /tmp/tivustream.tar -C /'], finishedCallback=self.ipkrestrt, closeOnSuccess=False)

        def ipkrestrt(self):
                epgpath = '/media/hdd/epg.dat'
                epgbakpath = '/media/hdd/epg.dat.bak'
                if os.path.exists(epgbakpath):
                        os.remove(epgbakpath)
                if os.path.exists(epgpath):
                        copyfile(epgpath, epgbakpath)
                self.session.open(TryQuitMainloop, 3)

class OpenConsole(Screen):

        def __init__(self, session, title = None, cmdlist = None, finishedCallback = None, closeOnSuccess = False):
                self.session = session
                skin = skin_path + '/OpenConsole.xml'
                f = open(skin, 'r')
                self.skin = f.read()
                f.close()
                Screen.__init__(self, session)
                self.finishedCallback = finishedCallback
                self.closeOnSuccess = closeOnSuccess
                self['text'] = ScrollLabel('')
                self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.cancel,
                 'back': self.cancel,
                 'up': self['text'].pageUp,
                 'down': self['text'].pageDown}, -1)
                self.cmdlist = cmdlist
                self.container = eConsoleAppContainer()
                self.run = 0
                try:
                        self.container.appClosed.append(self.runFinished)
                except:
                        self.appClosed_conn = self.container.appClosed.connect(self.runFinished)
                try:
                        self.container.dataAvail.append(self.dataAvail)
                except:
                        self.dataAvail_conn = self.container.dataAvail.connect(self.dataAvail)
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
                        str = self['text'].getText()
                        str += _('Execution finished !!')
                        self['text'].setText(str)
                        self['text'].lastPage()
                        if self.finishedCallback is not None:
                                self.finishedCallback()
                        if not retval and self.closeOnSuccess:
                                self.cancel()
                return

        def cancel(self):
                if self.run == len(self.cmdlist):
                        self.close()
                try:
                        self.container.appClosed.remove(self.runFinished)
                except:
                        self.appClosed_conn = None

                try:
                        self.container.dataAvail.remove(self.dataAvail)
                except:
                        self.dataAvail_conn = None

                return

        def dataAvail(self, str):
                self['text'].setText(self['text'].getText() + str)


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
                        if isDreamOS:
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
                if self.timeout_default is not None:
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
                self['text'] = ScrollLabel()
                self['actions'] = ActionMap(['OkCancelActions',
                 'DirectionActions','ColorActions', 'SetupActions'], {'ok': self.clsgo,
                 'cancel': self.clsgo,
                 'back': self.clsgo,
                 'red': self.clsgo,
                 'up': self['text'].pageUp,
                 'down': self['text'].pageDown,
                 'left': self['text'].pageUp,
                 'right': self['text'].pageDown,
                 'green': self.clsgo}, -1)
                self.onLayoutFinish.append(self.checkDwnld)


        def checkDwnld(self):
                server_ref()
                self.icount = 0
                self['text'].setText(_('\n\n\nCheck Connection wait please...'))
                self.timer = eTimer()
                self.timer.start(100, 1)

                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.OpenCheck)
                else:
                        self.timer.callback.append(self.OpenCheck)

        def OpenCheck(self):
                url3 = str(upd_fr_txt)
                getPage(url3).addCallback(self.ConnOK).addErrback(self.error)

        def ConnOK(self, data):
                URL = ('%se2liste/note.txt'% server)
                try:
                        self['text'].setText(make_request(URL))
                except:
                        self['text'].setText(_('\n\n' + 'Error downloading updates!'))

        def error(self, error):
                self['text'].setText(_('\n\n' + 'Server Off !') + '\n' + _('check SERVER in config'))


        def clsgo(self):
                self.session.openWithCallback(self.close, OpenScript)

def checks():
    chekin= False
    if checkInternet():
            chekin = True
    return

def main(session, **kwargs):
        if checks:
                add_skin_font()
                if isDreamOS:
                        session.open(OpenScript)
                elif PY3:
                        session.open(OpenScript)
                else:
                        session.open(plgnstrt)
        else:
                session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)

def main2(session, **kwargs):
        if checkInternet():
                session.open(OpenM3u)
        else:
                session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)

def mainmenu(session, **kwargs):
        if menuid == 'mainmenu':
                return [(_('TiVuStream Revolution'), main, 'TiVuStream Revolution', 4)]
        else:
                return []

def cfgmain(menuid):
        if menuid == 'mainmenu':
                return [('TiVuStream Revolution',
                 main,
                 'TiVuStream Revolution by Lululla',
                 44)]
        else:
                return []

def Plugins(**kwargs):
        icona = 'logo.png'
        if not isDreamOS:
                icona = skin_path + '/logo.png'
        extDescriptor = PluginDescriptor(name='TiVuStream Revolution', description=_('TiVuStream Revolution'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon=icona, fnc=main)
        mainDescriptor = PluginDescriptor(name='TiVuStream Revolution', description=_('TiVuStream Revolution v.' + currversion), where=PluginDescriptor.WHERE_MENU, icon=icona, fnc=cfgmain)
        result = [PluginDescriptor(name='TiVuStream Revolution', description=_('TiVuStream Revolution v.' + currversion), where=[PluginDescriptor.WHERE_PLUGINMENU], icon=icona, fnc=main)]
        if config.plugins.TivuStream.strtext.value:
                result.append(extDescriptor)
        if config.plugins.TivuStream.strtmain.value:
                result.append(mainDescriptor)
        return result

def charRemove(text):
                char = ["1080p",
                 "2018",
                 "2019",
                 "2020",
                 "480p",
                 "4K",
                 "720p",
                 "ANIMAZIONE",
                 "APR",
                 "AVVENTURA",
                 "BIOGRAFICO",
                 "BDRip",
                 "BluRay",
                 "CINEMA",
                 "COMMEDIA",
                 "DOCUMENTARIO",
                 "DRAMMATICO",
                 "FANTASCIENZA",
                 "FANTASY",
                 "FEB",
                 "GEN",
                 "GIU",
                 "HDCAM",
                 "HDTC",
                 "HDTS",
                 "LD",
                 "MAFIA",
                 "MAG",
                 "MARVEL",
                 "MD",
                 "ORROR",
                 "NEW_AUDIO",
                 "POLIZ",
                 "R3",
                 "R6",
                 "SD",
                 "SENTIMENTALE",
                 "TC",
                 "TEEN",
                 "TELECINE",
                 "TELESYNC",
                 "THRILLER",
                 "Uncensored",
                 "V2",
                 "WEBDL",
                 "WEBRip",
                 "WEB",
                 "WESTERN",
                 "-",
                 "_",
                 ".",
                 "+",
                 "[",
                 "]"]

                myreplace = text
                for ch in char:
                        myreplace = myreplace.replace(ch, "").replace("  ", " ").replace("       ", " ").strip()
                return myreplace
