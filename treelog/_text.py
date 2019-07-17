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

import contextlib, logging, sys
from . import _base, _io

class ContextLog(_base.Log):
  '''Base class for loggers that keep track of the current list of contexts.

  The base class implements :meth:`context` and :meth:`open` which keep the
  attribute :attr:`currentcontext` up-to-date.

  .. attribute:: currentcontext

     A :class:`list` of contexts (:class:`str`\\s) that are currently active.
  '''

  def __init__(self):
    self.currentcontext = []

  def pushcontext(self, title):
    self.currentcontext.append(title)
    self.contextchangedhook()

  def popcontext(self):
    self.currentcontext.pop()
    self.contextchangedhook()

  def recontext(self, title):
    self.currentcontext[-1] = title
    self.contextchangedhook()

  def contextchangedhook(self):
    pass

  @contextlib.contextmanager
  def open(self, filename, mode, level, id):
    with self.context(filename), _io.devnull(filename) as f:
      yield f
    self.write(filename, level=level)

class StdoutLog(ContextLog):
  '''Output plain text to stream.'''

  def write(self, text, level):
    print(*self.currentcontext, text, sep=' > ')

class RichOutputLog(ContextLog):
  '''Output rich (colored,unicode) text to stream.'''

  def __init__(self):
    super().__init__()
    self._current = '' # currently printed context
    _io.set_ansi_console()

  def contextchangedhook(self):
    _current = ''.join(item + ' > ' for item in self.currentcontext)
    if _current == self._current:
      return
    n = _first(c1 != c2 for c1, c2 in zip(_current, self._current))
    items = []
    if n == 0:
      items.append('\r')
    elif n < len(self._current):
      items.append('\033[{}D'.format(len(self._current)-n))
    if n < len(_current):
      items.extend(['\033[1;30m', _current[n:], '\033[0m'])
    if len(_current) < len(self._current):
      items.append('\033[K')
    sys.stdout.write(''.join(items))
    if n:
      sys.stdout.flush()
    self._current = _current

  def write(self, text, level):
    items = []
    if level == 4: # error
      items.append('\033[1;31m') # bold red
    elif level == 3: # warning
      items.append('\033[0;31m') # red
    elif level == 2: # user
      items.append('\033[1;34m') # bold blue
    items.extend([text, '\n'])
    if self.currentcontext:
      items.extend(['\033[1;30m', self._current])
    items.append('\033[0m')
    sys.stdout.write(''.join(items))

class LoggingLog(ContextLog):
  '''Log to Python's built-in logging facility.'''

  _levels = logging.DEBUG, logging.INFO, 25, logging.WARNING, logging.ERROR

  def __init__(self, name='nutils'):
    self._logger = logging.getLogger(name)
    super().__init__()

  def write(self, text, level):
    self._logger.log(self._levels[level], ' > '.join((*self.currentcontext, text)))

def _first(items):
  'return index of first truthy item, or len(items) of all items are falsy'
  i = 0
  for item in items:
    if item:
      break
    i += 1
  return i
