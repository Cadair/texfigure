# -*- coding: utf-8 -*-
"""
Created on Fri May 29 17:03:59 2015

@author: Stuart Mumford

This uses a fair bit of the magic from here:
http://bkanuka.com/articles/native-latex-plots/
"""

import numpy as np

import matplotlib
matplotlib.use('pgf')


def figsize(pytex, scale=None):
    """
    Configure a matplotlib figure size based on the native page width and the
    golden ratio.

    Parameters
    ----------

    pytex : PythonTeX Utilites Class
        The PythonTeX helper class instance from the LaTeX document.

    scale : float
        The scale of the figure width in comparison to the textwidth, i.e.
        1 = 100%.

    Returns
    -------

    fig_size : tuple
        The ``(width, height)`` tuple of the figure size in inches for mpl.


    Examples
    --------

    .. code-block:: latex

        % Give PythonTeX the Textwidth
        \setpythontexcontext{figurewidth=\the\textwidth}
        \begin{document}

        \begin{pycode}
        plt.figure(figsize=figsize(pytex))
        ...
        \end{pycode}

    """
    if hasattr(pytex, 'context'):
        textwidth_pt = float(pytex.context.get('figurewidth', 'pt')[:-2])
        if not scale:
            scale = float(pytex.context.get('figscale', 0.95))
    else:
        textwidth_pt = None
        if not scale:
            scale = 0.95

    if not textwidth_pt:
        raise AttributeError(r"pytex.context has no attribute figurewidth, please "
                             r"execute the following command in the preamble: "
                             r"\setpythontexcontext{figurewidth=\the\textwidth}")
    textwidth_in = pytex.pt_to_in(textwidth_pt)


    golden_mean = (np.sqrt(5.0)-1.0)/2.0
    fig_width = scale*textwidth_in # 90% width

    return (fig_width, fig_width*golden_mean)


def configure_latex_plots(pytex):
    """
    Configure a sane set of latex defaults for pgf figure generation.

    Parameters
    ----------

    pytex : PythonTeX Utilites class.
        The pytex class from the PythonTeX Session
    """

    pgf_with_latex = {
        "pgf.texsystem": "pdflatex",
        "text.usetex": True,
        "font.size": 10,
        "font.family": "serif",
        "font.serif": [],  # blank entries should cause plots to inherit fonts from the document
        "font.sans-serif": [],
        "font.monospace": [],
        "axes.labelsize": 10,  # LaTeX default is 10pt font.
        "legend.fontsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "figure.figsize": figsize(pytex),
        "pgf.preamble": [
            r"\usepackage[utf8x]{inputenc}",    # use utf8 fonts becasue your computer can handle it :)
            r"\usepackage[T1]{fontenc}",        # plots will be generated using this preamble
            ]
        }
    matplotlib.rcParams.update(pgf_with_latex)



def preamble_setup():
    preamble = """
    % pytexbug fix for context in customcode.
    \makeatletter
    \renewenvironment{pythontexcustomcode}[2][begin]{%
    	\VerbatimEnvironment
    	\Depythontex{env:pythontexcustomcode:om:n}%
    	\ifstrequal{#1}{begin}{}{%
    		\ifstrequal{#1}{end}{}{\PackageError{\pytx@packagename}%
    			{Invalid optional argument for pythontexcustomcode}{}
    		}%
    	}%
    	\xdef\pytx@type{CC:#2:#1}%
    	\edef\pytx@cmd{code}%
    	% PATCH \def\pytx@context{}%
    	\pytx@SetContext
    	% END PATCH
    	\def\pytx@group{none}%
    	\pytx@BeginCodeEnv[none]}%
    {\end{VerbatimOut}%
    \setcounter{FancyVerbLine}{\value{pytx@FancyVerbLineTemp}}%
    \stepcounter{\pytx@counter}%
    }%
    \makeatother

    \setpythontexcontext{textwidth=\the\textwidth}
    """
    return preamble