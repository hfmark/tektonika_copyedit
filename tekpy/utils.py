import numpy as np
from re import finditer
import os, sys

####
# functions for text processing of pandoc outputs
####

def parse_environment(line,ftex_in,ftex_out,fjunk,nequ,nfig,ntab):
    """
    read and deal with an environment (equation, figure, table)
    """
    print('environment detected')  # notify the user that we found something
    temp = [line]
    while True:
        line = ftex_in.readline()
        temp.append(line)
        if line.startswith('\end{'):
            break
    if len(temp) < 10:
        for e in temp: print('\t',e[:-1])  # skip newlines with [:-1]
    else:
        for e in temp[:9]: print('\t',e[:-1])

    ieq = input('is this an [e]quation, [f]igure, [t]able, or [n]one of the above?') or 'n' # ask if it looks like an equation
    print('\n')
    if ieq.lower() == 'e':  # if it does, parse it like one
        ftex_out.write('\\begin{equation}\n')
        for k in range(0,len(temp)):  # this only matters if someone puts their equations in tables
            if temp[k].startswith('\\toprule') or temp[k].startswith('\endhead')\
                or temp[k].startswith('\\bottomrule') or temp[k].startswith('\end{')\
                or temp[k].startswith('\\begin{longtable'):
                pass
            elif temp[k].startswith('\('):  # probably the start of the equation
                if '&' in temp[k]:
                    goodpart = temp[k].split('&')[0].rstrip()  # get rid of 2nd column (if table)
                    ftex_out.write(goodpart[2:-2]+'\n')
                else:
                    ftex_out.write(temp[k][2:-2]+'\n') # strip the \( part?
            else:
                ftex_out.write(temp[k])  # split lines? who knows?
        ftex_out.write('\label{eq%i}\n' % nequ)  # label the equation for tex reference
        ftex_out.write('\end{equation}\n')
        nequ += 1  # increment the equation counter

    elif ieq.lower() == 'f':
        ftex_out.write('\\begin{figure}\n')
        ftex_out.write('\includegraphics[width = \columnwidth]{example-image}\n')
        ftex_out.write('\caption{placeholder caption}\n')
        ftex_out.write('\label{fig%i}\n' % nfig)
        ftex_out.write('\end{figure}\n')
        print('moving this environment to junk file; sort it out manually\n')
        fjunk.write('Figure %i\n' % nfig)
        for k in temp:
            fjunk.write(k)
        fjunk.write('\n')  # saving for later
        nfig += 1

    elif ieq.lower() == 't':
        ftex_out.write('\\begin{table}[h]\n')
        ftex_out.write('\centering\n')
        ftex_out.write('\\begin{tabular}{lc}\hline\n')
        ftex_out.write('\\textbf{Data type} & \\textbf{some numbers} \\\\ \hline \n')
        ftex_out.write('type 1 & 1 \\\\ \n')
        ftex_out.write('type 2 & 2 \\\\ \hline \n')
        ftex_out.write('\end{tabular}\n')
        ftex_out.write('\caption{placeholder caption}\n')
        ftex_out.write('\label{tbl%i}\n' % ntab)
        ftex_out.write('\end{table}\n')
        print('moving this environment to junk file; sort it out manually\n')
        fjunk.write('Table %i\n' % ntab)
        for k in temp:
            fjunk.write(k)
        fjunk.write('\n')  # saving for later
        ntab += 1

    else:
        print('moving this environment to junk file; sort it out manually\n')
        fjunk.write('Unspecified thing:\n')
        for k in temp:
            fjunk.write(k)
        fjunk.write('\n')

    return ftex_in, ftex_out, fjunk, nequ, nfig, ntab, ieq

def check_for_fig_tab_eqn_refs(to_write):
    """
    check a line for 'Figure 1' or 'Equation 9' or whatever, replace those with linked refs
    """

    capital_names = ['Figure','Equation','Table','Fig.','Eq.']
    ref_names = ['fig','eq','tbl','fig','eq']

    for iw, word in enumerate(capital_names):
        if word in to_write.split() or '('+word in to_write.split():
            nrefs = len([m.start() for m in finditer(word,to_write)])
            # for each such index, look for the number
            for ireplace in range(nrefs):
                inds = np.array([m.start() for m in finditer(word,to_write)])
                ifig = inds[ireplace]
                shift = len(word) + 1
                try:
                    fig_num = int(to_write[ifig+shift])
                except ValueError:  # this isn't an int
                    if to_write[ifig+shift] == 'S':  # a supplemental item? skip it
                        fig_num = 999
                    else:
                        try:
                            shift = len(word)+ + 2
                            fig_num = int(to_write[ifig+shift])  # maybe the number was in parens?
                        except ValueError:
                            fig_num = 999

                if fig_num != 999: # check again for double-digit numbers
                    try:           # (if anyone has >99 figures we are in trouble)
                        second_digit = int(to_write[ifig+shift+1])
                        fig_num = int(to_write[ifig+shift:ifig+shift+2])
                    except ValueError:
                        pass  # we were fine to start with

                if fig_num != 999:
                    # replace the word and number with an inline reference 
                    line_start = to_write[:ifig]
                    if fig_num > 9:
                        line_end = to_write[ifig+shift+2:]
                    else:
                        line_end = to_write[ifig+shift+1:]
                    to_write = line_start + word + '~\\ref{%s%i}' % (ref_names[iw],fig_num) + line_end

    return to_write
