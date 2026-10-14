# Beta 0.3.0 源文件说明 / Source snapshot

本次源码对应已发布的 Beta 0.3.0 安装包，补齐奶鸽、奶茶、奶脚、主体材质、黄色特效和长椅改色的制作文件。`content/` 为编辑资源，`tools/beta030/` 为制作与补丁代码，`release-data/beta030/` 为实际发行文件导出的最终参数与校验表。

## 模型与编辑入口

| 游戏资源 | 当前编辑入口 |
| --- | --- |
| 婆婆主体、奶茶、奶脚与长椅 | `content/models/heroes_wip/baba/baba.vmdl`；主体/道具四级 LOD 在 `content/models/naidan_cupturn/` |
| 背上折翼/展开奶鸽 | 主体 ModelDoc 引用的 `content/models/naidan_props/bench_folded_lod*.fbx`、`bench_open_lod*.fbx` |
| 普通奶鸽、变身奶鸽 | `content/models/heroes_wip/baba/baba_pigeon.vmdl`、`baba_pigeon_transform.vmdl` |
| 选人界面背后奶鸽 | `content/models/naidan_props/picker.vmdl`，编译后映射到 `models/heroes_wip/baba/baba_pidge_picker.vmdl_c` |
| 选人装饰奶鸽 | `content/models/heroes_wip/baba/baba_pigeon_pickscreen_a.vmdl` |
| 特效、幽灵奶鸽 | `content/models/naige_all/effect.vmdl`、`ghost.vmdl`；effect 编译后映射到 `models/heroes_wip/baba/baba_pigeon_effect.vmdl_c` |

`authoring/beta030/main-props-lod0.blend` 是奶茶转面后主体/道具的 Blender 编辑工程。其余 Blender 文件是奶鸽形状与独立角色的编辑起点；**背上奶鸽后续权重、所有最终 LOD 和实际组合以当前 ModelDoc 引用的 FBX 为准**，不能用较早 Blender 草稿覆盖这些最终导出文件。导入 FBX 可继续编辑完整网格和骨架。

## 贴图、材质和特效

- 原贴图重着色的长椅图、奶脚渐变图与奶茶材质位于 `content/materials/models/naidan_props/`。
- 主体材质位于 `content/materials/models/naidan/`。数值开关已与发布版同步；材质最终还经历了原生资源补丁。
- 当前技能图标与奶龙蛋图标位于 `content/panorama/images/`。
- `content/particles/` 是从最终发行包恢复的可编辑粒子文件，包含大招命中后变身羽毛与闪电的黄色参数。
- `release-data/beta030/` 中的 `.kv3` 是最终编译资源的 DATA 参数快照，供核对/修改；它们不是可直接交给资源编译器的 VMAT 源文件。
- 原生材质补丁保留了游戏中的纹理打包、动态表达式和其他资源块，因此仅重新编译 VMAT 不保证逐字节还原发布结果。最终参数以这些快照及对应补丁代码为准。

## 制作代码与顺序

`tools/beta030/work/` 保留了各阶段的相对目录，便于对照制作过程：

1. `naige-successor/smooth-joints/`：连续曲面奶鸽建模与权重修整。
2. `naige-solid-install/`、`naige-all/`：不同鸽子角色的适配及 LOD；`cup-egg-motion/build-wings.py`：背上奶鸽的解剖部位权重映射。
3. `body-ult-fix/build.py`：当前奶茶笑脸、180°转面、奶脚及四级 LOD。
4. `bench-texture-fix/bake.py` 和 `MaterialPatch/`：保留原始细节的长椅贴图重着色。
5. `lighting-sync/MaterialPatch/`：主体材质受光同步。随后必须恢复主体与眼睛的原有反壳描边材质；最终两个描边的 DATA 快照在 `release-data/beta030/materials/models/naidan/`。不要再次应用中间版本的描边改动。
6. `yellow-complete/`：黄色纹理、羽毛与场景灯光；`body-ult-fix/Patch/`：最终长椅亮度与大招命中后粒子色彩修正。
7. `yellow-feedback/build-map.py`：独立选人场景 VPK 的重打包。最终灯光参数在 `release-data/beta030/selection-map/`。

这些是经过整理的制作代码，不是已经验证的一键从零构建系统。部分脚本仍需要前一阶段导出文件、游戏原始资源或实际发行包作为基线；默认工作位置已改为通用的 `D:/NaiDanWorkspace`，请按自己的路径调整。不要直接运行历史阶段代码覆盖最终文件。

## 工具与复现范围

已使用 Blender 4.5.9、Source 2 ResourceCompiler、Source 2 Viewer / ValveResourceFormat、Python（Pillow、NumPy 等）和 .NET 10。游戏原始资源与 Valve 编译器需自行从合法安装环境提供；不包含工具二进制、账户信息、私信或远程控制脚本。

C# 补丁项目使用外部 ValveResourceFormat 源码：

```text
dotnet run --project tools/beta030/work/body-ult-fix/Patch -p:VRFProject=/path/to/ValveResourceFormat/ValveResourceFormat.csproj
```

执行前需按脚本中的相对路径准备基线；其他 C# 项目同理。项目随附的验证记录是当次构建检查结果，不代表所有环境都能直接重建，也不等于新增游戏实测。

本次源码检查确认 ModelDoc/VMAT/VTEX 中直接引用的 FBX、DMX 和自带 PNG 均存在；原游戏材质、动画图和其他引擎资源仍为外部依赖。发布安装包保持不变：

- 主 VPK SHA256：`7559302b452e37e669a1b43b3adaff75770927d3de33da0ac51d6beb31233de9`
- 选人场景 VPK SHA256：`b40fab049144758e30adb0f0e52a601cf9e9017c4c1c4329ba8e9da6530d7f92`

GitHub 的 Source code ZIP/TAR 会随修正后的 `v0.3.0` 标签包含本次源文件。运行安装仍使用 Release 中的 ModManager ZIP；黄色选人场景灯光补充包按随附说明手动安装。

## Rights

Author-owned contributions remain CC BY-NC 4.0. Original game resources, character designs and other third-party dependencies retain their respective rights. This source snapshot does not grant ownership or additional rights over third-party content.
