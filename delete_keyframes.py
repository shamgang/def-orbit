import bpy

for obj in bpy.data.objects:
    obj.animation_data_clear()
    
for lamp in bpy.data.lamps:
    lamp.animation_data_clear()