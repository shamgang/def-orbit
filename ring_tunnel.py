import bpy
from mathutils import Vector
from mathutils import Color
import time

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


torus = bpy.data.objects['Torus']
scene = bpy.data.scenes['Scene']
c = Color()
numtor = 50
for i in range(1,numtor+1):
    name = 'Torus' + str(i)
    newtorus = duplicateObject(scene, name, torus)
    newtorus.location = Vector((0, 0, -20*i))
    matname = 'TorMat' + str(i)
    newmat = bpy.data.materials.new(matname)
    c.hsv = float(i-1) / float(numtor), 1.0, 0.735
    newmat.diffuse_color = c.r, c.g, c.b
    newmat.emit = 1.
    newtorus.active_material = newmat
    newconstraint = newtorus.constraints.new('CHILD_OF')
    newconstraint.target = torus
    newconstraint.use_scale_x = False
    newconstraint.use_scale_y = False
    newconstraint.use_scale_z = False
