import biblib.bib as bbl
import tekpy.tektonika_temps as tt
import tekpy.utils as ut
import numpy as np
import os, sys


####
# run through a pandoc'd latex file line by line, correcting things it doesn't catch well
# in particular inline citations (so also read corresponding bibtex first)
# NOTE: this script assumes:
    # the input file used the tektonika docx template, and used it *properly* (esp. headers/styles)
    # equations were typeset using word's native equation thing
    # there are no more than 99 equations, figures, and tables, respectively, in the document
    # a bibtex file using the reference list has already been created
    # references/bibliography is the LAST SECTION of the document, nothing after it will be kept
    # Table and Figure captions start with the capitalized words 'Table' or 'Figure'
# TODO:
    # preambles/suffices to inline citations -> not currently parsed, should be? can they be?
    # author info in header? can it be parsed?
    # citations where there are multiple years in a row for the same authors don't work (yet)
    # also, citations that are just parenthetical years aren't parsed (but they are in red)
    # why are DOIs not included in {apalike} bibliography?
####

# set filenames and review status  TODO: set these filenames to get started
bibtex = 'docx_init.bib'
tex_in = 'docx_pandoc.tex'
tex_mid = 'docx_temp.tex'
tex_out = 'docx_init.tex'
junk_out = 'junk.tex'  # this is for table and figure info that can't be parsed automatically
review = False  # switch for draft watermark and line numbers

########################################################################
# setup:
# read bibtex, get list of keys for entries that we expect to find in the text
parser = bbl.Parser()
biblio = parser.parse(open(bibtex,'r'))
bibkeys = biblio.get_entries().keys()

# open pandoc file and output file
ftex_in = open(tex_in,'r')
ftex_out = open(tex_mid,'w')
fjunk = open(junk_out,'w')

# set up counters for figures, equations, and tables
nfig = 1; nequ = 1; ntab = 1
figcap = {}; tabcap = {}

special_section_names = ['acknowledgements','acknowledgments','data-availability','author-contributions']  # for sections that aren't numbered, lowercase and with spaces as -
skip_sections = ['references','bibliography']  # when we get to this header, skip to the end

########################################################################
# start at the beginning, deal with title and abstract
# skip header stuff in input file, find title
while True:
    line = ftex_in.readline()
    if line.startswith('\\begin{document}'):
        break

while True:
    line = ftex_in.readline()
    if line != '\n':
        break  # this is probably the title

# get the title text and feed it to header template/write header template to file
article_title = line
ftex_out = tt.set_up_header(ftex_out,article_title,review=review)


# TODO: maybe parse authors and affiliations?

# read some more lines, look for abstract heading
while True:
    line = ftex_in.readline()
    if line.startswith('\section{Abstract}'):
        break  # assumption line is 'Abstract' or '1 Abstract' or similar
               # (ie we assume pandoc hasn't figured out this is a heading)

# read lines cautiously, find the actual abstract text
abst = ""
while True:
    line = ftex_in.readline()
    if not line.startswith('\hypertarget'):
        abst = abst + line
    else:
        break

# deal with the second-language abstract  if there is one
if line.startswith('\hypertarget{second-language-abstract'):
    line = ftex_in.readline()  # skip over the section header here
    second_abst = ''
    while True:
        line = ftex_in.readline()
        if not line.startswith('\hypertarget'):  # until we hit the next section
            second_abst = second_abst + line
        else:
            break
    abst = abst + '\\begin{center} \\abstractnamefont Second-language abstract \end{center}\n\n\\normalfont \small \n' + second_abst

ftex_out = tt.add_abstract(ftex_out,abst)  # add abstract after header in output file
########################################################################
# go through the rest of the sections! and deal with citations, figures, and equations

