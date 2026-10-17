# 婆婆奶蛋 0.3.3：视角数据修复与复现

恢复10条相机定义及16个根骨挂点；修正291个动作的读取偏移，保留原286动作姿态，提供匹配的243骨骨架和5个新增动作转换。保留旧版外观、声音与UI；不是四肢版。

## 输入与结果

- 基线VPK SHA256：`1ca251db7ad4fd3d4990a5ab6d5a0cf5bc2e8f3d137fa8af0d1d6b8e323cd47e`。先从本仓库上一版Release的ModManager ZIP中提取VPK。
- 结果VPK SHA256：`7f73e1879103b17b0c21bdb2d87b35517b1ff38732149d6064b179868f59b2f6`，共700项资源。
- 未改动的原有资源：407项；哈希清单位于 `release-data/v0.3.3/payload-sha256.json`。
- `compiled/`增量资源、零售模型参考输入与修复代码均随本提交提供；不依赖个人设备路径、远程登录或安装状态。

## 确定性重新打包

```sh
python3 tools/camera-contract/rebuild.py BASELINE.vpk rebuilt.vpk --version 0.3.3
```

## 从修复源码重新生成

需要Python3、.NET10及ValveResourceFormat。上游仓库 `https://github.com/ValveResourceFormat/ValveResourceFormat`，本次读取器基于提交 `d9926fcb7df821b8476f4750250d5dbf61a6bab7`，先在该仓库应用 `tools/camera-contract/vrf-kv3-compat.patch`（KV3类型26/27兼容；上游许可证适用）。

```sh
python3 tools/camera-contract/rebuild.py BASELINE.vpk rebuilt-source.vpk --version 0.3.3 --from-source --vrf-project /path/to/ValveResourceFormat/ValveResourceFormat.csproj
```

`--dotnet`可指定dotnet可执行文件。脚本使用临时目录，并拒绝覆盖已有输出；逐资源验证后再断言完整VPK哈希。此源码路径已在本次发布环境执行，结果与群包/安装VPK字节一致；不声称已在干净机器完成整个历史模型作者工程构建。

## 检查边界

相机定义与各自当前零售模型一致，所有MDAT根挂点精确匹配；模型其他数据、材质和外观不改。291动作243轨道和243骨骨架配套，2,703,861次随机读取采样与顺序解码一致；5个新增动作世界位置转换误差小于0.012165原版单位。

完整验证摘要：`release-data/v0.3.3/validation.json`。实际安装哈希已核对；尚未完成所有技能/特殊状态的实机回归。

旧Release资产不改；奶蛋四肢分支保留。
