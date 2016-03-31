# -*- coding: utf-8 -*-
import sys
sys.path.append('telebot')

import re
import search

def sorting(seq, idfun=None):
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result


def extrude():
    with open('telebot/web1913.txt') as dictionary:
        dicstring = dictionary.read()
        pat = re.compile(r'(?<=\r\n\r\n)[A-Z]+(?![a-z])(?=\r\n)')
        entries = sorting(re.findall(pat, dicstring))
        return entries

def separate(word):
    PATH = 'telebot/dictionary/' + word + '.txt'
    with open(PATH, mode='w') as f:
        article = search.wordsearch(word, 'telebot/web1913.txt').encode('utf-8')
        f.write(article)