goto_end = False
first_line = True  # abstract reading stopped at a section, so don't skip that
while not goto_end:
    if not first_line:  # if not, we already read the first hypertarget to get to the end of the abs.
        line = ftex_in.readline()
    else:
        first_line = False
    if line.startswith('\end{document}'): # this is the end, stop reading
        break

    if line.startswith('\hypertarget'):  # the next line will be a section
        lower_section = line.split('{')[1].split('}')[0]
        line = ftex_in.readline()  # actual section line
        stype = line.split('{')[0]
        if lower_section in special_section_names:
            sname = line.split('{')[1].split('}')[0]
            stype = stype + '*'
        elif lower_section in skip_sections:
            goto_end = True
        else:
            sname = ' '.join(line.split('{')[1].split('}')[0].split(' ')[1:])  # strip leading number
        if sname != '':
            ftex_out.write('%s{%s}\n' % (stype,sname))

    else:  # not a section header, so parse as a line and deal with citations or math or whatever
        if line.startswith('\('):  # possibly an equation
            print(line[:-1])
            iq = input('is this an equation? [y]/n') or 'y'
            if iq.lower() == 'y':
                # scrape off the \( and \) bits since we're putting this in an environment
                line = line.split('\)')[0].split('\(')[1]
                ftex_out.write('\\begin{equation}\n')
                ftex_out.write(line)
                ftex_out.write('\n')
                ftex_out.write('\label{eq%i}\n' % nequ)
                ftex_out.write('\end{equation}\n')
                nequ += 1
            else:
                print('ok, writing line plain, then')
                ftex_out.write(line)

        elif line.startswith('\\begin{'):  # some kind of environment?
            ftex_in, ftex_out, fjunk, nequ, nfig, ntab, itype = \
                    ut.parse_environment(line,ftex_in,ftex_out,fjunk,nequ,nfig,ntab)

        elif line.startswith('\includegraphics'):
            ftex_out.write('\\begin{figure}\n')
            ftex_out.write('\includegraphics[width = \columnwidth]{example-image}\n')
            ftex_out.write('\caption{placeholder caption}\n')
            ftex_out.write('\label{fig%i}\n' % nfig)
            ftex_out.write('\end{figure}\n')
            print('figure found; moving original line to junk file')
            fjunk.write('Figure %i\n' % nfig)
            fjunk.write(line)
            fjunk.write('\n')  # saving for later
            nfig += 1

        else:
            to_write = ''  # append pieces as you check them
            if '(' in line:  # check for parentheticals
                # find indices of open/close parens
                open_par = [pos for pos, char in enumerate(line) if char == '(']
                clse_par = [pos for pos, char in enumerate(line) if char == ')']
                if len(open_par) != len(clse_par):
                    print('mismatched parentheticals :(')
                    print(line)
                    sys.exit()

                for k in range(len(open_par)):  # loop parentheticals, see if they look like citations
                    if k == 0:  # add text before this parenthetical to the output string
                        to_write += line[:open_par[k]]
                    else:
                        to_write += line[clse_par[k-1]+1:open_par[k]]
                    paren = line[open_par[k]+1:clse_par[k]]  # text within parens
                    # signs of citation: contains et al., starts with e.g., formatted bit matches bib
                    # split into space-separated chunks, try to skip preambles, find first year
                    paren = paren.split(' ')

                    cite_text = '\citep{'

                    yr_inds = np.where([e[:4].isdigit() for e in paren])[0] + 1
                    yr_inds = np.append(0,yr_inds)
                    for l in range(len(yr_inds)-1):
                        # combine each set of pieces into a string, try to find in bib keys
                        cite_pieces = paren[yr_inds[l]:yr_inds[l+1]]
                        cite_pieces = [word.translate({ord(k): None for k in ['.',',','&','\\',';']}) \
                                        for word in cite_pieces]  # remove punctuation
                        if len(cite_pieces) == 1 and cite_pieces[0].isdigit():  # just a year:
                            cite_text = '\\textcolor{red}{%s' % cite_pieces[0]
                            break
                        et_ind = [e == 'et' for e in cite_pieces]  # look for et al
                        if sum(et_ind) > 0:  # if there is an et al, deal with it
                            et_ind = np.where(et_ind)[0][0]
                            cite_pieces[et_ind] = 'E'  # replace the et al with EA
                            cite_pieces[et_ind+1] = 'A'
                        and_ind = [e == 'and' for e in cite_pieces]  # look for 'and'
                        if sum(and_ind) > 0:
                            and_ind = np.where(and_ind)[0][0]
                            cite_pieces = np.delete(cite_pieces, and_ind)
                        test_cite = ''.join(cite_pieces)
                        # check if this citation matches any of the keys in the bibliography
                        if test_cite + 'a' not in bibkeys:
                            # possibly a preamble? try skipping a character at a time until it matches
                            for m in range(5,len(test_cite)):
                                if test_cite[-m:] + 'a' in bibkeys:
                                    preamble = tt.escape_latex(test_cite[:-m])
                                    test_cite = test_cite[-m:]
                                    cite_text = '\\textcolor{red}{'+preamble+ '}' + cite_text
                                    if l == 0:
                                        cite_text = cite_text + test_cite + 'a' # first citation
                                    else:
                                        cite_text = cite_text + ', ' + test_cite + 'a'
                                    break
                            else:
                                cite_text = '\\textcolor{red}{bad ref skipped}' + cite_text

                        else:  # 'a' *was* in the keylist
                            if test_cite + 'b' in bibkeys:
                                cite_text = 'ref year ambiguity ' + cite_text
                            if l == 0:
                                cite_text = cite_text + test_cite + 'a' # first citation
                            else:
                                cite_text = cite_text + ', ' + test_cite + 'a'
                    cite_text = cite_text + '}'

                    if cite_text.endswith('\citep{}'):  # parenthetical didn't match anything, keep it
                        to_write += '(' 
                        to_write += ' '.join(paren) 
                        to_write += ')'
                    else:
                        to_write += cite_text

                if k == len(open_par) - 1:
                    to_write += line[clse_par[-1]+1:]
            else:  # no parentheticals at all!
                to_write = line

            # rescan line and look for figure/equation references to link
            to_write = ut.check_for_fig_tab_eqn_refs(to_write)

            # a few last checks for special cases:
            if to_write.startswith('Figure') or to_write.startswith('Table'): # likely a caption
                print('\t'+to_write[:40])
                iq = input('Is this a caption? [y]/n') or 'y'
                if iq.lower() == 'y':  # save in caption dict, don't write here
                    cap = to_write.split('\\ref{')[1]
                    tag = cap.split('}')[0]
                    if to_write.startswith('Figure'):
                        figcap[tag] = to_write.split(tag)[1][2:].lstrip()
                    elif to_write.startswith('Table'):
                        tabcap[tag] = to_write.split(tag)[1][2:].lstrip()
                    to_write = ''
            elif to_write[0].islower():           # lines (paragraphs) that start with lowercase
                ftex_out.write('\\noindent \n')  # are probably continuing sentences after eqns
            ftex_out.write(to_write)    # finally, write the line


