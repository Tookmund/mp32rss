#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from email.utils import format_datetime
from email.utils import formatdate
from urllib.parse import quote

from lxml.etree import Element
from lxml.etree import SubElement
from lxml.etree import ElementTree
from lxml.builder import ElementMaker

from mutagen.mp3 import EasyMP3 as MP3

NS = {
    "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "content": "http://purl.org/rss/1.0/modules/content/"
}

def staticelem(parent, name, text):
    elem = SubElement(parent, name)
    elem.text = text
    return elem

def staticnselem(parent, ns, name, text):
    return staticelem(parent, nsname(ns, name), text)

def promptelem(parent, name, prompt):
    return staticelem(parent, name, input(prompt+": "))

def nsname(ns, name):
    return "{{{0}}}{1}".format(NS[ns], name)

def promptnselem(parent, ns, name, prompt):
    return promptelem(parent, nsname(ns, name), prompt)

RSSPATH = input("rss.xml HTTP directory: ")
rss = Element("rss", nsmap=NS, version="2.0")
channel = SubElement(rss, "channel")
title = promptelem(channel, "title", "Program Title")
description = promptelem(channel, "description",
        "Program Description")
link = promptelem(channel, "link", "Link to Program")
language = staticelem(channel, "language", "en-us")
docs = staticelem(channel, "docs",
        "https://help.apple.com/itc/podcasts_connect/#/itcbaf351599")
itunesauthor = promptnselem(channel, "itunes", "author",
        "Program Author")
itunessubtitle = promptnselem(channel, "itunes", "subtitle",
        "Program Subtitle")
owner = SubElement(channel, nsname("itunes", "owner"))
ownername = promptnselem(owner, "itunes", "name", "Owner Name")
owneremail = promptnselem(owner, "itunes", "email", "Owner Email")

explicit = promptnselem(channel, "itunes", "explicit",
        "Explicit (Will apply to all episodes) (Yes/No)")
image = SubElement(channel, nsname("itunes", "image"))
image.attrib["href"] = RSSPATH+"/"+input("Image relative path: ")
category = SubElement(channel, nsname("itunes", "category"))
category.attrib["text"] = input("iTunes Category: ")

for DIR in sys.argv:
    episodenum = 1
    prevdate = None
    for f in sorted(os.scandir(DIR), key=lambda x: x.name):
        if not f.name.endswith(".mp3"):
            continue
        name = f.name[:-4]
        item = SubElement(channel, "item")
        fmp3 = MP3(DIR+"/"+f.name)
        ftitle = fmp3["title"][0] if "title" in fmp3 else name
        itemtitle = staticelem(item, "title", ftitle)
        itemnum = staticnselem(item, "itunes", "episode", str(episodenum))
        episodenum += 1
        description = staticelem(item, "description", name)
        url=RSSPATH+"/"+quote(f.name)
        stat = f.stat()
        size = stat.st_size
        itemdate = stat.st_ctime
        if prevdate is not None and prevdate >= itemdate:
            itemdate = prevdate+5
        prevdate = itemdate
        enclosure = SubElement(item, "enclosure",
                length=str(size),
                type="audio/mpeg",
                url=url)
        guid = staticelem(item, "guid", url)
        pubDate = staticelem(item, "pubDate", formatdate(itemdate))
        mp3duration = int(fmp3.info.length)
        duration = staticnselem(item, "itunes", "duration", str(mp3duration))
        itemexplicit = staticnselem(item, "itunes", "explicit", explicit.text)

    et = ElementTree(rss)
    et.write(DIR+"/rss.xml", pretty_print=True, xml_declaration=True,
            encoding="UTF-8")
