# How to Run the Blender Setup Script

In Blender:
1. Open the Scripting workspace.
2. Open `setup_character_project.py`.
3. Click **Run Script**.
4. Save the new `.blend` as `GBAM_BASE_v001.blend`.

The script creates:
- metric scene settings
- project collections
- 1024 x 1024 Eevee preview render settings
- portrait camera
- soft 3-light studio setup
- head-origin guide

The bootstrap supports the Eevee engine names in Blender 4.x and 5.x.

## Face Match Puzzle portrait pass

From the repository root, use Blender 5.2:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python art/blender/scripts/create_gbam_character.py -- --character all
```

The portrait builder runs this bootstrap, aims its lights at the head, switches to front
orthographic framing and Cycles, and builds the two selected roster characters. It saves and
reopens each scene before rendering the complete portrait and its blank puzzle base.
Use `--character boy` or `--character girl` for just one; add `--verify-only` to validate saved
scenes and PNGs without rebuilding. Outputs and prototype limitations are in `docs/GAME_DESIGN.md`.

Your AI can then build into the prepared collections.
