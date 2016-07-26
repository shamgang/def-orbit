import bpy

# delete all pre-existing rings besides the original
for obj in bpy.context.scene.objects:
    obj.select = ( obj.name[:5] == "Torus" ) and ( obj.name != "Torus" )

bpy.ops.object.delete()