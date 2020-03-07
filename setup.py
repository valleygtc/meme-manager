from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='meme-manager',
    version='0.1.0',
    description='A meme manager with web UI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/valleygtc/meme-manager',
    author='gutianci',
    author_email='gutianci@qq.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Desktop Environment',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "Operating System :: OS Independent",
    ],

    keywords='application web',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.7',
    install_requires=['flask', 'flask-sqlalchemy', 'waitress'],
    # extras_require={  # Optional
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # setuptools not support "**" rescursive include sub directory. so I have to specify every sub dir.
    # ref: https://github.com/pypa/setuptools/issues/1806
    package_data={
        'meme_manager': ['frontend/*', 'frontend/static/css/*', 'frontend/static/js/*'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    #
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],  # Optional

    entry_points={
        'console_scripts': [
            'meme-manager=meme_manager:cli',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/valleygtc/meme-manager/issues',
        'Source': 'https://github.com/valleygtc/meme-manager/',
    },
)
