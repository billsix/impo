% osbook.cls
% Document class for the OpenStax Calculus volumes, typeset in a house
% style adapted from the Open Logic Project's open-logic-book.cls.
%
% Captures the OpenLogic "nice book" look — memoir base, golden-ratio
% type block, Latin Modern (Computer Modern) fonts, big
% bold-italic colored chapter titles with a vertical accent bar — while
% dropping the logic-specific / KDP-cover / pdfx machinery.
%
% Paper-size options:
%   letter  (default) -- US Letter 8.5x11in, 5.5in measure, colored links
%   screen            -- 8x5in, 300pt measure, colored links
%   print             -- KDP quarto trim, asymmetric (spine) margins,
%                        black links, chapter side-bars

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{osbook}[2026/06/20 OpenStax Calculus, OpenLogic-style]

% Paper-size options (mutually exclusive):
%   letter  (default) -- US Letter 8.5x11in, generous margins, colored links
%   screen            -- 8x5in, symmetric margins, colored links
%   print             -- KDP quarto trim, asymmetric (spine) margins, black links
\def\calc@mode{letter}
\DeclareOption{letter}{\def\calc@mode{letter}}
\DeclareOption{screen}{\def\calc@mode{screen}}
\DeclareOption{print}{\def\calc@mode{print}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{memoir}}
\ExecuteOptions{letter}
\ProcessOptions\relax

% ---- base class -----------------------------------------------------
\LoadClass[11pt,openany]{memoir}

% ---- core packages (order matters for the theorem/font stack) -------
\RequirePackage{fontspec}       % lualatex: Unicode text fonts (OpenStax house)
\setmainfont{Roboto Slab}[AutoFakeSlant=0.18]  % body serif (Roboto Slab has no italic)
\setsansfont{Noto Sans}         % headings / labels
\RequirePackage[english]{babel}
\RequirePackage{amsmath}
\RequirePackage{mathtools}       % \mathrlap etc. (zero-width boxes for MathML mpadded)
\RequirePackage{capt-of}        % \captionof for non-floating figures
\RequirePackage{graphicx}
\RequirePackage{xcolor}

