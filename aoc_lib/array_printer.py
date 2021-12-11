# usage:
#
# import sys
# from pathlib import Path
# sys.path.append(str(Path('.').resolve().parents[1]))
# from aoc_lib import array_printer

import numpy as np
import html
html_formatter = get_ipython().display_formatter.formatters['text/html']

def ndarray_to_html(a):
    return "<pre>{}</pre>".format(html.escape(str(a)))

html_formatter.for_type(np.ndarray, ndarray_to_html)
