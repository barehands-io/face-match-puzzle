# Face Match Puzzle

A children's face-building puzzle game: look at the example character, then drag the eyes, nose, mouth
and hair onto a blank face to rebuild it. Inspired by magnetic face-puzzle toys.

| GBAM boy — short coils, yellow hoodie | GBAM girl — puff buns, green overalls |
|---|---|
| ![Flat boy portrait](art/renders/gbam-boy-portrait-flat.png) | ![Flat girl portrait](art/renders/gbam-girl-portrait-flat.png) |
| [Blank face](art/renders/gbam-boy-blank-flat.png) | [Blank face](art/renders/gbam-girl-blank-flat.png) |

- **Engine:** Godot 4 (2D) — iOS, Android, Web
- **Art:** Blender (scripted, `art/blender/`)
- **Design doc:** [`docs/GAME_DESIGN.md`](docs/GAME_DESIGN.md)

## Play the prototype

Open `game/project.godot` in Godot 4 and press **F5**. Drag features onto the blank face to
match the example. Nearby drops snap into place; other drops gently return to the tray.
Complete the face, try again, or switch characters. Mouse and touch are supported.

On this Mac:
```sh
/Applications/Godot.app/Contents/MacOS/Godot --path game
```

Run the mechanics checks:
```sh
/Applications/Godot.app/Contents/MacOS/Godot --headless --path game --script res://tests/puzzle_test.gd
```

Regenerate the game assets from the saved flat Blender scenes:
```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python art/blender/scripts/export_puzzle_pieces.py
```

Status: first playable desktop prototype; mobile devices and web/Safari export are not yet tested.
Earlier redhead/clown artwork is
preserved as history. The clay-style GBAM renders are also historical; the active artwork uses
`-flat` filenames and the owner's flat-illustration reference sheet.
