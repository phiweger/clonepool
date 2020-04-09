from setuptools import setup

setup(
    name='clonepool',
    version='0.1',
    entry_points='''
        [console_scripts]
        clonepool=clonepool.__main__:cli
    ''',
)
