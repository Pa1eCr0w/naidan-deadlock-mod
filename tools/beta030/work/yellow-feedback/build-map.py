from pathlib import Path
import struct,zlib,hashlib,json
r=Path('work/yellow-feedback'); b=(r/'baba-map-baseline.vpk').read_bytes()
assert hashlib.sha256(b).hexdigest()=='8299807b23f12c51be0be8e05975b36589cd4bbff2209b464d012dc3cb8b6f4d'
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
original=files.copy(); stage={x.relative_to(r/'map-stage').as_posix():x.read_bytes() for x in (r/'map-stage').rglob('*') if x.is_file()}
assert len(stage)==1
assert set(stage)=={'maps/ui/hero_prefabs/baba/entities/default_ents.vents_c'}
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
(r/'baba-map-patched.vpk').write_bytes(out)
manifest={k:hashlib.sha256(v).hexdigest() for k,v in files.items()}
(r/'map-manifest.json').write_text(json.dumps(manifest))
report={'originalFiles':len(original),'mergedFiles':len(files),'replaced':[k for k in stage if k in original],'added':[k for k in stage if k not in original],'untouchedVerified':all(files[k]==v for k,v in original.items() if k not in stage),'sha256':hashlib.sha256(out).hexdigest()}
(r/'map-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
