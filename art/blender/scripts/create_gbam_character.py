"""Build GBAM portrait prototypes using the supplied kit's passes 1-4.

Blender --background --factory-startup --python this_file.py -- --character all
Use --no-render to save scenes only; --verify-only reopens and checks saved files.
Rigging, deformation topology, full bodies and game exports are later passes.
"""

import argparse
import csv
import hashlib
import math
from pathlib import Path
import random
import runpy
import sys

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[3]
KIT = ROOT / "art/gbam_kit"
OUTPUT = ROOT / "art/blender"
RENDERS = ROOT / "art/renders"
CHARACTERS = {
    "boy": ("CHR_M_001_COILS_YELLOW", "SKIN_WARM_MEDIUM"),
    "girl": ("CHR_F_001_PUFFS_OVERALLS", "SKIN_WARM_BROWN"),
}
PALETTE = dict(line.split() for line in
               (KIT / "07_MATERIALS/palette.hex.txt").read_text().splitlines() if line.strip())
with (KIT / "02_STYLE_SYSTEM/ANCHORS.csv").open(newline="") as source:
    ANCHORS = {row["Anchor"]: tuple(float(row[key]) for key in ("X_m", "Y_m", "Z_m"))
               for row in csv.DictReader(source)}
HEAD_SIZE = (0.440, 0.400, 0.500)


def srgb(hex_color):
    values = [int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
                 for v in values) + (1,)


def material(key, roughness=0.67, hex_color=None):
    mat = bpy.data.materials.new("MAT_" + key)
    mat.diffuse_color = srgb(hex_color or PALETTE[key])
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = mat.diffuse_color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = 0
    return mat


def group(name, parent, piece_id=None):
    coll = bpy.data.collections.new(name)
    bpy.data.collections[parent].children.link(coll)
    coll["draggable"] = piece_id is not None
    if piece_id:
        coll["piece_id"] = piece_id
    return coll


def put(obj, name, coll, mat=None):
    obj.name = name
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    coll.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    obj["gbam_fit_head"] = "HEAD_V1"
    obj["gbam_variant_id"] = name
    obj["gbam_age_group"] = "child_portrait"
    obj["gbam_lod"] = "PROTOTYPE"
    obj["gbam_part_type"] = coll.name
    return obj


def smooth(obj):
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


def ellipsoid(name, center, size, mat, coll, segments=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=center)
    obj = bpy.context.object
    for vert in obj.data.vertices:
        vert.co.x *= size[0] / 2
        vert.co.y *= size[1] / 2
        vert.co.z *= size[2] / 2
    return smooth(put(obj, name, coll, mat))


def tube(name, points, radius, mat, coll, cyclic=False):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 16
    curve.bevel_depth = radius
    curve.bevel_resolution = 4
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    spline.use_cyclic_u = cyclic
    for control, point in zip(spline.bezier_points, points):
        control.co = point
        control.handle_left_type = "AUTO"
        control.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    coll.objects.link(obj)
    return put(obj, name, coll, mat)


def plaque(name, outline, depth, mat, coll, bevel=0.002, thickness=0.003):
    """Rounded, shallow face module; outline is authored in head-local X/Z."""
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "2D"
    curve.resolution_u = 24
    curve.fill_mode = "BOTH"
    curve.extrude = thickness / 2
    curve.bevel_depth = bevel
    curve.bevel_resolution = 4
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(outline) - 1)
    spline.use_cyclic_u = True
    for control, (x, z) in zip(spline.bezier_points, outline):
        control.co = (x, z, 0)
        control.handle_left_type = "AUTO"
        control.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    coll.objects.link(obj)
    obj.rotation_euler.x = math.pi / 2
    obj.location.y = depth
    return put(obj, name, coll, mat)


def front_y(x, z):
    taper = 1 - 0.13 * max(0, -z / 0.25) ** 1.3
    return -0.2 * max(0.001, 1 - abs(x / (0.22 * taper)) ** 3.2
                     - abs(z / 0.25) ** 3.2) ** (1 / 3.2)


