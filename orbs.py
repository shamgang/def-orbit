import bpy
from mathutils import Vector
from mathutils import Color
import time
import random

def duplicateObject(scene, name, copyobj):
 
    # Create new mesh
    mesh = bpy.data.meshes.new(name)
 
    # Create new object associated with the mesh
    ob_new = bpy.data.objects.new(name, mesh)
 
    # Copy data block from the old object into the new object
    ob_new.data = copyobj.data.copy()
    ob_new.scale = copyobj.scale
    ob_new.location = copyobj.location
    
    # Link new object to the given scene and select it
    scene.objects.link(ob_new)
    ob_new.select = True
 
    return ob_new

# delete all pre-existing orbs besides the original
for obj in bpy.context.scene.objects:
    obj.select = ( obj.name[:3] == "Orb" or obj.name[:5] == "Glass") and ( obj.name != "Orb" and obj.name != "Glass")
    bpy.ops.object.delete()

orb = bpy.data.objects['Orb']
glass = bpy.data.objects['Glass']
scene = bpy.data.scenes['Scene']
c = Color()
numorb = 150
random.seed(0)
for i in range(1, numorb+1):
    name = 'Orb' + str(i)
    glassname = 'Glass' + str(i)
    neworb = duplicateObject(scene, name, orb)
    neworb.location = Vector((-20+40*random.random(), -20+40*random.random(), 20*random.random()))
    newglass = duplicateObject(scene, glassname, glass)
    newglass.location = neworb.location
    matname = 'OrbMat' + str(i)
    newmat = bpy.data.materials.new(matname)
    c.hsv = random.random(), 1.0, 0.735
    newmat.diffuse_color = c.r, c.g, c.b
    newmat.emit = 0.
    neworb.active_material = newmat
