#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
# -*- tabstop: 4 -*-

'''
 This program source code file is shared library for easy pygtk+2 TextView widget
virtual terminal emulation.
 
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
class VTtags:
	def __init__(it, txtViewBuff):
		for tag_arg in (
			('bold', 'bld', pango.WEIGHT_BOLD),
			('underline', 'unl', pango.UNDERLINE_SINGLE),
			('black', 'fg', 'black'),
			('dk_grey','fg_gdk',  gtk.gdk.Color('#444')),
			('red', 'fg', 'red'),
			('pink', 'fg', 'pink'),
			('green', 'fg', 'green'),
			('lt_green', 'fg_gdk',  gtk.gdk.Color('#8F8')),
			('yellow', 'fg', 'yellow'),
			('lt_yellow', 'fg_gdk',  gtk.gdk.Color('#FF8')),
			('blue', 'fg', 'blue'),
			('lt_blue', 'fg_gdk',  gtk.gdk.Color('#88F')),
			('magenta', 'fg_gdk',  gtk.gdk.Color('#F0F')),
			('lt_magenta', 'fg_gdk',  gtk.gdk.Color('#F8F')),
			('cyan', 'fg', 'cyan'),
			('lt_cyan', 'fg_gdk',  gtk.gdk.Color('#8FF')),
			('white', 'fg', 'white'),
			('grey', 'fg', 'grey'),
			('bg_black', 'bk', 'black'),
			('bg_dk_grey','bk_gtk',  gtk.gdk.Color('#444')),
			('bg_red', 'bk', 'red'),
			('bg_pink', 'bk', 'pink'),
			('bg_green', 'bk', 'green'),
			('bg_lt_green', 'bk_gtk',  gtk.gdk.Color('#8F8')),
			('bg_yellow', 'bk', 'yellow'),
			('bg_lt_yellow', 'bk_gtk',  gtk.gdk.Color('#FF8')),
			('bg_blue', 'bk', 'blue'),
			('bg_lt_blue', 'bk_gtk',  gtk.gdk.Color('#88F')),
			('bg_magenta', 'bk_gtk',  gtk.gdk.Color('#F0F')),
			('bg_lt_magenta', 'bk_gtk',  gtk.gdk.Color('#F8F')),
			('bg_cyan', 'bk', 'cyan'),
			('bg_lt_cyan', 'bk_gtk',  gtk.gdk.Color('#8FF')),
			('bg_white', 'bk', 'white'),
			('bg_grey', 'bk', 'grey'),
			):
			name, case, _attr = tag_arg
			if case=='bk':
				setattr(it, name, txtViewBuff.create_tag(name, background = _attr))
			elif case=='bk_gtk':
				setattr(it, name, txtViewBuff.create_tag(name, background_gdk = _attr))
			elif case=='fg':
				setattr(it, name, txtViewBuff.create_tag(name, foreground = _attr))
			elif case=='fg_gdk':
				setattr(it, name, txtViewBuff.create_tag(name, foreground_gdk = _attr))
			elif case=='bld':
				setattr(it, name, txtViewBuff.create_tag(name, weight = _attr))
			elif case=='unl':
				setattr(it, name, txtViewBuff.create_tag(name, underline = _attr))

	def get(it, tag_name):
		if tag_name and(hasattr(it, tag_name)):
			return getattr(it, tag_name)
		return None

class VTtext:
	def __init__(it, textView):
		"""
		cursor controls
		ESC[#;#H or ESC[#;#f	moves cursor to line #, column #
		ESC[#A	moves cursor up # lines
		ESC[#B	moves cursor down # lines
		ESC[#C	moves cursor right # spaces
		ESC[#D	moves cursor left # spaces
		ESC[#;#R	reports current cursor line & column
		ESC[s	save cursor position for recall later
		ESC[u	Return to saved cursor position
		erase functions
		ESC[2J	clear screen and home cursor
		ESC[K	clear to end of line
		"""
		it.logView = textView
		tBuff= textView.get_buffer()
		it.logTags = VTtags(tBuff)
		Es = '\x1B'
		Esc = Es+'['
		it.dcTermCodeToTagName = {
			Esc+"0m": None,
			Esc+"1m": 'bold',
			Esc+"4m": 'underline',
			#Esc+"5m": 'blink on',
			#Esc+"7m": 'reverse video on',
			#Esc+"8m": 'nondisplayed (invisible)',
			#Esc+"39;49m": 
			#Es+"(B": 
			Esc+"30m": 'black',
			Esc+"30;1m": 'dk_grey',
			Esc+"31m": 'red',
			Esc+"31;1m": 'pink',
			Esc+"32m": 'green',
			Esc+"32;1m": 'lt_green',
			Esc+"33m": 'yellow',
			Esc+"33;1m": 'lt_yellow',
			Esc+"34m": 'blue',
			Esc+"34;1m": 'lt_blue',
			Esc+"35m": 'magenta',
			Esc+"35;1m": 'lt_magenta',
			Esc+"36m": 'cyan',
			Esc+"36;1m": 'lt_cyan',
			Esc+"37m": 'white',
			Esc+"37;1m": 'grey',
			Esc+"40m": 'bg_black',
			Esc+"40;1m": 'bg_dk_grey',
			Esc+"41m": 'bg_red',
			Esc+"41;1m": 'bg_pink',
			Esc+"42m": 'bg_green',
			Esc+"42;1m": 'bg_lt_green',
			Esc+"43m": 'bg_yellow',
			Esc+"43;1m": 'bg_lt_yellow',
			Esc+"44m": 'bg_blue',
			Esc+"44;1m": 'bg_lt_blue',
			Esc+"45m": 'bg_magenta',
			Esc+"45;1m": 'bg_lt_magenta',
			Esc+"46m": 'bg_cyan',
			Esc+"46;1m": 'bg_lt_cyan',
			Esc+"47m": 'bg_white',
			Esc+"47;1m": 'bg_grey',
			}
		it.lsTag = []
		it.buffConCode = ''
		it.bufRN = ''
		it.txtBfSchFlags = gtk.TEXT_SEARCH_TEXT_ONLY | gtk.TEXT_SEARCH_VISIBLE_ONLY

	def logWrite(it, fd, condition):
		txtWgt = it.logView
		txtBuff = txtWgt.get_buffer()
		try:
			newTxt = fd.read().decode('utf-8')
		except UnicodeDecodeError:
			print("Can't decode to UTF-8")
			return True
			#newTxt = ''
		for char in newTxt:
			if char=='\x1B' and it.buffConCode=='\x1B':
				it.buffConCode = ''
			elif char=='\x1B' or it.buffConCode:
				it.buffConCode += char
				if char!='m':
					continue
				currTag = it.logTags.get(it.dcTermCodeToTagName.get(it.buffConCode))
				if currTag:
					it.lsTag.append(currTag)
				else:
					if it.buffConCode=="\x1B[0m":
						while len(it.lsTag):
							it.lsTag.pop()
					else:
						print("Unknown Console Code:<Esc>%s" % it.buffConCode[1:])
				it.buffConCode = ''
				continue
			iterEnd = txtBuff.get_end_iter()
			if char=='\n':
				it.bufRN += char
			if char=='\r':
				it.bufRN = char
			else:
				if char!='\n' and(it.bufRN=='\r'):
					result = iterEnd.backward_search('\n', it.txtBfSchFlags)
					if result:
						iterBogus, iterStartDel = result
						del(iterBogus, result)
						txtBuff.delete(iterStartDel, iterEnd)
						del(iterStartDel)
						it.bufRN = ''
				if it.lsTag:
					txtBuff.insert_with_tags(iterEnd, char, *it.lsTag)
				else:
					txtBuff.insert(iterEnd, char)
		return True
