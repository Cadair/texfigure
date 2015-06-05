# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 18:01:51 2014

@author: Stuart Mumford

A Class that holds Python information on a chapter level.
"""
import os
import sys
from collections import OrderedDict

import numpy as np

import matplotlib.pyplot as plt

from plotting_helpers import fig_str, sub_fig_str, get_pgf_include

__all__ = ['Manager', 'Figure', 'MultiFigure']

class Figure(object):
    """
    A class for holding a figure file, that knows how to represent itself
    as a latex environment.

    Parameters
    ----------

    file_name : string
        The full path of the figure file.

    reference : string
        A reference label for this figure, used as default values for caption
        and label.

    Attributes
    ----------
    fname : string
        The base name of the full file path

    base_dir : string
        The directory containing the figure file

    caption : string
        The caption to use when representing the figure. (Default ``Figure reference``)

    label : string
        The latex label assigned to the figure envrionment. (Default ``fig:reference``)

    placement : string
        The figure envrionment placement value. (Default ``H``)

    figure_width : string
        The latex figure width, not used for pgf files. (Default ``0.9\columnwidth``)

    extension_mapping : dict
        A mapping of file extensions to methods to return LaTeX includes for
        the file type.

    fig_str : string
        The latex figure layout template.
    """

    fig_str = r"""
\begin{{figure}}
    \centering
    {myfig}
    \caption{{ {caption} }}
    \label{{ {label} }}
\end{{figure}}
"""

    subfig_str = r"""
    \begin{{subfigure}}[{placement}]{{{width}}}
        {myfig}
        \caption{{{caption}}}
        \label{{{label}}}
    \end{{subfigure}}"""


    def __init__(self, file_name, reference=None):
        file_name = os.path.abspath(file_name)
        if not reference:
            self.reference = os.path.splitext(os.path.basename(file_name))[1]
        else:
            self.reference = reference

        self.reference = self.reference.replace('_','-')

        self.file_name = file_name
        self.fname = os.path.basename(file_name)
        self.base_dir = os.path.dirname(file_name) + '/'

        self.caption = "Figure {}".format(self.reference)
        self.label = "fig:{}".format(self.reference)
        self.placement = 'H'
        self.figure_width = r'0.9\columnwidth'
        self.subfig_width = r'0.45\textwidth'
        self.subfig_placement = 'b'

        self.extension_mapping = {'.pgf': self.get_pgf_include,
                                  '.png': self.get_standard_include,
                                  '.pdf': self.get_standard_include}

    @property
    def extension(self):
        """
        File extension of the file_name.
        """
        return os.path.splitext(self.fname)[1]

    def get_pgf_include(self):
        return r"\IfFileExists{{{file_name}}}{{\import{{{base_dir}}}{{{fname}}}}}{{}}".format(
                                                      fname=self.fname,
                                                      base_dir=self.base_dir,
                                                      file_name=self.file_name)

    def get_standard_include(self):
        return "\includegraphics[width={width}]{{{file_name}}}".format(
                                                      width=self.figure_width,
                                                      file_name=self.file_name)

    def _repr_latex_(self):

        default_kwargs = {'placement':self.placement,
                          'caption':self.caption,
                          'label': self.label}

        myfig = self.extension_mapping[self.extension]()

        return self.fig_str.format(myfig=myfig, **default_kwargs)

    def repr_subfigure(self):
        default_kwargs = {'placement': self.subfig_placement,
                          'width': self.subfig_width,
                          'caption': self.caption,
                          'label': self.label}

        myfig = self.extension_mapping[self.extension]()

        return self.subfig_str.format(myfig=myfig, **default_kwargs)


class MultiFigure(object):
    """
    A Multifigure is a container object for building subfigures from
    `texfigure.Figure` classes.

    Parameters
    ----------

    nrows : float
        Number of rows for the MultiFigure.

    ncols : float
        Number of columns for the MultiFigure.

    """

    fig_str = r"""
\begin{{figure*}}
    \centering
    {myfig}
    \caption{{ {caption} }}
    \label{{ {label} }}
