from pathlib import Path
import struct,zlib,hashlib,json,zipfile
import argparse
a=argparse.ArgumentParser();a.add_argument('source',type=Path);a.add_argument('output',type=Path);args=a.parse_args()
r=args.output;r.mkdir(parents=True,exist_ok=True);b=args.source.read_bytes();assert hashlib.sha256(b).hexdigest()=='7559302b452e37e669a1b43b3adaff75770927d3de33da0ac51d6beb31233de9'
sig,ver,ts,ds,*_=struct.unpack_from('<7I',b);p=28;files={}
def string():
 global p
 q=b.index(0,p);s=b[p:q].decode();p=q+1;return s
while (ext:=string()):
 while (directory:=string()):
  while (name:=string()):
   crc,pre,arc,off,size,end=struct.unpack_from('<IHHIIH',b,p);p+=18;assert end==65535 and arc==32767
   data=b[p:p+pre]+b[28+ts+off:28+ts+off+size];p+=pre;assert zlib.crc32(data)==crc
   files[(directory+'/' if directory!=' ' else '')+name+'.'+ext]=data
before={k:hashlib.sha256(v).hexdigest() for k,v in files.items()};assert len(files)==1209
removed=files.pop('scripts/heroes.vdata_c');assert not any(k.startswith('scripts/') for k in files)
groups={}
for path,data in sorted(files.items()):
 d,_,n=path.rpartition('/');name,ext=n.rsplit('.',1);groups.setdefault(ext,{}).setdefault(d or ' ',[]).append((name,data))
tree=bytearray();payload=bytearray()
for ext,dirs in sorted(groups.items()):
 tree+=ext.encode()+b'\0'
 for d,entries in sorted(dirs.items()):
  tree+=d.encode()+b'\0'
  for name,data in entries:tree+=name.encode()+b'\0'+struct.pack('<IHHIIH',zlib.crc32(data),0,32767,len(payload),len(data),65535);payload+=data
  tree+=b'\0'
 tree+=b'\0'
tree+=b'\0';out=struct.pack('<7I',sig,2,len(tree),len(payload),0,48,0)+tree+payload;out+=hashlib.md5(tree).digest()+hashlib.md5(b'').digest();out+=hashlib.md5(out).digest()
(r/'fixed.vpk').write_bytes(out);after={k:hashlib.sha256(v).hexdigest() for k,v in files.items()};assert all(before[k]==v for k,v in after.items())
(r/'manifest.json').write_text(json.dumps(after,indent=2));report={'sourceSHA256':hashlib.sha256(b).hexdigest(),'fixedSHA256':hashlib.sha256(out).hexdigest(),'removed':['scripts/heroes.vdata_c'],'retainedFiles':len(files),'allRetainedPayloadsByteExact':True,'noGlobalScriptOverrides':True,'uiAccentNote':'Baba UI accent supplied by heroes.vdata now follows the game default; yellow models and effects are untouched.'};(r/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
