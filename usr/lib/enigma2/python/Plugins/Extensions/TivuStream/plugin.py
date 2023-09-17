#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
****************************************
*        coded by Lululla              *
*                                      *
*             01/09/2023               *
****************************************
Info http://t.me/tivustream
'''
from __future__ import print_function
from . import _
from . import Utils
try:
    from Components.AVSwitch import eAVSwitch as AVSwitch
except Exception:
    from Components.AVSwitch import iAVSwitch as AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.MultiContent import MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap
from Components.PluginComponent import plugins
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.Sources.Progress import Progress
from Components.Sources.StaticText import StaticText
from Components.config import config, ConfigSelection, ConfigText
from Components.config import ConfigEnableDisable, ConfigYesNo
from Components.config import getConfigListEntry, ConfigDirectory
from Components.config import ConfigSubsection, configfile
from Plugins.Plugin import PluginDescriptor
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import SCOPE_PLUGINS
from Tools.Directories import resolveFilename, copyfile
from Tools.Downloader import downloadWithProgress
from enigma import eConsoleAppContainer
from enigma import RT_VALIGN_CENTER
from enigma import RT_HALIGN_LEFT
from enigma import eListboxPythonMultiContent
from enigma import eTimer
from enigma import gPixmapPtr
from enigma import gFont
from enigma import ePicLoad
from enigma import loadPNG
from enigma import getDesktop
import os
import ssl
import sys
import six
import codecs
PY3 = sys.version_info.major >= 3
print('Py3: ', PY3)
if PY3:
    from urllib.request import urlopen
    PY3 = True
else:
    from urllib2 import urlopen


if sys.version_info >= (2, 7, 9):
    try:
        sslContext = ssl._create_unverified_context()
    except:
        sslContext = None

try:
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


currversion = '3.2'
# Version = currversion + ' - 14/01/2022'
title_plug = '..:: TivuStream Revolution V. %s ::..' % currversion
name_plug = 'TivuStream Revolution'
Credits = 'Info http://t.me/tivustream'
Maintener = 'Maintener @Lululla'
dir_enigma2 = '/etc/enigma2/'
service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'
plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/TivuStream'
res_plugin_path = os.path.join(plugin_path, 'res/')
# ================
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
config.plugins.TivuStream = ConfigSubsection()
config.plugins.TivuStream.autoupd = ConfigYesNo(default=True)
config.plugins.TivuStream.pthm3uf = ConfigDirectory(default='/media/hdd/movie')
try:
    from Components.UsageConfig import defaultMoviePath
    downloadpath = defaultMoviePath()
    config.plugins.TivuStream.pthm3uf = ConfigDirectory(default=downloadpath)
except:
    if os.path.exists("/usr/bin/apt-get"):
        config.plugins.TivuStream.pthm3uf = ConfigDirectory(default='/media/hdd/movie')
# config.plugins.TivuStream.code = ConfigNumber(default = 1234)
config.plugins.TivuStream.code = ConfigText(default="1234")
config.plugins.TivuStream.bouquettop = ConfigSelection(default='Bottom', choices=['Bottom', 'Top'])
config.plugins.TivuStream.server = ConfigSelection(default='CORVOBOYS', choices=['DEFAULT', 'CORVOBOYS'])
config.plugins.TivuStream.services = ConfigSelection(default='4097', choices=modechoices)
config.plugins.TivuStream.cachefold = ConfigDirectory(default='/media/hdd/')
config.plugins.TivuStream.strtext = ConfigYesNo(default=True)
config.plugins.TivuStream.strtmain = ConfigYesNo(default=True)
config.plugins.TivuStream.thumb = ConfigYesNo(default=False)
config.plugins.TivuStream.thumbpic = ConfigYesNo(default=False)
config.plugins.TivuStream.dowm3u = ConfigYesNo(default=False)
global pngori, skin_path
global Path_Movies
Path_Movies = str(config.plugins.TivuStream.pthm3uf.value) + "/"
if Path_Movies.endswith("\/\/") is True:
    Path_Movies = Path_Movies[:-1]
print('patch movies: ', Path_Movies)

tvstrvl = config.plugins.TivuStream.cachefold.value + "tivustream"
tmpfold = config.plugins.TivuStream.cachefold.value + "tivustream/tmp"
picfold = config.plugins.TivuStream.cachefold.value + "tivustream/pic"
_firstStarttvstream = True

if not os.path.exists(tvstrvl):
    os.system("mkdir " + tvstrvl)
if not os.path.exists(tmpfold):
    os.system("mkdir " + tmpfold)
if not os.path.exists(picfold):
    os.system("mkdir " + picfold)


pngori = os.path.join(plugin_path, 'res/pics/nasa3.jpg')
png = os.path.join(plugin_path, 'res/pics/setting.png')


screenwidth = getDesktop(0).size()
if screenwidth.width() == 2560:
    skin_path = plugin_path + '/res/skins/uhd/'
elif screenwidth.width() == 1920:
    skin_path = plugin_path + '/res/skins/fhd/'
else:
    skin_path = plugin_path + '/res/skins/hd/'
if Utils.DreamOS():
    skin_path = skin_path + 'dreamOs/'


class tvList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if screenwidth.width() == 2560:
            self.l.setItemHeight(60)
            textfont = int(42)
            self.l.setFont(0, gFont('Regular', textfont))
        elif screenwidth.width() == 1920:
            self.l.setItemHeight(50)
            textfont = int(30)
            self.l.setFont(0, gFont('Regular', textfont))
        else:
            self.l.setItemHeight(30)
            textfont = int(24)
            self.l.setFont(0, gFont('Regular', textfont))


def tvListEntry(name, png):
    res = [name]
    if 'radio' in name.lower():
        png = os.path.join(plugin_path, 'res/pics/radio.png')
    elif 'webcam' in name.lower():
        png = os.path.join(plugin_path, 'res/pics/webcam.png')
    elif 'music' in name.lower():
        png = os.path.join(plugin_path, 'res/pics/music.png')
    elif 'sport' in name.lower():
        png = os.path.join(plugin_path, 'res/pics/sport.png')
    else:
        png = os.path.join(plugin_path, 'res/pics/tv.png')
    if screenwidth.width() == 2560:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(50, 50), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(110, 0), size=(1200, 50), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    elif screenwidth.width() == 1920:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(40, 40), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(70, 0), size=(1000, 50), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(3, 3), size=(30, 30), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(50, 0), size=(500, 30), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


Panel_list = [('This plugin is no longer supported')]


class MainTvStream(Screen):
    def __init__(self, session):
        self.session = session
        global _session
        _session = session
        skin = os.path.join(skin_path, 'MainTvStream.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self.setup_title = _('Channel List')
        self['list'] = tvList([])
        self.icount = 0
        self['listUpdate'] = Label()
        self['title'] = Label(_(title_plug))
        self['Maintener'] = Label('%s' % Maintener)
        self['info'] = Label('%s' % Credits)
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button()
        self['key_yellow'] = Button('')
        self["key_blue"] = Button(_("Player"))
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'MenuActions',
                                     'EPGSelectActions',
                                     'ButtonSetupActions'], {'ok': self.closerm,
                                                             'menu': self.closerm,
                                                             'red': self.closerm,
                                                             'green': self.closerm,
                                                             'info': self.closerm,
                                                             'yellow': self.closerm,
                                                             'blue': self.closerm,
                                                             'back': self.closerm,
                                                             'cancel': self.closerm}, -1)
        self.onLayoutFinish.append(self.updateMenuList)

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
        if sel == ("This plugin is no longer supported"):
            self.mbox = self.session.open(MessageBox, _('This plugin is no longer supported'), MessageBox.TYPE_ERROR, timeout=4)
            return

    def closerm(self):
        self.close()


class OpenConfig(Screen, ConfigListScreen):
    def __init__(self, session):
        self.session = session
        global _session
        _session = session
        skin = os.path.join(skin_path, 'OpenConfig.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self.setup_title = _("TiVuStream Config")
        self.onChangedEntry = []
        info = '***'
        self['title'] = Label(_(title_plug))
        self['Maintener'] = Label('%s' % Maintener)
        self['info'] = Label('%s' % Credits)
        self["paypal"] = Label()
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Save'))
        self['key_yellow'] = Button(_('Update'))
        self["key_blue"] = Button(_(''))
        self["key_blue"].hide()
        self['list'] = Label(info)
        self["description"] = Label(_(''))
        self.cbUpdate = False
        self['actions'] = ActionMap(["SetupActions",
                                     "ColorActions",
                                     "VirtualKeyboardActions"], {'cancel': self.extnok,
                                                                 'red': self.extnok,
                                                                 'green': self.cfgok,
                                                                 'yellow': self.msgupdt1,
                                                                 'showVirtualKeyboard': self.KeyText,
                                                                 'ok': self.Ok_edit,
                                                                 }, -2)
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self.createSetup()
        self.onLayoutFinish.append(self.checkUpdate)
        self.onLayoutFinish.append(self.layoutFinished)
        if self.setInfo not in self['config'].onSelectionChanged:
            self['config'].onSelectionChanged.append(self.setInfo)

    def checkUpdate(self):
        try:
            fp = ''
            destr = plugin_path + 'update.txt'
            fp = Utils.ReadUrl('')
            fp = six.ensure_str(fp)
            with open(destr, 'w') as f:
                f.write(fp)
                f.close()
            with open(destr, 'r') as fp:
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
                    self['list'].setText(_('Version: ') + currversion + '\n' + _('No updates!') + '\n' + _('if you like it you can make a free donation') + '\n' + _('www.paypal.me/TivuStream'))
                else:
                    self.cbUpdate = True
                    print("Update True =", s1)
                    updatestr = (_('Version: ') + currversion + '\n' + _('Last update ') + s1 + ' ' + _('available!') + '\n' + _('ChangeLog:') + self.info)
                    self['list'].setText(updatestr)
        except:
            self.cbUpdate = False
            self['list'].setText(_('No updates available') + '\n' + _('No internet connection or server OFF') + '\n' + _('Please try again later or change SERVER to config menu.'))
        self.timerx = eTimer()
        self.timerx.start(100, 1)
        if Utils.DreamOS():
            self.timerx_conn = self.timerx.timeout.connect(self.msgupdt2)
        else:
            self.timerx.callback.append(self.msgupdt2)

    def paypal2(self):
        conthelp = "If you like what I do you\n"
        conthelp += "can contribute with a coffee\n\n"
        conthelp += "scan the qr code and donate € 1.00"
        return conthelp

    def layoutFinished(self):
        paypal = self.paypal2()
        self["paypal"].setText(paypal)
        self.setTitle(self.setup_title)

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        self.list.append(getConfigListEntry(_('Server:'), config.plugins.TivuStream.server, _("Configure Server for Update Service and List")))
        self.list.append(getConfigListEntry(_('Auto Update Plugin:'), config.plugins.TivuStream.autoupd, _("Set Automatic Update Plugin Version")))
        self.list.append(getConfigListEntry(_('Personal Password:'), config.plugins.TivuStream.code, _("Enter the password to download Lists XXX Adults")))
        self.list.append(getConfigListEntry(_('IPTV bouquets location '), config.plugins.TivuStream.bouquettop, _("Configure position of the bouquets of the converted lists")))
        self.list.append(getConfigListEntry(_('Player folder List <.m3u>:'), config.plugins.TivuStream.pthm3uf, _("Folder path containing the .m3u files")))
        self.list.append(getConfigListEntry(_('Services Player Reference type'), config.plugins.TivuStream.services, _("Configure Service Player Reference")))
        self.list.append(getConfigListEntry(_('Download file tivustream.m3u'), config.plugins.TivuStream.dowm3u, _("Download file tivustream.m3u complete")))
        self.list.append(getConfigListEntry(_('Show thumpics?'), config.plugins.TivuStream.thumb, _("Show Thumbpics ? Enigma restart required")))
        if config.plugins.TivuStream.thumb.value is True:
            self.list.append(getConfigListEntry(_('Download thumpics?'), config.plugins.TivuStream.thumbpic, _("Download thumpics in Player M3U (is very Slow)?")))
        self.list.append(getConfigListEntry(_('Folder Cache for Thumbpics:'), config.plugins.TivuStream.cachefold, _("Configure position folder for temporary Thumbpics")))
        self.list.append(getConfigListEntry(_('Link in Extensions Menu:'), config.plugins.TivuStream.strtext, _("Show Plugin in Extensions Menu")))
        self.list.append(getConfigListEntry(_('Link in Main Menu:'), config.plugins.TivuStream.strtmain, _("Show Plugin in Main Menu")))
        self['config'].list = self.list
        self["config"].l.setList(self.list)
        # self.setInfo()

    def setInfo(self):
        try:
            sel = self['config'].getCurrent()[2]
            if sel:
                # print('sel =: ', sel)
                self['description'].setText(str(sel))
            else:
                self['description'].setText(_('SELECT YOUR CHOICE'))
            return
        except Exception as e:
            print("Error ", e)

    def changedEntry(self):
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
        if path is not None:
            if self.setting == 'pthm3uf':
                config.plugins.TivuStream.pthm3uf.setValue(path)
            elif self.setting == 'cachefold':
                config.plugins.TivuStream.cachefold.setValue(path)
        return

    def cfgok(self):
        self.save()

    def save(self):
        if not os.path.exists(config.plugins.TivuStream.pthm3uf.value):
            self.mbox = self.session.open(MessageBox, _('M3u list folder not detected!'), MessageBox.TYPE_INFO, timeout=4)
            return
        if self['config'].isChanged():
            for x in self['config'].list:
                x[1].save()
            config.plugins.TivuStream.server.save()
            configfile.save()
            plugins.clearPluginList()
            plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
            self.mbox = self.session.open(MessageBox, _('Settings saved correctly!'), MessageBox.TYPE_INFO, timeout=5)
            self.close()
        else:
            self.close()

    def VirtualKeyBoardCallback(self, callback=None):
        if callback is not None and len(callback):
            self["config"].getCurrent()[1].setValue(callback)
            self["config"].invalidate(self["config"].getCurrent())

    def KeyText(self):
        sel = self['config'].getCurrent()
        if sel:
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)

    def extnok(self, answer=None):
        if answer is None:
            if self["config"].isChanged():
                self.session.openWithCallback(self.zExit, MessageBox, _("Really close without saving settings?"))
            else:
                self.close(False)
        elif answer:
            for x in self["config"].list:
                x[1].cancel()
            self.close(True)
        return

    def msgupdt2(self):
        if self.cbUpdate is False:
            return
        if config.plugins.TivuStream.autoupd.value is False:
            return
        self.session.openWithCallback(self.runupdate, MessageBox, _('New Online Version!') + '\n\n' + _('Update Plugin to Version %s ?\nPlease Restart GUI Required!' % self.version), MessageBox.TYPE_YESNO)

    def msgupdt1(self):
        if self.cbUpdate is False:
            return
        self.session.openWithCallback(self.runupdate, MessageBox, _('Update Plugin ?'), MessageBox.TYPE_YESNO)

    def runupdate(self, result):
        if result:
            dom = 'Last version ' + self.version
            cmd = "wget -U '%s' -c '%s' -O '/tmp/tivustream.tar'" % ('Enigma2 - TVstream Plugin', self.link)
            if "https" in str(self.link):
                cmd = "wget --no-check-certificate -U '%s' -c '%s' -O '/tmp/tivustream.tar'" % ('Enigma2 - TVstream Plugin', self.link)
            print('cmd comand wget: ', cmd)
            # os.system('wget %s -O /tmp/tivustream.tar > /dev/null' % self.link)
            os.system(cmd)
            os.system('sleep 3')
            self.session.open(OpenConsole, _('Update Plugin: %s') % dom, ['tar -xvf /tmp/tivustream.tar -C /'], closeOnSuccess=False)  # finishedCallback=self.ipkrestrt, closeOnSuccess=False)

    def ipkrestrt(self):
        epgpath = '/media/hdd/epg.dat'
        epgbakpath = '/media/hdd/epg.dat.bak'
        if os.path.exists(epgbakpath):
            os.remove(epgbakpath)
        if os.path.exists(epgpath):
            copyfile(epgpath, epgbakpath)
        self.session.open(TryQuitMainloop, 3)


class OpenConsole(Screen):
    def __init__(self, session, title="Console", cmdlist=None, finishedCallback=None, closeOnSuccess=False, endstr=''):
        self.session = session
        global _session
        _session = session
        skin = os.path.join(skin_path, 'OpenConsole.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self.endstr = endstr
        self['list'] = ScrollLabel('')
        # self["text"] = Label('')
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.cancel,
                                                                            'back': self.cancel,
                                                                            'blue': self.restartenigma,
                                                                            'up': self['list'].pageUp,
                                                                            'down': self['list'].pageDown}, -1)
        self.cmdlist = cmdlist
        self.container = eConsoleAppContainer()
        self.run = 0
        try:
            self.container.appClosed.append(self.runFinished)
            self.container.dataAvail.append(self.dataAvail)
        except:
            self.appClosed_conn = self.container.appClosed.connect(self.runFinished)
            self.dataAvail_conn = self.container.dataAvail.connect(self.dataAvail)
        self.onLayoutFinish.append(self.startRun)

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        self['list'].setText(_('Executing in run:') + '\n\n')
        if self.container.execute(self.cmdlist[self.run]):
            self.runFinished(-1)

    def runFinished(self, retval):
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]):
                self.runFinished(-1)
        else:
            str = self["text"].getText()
            if not retval and self.endstr.startswith("Swapping"):
                str += _("\n\n"+self.endstr)
            else:
                str += _("Execution finished!!\n")
            self["text"].setText(str)
            self["text"].lastPage()
            self.cancel()

    def dataAvail(self, data):
        if PY3:
            data = data.decode("utf-8")
        try:
            self["text"].setText(self["text"].getText() + data)
        except Exception as e:
            print('error ', e)
        return
        if self["text"].getText().endswith("Do you want to continue? [Y/n] "):
            self.session.openWithCallback(self.processAnswer, MessageBox, _("Additional packages must be installed. Do you want to continue?"), MessageBox.TYPE_YESNO)

    def processAnswer(self, retval):
        if retval:
            self.container.write("Y", 1)
        else:
            self.container.write("n", 1)
        self.dataSent_conn = self.container.dataSent.connect(self.processInput)

    def processInput(self, retval):
        self.container.sendEOF()

    def restartenigma(self):
        self.session.open(TryQuitMainloop, 3)

    def cancel(self):
        if self.run == len(self.cmdlist):
            self.close()
            try:
                self.appClosed_conn = None
                self.dataAvail_conn = None
            except:
                self.container.appClosed.remove(self.runFinished)
                self.container.dataAvail.remove(self.dataAvail)


class openMessageBox(Screen):
    TYPE_YESNO = 0
    TYPE_INFO = 1
    TYPE_WARNING = 2
    TYPE_ERROR = 3
    TYPE_MESSAGE = 4

    def __init__(self, session, text, type=TYPE_YESNO, timeout=-1, close_on_any_key=False, default=True, enable_input=True, msgBoxID=None, picon=None, simple=False, list=[], timeout_default=None):
        self.type = type
        self.session = session
        global _session
        _session = session
        skin = os.path.join(skin_path, 'openMessageBox.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
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
            elif default is True:
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
            if Utils.DreamOS():
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
        global _session
        _session = session
        skin = os.path.join(skin_path, 'Plgnstrt.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self["poster"] = Pixmap()
        self["poster"].hide()
        self['list'] = StaticText()
        self['actions'] = ActionMap(['OkCancelActions',
                                     'DirectionActions',
                                     'ColorActions'], {'ok': self.clsgo,
                                                       'cancel': self.clsgo,
                                                       'back': self.clsgo,
                                                       'red': self.clsgo,
                                                       'green': self.clsgo}, -1)
        self.onFirstExecBegin.append(self.loadDefaultImage)
        # self.onLayoutFinish.append(self.image_downloaded)
        self.onLayoutFinish.append(self.checkDwnld)

    def decodeImage(self, pngori):
        pixmaps = pngori
        if Utils.DreamOS():
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
        if Utils.DreamOS():
            if self.picload.startDecode(pixmaps, False) == 0:
                ptr = self.picload.getData()
        else:
            if self.picload.startDecode(pixmaps, 0, 0, False) == 0:
                ptr = self.picload.getData()
        if ptr is not None:
            self['poster'].instance.setPixmap(ptr)
            self['poster'].show()
        else:
            print('no cover.. error')
        return

    def image_downloaded(self):
        pngori = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/nasa.jpg".format('TivuStream'))
        if os.path.exists(pngori):
            print('image pngori: ', pngori)
            try:
                self.decodeImage(pngori)
            except Exception as ex:
                print(ex)
                pass
            except:
                pass

    def loadDefaultImage(self, failure=None):
        # import random
        print("*** failure *** %s" % failure)
        global pngori
        fldpng = '/usr/lib/enigma2/python/Plugins/Extensions/TivuStream/res/pics/'
        npj = 'nasa.jpg'  # random.choice(imgjpg)
        pngori = fldpng + npj
        self.decodeImage(pngori)

    def checkDwnld(self):
        self.icount = 0
        self['list'].setText(_('\n\n\nCheck Connection wait please...'))
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.OpenCheck)
        else:
            self.timer.callback.append(self.OpenCheck)
        self.timer.start(1500, 1)

    def getinfo(self):
        continfo = _("==========       WELCOME     ============\n")
        continfo += _("=========     SUPPORT ON:   ============\n")
        continfo += _("+WWW.TIVUSTREAM.COM - WWW.CORVOBOYS.COM+\n")
        continfo += _("http://t.me/tivustream\n\n")
        continfo += _("========================================\n")
        continfo += _("ATTENTION: \n")
        continfo += _("This plugin is no longer supported\n")
        continfo += _(", please visit our social links go to\n")
        continfo += _("tivustream.com or corvoboys.org and ask\n")
        continfo += _(" about new supported plugins.\n")
        continfo += _("Thank you with all my heart\n")
        continfo += _("Just for passion!!!.\n")
        continfo += _("========================================\n")
        return continfo

    def OpenCheck(self):
        try:
            self['list'].setText(self.getinfo())
        except:
            self['list'].setText(_('\n\n' + 'Error downloading News!'))

    def error(self):
        self['list'].setText(_('\n\n' + 'Server Off !') + '\n' + _('check SERVER in config'))

    def clsgo(self):
        self.close()
        # self.session.openWithCallback(self.close, MainTvStream)


class AutoStartTimertvstream:

    def __init__(self, session):
        self.session = session
        global _firstStarttvstream
        print("*** running AutoStartTimertvstream ***")
        if _firstStarttvstream:
            self.runUpdate()

    def runUpdate(self):
        print("*** running update ***")
        try:
            from . import Update
            Update.upd_done()
            _firstStarttvstream = False
        except Exception as e:
            print('error TiVuStream', str(e))


def autostart(reason, session=None, **kwargs):
    print("*** running autostart ***")
    global autoStartTimertvstream
    global _firstStarttvstream
    if reason == 0:
        if session is not None:
            _firstStarttvstream = True
            autoStartTimertvstream = AutoStartTimertvstream(session)
    return


def main(session, **kwargs):
    try:
        # if PY3:
            # session.open(MainTvStream)
        # else:
        session.open(plgnstrt)
    except:
        import traceback
        traceback.print_exc()
        pass


def cfgmain(menuid):
    if menuid == 'mainmenu':
        return [('TiVuStream Revolution', main, 'TiVuStream Revolution', 44)]
    else:
        return []


def Plugins(**kwargs):
    icona = 'logo.png'
    if not Utils.DreamOS():
        icona = skin_path + 'logo.png'
    # extDescriptor = PluginDescriptor(name=name_plug, description=_(title_plug), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon=icona, fnc=main)
    # mainDescriptor = PluginDescriptor(name=name_plug, description=_(title_plug), where=PluginDescriptor.WHERE_MENU, icon=icona, fnc=cfgmain)
    result = [PluginDescriptor(name=name_plug, description=title_plug, where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart),
              PluginDescriptor(name=name_plug, description=title_plug, where=PluginDescriptor.WHERE_PLUGINMENU, icon=icona, fnc=main)]
    # if config.plugins.TivuStream.strtext.value:
        # result.append(extDescriptor)
    # if config.plugins.TivuStream.strtmain.value:
        # result.append(mainDescriptor)
    return result
