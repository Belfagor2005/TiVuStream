#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
****************************************
*        coded by Lululla              *
*           thank's Pcd                *
*             12/10/2022               *
*       skin by MMark                  *
****************************************
Info http://t.me/tivustream
'''
from __future__ import print_function
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap, MovingPixmap
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.config import config
from Screens.InfoBarGenerics import InfoBarSubtitleSupport, InfoBarMenu
from Screens.InfoBarGenerics import InfoBarSeek
from Screens.InfoBarGenerics import InfoBarAudioSelection, InfoBarNotifications
from Screens.InfoBar import MoviePlayer
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import SCOPE_PLUGINS
from Tools.Directories import fileExists
from Tools.Directories import resolveFilename
from enigma import iPlayableService
from enigma import eServiceReference
from enigma import eTimer
from time import sleep
import os
import sys
from . import Utils

global skin_path, tmpfold, picfold
global defpic, dblank


try:
    import Image
except:
    from PIL import Image, ImageChops

_session = None

PY3 = sys.version_info.major >= 3
print('Py3: ', PY3)

if PY3:
    from urllib.request import Request
    unicode = str
    unichr = chr
    long = int
    PY3 = True
else:
    from urllib2 import Request

plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/".format('TivuStream'))
skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/skins/hd/".format('TivuStream'))
defpic = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/default.png".format('TivuStream'))
dblank = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/blank.png".format('TivuStream'))

if Utils.isFHD():
    skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/skins/fhd/".format('TivuStream'))
    defpic = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/defaultL.png".format('TivuStream'))
    dblank = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/blankL.png".format('TivuStream'))
if Utils.DreamOS():
    skin_path = skin_path + 'dreamOs/'

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


def cleanName(name):
    name = name.strip()
    # filter out non-allowed characters
    non_allowed_characters = "/.\\:*?<>|\""
    name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
    name = ''.join(['_' if c in non_allowed_characters or ord(c) < 32 else c for c in name])
    return name


def getpics(names, pics, tmpfold, picfold):
    global defpic
    defpic = defpic
    print("In getpics tmpfold =", tmpfold)
    print("In getpics picfold =", picfold)
    pix = []
    if config.plugins.TivuStream.thumbpic.value is False:
        npic = len(pics)
        i = 0
        while i < npic:
            pix.append(defpic)
            i = i+1
        return pix
    cmd = "rm " + tmpfold + "/*"
    os.system(cmd)
    npic = len(pics)
    j = 0
    print("In getpics names =", names)
    print("In getpics pics =", pics)
    while j < npic:
        name = names[j]
        print("In getpics name =", name)
        if name is None or name == '':
            name = "Video"
        name = cleanName(name)
        print(name)
        # test
        name = name.replace(' ', '-').replace("'", '').replace('&', '').replace('(', '').replace(')', '')
        print(name)
        # end test
        url = pics[j]
        if url is None:
            url = ""
        url = url.replace(" ", "%20")
        url = url.replace("ExQ", "=")
        url = url.replace("AxNxD", "&")
        # print("In getpics url =", url)
        ext = str(os.path.splitext(url)[-1])
        picf = picfold + "/" + name + ext
        tpicf = tmpfold + "/" + name + ext
        if fileExists(picf):
            if ('Stagione') in str(name):
                cmd = "rm " + picf
                os.system(cmd)
            cmd = "cp " + picf + " " + tmpfold
            print("In getpics fileExists(picf) cmd =", cmd)
            os.system(cmd)
        if fileExists(tpicf):
            if ('Stagione') in str(name):
                cmd = "rm " + tpicf
                os.system(cmd)
        if not fileExists(picf):
            if plugin_path in url:
                try:
                    cmd = "cp " + url + " " + tpicf
                    print("In getpics not fileExists(picf) cmd =", cmd)
                    os.system(cmd)
                except:
                    pass
            else:
                try:
                    if "|" in url:
                        n3 = url.find("|", 0)
                        n1 = url.find("Referer", n3)
                        n2 = url.find("=", n1)
                        url = url[:n3]
                        referer = url[n2:]
                        p = Utils.getUrl2(url, referer)
                        # -----------------
                        # f1 = open(tpicf, "wb")
                        # f1.write(p)
                        # f1.close()
                        with open(tpicf, 'wb') as f1:
                            f1.write(p)
                    else:
                        print("Going in urlopen url =", url)
                        p = Utils.ReadUrl2(url)
                        # p = p.decode('utf-8', 'ignore')
                        with open(tpicf, 'wb') as f1:
                            f1.write(p)
                        # f1 = open(tpicf, "wb")
                        # f1.write(p)
                        # f1.close()
                except:
                    cmd = "cp " + defpic + " " + tpicf
                    os.system(cmd)

        if not fileExists(tpicf):
            print("In getpics not fileExists(tpicf) tpicf=", tpicf)
            cmd = "cp " + defpic + " " + tpicf
            print("In getpics not fileExists(tpicf) cmd=", cmd)
            os.system(cmd)
        if Utils.isFHD():
            nw = 220
        else:
            nw = 150
        if os.path.exists(tpicf):
            try:
                im = Image.open(tpicf)  # .convert('RGBA')
                # imode = im.mode
                # if im.mode == "JPEG":
                    # im.save(tpicf)
                    # # in most case, resulting jpg file is resized small one
                # if imode.mode in ["RGBA", "P"]:
                    # imode = imode.convert("RGB")
                    # rgb_im.save(tpicf)
                # if imode != "P":
                    # im = im.convert("P")
                # if im.mode != "P":
                    # im = im.convert("P")
                w = im.size[0]
                d = im.size[1]
                r = float(d)/float(w)
                d1 = r * nw
                if w != nw:
                    x = int(nw)
                    y = int(d1)
                    im = im.resize((x, y), Image.ANTIALIAS)
                im.save(tpicf, quality=100, optimize=True)
                # im.save(tpicf, 'PNG')
                # im.save(tpicf, 'JPG')
                # # im.save(tpicf)
            except Exception as e:
                print("******* picon resize failed *******")
                print(e)
        else:
            print("******* make picon failed *******")
            tpicf = defpic
        # except:
            # print("******* make picon failed *******")
            # tpicf = defpic
        pix.append(j)
        pix[j] = picf
        j = j+1
    cmd1 = "cp " + tmpfold + "/* " + picfold + " && rm " + tmpfold + "/* &"
    # print("In getpics final cmd1=", cmd1)
    os.system(cmd1)

    return pix


class GridMain(Screen):

    def __init__(self, session, names, urls, pics=[]):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        skin = skin_path + 'GridMain.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        f.close()
        self['title'] = Label(_('..:: TiVuStream Revolution ::..'))
        self.pos = []
        if Utils.isFHD():
            self.pos.append([30, 24])
            self.pos.append([396, 24])
            self.pos.append([764, 24])
            self.pos.append([1134, 24])
            self.pos.append([1504, 24])
            self.pos.append([30, 468])
            self.pos.append([396, 468])
            self.pos.append([764, 468])
            self.pos.append([1134, 468])
            self.pos.append([1504, 468])
        else:
            self.pos.append([26, 15])
            self.pos.append([272, 15])
            self.pos.append([516, 15])
            self.pos.append([756, 15])
            self.pos.append([996, 15])
            self.pos.append([26, 315])
            self.pos.append([272, 315])
            self.pos.append([516, 315])
            self.pos.append([756, 315])
            self.pos.append([996, 315])          
        print(" self.pos =", self.pos)
        tmpfold = config.plugins.TivuStream.cachefold.value + "/tivustream/tmp"
        picfold = config.plugins.TivuStream.cachefold.value + "/tivustream/pic"
        # pics = getpics(names, pics, tmpfold, picfold)
        self["info"] = Label()
        pics = getpics(names, pics, tmpfold, picfold)
        print("In Gridmain pics = ", pics)
        self.picsint = eTimer()
        self.picsint.start(1000, True)
        self.urls = urls
        self.pics = pics
        self.name = "TivuStream"
        self.names = names
        sleep(3)
        list = []
        list = names
        self["info"] = Label()
        self["menu"] = List(list)
        for x in list:
            print("x in list =", x)
        self["frame"] = MovingPixmap()
        i = 0
        while i < 20:
            self["label" + str(i+1)] = StaticText()
            self["pixmap" + str(i+1)] = Pixmap()
            i = i+1
        self.index = 0
        self.ipage = 1
        ln = len(self.names)
        self.npage = int(float(ln/10)) + 1
        print("self.npage =", self.npage)
        self["actions"] = ActionMap(["OkCancelActions",
                                     "MenuActions",
                                     "DirectionActions",
                                     "NumberActions"], {"ok": self.okClicked,
                                                        "cancel": self.cancel,
                                                        "left": self.key_left,
                                                        "right": self.key_right,
                                                        "up": self.key_up,
                                                        "down": self.key_down})
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openTest)
        # self.onShown.append(self.openTest)

    def cancel(self):
        self.close()

    def exit(self):
        self.close()

    def paintFrame(self):
        print("In paintFrame self.index, self.minentry, self.maxentry =", self.index, self.minentry, self.maxentry)
        # if self.maxentry < self.index or self.index < 0:
        #     return
        print("In paintFrame self.ipage = ", self.ipage)
        try:
            ifr = self.index - (10*(self.ipage-1))
            print("ifr =", ifr)
            ipos = self.pos[ifr]
            print("ipos =", ipos)
            inf = self.index
            if inf:
                try:
                    self["info"].setText(self.infos[inf])
                    print('infos: ', inf)
                except:
                    self["info"].setText('')
                    print('except info')
            self["frame"].moveTo(ipos[0], ipos[1], 1)
            self["frame"].startMoving()
        except Exception as e:
            print('error  in paintframe: ', str(e))

    def openTest(self):
        print("self.index, openTest self.ipage, self.npage =", self.index, self.ipage, self.npage)
        if self.ipage < self.npage:
            self.maxentry = (10*self.ipage)-1
            self.minentry = (self.ipage-1)*10
            print("self.ipage , self.minentry, self.maxentry =", self.ipage, self.minentry, self.maxentry)

        elif self.ipage == self.npage:
            print("self.ipage , len(self.pics) =", self.ipage, len(self.pics))
            self.maxentry = len(self.pics) - 1
            self.minentry = (self.ipage-1)*10
            print("self.ipage , self.minentry, self.maxentry B=", self.ipage, self.minentry, self.maxentry)
            i1 = 0
            blpic = dblank
            while i1 < 12:
                self["label" + str(i1+1)].setText(" ")
                self["pixmap" + str(i1+1)].instance.setPixmapFromFile(blpic)
                i1 = i1+1
        print("len(self.pics), self.minentry, self.maxentry =", len(self.pics), self.minentry, self.maxentry)
        self.npics = len(self.pics)

        i = 0
        i1 = 0
        self.picnum = 0
        print("doing pixmap")
        ln = self.maxentry - (self.minentry-1)
        while i < ln:
            idx = self.minentry + i
            print("i, idx =", i, idx)
            print("self.names[idx] B=", self.names[idx])
            self["label" + str(i+1)].setText(self.names[idx])
            print("idx, self.pics[idx]", idx, self.pics[idx])
            pic = self.pics[idx]
            print("pic =", pic)
            if os.path.exists(pic):
                print("pic path exists")
            else:
                print("pic path exists not")
            picd = defpic
            try:
                self["pixmap" + str(i+1)].instance.setPixmapFromFile(pic)
            except:
                self["pixmap" + str(i+1)].instance.setPixmapFromFile(picd)
            i = i+1
        self.index = self.minentry
        print("self.minentry, self.index =", self.minentry, self.index)
        self.paintFrame()

    def key_left(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.maxentry
            self.key_up()
        else:
            self.paintFrame()

    def key_right(self):
        i = self.npics - 1
        if self.index == i:
            self.index = 0
            self.ipage = 1
            self.openTest()
        self.index += 1
        if self.index > self.maxentry:
            self.index = 0
            self.key_down()
        else:
            self.paintFrame()

    def key_up(self):
        print("keyup self.index, self.minentry = ", self.index, self.minentry)
        self.index = self.index - 5
        print("keyup self.index, self.minentry 2 = ", self.index, self.minentry)
        print("keyup self.ipage = ", self.ipage)
        if self.index < (self.minentry):
            if self.ipage > 1:
                self.ipage = self.ipage - 1
                self.openTest()
            elif self.ipage == 1:
                return
            else:
                self.index = 0
            self.paintFrame()
        else:
            self.paintFrame()

    def key_down(self):
        print("keydown self.index, self.maxentry = ", self.index, self.maxentry)
        self.index = self.index + 5
        print("keydown self.index, self.maxentry 2= ", self.index, self.maxentry)
        print("keydown self.ipage = ", self.ipage)

        if self.index > (self.maxentry):
            if self.ipage < self.npage:
                self.ipage = self.ipage + 1
                self.openTest()

            elif self.ipage == self.npage:
                self.index = 0
                self.ipage = 1
                self.openTest()

            else:
                print("keydown self.index, self.maxentry 3= ", self.index, self.maxentry)
                self.index = 0
            self.paintFrame()
        else:
            self.paintFrame()

    def okClicked(self):
        itype = self.index
        url = self.urls[itype]
        name = self.names[itype]
        self.session.open(M3uPlay2, name, url)
        return


class TvInfoBarShowHide():
    """ InfoBar show/hide control, accepts toggleShow and hide actions, might start
    fancy animations. """
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3
    skipToggleShow = False

    def __init__(self):
        self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"], {"toggleShow": self.OkPressed, "hide": self.hide}, 0)
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(self.doTimerHide)
        except:
            self.hideTimer.callback.append(self.doTimerHide)
        self.hideTimer.start(5000, True)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

    def serviceStarted(self):
        if self.execing:
            if config.usage.show_infobar_on_zap.value:
                self.doShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def __onHide(self):
        self.__state = self.STATE_HIDDEN

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            self.hideTimer.stop()
            idx = config.usage.infobar_timeout.index
            if idx:
                self.hideTimer.start(idx * 1500, True)

    def doShow(self):
        self.hideTimer.stop()
        self.show()
        self.startHideTimer()

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()

    def OkPressed(self):
        self.toggleShow()

    def toggleShow(self):
        if self.skipToggleShow:
            self.skipToggleShow = False
            return
        if self.__state == self.STATE_HIDDEN:
            self.show()
            self.hideTimer.stop()
        else:
            self.hide()
            self.startHideTimer()

    def lockShow(self):
        try:
            self.__locked += 1
        except:
            self.__locked = 0
        if self.execing:
            self.show()
            self.hideTimer.stop()
            self.skipToggleShow = False

    def unlockShow(self):
        try:
            self.__locked -= 1
        except:
            self.__locked = 0
        if self.__locked < 0:
            self.__locked = 0
        if self.execing:
            self.startHideTimer()

    def debug(obj, text=""):
        print(text + " %s\n" % obj)


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
    screen_timeout = 4000

    def __init__(self, session, name, url):
        global streaml
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = 'MoviePlayer'
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
                                                             'info': self.showIMDB,
                                                             'stop': self.leavePlayer,
                                                             'cancel': self.cancel,
                                                             'back': self.cancel}, -1)
        self.allowPiP = False
        self.service = None
        self.pcip = 'None'
        self.icount = 0
        self.url = url
        self.name = Utils.decodeHtml(name)
        self.state = self.STATE_PLAYING
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onClose.append(self.cancel)
        # if '8088' in str(self.url):
            # # self.onLayoutFinish.append(self.slinkPlay)
            # self.onFirstExecBegin.append(self.slinkPlay)
        # else:
            # # self.onLayoutFinish.append(self.cicleStreamType)
            # self.onFirstExecBegin.append(self.cicleStreamType)
        self.onLayoutFinish.append(self.openPlay)

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

    def showIMDB(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        text_clear = self.name
        if Utils.is_tmdb:
            try:
                from Plugins.Extensions.TMBD.plugin import TMBD
                text = Utils.badcar(text_clear)
                text = Utils.charRemove(text_clear)
                _session.open(TMBD.tmdbScreen, text, 0)
            except Exception as ex:
                print("[XCF] Tmdb: ", str(ex))
        elif Utils.is_imdb:
            try:
                from Plugins.Extensions.IMDb.plugin import main as imdb
                text = Utils.badcar(text_clear)
                text = Utils.charRemove(text_clear)
                imdb(_session, text)
                # _session.open(imdb, text)
            except Exception as ex:
                print("[XCF] imdb: ", str(ex))
        else:
            self.session.open(MessageBox, text_clear, MessageBox.TYPE_INFO)

    def slinkPlay(self, url):
        name = self.name
        ref = "{0}:{1}".format(url.replace(":", "%3a"), name.replace(":", "%3a"))
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def openPlay(self):
        url = str(self.url)
        name = self.name
        servicetype = '4097'
        ref = '4097:0:1:0:0:0:0:0:0:0:' + url
        if config.plugins.TivuStream.services.value == 'Gstreamer':
            # ref = '5001:0:1:0:0:0:0:0:0:0:' + url
            servicetype = '5001'
        elif config.plugins.TivuStream.services.value == 'Exteplayer3':
            # ref = '5002:0:1:0:0:0:0:0:0:0:' + url
            servicetype = '5002'
        elif config.plugins.TivuStream.services.value == 'eServiceUri':
            # ref = '8193:0:1:0:0:0:0:0:0:0:' + url
            servicetype = '8193'
        elif config.plugins.TivuStream.services.value == 'Dvb':
            ref = '1:0:1:0:0:0:0:0:0:0:' + url
            servicetype = '1'
        else:
            # if config.plugins.TivuStream.services.value == 'Iptv':
            ref = "{0}:0:0:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3a"), name.replace(":", "%3a"))
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def cicleStreamType(self):
        global streaml
        streaml = False
        from itertools import cycle, islice
        self.servicetype = str(config.plugins.stvcl.services.value)  # +':0:1:0:0:0:0:0:0:0:'  # '4097'
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
        if Utils.isStreamlinkAvailable():
            streamtypelist.append("5002")  # ref = '5002:0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + url
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
        # pass
        self.up()

    def doEofInternal(self, playing):
        self.close()

    def __evEOF(self):
        self.end = True

    def ok(self):
        if self.shown:
            self.hideInfobar()
        else:
            self.showInfobar()

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback is not None:
            self.infoCallback()
        return

    def showAfterSeek(self):
        if isinstance(self, TvInfoBarShowHide):
            self.doShow()

    def cancel(self):
        if os.path.isfile('/tmp/hls.avi'):
            os.remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(self.srefInit)
        if not self.new_aspect == self.init_aspect:
            try:
                self.setAspect(self.init_aspect)
            except:
                pass
        streaml = False
        self.close()

    def leavePlayer(self):
        self.close()
