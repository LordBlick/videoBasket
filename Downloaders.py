#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
# -*- tabstop: 4 -*-

'''
 This program source code file is part of videoBasket, a video download GUI
 application.
 
 Copyright  © 2015 by LordBlick (at) gmail.com
 
 This program is free software; you can redistribute mn and/or
 modify mn under the terms of the GNU General Public License
 as published by the Free Software Foundation; either version 2
 of the License, or (at your option) any later version.
 
 This program is distributed in the hope that mn will be useful,
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

from urllib2 import urlopen, URLError, HTTPError
from urlparse import parse_qs
from time import time as t_s
from os import path as ph
from sys import stdout as sto

from clIniFile import _p, hh, sto

dbg = True

def _dbg(_str):
	if dbg: sto.write(hh(str(_str)))

class YoutubeDL:
	def __init__(it, logger=None, dst_dn=None):
		it.iddle = True
		it.downloading = False
		it.start_time = t_s()
		it.size = None
		it.vidid = ''
		it.logger = logger
		it.dst_dn = dst_dn
		it.lenght = it.done = 0

	def go(it, vidid, reslimit):
		if it.iddle==False:
			_dbg("Busy")
			return True # busy
		it.iddle = False
		it.done = 0
		it.vidid = vidid
		try:
			resp = urlopen("https://www.youtube.com/get_video_info?video_id=%s" % vidid)
		except HTTPError as e:
			it.logger("\nThe server couldn\'t fulfill the request.\n")
			it.logger("Error code: %s\n" % str(e.code))
		except URLError as e:
			it.logger("\nWe failed to reach a server.\n")
			it.logger("Reason: %s\n" % str(e.reason))
		else:
			data = resp.read()
			resp.close()
			info = parse_qs(data)
			if info.has_key('title') and info.has_key('url_encoded_fmt_stream_map'):
				it.title = info['title'][0]
				_dbg("Downloading %s\n" % it.title)
				dst_fn = "%s/%s-%s.mp4" % (it.dst_dn, it.title.replace('/', '_'), vidid)
				stream_map = info['url_encoded_fmt_stream_map'][0]
				for v_info in stream_map.split(','):
					item = parse_qs(v_info)
					tags = 'quality type url'.split()
					if not(False in map(lambda key: item.has_key(key), tags)):
						_dbg('\n'.join(map(lambda tag: item[tag][0], tags))+'\n')
						url = item['url'][0]
						try:
							h_url = urlopen(url)
						except HTTPError as e:
							it.logger("\nThe server couldn\'t fulfill the request.\n")
							it.logger("Error code: %s\n" % str(e.code))
						except URLError as e:
							it.logger("\nWe failed to reach a server.\n")
							it.logger("Reason: %s\n" % str(e.reason))
						else:
							_dbg("%s\n" % h_url.headers)
							lenght = int(h_url.headers['Content-Length'])
							if lenght:
								it.lenght = lenght
								it.start_time = t_s()
								it.route_fd(h_url, dst_fn)
								break
		it.iddle = True
		return False

	def route_fd(it, h_url, dst_fn):
		it.downloading = True
		fd = open(dst_fn, 'wb+')
		it.done = 0
		while it.done<it.lenght:
			buff = h_url.read(1024)
			if not(buff):
				break
			fd.write(buff)
			it.done += len(buff)
		h_url.close()
		fd.close()
		it.downloading = False
