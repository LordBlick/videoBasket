#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
# -*- tabstop: 4 -*-

'''
 This program source code file is shared library for easiest gtk+2 windows
 position store and restore.
 
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

from os import path as ph
H = ph.expanduser('~') # Home dir
hh = lambda s: s.replace(H, '~')
from sys import stdout as sto
_p = lambda _str: sto.write(hh(str(_str)))
debug = False
def _dbg(_str):
	if debug: sto.write(hh(str(_str)))
"""
Example of use:
		from dlgEngine import DialogEngine
		ui.dlgEngine = DialogEngine(ui)
"""

class DialogEngine:
	def __init__(it, ui):
		it.ui = ui
		if hasattr(ui, '_p') and(callable(ui._p)):
			_p = lambda _str: ui._p(hh(str(_str)))
		for attr_n in ('sGeo', 'rGeo', 'Hide', 'Restore', 'dlgStd', 'boxInfo', 'boxQst', 'boxErr'):
			setattr(ui, attr_n, getattr(it, attr_n))

	#sGeo = lambda ui, w: ','.join(map(lambda i: "%i" % i, w.window.get_frame_extents()))
	def sGeo(it, win):
		gdw = win.window
		pos = tuple(gdw.get_frame_extents())[:2]
		size = gdw.get_geometry()[2:4]
		geo = ','.join(map(lambda i: "%i" % i, pos+size))
		dlgName = win.get_title()
		_dbg("Storing '%s' Window Geometry: %s\n" % (dlgName, geo))
		return geo

	#TODO: catch out off screen coordinates
	def rGeo(it, win, keyGeo):
		ui = it.ui
		if hasattr(ui, 'cfg'):
			s_Geo = ui.cfg.get(keyGeo)
			if s_Geo:
				t = tuple(map(int, s_Geo.split(',')))
				_dbg("Window: '%s',\n\tx:%i, y:%i, w:%i, h:%i\n" % ((win.get_title(),)+t))
				win.move(*t[:2])
				if win.get_resizable():
					win.window.resize(*t[2:])
			else:
				_dbg("%s:No UI cfg…\n" % win.get_title())

	def Hide(it, attr_name, cfg_name, bStore=True):
		ui = it.ui
		dlg = getattr(ui, attr_name)
		if dlg.get_property("visible"):
			if bStore:
				ui.cfg[cfg_name] = it.sGeo(dlg)
			dlg.hide()

	def Restore(it, attr_name, cfg_name):
		dlg = getattr(it.ui, attr_name)
		bRestore = True
		if dlg.get_property("visible"):
			bRestore = False
		dlg.present()
		if bRestore:
			it.rGeo(dlg, cfg_name)

	def dlgStd(it, attr_name, cfg_name, title, call_widgets_prep, call_sizer=None,
			geom_t=None, fixed=True, top=False, modal=False, ntrans=False, bw=5, bTestUI=False):
		"Req ui.mainWindow"
		ui = it.ui
		dlg = gtk.Window(gtk.WINDOW_TOPLEVEL) if bTestUI else  gtk.Window()
		setattr(ui, attr_name, dlg)
		if type(geom_t) in(tuple, list) and(len(geom_t) in(2, 4)) and(not(False in map(lambda _i: type(_i)==int, geom_t))):
			if len(geom_t)==2:
				w, h = geom_t
				dlg.set_geometry_hints(min_width=w, min_height=h)
				_dbg("%s.set_geometry_hints: w≥%i, h≥%i\n" % (attr_name, w, h))
			else:
				w, h, w_, h_ = geom_t
				dlg.set_geometry_hints(min_width=w, min_height=h, max_width=w_, max_height=h_)
				_dbg("%s.set_geometry_hints: %i≥w≥%i, %i≥h≥%i\n" % (attr_name, w_, w, h_, h))
		if not(bTestUI) and(modal):
			#dlg.set_parent_window(ui.mainWindow.window)
			dlg.set_modal(True)
		if hasattr(ui, 'accGroup') and(type(ui.accGroup)==gtk.AccelGroup):
			dlg.add_accel_group(ui.accGroup)
		dlg.set_border_width(bw)
		dlg.set_resizable(bool(call_sizer))
		dlg.set_title(title)
		if attr_name!='mainWindow':
			if not(bTestUI and(ntrans)):
				dlg.set_transient_for(ui.mainWindow)
			dlg.set_destroy_with_parent(True)
			dlg.set_deletable(False)
			dlg.set_skip_taskbar_hint(False)
		if globals().has_key('BGcolor'):
			dlg.modify_bg(gtk.STATE_NORMAL, BGcolor)
		if fixed:
			dlg.dlgFrame = gtk.Fixed()
		dlg.Restore = lambda: it.Restore(attr_name, cfg_name)
		dlg.Hide = lambda bStore=True: it.Hide(attr_name, cfg_name, bStore=bStore)
		if callable(call_widgets_prep):
			call_widgets_prep(dlg, test=bTestUI)
		if fixed:
			dlg.add(dlg.dlgFrame)
		dlg.show_all()
		dlg.lastWinSize = None
		if not(bTestUI):
			dlg.Hide(False)
		if callable(call_sizer):
			dlg.connect("configure-event", call_sizer)
		if bTestUI:
			for s_attr in('Cancel', 'OK'):
				if hasattr(dlg, 'button'+s_attr):
					getattr(dlg, 'button'+s_attr).connect("clicked", lambda w: dlg.Hide())
					_dbg("Assigned Hide() for %s.button%s\n" % (attr_name, s_attr))
				elif hasattr(dlg, 'dcWgt') and(dlg.dcWgt.has_key(s_attr)):
					dlg.dcWgt[s_attr].connect("clicked", lambda w: dlg.Hide())
					_dbg("Assigned Hide() for %s.dcWgt%s]\n" % (attr_name, s_attr))
		return dlg

	def boxCommon(it, hDialog, message, caption):
		ui = it.ui
		hDialog.set_markup(message)
		hDialog.set_title(caption)
		if globals().has_key('BGcolor'):
			dlg.modify_bg(gtk.STATE_NORMAL, BGcolor)
		if globals().has_key('FGcolor'):
			for child in hDialog.vbox.children()[0].children()[1].children():
				child.modify_fg(gtk.STATE_NORMAL, FGcolor)

	def boxInfo(it, parent=None, message="...", caption = 'Information'):
		hDialog = gtk.MessageDialog(parent=parent, flags=gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK, message_format=None)
		it.boxCommon(hDialog, message, caption)
		hDialog.run()
		hDialog.destroy()

	def boxQst(it, parent=None, message="...?", caption = 'Ωuestion'):
		hDialog = gtk.MessageDialog(parent=parent, flags=gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format=None)
		it.boxCommon(hDialog, message, caption)
		answer = hDialog.run()
		hDialog.destroy()
		return answer

	def boxErr(it, parent=None, message="...!", caption = 'error!'):
		hDialog = gtk.MessageDialog(parent=parent, flags=gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format=None)
		it.boxCommon(hDialog, message, caption)
		hDialog.run()
		hDialog.destroy()
