#!/usr/bin/python2
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
# -*- tabstop: 4 -*-

'''
 This program source code file is shared library for easiest configuration files use.
 
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
_p = lambda _str, tag=None: sto.write(hh(str(_str)))

dbg = False

def _dbg(_str):
	if dbg: sto.write(str(_str))

class xlist(list):
	def clear(it):
		l = it.__len__()
		if not(l):
			return
		elif l==1:
			it.pop()
			return
		it.__delslice__(0, l)

	def replace(it, iterable):
		it.clear()
		it.extend(iterable)

	copy = lambda it: xlist((lst_el.copy() if hasattr(lst_el, 'copy') else lst_el.__class__(lst_el) for lst_el in it))


class Section(xlist):
	def __init__(it):
		xlist.__init__(it)
		it.name = ''

	def load(it, lines):
		head = lines[0]
		if not(head and((head[0], head[-1])==('[', ']'))):
			return None
		it.name = head[1:-1]
		idx = 1
		ln_max = len(lines)
		while True:
			try: line = lines[idx]
			except IndexError:
				_p("Bad index:%i in Section:%s \n" % (idx, it.name))
				return idx-1
			if line=='':
				idx += 1
			elif (line[0], line[-1])==('[', ']') or(idx==ln_max):
				return idx
			elif '=' in line:
				key, value = line.split('=', 1)
				it[key.strip()] = value.lstrip()
				idx += 1
			elif line.strip().startswith(';'): # comment
				it.append( (None, line) )
				idx += 1
				if idx==ln_max:
					return idx # end of file
			else:
				_p("Unrecognized line[%i]:'%s' in Section:%s \n" % (idx, line, it.name))
				idx += 1
			if idx==ln_max:
				return idx # end of file

	def get_place(it, key):
		names = it.keys()
		if key in names:
			return names.index(key)
		return None

	def get_commented_place(it, key):
		names = map(lambda (key, value): key.lstrip(';'), it)
		if key in names:
			return names.index(key)
		return None

	def __getitem__(it, key):
		if type(key) is int:
			return xlist.__getitem__(it, key)
		elif it.has_key(key):
			return xlist.__getitem__(it, it.get_place(key))[1]
		else:
			return None

	get = __getitem__

	def __setitem__(it, key, value):
		if type(key) is int:
			xlist.__setitem__(it, key, value)
			return
		else:
			idx = it.get_place(key)
			if idx is not None:
				it[idx] = key, value
				return
			idx = it.get_commented_place(key)
			if idx is not None:
				it[idx] = key, value
				return
			else:
				it.append( (key, value) )

	dump_name = lambda it: "%s\n" % it.name
	has_key = lambda it, key: key in it.keys()
	items = lambda it: it.copy()
	keys = lambda it: xlist(map(lambda (key, value): key, it))
	values = lambda it: xlist(map(lambda (key, value): value, it))

	def place(it, name, value, index=None):
		if type(index) is int and(index<len(it)):
			old_idx = it.get_place(name)
			if old_idx is not None:
				cut_section = it.pop(old_idx)
				if index<len(it):
					it.insert(index, cut_section) # Nevermind value, it will be replaced at the end
		it[name] = value

	def remove(it, name):
		idx = it.get_place(name)
		if idx is None:
			return
		it.pop(idx)

	def deactivate(it, key):
		if type(key) is int:
			if key>=len(it):
				raise IndexError( "index '%i' out of range'0 - %i'" % (key, len(it)-1))
			key = it[key][0]
		idx = it.get_place(key)
		if idx is None:
			return
		it[idx] = ';'+key, it[key]

	def write_out(it):
		out = "[%s]\n" % it.name
		for _set in it:
			if _set[1]:
				out += '='.join(_set)+'\n'
		return out+'\n'

	def write_out_old_cfg(it):
		out = ''
		for _set in it:
			out += ':'.join((it.name.replace('Main', 'mn').replace('UI', 'ui'),)+_set)+'\n'
		return out

class IniSections(xlist):
	def __init__(it):
		xlist.__init__(it)
		it.filename = ''
		from sys import _current_frames as _cf
		callingFilename = _cf().values()[0].f_back.f_code.co_filename
		it.callDir = ph.dirname(ph.realpath(callingFilename))

	@classmethod
	def load_new(cls, file_name, dbg=False):
		instance = cls()
		instance.load(file_name, dbg=dbg)
		return instance

	def __getitem__(it, key):
		if type(key) is int:
			return xlist.__getitem__(it, key)
		elif it.has_key(key):
			return xlist.__getitem__(it, it.get_place(key))
		else:
			new_section = Section()
			new_section.name = key
			it.append(new_section)
			return it[key]

	get_section = __getitem__

	def __setitem__(it, key, value):
		if type(key) is int:
			xlist.__setitem__(it, key, value)
		elif it.has_key(key):
			xlist.__setitem__(it, it.get_place(key), value)
		return

	keys = lambda it: xlist(map(lambda section: section.name, it))
	has_key = lambda it, key: key in it.keys()
	get_sections_names = lambda it: tuple(it.keys())
	dump_sections_names = lambda it: ', '.join(it.get_sections_names())+'\n'

	def get_place(it, section_name):
		section_names = it.keys()
		if section_name in section_names:
			return section_names.index(section_name)
		return None

	def section_place(it, section_name, index=None):
		idx = it.get_place(section_name)
		if idx is None:
			new_section = Section()
			new_section.name = section_name
			if type(index) is int and(index<len(it)):
				it.insert(index, new_section)
			else:
				it.append(new_section)
			return
		elif type(index) is int and(index<len(it)):
			cut_section = it.pop(idx)
			if index<len(it):
				it.insert(index, cut_section)
			else:
				it.append(cut_section)

	def section_delete(it, section_name):
		idx = it.get_place(section_name)
		if idx is None:
			return
		it.pop(idx)

	def load(it, fn, dbg=False):
		it.filename = fn
		fd = open(fn, 'r')
		lines = fd.read().splitlines()
		if dbg:
			it.lines = lines
		fd.close()
		ln_cnt = ln_pos = 0
		ln_max = len(lines)
		if not(ln_max):
			_p("File '%s' is empty…\n" % fn)
			return
		bNew = True
		while ln_pos<=ln_max and(lines[ln_pos:]):
			if bNew: new_section = Section()
			read_cnt = new_section.load(lines[ln_pos:])
			if read_cnt is None:
				if dbg:
					_p("Skip line:%i of %i\n" % (ln_pos+1, ln_max))
				ln_pos += 1
				bNew = False
				continue
			elif type(read_cnt) is int and(ln_pos<ln_max):
				it.append(new_section)
				ln_pos += read_cnt
				if dbg:
					_p("Last Section '%s' line No: %i\n" % (new_section.name, ln_pos))
				if ln_pos>=ln_max:
					return
				bNew = True

	def load_old_cfg(it, fn):
		fd = open(fn, 'r')
		lines = fd.read().splitlines()
		fd.close()
		for inputLine in lines:
			if inputLine and ':' in inputLine:
				splitCnt = inputLine.count(':')
				if '://' in inputLine:
					splitCnt -= 1
				if not(splitCnt):
					continue
				_dbg("Loading old config line:\n%s\nsplitCnt:%i\n" % (inputLine, splitCnt))
				split_line = inputLine.split(':', splitCnt)
				if len(split_line)==3:
					section_name, name, value = split_line
				elif len(split_line)==2:
					section_name = 'mn'
					name, value = split_line
				section_name = section_name.replace('mn', 'Main').replace('ui', 'UI')
				it[section_name][name] = value
				if not(it[section_name].name):
					it[section_name].name = section_name
					_p("Supplemented section name: '%s'\n" % it[section_name].name)

	def dump(it):
		out = it.write_out().splitlines()
		fmt_str = "%%%ii: %%s\n" % len("%i" % len(out))
		for n, l in enumerate(out):
			_p(fmt_str % (n+1, l))

	def write_out(it):
		out = ''
		for section in it:
			out += section.write_out()
		return out

	def write_out_old_cfg(it):
		out = ''
		for section in it:
			out += section.write_out_old_cfg()
		return out

	def store(it):
		fd = open(it.filename, 'w')
		fd.write(it.write_out())
		fd.close()
		_p("Written config:%s...\n" %it.filename)

	def store_old_cfg(it, fn):
		fd = open(fn, 'w')
		fd.write(it.write_out_old_cfg())
		fd.close()
		_p("Written config:%s...\n" % fn)

