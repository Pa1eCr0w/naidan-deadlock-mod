from pathlib import Path
import struct,zlib,hashlib,json
r=Path('work/body-ult-fix'); b=(r/'baseline.vpk').read_bytes()
assert hashlib.sha256(b).hexdigest()=='b63a8c4b055119ccebfe982abcdd0b6d6b2ceb7558bd9a98b07e27fa6fba9666'
sig,ver,ts,ds,*_=struct.unpack_from('<7I',b); assert sig==0x55aa1234 and ver==2
p=28; files={}
def string():
 global p
 q=b.index(0,p); s=b[p:q].decode();p=q+1;return s
while (ext:=string()):
 while (directory:=string()):
  while (name:=string()):
   crc,pre,arc,off,size,end=struct.unpack_from('<IHHIIH',b,p);p+=18
   assert end==65535 and arc==32767
   data=b[p:p+pre]+b[28+ts+off:28+ts+off+size];p+=pre
   assert zlib.crc32(data)==crc
   path=('/' if directory==' ' else directory+'/')+name+'.'+ext
   files[path.lstrip('/')]=data
assert p==28+ts and files
original=files.copy(); stage={x.relative_to(r/'stage').as_posix():x.read_bytes() for x in (r/'stage').rglob('*') if x.is_file()}
allowed=set(json.loads((r/'allowlist.json').read_text()))
assert len(stage)==len(allowed)
assert set(stage)==allowed,(set(stage)-allowed,allowed-set(stage))
files.update(stage); groups={}
for path,data in sorted(files.items()):
 d,_,n=path.rpartition('/');name,ext=n.rsplit('.',1);groups.setdefault(ext,{}).setdefault(d or ' ',[]).append((name,data))
tree=bytearray();payload=bytearray()
for ext,dirs in sorted(groups.items()):
 tree+=ext.encode()+b'\0'
 for d,entries in sorted(dirs.items()):
  tree+=d.encode()+b'\0'
  for name,data in entries:
   tree+=name.encode()+b'\0'+struct.pack('<IHHIIH',zlib.crc32(data),0,32767,len(payload),len(data),65535);payload+=data
  tree+=b'\0'
 tree+=b'\0'
tree+=b'\0'; out=struct.pack('<7I',sig,2,len(tree),len(payload),0,48,0)+tree+payload
out+=hashlib.md5(tree).digest()+hashlib.md5(b'').digest();out+=hashlib.md5(out).digest()
(r/'merged.vpk').write_bytes(out)
manifest={k:hashlib.sha256(v).hexdigest() for k,v in files.items()}
(r/'merged-manifest.json').write_text(json.dumps(manifest))
report={'originalFiles':len(original),'mergedFiles':len(files),'replaced':[k for k in stage if k in original],'added':[k for k in stage if k not in original],'untouchedVerified':all(files[k]==v for k,v in original.items() if k not in stage),'sha256':hashlib.sha256(out).hexdigest()}
(r/'merge-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