def build_head(mat):
    """One deterministic quad cage, shared unchanged by both skin variants."""
    coll = bpy.data.collections["01_BASE"]
    bpy.ops.mesh.primitive_cube_add(size=2)
    head = bpy.context.object
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.subdivide(number_cuts=25)
    bpy.ops.object.mode_set(mode="OBJECT")
    for vert in head.data.vertices:
        point = vert.co
        factor = sum(abs(v) ** 3.2 for v in point) ** (1 / 3.2)
        point /= factor
        taper = 1 - 0.13 * max(0, -point.z) ** 1.3
        point.x *= 0.22 * taper
        point.y *= 0.20
        point.z *= 0.25
    smooth(put(head, "MESH_HEAD_BASE", coll, mat))
    head.data.name = "HEAD_V1_SHARED_NEUTRAL_QUADS"
    head["canonical_dimensions_m"] = list(HEAD_SIZE)
    head["topology_status"] = "Portrait cage only; facial deformation loops deferred."
    head["geometry_sha256"] = head_digest(head)
    return head


def head_digest(head):
    return hashlib.sha256(
        repr([tuple(round(v, 8) for v in vertex.co) for vertex in head.data.vertices]).encode()
    ).hexdigest()


def build_base(skin, m):
    head = build_head(skin)
    base = bpy.data.collections["01_BASE"]
    ellipsoid("MESH_NECK_BASE", (0, 0.025, -0.285), (0.115, 0.125, 0.155), skin, base)
    ears = group("BASE_EARS_01", "01_BASE")
    cheeks = group("BASE_CHEEKS_01", "01_BASE")
    for side, sign in (("L", -1), ("R", 1)):
        x, y, z = ANCHORS["EAR_" + side]
        ellipsoid("MESH_EAR_" + side, (x, y, z), (0.095, 0.035, 0.115), skin, ears)
        points = [(x + sign * dx, -0.030, z + dz) for dx, dz in (
            (0.013, -0.029), (0.029, -0.017), (0.031, 0.015),
            (0.016, 0.032), (-0.004, 0.020))]
        tube("MESH_EAR_INNER_C_" + side, points, 0.006, m["ear"], ears)
        ellipsoid("MESH_EAR_TRAGUS_" + side, (x + sign * 0.002, -0.034, z - 0.012),
                  (0.024, 0.014, 0.024), skin, ears)
        cx, _, cz = ANCHORS["CHEEK_" + side]
        cz += 0.0015 if sign > 0 else 0
        # Project the thin patch onto the head instead of floating a flat disc.
        vertices = [(cx, front_y(cx, cz) - 0.002, cz)]
        rings, count = 5, 48
        for ring in range(1, rings + 1):
            for i in range(count):
                angle = math.tau * i / count
                x = cx + 0.036 * ring / rings * math.cos(angle)
                z = cz + 0.033 * ring / rings * math.sin(angle)
                vertices.append((x, front_y(x, z) - 0.002, z))
        faces = [(0, 1 + i, 1 + (i + 1) % count) for i in range(count)]
        for ring in range(rings - 1):
            a = 1 + ring * count
            b = a + count
            for i in range(count):
                j = (i + 1) % count
                faces.append((a + i, b + i, b + j, a + j))
        mesh = bpy.data.meshes.new("CHEEK_PATCH_" + side)
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        obj = bpy.data.objects.new("MESH_CHEEK_" + side, mesh)
        cheeks.objects.link(obj)
        smooth(put(obj, obj.name, cheeks, m["CHEEK_CORAL"]))
    return head


