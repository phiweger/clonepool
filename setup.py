# For a template, see:
# https://github.com/pypa/sampleproject/blob/master/setup.py

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='clonepool',
    # license='',         # TODO
    version='0.1',
    description='Efficient sample pooling under varying conditions',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',
    url='https://github.com/phiweger/clonepool',  # Optional
    # author='',  # Optional TODO
    # author_email='',  # Optional TODO
    packages=find_packages(),
    python_requires='>=2.7',

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'click',
        'networkx',
        'numpy',
        'tqdm',
    ],  # Optional

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    # package_data={  # Optional TODO
    #     'sample': ['package_data.dat'],
    # },

    entry_points='''
        [console_scripts]
        clonepool=clonepool.__main__:cli
    ''',

    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    # project_urls={  # Optional
    #     'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
    #     'Funding': 'https://donate.pypi.org',
    #     'Say Thanks!': 'http://saythanks.io/to/example',
    #     'Source': 'https://github.com/pypa/sampleproject/',
    #     'Preprint': 'arxiv.org/bioRxiv etc.'      # TODO
    # },

    classifiers=[
        'Programming Language :: Python :: 3.7',
        # TODO pick license. ID: cf. https://pypi.org/classifiers/
        # 'License :: OSI Approved :: MIT License',
    ],
)
