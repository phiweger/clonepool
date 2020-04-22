import os

# Import API.
from clonepool.clonepool import layout, simulate, resolve

# https://docs.pytest.org/en/latest/goodpractices.html
name = 'clonepool'


# stackoverflow.com/questions/4519127
# _ROOT = os.path.abspath(os.path.dirname(__file__))
# def get_data(path):
#     return os.path.join(_ROOT, 'data', path)
