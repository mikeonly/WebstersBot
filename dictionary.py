# -*- coding: utf-8 -*-
from struct import unpack
import os, gzip, re


class Dic(object):
    def __init__(self, directory):
        self.path = self.pathize(directory, 'dz')
        self.index = Idx(directory)

    def __getitem__(self, word, rawy=False):

        if type(word) == str:
            word = word.decode('utf-8')

        def rawize(word):
            bounds = self.index.dict[word]
            with gzip.open(self.path, mode='rb') as f:
                f.seek(bounds[0])
                raw = f.read(bounds[1]).decode('utf-8')
            return raw

        def articlize(raw):  # Produces the finest article out of raw
            # Subs for subtitutions dictionary: {'old string': 'new string'}
            subs = {
                    u'Note:': u'☞',
                    u'\[root\]': u'√',
                    u' \. \. \.': u'…',
                    u'``': u'“',
                    u'\'\'': u'”',
                    u'\[ae\]': u'æ',
                    u'\[\"o\]': u'ö',
                    u'--': u'—',
                    u' {2,64}': u' ',  # Re handles superfluous spaces
                    u'(?<![xvi].)(?<=[].)])\n(?=\d{1,2}.)|(?<=[].)])\n(?=[A-Z])': u'\n\n',
                    u'(—[A-Z][a-z0-9 \.]*.) ?(\n)?(\([a-z]\))': u'\\1\\n\\n\\3'  # Re handles 
                    # missing \n between citations and ([a-z]).
                    }
            article = ''
            lines = raw.splitlines()

            for n, line in enumerate(lines[:-1]):
                if lines[n+1] == '':
                    nword = ' '
                else:
                    nword = str(lines[n+1].strip().split(' ')[0]) + ' '*2

                if len(line + ' ' + nword) > 66 and (not (re.match('\d\d?\. ', lines[n+1]) and not line.endswith(u',')) or lines[n+1].startswith(u' '*50)):
                    # Almost unreadable handling of some special cases together with more
                    # general rules of line breaking; more specifically it combines lines 
                    # as required, treating correctly separetaed chapter numbers from ci-
                    # tations
                    article += line.strip() + ' '
                else:
                    article += line.strip() + '\n'
            else:
                article += lines[-1].strip()

            for key in subs:
                article = re.sub(key, subs[key], article)

            return article

        try:
            raw = rawize(word)  # Returns a raw text
        except KeyError:
            return None

        if rawy:
            return raw
        else:
            return articlize(raw)  # Returns a formated article

    def pathize(self, path, ext):  # Finds pathes to needed files by their extensions
        if not os.path.exists(path):
            raise Exception('Path “%s” does not exists' % path)
        else:
            for f in os.listdir(path):
                if f.endswith('.' + ext): return os.path.join(path, f)
            raise Exception('No file with an extension %s can be found in %s.' % ('.' + ext, path))


class Idx(Dic):
    def __init__(self, directory, offset=4):

        self.path = self.pathize(directory, 'idx')
        self.offset = offset

        self.dict = {}  # Dictionary: {u'word': [offset, size]}
        self.__fillize()

    def __bytize(self, stream):
        array = stream.read(self.offset)  # Reads self.offset bytes from the stream
        integer = unpack('>L', array)[0]  # From old to young byte to L for unsigned long
        return integer

    def __fillize(self):
        word = ''
        with open(self.path, 'rb') as stream:
            while True:
                byte = stream.read(1)  # Read 1 byte
                if not byte: break
                if byte != b'\0':  # If not EOL then add to word
                    word += byte.decode('utf-8')
                else:
                    wordoffset = self.__bytize(stream)
                    wordsize = self.__bytize(stream)
                    self.dict[word] = [wordoffset, wordsize]
                    word = ''