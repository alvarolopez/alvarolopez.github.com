#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Alvaro'
SITENAME = u'aloga'
SITEURL = 'http://alvarolopez.github.io'
SITESUBTITLE = ''

TIMEZONE = 'Europe/Madrid'

DEFAULT_LANG = u'en'
STATIC_PATHS = ['images', 'static']

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'
TRANSLATION_FEED_ATOM = None

LOCALE = "C"

# NOTE(aloga): not used
# Blogroll
#LINKS =  (('Pelican', 'http://getpelican.com/'),
#          ('Python.org', 'http://python.org/'),
#          ('Jinja2', 'http://jinja.pocoo.org/'),
#          ('You can modify those links in your config file', '#'),)
#
## Social widget
#SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

THEME = "themes/octoflat"


MENUITEMS = (
    ("Index", "/"),
    ("Blog Archives", "/archives.html"),
)


GITHUB_USER="alvarolopez"
DEFAULT_DATE_FORMAT = '%d %b %Y'
LINKEDIN_USER = 96341003
GOOGLE_ANALYTICS = "UA-317422-7"
