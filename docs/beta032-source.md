# Beta 0.3.2 reproducible compatibility core

Authoritative delta source: `sources/beta032/`. Historical content directories remain for earlier versions and must not be blindly repackaged.

Reproduce the tested core with Python 3.9+:

```sh
python3 tools/beta032/repack.py /path/to/official-beta031/pak01_dir.vpk /new/path/pak01_dir.vpk
node tools/beta032/bridge-test.js sources/beta032/panorama/scripts/independent_wordmark_bridge.js
```

The repacker requires the official Beta0.3.1 input hash, keeps 685 original payloads byte-for-byte, removes 523 conflicting/full-table resources and adds five compiled resources. The retained shared hero-logo layout is replaced with the neutral bridge layout. Output has 690 resources. Main VPK SHA256: `e62ebe903c9f7d075d4fed3dac106cf28a622f0e3d9fd9e48d562c77d9465cf0`.

The five exact compiled artifacts are in release-data/beta032/compiled; sources are included. Recompile with a compatible Source2 toolchain: `resourcecompiler.exe -game GAME_CITADEL -i CONTENT_FILE -nop4`, then decode/review with Source2Viewer. Both mods must ship byte-identical shared layout/style/script. The bridge uses engine-tested BHasClass and a fresh inner Panel per hero change, and only activates an extension with a successful BLoadLayout and IndependentWordmarkReady marker. Unknown/new heroes keep native behavior. Independent extensions contain only their own art; this repo adds no AberLai resources.

Current Valve UI-language path is `Game_UILanguage citadel_*LANGUAGE*`. Use `python3 tools/beta032/ui-language-path.py check --gameinfo PATH`; apply/restore require an explicit new backup path. The repair changes only the path-type token and rejects ambiguous input or unrelated later edits. Verify actual engine mounting after restart. The gameinfo itself is not part of the mod.

Ordinary names are separate from artwork. Optional token declarations do not load automatically; merge exact token changes onto current retail localization and combine other mods deliberately. Never ship a stale complete hero table. English Baba skill2 remains Granny Long Legs. See release notes for the eight-profile validation scope and limitations. Runtime test environment was restored afterwards; release does not claim a permanent local installation.