\end{{figure*}}
"""

    def __init__(self, nrows, ncols, reference=''):
        self.nrows = nrows
        self.ncols = ncols
        self.reference = reference

        self.caption = "MultiFigure {}".format(self.reference)
        self.label = "fig:{}".format(self.reference)
        self.placement = 'H'

        self.figures = np.zeros([nrows, ncols], dtype=object)
        self.figures[:] = None

    def append(self, figure):
        """
        Add a `texfigure.Figure` object to the next empty slot in the MultiFigure.
        """
        if not isinstance(figure, Figure):
            raise TypeError("Only texfigure.Figures can be appended to a MultiFigure")

        empties = np.logical_not(self.figures.flat).nonzero()[0]

        if len(empties):
            self.figures.flat[empties[0]] = figure
        else:
            raise ValueError("This MultiFigure is full")

    def _repr_latex_(self):

        default_kwargs = {'placement':self.placement,
                          'caption':self.caption,
                          'label': self.label}

        subfigures = ""

        for i, fig in enumerate(self.figures.flat):
            if fig:
                if i % self.ncols == 0:
                    subfigures +='\n'
                subfigures += fig.repr_subfigure()

        return self.fig_str.format(myfig=subfigures, **default_kwargs)


class Manager(object):
    """
    A class holding information about different figures and data.

    Parameters
    ----------

    pytex : ``PythonTeXUtils`` instance.
        The pytex object from the PythonTeX session.

    number : float
        Numerical index for this chapter.

    base_path : string
        Path to the base directory for all files for this manager.

    python_dir : bool or string
        Path to a directory containing Python code to be added to the Python
        path.

    """

    def __init__(self, pytex, base_path, number=1, python_dir=True,
                 data_dir=True, fig_dir=True):

        self.pytex = pytex
        self._number = number
        self._base_path = base_path


        self._python_dir = None
        self.python_dir = python_dir

        self._data_dir = None
        self.data_dir = data_dir

        self._fig_dir = None
        self.fig_dir = fig_dir

        self.fig_count = 1
        self._figure_registry = OrderedDict()

    def _add_dir(self, adir, attr, default):
        if adir:
            if not isinstance(adir, str):
                setattr(self, attr, os.path.join(self._base_path, default))
            else:
                setattr(self, attr, adir)

            if not os.path.exists(getattr(self, attr)):
                os.makedirs(getattr(self, attr))

    @property
    def data_dir(self):
        """
        Data directory for files tracked with this manager.

        If data_dir is set to False no directory will be used, if set to True
        the default directory of ``manager.base_path/Data`` will be used, if
        data_dir is set to a string then that dir will be used.
        """
        return self._data_dir

    @data_dir.setter
    def data_dir(self, value):
        self._add_dir(value, '_data_dir', 'Data')

    @property
    def fig_dir(self):
        """
        Figure directory for figures tracked with this manager.

        If fig_dir is set to False no directory will be used, if set to True
        the default directory of ``manager.base_path/Figs`` will be used, if
        fig_dir is set to a string then that dir will be used.
        """
        return self._fig_dir

    @fig_dir.setter
    def fig_dir(self, value):
        self._add_dir(value, '_fig_dir', 'Figs')

    @property
    def python_dir(self):
        """
        Python directory for custom python code, this directory will be added
        to your Python Path.

        If python_dir is set to False no directory will be used, if set to True
        the default directory of ``manager.base_path/Python`` will be used, if
        python_dir is set to a string then that dir will be used.

        Notes
        -----

        If this attribute is changed, the old directory will not be removed from
        the python path.
        """
        return self._python_dir

    @python_dir.setter
    def python_dir(self, value):
        self._add_dir(value, '_python_dir', 'Python')
        if self._python_dir:
            sys.path.append(self._python_dir)

    @property
    def number(self):
        return self._number

    @property
    def chapter_path(self):
        return self._chapter_path

    def data_file(self, file_name):
        """
        Get the full path of a data file in this chapters data directory,
        add it to the pytex tracked files.

        Parameters
        ----------
        file_name : str
            The filename in the data directory
        """

        fname = os.path.join(self.data_dir, file_name)
        self.pytex.add_dependencies(fname)
        return fname

    def make_figure_filename(self, ref, fname=None, fext=''):
        """
        Return the standard template figure name with number.

        Parameters
        ----------
        ref : string
            The latex reference for this figure (excluding 'fig:')
        fname : string
            Overwrite the default file name template with this name.

        Returns
        -------
        fname : string
            The file name
        """
        if not fname:
            fname = 'Chapter{}-Figure{}-{}{}'.format(self.number, self.fig_count,
                                                     ref, fext)

        fname = fname

        return fname

    def add_figure(self, ref, Fig):
        """
        Add the figure to the tracked files and increment the figure count.

        Parameters
        ----------
        ref : string
            The latex reference for this figure (excluding 'fig:')

        fname : string
            Overwrite the default file name template with this name.
        """

        self.pytex.add_created(Fig.file_name)

        self._figure_registry[ref] = {'number': self.fig_count, 'Figure': Fig}
        self.fig_count += 1

    def save_figure(self, ref, fig=None, fname=None, fext='.pgf'):
        """
        Save a matplotlib figure and track it in this chapter
        """

        if fig is None:
            fig = plt.gcf()

        fname = os.path.join(self.fig_dir, self.make_figure_filename(ref, fname=fname, fext=fext))

        fig.savefig(fname)

        Fig = Figure(fname, reference=ref)

        self.add_figure(ref, Fig)

        return Fig

    def get_figure(self, ref):
        """
        Get the filename of a figure that has already been saved

        Parameters
        ----------
        ref : str
            The Figure reference

        Returns
        -------
        fname : str
            The filename
        """

        return self._figure_registry[ref]['Figure']

    def build_figure(self, ref, **kwargs):
        """
        Print a whole figure environment
        """

        Fig = self.get_figure(ref)

        for k,v in kwargs.items():
            setattr(Fig, k, v)

        return Fig

    def build_subfigure(self, ref, **kwargs):
        """
        Print a whole figure environment
        """

        fname = self.get_figure_filename(ref)

        default_kwargs = {'placement':'b', 'caption':'Figure {}'.format(ref),
                          'label':'fig:{}'.format(ref), 'width':r'\columnwidth'}
        default_kwargs.update(kwargs)

        myfig = get_pgf_include(fname)

        return sub_fig_str.format(myfig=myfig, **default_kwargs)
