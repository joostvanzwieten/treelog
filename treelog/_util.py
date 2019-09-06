import sys, os, re, fnmatch, argparse, urllib.request, functools, hashlib

def fetch():
  parser = argparse.ArgumentParser()
  parser.add_argument('uri')
  parser.add_argument('pattern', nargs='?', default='*')
  parser.add_argument('-0', '--numberfirst', action='store_true', help='add -0 suffix to first item in sequence')
  args = parser.parse_args()

  opener = urllib.request.urlopen if '://' in args.uri else functools.partial(open, mode='rb')
  anchor = re.compile(r'<a href="([0-9a-f]{40})([.][^"]+)" download="([^"]+\2)">\3</a>')
  hashes = _group((filename, hash) for hash, ext, filename in anchor.findall(_read(args.uri, opener).decode()))
  filtered = fnmatch.filter(hashes, args.pattern)
  if not filtered:
    sys.exit('no matching files.')

  copy = []
  status = []
  for filename in sorted(filtered):
    count = [0, 0]
    for i, hash in enumerate(hashes[filename]):
      dst = '-{}'.format(i).join(os.path.splitext(filename)) if i or args.numberfirst else filename
      new = not os.path.exists(dst)
      if new:
        copy.append((hash, dst))
      elif hash != _sha1(dst):
        sys.exit('error: file exists: {}'.format(dst))
      count[new] += 1
    status.append(filename + ': ' + ', '.join(['{} present', '{} new'][i].format(n) for i, n in enumerate(count) if n))
  _print2(status)
  for hash, dst in copy:
    print(hash, '->', dst)
    src = os.path.join(os.path.dirname(args.uri), hash + os.path.splitext(dst)[1])
    with opener(src) as fin, open(dst, 'wb') as fout:
      fout.write(fin.read())
  print('done.')

def gc():
  parser = argparse.ArgumentParser()
  parser.add_argument('-y', '--yes', action='store_true', help='answer yes to all questions')
  args = parser.parse_args()

  listdir = os.listdir(os.curdir)
  pattern = re.compile(r'\b[0-9a-f]{40}[.].+?\b')
  refs = {hash for item in listdir if item.endswith('.html') for hash in pattern.findall(_read(item))}
  garbage = [item for item in listdir if pattern.match(item) and item not in refs]
  if garbage:
    _print2(garbage)
    _confirm('remove {} unreferenced items?'.format(len(garbage)), auto=args.yes)
    for item in garbage:
      os.unlink(item)
  print('no unreferenced items.')

def _sha1(path):
  with open(path, 'rb') as f:
    return hashlib.sha1(f.read()).hexdigest()

def _read(name, open=open):
  print('scanning', name)
  try:
    with open(name) as f:
      return f.read()
  except Exception as e:
    sys.exit('error: {}'.format(e))

def _group(items):
  group = {}
  for key, value in items:
    group.setdefault(key, []).append(value)
  return group

def _print2(items):
  n, k = divmod(len(items), 2)
  L = max(map(len, items[:n+k]))
  for i in range(n):
    print(items[i].ljust(L+1), items[i-n])
  if k:
    print(items[n])

def _confirm(question, auto=False):
  if auto:
    print(question, 'yes')
  elif input(question + ' yes/[no] ') != 'yes':
    sys.exit('aborted.')
