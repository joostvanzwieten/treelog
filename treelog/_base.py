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

import abc

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

  def recontext(self, title):
    self.popcontext()
    self.pushcontext(title)

  @abc.abstractmethod
  def write(self, text, level):
    raise NotImplementedError

  @abc.abstractmethod
  def open(self, filename, mode, level, id):
    raise NotImplementedError

# vim:sw=2:sts=2:et
