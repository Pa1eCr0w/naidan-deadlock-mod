# Beta 0.3.2 reproducible compatibility core

Authoritative delta source: `sources/beta032/`. Historical content directories remain for earlier versions and must not be blindly repackaged.

Reproduce the tested core with Python 3.9+:

```sh
python3 tools/beta032/repack.py /path/to/official-beta031/pak01_dir.vpk /new/path/pak01_dir.vpk
node tools/beta032/bridge-test.js sources/beta032/panorama/scripts/independent_wordmark_bridge.js
```

The repacker requires the official Beta0.3.1 input hash, removes 523 conflicting resources, then overlays ten compiled artifacts. One overlay updates retained Baba HUD CSS; 684 original payloads remain byte-identical. Output has 694 resources. Main VPK SHA256: `1ca251db7ad4fd3d4990a5ab6d5a0cf5bc2e8f3d137fa8af0d1d6b8e323cd47e`.

The ten compiled artifacts and corresponding sources include the shared bridge, own wordmark, yellow selection abilities/tags and active central bench-run HUD. Recompile with a compatible Source2 toolchain: `resourcecompiler.exe -game GAME_CITADEL -i CONTENT_FILE -nop4`, then decode/review with Source2Viewer. Both mods must ship byte-identical shared layout/style/script. The bridge uses engine-tested BHasClass and a fresh inner Panel per hero change, and only activates an extension with a successful BLoadLayout and IndependentWordmarkReady marker. Unknown/new heroes keep native behavior. Independent extensions contain only their own art; this repo adds no AberLai resources.

Current Valve UI-language path is `Game_UILanguage citadel_*LANGUAGE*`. Use `python3 tools/beta032/ui-language-path.py check --gameinfo PATH`; apply/restore require an explicit new backup path. The repair changes only the path-type token and rejects ambiguous input or unrelated later edits. Verify actual engine mounting after restart. The gameinfo itself is not part of the mod.

Ordinary names are separate from artwork. Optional token declarations do not load automatically; merge exact token changes onto current retail localization and combine other mods deliberately. Never ship a stale complete hero table. English Baba skill2 remains Granny Long Legs. The Chinese active central HUD title is supplied by a native SplitLabel/progress pair, separately from optional ordinary-name tokens. The ability-details experiment is not included. See release notes and validation.json for the exact staged test scope; the final HUD was owner-accepted in a combined installation.
