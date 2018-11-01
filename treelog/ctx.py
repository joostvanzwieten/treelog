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
from . import abc, _io

class ContextLog(abc.Log):
  '''Base class for loggers that keep track of the current list of contexts.

  The base class implements :meth:`context` and :meth:`open` which keep the
  attribute :attr:`_context` up-to-date.

  .. attribute:: _context

     A :class:`list` of contexts (:class:`str`\\s) that are currently active.
  '''

  def __init__(self):
    self._context = []

  def pushcontext(self, title):
    self._context.append(title)

  def popcontext(self):
    self._context.pop()

  @contextlib.contextmanager
  def open(self, filename, mode, level, id):
    with self.context(filename), _io.devnull(filename) as f:
      yield f
    self.write(filename, level=level)

class StdoutLog(ContextLog):
  '''Output plain text to stream.'''

  def write(self, text, level):
    print(*self._context, text, sep=' > ')

class RichOutputLog(ContextLog):
  '''Output rich (colored,unicode) text to stream.'''

  def __init__(self, interval=.1):
    import _thread
    super().__init__()
    self._sleep = _thread.allocate_lock() # to be acquired by thread, released by self
    self._state = [True, True] # mutable shared state: [alive, asleep]
    _thread.start_new_thread(self._context_thread, (self._context, self._sleep, self._state, interval))

  @staticmethod
  def _context_thread(context, sleep, state, interval): # pragma: no cover (tested via stdout)
    try:
      while state[0]: # alive
        if not sleep.acquire(timeout=-1 if state[1] else interval): # timed out
          sys.stdout.write('\033[K\033[1;30m' + ' · '.join(context) + '\033[0m\r' if context else '\033[K\r')
          state[1] = True # asleep
    except Exception as e:
      sys.stdout.write('\033[Kcontext thread died unexpectedly: {}\n'.format(e))

  def _trigger_thread(self):
    self._state[1] = False # awake
    if self._sleep.locked():
      self._sleep.release()

  def pushcontext(self, title):
    super().pushcontext(title)
    if self._state[1]: # asleep
      self._trigger_thread()

  def popcontext(self):
    super().popcontext()
    if self._state[1]: # asleep
      self._trigger_thread()

  def write(self, text, level):
    line = '\033[K' # clear line
    if self._context:
      line += '\033[1;30m' + ' · '.join(self._context) + ' · ' # context in gray
    if level == 4: # error
      line += '\033[1;31m' # bold red
    elif level == 3: # warning
      line += '\033[0;31m' # red
    elif level == 2: # user
      line += '\033[1;34m' # bold blue
    elif self._context:
      line += '\033[0m' # reset color
    line += text
    line += '\033[0m\n' # reset and newline
    sys.stdout.write(line)
    self._trigger_thread()

  def __del__(self):
    if hasattr(self, '_state'):
      self._state[0] = False # signal that the thread should stop
      self._trigger_thread()

class LoggingLog(ContextLog):
  '''Log to Python's built-in logging facility.'''

  _levels = logging.DEBUG, logging.INFO, 25, logging.WARNING, logging.ERROR

  def __init__(self, name='nutils'):
    self._logger = logging.getLogger(name)
    super().__init__()

  def write(self, text, level):
    self._logger.log(self._levels[level], ' > '.join((*self._context, text)))
