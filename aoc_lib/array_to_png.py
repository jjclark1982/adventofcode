# usage:
#
# import sys
# from pathlib import Path
# sys.path.append(str(Path('.').resolve().parents[1]))
# from aoc_lib import array_to_png

import PIL.Image
from io import BytesIO
import IPython.display
import numpy as np
import html
html_formatter = get_ipython().display_formatter.formatters['text/html']

def int_array_to_image(a, fmt='png'):
    a = 240 - (a/(a.max() or 1) * 224).astype(np.uint8)
    f = BytesIO()
    PIL.Image.fromarray(a).save(f, fmt)
    return IPython.display.Image(data=f.getvalue())

def double_bitmap(a):
    (h, w) = a.shape
    return np.tile(a.reshape((-1, 1)), 2).reshape((h, w*2))

def quad_bitmap(a):
    return double_bitmap(double_bitmap(a).T).T

def ndarray_to_html(a):
    if len(a.shape) == 2 and a.min() >= 0:
        while a.size < 1024:
            a = quad_bitmap(a)

        for bundle in int_array_to_image(a)._repr_mimebundle_():
            for mimetype, b64value in bundle.items():
                if mimetype.startswith('image/'):
                    src = f'data:{mimetype};base64,{b64value}'
                    return f'<img src="{src}">'
    else:
        return "<pre>{}</pre>".format(html.escape(repr(a)))

html_formatter.for_type(np.ndarray, ndarray_to_html)

def item_to_html(item):
    formatter = html_formatter.for_type(type(item))
    if callable(formatter):
        item = formatter(item)

    if callable(getattr(item, '_repr_mimebundle_', None)):
        for bundle in item._repr_mimebundle_():
            for mimetype, b64value in bundle.items():
                if mimetype.startswith('image/'):
                    src = f'data:{mimetype};base64,{b64value}'
                    return f'<img src={src}>'
    
    if not formatter:
        item = '<tt>{}</tt>'.format(html.escape(repr(item)))
    return f'<span style="margin-left:0.2em">{item}</span>'

def list_to_html(l):
    items = [item_to_html(item) for item in l]
    return '<tt style="display:flex;flex-wrap:wrap;align-items:center">[{}]</tt>'.format(', '.join(items))

html_formatter.for_type(list, list_to_html)

def tuple_to_html(l):
    items = (item_to_html(item) for item in l)
    return '<tt style="display:flex;flex-wrap:wrap;align-items:center">({})</tt>'.format(', '.join(items))

html_formatter.for_type(tuple, tuple_to_html)

["Text", np.array([[1,2],[3,4]]), np.eye(10), [(i, np.random.randint(0,2,(10,10))) for i in range(1,4)]]
