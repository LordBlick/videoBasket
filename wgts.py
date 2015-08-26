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

import gtk, pango

dbg = False

if dbg:
	from os import path as ph
	H = ph.expanduser('~') # Home dir
	hh = lambda s: s.replace(H, '~')
	from sys import stdout as sto

def _dbg(_str):
	if dbg: sto.write(hh(str(_str)))

Height = 30


def getTxtPixelWidth(widget, txt, fontDesc=None):
	pangoLayout = widget.create_pango_layout(txt)
	if fontDesc:
		pangoLayout.set_font_description(fontDesc)
	pangoTxtSpc = pangoLayout.get_pixel_size()[0]
	del(pangoLayout)
	return pangoTxtSpc

def putScroll(hFixed, widget, posX, posY, width, height):
	hScroll = gtk.ScrolledWindow()
	hScroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	hScroll.add(widget)
	hScroll.set_size_request(width, height)
	hFixed.put(hScroll, posX, posY)
	return hScroll

class MvWg:
	"This is abctract class !"
	def __init__(it, *args):
		raise TypeError('MvWg.__init__(): abstract class')

	def move(it, x, y):
		it.hFixed.move(it, x, y)

	size = lambda it, w, h: it.set_size_request(w, h)

class Image(gtk.Image, MvWg):
	def __init__(it, hFixed, posX, posY, pix=None):
		it.hFixed = hFixed
		super(it.__class__, it).__init__() # gtk.Label
		if isinstance(pix, gtk.gdk.Pixbuf):
			it.set_from_pixbuf(pix)
		hFixed.put(it, posX, posY)

class Label(gtk.Label, MvWg):
	def __init__(it, txtLabel, hFixed, posX, posY, width, height=None, fontDesc=None, xalign=None, selectable=False):
		it.hFixed = hFixed
		super(it.__class__, it).__init__(txtLabel) # gtk.Label
		if fontDesc:
			it.modify_font(fontDesc)
		if type(xalign)==float and(0.<=xalign<=1.):
			yalign = it.get_alignment()[1]
			it.set_alignment(xalign, yalign)
		if type(selectable)==bool:
			it.set_selectable(selectable)
			it.set_can_focus(False)
		it.show()
		if not height:
			height=Height
		it.set_size_request(width, height)
		hFixed.put(it, posX, posY)

class Butt(gtk.Button, MvWg):
	"""If stockID is set, txtLabel set as True means full stock button,
	non-null string - own Label for stock image,
	in other case - button with only stock image"""
	def __init__(it, txtLabel, hFixed, posX, posY, width, height=None, fileImage=None, stockID=None, fontDesc=None):
		it.hFixed = hFixed
		if stockID == None and fileImage == None:
			super(it.__class__, it).__init__(label=txtLabel, use_underline=False)
			if fontDesc:
				btLabel = it.child
				btLabel.modify_font(fontDesc)
		else:
			if type(txtLabel)==int or type(txtLabel)==float or type(txtLabel)==type(None) or (type(txtLabel)==str and txtLabel==''):
				txtLabel = bool(txtLabel)
			if type(txtLabel)==bool and txtLabel==True or type(txtLabel)==str:
				if stockID:
					super(it.__class__, it).__init__(stock=stockID)
				elif fileImage:
					image = gtk.Image()
					image.set_from_file(fileImage)
					super(it.__class__, it).__init__()
					it.add(image)
				if type(txtLabel)==str:
					btLabel = it.get_children()[0].get_children()[0].get_children()[1]
					btLabel.set_text(txtLabel)
					if fontDesc:
						btLabel.modify_font(fontDesc)
			else:
				image = gtk.Image()
				if stockID:
					image.set_from_stock(stockID, gtk.ICON_SIZE_BUTTON)
				elif fileImage:
					image.set_from_file(fileImage)
				super(it.__class__, it).__init__()
				it.add(image)
		if not height:
			height = Height
		it.set_size_request(width, height)
		hFixed.put(it, posX, posY)

class Check(gtk.CheckButton, MvWg):
	def __init__(it, txtLabel, hFixed, posX, posY, width, height=None, fontDesc=None):
		it.hFixed = hFixed
		super(it.__class__, it).__init__(label=txtLabel, use_underline=False)
		if fontDesc:
			it.child.modify_font(fontDesc)
		if not height:
			height = Height
		it.set_size_request(width, height)
		hFixed.put(it, posX, posY)

class ComboBox(gtk.ComboBox):
	def __init__(it, modelCb, hFixed, posX, posY, width, height=None, fontDesc=None, wrap=None, selTxt=0):
		it.hFixed = hFixed
		super(it.__class__, it).__init__()
		cellRendr = gtk.CellRendererText()
		if fontDesc:
			cellRendr.set_property('font-desc', fontDesc)
		it.pack_start(cellRendr)
		it.set_attributes(cellRendr, text=selTxt)
		if wrap:
			it.set_wrap_width(wrap)
		else:
			cellRendr.set_property('ellipsize', pango.ELLIPSIZE_END)
		it.set_model(modelCb)
		if not height:
			height=Height+4
		it.set_size_request(width, height)
		hFixed.put(it, posX, posY-2)

	def move(it, x, y):
		it.hFixed.move(it, x, y-2)

