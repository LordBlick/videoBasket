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

import re
#rexRGB = re.compile('#[\dA-F]{

from time import sleep as slp
import gtk, pango
from gtk.gdk import color_parse as _cp
class TextBufferTags:
	def __init__(it, tbf): # tbf - instance of gtk.TextBuffer
		it.lsTags = []
		it.bold = tbf.create_tag('bold', weight = pango.WEIGHT_BOLD)
		it.italic = tbf.create_tag('italic', style = pango.STYLE_ITALIC)
		it.underline = tbf.create_tag('underline', underline = pango.UNDERLINE_SINGLE)
		for name, color in (
			('black', 'black'),
			('dk_grey', '#444'),
			('red', 'red'),
			('pink', 'pink'),
			('green', 'green'),
			('lt_green', '#5F5'),
			('yellow', '#AA0'),
			('lt_yellow', '#FF5'),
			('blue', 'blue'),
			('lt_blue', '#55F'),
			('magenta', '#A0A'),
			('lt_magenta', '#F0F'),
			('cyan', 'cyan'),
			('lt_cyan', '#AFF'),
			('white', 'white'),
			('grey', 'grey'),
			):
			setattr(it, 'fg_'+name, tbf.create_tag('fg_'+name, foreground_gdk=_cp(color)))
			setattr(it, 'bg_'+name, tbf.create_tag('bg_'+name, background_gdk=_cp(color)))
		_dbg("yellow:%s\n" % str(it.bg_yellow.get_property('background-gdk')))
		_dbg("lt_yellow:%s\n" % str(it.bg_lt_yellow.get_property('background-gdk')))

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
		if not(tag_name):
			return False
		if not(hasattr(it, tag_name)) and(tag_name[:4] in('fg__', 'bg__')):
			try:
				color = _cp('#'+tag_name[3:])
			except ValueError:
				return False
			if tag_name[:2]=='fg':
				setattr(it, tag_name, tbf.create_tag(tag_name, foreground_gdk=color))
			elif tag_name[:2]=='bg':
				setattr(it, tag_name, tbf.create_tag(tag_name, background_gdk=color))
		if not(hasattr(it, tag_name)):
			return False
		it_attr =  getattr(it, tag_name)
		if callable(it_attr):
			it_attr()
			return True
		elif isinstance(it_attr, gtk.TextTag):
			it.cm_reset(tag_name[:3])
			it.lsTags.append(it_attr)
			return True
		return False

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
rTxt = '(?P<TermCtrl>(\x1B|(\^\[))(\[|\()(?P<Params>[;\d]*)(?P<Code>[A-HJKSTfhilmnsu]){1})'
reTermCtrl = re.compile(rTxt, re.X | re.U)


def dbgReportIterPos(tbf, bfi):
	p, a = bfi.get_offset(), tbf.get_char_count()
	x, y, w, h = bfi.get_line_offset(), bfi.get_line(), bfi.get_chars_in_line(), tbf.get_line_count()-1
	_dbg("p:%i/%i,↓:%i/%i,→:%i/%i\n" % (p, a, y, h, x, w))

# Default color levels for the color cube - author https://gist.github.com/TerrorBite/
# from calc256.py: https://gist.github.com/TerrorBite/e738e25881d4aecf9043
cubelevels = [0x00, 0x5F, 0x87, 0xAF, 0xD7, 0xFF]
# Generate a list of midpoints of the above list
snaps = ((x+y)/2 for x, y in zip(cubelevels, [0]+cubelevels)[1:])
_err("###\nSnaps:%s\n###\n" % str(tuple(snaps)))

def rgb2short(r, g, b):
	'''Converts RGB values to the nearest equivalent xterm-256 color.
	'''
	# Using list of snap points, convert RGB value to cube indexes
	r, g, b = map(lambda x: len(tuple(s for s in snaps if s<x)), (r, g, b))
	# Simple colorcube transform
	return r*36 + g*6 + b + 16

def base6(number):
	d, m = divmod(number, 6)
	m_base = ''.join(map(lambda i: str(i), range(6)))[m]
	if d > 0:
		return base6(d)+m_base
	return m_base

