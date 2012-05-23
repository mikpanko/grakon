# -*- coding:utf-8 -*-
import os.path

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

VK_APP_ID = 2798211

GOOGLE_ANALYTICS_ID = 'UA-28992589-1'

YA_METRIKA_ID = 12237667

YANDEX_MAPS_KEY = 'ADSyKU8BAAAAD-VBCwIA5ak5VGynqt5xp2tzedBMfAmF8-kAAAAAAAAAAAD_nM6wtAPq97uJHRvkF_aJL3gRVQ=='

ADMIN_EMAIL = 'admin@grakon.org' # emails from users and notifications should be delivered here

EMAILS = {
    'noreply': (u'Гракон', 'noreply@grakon.org'),
}

DISQUS_SHORTNAME = 'grakon2'
DISQUS_URL_PREFIX = 'http://grakon.org' # TODO: temporary
DISQUS_CATEGORIES = {
    'general': 1444561,
    'locations': 1444565,
    'officials': 1444566,
    'events': 1456479,
    'tasks': 1470945,
    'posts': 1471343,
}
