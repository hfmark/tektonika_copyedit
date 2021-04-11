import numpy as np
import biblib.bib as bbl
import os, sys

in_bib = 'docx_anystyle.bib'  # initial .bib from anystyle
out_bib = 'docx_init.bib'   # place to write corrected bib entries

parser = bbl.Parser()  # parser for bibtex

parsed = parser.parse(open(in_bib,'r'))  # parse the input file with biblib

# get entries
bib_OD = parsed.get_entries()  # returns collections.OrderedDict

# open outfile for writing
fout = open(out_bib,'w')  # will overwrite if file exists

newkey_list = []  # for tracking keys used in case we need 'a' and 'b'
# loop entry keys
for key in bib_OD:
    entry = bib_OD[key]
    # for each, make 'year' and fill with year from 'date'
    if 'date' in entry.keys():
        if len(entry['date']) == 4: # assume this means it's a year, which is probably true
            entry['year'] = entry['date']
        else: # possibly 'month year'?
            entry['year'] = entry['date'].split(' ')[1]

    # for each, reformat key to be what we'd look for in inline citations
    # first, count authors: if >2, key is firstauthorEAYYYY, if 2 or less is author(author)YYYY
    if len(entry.authors()) > 2:
        newkey = entry.authors()[0].last + 'EA' + entry['year']
    elif len(entry.authors()) == 2:
        newkey = entry.authors()[0].last + entry.authors()[1].last + entry['year']
    elif len(entry.authors()) == 1:
        newkey = entry.authors()[0].last + entry['year']
    newkey = newkey.replace(" ","")  # get rid of spaces if there are any (like van Keken or something)
    nextletter = 'a'
    if newkey + nextletter in newkey_list:  # already have 'a', try the next letter
        thisauthor = [e for e in newkey_list if e.startswith(newkey)]
        alphabet = [e[-1] for e in thisauthor]
        nextletter = chr(ord(alphabet[-1]) + 1)
    newkey= newkey + nextletter  # this is what we'll use for bibtex

    if len(newkey) != len(newkey.encode()):
        print('key ascii error: ',newkey)  # non-ascii is fine within citations, just not in keys
        newkey2 = input('enter a corrected key to use for this entry: ') or newkey
        if newkey2 == newkey:
            print('not correcting key; this may cause problems later')
        newkey = newkey2

    newkey_list.append(newkey)
    entry.key = newkey

    # write entry to new bib file
    fout.write(entry.to_bib())
    fout.write('\n')

fout.close()