def build_face(skin, m):
    for side, sign in (("L", -1), ("R", 1)):
        eye = group("EYE_02_WIDE_" + side, "02_FACE", "eye_" + side.lower())
        x, _, z = ANCHORS["EYE_" + side]
        # Wide variant: +20% width/+10% height over the canonical round globe.
        ellipsoid("MESH_EYE_" + side, (x, -0.197, z),
                  (0.0936, 0.048, 0.0858), m["EYE_WHITE"], eye)
        ellipsoid("MESH_IRIS_" + side, (x + 0.003, -0.220, z + 0.001),
                  (0.038, 0.009, 0.038), m["iris"], eye)
        ellipsoid("MESH_PUPIL_" + side, (x + 0.003, -0.225, z + 0.001),
                  (0.020, 0.005, 0.020), m["HAIR_NEAR_BLACK"], eye)
        ellipsoid("MESH_CATCHLIGHT_" + side, (x - 0.003, -0.229, z + 0.008),
                  (0.009, 0.004, 0.009), m["EYE_WHITE"], eye)
        brow = group("BROW_01_" + side, "02_FACE", "brow_" + side.lower())
        offset = 0.003 if side == "R" else 0
        points = [(x - 0.043, -0.192, 0.106 + offset),
                  (x - 0.010, -0.203, 0.121 + offset),
                  (x + 0.030, -0.197, 0.117 + offset),
                  (x + 0.043, -0.192, 0.111 + offset)]
        tube("MESH_BROW_" + side, points, 0.009, m["HAIR_NEAR_BLACK"], brow)
    nose = group("NOSE_02_WEDGE", "02_FACE", "nose")
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    for vert in obj.data.vertices:
        x, y, z = vert.co
        width = 0.036 if z > 0 else 0.075
        vert.co = (x * width, y * 0.060 + (0.016 if z > 0 else 0),
                   z * 0.110)
    obj.location = (0, -0.215, -0.013)
    put(obj, "MESH_NOSE_02_WEDGE", nose, skin)
    bevel = obj.modifiers.new("Soft graphic wedge corners", "BEVEL")
    bevel.width = 0.016
    bevel.segments = 5
    obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    smooth(obj)
    mouth = group("MOUTH_03_OPEN_HAPPY", "02_FACE", "mouth")
    outline = [(-0.085, -0.084), (-0.044, -0.088), (0.008, -0.090),
               (0.080, -0.081), (0.075, -0.113), (0.040, -0.145),
               (-0.015, -0.148), (-0.061, -0.126)]
    plaque("MESH_MOUTH_LIP", outline, -0.195, m["lip"], mouth, bevel=0.005)
    inset = [(x * 0.92, -0.111 + (z + 0.111) * 0.85) for x, z in outline]
    plaque("MESH_MOUTH_INTERIOR", inset, -0.202, m["MOUTH_DARK"], mouth)
    teeth = [(-0.064, -0.091), (-0.028, -0.094), (0.023, -0.094),
             (0.064, -0.088), (0.057, -0.105), (0.011, -0.111),
             (-0.031, -0.110), (-0.059, -0.103)]
    plaque("MESH_UPPER_TEETH_BLOCK", teeth, -0.208, m["EYE_WHITE"], mouth, bevel=0.0015)
    for i, x in enumerate((-0.027, 0.008, 0.041)):
        tube(f"MESH_TOOTH_DIVISION_{i}", [(x, -0.212, -0.095), (x, -0.212, -0.108)],
             0.00065, m["CREAM"], mouth)
    plaque("MESH_TONGUE", [(-0.026, -0.138), (-0.012, -0.127), (0.017, -0.128),
                          (0.032, -0.138), (0.005, -0.143)],
           -0.208, m["CORAL"], mouth, bevel=0.001)


def signed_power(value, exponent):
    return math.copysign(abs(value) ** exponent, value)


def scalp_point(phi, theta):
    return Vector((0.225 * math.sin(phi) ** 0.625 * signed_power(math.sin(theta), 0.625),
                   -0.207 * math.sin(phi) ** 0.625 * signed_power(math.cos(theta), 0.625),
                   0.258 * signed_power(math.cos(phi), 0.625)))


def scalp_extent(theta):
    return 1.43 - 0.30 * max(0, math.cos(theta))


