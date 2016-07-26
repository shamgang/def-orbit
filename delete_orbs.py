import bpy

# delete all pre-existing orbs besides the original
for obj in bpy.context.scene.objects:
    obj.select = ( obj.name[:3] == "Orb" or obj.name[:5] == "Glass") and ( obj.name != "Orb" and obj.name != "Glass")
    
bpy.ops.object.delete()