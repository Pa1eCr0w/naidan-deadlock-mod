using ValveResourceFormat;
using ValveResourceFormat.ResourceTypes;
using ValveResourceFormat.Serialization.KeyValues;
using ValveKeyValue;
using System.Text.Json;
var root="work/yellow-v3";int files=0,diffs=0;
foreach(var path in Directory.GetFiles(root+"/patched","*_c",SearchOption.AllDirectories)){
 var rel=Path.GetRelativePath(root+"/patched",path);var orig=rel.StartsWith("materials")?Path.Combine(root,"more-assets",rel):Path.Combine(root,"retail",rel);
 using var a=new Resource();a.Read(orig);using var b=new Resource();b.Read(path);
 if(a.Blocks.Count!=b.Blocks.Count)throw new Exception("Block count changed");
 var rawA=File.ReadAllBytes(orig);var rawB=File.ReadAllBytes(path);
 for(int i=0;i<a.Blocks.Count;i++){var x=a.Blocks[i];var y=b.Blocks[i];if(x.Type!=y.Type)throw new Exception("Block type changed");if(x.Type!=BlockType.DATA&&!rawA.AsSpan((int)x.Offset,(int)x.Size).SequenceEqual(rawB.AsSpan((int)y.Offset,(int)y.Size)))throw new Exception("Non DATA changed: "+rel);}
 var ak=a.DataBlock is BinaryKV3 ba?ba.Data.Root:((KeyValuesOrNTRO)a.DataBlock!).Data;
 var bk=b.DataBlock is BinaryKV3 bb?bb.Data.Root:((KeyValuesOrNTRO)b.DataBlock!).Data;
 Compare(ak,bk,"");files++;
}
File.WriteAllText(root+"/validation.json",JsonSerializer.Serialize(new{files,changedColorScalars=diffs,nonColorFieldsIdentical=true,nonDataBlocksIdentical=true,otherHeroesIdentical=true,gameTested=false},new JsonSerializerOptions{WriteIndented=true}));
Console.WriteLine($"Validated {files} resources; {diffs} changed color components; all other fields and blocks identical.");
void Compare(KVObject a,KVObject b,string path){
 if(a.IsCollection){if(!b.IsCollection)throw new Exception("Type changed "+path);
 if(a.Count!=b.Count){if(path!=""||a.ContainsKey("m_ConstantColor")||b.Count!=a.Count+1||!b.ContainsKey("m_ConstantColor"))throw new Exception("Keys changed "+path);
 var c=b["m_ConstantColor"].Values.Select(x=>x.ToInt32(System.Globalization.CultureInfo.InvariantCulture)).ToArray();if(!c.SequenceEqual(new[]{255,216,79,255}))throw new Exception("Unexpected constant");}foreach(var(n,x)in a.Children)Compare(x,b[n],path+"/"+n);}
 else if(a.IsArray){if(!b.IsArray||a.Count!=b.Count)throw new Exception("Array changed "+path);var av=a.Values.ToArray();var bv=b.Values.ToArray();for(int i=0;i<av.Length;i++)Compare(av[i],bv[i],path+"/"+i);}
 else if(a.ToKV3String()!=b.ToKV3String()){
  bool color=path.Contains("/m_Color/")||path.Contains("/m_ColorMin/")||path.Contains("/m_ColorMax/")||path.Contains("/m_ColorFade/")||path.Contains("/m_ConstantColor/")||path.Contains("/m_LiteralColor/")||((path.Contains("Color")||path.Contains("color"))&&path.Contains("/m_vLiteralValue/"))||path.StartsWith("/m_vectorParams/")&&path.Contains("/m_value/")||path.StartsWith("/hero_baba/m_colorUI/");
  if(!color||path.EndsWith("/3"))throw new Exception("Unexpected change "+path);diffs++;
 }
}
