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

def Label(txtLabel, hFixed, posX, posY, width, height=None, fontDesc=None, xalign=None, selectable=False):
	hLabel = gtk.Label(txtLabel)
	if fontDesc:
		hLabel.modify_font(fontDesc)
	if type(xalign)==float and(0.<=xalign<=1.):
		yalign = hLabel.get_alignment()[1]
		hLabel.set_alignment(xalign, yalign)
	if type(selectable)==bool:
		hLabel.set_selectable(selectable)
	hLabel.show()
	if not height:
		height=Height
	hLabel.set_size_request(width, height)
	if hFixed:
		hFixed.put(hLabel, posX, posY)
	return hLabel

def Butt(txtLabel, hFixed, posX, posY, width, height=None, fileImage=None, stockID=None, fontDesc=None):
	"""If stockID is set, txtLabel set as True means full stock button,
	non-null string - own Label for stock image,
	in other case - button with only stock image"""
	if stockID == None and fileImage == None:
		hButt = gtk.Button(label=txtLabel, use_underline=False)
		if fontDesc:
			hLabel = hButt.child
			hLabel.modify_font(fontDesc)
	else:
		if type(txtLabel)==int or type(txtLabel)==float or type(txtLabel)==type(None) or (type(txtLabel)==str and txtLabel==''):
			txtLabel = bool(txtLabel)
		if type(txtLabel)==bool and txtLabel==True or type(txtLabel)==str:
			if stockID:
				hButt = gtk.Button(stock=stockID)
			elif fileImage:
				image = gtk.Image()
				image.set_from_file(fileImage)
				hButt = gtk.Button()
				hButt.add(image)
			if type(txtLabel)==str:
				hLabel = hButt.get_children()[0].get_children()[0].get_children()[1]
				hLabel.set_text(txtLabel)
				if fontDesc:
					hLabel.modify_font(fontDesc)
		else:
			image = gtk.Image()
			if stockID:
				image.set_from_stock(stockID, gtk.ICON_SIZE_BUTTON)
			elif fileImage:
				image.set_from_file(fileImage)
			hButt = gtk.Button()
			hButt.add(image)
	if not height:
		height = Height
	hButt.set_size_request(width, height)
	hFixed.put(hButt, posX, posY)
	return hButt

class ComboBox(gtk.ComboBox):
	def __init__(it, modelCb, hFixed, posX, posY, width, height=None, fontDesc=None, wrap=None, selTxt=0):
		super(gtk.ComboBox, it).__init__()
		it.hFixed = hFixed
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

def Entry(hFixed, posX, posY, width, height=None, startIco=None, clearIco=False, bEditable=True, fontDesc=None):
	def entryIcoClr(ed, icoPos, sigEvent):
		if icoPos == gtk.ENTRY_ICON_SECONDARY:
			ed.set_text('')
	hEntry = gtk.Entry()
	if fontDesc:
		hEntry.modify_font(fontDesc)
	if startIco:
		textInput.set_icon_from_pixbuf(0, startIco)
	if clearIco:
		hEntry.set_icon_from_stock(1, gtk.STOCK_CLOSE)
		hEntry.set_icon_tooltip_text (1, 'Clear')
		hEntry.connect("icon-release", entryIcoClr)
	hEntry.set_property("editable", bool(bEditable))
	if not height:
		height = Height
	hEntry.set_size_request(width, height)
	hFixed.put(hEntry, posX, posY)
	return hEntry

class TextView(gtk.TextView):
	def __init__(it, hFixed, posX, posY, width, height, bWrap=False, bEditable=True, tabSpace=2, fontDesc=None):
		super(gtk.TextView, it).__init__()
		it.hFixed = hFixed
		it.autoscroll = True
		it.changed = False
		it.set_property("editable", bEditable)
		if fontDesc:
			it.modify_font(fontDesc)
			it.setTabSpace(tabSpace, fontDesc=fontDesc)
		if bWrap:
			it.set_wrap_mode(gtk.WRAP_WORD)
		scrollViewTxt = gtk.ScrolledWindow()
		vadj = scrollViewTxt.get_vadjustment()
		vadj.connect('changed', it.reScrollV, scrollViewTxt)
		scrollViewTxt.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrollViewTxt.add(it)
		scrollViewTxt.set_size_request(width, height)
		hFixed.put(scrollViewTxt, posX, posY)

	def set_text(it, txt):
		it.get_buffer().set_text(txt)
		it.changed = True

	clear_text = lambda it: it.set_text('')

	def set_size_request(it, x, y):
		try:
			parent = it.get_parent()
			bPass = True
		except AttributeError, e:
			bPass = False
		if bPass and(isinstance(parent, gtk.ScrolledWindow)):
			parent.set_size_request(x, y)
		else:
			super(gtk.TextView, it).set_size_request(x, y)

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

	def reScrollV(it, adjV, scrollV):
		"""Scroll to the bottom of the TextView when the adjustment changes."""
		if it.autoscroll:
			adjV.set_value(adjV.upper - adjV.page_size)
			scrollV.set_vadjustment(adjV)
		return

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
		ttcLabel = gtk.Label(txtLabel)
		ttcLabel.modify_font(fontDesc)
		tvc.set_widget(ttcLabel)
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
