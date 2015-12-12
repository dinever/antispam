.. title:: Antispam - Spam filter for Python.
.. highlight:: python

Antispam
========

Antispam is a bayesian anti-spam classifier written in Python.

Installation
------------

::

    pip install antispam

Usage
-----

Use the built-in model provided & trained by author::

    import antispam

    antispam.score("Cheap shoes for sale at DSW shoe store!")
    # => 0.9657724517163143

    antispam.is_spam("Cheap shoes for sale at DSW shoe store!")
    # => True

    antispam.score("Hi mark could you please send me a copy of your machine learning homework? thanks")
    # => 0.0008064840568731558

    antispam.is_spam("Hi mark could you please send me a copy of your machine learning homework? thanks")
    # => False

Documentation
-------------

.. toctree::
   :titlesonly:

   api

LICENSE
-------

`MIT License <https://opensource.org/licenses/MIT>`_
