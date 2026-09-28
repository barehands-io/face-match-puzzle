# Blender Material Specification

Use Principled BSDF.

## Skin
- Metallic: 0
- Roughness: 0.58–0.72
- Specular/IOR: standard dielectric
- Subsurface: optional 0.00–0.04 only
- no pore normal map

## Eyes
Sclera:
- Roughness: 0.32–0.45
Iris/pupil:
- Roughness: 0.28–0.40
Optional cornea:
- very simple clear outer shell if needed, not mandatory for mobile

## Hair
- Roughness: 0.62–0.80
- subtle warm highlight
- no anisotropic strand rendering required

## Clothing
- Roughness: 0.65–0.85
- mild normal/roughness grain

## Texture size
Hero close-up:
- 2048 px per character atlas
Mobile/general:
- 1024–2048 px
Shared accessories:
- 1024 px atlas

Suggested maps:
- Base Color
- Roughness
- optional Normal
- optional baked AO
No metallic map unless an actual metal accessory exists.
