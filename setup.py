from setuptools import setup

from peewee_mssql import __version__

def long_description():
    descr = open('README.rst', 'r').read()

    try:
        descr += '\n\n' + open('docs/changelog.rst', 'r').read()
    except:
        pass

    return descr

setup(
    name='peewee-mssql',
    version=__version__,
    url='https://github.com/cour4g3/peewee-mssql',
    license='MIT',
    author='Michael de Villiers',
    author_email='twistedcomplexity@gmail.com',
    description='Database driver to add Microsoft SQL Server/Azure support to Peewee',
    long_description=long_description(),
    py_modules=['peewee_mssql'],
    platforms='any',
    install_requires=[
        'peewee',
        'pymssql',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
