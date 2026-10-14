"""Minimal, byte-preserving gameinfo edit. Python 3.9+. Never installs a mod."""
import argparse, hashlib, json, re
from pathlib import Path

def sha(data): return hashlib.sha256(data).hexdigest()
def inspect(data):
    # Require the known single SearchPaths language entry; reject ambiguous input.
    matches = list(re.finditer(rb'(?m)^([ \t]*)(Game_Language|Game_UILanguage)([ \t]+citadel_\*LANGUAGE\*[^\r\n]*)(\r?\n|$)', data))
    if len(matches) != 1: raise ValueError('Expected exactly one unquoted citadel language entry; review manually')
    m = matches[0]
    prefix = re.sub(rb'//[^\r\n]*', b'', data[:m.start()])
    pos = prefix.rfind(b'SearchPaths')
    if pos < 0 or prefix[pos:].count(b'{')-prefix[pos:].count(b'}') != 1:
        raise ValueError('Language entry is not directly inside SearchPaths; review manually')
    return m

p=argparse.ArgumentParser()
p.add_argument('action',choices=['check','apply','restore'])
p.add_argument('--gameinfo',required=True,type=Path)
p.add_argument('--backup',type=Path)
a=p.parse_args(); data=a.gameinfo.read_bytes()
if a.action=='restore':
    if not a.backup: p.error('--backup is required')
    original=a.backup.read_bytes(); m=inspect(original)
    expected=original[:m.start(2)]+b'Game_UILanguage'+original[m.end(2):]
    if data not in (original,expected): raise SystemExit('REFUSED: gameinfo changed since patch; do not overwrite unrelated edits')
    a.gameinfo.write_bytes(original)
    print(json.dumps({'status':'RESTORED','sha256':sha(original)}));raise SystemExit()
m=inspect(data); fixed=data[:m.start(2)]+b'Game_UILanguage'+data[m.end(2):]
result={'status':'CURRENT' if data==fixed else 'LEGACY','beforeSHA256':sha(data),'afterSHA256':sha(fixed),'runtimeMount':'UNVERIFIED'}
if a.action=='apply' and fixed!=data:
    if not a.backup: p.error('--backup is required')
    if a.backup.resolve()==a.gameinfo.resolve(): raise SystemExit('Backup must differ from gameinfo')
    with a.backup.open('xb') as f: f.write(data)
    a.gameinfo.write_bytes(fixed)
    assert a.gameinfo.read_bytes()==fixed
    result['status']='PATCHED'
print(json.dumps(result,indent=2))
