奶蛋 — Beta 0.3.2

• 重构奶蛋艺术字加载，支持与使用同版公共桥接的亚伯来独立安装及同时安装，修复切换英雄后艺术字无法再次加载的问题。
• 移除过期的整套本地化表、全英雄艺术字副本及旧公共样式覆盖，其他英雄继续使用原生资源。
• 恢复选人界面奶蛋的黄色技能图标底色和标签。
• 开启二技能后，屏幕中央的中文提示改为“长腿奶蛋”，进度显示改为黄色，沿用原生进度与显示生命周期。
• 保留 Beta 0.3.1 的模型、材质、特效与英雄解锁修复。

NaiDan — Beta 0.3.2

• Independent wordmarks with the matching AberLai shared bridge; fixed reload after hero switching.
• Removed stale full localization tables, copied all-hero artwork and old shared-style overrides.
• Restored yellow selection ability circles and tags.
• Active bench-run HUD now shows 长腿奶蛋 in Chinese with yellow progress. Native progress and visibility lifecycle remain; English keeps its original title.
• Preserved Beta 0.3.1 models, materials, effects and hero-unlock fix.

安装与验证 / Installation and validation

主包替换旧奶蛋主包，不要同时启用两版。选人灯光包未变，已经安装的无需重复更新。新装灯光包将 maps 文件夹解压到 Deadlock/game/citadel/addons/。普通名字与技能详情文字不由核心包自动改名；可选 token 声明须合并到当前游戏文本，不能叠加旧全表。

中文艺术字需要正确挂载 Game_UILanguage 语言资源，仓库提供最小检测与备份修复工具，不附带整份 gameinfo。

最终中央 HUD 已由用户实机验收，已核对安装包哈希。黄色选人 UI 基线通过中文单装、双装两种顺序四配置检查；公共艺术字桥接较早版本通过中英文八配置检查。这些不等于最终 HUD 完整回归：未完成该最终候选的英文、单双装矩阵及开始/中途/结束/重触发自动截图。694 项资源已独立读回校验。兼容范围为匹配公共桥接的版本，不保证任意第三方 UI 覆盖或未来游戏版本。

Replace the old main package. Selection lighting is unchanged. Ordinary names/tooltips require an explicit optional token merge onto current retail text. Do not stack stale localization tables. Final central HUD was accepted by the owner in game and installed hashes were confirmed. Earlier yellow selection UI passed four Chinese configurations; earlier shared bridge passed eight Chinese/English configurations. The final HUD has not completed an automated lifecycle capture or English/single/combined matrix. All 694 payloads were independently read and verified.
