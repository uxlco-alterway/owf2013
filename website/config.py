# coding=utf-8

#
# Technical configuration
#
DEBUG = True
ASSETS_DEBUG = DEBUG
SECRET_KEY = "joouqxounbuttuyctuyctuvycrwvtyuew"
# FIXME later
#ASSETS_DEBUG = True
FLATPAGES_AUTO_RELOAD = True
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = '../pages'
SQLALCHEMY_DATABASE_URI = "sqlite:///../data/abilian.db"
SQLALCHEMY_ECHO = "True"


#
# Application configuration
#
SITE_URL = 'http://www.openworldforum.org/'
SITE_TITLE = 'Open World Forum 2013'
SITE_DESCRIPTION = "TODO"

ABSTRACT_LENGTH = 350

FEED_MAX_LINKS = 25
SECTION_MAX_LINKS = 12

ALLOWED_LANGS = ['fr', 'en']

MAIN_MENU = {'fr': [('', u'Accueil'),
                    ('a-propos/', u'A propos'),
                    ('speakers/', u"Intervenants"),
                    ('programme/', u'Programme'),
                    ('lieu/', u'Lieu'),
                    ('news/', u'Actualités'),
                    ('registration/', u'Inscription', 'menu-registration')],
             'en': [('', u'Home'),
                    ('about/', u'About'),
                    ('speakers/', u"Speakers"),
                    ('schedule/', u'Schedule'),
                    ('venue/', u'Venue'),
                    ('news/', u'News'),
                    ('registration/', u'Registration', 'menu-registration')]}

IMAGE_SIZES = {
    'small': (300, 180),
    'large': (620, 348),
}
