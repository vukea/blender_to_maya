import bpy

class MaterialFaceAssignments:
    @staticmethod
    def split_objects_by_material():
        # Loop through all mesh objects in the scene
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and len(obj.material_slots) > 1:
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.separate(type='MATERIAL')  # Separate by material
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.select_set(False)

# Usage
MaterialFaceAssignments.split_objects_by_material()
