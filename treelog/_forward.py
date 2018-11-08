# Copyright (c) 2018 Evalf
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import contextlib
from . import _base, _io

class TeeLog(_base.Log):
  '''Forward messages to two underlying loggers.'''

  def __init__(self, baselog1, baselog2):
    self._baselog1 = baselog1
    self._baselog2 = baselog2

  def pushcontext(self, title):
    self._baselog1.pushcontext(title)
    self._baselog2.pushcontext(title)

  def popcontext(self):
    self._baselog1.popcontext()
    self._baselog2.popcontext()

  def write(self, text, level):
    self._baselog1.write(text, level)
    self._baselog2.write(text, level)

  @contextlib.contextmanager
  def open(self, filename, mode, level, id):
    with self._baselog1.open(filename, mode, level, id) as f1, self._baselog2.open(filename, mode, level, id) as f2:
      if not f1:
        yield f2
      elif not f2:
        yield f1
      elif f2.seekable() and f2.readable():
        yield f2
        f2.seek(0)
        f1.write(f2.read())
      elif f1.seekable() and f1.readable():
        yield f1
        f1.seek(0)
        f2.write(f1.read())
      else:
        with _io.tempfile(filename, mode) as tmp:
          yield tmp
          tmp.seek(0)
          data = tmp.read()
        f1.write(data)
        f2.write(data)

class FilterLog(_base.Log):
  '''Filter messages based on level.'''

  def __init__(self, baselog, minlevel):
    self._baselog = baselog
    self._minlevel = minlevel

  def pushcontext(self, title):
    return self._baselog.pushcontext(title)

  def popcontext(self):
    return self._baselog.popcontext()

  def write(self, text, level):
    if level >= self._minlevel:
      self._baselog.write(text, level)

  def open(self, filename, mode, level, id):
    return self._baselog.open(filename, mode, level, id) if level >= self._minlevel else _io.devnull(filename)

# vim:sw=2:sts=2:et
