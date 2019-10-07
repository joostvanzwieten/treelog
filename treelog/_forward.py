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

import contextlib, typing, typing_extensions, tempfile, warnings
from . import proto, _io

class TeeLog:
  '''Forward messages to two underlying loggers.'''

  def __init__(self, baselog1: proto.Log, baselog2: proto.Log) -> None:
    self._baselog1 = baselog1
    self._baselog2 = baselog2

  def pushcontext(self, title: str) -> None:
    self._baselog1.pushcontext(title)
    self._baselog2.pushcontext(title)

  def popcontext(self) -> None:
    self._baselog1.popcontext()
    self._baselog2.popcontext()

  def recontext(self, title: str) -> None:
    self._baselog1.recontext(title)
    self._baselog2.recontext(title)

  def write(self, text: str, level: proto.Level) -> None:
    self._baselog1.write(text, level)
    self._baselog2.write(text, level)

  @contextlib.contextmanager
  def open(self, filename: str, mode: str, level: proto.Level) -> typing.Generator[proto.IO[typing.Any], None, None]:
    with self._baselog1.open(filename, mode, level) as f1, self._baselog2.open(filename, mode, level) as f2:
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
        with tempfile.TemporaryFile(mode+'+') as tmp:
          yield tmp
          tmp.seek(0)
          data = tmp.read()
        f1.write(data)
        f2.write(data)

class FilterLog:
  '''Filter messages based on level.'''

  def __init__(self, baselog: proto.Log, minlevel: typing.Union[proto.Level, int]) -> None:
    self._baselog = baselog
    if isinstance(minlevel, int):
      warnings.warn('minlevel of type "int" is deprecated, use "proto.Level" instead', DeprecationWarning)
      self._minlevel = tuple(proto.Level)[minlevel] # type: proto.Level
    else:
      self._minlevel = minlevel

  def pushcontext(self, title: str) -> None:
    self._baselog.pushcontext(title)

  def popcontext(self) -> None:
    self._baselog.popcontext()

  def recontext(self, title: str) -> None:
    self._baselog.recontext(title)

  def write(self, text: str, level: proto.Level) -> None:
    if level.value >= self._minlevel.value:
      self._baselog.write(text, level)

  def open(self, filename: str, mode: str, level: proto.Level) -> typing_extensions.ContextManager[proto.IO[typing.Any]]:
    return self._baselog.open(filename, mode, level) if level.value >= self._minlevel.value else _io.devnull()

# vim:sw=2:sts=2:et
