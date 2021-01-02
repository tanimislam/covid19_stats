from setuptools import setup, find_packages

#
## ones that live on PyPI
reqs = sorted(set(map(lambda line: line.strip(),
                      filter(lambda line: len( line.strip( ) ) != 0 and not line.strip( ).startswith('git+'),
                             open( 'requirements.txt', 'r').readlines()))))

#
## git+https modules
dependency_links = sorted(set(map(lambda line: line.strip( ),
                                  filter(lambda line: line.strip( ).startswith('git+'),
                                         open( 'requirements.txt', 'r' ).readlines( ) ) ) ) )
setup(
    name = 'covid19_stats',
    version = '1.0',
    #
    ## following advice on find_packages excluding tests from https://setuptools.readthedocs.io/en/latest/setuptools.html#using-find-packages
    packages = find_packages( exclude = ["*.tests", "*.tests.*", "tests" ] ),
    url = 'https://github.com/tanimislam/covid19_stats',
    license = 'BSD-2-Clause',
    author = 'Tanim Islam',
    author_email = 'tanim.islam@gmail.com',
    description = "This is my COVID-19 tracker, which is a front-end to the NY Times's database of COVID-19 cases.",
    #
    ## classification: where in package space does "covid19_stats live"?
    ## follow (poorly) advice I infer from https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-setup-script
    classifiers=[
    # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Programming Language :: Python :: 3',
    # uncomment if you test on these interpreters:
    # 'Programming Language :: Python :: Implementation :: IronPython',
    # 'Programming Language :: Python :: Implementation :: Jython',
    # 'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Utilities',
    ],
    #
    ## requirements
    install_requires = reqs,
    dependency_links = dependency_links,
    python_requires = '>=3.5',
    #
    ## the executables I am creating
    entry_points = {
        'console_scripts' : [
            'covid19_create_movie_or_summary = covid19_stats.cli.covid19_create_movie_or_summary:main',
            'covid19_state_summary = covid19_stats.cli.covid19_state_summary:main',
            'covid19_update_database = covid19_stats.cli.covid19_update_database:main',
            'covid19_movie_updates = covid19_stats.cli.covid19_movie_updates:main',
        ]
    },
    #
    ## here is the link to the terrible undocumented documentation: https://setuptools.readthedocs.io/en/latest/setuptools.html#including-data-files
    package_data = {
        "covid19_stats" : [ "resources/*" ]
        }
)
