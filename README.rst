Maze solver
===========

Homework solution for course MI-PYT on FIT CTU in Prague.

About maze
==========
There were implemented 5 actor types:

- Accelerator (increases speed with a little less speedup with each succeeded try with probability of 10%,
up to 75% faster than the standard actor speed)

- Scatterbrain (moves in random wrong direction with probability of 20%)
- Speedster (moves 50% faster than the standard actor)
- Teleporter (teleports into random place (not walls and castle) with probability of 20%,
cannot perform teleportation closer than 5 tiles to castle)

- Jumper (jumps through a wall with probability of 20% if a path behind the wall is shorter)

Installation
============

You must install `Cython <http://cython.org/>`__ and `NumPy <http://www.numpy.org/>`__
before doing anything with this module.

Type from the project root ``python -m pip install -r requirements.txt`` in order to install all required dependencies.

Development
===========

Type ``cython -3 --annotate solver.pyx`` in order to annotate source code (add path to filename if needed).

Don't forget to use ``python setup.py develop`` or ``python setup.py build_ext --inplace``
in order to compile Cython code (``.pyx``) during the development process.

Production
==========

You may compile code and run tests by typing:

``python setup.py build_ext -i``

``python -m pytest``

Run the application by ``python -m maze``

Images
======

All images were created by the `Kenney <http://kenney.nl/>`__ studio, and were kindly
released into the Public Domain. They can be downloaded from
`OpenGameArt.org <http://opengameart.org/users/kenney>`__.
