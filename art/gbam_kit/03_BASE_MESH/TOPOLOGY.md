# Topology Targets

For real-time/mobile-friendly LOD0:
- full character total: 25k–45k triangles
- head + face: 8k–14k
- hair/headwear: 4k–12k
- clothing/body: 10k–18k

LOD1: 12k–20k total
LOD2: 5k–8k total

Rules:
- preserve silhouette before internal detail
- do not spend polygons on flat cheek patches
- use curves converted to mesh for braids, then optimise
- avoid overlapping hidden geometry under hijab/hats
- keep the eye globes smooth enough to rotate without faceting
