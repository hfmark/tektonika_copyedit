# docx parsing for Tektonika

## dependencies:
- python 3.n (preferably 3.8+)
- numpy
- biblib

A conda environment is a nice way to set this up.

You will also need to have pandoc (pandoc.org/) installed for the initial conversion of the .docx file.


## general steps for the conversion process
- convert .docx article file to latex
    - pandoc file.docx -f docx -t latex --wrap=none -s -o file_pandoc.tex

- copy-paste bibliography from docx into anystyle.io (or run the anystyle gem locally if you're into that) and output as bibtex, save as a .bib file
    - [anystyle.io -> file_anystyle.bib]

- fix anystyle bibtex file year fields and keys, make a new .bib file
    - (set input filenames manually in the script)
    - fix_bibtex.py -> file_init.bib

- manually correct any non-ascii keys in bib file, if there are any
    - (these will be printed to stdout so we know they need to be fixed, usually for non-ascii characters)
    - (feels like there should be a way around this but I don't know it)

- parse the pandoc output tex file to a better tex format
    - (set the input filenames manually in the script)
    - parse_pandoc_file.py -> file_init.tex

- run bibtex and pdflatex, look at the output and figure out what needs fixing
    - pdflatex file_init.tex -> file_init.pdf
    - bibtex file_init.aux
    - pdflatex ''
    - pdflatex ''
    - (running at least twice gives inline references a chance to sort themselves out)

- manually link figure files at the right sizes, adjust placement of automated \includegraphics as needed
    - pandoc does not extract image files from word so they will need to be uploaded separately
- manually adjust for extra bits of inline citations (in red), in line citations for multiple papers by the same authors (hopefully in red), and year-only citations (in red)
- add extra hyphenation rules for words latex doesn't know if columns are overfull
- manually add authors, affilitations, short title, other header metadata with default placeholders
- look at junk file and manually reformat/place tables in text where they belong (because I do not understand longtable)


## TODO: 
- make sure catch for supplemental figures/tables works for in-text references
- figure out parsing for author metadata
- figure out longtable/table parsing?
- parse extra bits of citations, like 'e.g.,' wherever possible
- more user-friendly startup (ie input filenames, rather than editing scripts)
    - related: complete workflow that runs all scripts in sequence automatically
    - and maybe make this all install as a package?

