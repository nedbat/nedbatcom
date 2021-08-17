import os
import sys

import bpy

qual = int(os.environ.get("QUAL", 0))

scene = bpy.data.scenes[0]
scene.cycles.samples = [100, 500, 1000][qual]
scene.cycles.max_bounces = [10, 20, 20][qual]
scene.cycles.tile_order = "BOTTOM_TO_TOP"   # Better estimate of ETA
scene.render.resolution_percentage = [50, 200, 400][qual]
scene.render.threads_mode = "FIXED"
scene.render.threads = os.cpu_count() - 1   # Leave me something

scene.render.filepath = "./dodeca3_transparent.png"
bpy.ops.render.render(write_still=True)
