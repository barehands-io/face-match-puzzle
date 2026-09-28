# Game Export Specification

Preferred interchange:
- GLB / glTF 2.0
Fallback:
- FBX

Before export:
- apply scale and rotation
- character root at world origin
- +Z up
- character faces -Y in Blender source
- verify exporter/engine forward-axis conversion
- no duplicate hidden meshes
- remove unused materials
- pack or copy textures
- armature scale = 1
- no non-manifold accidental geometry
- check normals
- keep animation names simple ASCII

Textures:
- PNG
- 1024 or 2048 square
- use atlas where practical
