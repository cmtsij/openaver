#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
from lxml import etree
import posixpath

import sys
import os.path

import openaverbase
import thirdparty



if len(sys.argv) == 1:
    query="n0859"
else:
    query=sys.argv[1]

info = {}


cj = openaverbase.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

site_url = "http://my.tokyo-hot.com"
search = opener.open(site_url + "/product/?q=%s&x=0&y=0"%(query))
search_content = search.read()
tree = etree.HTML(search_content)
try:
    a = tree.xpath("//ul[@class='list slider cf']//a")[0]
except IndexError:
    print "Nothing found"
    exit(1)

ref = a.get('href')

info['referer'] = site_url + ref

home = opener.open(site_url + ref)
content = home.read()

tree = etree.HTML(content, etree.HTMLParser(encoding="utf-8"))



title = tree.xpath("//div[@class='contents']/h2")[0].text
info['title'] = title

nodes = tree.xpath("//dl[@class='info']/dt")
for node in nodes:
    try:
        name = openaverbase.join_all_text_of_childrens(node)
        value = openaverbase.join_all_text_of_childrens(node.getnext())
    except IndexError:
        continue

    #print "%s=%s"%(name,value)
    info[openaverbase.column_name2type(name)] = value

info['cover_url'] = []
info['cover_url'] += [tree.xpath("//div[@class='movie cf']//video")[0].get("poster")]
info['cover_url'] += [tree.xpath("//div[@class='movie cf']//li[@class='package']/a")[0].get("href")]

for key, value in info.iteritems():
    print "%s=%s" % (key, value)

