#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
# -*- tabstop: 4 -*-

'''
 This program source code file is part of videoBasket, a video download GUI
 application.
 
 Copyright  © 2015 by LordBlick (at) gmail.com
 
 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU General Public License
 as published by the Free Software Foundation; either version 2
 of the License, or (at your option) any later version.
 
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with this program; if not, you may find one here:
 http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
 or you may search the http://www.gnu.org website for the version 2 license,
 or you may write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
'''

from wgts import gtk, pango
import wgts as wg
class videoBasketUI:
	def __init__(ui):
		ui.fontDesc = pango.FontDescription('Univers,Sans Condensed 7')
		ui.fontFixedDesc = pango.FontDescription('Terminus,Monospace Bold 7')
		wg.Height = 25
		ui.uiInit()
		from TextViewVT import VTtext
		ui.vt = VTtext(ui.logView)
		ui.dialogsInit()
		if __name__ == "__main__":
			ui.mainWindow.connect("destroy", lambda w: gtk.main_quit())
			ui.buttonExit.connect("clicked", lambda w: gtk.main_quit())
			ui.logView.insert_end("User Interface Test...\nSo long… So long… So long… So long… long… Sooooo long… ")
			gtk.main()

	def uiInit(ui):
		from os import path as ph
		runpath = ph.dirname(ph.realpath(__file__))
		if __name__ == "__main__":
			ui.cfg = {}
		wg.Height = 25
		ui.title = 'Basket for videos - drag URLs below…'
		ui.mainWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
		w, h = (300, 400)
		ui.mainWindow.set_geometry_hints(min_width=w, min_height=h)
		ui.mainWindow.set_size_request(w, h)
		ui.mainWindow.set_title(ui.title)
		ui.mainWindow.set_border_width(5)
		accGroup = gtk.AccelGroup()
		ui.mainWindow.add_accel_group(accGroup)
		mfm = ui.mainFrame = gtk.Fixed()

		#List of Config Memory (Fuses, Lock) Name|ValueHex|TooltipValueBin
		from gobject import TYPE_STRING as goStr, TYPE_INT as goInt
		lsUrls = gtk.ListStore(goStr, goStr, goStr, goStr)
		ui.tvUrls = wg.TreeView(lsUrls, mfm)
		#tvUrlsSelection = ui.tvUrls.get_selection()
		#tvUrlsSelection.set_mode(gtk.SELECTION_SINGLE)
		#Column #1 - Engine
		lsCellRendProps = (
		('cell-background-gdk', gtk.gdk.Color('#580')), ('xalign', 0.5), ('editable', True) )
		tvcEngine, crtxtEngine = wg.TreeTxtColumn('Engine', 224, (0,), lsCellRendProps, fontDesc = ui.fontDesc)
		ui.tvUrls.append_column(tvcEngine)
		#Column #2 - Url to download
		lsCellRendProps = ( ('cell-background-gdk', gtk.gdk.Color('#990')),)
		tvcUrl, crtxtUrl = wg.TreeTxtColumn('Url', None, (1,), lsCellRendProps, fontDesc = ui.fontDesc)
		ui.tvUrls.append_column(tvcUrl)
		ui.tvUrls.set_tooltip_column(2, )
		ui.tvUrls.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color('#131'))

		ui.logView = wg.TextView(mfm, bEditable=False, tabSpace=4, fontDesc = ui.fontFixedDesc)

		ui.txtAddURL = wg.Entry(mfm, 0,  0, 0, clearIco=True)
		ui.buttonAddURL = wg.Butt("Add URL", mfm, 0,  0, 50)

		ui.checkOwnYTdl = wg.Check("Internal YT downloader", mfm, 0,  0, 130)
		ui.labelLimit = wg.Label("Resolution limit:", mfm, 0,  0, 80)
		ui.lsLimit = gtk.ListStore(goStr, goInt)
		ui.cbLimit = wg.ComboBox(ui.lsLimit, mfm, 0, 0, 70)

		ui.logoBigPixbuf = gtk.gdk.pixbuf_new_from_file(runpath+"/pic/video.svg")
		gtk.window_set_default_icon_list(ui.logoBigPixbuf, )
		ui.imageLogo = gtk.Image()
		ui.imageLogo.set_from_pixbuf(ui.logoBigPixbuf)
		mfm.put(ui.imageLogo, 0, 0)

		ui.buttonReload = wg.Butt(None, mfm, 0, 0, 30, stockID=gtk.STOCK_REFRESH) #"Read File..."

		ui.buttonClear = wg.Butt("Clear", mfm, 0,  0, 50)

		ui.buttonExit = wg.Butt("Exit (Ctrl+Q)", mfm, 0, 0, 80)
		ui.buttonExit.add_accelerator("clicked", accGroup, ord('Q'),
			gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

		ui.mainWindow.add(mfm)
		ui.mainWindow.show_all()
		ui.mainWindow.set_keep_above(True)
		ui.lastWinSize = None
		ui.mainWindow.connect("configure-event", ui.uiSize)

	def uiSize(ui, window, event):
		if event.type==wg.gtk.gdk.CONFIGURE:
			w, h = event.width, event.height
			if ui.lastWinSize==(w, h):
				return True
			ui.lastWinSize = w, h
			H = wg.Height
			y = h-95
			h1 = y/2+50
			h2 = y/2-60
			ya = h1+5
			ui.tvUrls.size(w-10, h1)
			ui.logView.move(0, ya)
			ui.logView.size(w-10, h2)
			ui.txtAddURL.move(0, y)
			ui.txtAddURL.size(w-65, H)
			ui.buttonAddURL.move(w-60, y)
			y += 30
			ui.checkOwnYTdl.move(0, y)
			ui.labelLimit.move(w-165, y)
			ui.cbLimit.move(w-80, y)
			y += 30
			ui.mainFrame.move(ui.imageLogo, 0, y-2)
			ui.buttonReload.move(50, y)
			ui.buttonClear.move(w-145, y)
			ui.buttonExit.move(w-90, y)
			return True

	def dialogsInit(ui):
		pass

	def restoreGeometry(ui):
		ui.rGeo(ui.mainWindow, 'MainWindowGeometry')

	def storeGeometry(ui):
		ui.cfg['MainWindowGeometry'] = ui.sGeo(ui.mainWindow)

# Entry point
if __name__ == "__main__":
	videoBasketUI()
