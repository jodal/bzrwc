bzrwc
=====

What is bzrwc?
--------------

bzrwc is a Django_ application which uses the `Cairo`_ to graph
various data about Bazaar_ repositories, like lines of code over time.

.. _Django: http://www.djangoproject.com/
.. _Bazaar: http://bazaar-vcs.org/
.. _Cairo: http://cairographics.org/


Credits
-------

bzrwc was originally created by Stein Magnus Jodal <stein.magnus@jodal.no>.
Continued delevelopment by Thomas Kongevold Adamcik <thomas@adamcik.no>.


License
-------

bzrwc is licensed under the GNU General Public License version 2. See COPYING
for the full license.


Dependencies
------------

As Debian/Ubuntu package names:

* python-django >= 1.0
* bzrlib (bundled with bzr)
* python-cairo


Installation
------------

1. Execute `python setup.py install` or put the `bzrwc` directory on your
   PYTHONPATH manually.
2. Add `bzrwc` to `INSTALLED_APPS` in your Django project settings.
3. Add bzrwc to your main `urls.py`, i.e. like the following:

.. sourcecode:: python

    urlpatterns += patterns('',
        (r'^bzrwc/', include('bzrwc.urls')),
    )


Usage
-----

1. Setup reposities and graphs using the Django admin.
2. Go to the bzrwc URL to view the graphs.


TODO
----

* Speedups, i.e. more caching.


Further documentation
---------------------

* http://bazaar-vcs.org/BzrLib
* http://cairographics.org/manual/
* http://www.tortall.net/mu/wiki/CairoTutorial
* Use the force, read the source.

