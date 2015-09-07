# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 18:01:51 2014

@author: Stuart Mumford

A Class that holds Python information on a chapter level.
"""
import os
import sys
from collections import OrderedDict, Sequence

import numpy as np

import matplotlib
import matplotlib.pyplot as plt

try:
    import mayavi
    from mayavi import mlab
    HAVE_MAYAVI = True
except ImportError:
    HAVE_MAYAVI = False

try:
    import yt
    HAVE_YT = True
except ImportError:
    HAVE_YT = False


__all__ = ['Manager', 'Figure', 'MultiFigure']


class Figure(object):
    r"""
    A class for holding a figure file, that knows how to represent itself
    as a latex environment.

    Parameters
    ----------

    file_name : `str`
        The full path of the figure file.

    reference : `str`
        A reference label for this figure, used as default values for caption
        and label.


    Attributes
    ----------
    fname : `str`
        The base name of the full file path

    base_dir : `str`
        The directory containing the figure file

    caption : `str`
        The caption to use when representing the figure.
        (Default ``Figure reference``)

    label : `str`
        The latex label assigned to the figure envrionment, will bre prefixed
        with ``'fig``. (Default ``fig:reference``)

    placement : `str`
        The figure envrionment placement value. (Default ``h``)

    figure_width : `str`
        The latex figure width, not used for pgf files.
        (Default ``0.95\columnwidth``)

    subfig_width : `str`
        LaTeX figure width for when the figure is included in a subfigure.
        (Default ``0.45\columnwidth``)

    subfig_placement : `str`
        The subfigure environment placement. (Default ``b``)

    extension_mapping : `dict`
        A mapping of file extensions to methods to return LaTeX includes for
        the file type.

    fig_str : `str`
        The LaTeX template for representing this `~texfigure.Figure` as
        a figure environment.

    subfig_str : `str`
        The LaTeX template for representing this `~texfigure.Figure` as
        a subfigure.

    Examples
    --------

    .. code-block:: latex

        \begin{pycode}
        import matplotlib.pyplot as plt

        fig = plt.figure()
        plt.plot([1,2], [3,4], 'o')

        myfig = texfigure.Figure(fig, 'myfig')
        \end{pycode}

        \py|myfig|

    """

    fig_str = r"""
\begin{{figure}}[{placement}]
    \centering
    {myfig}
    \caption{{{caption}}}
    \label{{{label}}}
\end{{figure}}
"""

    # Note the different indentation here, this is deleberate.
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

        self.reference = self.reference.replace('_', '-')

        self.file_name = file_name
        self.fname = os.path.basename(file_name)
        self.base_dir = os.path.dirname(file_name) + '/'

        self.caption = "Figure {}".format(self.reference)
        self.label = "fig:{}".format(self.reference)
        self.placement = 'h'
        self.figure_width = r'0.95\columnwidth'
        self.subfig_width = r'0.45\columnwidth'
        self.subfig_placement = 'b'

        self.extension_mapping = {'.pgf': self.get_pgf_include,
                                  '.png': self.get_standard_include,
                                  '.pdf': self.get_standard_include}

    @property
    def extension(self):
        """
        File extension of fname.
        """
        return os.path.splitext(self.fname)[1]

    def get_pgf_include(self):
        """
        Return the import statement for this `~texfigure.Figure` as
        a pgf file.close.
        """

        return r"\IfFileExists{{{file_name}}}{{\import{{{base_dir}}}{{{fname}}}}}{{}}".format(
                                                      fname=self.fname,
                                                      base_dir=self.base_dir,
                                                      file_name=self.file_name)

    def get_standard_include(self):
        """
        Return the includegraphics command for most other file types.
        """

        return "\includegraphics[width={width}]{{{file_name}}}".format(
                                                      width=self.figure_width,
                                                      file_name=self.file_name)

    def repr_figure(self):
        """
        Return a string LaTeX figure environment for this `~texfigure.Figure`
        """

        default_kwargs = {'placement': self.placement,
                          'caption': self.caption,
                          'label': self.label}

        myfig = self.extension_mapping[self.extension]()

        return self.fig_str.format(myfig=myfig, **default_kwargs)

    def repr_subfigure(self):
        """
        Return a string subfigure environment for this `~texfigure.Figure`
        """
        default_kwargs = {'placement': self.subfig_placement,
                          'width': self.subfig_width,
                          'caption': self.caption,
                          'label': self.label}

        myfig = self.extension_mapping[self.extension]()

        return self.subfig_str.format(myfig=myfig, **default_kwargs)

    def _repr_latex_(self):
        return self.repr_figure()


class MultiFigure(Sequence):
    r"""
    A Multifigure is a container object for building subfigures from
    `texfigure.Figure` classes.

    Parameters
    ----------

    nrows : `int`
        Number of rows for the MultiFigure.

    ncols : `int`
        Number of columns for the MultiFigure.


    Attributes
    ----------

    figures : `numpy.ndarray`
        Array holding `texfigure.Figure` objects, has a shape of (nrows, ncols).

    caption : `str`
        The caption to use when representing the figure.
        (Default ``Figure reference``)

    label : `str`
        The latex label assigned to the figure envrionment.
        (Default ``fig:reference``)

    placement : `str`
        The figure envrionment placement value. (Default ``h``)

    frontmatter : `str`
        LaTeX code included in the first line of the figure environment.
        (Default ``\centering``)

    Examples
    --------

    .. code-block:: latex

        \begin{pycode}

        muti = texfigure.MultiFigure(1,2)

        X = [[5,6], [7,8]]
        Y = [[1,2], [3,4]]

        for x,y in zip(X,Y):
            fig = plt.figure()
            plt.plot(x, y, 'o')

            Fig1 = texfigure.Figure(fig)
            multi.append(Fig)
        \end{pycode}

        \py|multi|

    """

    fig_str = r"""
