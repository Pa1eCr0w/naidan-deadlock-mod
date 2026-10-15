# Naidan (奶蛋,Nailong,奶龙) over Baba

naidanbaba

奶龙奶蛋替换婆婆mod，技能和角色图标都有经过重置，还在快速迭代中，获取最新进度&锁锁奶龙宇宙modQQ交流群824273044

[GameBanana 原发布页](https://gamebanana.com/mods/726842)

## Beta 0.3.2

独立艺术字、黄色选人界面与中央“长腿奶蛋”提示更新；模型、材质和特效保持 Beta 0.3.1。主包不再附带整张改名表，普通名称改动需要显式合并可选覆盖层。中文艺术字需正确挂载 Game_UILanguage 资源。

[下载 Beta 0.3.2](https://github.com/Pa1eCr0w/naidan-deadlock-mod/releases/tag/v0.3.2) · [源码、复现与兼容说明](docs/beta032-source.md)

## Beta 0.3.1

奶蛋 — Beta 0.3.1

• 修复安装模组后空骨丹尼在选人界面被锁定、无法使用的问题。
• 移除过期的全局英雄配置，后续英雄解锁跟随游戏更新，避免阿紫、护士等新英雄出现同类问题。
• 保留 Beta 0.3.0 的模型、材质和特效。原先通过英雄配置修改的界面主题色恢复为游戏默认颜色。

NaiDan — Beta 0.3.1

• Fixed the mod preventing the newly unlocked hero from being selected.
• Removed the outdated global hero configuration so future hero unlocks follow game updates, avoiding the same compatibility issue for upcoming heroes.
• Retained Beta 0.3.0 models, materials and effects. The UI accent previously changed through the hero configuration now follows the game default.

[下载 Beta 0.3.1](https://github.com/Pa1eCr0w/naidan-deadlock-mod/releases/tag/v0.3.1) · [兼容修复说明](docs/beta031-source.md)

## Beta 0.3.0

奶蛋 — Beta 0.3.0

• 将所有婆婆的鸽子替换为奶鸽。
• 将婆婆的茶杯替换为奶茶。
• 将婆婆的杖子替换为奶脚。
• 更新奶蛋主体的材质。
• 将所有婆婆的紫色元素改为黄色。
• 将长椅的颜色改得更接地气。

NaiDan — Beta 0.3.0

• Replaced all of Baba’s pigeons with NaiGe.
• Replaced Baba’s teacup with NaiCha.
• Replaced Baba’s staff with NaiJiao, a Nailong foot.
• Updated NaiDan’s body materials.
• Changed all of Baba’s purple elements to yellow.
• Updated the bench with more natural, everyday park-bench colors.


[下载 Beta 0.3.0](https://github.com/Pa1eCr0w/naidan-deadlock-mod/releases/tag/v0.3.0) · [源码说明](docs/beta030-source.md)

## Beta 0.2.0

奶蛋 — Beta 0.2.0

• 更新骨架动作与表情表现，优化眼球造型和身体颜色。
• 更新常规、危急和大笑三种头像，并调整头像位置。
• 新增独立小地图图标。
• 更新二、三技能图标，突出长腿与茶壶特征。
• 更新白色「奶蛋 / NaiDan」艺术字，修复其他英雄艺术字及语言显示问题。
• 调整技能特效为奶蛋主题黄色。

NaiDan — Beta 0.2.0

• Updated rigged animations and facial expressions, with refinements to eye shape and body color.
• Updated the normal, critical-health, and laughing portraits and adjusted their positioning.
• Added a dedicated minimap icon.
• Updated ability 2 and 3 icons to better highlight the long legs and teapot.
• Updated the white “奶蛋 / NaiDan” wordmarks and fixed other heroes’ stylized names and language display.
• Updated ability effects with NaiDan’s yellow theme.

## 文件说明

- `art/`：二维美术原图、三状态头像、独立小地图图标和中英文矢量艺术字。
- `content/`：Source 2 UI 源文件、材质及模型 FBX。当前版本以 `art/portraits/critical-selected.png` 为危急头像。
- `tools/`：动作映射与资源修改工具。historical 中为制作过程脚本，需要调整本地路径和依赖，尚未整理为一键构建工具。
- `authoring/beta030/`：奶茶、奶脚和奶鸽的 Blender 编辑工程。完整发行版网格与 LOD 以 `content/` 中 ModelDoc 引用的 FBX 为准。
- `release-data/beta030/`：从实际发布包导出的材质、特效参数及文件校验表，包含直接修改编译资源的最终结果。
- `tools/beta030/`：本次模型、权重、贴图及材质/粒子修改代码。
- GitHub 的 Source code ZIP/TAR 包含上述源码和 Blender 工程；游戏安装包单独提供。

美术制作使用了 AI 生成及人工指导迭代。Deadlock 原始模型、骨架、动画、界面和粒子依赖属于游戏来源内容；奶龙角色及参考素材来自相应原作者。公开文件不表示这些第三方内容由本仓库作者原创或可替第三方授权。

## 许可 / License

本项目作者有权授权的内容采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)。允许署名后非商业修改与再发布，修改时请注明变更。第三方角色、游戏资源及依赖仍受各自权利约束。

Author-owned contributions are available under CC BY-NC 4.0: attribution is required; noncommercial modification and redistribution are permitted. Identify your changes. Third-party content retains its own rights and terms.

这是允许非商用衍生的公开源文件仓库，不属于允许商用的 OSI 开源许可。
