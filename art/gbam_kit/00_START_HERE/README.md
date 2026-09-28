# GBAM Character Kit v1

This is the production handoff package for building a unique modular 3D character family in Blender.

## Core idea
The characters should feel:
- playful
- warm
- African-led and globally inclusive
- handmade rather than hyper-polished
- simple enough for games and animation
- recognisable as one family even when hairstyles, skin tones, clothes, ages, and accessories change

The signature visual language is:
1. oversized rounded head
2. large expressive eyes
3. circular/oval cheek accents
4. simple geometric nose
5. wide friendly mouth
6. chunky graphic hair shapes
7. matte, softly textured materials
8. mild intentional asymmetry
9. clean silhouettes
10. strong colour blocking

## Copyright/design rule
Do NOT recreate any commercial toy, packaging, illustration, animation studio, or named artist style.
The supplied images in `01_REFERENCE_IMAGES/OWN_STYLE_PRIMARY` are the main visual references.
Use the general concept of modular face parts, but keep the shapes, proportions, palette, clothing, hairstyles, and facial construction specific to this GBAM design system.

## Recommended Blender target
- Blender 4.x
- Metric units
- 1 Blender Unit = 1 metre
- Character forward = -Y
- Up = +Z
- Character right = +X
- Apply transforms before export
- Keep every swappable part as a separate named object until final optimisation

## Build order
Read:
1. `AI_MASTER_BRIEF.txt`
2. `AI_TASK_SEQUENCE.md`
3. `../02_STYLE_SYSTEM/STYLE_BIBLE.md`
4. `../02_STYLE_SYSTEM/DIMENSIONS.csv`
5. `../03_BASE_MESH/*`
6. the relevant face/hair/clothing file
7. rig/export rules