def code2rgb(code):
	if code==7:
		r, g, b = (0x5F,)*3
	elif code==8:
		r, g, b = (0xB0,)*3
	elif code<16:
		r, g, b, l = reversed(map(lambda s: int(s), '{:04b}'.format(code)))
		r, g, b = map(lambda c: (l+1)*c*0x7F+l, (r, g, b))
	elif 232>code>15: # a
		r, g, b = map(lambda s: int(s), base6(code-16))
	elif 255>code>231: # end greyscale
		r, g, b = (((code-231)*256/24)+8,)*3
	

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
		#(38, 5): 'fg_ext_pallette',
		39: 'fg_reset', # Default text color (foreground)
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
		#(48, 5): 'bg_ext_pallette',
		49: 'bg_reset', # Default background color
		(39, 49): 'fg_bg_reset', # Default text color (foreground); Default background color
		}

	def __init__(it, textView):
		if not(isinstance(textView, gtk.TextView)):
			raise TypeError("Class %s initial argument must be gtk.TextView instance used to write console output" % it.__class__.__name__)
		textView.set_overwrite(True)
		it.chPtr = 0
		it.busy = False
		it.logView = textView
		tbf = it.txtBuff = textView.get_buffer()
		it.logBufTags = TextBufferTags(tbf)
		it.buffConCode = ''
		it.proc = None
		it.trans_rr = False


	def _m(it, bfi, *args_in):
		args = tuple(arg for arg in args_in if type(arg) is int)
		_la = len(args)
		if not(args):
			subcode = 0
		elif _la==1:
			subcode = args[0]
		elif _la==2:
			if args[0]==0:
				it.logBufTags.all_reset()
				subcode = args[1]
			else:
				subcode = args[0], args[1]
		#elif _la==3 and(args[0] in(38, 48)) and(args[1]==5) and(args[2]in range(0, 16)):
			#subcode = args[0], args[2]
		else:
			_err("Strange Select Graphic Rendition code(s): %s\n" % str(';'.join(args)))
			return False
		term_code = it.dc_m.get(subcode)
		if not(term_code):
			_err("Unknown Select Graphic Rendition code(s): %s\n" %  str(subcode))
			return False
		if not(it.logBufTags.get(term_code)):
			_err("Unhandled tag code(no TextBufferTags.%s method)\n" % term_code)
			return False
		#_dt = ';'.join(args)
		#_dbg("Handle <Esc><[|(>%sm\n" % _dt)
		return True

	def cursor(it, bfi, code, *args_in):
		tbf = it.txtBuff
		args = tuple(arg for arg in args_in if type(arg) is int)
		if not(args):
			count = 1
			_dt = 'default'
		elif len(args)==1:
			count = args[0]
			_dt = "%i" % count
		else:
			_err("Strange args to Move Cursor %s: %s\n" % (code.capitalize(), str(args)))
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

	cursor_up = lambda it, bfi, *args_in: it.cursor(bfi, 'up', *args_in)
	cursor_down = lambda it, bfi, *args_in: it.cursor(bfi, 'down', *args_in)
	cursor_forward = lambda it, bfi, *args_in: it.cursor(bfi, 'forward', *args_in)
	cursor_back = lambda it, bfi, *args_in: it.cursor(bfi, 'back', *args_in)

	def get_coords(it, bfi, tbf):
		y, h =  bfi.get_line(), tbf.get_line_count()-1
		x, w = bfi.get_line_offset(), bfi.get_chars_in_line()-int(y<h)
		return x, y, w, h

	def cursor_yx(it, bfi, row, column):
		if row is None:
			row = 1
		row -= 1 # rebase from 1 to 0
		if column is None:
			column = 1
		column -= 1 # rebase from 1 to 0
		tbf = it.txtBuff
		x, y, w, h = it.get_coords(bfi, tbf)
		if row>h:
			pass
		else:
			pass

	def clear_line(it, bfi, *args_in):
		args = tuple(arg for arg in args_in if type(arg) is int)
		if not(args):
			code = 0
			_dt = 'default'
		elif len(args)==1 and(args[0] in range(0, 3)):
			code = args[0]
			_dt = "%i" % code
		else:
			_dbg("Strange args to Clear Line: %s\n" % str(args_in))
			return False
		tbf = it.txtBuff
		x, y, w, h = it.get_coords(bfi, tbf)
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
		return True

	def clear_text(it):
		it.logView.clear_text()
		it.chPtr = 0

	def insert_p(it, bfi, txt):
		if not(txt):
			return
		tbf = it.txtBuff
		x, y, w, h = it.get_coords(bfi, tbf)
		ln = len(txt)
		cfi = bfi.copy()
		if w-x and (ln):
			forward = min(ln, w-x) #-1
			cfi.forward_chars(forward)
			_dbg("insert_p::N forward:%i,len(txt):%i,→:%i/%i\n" % (forward, ln, x, w))
			_dt = tbf.get_slice(bfi, cfi).decode('utf-8')
			_dc = cfi.get_char()
			_dbg("Deleting[%i]:@%s\n\t%s\n" % (len(_dt), repr(_dc), repr(_dt)))
			tbf.delete(bfi, cfi)
		ltg = it.logBufTags
		if ltg.lsTags:
			tbf.insert_with_tags(bfi, txt, *ltg.lsTags)
		else:
			tbf.insert(bfi, txt)

	def asciiCtrlHandle(it, bfi, txt):
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
		_dbn("asciiCtrlHandle[%i]:\n\t%s\n" % (len(txt),repr(txt)))
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
					if it.trans_rr and(txt[0]=='\r'):
						txt[0]=='\n'
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
					it.asciiCtrlHandle(bfi, newTxt[:findEsc])
				mTermCtrl = reTermCtrl.search(newTxt)
				if mTermCtrl:
					ctrlB, ctrlE = mTermCtrl.span()
					Code  = mTermCtrl.group('Code')
					newTxt = newTxt[ctrlE:]
					select_code = it.dcCodes.get(Code)
					if select_code and(hasattr(it, select_code)):
						it_handle = getattr(it, select_code)
						if callable(it_handle):
							params = tuple(map(
								lambda p: int(p) if p.isdigit() else None, mTermCtrl.group('Params').split(';')))
							bHandled = it_handle(bfi, *params)
						else:
							bHandled = False
							_err("VTtext.%s not callable…\n" % (select_code))
						if not(bHandled):
							_err("Uhandled Console Code:<Esc>%s\n" % (mTermCtrl.group('TermCtrl')[1:]))
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
				it.asciiCtrlHandle(bfi, newTxt)
				newTxt = ''
		it.chPtr = bfi.get_offset()
		#_dbg("Insert: %s\n" % str(bfi.get_offset()))
		it.busy = False

	def ptyReceiver(it, fd, condition):
		it.escHandle(fd.read())
		return True

	def ptyConnect(it, watchcall=None):
		if watchcall is None:
			watchcall = it.ptyReceiver
		from gobject import IO_IN as ioIN, IO_HUP as ioHUP, io_add_watch as addWatch
		import pty, fcntl
		from os import ttyname, fdopen as fdo, O_NONBLOCK as nBlk, O_RDONLY as RdO, O_NDELAY as nDly,\
			mkfifo as mkff, path as ph, getpid, open as oo
		it.pid = pid =  getpid()
		it.pty_parent_fd, it.pty_child_fd = pty.openpty()
		_dbg("pid: %s\n" % pid)
		_dbg("parent pty: %s\n" % ttyname(it.pty_parent_fd))
		_dbg("child pty: %s\n" % ttyname(it.pty_child_fd))
		it.fd = fdo(it.pty_parent_fd, 'r')
		file_flags = fcntl.fcntl(it.fd, fcntl.F_GETFL)
		fcntl.fcntl(it.fd, fcntl.F_SETFL, file_flags|nDly)
		it.watchID = addWatch(it.fd, ioIN, watchcall)
		#tmpdir = ph.expanduser('~/tmp')
		#if not(ph.isdir(tmpdir)):
			#tmpdir = '/tmp'
		#ff_in_fn = it.fifo_in_fn = ph.join(tmpdir, ".%s-stdin.%i" % (ph.basename(__file__).split('.')[0], pid))
		#ff_err_fn = it.fifo_err_fn = ph.join(tmpdir, ".%s-stderr.%i" % (ph.basename(__file__).split('.')[0], pid))
		#_dbg("fifo in filename: %s\n" % ff_in_fn)
		#_dbg("fifo err filename: %s\n" % ff_err_fn)
		#mkff(ff_in_fn) # for future use to control stdin
		#it.run = True
		#mkff(ff_err_fn) # for future use to read stderr
		#it.std_watch_err = oo(ff_err_fn, RdO|nBlk)
		#from thread import start_new_thread as nt
		#nt(it.ptyReadErr, ())


	#def ptyReadErr(it):
		#while it.run:
			#data = it.std_watch_err.read()
			#if data:
				#_dbg("Read stderr:\n%s\n" % repr(data))
			#slp(.5)
		#it.std_watch_err.close()

	def ptyDisconnect(it):
		#it.run = False
		it.kill()
		from gobject import source_remove as unWatch
		unWatch(it.watchID)
		it.fd.close()
		from os import remove as rm
		#rm(it.fifo_err_fn)
		#rm(it.fifo_in_fn)

	from subprocess import PIPE # must be there, because its needed by deafault stdin
	def runInVT(it, cmd, envm=None, stdin=PIPE):
		from subprocess import Popen as ppn, STDOUT
		from shlex import split as shs
		from os import setsid
		from psutil import Process as pss
		if envm is None:
			from os import environ as env
			envm = env.copy()
		# drop run if busy by previous task
		if type(it.proc) is ppn and(it.proc.poll()== None):
			return False
		it.proc = ppn(shs(cmd),
			env=envm,
			#stdin=it.fifo_in_fn,
			stdin=stdin,
			stdout=it.pty_child_fd,
			stderr=STDOUT, preexec_fn=setsid)
		it.proc.children = None
		try:
			p = pss(it.proc.pid)
			it.proc.children = p.get_children(recursive=True)
		except:
			pass
		#it.std_reply = open(it.fifo_in_fn, 'wb')
		while it.proc.poll()==None: # poll()==None means still running
			slp(.5)
		#it.std_reply.close()
		it.proc = None
		return True

	def kill(it):
		if not(it.proc is None):
			it.proc.terminate()
