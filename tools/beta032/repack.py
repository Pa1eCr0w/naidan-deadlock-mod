from pathlib import Path
import argparse,hashlib,json,struct,zlib
p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
b=a.baseline.read_bytes()
assert hashlib.sha256(b).hexdigest()=='d2804eb086e73a8590c531ccf8dc299d3cb8437e58581b47e2416de8817d9e6a','Requires official Beta0.3.1 main VPK'
_,_,ts,*_=struct.unpack_from('<7I',b);p=28;files={}
def string():
 global p
 q=b.index(0,p);s=b[p:q].decode();p=q+1;return s
while (ext:=string()):
 while (directory:=string()):
  while (name:=string()):
   crc,pre,arc,off,size,end=struct.unpack_from('<IHHIIH',b,p);p+=18;assert arc==32767 and end==65535
   data=b[p:p+pre]+b[28+ts+off:28+ts+off+size];p+=pre;assert zlib.crc32(data)==crc
   files[(directory+'/' if directory!=' ' else '')+name+'.'+ext]=data
assert len(files)==1208 and 'scripts/heroes.vdata_c' not in files

files={k:v for k,v in files.items() if not (k.startswith(('resource/localization/','panorama/images/naidan_official_names/')) or k in ['panorama/styles/citadel_base_styles.vcss_c','panorama/styles/citadel_db_page_hero_release_vote.vcss_c','panorama/styles/citadel_hero_logo.vcss_c','panorama/layout/citadel_hero_logo.vxml_c'])}
assert len(files)==685
root=Path(__file__).resolve().parents[2]/'release-data/beta032'
for f in (root/'compiled').rglob('*'):
 if f.is_file():files[f.relative_to(root/'compiled').as_posix()]=f.read_bytes()
manifest=json.loads((root/'main-payload-sha256.json').read_text())
assert {k:hashlib.sha256(v).hexdigest() for k,v in files.items()}==manifest
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
tree+=b'\0';b=struct.pack('<7I',0x55aa1234,2,len(tree),len(payload),0,48,0)+tree+payload;b+=hashlib.md5(tree).digest()+hashlib.md5(b'').digest();b+=hashlib.md5(b).digest()

assert hashlib.sha256(b).hexdigest()=='1ca251db7ad4fd3d4990a5ab6d5a0cf5bc2e8f3d137fa8af0d1d6b8e323cd47e'
a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open('xb') as f:f.write(b)
print('PASS: 694 resources; exact tested Beta0.3.2 core')
