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

  class Thread:
    def __init__(self, context, interval):
      import _thread
      self._context = context
      self._alive = True
      self._uptodate = True
      self._lock = _thread.allocate_lock() # to be acquired by run, released by main thread
      _thread.start_new_thread(self.run, (interval,))
    def release_lock(self):
      if self._lock.locked():
        self._lock.release()
    def signal_stop(self):
      self._alive = False
      self._uptodate = False
      self.release_lock()
    def signal_contextchange(self):
      if self._uptodate:
        self._uptodate = False
        self.release_lock()
    def print_context(self):
      sys.stdout.write('\033[K\033[1;30m' + ' · '.join(self._context) + '\033[0m\r' if self._context else '\033[K\r')
      self._uptodate = True
    def run(self, interval):
      try:
        while self._alive:
          if not self._lock.acquire(timeout=-1 if self._uptodate else interval):
            # acquire timed out, implies _uptodate == False
            self.print_context()
      except Exception as e:
        sys.stdout.write('\033[Kcontext thread died unexpectedly: {}\n'.format(e))

  def __init__(self, interval=.1):
    super().__init__()
    _io.set_ansi_console()
    self._thread = self.Thread(self._context, interval)

  def pushcontext(self, title):
    super().pushcontext(title)
    self._thread.signal_contextchange()

  def popcontext(self):
    super().popcontext()
    self._thread.signal_contextchange()

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
    self._thread.print_context()
    self._thread.release_lock()

  def __del__(self):
    if hasattr(self, '_thread'):
      self._thread.signal_stop()

class LoggingLog(ContextLog):
  '''Log to Python's built-in logging facility.'''

  _levels = logging.DEBUG, logging.INFO, 25, logging.WARNING, logging.ERROR

  def __init__(self, name='nutils'):
    self._logger = logging.getLogger(name)
    super().__init__()

  def write(self, text, level):
    self._logger.log(self._levels[level], ' > '.join((*self._context, text)))
