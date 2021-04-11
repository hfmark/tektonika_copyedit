import os, sys

# TODO: separate begin{document} and adding abstract?

def set_up_header(fout,title,review=True):
    """
    write out the basic tektonika latex header, with the article title added
    other bits will need to be set manually 
    fout is an open file handler ready for writing this header
    if review, includes draft watermark and linenumbers
    """

    header1 = """\documentclass[10pt,twoside,a4paper]{article}

%  EDIT THIS SECTION  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\\newcommand{\Title}{""" + title + """} % Manuscript title goes here
\\newcommand{\shortTitle}{shorttitle} % Short title for header goes here
\\newcommand{\Author}{Author et al.\\xspace} % First author goes here. Leave blank if opting for blind review.
\\newcommand{\Year}{2021} % Year goes here
\\newcommand{\\vol}{Vol: 01} % Volume number goes here
\\newcommand{\doi}{\\url{doi.org/10.12545/tek-01-01-01}} % DOI goes here
\\newcommand{\journal}{$\\tau e\kappa\\tau oni\kappa a$}
\\newcommand{\dSubmitted}{Received: 01 January 2021}
\\newcommand{\dAccepted}{Accepted: 01 February 2021}
\\newcommand{\dOnline}{Online: 15 February 2021}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%  DO NOT EDIT THIS SECTION  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\pdftrailerid{} %Remove ID
\pdfsuppressptexinfo15 %Suppress PTEX.Fullbanner and info of imported PDFs

\\usepackage[affil-sl]{authblk}
\setcounter{Maxaffil}{3}
\\renewcommand\Affilfont{\itshape\small}
\\renewcommand{\\thefootnote}{\\fnsymbol{footnote}}

\\usepackage{titlesec}
\\titleformat*{\section}{\large \sc \\bfseries}
\\titleformat*{\subsection}{}
\\titleformat*{\subsubsection}{\sl}
\\renewcommand{\\thesubsubsection}{\emph{\\thesubsection.\\arabic{subsubsection}}}

\\usepackage{xcolor}
\definecolor{PUSblue}{HTML}{005FA8}
\\usepackage{hyperref} 
\hypersetup{colorlinks = true, 
			citecolor = PUSblue,
			linkcolor=black,
			urlcolor  = PUSblue}
\\urlstyle{same}

\\usepackage{lipsum}
\\usepackage[pangram]{blindtext}
\\usepackage{fancyhdr}
\\usepackage[french,english]{babel}

\\usepackage{microtype}

\\usepackage[utf8]{inputenc} 
\\usepackage[]{kpfonts}
\\usepackage[T1]{fontenc}

\\usepackage{graphicx}
\\usepackage{booktabs}
\\usepackage{longtable}
\\usepackage[sectionbib,elide]{natbib}
\\bibliographystyle{apalike}
"""
    header2 = """\\usepackage{draftwatermark}
\SetWatermarkText{\sc DRAFT}
\SetWatermarkScale{1}
\SetWatermarkColor[gray]{0.85}
"""
    header3 = """\\newcommand\\blfootnote[1]{%
  \\begingroup
  \\renewcommand\\thefootnote{}\\footnote{#1}%
  \\addtocounter{footnote}{-1}%
  \endgroup
}
\\usepackage{float}
%\\newfloat{footnote}{hb}
\\usepackage[switch]{lineno}

"""
    header4 = """\linenumbers % Enable line numbers to facilitate review process. 
"""
    header5 = """\\usepackage[tmargin=1in,bmargin=1in,lmargin=0.9 in,rmargin=0.9in]{geometry} 

\\usepackage{abstract}
\\renewcommand{\\abstractnamefont}{\\normalfont \large \sc \\bfseries}

\pagestyle{fancy}
\\fancyhf{}
\\fancyhead[LE]{\shortTitle}
\\fancyhead[RE]{\sc \Author, \ \Year}
\\fancyhead[LO]{$\\tau e\kappa\\tau oni\kappa a$, \\vol}
\\fancyhead[RO]{\doi}
\\rfoot{Page \\thepage}
\\fancypagestyle{firststyle}
{
   \\fancyhf{}
   \\fancyhead{\includegraphics[width=\\textwidth]{article_banner.png}}
}
\\title{\Title}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%  EDIT THIS SECTION  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\author{First A Author$^{1,2}$*,
        Second B Author$^{1}$,
        Third Author$^{1}$, \&
        Fourth D Author$^{1}$
~\\\$^{1}${First affiliation, university, place}
\\\$^{2}${Second affiliation, university, place}
\\\{*}Corresponding author (e-mail: authoremail@someplace.edu)}
% Author list goes here, with affiliations defined. Corresponding author email address is defined in the same way. Leave blank if opting for blind review.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
    fout.write(header1)
    if review:
        fout.write(header2)
    fout.write(header3)
    if review:
        fout.write(header4)
    fout.write(header5)
    return fout

def add_abstract(fout,abstract=""):
    """
    write abstract into file after header
    """
    towrite = """
%  DO NOT EDIT THIS SECTION  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\\begin{document}
\date{}

\\twocolumn[
  \\begin{@twocolumnfalse}
    \maketitle
\\thispagestyle{firststyle}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  EDIT THIS SECTION  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\begin{abstract}
""" + abstract + """
\end{abstract}
\\vspace{5mm}
\\vspace{5mm}
  \end{@twocolumnfalse}
]
"""

    fout.write(towrite)
    return fout


_latex_special_chars = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\^{}',
    '\\': r'\textbackslash{}',
    '\n': '\\newline%\n',
    '-': r'{-}',
    '\xA0': '~',  # Non-breaking space
    '[': r'{[}',
    ']': r'{]}',
}

class NoEscape(str):
    """
    A simple string class that is not escaped.
    When a `.NoEscape` string is added to another `.NoEscape` string it will
    produce a `.NoEscape` string. If it is added to normal string it will
    produce a normal string.
    Args
    ----
    string: str
        The content of the `NoEscape` string.
    """

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self)

    def __add__(self, right):
        s = super().__add__(right)
        if isinstance(right, NoEscape):
            return NoEscape(s)
        return s

def escape_latex(s):
    r"""Escape characters that are special in latex.
    Args
    ----
    s : `str`, `NoEscape` or anything that can be converted to string
        The string to be escaped. If this is not a string, it will be converted
        to a string using `str`. If it is a `NoEscape` string, it will pass
        through unchanged.
    Returns
    -------
    NoEscape
        The string, with special characters in latex escaped.
    Examples
    --------
    >>> escape_latex("Total cost: $30,000")
    'Total cost: \$30,000'
    >>> escape_latex("Issue #5 occurs in 30% of all cases")
    'Issue \#5 occurs in 30\% of all cases'
    >>> print(escape_latex("Total cost: $30,000"))
    References
    ----------
        * http://tex.stackexchange.com/a/34586/43228
        * http://stackoverflow.com/a/16264094/2570866
    """

    if isinstance(s, NoEscape):
        return s

    return NoEscape(''.join(_latex_special_chars.get(c, c) for c in str(s)))
