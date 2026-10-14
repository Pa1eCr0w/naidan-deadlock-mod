using ValveResourceFormat;
using ValveResourceFormat.ResourceTypes;
using ValveResourceFormat.Serialization.KeyValues;
using ValveKeyValue;
using System.Text.Json;
var root=args[0];var report=new List<object>();
Patch(Path.Combine(root,"extracted/prefab/maps/ui/hero_prefabs/baba/entities/default_ents.vents_c"),"maps/ui/hero_prefabs/baba/entities/default_ents.vents_c",false);
Patch(Path.Combine(root,"feather.vmat_c"),"models/heroes_wip/baba/materials/baba_picker_feather.vmat_c",true);
File.WriteAllText(Path.Combine(root,"native-patch-report.json"),JsonSerializer.Serialize(report,new JsonSerializerOptions{WriteIndented=true}));
void Patch(string src,string relative,bool mat){
 using var r=new Resource();r.Read(src);var data=(KeyValuesOrNTRO)r.DataBlock!;var changes=new List<object>();
 if(mat){foreach(var v in data.Data["m_intParams"].Values)if(v["m_name"].ToString()=="F_VERTEX_COLOR"){v["m_nValue"]=0;changes.Add(new{field="F_VERTEX_COLOR",before=1,after=0});}
 foreach(var v in data.Data["m_vectorParams"].Values)if(v["m_name"].ToString()=="g_vColorTint1") {var arr=KVObject.Array();foreach(var x in new[]{1f,.72f,.06f,0f})arr.Add(x);v["m_value"]=arr;changes.Add(new{field="g_vColorTint1",after="1 .72 .06 0"});}
 if(changes.Count!=2)throw new Exception("Unexpected feather material");
 }else{
 foreach(var ent in data.Data["m_entityKeyValues"].Values){var v=ent["keyValues3Data"]["values"];if(!v.ContainsKey("classname")||!v["classname"].ToString().StartsWith("light_"))continue;
 foreach(var key in new[]{"color","skycolor"}){if(!v.ContainsKey(key))continue;var a=v[key].Values.Select(x=>x.ToInt32(null)).ToArray();if(a[2]<=a[1]||a[0]<=a[1])continue;var m=a.Max();var min=a.Min();var arr=KVObject.Array();foreach(var x in new[]{m,(int)Math.Round(m-(m-min)*.15),min})arr.Add(x);v[key]=arr;changes.Add(new{source=v["compile_source_id"].ToString(),field=key,before=a,after=arr.ToKV3String()});}}
 if(changes.Count!=5)throw new Exception("Unexpected light count "+changes.Count);
 }
 var dest=Path.Combine(root,"stage",relative);Directory.CreateDirectory(Path.GetDirectoryName(dest)!);using var ms=new MemoryStream();data.Serialize(ms);ReplaceData(src,dest,ms.ToArray());using var check=new Resource();check.Read(dest);if(((KeyValuesOrNTRO)check.DataBlock!).Data.ToKV3String()!=data.Data.ToKV3String())throw new Exception("Roundtrip failed");report.Add(new{path=relative,changes,roundtrip=true});Console.WriteLine(relative);
}
static void ReplaceData(string input,string output,byte[] data){var raw=File.ReadAllBytes(input);int table=8+BitConverter.ToInt32(raw,8);int count=BitConverter.ToInt32(raw,12);using var ms=new MemoryStream();using var w=new BinaryWriter(ms);w.Write(raw,0,16);w.Write(new byte[count*12]);var entries=new List<(byte[] Tag,int At,int Len)>();for(int i=0;i<count;i++){int p=table+12*i;var tag=raw[p..(p+4)];int start=p+4+BitConverter.ToInt32(raw,p+4),length=BitConverter.ToInt32(raw,p+8);while(ms.Position%4!=0)w.Write((byte)0);int at=(int)ms.Position;var payload=System.Text.Encoding.ASCII.GetString(tag)=="DATA"?data:raw[start..(start+length)];w.Write(payload);entries.Add((tag,at,payload.Length));}ms.Position=0;w.Write((uint)ms.Length);ms.Position=8;w.Write(8);w.Write(count);for(int i=0;i<count;i++){int p=16+i*12;ms.Position=p;w.Write(entries[i].Tag);w.Write(entries[i].At-(p+4));w.Write(entries[i].Len);}File.WriteAllBytes(output,ms.ToArray());}
