Figure Manager
==============

The `~texfigure.Manager` class is the primary component of texfigure, it makes it easier to
generate and work with figures generated in PythonTeX code blocks from within a
LaTeX document.

A figure manager does a number of things:

1. Tracks data files in a given directory.
1. Adds python files in a given directory to the Python Path.
1. Saves figures from any know figure type.
1. Tracks figures allowing them to be recalled later.
1. Returns MultiFigure objects containing any number of already tracked Figures.

The purpose of a `~texfigure.Manager` object is to deal with the paths to your
data, code and figures so that you don't have to. It also abstracts away the
saving of the figures for you so that you can pass any known figure object to
the `~texfigure.Manager` and it will save it in the correct directory and return
you a `texfigure.Figure` object.


Using a Figure Manager
----------------------

There are a few ways to use a `~texfigure.Manager` instance, you can either use it as a quick way to save figures and generate `~texfigure.Figure` objects. Or you can use it as a store for all the figures generated using the `~texfigure.Manager`, saving the figures using the `~texfigure.Manager` and then latter recalling them using their reference and including them in your document.

You can generate a `~texfigure.Figure` object using the `texfigure.Manager.save_figure` function:

.. code-block:: latex

   \begin{pycode}
   manager = texfigure.Manager(pytex, './')
   \end{pycode}

   This is my document, spam eggs, eggs and spam.

   \begin{pycode}
   fig, ax = plt.subplots()
   ax.plot([0,1], [0,1], 'o')

   Fig = manager.save_figure(fig, "plot1")
   \end{pycode}

   \py|Fig|



Alternatively, you can use the `~texfigure.Manager.get_figure` method to request the `~texfigure.Figure` object at a later date. This method is normally more useful in more complex situations than the example below:

.. code-block:: latex

   \begin{pycode}
   manager = texfigure.Manager(pytex, './')
   \end{pycode}

   This is my document, spam eggs, eggs and spam.

   \begin{pycode}
   fig, ax = plt.subplots()
   ax.plot([0,1], [0,1], 'o')

   manager.save_figure(fig, "plot1")
   \end{pycode}

   \py|manager.get_figure("plot1")|


Figure Types
------------

`~texfigure.Manager` can save three different types of figure objects.

1. `matplotlib.figure.Figure`.
1. `yt.visualization.plot_container.ImagePlotContainer`.
1. `mayavi.core.scene.Scene`.

This means you can pass any of these three objects (or their subclasses) to
`texfigure.Manager.save_figure` and it will save them to the provided
``figure_dir`` and generate a `~texfigure.Figure` object to add to the registry.

You can register save functions with the `~texfigure.Manager` to save custom plot types, the function given to the manager has to have the following signature::

  def myfigure_handler(fig, filename, **kwargs):
      fig.save(filename)
      return filename


You can then register the function with the `~texfigure.Manager`::

  mymanager = texfigure.Manager(pytex, './')
  mymanager.savefigure_functions[MyFigureClass] = myfigure_handler

If you have another plotting library that you would like texfigure to support, you can add support for your figure type into texfigure and submit a PR.

