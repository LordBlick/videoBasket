---
title: videoBasket
description: Small, video download GUI, written in Python/gtk+2
author: LordBlick
tags: video, download, youtube, python, gtk
created:  2015.07.15
modified: 2015.07.15

---

videoBasket
=======
## Introduction

videoBasket is a program for easier use youtube-dl and if the address is clearly simple client lftp is used, downloading multipartly.


## Running initially testing script.
From command line in dir with script:
> python basketVideo

Unix based OS user can set execute privileges to execute as any other shell script:
> chmod +x basketVideo

> ./basketVideo

To run it it's nessesary to install:
- [Python interpreter] in version 2 (On today newests is 2.7.10). Don't miss with version 3 (On today newests is 3.4.3).
- [lftp] - a powerful ftp/http/https client.
- [YouTube Downloader] powerfull comand line videos downloader. Has own [Github repository] and [Github homepage]…
- [GTK Libraries].
[Python interpreter]: https://www.python.org/downloads/
[lftp]: http://lftp.yar.ru/
[YouTube Downloader]: http://youtube-dl.org/downloads/latest/
[Github repository]: https://github.com/rg3/youtube-dl
 [Github homepage]: http://rg3.github.io/youtube-dl/
[GTK Libraries]: http://www.gtk.org/download/

TO DO:
- youtube-dl classes integration.
- destination download dir configurable.
- separate configuration dialog.
- free lftp depedency (internal multidownload routine with multithreading Cython)
- make possible to pack std pypi package
