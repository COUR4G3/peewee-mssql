Peewee
######
A database driver to add Microsoft SQL Server and Azure support using
`pymssql <http://pymssql.org>`_ and `FreeTDS <http://freetds.org>`_ in
Peewee and should run on most Unix-like systems, Microsoft Windows and Mac OS X.

In it's current state you should be able to access data and possibly do certain
updates. You will not be able to create tables or introspect existing databases,
so you will have to write your models manually. Offsets will also not work,
since the query compiler will need some significant rewrite to support TSQL
dialect, however limit will work (TOP).

Installation
============
Install the latest stable release from Pypi:

    pip install peewee-mssql

Or alternatively, select a release or development version from Github and run:

    python setup.py install

Getting Started
===============
For help on installing and configuring `FreeTDS <http://freetds.org>`_ I
recommend taking a look at the
`guide <http://pymssql.org/en/latest/freetds.html>`_ in the
`pymssql <http://www.pymssql.org>`_ documentation.

And then you should be able to instantiate a database as below and start
building your models for accessing data:

.. code-block:: python

    from peewee_mssql import MssqlDatabase

    db = MssqlDatabase('MyDatabase', host='host.example.com', user=r'domain\username', password='password')

If you are using Microsoft SQL Server 2005 you will need to use the legacy
datetime data types, simple pass `use_legacy_datetime=True` to the
database driver when initializing.