def build_scalp(coll, m):
    vertices = [(0, 0, 0.258)]
    count, rows = 64, 14
    for row in range(1, rows + 1):
        for i in range(count):
            theta = math.tau * i / count
            maximum = scalp_extent(theta)
            vertices.append(tuple(scalp_point(maximum * row / rows, theta)))
    faces = [(0, 1 + (i + 1) % count, 1 + i) for i in range(count)]
    for row in range(rows - 1):
        a = 1 + row * count
        b = a + count
        for i in range(count):
            j = (i + 1) % count
            faces.append((a + i, a + j, b + j, b + i))
    mesh = bpy.data.meshes.new("HAIR_CAP_SHARED")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("MESH_HAIR_CAP", mesh)
    coll.objects.link(obj)
    smooth(put(obj, obj.name, coll, m["HAIR_NEAR_BLACK"]))
    solidify = obj.modifiers.new("Scalp shell", "SOLIDIFY")
    solidify.thickness = 0.004


def clump(name, center, size, coll, m, rng):
    obj = ellipsoid(name, center, size, m, coll, segments=20, rings=12)
    phase = rng.uniform(0, math.tau)
    for vert in obj.data.vertices:
        p = vert.co
        angle = math.atan2(p.y / size[1], p.x / size[0])
        latitude = p.z / (size[2] / 2)
        p *= 1 + 0.065 * math.cos(5 * angle + phase) * (1 - latitude * latitude)
    return obj


def build_hair(character, m):
    rng = random.Random(20260928)
    if character == "boy":
        coll = group("HAIR_COILS_SHORT_01", "03_HAIR_HEADWEAR", "hair_coils")
        build_scalp(coll, m)
        for row, count in enumerate((1, 12, 20, 26, 32, 38, 42, 46)):
            for i in range(count):
                theta = math.tau * (i + 0.45 * (row % 2)) / count
                maximum = scalp_extent(theta)
                phi = 0.01 if row == 0 else maximum * row / 7
                center = scalp_point(phi, theta)
                center += Vector((center.x, center.y, center.z)).normalized() * 0.006
                size = rng.uniform(0.058, 0.066)
                clump(f"MESH_COIL_{row:02d}_{i:02d}", center,
                      (size, size * 0.92, size * 0.84), coll,
                      m["hair_warm"] if i % 5 == 0 else m["HAIR_NEAR_BLACK"], rng)
    else:
        cap = group("HAIR_PUFFS_CAP_01", "03_HAIR_HEADWEAR", "hair_cap")
        build_scalp(cap, m)
        for sign in (-1, 1):
            for index in range(5):
                points = []
                for t in (0, 0.25, 0.5, 0.75, 1):
                    theta = sign * (0.10 + index * 0.21 + t * 0.24)
                    points.append(scalp_point(scalp_extent(theta) * (0.18 + t * 0.76), theta))
                points = [tuple(point + point.normalized() * 0.004) for point in points]
                tube(f"MESH_SWEPT_HAIR_{sign}_{index}", points, 0.0025,
                     m["hair_warm"], cap)
        for side, sign in (("L", -1), ("R", 1)):
            coll = group("HAIR_PUFF_BUN_" + side, "03_HAIR_HEADWEAR",
                         "hair_puff_" + side.lower())
            center = Vector((sign * 0.226, 0.006, 0.223 + (0.006 if sign > 0 else 0)))
            clump("MESH_PUFF_MASS_" + side, center, (0.231, 0.203, 0.223),
                  coll, m["HAIR_NEAR_BLACK"], rng)
            count = 86
            for i in range(count):
                z = 1 - 2 * (i + 0.5) / count
                theta = i * math.pi * (3 - math.sqrt(5))
                radius = math.sqrt(1 - z * z)
                delta = Vector((0.103 * radius * math.cos(theta),
                                0.088 * radius * math.sin(theta), 0.100 * z))
                size = rng.uniform(0.062, 0.076)
                clump(f"MESH_PUFF_{side}_COIL_{i:02d}", center + delta,
                      (size, size * 0.92, size), coll,
                      m["hair_warm"] if i % 6 == 0 else m["HAIR_NEAR_BLACK"], rng)
            flower = Vector((sign * 0.211, -0.122, 0.202))
            for petal in range(5):
                theta = math.tau * petal / 5
                offset = Vector((math.sin(theta) * 0.022, 0, math.cos(theta) * 0.022))
                obj = ellipsoid(f"MESH_FLOWER_{side}_PETAL_{petal}", flower + offset,
                                (0.020, 0.012, 0.034), m["PINK"], coll)
                obj.rotation_euler.y = theta
            ellipsoid("MESH_FLOWER_" + side + "_CENTER", flower + Vector((0, -0.009, 0)),
                      (0.021, 0.013, 0.021), m["YELLOW"], coll)


