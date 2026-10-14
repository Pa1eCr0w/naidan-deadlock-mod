# Beta 0.3.1 compatibility fix

The Beta 0.3.0 package included an outdated `scripts/heroes.vdata_c`. This could override newer hero release states. Beta 0.3.1 removes that entire global override rather than replacing it with another snapshot.

All 1,208 remaining resources are byte-identical to Beta 0.3.0. Models, materials, artwork and effects continue to use the source documented in [Beta 0.3.0](beta030-source.md). The yellow selection-lighting VPK is unchanged. The hero-table UI accent returns to the game default.

Reproduce from the official Beta 0.3.0 main VPK:

```sh
python3 tools/beta031/repack.py /path/to/beta030/pak01_dir.vpk /path/to/output
```

The tool requires the known Beta 0.3.0 input hash, removes only the global hero table, and writes `fixed.vpk`, `manifest.json` and `validation.json`. Package `fixed.vpk` as `pak01_dir.vpk` at the ZIP root for Mod Manager. Do not include `scripts/heroes.vdata_c` in future packages, including when using historical build scripts.

Validation: independent VRF extraction matched all 1,208 payload hashes; installation preserved unrelated mods. The user confirmed the hero-selection issue resolved in game on 2026-10-14. This prevents the stale-table unlock regression, not every possible future game compatibility issue.

Main VPK SHA256: `d2804eb086e73a8590c531ccf8dc299d3cb8437e58581b47e2416de8817d9e6a`.