ftex_out.write('\\bibliography{%s}\n' % bibtex.split('/')[-1].split('.')[0])
ftex_out.write('\end{document}')

ftex_in.close()
ftex_out.close()
fjunk.close()

# reread to put in figure captions
ftex_in = open(tex_mid,'r')  # open intermediate file
ftex_out = open(tex_out,'w')

while True:
    line = ftex_in.readline()
    if line.startswith('\\begin{figure}'):
        temp = [line]
        while True:
            line = ftex_in.readline()
            temp.append(line)
            if line.startswith('\label'):
                tag = line.split('\label{')[1].split('}')[0]
            if line.startswith('\end{'):
                break

        for t in temp:
            if t.startswith('\caption'):
                ftex_out.write('\caption{%s}\n' % figcap[tag])
            else:
                ftex_out.write(t)

    elif line.startswith('\\begin{table}'):
        temp = [line]
        while True:
            line = ftex_in.readline()
            temp.append(line)
            if line.startswith('\label'):
                tag = line.split('\label{')[1].split('}')[0]
            if line.startswith('\end{table}'):  # can't be \end{tabular}
                break

        for t in temp:
            if t.startswith('\caption'):
                ftex_out.write('\caption{%s}\n' % tabcap[tag])
            else:
                ftex_out.write(t)

    elif line.startswith('\end{document'):
        ftex_out.write(line)
        break
    else:
        ftex_out.write(line)
        
ftex_in.close()
ftex_out.close()