class Entry(gtk.Entry, MvWg):
	def __init__(it, hFixed, posX, posY, width, height=None, startIco=None, clearIco=False, bEditable=True, fontDesc=None):
		def entryIcoClr(ed, icoPos, sigEvent):
			if icoPos == gtk.ENTRY_ICON_SECONDARY:
				ed.set_text('')
		it.hFixed = hFixed
		super(it.__class__, it).__init__()
		if fontDesc:
			it.modify_font(fontDesc)
		if startIco:
			textInput.set_icon_from_pixbuf(0, startIco)
		if clearIco:
			it.set_icon_from_stock(1, gtk.STOCK_CLOSE)
			it.set_icon_tooltip_text (1, 'Clear')
			it.connect("icon-release", entryIcoClr)
		it.set_property("editable", bool(bEditable))
		if not height:
			height = Height
		it.set_size_request(width, height)
		hFixed.put(it, posX, posY)

class MvScrolled:
	"This is abctract class !"
	def reScrollV(it, adjV, scrollV):
		'Scroll to the bottom of the TextView when the adjustment changes.'
		if it.autoscroll:
			adjV.set_value(adjV.upper - adjV.page_size)
			scrollV.set_vadjustment(adjV)
		return

	def setup_scroll(it, x, y, w, h):
		scrollViewport = gtk.ScrolledWindow()
		vadj = scrollViewport.get_vadjustment()
		vadj.connect('changed', it.reScrollV, scrollViewport)
		scrollViewport.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrollViewport.add(it)
		scrollViewport.set_size_request(w, h)
		it.hFixed.put(scrollViewport, x, y)

	def size(it, x, y):
		try:
			parent = it.get_parent()
			bPass = True
		except AttributeError, e:
			bPass = False
		if bPass and(isinstance(parent, gtk.ScrolledWindow)):
			parent.set_size_request(x, y)
		else:
			super(it.__class__, it).set_size_request(x, y)

	def move(it, x, y):
		try:
			parent = it.get_parent()
			bPass = True
		except AttributeError, e:
			bPass = False
		if bPass and(isinstance(parent, gtk.ScrolledWindow)):
			it.hFixed.move(parent, x, y)
		else:
			it.hFixed.move(it, x, y)

class TreeView(gtk.TreeView, MvScrolled):
	def __init__(it, model, hFixed, posX=0, posY=0, width=0, height=0):
		super(it.__class__, it).__init__(model)
		it.hFixed = hFixed
		it.autoscroll = True
		it.setup_scroll(posX, posY, width, height)

class TextView(gtk.TextView, MvScrolled):
	def __init__(it, hFixed, posX=0, posY=0, width=0, height=0, bWrap=False, bEditable=True, tabSpace=2, fontDesc=None):
		super(it.__class__, it).__init__()
		it.hFixed = hFixed
		it.autoscroll = True
		it.changed = False
		it.set_property("editable", bEditable)
		if fontDesc:
			it.modify_font(fontDesc)
			it.setTabSpace(tabSpace, fontDesc=fontDesc)
		if bWrap:
			it.set_wrap_mode(gtk.WRAP_WORD)
		it.setup_scroll(posX, posY, width, height)

	def set_text(it, txt):
		it.get_buffer().set_text(txt)
		it.changed = True

	clear_text = lambda it: it.set_text('')

	def get_text(it):
		tBuff = it.get_buffer()
		return tBuff.get_text(tBuff.get_start_iter(), tBuff.get_end_iter())
	
	def insert_end(it, txt, tag=None):
		buff = it.get_buffer()
		end = buff.get_end_iter()
		text = txt.encode('utf-8', errors='replace')
		if tag:
			buff.insert_with_tags(end, text, tag)
		else:
			buff.insert(end, text)
		del(end)
		it.changed = True

	def setTabSpace(it, spaces, fontDesc=None):
		pangoTabSpc = getTxtPixelWidth(it, ' '*spaces, fontDesc)
		tabArray =  pango.TabArray(1, True)
		tabArray.set_tab(0, pango.TAB_LEFT, pangoTabSpc)
		it.set_tabs(tabArray)
		return pangoTabSpc

def TreeTxtColumn(txtLabel, colWidth, nCol, lsRendProp, fontDesc=None):
	if txtLabel and not fontDesc:
		tvc = gtk.TreeViewColumn(txtLabel)
	else:
		tvc = gtk.TreeViewColumn()
	tvc.set_alignment(0.5) # Headers Center
	if colWidth:
		tvc.set_fixed_width(colWidth)
	if fontDesc:
		f = fontDesc
		ttcLabel = gtk.Label(txtLabel)
		ttcLabel.modify_font(fontDesc)
		tvc.set_widget(ttcLabel)
		ttcLabel.show()
	lscrtxt = []
	for n in nCol:
		crtxt = gtk.CellRendererText()
		if fontDesc:
			crtxt.set_property('font-desc', fontDesc)
		for Prop in lsRendProp:
			crtxt.set_property(*Prop)
		tvc.pack_start(crtxt, True)
		if type(n) in(int, str):
			tvc.set_attributes(crtxt, text=n)
		elif type(n)==tuple:
			if n[0]!=None and(callable(n[0])) and(len(n)>1):
				tvc.set_cell_data_func(crtxt, n[0], n[1:])
		lscrtxt.append(crtxt)
	return tvc, lscrtxt
