奶蛋 — Beta 0.3.2

• 重构奶蛋艺术字加载方式，支持与采用同版公共 bridge v3 的亚伯来模组独立安装、同时安装及交换加载顺序。
• 移除整套本地化表、全英雄艺术字副本和旧公共样式覆盖，只保留奶蛋自身资源与必要的公共桥接文件。
• 修复切换英雄后艺术字无法再次加载的问题；其他英雄继续使用游戏原生艺术字。
• 补充当前游戏语言资源加载配置的检测与最小修复工具，解决旧 Game_Language 配置造成中文艺术字缺失的问题。
• 保留 Beta 0.3.1 的模型、材质、特效及英雄解锁修复。

NaiDan — Beta 0.3.2

• Added independent wordmark loading compatible with the matching shared bridge v3 used by AberLai, including both package orders.
• Removed full localization tables, copied all-hero artwork and old shared-style overrides; retained NaiDan assets and the three neutral bridge resources.
• Fixed wordmarks failing to reload after switching heroes. Other heroes use native game artwork.
• Added a minimal UI-language search-path check/repair tool for the current Game_UILanguage setting.
• Preserved Beta 0.3.1 models, materials, effects and the hero-unlock fix.

安装与限制 / Installation and limits

主包替换旧奶蛋主包，不要同时启用两版。普通角色名字并不由此核心包自动修改：需要改名时，按 sources/beta032/optional-baba-name-patch.json 对当前原版文字做显式合并；同时使用其他改名模组时必须合并到同一覆盖层，不能直接叠加整张旧表。中文二技能“长腿奶蛋”亦属于该可选覆盖层。测试时使用了单独构建的名字覆盖层；不将旧全表随包分发。

检查 game/citadel/gameinfo.gi 的语言路径：当前游戏使用 Game_UILanguage citadel_*LANGUAGE*。若仍为 Game_Language，可使用仓库 tools/beta032/ui-language-path.py 检测、备份后仅改这一项；不要整份覆盖 gameinfo，也不要把个人配置打进模组。用游戏实际 path 输出确认对应语言包挂载。

Replace the old main package. This core does not automatically rename ordinary text. Apply the optional Baba token declaration to freshly extracted current localization text, merging explicitly with any other rename mod into one overlay. Never stack stale full tables. The Chinese skill-2 rename is optional text as well. Tests used explicit separate name overlays.

Check the current Game_UILanguage search path and actual language-pak mounting; the repository includes a minimal backed-up repair tool. No gameinfo file is bundled. The selection-lighting VPK is unchanged; existing installations need no update. For a new lighting install, extract its maps folder into Deadlock/game/citadel/addons/, preserving folders.

验证 / Validation

8 套实机组合：奶蛋单独、亚伯来单独、双包两种顺序，各自中英文；Atlas、Apollo、Lash、Pocket、Baba 艺术字、反复切换及婆婆二技能说明均已核对。显式合并名字层的中英文实际 token 解析另行验证通过。661 项模型/材质/粒子/maps 资源与 Beta 0.3.1 字节一致。未承诺所有第三方公共 UI 覆盖或未来游戏版本均兼容；需使用相同公共 bridge 的兼容版本。

Eight in-game configurations passed artwork and switching review in Chinese and English, with Baba skill-2 tooltips checked. Ordinary-name resolution was separately tested with an explicit merged overlay. All 661 protected model/material/particle/map resources match Beta 0.3.1. This is not a guarantee for arbitrary third-party shared UI replacements or future game changes.
