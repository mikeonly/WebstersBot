# -*- coding: utf-8 -*-

# This function splits the input text into the chunks with the
# given maximum length tolerating the unity of lines and paragraphs.


def split(text, m):
    chunks = []
    while len(text) > m:
        partition = text[:m].rpartition('\n\n')
        if not partition[1]:
            partition = text[:m].rpartition('\n')
        chunks.append(partition[0])
        text = partition[2] + text[m:]
    else:
        chunks.append(text)
        return chunks
