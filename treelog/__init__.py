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

version = '1.0b4'

import sys, functools, contextlib

from ._base import Log
from ._forward import TeeLog, FilterLog
from ._silent import NullLog, DataLog, RecordLog
from ._text import StdoutLog, RichOutputLog, LoggingLog
from ._html import HtmlLog

current = FilterLog(TeeLog(StdoutLog(), DataLog()), minlevel=1)

@contextlib.contextmanager
def set(logger):
  '''Set logger as current.'''

  global current
  old = current
  try:
    current = logger
    yield logger
  finally:
    current = old

def add(logger):
  '''Add logger to current.'''

  return set(TeeLog(current, logger))

def disable():
  '''Disable logger.'''

  return set(NullLog())

@contextlib.contextmanager
def context(*args, sep=' '):
  current.pushcontext(sep.join(map(str, args)))
  try:
    yield
  finally:
    current.popcontext()

def withcontext(f):
  '''Decorator; executes the wrapped function in its own logging context.'''

  @functools.wraps(f)
  def wrapped(*args, **kwargs):
    with context(f.__name__):
      return f(*args, **kwargs)
  return wrapped

def _print(level, *args, sep=' '):
  '''Write message to log.

  Args
  ----
  *args : tuple of :class:`str`
      Values to be printed to the log.
  sep : :class:`str`
      String inserted between values, default a space.
  '''
  current.write(sep.join(map(str, args)), level)

@contextlib.contextmanager
def _file(level, name, mode, *, id=None):
  '''Open file in logger-controlled directory.

  Args
  ----
  filename : :class:`str`
  mode : :class:`str`
      Should be either ``'w'`` (text) or ``'wb'`` (binary data).
  id :
      Bytes identifier that can be used to decide a priori that a file has
      already been constructed. Default: None.
  '''
  with current.open(name, mode, level, id) as f, context(name):
    yield f

debug, info, user, warning, error = [functools.partial(_print, level) for level in range(5)]
debugfile, infofile, userfile, warningfile, errorfile = [functools.partial(_file, level) for level in range(5)]

del _print, _file

# vim:sw=2:sts=2:et
