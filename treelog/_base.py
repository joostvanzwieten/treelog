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

import abc, contextlib

class Log(abc.ABC):
  '''Abstract base class for log objects.

  A subclass must define a :meth:`context` method that handles a context
  change, a :meth:`write` method that logs a message, and an :meth:`open`
  method that returns a file context.'''

  @abc.abstractmethod
  def pushcontext(self, title):
    raise NotImplementedError

  @abc.abstractmethod
  def popcontext(self):
    raise NotImplementedError

  @abc.abstractmethod
  def write(self, text, level):
    raise NotImplementedError

  @abc.abstractmethod
  def open(self, filename, mode, level, id):
    raise NotImplementedError

  @contextlib.contextmanager
  def context(self, *args, sep=' '):
    self.pushcontext(sep.join(map(str, args)))
    try:
      yield
    finally:
      self.popcontext()

  def _factory(level):

    def print(self, *args, sep=' '):
      '''Write message to log.

      Args
      ----
      *args : tuple of :class:`str`
          Values to be printed to the log.
      sep : :class:`str`
          String inserted between values, default a space.
      '''
      self.write(sep.join(map(str, args)), level)

    def file(self, name, mode, *, id=None):
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
      return self.open(name, mode, level, id)

    name = ['debug', 'info', 'user', 'warning', 'error'][level]
    print.__name__ = name
    print.__qualname__ = 'Log.' + name
    file.__name__ = name + 'file'
    file.__qualname__ = 'Log.' + name + 'file'
    return print, file

  debug,   debugfile   = _factory(0)
  info,    infofile    = _factory(1)
  user,    userfile    = _factory(2)
  warning, warningfile = _factory(3)
  error,   errorfile   = _factory(4)

  del _factory

# vim:sw=2:sts=2:et
