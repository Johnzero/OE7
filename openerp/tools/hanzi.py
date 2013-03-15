# -*- coding: UTF-8 -*-


import re
from maps import *

western_maps = [ latin_map, latin_symbol_map, greek_map, turkish_map, \
                russian_map, ukrainian_map, czech_map, polish_map, latvian_map ]

pinyin_map = dict([(ord(k), v[0])for k, v in pinyin_map.items()])

for i in xrange(len(western_maps)):
    western_maps[i] = dict([(ord(k), v) for k, v in western_maps[i].items()])

stop_words = [u'a', u'an', u'as', u'at', u'before', u'but', u'by', u'for',
              u'from', u'is', u'in', u'into', u'like', u'of', u'off', u'on',
              u'onto', u'per', u'since', u'than', u'the', u'this', u'that',
              u'to', u'up', u'via', u'with']

reserved_words = [u'blog', u'edit', u'delete', u'new', u'popular', u'wiki']


def urlify(urlstring, default='default', max_length=50,
           stop_words=stop_words, reserved_words=reserved_words):
    """
    Urlify is a simple function that generates the slug of a urlstring
    automatically using python.

    Urlify has support for language maps. Language maps work by replacing
    kanji with pinyin and characters in other western languages with similar
    ones in English. The replacement is done in the generated slug only.
    For example, a urlstring "派森是好物" will create a slug of 
    "pai-sen-shi-hao-wu" and a urlstring "Это простое испытание название" 
    will create a slug of "eto-prostoe-ispytanie-nazvanie".

    There is support for PinYin, Latin, Greek, Turkish, Russian, Ukranian, 
    Czech and Polish maps. These maps are acquired from pyzh project
    <http://code.google.com/p/pyzh/> and Django project
    <http://www.djangoproject.com/>. So these maps are not under the tems of 
    GPLv3 license.
        
    Urlify also has support for stop words and reserved words.

    """

    slug = ''

    re_alnum = re.compile(r'[\w\s\-]+')
    re_stop = re.compile('|'.join([r'\b%s\b' % word for word in stop_words]))
    re_reserved = re.compile('|'.join([r'\b%s\b' % word for word in reserved_words]))
    re_space = re.compile(r'[\s_\-]+')

    for char in urlstring:
        if len(slug) >= max_length:
            break
        if re_alnum.match(char):
            slug += char
            continue
        char_ord = ord(char)
        if char_ord in pinyin_map:
            slug += u' ' + pinyin_map[char_ord] + u' '
            continue
        for dict in western_maps:
            if char_ord in dict:
                slug += dict[char_ord]
                break

    slug = re_stop.sub(u'', slug.lower())
    slug = re_space.sub(u'-', slug.strip())
    if slug is '' or re_reserved.match(slug):
        slug = default

    return slug

def get_initial(name):
    l_list = [n.upper()[0] for n in urlify(name).split('-')]
    return ''.join(l_list)
    
    