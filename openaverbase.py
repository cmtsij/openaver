#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cookielib
import thirdparty
import posixpath
import urllib2

import os

type_translate_table = dict(actress=[u"AV女優", u"出演者", u"出演"],
                            studio=[u"AVメーカー"],
                            label=[u"AVレーベル"],
                            category=[u"カテゴリ", u"カテゴリー"],
                            series=[u"シリーズ"],
                            director=[u"監督"],
                            release_date=[u"発売日", u"配信開始日", u"配信日"],
                            duration=[u"収録時間", u"再生時間"],
                            tag=[u"タグ"],
                            user_rating=[u"ユーザー評価"],
                            part_number=[u"品番"])


def join_all_text_of_childrens(node, sep=u" "):
    return sep.join([text.strip() for text in node.xpath(".//text()") if len(text.strip()) > 0])


def image_download(opener, referer_url, image_url):
    referer_url = thirdparty.url_fix(referer_url)
    image_url = thirdparty.url_fix(image_url)

    # save default headers
    old_headers = opener.addheaders

    #set referer
    opener.addheaders += [('Referer', referer_url)]
    try:
        image = opener.open(image_url)
    except:
        print "get fail: " + image_url
        return

    #download image
    image_name = posixpath.basename(image_url)
    print image_name
    with open(image_name, "w") as f:
        f.write(image.read())

    # restore default headers
    opener.addheaders = old_headers


class CookieJar(cookielib.LWPCookieJar):
    def __init__(self, filename="cookie.txt", delayload=None, policy=None):
        cookielib.LWPCookieJar.__init__(self, filename, delayload, policy)
        try:
            self.load()
        except IOError:
            # cookie is not exist
            pass

    def set_cookie(self, cookie):
        cookielib.LWPCookieJar.set_cookie(self, cookie)
        self.save()


class OpenAverBase:
    class ItemInfo(dict):
        def __missing__(self, k):
            print "missing item_info['{0}']".format(k)
            return ""

        def debug(self):
            for key, value in self.items():
                print u"{0}={1}".format(key, value)


    def __init__(self, cookie_filename=None):
        if cookie_filename:
            cj = CookieJar(cookie_filename)
        else:
            cj = CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        self.opener.default_header = [('User-agent', 'Mozilla/5.0')]

    def open(self, url, referer_url=None):
        self.opener.addheaders = self.opener.default_header
        if referer_url:
            self.opener.addheaders += [('Referer', referer_url)]
        respone = self.opener.open(thirdparty.url_fix(url))
        return respone

    def login(self):
        raise NotImplementedError

    def search(self, query):
        raise NotImplementedError

    def fetch_item(self, index=0):
        raise NotImplementedError

    def download_item(self, Index_or_ItemInfo=None, path=os.curdir):
        item_info = None
        if isinstance(Index_or_ItemInfo, int):
            item_info = self.items[Index_or_ItemInfo]['item_info']
        elif isinstance(Index_or_ItemInfo, self.ItemInfo):
            item_info = Index_or_ItemInfo
        else:
            print "Item is not exist/valid."
            return -1

        if len(item_info['cover_url']) > 0:
            image = self.open(item_info['cover_url'], item_info['referer'])
            filename = path + os.sep + item_info['part_number'] + ".jpg"
            with open(filename, "w") as f:
                f.write(image.read())


def column_name2type(name):
    for type, type_names in type_translate_table.iteritems():
        if name in type_names:
            return type
    else:
        return name


if __name__ == "__main__":
    pass


