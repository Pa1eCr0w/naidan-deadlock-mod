# 四肢版编译后检查工具

依赖 .NET 10 和 [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) 源码项目。外部库未复制进本目录，使用时遵守其许可证。读取器须支持 KV3 的 UINT32_ZERO / UINT32_ONE 类型。

构建时用 `-p:ValveResourceFormatProject=...` 指定本地 `ValveResourceFormat.csproj`。以下路径都是调用者提供的本地输入，程序不连接任何设备或账户。

## RuntimeContractPatch

参数顺序：当前自定义编译模型、当前零售婆婆编译模型、自定义动作目录、独立输出目录。

该工具针对本版资源契约：恢复当前零售婆婆的 16 个 root_motion 挂点及 10 条相机定义；重新累计 291 个自定义动作的 16 位轨道读取偏移。保留压缩姿态字节。数量或结构不符会停止，不适用于任意英雄或任意未来游戏版本。

先确认输入模型已经完成四档网格单位修正和四肢绑定。此工具不会自动修正网格尺度，也不会安装或打包模组。模型再次编译后应重跑契约检查。

## TrackAudit

参数顺序：输出 JSON、一个或多个动作目录。报告轨道读取偏移与静态/动态字段累计长度是否一致，以及模型空间采样索引。它只作数据检查，不能证明实际游戏表现。

原生库的读取偏移使用 16 位字单位。完整实际版本的哈希和验证摘要见 `downloads/naidan-limbs-0.3.2/`。运行时测试仍然必要。
