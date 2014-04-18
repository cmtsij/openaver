#!/usr/bin/env python
# -*- coding: utf-8 -*-

import openaverbase

from lxml import etree
import sys
import unicodedata
import urlparse


class Arzon(openaverbase.OpenAverBase):
    site = "http://www.arzon.jp"

    def login(self):
        self.open(self.site)

        # login first to get cookie
        page = self.open(self.site)
        tree = etree.HTML(page.read())
        e_list = tree.xpath("//td[@class='yes']/a")
        try:
            a = e_list[0]
            confirm_url = a.get('href')
            self.open(self.site + confirm_url)
        except IndexError:
            pass  # logged-in and got cookie already.

    def search(self, query):
        self.items = []

        print u"searching: %s"%(query)
        search_url = self.site + "/itemlist.html?list=list&t=&m=all&s=&q=" + query
        print search_url
        search_page = self.open(search_url,self.site)
        tree = etree.HTML(search_page.read())
        e_list = tree.xpath("//table[@class='listitem']/tr")
        print "result count: %d" % (len(e_list))
        for e in e_list:
            try:
                a = e.xpath(".//a[@title]")[0]
                a_actress = e.xpath("(.//div[@class='data']/ul)[1]//a")
            except IndexError:
                continue
            href = a.get('href')
            title = a.get('title')
            actress = u" ".join([a.text for a in a_actress])

            if len(actress.split(" ")) == 1:
                self.items += [dict(href=href, title=title, actress=actress)]
                #print "%s|%s|%s" % (href, actress, title)

        for i in xrange(len(self.items)):
            print u"[{i}]|{item[actress]}|{item[title]}".format(i=i, item=self.items[i])

        return len(self.items)

    def search_actress(self, query):
        self.items = []
        page = 1
        max_page = 1

        print u"searching: %s"%(query)
        while page <= max_page:
            search_url = self.site + u"/itemlist.html?list=list&sort=-saledate&from={page}&txtcst={query}".format(page=page, query=query)
            page += 1
            search_page = self.open(search_url)
            search_content = search_page.read()
            with open("search.html","w") as f:
                f.write(search_content)
            tree = etree.HTML(search_content)

            # get max_page
            try:
                max_page = int(tree.xpath("(//table/tr/td/span/b)[2]")[0].text)
            except IndexError:
                pass

            e_list = tree.xpath("//table[@class='listitem']/tr")
            for e in e_list:
                href = e.xpath(".//a[@title]")[0].get('href')
                title = e.xpath(".//a[@title]")[0].get('title')
                actress = u" ".join(e.xpath("(.//div[@class='data']/ul)[1]//a/text()"))
                self.items += [dict(href=href, title=title, actress=actress)]
                #print "%s|%s|%s" % (href, actress, title)

        for i in xrange(len(self.items)):
            print u"[{i}]{title}".format(i=i, **self.items[i])
        return len(self.items)


    def fetch_item(self, index):
        item_info = self.ItemInfo()

        if index >= len(self.items):
            print "item[{0}] is not available.".format(index)
            sys.exit(1)

        info_url = self.site + self.items[index]['href']
        info_page = self.open(info_url)
        info_content = info_page.read()
        tree = etree.HTML(info_content)

        # referer
        item_info['referer'] = info_url

        # title
        title = tree.xpath("//div[@class='detail_title']/h1")[0].text
        item_info['title'] = title

        # cover_url
        try:
            cover_url = tree.xpath("//table[@class='item_detail']//a[@title]")[0].get('href')
            item_info['cover_url'] = urlparse.urljoin(self.site, cover_url)
        except IndexError:
            with open("info.html", "w") as f:
                f.write(page_content)

        #infos=tree.xpath("//td[@class='caption']/table/tr")
        trs = tree.xpath("//td[@class='caption']/table/tr")
        for tr in trs:
            try:
                name = openaverbase.join_all_text_of_childrens(tr[0])
                values = openaverbase.join_all_text_of_childrens(tr[1])
            except IndexError:
                continue
            column_name = unicodedata.normalize('NFKC', unicode(name)).strip(u":")
            column_values = unicodedata.normalize('NFKC', unicode(values))
            item_info[openaverbase.column_name2type(column_name)] = column_values

        # workaround to fix item_info[]
        item_info['part_number'] = item_info['part_number'].replace(u"廃盤", "").strip()
        item_info['release_date'] = item_info['release_date'].split()[0].replace("/", "-")
        self.items[index]['item_info'] = item_info
        return item_info


if __name__ == "__main__":
    query = u"小倉ゆず"  # just for debug
    index = 0  # just for debug
    if len(sys.argv) >= 2:
        query = sys.argv[1].decode('utf-8')
    if len(sys.argv) >= 3:
        index = int(sys.argv[2])

    oa = Arzon()
    oa.login()

    #num = oa.search_actress(query)
    num = oa.search_actress(query)
    print "num: %d"%(num)

    for i in xrange(num):
        item_info = oa.fetch_item(i)
        print item_info['part_number']
    exit(0)

    item_info = oa.fetch_item(index)
    item_info.debug()

