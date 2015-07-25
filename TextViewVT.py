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

dbg = False
from sys import stdout as sto
def _err(_str):
	sto.write(str(_str))
def _dbg(_str):
	if dbg: sto.write(str(_str))
_dbn = lambda _str: None

import gtk, pango
from gtk.gdk import Color
class TextBufferTags:
	def __init__(it, txtViewBuff):
		it.lsTags = []
		for tag_arg in (
			('bold', 'bld', pango.WEIGHT_BOLD),
			('italic', 'stl', pango.STYLE_ITALIC),
			('underline', 'unl', pango.UNDERLINE_SINGLE),
			('fg_black', 'fg', 'black'),
			('fg_dk_grey','fg_gdk',  Color('#444')),
			('fg_red', 'fg', 'red'),
			('fg_pink', 'fg', 'pink'),
			('fg_green', 'fg', 'green'),
			('fg_lt_green', 'fg_gdk',  Color('#8F8')),
			('fg_yellow', 'fg', 'yellow'),
			('fg_lt_yellow', 'fg_gdk',  Color('#FF8')),
			('fg_blue', 'fg', 'blue'),
			('fg_lt_blue', 'fg_gdk',  Color('#88F')),
			('fg_magenta', 'fg_gdk',  Color('#F0F')),
			('fg_lt_magenta', 'fg_gdk',  Color('#F8F')),
			('fg_cyan', 'fg', 'cyan'),
			('fg_lt_cyan', 'fg_gdk',  Color('#8FF')),
			('fg_white', 'fg', 'white'),
			('fg_grey', 'fg', 'grey'),
			('bg_black', 'bk', 'black'),
			('bg_dk_grey','bk_gtk',  Color('#444')),
			('bg_red', 'bk', 'red'),
			('bg_pink', 'bk', 'pink'),
			('bg_green', 'bk', 'green'),
			('bg_lt_green', 'bk_gtk',  Color('#8F8')),
			('bg_yellow', 'bk', 'yellow'),
			('bg_lt_yellow', 'bk_gtk',  Color('#FF8')),
			('bg_blue', 'bk', 'blue'),
			('bg_lt_blue', 'bk_gtk',  Color('#88F')),
			('bg_magenta', 'bk_gtk',  Color('#F0F')),
			('bg_lt_magenta', 'bk_gtk',  Color('#F8F')),
			('bg_cyan', 'bk', 'cyan'),
			('bg_lt_cyan', 'bk_gtk',  Color('#8FF')),
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
			elif case=='stl':
				setattr(it, name, txtViewBuff.create_tag(name, style = _attr))

	def all_reset(it):
		while len(it.lsTags):
			it.lsTags.pop()

	def fg_bg_reset(it):
		rm_tags = []
		for idx, tag in enumerate(it.lsTags):
			name = tag.get_property("name")
			if name[:3] in 'fg_ bg_'.split():
				rm_tags.append(idx)
		for idx in reversed(rm_tags):
			it.lsTags.pop(idx)

	def cm_reset(it, code):
		rm_tags = []
		for idx, tag in enumerate(it.lsTags):
			name = tag.get_property("name")
			if name[:3]==code:
				rm_tags.append(idx)
		for idx in reversed(rm_tags):
			it.lsTags.pop(idx)

	fg_reset = lambda it: it.cm_reset('fg_')
	bg_reset = lambda it: it.cm_reset('bg_')

	def get(it, tag_name):
		if tag_name and(hasattr(it, tag_name)):
			it_attr =  getattr(it, tag_name)
			if callable(it_attr):
				it_attr()
				return True
			elif isinstance(it_attr, gtk.TextTag):
				it.cm_reset(tag_name[:3])
				it.lsTags.append(it_attr)
				return True
		return None

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

import re
rTxt = '(?P<TermCtrl>(\x1B|(\^\[))(\[|\()(?P<p1>\d*);?(?P<p2>\d*)(?P<Code>[A-HJKSTfhilmnsu]){1})'
reTermCtrl = re.compile(rTxt, re.X | re.U)


def dbgReportIterPos(tbf, bfi):
	p, a = bfi.get_offset(), tbf.get_char_count()
	x, y, w, h = bfi.get_line_offset(), bfi.get_line(), bfi.get_chars_in_line(), tbf.get_line_count()-1
	_dbg("p:%i/%i,↓:%i/%i,→:%i/%i\n" % (p, a, y, h, x, w))

class VTtext:
	#Es = '\x1B'
	#Esc = Es+'['
	dcCodes = {
		'A': 'cursor_up', # 
		'B': 'cursor_down', # 
		'C': 'cursor_forward', # 
		'D': 'cursor_back', # 
		#'E': 'line_next_home', # 
		#'F': 'line_previous_home', # 
		#'G': 'cursor_x', # Cursor Horizontal Absolute
		#'H': 'cursor_yx', # Cursor Position
		#'J': 'clear_screen', # 
		'K': 'clear_line', # 
		#'S': 'scroll_up', # 
		#'T': 'scroll_down', # 
		#'f': 'cursor_yx', # Horizontal and Vertical Position
		'm': '_m', # Select Graphic Rendition
		#'n': 'report_pos', # must be in reply to stdin of app by ESC[x;yR
		#'s': 'store_pos', # 
		#'u': 'load_pos', # 
		}
	dc_m = { # https://en.wikipedia.org/wiki/ANSI_escape_code
		0: 'all_reset',
		#5: 'blink on',
		#7: 'reverse video on',
		#8: 'nondisplayed (invisible)',
		(39, 49): 'fg_bg_reset', # Default text color (foreground); Default background color
		39: 'fg_reset', # Default text color (foreground)
		49: 'bg_reset', # Default background color
		1: 'bold',
		3: 'italic',
		4: 'underline',
		30: 'fg_black',
		(30, 1): 'fg_dk_grey',
		31: 'fg_red',
		(31, 1): 'fg_pink',
		32: 'fg_green',
		(32, 1): 'fg_lt_green',
		33: 'fg_yellow',
		(33, 1): 'fg_lt_yellow',
		34: 'fg_blue',
		(34, 1): 'fg_lt_blue',
		35: 'fg_magenta',
		(35, 1): 'fg_lt_magenta',
		36: 'fg_cyan',
		(36, 1): 'fg_lt_cyan',
		37: 'fg_white',
		(37, 1): 'fg_grey',
		40: 'bg_black',
		(40, 1): 'bg_dk_grey',
		41: 'bg_red',
		(41, 1): 'bg_pink',
		42: 'bg_green',
		(42, 1): 'bg_lt_green',
		43: 'bg_yellow',
		(43, 1): 'bg_lt_yellow',
		44: 'bg_blue',
		(44, 1): 'bg_lt_blue',
		45: 'bg_magenta',
		(45, 1): 'bg_lt_magenta',
		46: 'bg_cyan',
		(46, 1): 'bg_lt_cyan',
		47: 'bg_white',
		(47, 1): 'bg_grey', # ;1 - Bold or increased intensity
		}

	def __init__(it, textView):
		textView.set_overwrite(True)
		it.chPtr = 0
		it.busy = False
		it.logView = textView
		tbf = it.txtBuff = textView.get_buffer()
		it.logBufTags = TextBufferTags(tbf)
		it.buffConCode = ''
		it.txtBfSchFlags = gtk.TEXT_SEARCH_TEXT_ONLY | gtk.TEXT_SEARCH_VISIBLE_ONLY

	def _m(it, bfi, p1, p2):
		if p1 is None and(p2 is None):
			subcode = 0
			_dt = ''
		elif type(p1) is int and(type(p2) is int):
			subcode = p1, p2
			_dt = "%i;%i" % (p1, p2)
		elif type(p1) is int and(p2 is None):
			subcode = p1
			_dt = "%i" % p1
		else:
			_err("Strange Select Graphic Rendition code(s): %s;%s\n" % (str(p1), str(p2)))
			return False
		term_code = it.dc_m.get(subcode)
		if not(term_code):
			_err("Unknown Select Graphic Rendition code(s): %s\n" %  str(subcode))
			return False
		if not(it.logBufTags.get(term_code)):
			_err("Unhandled tag code(no TextBufferTags.%s method)\n" % term_code)
			return False
		#_dbg("Handle <Esc><[|(>%sm\n" % _dt)
		return True

	def cursor(it, bfi, p1, p2, code):
		tbf = it.txtBuff
		args = tuple(arg for arg in (p1, p2) if type(arg) is int)
		if not(args):
			count = 1
			_dt = 'default'
		elif len(args)==1:
			count = p1
			_dt = "%i" % p1
		else:
			_dbg("Strange args to Move Cursor %s: %i;%i\n" % (code.capitalize(), p1, strp2))
			return False
		ds = {'up': '↑', 'down': '↓', 'forward': '→', 'back': '←'}[code]
		_dbg("Handle %sx%s\n" % (ds, _dt))
		dbgReportIterPos(tbf, bfi)
		x = bfi.get_line_offset()
		y =  bfi.get_line()
		w = bfi.get_chars_in_line()
		h = tbf.get_line_count()-1
		if code=='up':
			bfi.backward_lines(count)
		elif code=='down':
			bfi.forward_lines(count)
		elif code=='forward':
			forward = min(w-x, count)
			if forward:
				bfi.forward_chars(forward)
			if w-x<count:
				tbf.insert(bfi, ' '*(count+x-w))
		elif code=='back':
			backward = min(x, count)
			if backward:
				bfi.backward_chars(backward)
		if code in('up', 'down'):
			w = bfi.get_chars_in_line()
			forward = min(x, w)
			if forward:
				bfi.forward_chars(forward)
			if x>w:
				spc = u' '*(x-w)
				_dbg("Space Fill[%i]\n" % len(spc))
				tbf.insert(bfi, spc)
		dbgReportIterPos(tbf, bfi)
		return True

	cursor_up = lambda it, bfi, p1, p2: it.cursor(bfi, p1, p2, 'up')
	cursor_down = lambda it, bfi, p1, p2: it.cursor(bfi, p1, p2, 'down')
	cursor_forward = lambda it, bfi, p1, p2: it.cursor(bfi, p1, p2, 'forward')
	cursor_back = lambda it, bfi, p1, p2: it.cursor(bfi, p1, p2, 'back')

	def clear_line(it, bfi, *args_in):
		args = tuple(arg for arg in args_in if type(arg) is int)
		if not(args):
			code = 0
			_dt = 'default'
		elif len(args)==1 and(args[0] in range(0, 3)):
			code = args[0]
			_dt = "%i" % p1
		else:
			_dbg("Strange args to Clear Line: %s\n" % str(args_in))
			return False
		tbf = it.txtBuff
		y, h =  bfi.get_line(), tbf.get_line_count()-1
		x, w = bfi.get_line_offset(), bfi.get_chars_in_line()-int(y<h)
		cfi = bfi.copy()
		fwd = w-x
		if code in(0, 2) and fwd:
			cfi.forward_chars(w-x)
		if code in(1, 2) and (x):
			bfi.backward_chars(x)
		_dc = ord(cfi.get_char())
		_dbg("Clearing %s[%i/%i]:by %s code\n\tin pos:%i/%i\n" % (
			('line to the end', 'line from the beginning', 'the whole line')[code],
			y, h, _dt , x, w))
		tbf.delete(bfi, cfi)
		if code==1 and (x): # 
			tbf.insert(bfi, ' '*x)

	def clear_text(it):
		it.logView.clear_text()
		it.chPtr = 0

	def insert_p(it, bfi, txt):
		if not(txt):
			return
		tbf = it.txtBuff
		y, h =  bfi.get_line(), tbf.get_line_count()-1
		x, w = bfi.get_line_offset(), bfi.get_chars_in_line()-int(y<h)
		ln = len(txt)
		cfi = bfi.copy()
		if w-x and (ln):
			forward = min(ln, w-x) #-1
			cfi.forward_chars(forward)
			_dbg("insert_p::N forward:%i,len(txt):%i,→:%i/%i\n" % (forward, ln, x, w))
			_dt = tbf.get_slice(bfi, cfi).decode('utf-8')
			_dc = cfi.get_char()
			#if ord(_dc):
			_dbg("Deleting[%i]:@%s\n\t%s\n" % (len(_dt), repr(_dc), repr(_dt)))
			tbf.delete(bfi, cfi)
		ltg = it.logBufTags
		if ltg.lsTags:
			tbf.insert_with_tags(bfi, txt, *ltg.lsTags)
		else:
			tbf.insert(bfi, txt)

	def insertCtrl(it, bfi, txt):
		if not(txt):
			return
		tbf = it.txtBuff
		try:
			txt = txt.decode('utf-8')
		except UnicodeDecodeError:
			_err("Can't decode to UTF-8:\n'%s'\n" % txt)
			return
		if dbg:
			max_loop = 1000
		loop = 0
		_dbn("insertCtrl[%i]:\n\t%s\n" % (len(txt),repr(txt)))
		while txt:
			if dbg and(loop>=max_loop):
				_dbg("Overlooped Inserts, unprocessed text:\n\t%s\n" % repr(txt))
				break
			# Which code ist first?
			finds = tuple(txt.find(s) for s in '\b \r \n'.split(' ') if s in txt) # \x08
			if finds:
				findPos = min(finds)
				code = txt[findPos]
				txt_o = txt[:findPos]
				if txt_o:
					it.insert_p(bfi, txt_o)
				txt = txt[findPos+1:]
				_dbn("\x1b[32;1m%i\x1b[m:Leaving txt[%i]:\n\t%s\n" % (loop, len(txt), repr(txt)))
				if code=='\b':
					n = 1
					while txt and(txt[0]=='\b'):
						txt = txt[1:]
						n += 1
					x = bfi.get_line_offset()
					bspc = min(x,n)
					if bspc:
						bfi.backward_chars(bspc)
					_dbg("\x1b[32;1m%i\x1b[m:Backspace_B[%i/%i]\n" % (loop, bspc, n))
				elif code=='\r':
					if txt_o:
						_dbg("\x1b[32;1m%i\x1b[m:Insert_R[%i]:\n\t%s\n" % (loop, len(txt_o), repr(txt_o)))
					x = bfi.get_line_offset()
					if x:
						_dbg("\x1b[32;1m%i\x1b[m:Backward_R: %i\n" % (loop, x))
						result = bfi.backward_chars(x)
				elif code=='\n':
					if txt_o:
						_dbg("\x1b[32;1m%i\x1b[m:Insert_N[%i]:\n\t%s\n" % (loop, len(txt_o), repr(txt_o)))
					y =  bfi.get_line()
					h = tbf.get_line_count()-1
					bfi.forward_line()
					_dbn("\x1b[32;1m%i\x1b[m:N forward, ↓:%i/%i\n" % (loop, y, h))
					if y>=h:
						tbf.insert(bfi, '\n')
						_dbg("\x1b[32;1m%i\x1b[m:N add new line …\n"% loop)
				else:
					_err("\x1b[32;1m%i\x1b[m:Very strange, That code shuld be omitted:\n\t%s…\n" % (loop, repr(code)))
			else:
				_dbg("\x1b[32;1m%i\x1b[m:Insert_O[%i]:\n\t%s\n" % (loop, len(txt), repr(txt)))
				it.insert_p(bfi, txt)
				txt = u''
			_dbg("\x1b[32;1m%i\x1b[m:Left txt[%i]:\n\t%s\n" % (loop, len(txt),repr(txt)))
			if dbg:
				loop += 1

	def insert_ext(it, txt, tag=None):
		tbf = it.txtBuff
		bfi = it.txtBuff.get_iter_at_offset(it.chPtr)
		if tag:
			tbf.insert_with_tags(bfi, txt, tag)
		else:
			tbf.insert(bfi, txt)
		'''
		lsTags = it.logBufTags.lsTags
		saveTags = list(lsTags)
		it.logBufTags.all_reset()
		if tag:
			lsTags.append(tag)
		it.insertCtrl(bfi, txt)
		it.logBufTags.all_reset()
		lsTags.extend(saveTags)
		'''
		it.chPtr = bfi.get_offset()

	def escHandle(it, newTxt):
		txtWgt = it.logView
		it.busy = True
		#_dbg("Raw read:\n'%s'\n" % newTxt)
		_dbg("Raw read repr():\n%s\n" % repr(newTxt))
		#bfi = it.txtBuff.get_end_iter()
		bfi = it.txtBuff.get_iter_at_offset(it.chPtr)
		if it.buffConCode:
			newTxt = it.buffConCode+newTxt
			it.buffConCode = ''
		while newTxt:
			findEsc = newTxt.find('\x1B')
			if findEsc>-1:
				if findEsc>0:
					it.insertCtrl(bfi, newTxt[:findEsc])
				mTermCtrl = reTermCtrl.search(newTxt)
				if mTermCtrl:
					ctrlB, ctrlE = mTermCtrl.span()
					Code, p1, p2 = mTermCtrl.group('Code'),  mTermCtrl.group('p1'), mTermCtrl.group('p2')
					newTxt = newTxt[ctrlE:]
					select_code = it.dcCodes.get(Code)
					if select_code and(hasattr(it, select_code)):
						it_handle = getattr(it, select_code)
						if callable(it_handle):
							params = tuple(map(lambda p: int(p) if p.isdigit() else None, (p1, p2)))
							bHandled = it_handle(bfi, *params)
						else:
							_err("Uhandled Console Code:<Esc>%s - VTtext.%s not callable…\n" % (
								mTermCtrl.group('TermCtrl')[1:], select_code))
					else:
						_err("Unsupported Console Code:<Esc>%s\n" % mTermCtrl.group('TermCtrl')[1:])
				else: #Esc found but not ended
					if len(newTxt)>24: # Overlooping (In founding unknown escape code) prevent
						_err("Unknown Console Code in text:<Esc>%s\n" % newTxt[1:])
						newTxt = newTxt[1:]
						continue
					it.buffConCode = newTxt
					newTxt = ''
				continue
			else:
				it.insertCtrl(bfi, newTxt)
				newTxt = ''
		it.chPtr = bfi.get_offset()
		#_dbg("Insert: %s\n" % str(bfi.get_offset()))
		it.busy = False

	def logWrite(it, fd, condition):
		it.escHandle(fd.read())
		return True

	def ptyConnect(it, watchcall=None):
		if watchcall is None:
			watchcall = it.logWrite
		from gobject import IO_IN as ioIN, IO_HUP as ioHUP, io_add_watch as addWatch
		import pty, fcntl
		from os import ttyname, fdopen as fdo, O_NDELAY as nDly
		it.pty_parent_fd, it.pty_child_fd = pty.openpty()
		_dbg("parent pty: %s\n" % ttyname(it.pty_parent_fd))
		_dbg("child pty: %s\n" % ttyname(it.pty_child_fd))
		it.fd = fdo(it.pty_parent_fd, 'r')
		file_flags = fcntl.fcntl(it.fd, fcntl.F_GETFL)
		fcntl.fcntl(it.fd, fcntl.F_SETFL, file_flags|nDly)
		it.watchID = addWatch(it.fd, ioIN, watchcall)

	def ptyDisconnect(it):
		from gobject import source_remove as unWatch
		unWatch(it.watchID)
		it.fd.close()