% ---- color scheme (defined before hyperref so links can use it) -----
% Single accent color + a dark variant for links + a light tint for boxes.
% Override \colorlet{OScolor}{...} in a master to rebrand.
% OpenStax algebra-1 palette (from ce-styles algebra-1-pdf.css)
\definecolor{OScolor}{HTML}{093D4C}        % primary dark teal
\definecolor{OSmed}{HTML}{1E7A8F}          % medium teal (section headings)
\definecolor{OSaccent}{HTML}{C6CE33}       % chartreuse pop
% Per-book theme override: a book may ship an osbook-bookstyle.tex (placed beside
% the class in checkout/latex/ by apply.sh) to re-set \setmainfont and/or the base
% palette colors above (OScolor/OSmed/OSaccent). Loaded here -- BEFORE the derived
% colors below -- so an override of OScolor flows into OSdkcolor. Absent = the
% default Roboto-Slab + teal theme. (calculus ships a Times + blue book-style.)
\InputIfFileExists{osbook-bookstyle.tex}{}{}
\colorlet{OSdkcolor}{OScolor}
\colorlet{OSltcolor}{black!5}              % light gray box tint (~#F1F1F1)

\RequirePackage{textcomp}
\RequirePackage{mdframed}
\RequirePackage{multicol}       % OpenStax lays practice exercises in two columns
\RequirePackage{array}
\RequirePackage{colortbl}       % teal-header grid tables (OpenStax look)
\RequirePackage{hyperref}
% ntheorem before Computer Modern math (avoids multiple-\openbox clash); before thmtools
\RequirePackage[thmmarks,amsmath,amsthm,hyperref]{ntheorem}
\RequirePackage{thmtools}

% ---- fonts (after ntheorem, after amssymb) --------------------------
\RequirePackage{unicode-math}              % load last among math packages
\setmathfont{STIX Two Math}                % OpenStax math font (validated)
% amssymb names the converter emits that unicode-math does not alias by default
\providecommand{\square}{\mdlgwhtsquare}   % fill-in-the-blank box (was amssymb's)

% ---- circled exercise sub-part markers (ⓐ ⓑ ⓒ, Ⓐ.., ①..⑨) -----------
% The converter emits these as RAW Unicode (not \textcircled{a}) so the pandoc
% HTML build passes them through as proper circled glyphs; here we map each back
% to \textcircled so the lualatex PDF renders exactly as before. (\textcircled{a}
% fed to pandoc became "a"+U+20DD, the broken "a⃝" -- see convert.py.)
\RequirePackage{newunicodechar}
\newunicodechar{ⓐ}{\textcircled{a}}\newunicodechar{ⓑ}{\textcircled{b}}\newunicodechar{ⓒ}{\textcircled{c}}
\newunicodechar{ⓓ}{\textcircled{d}}\newunicodechar{ⓔ}{\textcircled{e}}\newunicodechar{ⓕ}{\textcircled{f}}
\newunicodechar{ⓖ}{\textcircled{g}}\newunicodechar{ⓗ}{\textcircled{h}}\newunicodechar{ⓘ}{\textcircled{i}}
\newunicodechar{ⓙ}{\textcircled{j}}\newunicodechar{ⓚ}{\textcircled{k}}\newunicodechar{ⓛ}{\textcircled{l}}
\newunicodechar{ⓜ}{\textcircled{m}}\newunicodechar{ⓝ}{\textcircled{n}}\newunicodechar{ⓞ}{\textcircled{o}}
\newunicodechar{ⓟ}{\textcircled{p}}\newunicodechar{ⓠ}{\textcircled{q}}\newunicodechar{ⓡ}{\textcircled{r}}
\newunicodechar{ⓢ}{\textcircled{s}}\newunicodechar{ⓣ}{\textcircled{t}}\newunicodechar{ⓤ}{\textcircled{u}}
\newunicodechar{ⓥ}{\textcircled{v}}\newunicodechar{ⓦ}{\textcircled{w}}\newunicodechar{ⓧ}{\textcircled{x}}
\newunicodechar{ⓨ}{\textcircled{y}}\newunicodechar{ⓩ}{\textcircled{z}}
\newunicodechar{Ⓐ}{\textcircled{A}}\newunicodechar{Ⓑ}{\textcircled{B}}\newunicodechar{Ⓒ}{\textcircled{C}}
\newunicodechar{Ⓓ}{\textcircled{D}}\newunicodechar{Ⓔ}{\textcircled{E}}\newunicodechar{Ⓕ}{\textcircled{F}}
\newunicodechar{Ⓖ}{\textcircled{G}}\newunicodechar{Ⓗ}{\textcircled{H}}\newunicodechar{Ⓘ}{\textcircled{I}}
\newunicodechar{Ⓙ}{\textcircled{J}}\newunicodechar{Ⓚ}{\textcircled{K}}\newunicodechar{Ⓛ}{\textcircled{L}}
\newunicodechar{Ⓜ}{\textcircled{M}}\newunicodechar{Ⓝ}{\textcircled{N}}\newunicodechar{Ⓞ}{\textcircled{O}}
\newunicodechar{Ⓟ}{\textcircled{P}}\newunicodechar{Ⓠ}{\textcircled{Q}}\newunicodechar{Ⓡ}{\textcircled{R}}
\newunicodechar{Ⓢ}{\textcircled{S}}\newunicodechar{Ⓣ}{\textcircled{T}}\newunicodechar{Ⓤ}{\textcircled{U}}
\newunicodechar{Ⓥ}{\textcircled{V}}\newunicodechar{Ⓦ}{\textcircled{W}}\newunicodechar{Ⓧ}{\textcircled{X}}
\newunicodechar{Ⓨ}{\textcircled{Y}}\newunicodechar{Ⓩ}{\textcircled{Z}}
\newunicodechar{①}{\textcircled{1}}\newunicodechar{②}{\textcircled{2}}\newunicodechar{③}{\textcircled{3}}
\newunicodechar{④}{\textcircled{4}}\newunicodechar{⑤}{\textcircled{5}}\newunicodechar{⑥}{\textcircled{6}}
\newunicodechar{⑦}{\textcircled{7}}\newunicodechar{⑧}{\textcircled{8}}\newunicodechar{⑨}{\textcircled{9}}

% OpenStax uses block paragraphs: no first-line indent, vertical space between
% (so worked-example steps/equations sit flush-left with breathing room).
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt plus 1.5pt minus 1pt}

% cleveref always last, after hyperref
\RequirePackage[nameinlink]{cleveref}

% clean proof-end box (ntheorem's \openbox can misbehave after cases)
\gdef\proofSymbol{\ensuremath{\Box}}

% ---- page geometry (golden-ratio type block) ------------------------
% \OSbookformat{height}{width}{upper margin}{l/r margin ratio}{text-block width}
\newcommand{\OSbookformat}[5]{%
  \setstocksize{#1}{#2}%
  \settrimmedsize{\stockheight}{\stockwidth}{*}%
  \settrims{0pt}{0pt}%
  \settypeblocksize{*}{#5}{1.62}%  golden-ratio height from the measure
  \setlrmargins{*}{*}{#4}%
  \setulmargins{#3}{*}{*}%
  \setheaderspaces{*}{*}{1}%
  \checkandfixthelayout%
}

\newlength{\barwidth}
\def\calc@modeprint{print}
\def\calc@modescreen{screen}
\ifx\calc@mode\calc@modeprint          % KDP quarto print interior
  \OSbookformat{24.589cm}{18.91cm}{90pt}{1.3}{300pt}
  \setlength{\barwidth}{7pt}
  \hypersetup{hidelinks}
\else\ifx\calc@mode\calc@modescreen    % 8x5in screen-reading
  \OSbookformat{8in}{5in}{.6in}{1}{300pt}
  \setlength{\barwidth}{0pt}
  \hypersetup{colorlinks=true,allcolors=OSdkcolor,
    linktoc=all,pdfdisplaydoctitle=true}
\else                                  % letter (default): US Letter 8.5x11in
  \OSbookformat{11in}{8.5in}{1.3in}{1}{5in}
  \setlength{\barwidth}{0pt}
  \hypersetup{colorlinks=true,allcolors=OSdkcolor,
    linktoc=all,pdfdisplaydoctitle=true}
\fi\fi

% ---- chapter & part heading style -----------------------------------
\makechapterstyle{OScalc}{%
  \setlength{\afterchapskip}{40pt}%
  \setlength{\beforechapskip}{50pt}%
  \setlength{\midchapskip}{10pt}%
  \renewcommand*{\afterchapternum}{\par\nobreak\vskip 0pt}%
  \renewcommand*{\chapnamefont}{\fontsize{14pt}{0pt}\selectfont\sffamily\bfseries}%
  \let\chapnumfont\chapnamefont
  \renewcommand*{\chaptitlefont}{%
    \normalfont\fontsize{44pt}{44pt}\selectfont\bfseries\itshape\color{OScolor}}%
  \renewcommand*{\printchaptername}{\chapnamefont\MakeUppercase{\@chapapp}}%
  \renewcommand*{\printchaptertitle}[1]{%
    \chaptitlefont ##1\\[-\baselineskip]%
    \hspace*{-20pt}%
    \smash{\color{OScolor}\rule{\barwidth}{350pt}}}%
}
\chapterstyle{OScalc}

\renewcommand*{\partnamefont}{\fontsize{24pt}{0pt}\selectfont\bfseries\sffamily}
\renewcommand*{\partnumfont}{\fontsize{24pt}{0pt}\selectfont\bfseries\sffamily}
\renewcommand*{\parttitlefont}{%
  \normalfont\fontsize{54pt}{54pt}\selectfont\bfseries\itshape\color{OScolor}}

% section headings in the accent color, sans-serif. OpenStax sets the lesson
% opener (our \section) in UPPERCASE; sub-headings stay title-case.
\setsecheadstyle{\Large\sffamily\bfseries\color{OSmed}\raggedright\MakeTextUppercase}
\setsubsecheadstyle{\large\sffamily\bfseries\color{OSmed}}
\setsubsubsecheadstyle{\normalsize\sffamily\bfseries}

% ---- captions -------------------------------------------------------
\captionnamefont{\footnotesize\itshape\color{OScolor}}
\captiontitlefont{\footnotesize}
\def\figurename{Figure}
% Uncaptioned floats: OpenStax still numbers them ("Figure 1.4"), but memoir's
% default ": " delimiter would leave a dangling colon ("Figure 1.4:"). Emit the
% number with no delimiter. Grouped so \captiondelim stays local to this caption.
\newcommand{\OSnumonlycaption}[1]{\begingroup\captiondelim{}\captionof{#1}{}\endgroup}

% ---- running heads --------------------------------------------------
\makepagestyle{OSpage}
\makepsmarks{OSpage}{%
  \createmark{chapter}{both}{shownumber}{\@chapapp\ }{ \textbullet\ }%
  \createmark{section}{right}{shownumber}{}{ \textbullet\ }%
}
% memoir defaults to \uppercaseheads (marks wrapped in \MakeUppercase); OpenStax
% running heads are title-case, so turn that off.
\nouppercaseheads
\makeoddhead{OSpage}{\small\sffamily\color{OScolor}\rightmark}{}%
  {\color{OScolor}\sffamily\bfseries\thepage}
\makeevenhead{OSpage}{\color{OScolor}\sffamily\bfseries\thepage}{}%
  {\small\sffamily\color{OScolor}\leftmark}
\makeoddfoot{OSpage}{}{}{}
\makeevenfoot{OSpage}{}{}{}

\setlength{\cftbeforechapterskip}{1.0em plus 0.5em minus 0.25em}

% make justification slightly loose to avoid overfull lines in math text
\midsloppy
\setlength{\emergencystretch}{3em}  % reduce overfull lines in dense math text

% ---- book metadata setters & front matter ---------------------------
\newcommand{\OSbooktitle}{Calculus}
\newcommand{\OSbooksubtitle}{}
\newcommand{\OSbookversion}{}
\newcommand{\setOSbooktitle}[1]{\renewcommand{\OSbooktitle}{#1}}
\newcommand{\setOSbooksubtitle}[1]{\renewcommand{\OSbooksubtitle}{#1}}
\newcommand{\setOSbookversion}[1]{\renewcommand{\OSbookversion}{#1}}

% License-page body and an optional dedication, both overridable per book so a
% NON-OpenStax book (e.g. the impo trench family) can state its own license and
% dedication. The DEFAULTS below reproduce the OpenStax CC BY-NC-SA 4.0 license
% page exactly, so any book that does not call these setters is unchanged.
\newcommand{\OSbookdedication}{}
\newcommand{\setOSbookdedication}[1]{\renewcommand{\OSbookdedication}{#1}}
\newcommand{\OSbookpublisher}{OpenStax}
\newcommand{\setOSbookpublisher}[1]{\renewcommand{\OSbookpublisher}{#1}}
\newcommand{\OSlicensetext}{%
  This work is produced from the OpenStax \emph{\OSbooktitle} textbook,
  published by OpenStax, a nonprofit educational initiative of Rice
  University. The original work is available at
  \url{https://openstax.org/} and is licensed under a Creative Commons
  Attribution-NonCommercial-ShareAlike 4.0 International License
  (CC BY-NC-SA 4.0).\par
  \medskip
  \noindent This LaTeX edition is likewise distributed under
  CC BY-NC-SA 4.0.\par
  \medskip
  \noindent Typeset in Latin Modern and Computer Modern Sans with \LaTeX.}
\newcommand{\setOSbooklicense}[1]{\renewcommand{\OSlicensetext}{#1}}

% \OSfrontmatter -- half-title, title page, license page, contents
\newcommand{\OSfrontmatter}{%
  \frontmatter
  \pagestyle{empty}
  % half title
  \vspace*{100pt}
  \begin{raggedleft}
    {\fontsize{24pt}{28pt}\selectfont\bfseries\sffamily\color{OScolor}%
      \OSbooktitle\par}
    \ifx\OSbooksubtitle\empty\else
      \medskip{\fontsize{16pt}{20pt}\selectfont\bfseries\itshape\OSbooksubtitle\par}
    \fi
  \end{raggedleft}
  \newpage
  % title page
  \vspace*{120pt}
  \begin{raggedleft}
    {\fontsize{30pt}{34pt}\selectfont\bfseries\sffamily\color{OScolor}\OSbooktitle\par}
    \ifx\OSbooksubtitle\empty\else
      \bigskip{\fontsize{18pt}{22pt}\selectfont\bfseries\itshape\OSbooksubtitle\par}
    \fi
    \vspace{120pt}
    {\fontsize{13pt}{16pt}\selectfont\OSbookpublisher\par}
    \vfill
    \ifx\OSbookversion\empty\else{\textsc{\OSbookversion}\par}\fi
  \end{raggedleft}
  \newpage
  % copyright / license page (body is \OSlicensetext, overridable per book)
  \vspace*{\fill}
  \noindent\small
  \OSlicensetext\par
  \vspace*{\fill}
  \newpage
  % optional dedication page (empty by default -> no page)
  \ifx\OSbookdedication\empty\else
    \vspace*{\fill}
    \begin{center}%
      {\fontsize{20pt}{24pt}\selectfont\itshape\color{OScolor}\OSbookdedication\par}%
    \end{center}
    \vspace*{\fill}
    \newpage
  \fi
  % contents
  \pagestyle{OSpage}
  \currentpdfbookmark{Table of Contents}{toc}
  \tableofcontents*
  \mainmatter
}

\endinput
