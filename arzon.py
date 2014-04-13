#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cookielib, urllib2
from lxml import etree
import posixpath

import sys


if len(sys.argv) == 1:
    query="xv992"
else:
    query=sys.argv[1]

cj = cookielib.FileCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

arzon = "http://www.arzon.jp"
home = opener.open(arzon + "/itemlist.html?t=&m=all&s=&q="+query)

content = home.read()


tree = etree.HTML(content)
a = tree.xpath("//td[@class='yes']/a")[0]
url = a.get('href')

home = opener.open(arzon + url)
content = home.read()

tree = etree.HTML(content)
try:
	a = tree.xpath(u"(//dt)[1]/a")[0]
except IndexError:
	print "Nothing found"
	exit(0)
	
url = a.get('href')

home = opener.open(arzon + url)
content = home.read()

tree = etree.HTML(content)

info = {}

# title
title = tree.xpath("//div[@class='detail_title']/h1")[0].text
info['title'] = title
print info['title']

# cover_url
cover_url = tree.xpath("//table[@class='item_detail']//a[@title='%s']" % (title))[0].get('href')
info['cover_url'] = cover_url
print info['cover_url']

opener.addheaders += [('Referer', arzon + url)]
print opener.addheaders
jpg = opener.open(info['cover_url'])

jpg_name = posixpath.basename(info['cover_url'])
with open(jpg_name, "w") as f:
    f.write(jpg.read())


#infos=tree.xpath("//td[@class='caption']/table/tr")
trs = tree.xpath("//td[@class='caption']/table/tr")

key_trans_table = {
    #key, keynames
    "actress": [u"AV女優"],
    "studio": [u"AVメーカー"],
    "label": [u"AVレーベル"],
    "series": [u"シリーズ"],
    "director": [u"監督"],
    "release_date": [u"発売日"],
    "duration": [u"収録時間"],
    "part_number": [u"品番"]};

for tr in trs:
    try:
        name = tr.getchildren()[0].text
        value = tr.getchildren()[1]
    except IndexError:
        continue

    if len(value) > 0:
        value = value.getchildren()[0]
    value = value.text

    if not isinstance(name, unicode):
        continue
    if not isinstance(value, unicode):
        continue

    name = name.strip().strip(u":：")
    value = value.strip()

    for key, keynames in key_trans_table.iteritems():
        if name in keynames:
            info[key] = value

for key, value in info.iteritems():
    print "%s=%s" % (key, value)
