# Copilot instructions — Face Match Puzzle

Read `docs/GAME_DESIGN.md` before doing any work. It is the source of truth for what this game is.

## What this project is
A children's face-building puzzle game. The player sees a **finished example face**, a **blank face base**
(head, ears, neck, cheeks only), and a tray of **loose facial features**. They drag each feature onto the
blank face to recreate the example. Pieces are split by **whole facial feature** (eye, eye, nose, mouth,
hair locks, hat, bow tie…), never jigsaw sections. Inspired by a physical magnetic toy — see
`art/reference/gameplay-concept-clown-box.png`.

## Owner
The owner is the game designer, not a programmer. Explain technical decisions in plain language,
keep replies short, and ask before making big design choices.

## Tech decisions (agreed)
- **Engine: Godot 4 (GDScript, 2D).** Not Three.js — it's a rendering library, not a game engine.
  Do not use C# (Godot 4 C# cannot export to web).
- **Targets:** iOS/iPadOS and Android (primary, native exports), Web (secondary, single-threaded
  export, Compatibility renderer; test Safari).
- **Art: Blender** is the art workshop only. The game loads exported **transparent PNG pieces**, not
  `.blend` files. See `.github/skills/blender-art-pipeline/SKILL.md`.

## Rules
- Child-friendly: large touch targets, forgiving snap-to-place, no failure states, no timers by default,
  encouraging feedback, no ads/accounts/tracking in v1, works offline.
- One multi-feature piece = one draggable node (e.g. an eye includes white + iris + pupil + highlight).
- Keep the Blender generation scripts reproducible; never hand-edit exported PNGs.
- Don't commit build outputs (`build/`, `.godot/`, exports).
