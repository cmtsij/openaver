#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
from lxml import etree
import posixpath

import sys
import os.path

import unicodedata

import openaverbase
import thirdparty


if len(sys.argv) == 1:
    query = "063011-738"
else:
    query = sys.argv[1]

info = {}

cj = openaverbase.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

site_url = "http://www.caribbeancom.com"

page = opener.open(site_url + "/moviepages/%s/" % (query))
page_content = page.read()
tree = etree.HTML(page_content, etree.HTMLParser(encoding="euc-jp"))

element = tree.xpath("//div[@class='video-detail']")[0]

info['title'] = openaverbase.join_all_text_of_childrens(element)

elements = tree.xpath("//div[@class='movie-info']//dt")

for e in elements:
    try:
        name = openaverbase.join_all_text_of_childrens(e)
        value = openaverbase.join_all_text_of_childrens(e.getnext())
    except IndexError:
        continue

    name = unicodedata.normalize('NFKC', unicode(name)).strip(u":")
    value = unicodedata.normalize('NFKC', unicode(value))

    #print "%s=%s"%(name,value)
    info[openaverbase.column_name2type(name)] = value

info['part_number'] = query

info['referer'] = page.url

info['image_url'] = []
info['image_url'] += ["www.caribbeancom.com/moviepages/%s/images/l_l.jpg" % (query)]


elements = tree.xpath("//div[@class='detail-content detail-content-gallery-old nodisplay']//td/a")
info['image_url'] += [ site_url+a.get('href').replace("/member","",1) for a in elements]


for url in  info['image_url']:
    #opennaver.image_download(opener,info['referer'],url)
    pass


for key, value in info.iteritems():
    print "%s=%s" % (key, value)



