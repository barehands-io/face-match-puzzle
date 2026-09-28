
import bpy

# GBAM Character Kit v1 - Blender scene bootstrap

# Units
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

# Render
scene.render.engine = 'BLENDER_EEVEE' if bpy.app.version >= (5, 0, 0) else 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.fps = 24

# World
scene.world.color = (0.18, 0.42, 0.34)

# Collections
collection_names = [
    "00_REFERENCE",
    "01_BASE",
    "02_FACE",
    "03_HAIR_HEADWEAR",
    "04_CLOTHING",
    "05_ACCESSORIES",
    "06_RIG",
    "07_LIGHTS_CAMERAS",
    "08_EXPORT",
]
for name in collection_names:
    if name not in bpy.data.collections:
        coll = bpy.data.collections.new(name)
        scene.collection.children.link(coll)

# Delete default camera/light only if present and recreate a simple studio rig
for obj_name in ["Camera", "Light"]:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

lights_coll = bpy.data.collections.get("07_LIGHTS_CAMERAS")

def link_only(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)

# Camera
cam_data = bpy.data.cameras.new("CAM_PORTRAIT_DATA")
cam = bpy.data.objects.new("CAM_PORTRAIT", cam_data)
lights_coll.objects.link(cam)
scene.camera = cam
cam.location = (0.0, -3.2, 1.45)
cam.rotation_euler = (1.5708, 0.0, 0.0)
cam.data.lens = 80

# Key
for name, loc, energy, size in [
    ("LIGHT_KEY", (-1.5, -2.2, 2.7), 900, 2.0),
    ("LIGHT_FILL", (1.7, -1.8, 2.2), 380, 2.4),
    ("LIGHT_RIM", (0.7, 1.3, 2.8), 300, 1.8),
]:
    data = bpy.data.lights.new(name + "_DATA", type='AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    lights_coll.objects.link(obj)

# Empty head-origin guide
empty = bpy.data.objects.new("GUIDE_HEAD_ORIGIN", None)
empty.empty_display_type = 'SPHERE'
empty.empty_display_size = 0.03
bpy.data.collections["01_BASE"].objects.link(empty)

print("GBAM Character Kit scene created.")
print("Units: Metric, 1 BU = 1 m")
print("Character forward convention: -Y, up: +Z")