def build_portrait_clothing(character, m):
    """Only the visible shoulder colour blocks, not full-body clothing assets."""
    coll = bpy.data.collections["04_CLOTHING"]
    coll["portrait_only"] = True
    if character == "boy":
        ellipsoid("MESH_TOP_HOODIE_PORTRAIT", (0, 0.025, -0.459),
                  (0.405, 0.225, 0.310), m["YELLOW"], coll)
        ellipsoid("MESH_HOOD_BACK_PORTRAIT", (0, 0.052, -0.338),
                  (0.294, 0.178, 0.155), m["YELLOW"], coll)
        tube("MESH_HOOD_ROLLED_EDGE",
             [(-0.135, 0.012, -0.322), (-0.111, -0.086, -0.332),
              (-0.052, -0.107, -0.351), (0, -0.108, -0.362),
              (0.062, -0.107, -0.345), (0.130, -0.055, -0.328),
              (0.119, 0.070, -0.290), (0, 0.102, -0.281),
              (-0.119, 0.070, -0.290)],
             0.027, m["YELLOW"], coll, cyclic=True)
        for sign in (-1, 1):
            tube(f"MESH_HOOD_DRAWSTRING_{sign}",
                 [(sign * 0.044, -0.127, -0.357), (sign * 0.048, -0.131, -0.417)],
                 0.004, m["CREAM"], coll)
    else:
        ellipsoid("MESH_CORAL_SHIRT_PORTRAIT", (0, 0.025, -0.459),
                  (0.405, 0.225, 0.310), m["CORAL"], coll)
        plaque("MESH_OVERALL_BIB_PORTRAIT",
               [(-0.106, -0.373), (0.106, -0.373), (0.110, -0.550), (-0.110, -0.550)],
               -0.102, m["OLIVE"], coll, bevel=0.009, thickness=0.006)
        for sign in (-1, 1):
            tube(f"MESH_OVERALL_STRAP_{sign}",
                 [(sign * 0.118, -0.035, -0.326), (sign * 0.110, -0.088, -0.352),
                  (sign * 0.082, -0.114, -0.405)],
                 0.016, m["OLIVE"], coll)
            ellipsoid(f"MESH_OVERALL_BUTTON_{sign}", (sign * 0.082, -0.133, -0.402),
                      (0.024, 0.009, 0.024), m["YELLOW"], coll)


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new("GBAM_MINT_STUDIO")
    runpy.run_path(str(KIT / "12_BLENDER_AUTOMATION/setup_character_project.py"))
    studio = bpy.data.collections["07_LIGHTS_CAMERAS"]
    camera = scene.camera
    camera.location = (0, -3.2, 0.002)
    camera.rotation_euler = (Vector((0, 0, 0.002)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 0.86
    # The supplied bootstrap leaves light rotations at zero; aim them at the head.
    for name, energy, height in (("LIGHT_KEY", 160, 1.6),
                                ("LIGHT_FILL", 65, 0.5), ("LIGHT_RIM", 50, 1.8)):
        obj = bpy.data.objects[name]
        obj.location.z = height
        obj.rotation_euler = (-obj.location).to_track_quat("-Z", "Y").to_euler()
        obj.data.energy = energy
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.65, 0.72, 0.68, 1)
    background.inputs["Strength"].default_value = 0.35
    backdrop = material("BACKDROP", 1.0, "#BDDCCD")
    # Unlit backdrop keeps complete/blank portraits the same clean pastel colour.
    nodes = backdrop.node_tree.nodes
    nodes.clear()
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = backdrop.diffuse_color
    output = nodes.new("ShaderNodeOutputMaterial")
    backdrop.node_tree.links.new(emission.outputs[0], output.inputs["Surface"])
    plaque("STUDIO_BACKDROP", [(-2, -2), (2, -2), (2, 2), (-2, 2)],
           0.6, backdrop, studio, bevel=0, thickness=0)
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 8
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    return scene


def build(character):
    scene = setup()
    identifier, skin_key = CHARACTERS[character]
    scene.name = identifier
    scene["character_id"] = identifier
    scene["gbam_passes"] = "1 bootstrap; 2 shared head; 3 required face modules; 4 coils/puffs"
    scene["scope"] = "Portrait prototypes only; full face/hair libraries, rig, UV/LOD/export deferred."
    scene["blank_base"] = "Hide 02_FACE and 03_HAIR_HEADWEAR; keep ears, cheeks, neck and outfit."
    scene["eye_variant"] = "EYE_02_WIDE: round globe width x1.20, height x1.10 for phone readability."
    scene["skin_palette"] = skin_key
    m = {key: material(key, 0.38 if key == "EYE_WHITE" else
                       0.74 if key == "HAIR_NEAR_BLACK" else 0.67)
         for key in ("EYE_WHITE", "HAIR_NEAR_BLACK", "MOUTH_DARK", "CREAM",
                     "CHEEK_CORAL", "CORAL", "PINK", "YELLOW", "OLIVE")}
    m["iris"] = material("IRIS_BROWN", 0.36, "#643A22")
    m["ear"] = material("EAR_INNER", 0.70, "#854023")
    m["lip"] = material("LIP_WARM", 0.70, "#8F3826")
    m["hair_warm"] = material("HAIR_WARM", 0.75, "#362017")
    skin = material(skin_key, 0.67)
    head = build_base(skin, m)
    build_face(skin, m)
    build_hair(character, m)
    build_portrait_clothing(character, m)
    for script in (Path(__file__), KIT / "12_BLENDER_AUTOMATION/setup_character_project.py"):
        bpy.data.texts.new(script.name).write(script.read_text())
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    head.select_set(True)
    bpy.context.view_layer.objects.active = head
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
                area.spaces.active.overlay.show_overlays = False
    scene.render.filepath = str(RENDERS / f"gbam-{character}-portrait.png")
    scene["object_count"] = len(scene.objects)
    scene["collection_count"] = len(bpy.data.collections)
    bpy.context.view_layer.update()
    return scene


def verify(character):
    scene = bpy.context.scene
    assert scene["character_id"] == CHARACTERS[character][0]
    assert scene.unit_settings.system == "METRIC"
    assert scene.unit_settings.scale_length == 1
    assert (scene.render.resolution_x, scene.render.resolution_y) == (1024, 1024)
    assert scene.render.resolution_percentage == 100
    assert scene.camera.data.type == "ORTHO"
    assert abs(scene.camera.data.ortho_scale - 0.86) < 1e-6
    assert len(scene.objects) == scene["object_count"]
    assert len(bpy.data.collections) == scene["collection_count"]
    head = bpy.data.objects["MESH_HEAD_BASE"]
    with (KIT / "02_STYLE_SYSTEM/DIMENSIONS.csv").open(newline="") as source:
        dimensions = next(row for row in csv.DictReader(source)
                          if row["Asset/feature"] == "Base head")
    assert HEAD_SIZE == tuple(float(dimensions[key]) for key in
                              ("Width_m", "Depth_or_thickness_m", "Height_m"))
    assert all(abs(value - target) < 0.001 for value, target in zip(head.dimensions, HEAD_SIZE))
    assert 3000 <= len(head.data.polygons) <= 6000
    assert all(len(poly.vertices) == 4 for poly in head.data.polygons)
    assert head_digest(head) == head["geometry_sha256"]
    pieces = {coll["piece_id"]: coll for coll in bpy.data.collections if coll.get("draggable")}
    expected = {"eye_l", "eye_r", "brow_l", "brow_r", "nose", "mouth"}
    expected |= {"hair_coils"} if character == "boy" else {"hair_cap", "hair_puff_l", "hair_puff_r"}
    assert set(pieces) == expected, set(pieces)
    for coll in pieces.values():
        assert len(coll.objects) > 0
        assert all(len(obj.users_collection) == 1 for obj in coll.objects)
    for side in ("L", "R"):
        assert len(pieces["eye_" + side.lower()].objects) == 4
        assert bpy.data.objects["MESH_CHEEK_" + side].users_collection[0].name == "BASE_CHEEKS_01"
        eye = bpy.data.objects["MESH_EYE_" + side]
        anchor = ANCHORS["EYE_" + side]
        assert abs(eye.location.x - anchor[0]) < 1e-6
        assert abs(eye.location.z - anchor[2]) < 1e-6
    skin = head.data.materials[0]
    assert all(abs(a - b) < 1e-6 for a, b in
               zip(skin.diffuse_color, srgb(PALETTE[CHARACTERS[character][1]])))
    for key in ("02_FACE", "03_HAIR_HEADWEAR"):
        assert not bpy.data.collections[key].hide_render
    assert not any(obj.type == "ARMATURE" for obj in scene.objects)
    assert bpy.data.texts[Path(__file__).name].as_string() == Path(__file__).read_text()
    assert bpy.data.texts["setup_character_project.py"].as_string() == (
        KIT / "12_BLENDER_AUTOMATION/setup_character_project.py").read_text()
    print(f"VERIFIED {scene.name}: {len(head.data.polygons)} head quads, "
          f"{len(pieces)} complete pieces; head={head_digest(head)}", flush=True)
    return head_digest(head)


def verify_images(character):
    for kind in ("portrait", "blank"):
        path = RENDERS / f"gbam-{character}-{kind}.png"
        image = bpy.data.images.load(str(path), check_existing=False)
        assert tuple(image.size) == (1024, 1024), path
        assert image.channels == 4, path
        assert path.stat().st_size > 20000, path
        bpy.data.images.remove(image)
    print(f"VERIFIED {character}: full-size portrait and blank RGBA PNGs", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", choices=("boy", "girl", "all"), default="all")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--no-render", action="store_true")
    mode.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    hashes = []
    for character in CHARACTERS if args.character == "all" else (args.character,):
        path = OUTPUT / f"gbam-{character}-portrait.blend"
        if not args.verify_only:
            scene = build(character)
            verify(character)
            bpy.context.preferences.filepaths.save_version = 0
            bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path))
        hashes.append(verify(character))
        if not args.no_render and not args.verify_only:
            scene = bpy.context.scene
            bpy.ops.render.render(write_still=True)
            for name in ("02_FACE", "03_HAIR_HEADWEAR"):
                bpy.data.collections[name].hide_render = True
            scene.render.filepath = str(RENDERS / f"gbam-{character}-blank.png")
            bpy.ops.render.render(write_still=True)
            for name in ("02_FACE", "03_HAIR_HEADWEAR"):
                bpy.data.collections[name].hide_render = False
            print(f"RENDERED {character}: portrait and blank base", flush=True)
        if not args.no_render:
            verify_images(character)
    assert len(set(hashes)) == 1, "Both characters must use the identical neutral head mesh"


if __name__ == "__main__":
    main()