\begin{{figure*}}
    {frontmatter}
    {myfig}
    \caption{{{caption}}}
    \label{{{label}}}
\end{{figure*}}
"""

    def __init__(self, nrows, ncols, reference='', continuation=False):
        self.nrows = nrows
        self.ncols = ncols
        self.reference = reference

        self.caption = "MultiFigure {}".format(self.reference)
        self.label = "fig:{}".format(self.reference)
        self.placement = 'H'
        self.frontmatter = '\centering'
        if continuation:
            self.frontmatter += '\n' + r'\ContinuedFloat'

        self.figures = np.zeros([nrows, ncols], dtype=object)
        self.figures[:] = None

    def __len__(self):
        return self.figures.size()

# TODO: This is not really felxible enough. It dosen't work when ncols > 1.
# It should probably be a method which can split it into x vertical chunks.
    def __getitem__(self, key):
        """
        Return a continuation when indexed, unless indexed for a single figure,
        when we return the `texfigure.Figure` instance.
        """
        if isinstance(key, int):
            return self.figures.flat[key]

        elif isinstance(key, slice):
            # If this is the start of the list then it's not a cont.
            if key.start is None or key.start == 0:
                continuation = False
                new_ref = self.reference
            else:
                continuation = True
                new_ref = self.reference + "-c"

            new_figures = self.figures[key]
            new_mf = MultiFigure(*new_figures.shape, reference=new_ref,
                                 continuation=continuation)
            new_mf.figures = new_figures

            # If we are at the end then add the caption
            if key.stop is None or key.stop == self.figures.size:
                new_mf.caption = self.caption
            else:
                new_mf.caption = ''
            return new_mf

        else:
            raise KeyError("MultiFigure only supports 1D indexing.")

    def append(self, figure):
        """
        Add a `texfigure.Figure` object to the next empty slot in the
        `~texfigure.MultiFigure`.
        """
        if not isinstance(figure, Figure):
            raise TypeError("Only texfigure.Figures can be"
                            " appended to a MultiFigure")

        empties = np.logical_not(self.figures.flat).nonzero()[0]

        if len(empties):
            self.figures.flat[empties[0]] = figure
        else:
            raise ValueError("This MultiFigure is full")

    def _repr_latex_(self):
        default_kwargs = {'placement': self.placement,
                          'caption': self.caption,
                          'label': self.label,
                          'frontmatter': self.frontmatter}

        subfigures = ""

        for i, fig in enumerate(self.figures.flat):
            if fig:
                if i % self.ncols == 0:
                    subfigures += '\n'
                subfigures += fig.repr_subfigure()

        return self.fig_str.format(myfig=subfigures, **default_kwargs)


class Manager(object):
    """
    A class holding information about different figures and data.

    Parameters
    ----------

    pytex : ``PythonTeXUtils`` instance.
        The pytex object from the PythonTeX session.

    number : `int`
        Numerical index for this chapter.

    base_path : `str`
        Path to the base directory for all files for this manager.

    python_dir : `bool` or `str`
        Path to a directory containing Python code to be added to the Python
        path.


    Attributes
    ----------

    savefig_functions : `dict`
        A mapping between figure types and functions to save them to a given
        filename. Functions in the mapping must accept two arguments, the
        figure object and a filename, the function must return the filename
        as saved to disk.

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

        self.savefigure_functions = {matplotlib.figure.Figure:
                                     self._save_mpl_figure}

        if HAVE_MAYAVI:
            self.savefigure_functions[mayavi.core.scene.Scene] = self._save_mayavi_figure

        if HAVE_YT:
            self.savefigure_functions[yt.visualization.plot_container.ImagePlotContainer] = self._save_yt_ipc

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
        data_dir is set to a `str` then that dir will be used.
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
        fig_dir is set to a `str` then that dir will be used.
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
        python_dir is set to a `str` then that dir will be used.

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
        file_name : `str`
            The filename in the data directory
        """

        fname = os.path.join(self.data_dir, file_name)
        self.pytex.add_dependencies(fname)

        return fname

    def make_figure_filename(self, ref, fname=None, fext='', fullpath=False):
        """
        Return the standard template figure name with number.

        Parameters
        ----------
        ref : `str`
            The latex reference for this figure (excluding 'fig:')
        fname : `str`
            Overwrite the default file name template with this name.

        Returns
        -------
        fname : `str`
            The file name
        """
        if not fname:
            fname = 'Chapter{}-Figure{}-{}{}'.format(self.number,
                                                     self.fig_count,
                                                     ref, fext)

        if fullpath:
            fname = os.path.join(self.fig_dir, fname)

        return fname

    def _save_mpl_figure(self, fig, filename, **kwargs):
        """
        A wrapper to save a matplotlib figure object to a file.
        """

        fig.savefig(filename)

        return filename

    def _save_mayavi_figure(self, fig, filename, azimuth=153, elevation=62,
                            distance=400, focalpoint=[25., 63., 60.], aa=16,
                            size=(1024, 1024)):
        """
        A wrapper to save a mayavi figure object
        """
        scene = fig.scene

        scene.anti_aliasing_frames = aa

        mlab.view(azimuth=azimuth, elevation=elevation, distance=distance,
                  focalpoint=focalpoint)

        scene.save(filename, size=size)

        return filename

    def _save_yt_ipc(self, slc, filename, **kwargs):
        if len(slc.plots) != 1:
            raise NotImplementedError("Can't currently handle a container with"
                                      " more than one plot!")

        fname, suffix = os.path.splitext(filename)
        filename, = slc.save(fname, suffix=suffix[1:], **kwargs)

        return filename

    def add_figure(self, ref, Fig):
        """
        Add the figure to the tracked files and increment the figure count.

        Parameters
        ----------
        ref : `str`
            The latex reference for this figure (excluding 'fig:')

        Fig : `texfigure.Figure`
            The `~texfigure.Figure` object to add to the manager.
        """

        self.pytex.add_created(Fig.file_name)

        self._figure_registry[ref] = {'number': self.fig_count, 'Figure': Fig}
        self.fig_count += 1

    def save_figure(self, ref, fig=None, fname=None, fext='.pdf', **kwargs):
        """
        Save a figure to a file, and track it using this manager object.

        Parameters
        ----------

        ref : `str`
            A `str` to use as a key inside this manager, and to add to the
            filename and to use a the latex reference.

        fig : object
            A figure object of a type that has an entry in the
            `~texfigure.Manager.savefig_functions` dictionary. If None it will
            be assumed that the current ``pyplot`` figure is to be used and
            `~matplotlib.pyplot.gcf` will be called.

        fname : `str`
            The file name to be used, not including the extension or the path.

        fext : `str`
            The file extension to be used to save the file.

        kwargs : `dict`
            Other keyword arguments are passed onto the save figure function.

        Returns
        -------

        Fig : `texfigure.Figure`
            The `~texfigure.Figure` object added to this `~texfigure.Manager`.
        """

        if fig is None:
            fig = plt.gcf()

        fname = self.make_figure_filename(ref, fname=fname, fext=fext,
                                          fullpath=True)

        for atype in self.savefigure_functions.keys():
            if issubclass(type(fig), atype):
                fname = self.savefigure_functions[atype](fig, fname, **kwargs)

        Fig = Figure(fname, reference=ref)

        self.add_figure(ref, Fig)

        return Fig

    def get_figure(self, ref):
        """
        Get the filename of a figure that has already been saved

        Parameters
        ----------
        ref : `str`
            The Figure reference

        Returns
        -------
        fname : `str`
            The filename
        """

        return self._figure_registry[ref]['Figure']

    def get_multifigure(self, nrows, ncols, refs, reference=''):
        """
        Return a `texfigure.MultiFigure` object made up of a set
        of figure references stored in this `~texfigure.Manager` instance.

        Parameters
        ----------

        nrows : `int`
            Number of rows for the MultiFigure.

        ncols : `int`
            Number of columns for the MultiFigure.

        refs : `list`
            A list of figure references no more than nrows * ncols long.

        reference : `str`
            The reference for the `texfigure.MultiFigure` object.

        Returns
        -------

        multfigure : `texfigure.MultiFigure`
            The initilised and populated multifigure object.

        """

        if len(refs) > nrows * ncols:
            raise ValueError("You can not specify more references than number "
                             "of spaces in your multifigure grid.")

        mf = MultiFigure(nrows, ncols, reference=reference)

        for ref in refs:
            lfig = self.get_figure(ref)
            mf.append(lfig)

        return mf
