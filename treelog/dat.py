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

import os, contextlib, functools
from . import abc, _io

class DataLog(abc.Log):
  '''Output only data.'''

  def __init__(self, dirpath=os.curdir, names=_io.sequence):
    self._names = functools.lru_cache(maxsize=32)(names)
    self._dir = _io.directory(dirpath)

  @contextlib.contextmanager
  def open(self, filename, mode, level, id):
    f = None
    try:
      if id is None:
        f, fname = self._dir.temp(mode, name=filename)
      else:
        self._dir.mkdir('.id')
        fname = os.path.join('.id', id.hex())
        f = self._dir.open(fname, mode, name=filename)
      with f:
        yield f
    except:
      if f:
        self._dir.unlink(fname)
      raise
    for realname in self._names(filename):
      if self._dir.link(fname, realname):
        break
    if id is None:
      self._dir.unlink(fname)

  def pushcontext(self, title):
    pass

  def popcontext(self):
    pass

  def write(self, text, level):
    pass
