#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Alvaro Lopez'
SITENAME = u'aloga'
SITEURL = 'http://alvarolopez.github.io'
SITESUBTITLE = ''

TIMEZONE = 'Europe/Madrid'

DEFAULT_LANG = u'en'
STATIC_PATHS = ['images', 'static']

EXTRA_PATH_METADATA = {'static/keybase.txt': {'path': 'keybase.txt'},}

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
TRANSLATION_FEED_ATOM = None

ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'
CATEGORY_FEED_ATOM = ''
CATEGORY_SAVE_AS = ''
CATEGORIES_SAVE_AS = ''
TAG_SAVE_AS = ''
TAGS_SAVE_AS = ''
AUTHORS_SAVE_AS = ''
AUTHOR_SAVE_AS = ''
DISPLAY_CATEGORIES_ON_MENU = False

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

DEFAULT_PAGINATION = 0

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

THEME = "themes/getback"

MENUITEMS = (
    ("Publications", "/publications.html"),
    ("Notes (not a blog)", "/notes.html"),
)

INDEX_SAVE_AS = 'notes.html'

PLUGIN_PATHS = ["plugins"]
PLUGINS = ["pelican_bibtex"]
DIRECT_TEMPLATES = ['index', 'publications']
#DIRECT_TEMPLATES = ["publications"]

PUBLICATIONS_SRC = 'content/pubs.bib'

RESEARCHGATE_USER="Alvaro_Lopez-Garcia"
KEYBASE_USER="aloga"
TWITTER_USERNAME="alvaretas"
GITHUB_USER="alvarolopez"
DEFAULT_DATE_FORMAT = '%d %b %Y'
LINKEDIN_USER = "lopezgarciaalvaro"
ORCID = "0000-0002-0013-4602"
#GOOGLE_ANALYTICS = "UA-317422-7"
#DISQUS_SITENAME = "aloga"
