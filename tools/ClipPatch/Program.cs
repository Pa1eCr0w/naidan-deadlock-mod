using System.Numerics;
using System.Text.Json;
using System.Buffers.Binary;
using ValveResourceFormat;
using ValveResourceFormat.ResourceTypes;
using ValveResourceFormat.ResourceTypes.ModelAnimation;
using ValveResourceFormat.ResourceTypes.ModelAnimation2;
using ValveResourceFormat.Serialization.KeyValues;
using ValveKeyValue;

var input=args[0];var output=args[1];Directory.CreateDirectory(output);
using var sr=new Resource();sr.Read(Path.Combine(input,"models/heroes_wip/baba/baba.vnmskel_c"));
var skel=Skeleton.FromSkeletonData(((BinaryKV3)sr.DataBlock!).Data);var bones=skel.Bones;int N=bones.Length;
var ids=bones.ToDictionary(b=>b.Name,b=>b.Index);var rest=new Matrix4x4[N];
foreach(var b in bones){rest[b.Index]=Matrix4x4.CreateFromQuaternion(b.Angle)*Matrix4x4.CreateTranslation(b.Position);if(b.Parent!=null)rest[b.Index]*=rest[b.Parent.Index];}
var B=new Matrix4x4(0,-.0254f,0,0,.0254f,0,0,0,0,0,.0254f,0,0,0,0,1);var Bi=Inv(B);
var aliases=new Dictionary<string,string>{{"low","bangsA1_0"},{"mid","bangsA1_1"},{"top","bangsA_4"},{"eyeLU","bangsB_0"},{"eyeLD","bangsB_1"},{"pupilLU","bangsB_2"},{"pupilLD","bangsB_3"},{"eyeRU","bangsA_0"},{"eyeRD","bangsA_1"},{"pupilRU","bangsA_2"},{"pupilRD","bangsA_3"},{"mouthU","shawlTie_0_L"},{"mouthD","shawlTie_0_R"}};
var changed=aliases.Values.Select(n=>ids[n]).ToHashSet();
var reports=new List<object>();var previews=new Dictionary<string,object>();
foreach(var file in Directory.GetFiles(Path.Combine(input,"models/heroes_wip/baba/clips"),"*.vnmclip_c",SearchOption.AllDirectories)){
 using var r=new Resource();r.Read(file);var clip=(AnimationClip)r.DataBlock!;
 if(clip.SkeletonName!="models/heroes_wip/baba/baba.vnmskel")continue;
 if(clip.TrackCompressionSettings.Length!=N)throw new Exception("Track count differs "+file);
 var name=Path.GetFileName(file).Replace(".vnmclip_c","");bool ui=name is "ui_main_menu" or "ui_shop";
 int count=ui?121:clip.NumFrames;float duration=ui?4:clip.Duration;
 var frames=new FrameBone[count][];var deformSamples=new List<object>();var preview=ui||name is "outofcombat_stand_idle" or "weapon_stand_idle" or "out_of_combat_run_n" or "jump_ground" or "landing_impact" or "ability_hex_casting" or "ability_threadsap_cast" or "ability_bench_run_n" or "flinch_back" or "sleep_idle" or "ability_pigeon_assault_channeling_loop";
 for(int f=0;f<count;f++){
  float phase=count>1?(float)f/(count-1):0;float t=phase*duration;
  var local=new FrameBone[N];clip.ReadFrame(Math.Min(f,clip.NumFrames-1),local);
  if(clip.IsAdditive)new ClipAnimation(clip).ComposeAdditiveOverBindPose(local,skel);
  var world=new Matrix4x4[N];foreach(var bone in bones){world[bone.Index]=local[bone.Index].ToMatrix();if(bone.Parent!=null)world[bone.Index]*=world[bone.Parent.Index];}
  Matrix4x4 D(string n)=>Bi*Inv(rest[ids[n]])*world[ids[n]]*B;
  var bench=D("bench_pitch");var head=D("baba_head");var spine=D("baba_spine_2");
  var state=State(name,phase,t,duration,clip.IsAdditive);
  var center=new Vector3(0,.23f,2.24f);var topCenter=new Vector3(0,.18f,2.48f);
  var mid=BlendAround(bench,spine,center,.24f);
  var top=BlendAround(bench,head,topCenter,.30f);
  // The bottom stays attached to the chair while upper sections respond to the same motion clips.
  var low=bench;
  mid=Around(center,Matrix4x4.CreateRotationY(state.Sway*.55f))*mid;
  top=Around(topCenter,Matrix4x4.CreateRotationY(state.Sway))*top;
  mid=Matrix4x4.CreateTranslation(0,0,state.Squash*.40f)*mid;
  top=Matrix4x4.CreateTranslation(0,0,state.Squash)*top;
  var targets=new Dictionary<string,Matrix4x4>{{"low",low},{"mid",mid},{"top",top}};
  foreach(var side in new[]{"L","R"}){
   float blink=state.Blink;float sign=side=="L"?-1:1;
   foreach(var edge in new[]{"U","D"}){
    float dz=edge=="U"?-.05952f:.05952f;
    var eye=Matrix4x4.CreateTranslation(0,.030f*blink,dz*blink)*top;
    targets["eye"+side+edge]=eye;
    targets["pupil"+side+edge]=Matrix4x4.CreateTranslation(0,0,0)*eye;
   }
  }
  targets["mouthU"]=Matrix4x4.CreateTranslation(0,-.002f*state.Open,state.Open*.008f)*top;
  targets["mouthD"]=Matrix4x4.CreateTranslation(0,-.006f*state.Open,-state.Open*.036f)*top;
  var desired=aliases.ToDictionary(a=>ids[a.Value],a=>rest[ids[a.Value]]*B*targets[a.Key]*Bi);
  // Resolve parents first, including intermediary bones that are not controls.
  foreach(var bone in bones){int i=bone.Index;var parent=bone.Parent==null?Matrix4x4.Identity:world[bone.Parent.Index];
   if(desired.TryGetValue(i,out var target)){world[i]=target;local[i]=FrameBone.FromMatrix(target*Inv(parent));}
   else world[i]=local[i].ToMatrix()*parent;
  }
  if(preview){deformSamples.Add(new{time=t,blink=state.Blink,open=state.Open,deforms=aliases.ToDictionary(a=>a.Value,a=>Array(targets[a.Key]))});}
  if(clip.IsAdditive)foreach(var i in changed){local[i]=new FrameBone(local[i].Position-bones[i].Position,local[i].Scale-1,Quaternion.Normalize(Quaternion.Inverse(bones[i].Angle)*local[i].Angle));}
  frames[f]=local;
 }
 var kv=clip.Data.Root;var settings=kv.GetArray("m_trackCompressionSettings");
 var ranges=new Dictionary<int,(Vector3 Min,Vector3 Range)>();
 foreach(var i in changed){var min=new Vector3(float.PositiveInfinity);var max=new Vector3(float.NegativeInfinity);foreach(var f in frames){min=Vector3.Min(min,f[i].Position);max=Vector3.Max(max,f[i].Position);}var range=Vector3.Max(max-min,new Vector3(.000001f));ranges[i]=(min,range);
  var st=settings[i]!;SetRange(st,"m_translationRangeX",min.X,range.X);SetRange(st,"m_translationRangeY",min.Y,range.Y);SetRange(st,"m_translationRangeZ",min.Z,range.Z);SetRange(st,"m_scaleRange",clip.IsAdditive?0:1,0);
  st["m_bIsRotationStatic"]=false;st["m_bIsTranslationStatic"]=false;st["m_bIsScaleStatic"]=true;
 }
 using var dataStream=new MemoryStream();using var writer=new BinaryWriter(dataStream);var offsets=KVObject.Array();
 var lengths=clip.TrackCompressionSettings.Select(s=>(s.IsRotationStatic?0:6)+(s.IsTranslationStatic?0:6)+(s.IsScaleStatic?0:2)).ToArray();
 var sourceOffsets=new int[N];for(int i=1;i<N;i++)sourceOffsets[i]=sourceOffsets[i-1]+lengths[i-1];
 for(int f=0;f<count;f++){
  offsets.Add((uint)(dataStream.Position/2));int originalFrame=Math.Min(f,clip.NumFrames-1);int baseOffset=checked((int)clip.CompressedPoseOffsets[originalFrame]*2);
  for(int i=0;i<N;i++)if(changed.Contains(i)){
   WriteQuat(writer,frames[f][i].Angle);var(min,range)=ranges[i];var p=frames[f][i].Position;writer.Write(Quant(p.X,min.X,range.X));writer.Write(Quant(p.Y,min.Y,range.Y));writer.Write(Quant(p.Z,min.Z,range.Z));
  }else writer.Write(clip.CompressedPoseData,baseOffset+sourceOffsets[i],lengths[i]);
 }
 kv["m_compressedPoseData"]=dataStream.ToArray();kv["m_compressedPoseOffsets"]=offsets;
 if(ui){kv["m_nNumFrames"]=count;kv["m_flDuration"]=duration;}
 clip.SerializationVersion=5;clip.SerializationCompressionMethod=KV3BinaryCompressionMethod.Lz4;
 using var block=new MemoryStream();clip.Serialize(block);
 var relative=Path.GetRelativePath(input,file);var dest=Path.Combine(output,relative);Directory.CreateDirectory(Path.GetDirectoryName(dest)!);ReplaceData(file,dest,block.ToArray());
 // Decode the saved resource and compare every untouched track and modified pose.
 using var verify=new Resource();verify.Read(dest);var check=(AnimationClip)verify.DataBlock!;float errP=0,errQ=0;
 for(int f=0;f<count;f++){var old=new FrameBone[N];var now=new FrameBone[N];clip.ReadFrame(Math.Min(f,clip.NumFrames-1),old);check.ReadFrame(f,now);
  for(int i=0;i<N;i++){var expected=changed.Contains(i)?frames[f][i]:old[i];var pe=Vector3.Distance(expected.Position,now[i].Position);var qe=1-MathF.Abs(Quaternion.Dot(expected.Angle,now[i].Angle));if(changed.Contains(i)){errP=MathF.Max(errP,pe);errQ=MathF.Max(errQ,qe);}else if(pe>1e-7||qe>1e-5||expected.Scale!=now[i].Scale)throw new Exception($"Untouched bone changed {name} {f} {bones[i].Name}");}}
 if(errP>.003f||errQ>.00001f)throw new Exception($"Pose quantization failed {name} {errP} {errQ}");
 reports.Add(new{name,frames=count,additive=clip.IsAdditive,tracks=changed.Count,maxPositionErrorInches=errP,maxQuaternionError=errQ,untouchedTracksIdentical=true});
 if(preview)previews[name]=new{duration,additive=clip.IsAdditive,samples=deformSamples};
 Console.WriteLine($"PATCH {name}: {count} frames, {errP:F6} max error");
}
// Keep facial controls sampled at distance and give them the same layer mask as the head.
var skv=(BinaryKV3)sr.DataBlock!;skv.Data.Root["m_numBonesToSampleAtLowLOD"]=N;
foreach(var mask in skv.Data.GetArray("m_maskDefinitions")){
 var primary=mask.GetSubCollection("m_primaryWeightList");var names=primary.GetArray<string>("m_boneIDs").ToList();var ws=primary.GetArray<float>("m_weights").ToList();
 if(names.Count==0)continue;
 float weight=0;var b=bones[ids["baba_head"]];
 while(b!=null){var at=names.IndexOf(b.Name);if(at>=0){weight=ws[at];break;}b=b.Parent;}
 foreach(var n in aliases.Values){var at=names.IndexOf(n);if(at>=0)ws[at]=weight;else{names.Add(n);ws.Add(weight);}}
 var na=KVObject.Array();foreach(var n in names)na.Add(n);var wa=KVObject.Array();foreach(var w in ws)wa.Add(w);primary["m_boneIDs"]=na;primary["m_weights"]=wa;
}
skv.SerializationVersion=5;skv.SerializationCompressionMethod=KV3BinaryCompressionMethod.Lz4;using(var buf=new MemoryStream()){skv.Serialize(buf);ReplaceData(Path.Combine(input,"models/heroes_wip/baba/baba.vnmskel_c"),Path.Combine(output,"models/heroes_wip/baba/baba.vnmskel_c"),buf.ToArray());}
File.WriteAllText(Path.Combine(output,"clip-report.json"),JsonSerializer.Serialize(reports,new JsonSerializerOptions{WriteIndented=true}));
File.WriteAllText(Path.Combine(output,"preview-animation.json"),JsonSerializer.Serialize(previews));
File.WriteAllText(Path.Combine(output,"control-bones.json"),JsonSerializer.Serialize(aliases));
Console.WriteLine($"COMPLETE {reports.Count} clips");
static Matrix4x4 Inv(Matrix4x4 m){if(!Matrix4x4.Invert(m,out var r))throw new Exception("Singular transform");return r;}
static Matrix4x4 Around(Vector3 c,Matrix4x4 m)=>Matrix4x4.CreateTranslation(-c)*m*Matrix4x4.CreateTranslation(c);
static Matrix4x4 BlendAround(Matrix4x4 a,Matrix4x4 b,Vector3 center,float w){Matrix4x4.Decompose(a,out _,out var qa,out _);Matrix4x4.Decompose(b,out _,out var qb,out _);var q=Quaternion.Slerp(qa,qb,w);var anchor=Vector3.Lerp(Vector3.Transform(center,a),Vector3.Transform(center,b),w);return Matrix4x4.CreateTranslation(-center)*Matrix4x4.CreateFromQuaternion(q)*Matrix4x4.CreateTranslation(anchor);}
static float[] Array(Matrix4x4 m)=>[m.M11,m.M12,m.M13,m.M14,m.M21,m.M22,m.M23,m.M24,m.M31,m.M32,m.M33,m.M34,m.M41,m.M42,m.M43,m.M44];
static (float Blink,float Open,float Sway,float Squash,float Gaze) State(string n,float p,float t,float duration,bool additive){
 float pulse=MathF.Sin(MathF.PI*p),cyc=MathF.Sin(2*MathF.PI*p);float blink=0,open=0,sway=0,squash=0,gaze=0;
 bool idle=n.Contains("idle")||n.StartsWith("ui_");
 if(!additive&&idle&&duration>1){float center=duration*.66f;float d=MathF.Abs(t-center);blink=d<.115f?MathF.Pow(1-d/.115f,.7f):0;sway=.015f*cyc;squash=.007f*cyc;gaze=.0025f*MathF.Sin(2*MathF.PI*p);}
 if(n.Contains("sleep")){blink=.98f;open=.15f;squash=.009f*cyc;}
 if(n.Contains("run_")&&!n.Contains("idle")){sway=.055f*cyc;squash=.022f*MathF.Sin(4*MathF.PI*p);open=.12f*(.5f+.5f*cyc);}
 if(n.Contains("jump")){squash=.085f*pulse-.03f*MathF.Sin(2*MathF.PI*p);open=.55f*pulse;}
 if(n.Contains("in_air")){open=.30f;sway=.025f*cyc;}
 if(n.Contains("landing")||n.Contains("slam_hit")){squash=-.10f*pulse;blink=.78f*pulse;open=.35f*pulse;}
 if(n.Contains("flinch")||n.Contains("knockdown")){blink=.82f*pulse;open=.9f*pulse;sway=.075f*pulse;}
 if(n.Contains("shoot")){blink=.38f*pulse;open=.22f*pulse;}
 if(n.Contains("reload")){gaze=-.006f*pulse;blink=.18f*pulse;}
 if(n.Contains("threadsap")){blink=.28f*pulse;open=.65f*pulse;sway=-.05f*pulse;}
 if(n.Contains("hex")){open=.78f*pulse;gaze=.004f*pulse;sway=.06f*cyc;}
 if(n.Contains("pigeon_assault")){open=.65f*(n.Contains("loop")?.6f+.4f*cyc:pulse);blink=.18f;sway=.045f*cyc;}
 if(n.Contains("melee")||n.Contains("parry")){blink=.60f*pulse;open=.55f*pulse;sway=.09f*pulse;}
 if(n.Contains("dash")||n.Contains("slide")){blink=.22f*pulse;open=.28f*pulse;sway=.045f*pulse;}
 return(Math.Clamp(blink,0,.99f),Math.Clamp(open,0,1),sway,squash,gaze);
}
static void SetRange(KVObject o,string name,float min,float range){var r=o.GetSubCollection(name);r["m_flRangeStart"]=min;r["m_flRangeLength"]=range;}
static ushort Quant(float x,float min,float range)=>(ushort)Math.Clamp((int)MathF.Round((x-min)/range*65535),0,65535);
static void WriteQuat(BinaryWriter w,Quaternion q){q=Quaternion.Normalize(q);float[] a=[q.X,q.Y,q.Z,q.W];int k=0;for(int i=1;i<4;i++)if(MathF.Abs(a[i])>MathF.Abs(a[k]))k=i;float sign=a[k]<0?-1:1;var v=a.Where((_,i)=>i!=k).Select(x=>(ushort)Math.Clamp((int)MathF.Round((x*sign+.7071067811865475f)/1.414213562373095f*32767),0,32767)).ToArray();v[0]|=(ushort)((k>>1)<<15);v[1]|=(ushort)((k&1)<<15);foreach(var x in v)w.Write(x);}
static void ReplaceData(string input,string output,byte[] data){var raw=File.ReadAllBytes(input);int table=8+BitConverter.ToInt32(raw,8);int count=BitConverter.ToInt32(raw,12);using var ms=new MemoryStream();using var w=new BinaryWriter(ms);w.Write(raw,0,16);w.Write(new byte[count*12]);var entries=new List<(byte[] Tag,int At,int Len)>();for(int i=0;i<count;i++){int p=table+12*i;var tag=raw[p..(p+4)];int start=p+4+BitConverter.ToInt32(raw,p+4),length=BitConverter.ToInt32(raw,p+8);while(ms.Position%4!=0)w.Write((byte)0);int at=(int)ms.Position;var payload=System.Text.Encoding.ASCII.GetString(tag)=="DATA"?data:raw[start..(start+length)];w.Write(payload);entries.Add((tag,at,payload.Length));}ms.Position=0;w.Write((uint)ms.Length);ms.Position=8;w.Write(8);w.Write(count);for(int i=0;i<count;i++){int p=16+i*12;ms.Position=p;w.Write(entries[i].Tag);w.Write(entries[i].At-(p+4));w.Write(entries[i].Len);}File.WriteAllBytes(output,ms.ToArray());}
