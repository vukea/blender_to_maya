import bpy
import re

class MayaNamingConvention:
    def __init__(self):
        # Define the datablocks we want to rename
        self.data_blocks = {
            "obj": bpy.data.objects,
            "mat": bpy.data.materials,
            "col": bpy.data.collections,
            "mesh": bpy.data.meshes,
            "curve": bpy.data.curves,
            "arm": bpy.data.armatures,
            "cam": bpy.data.cameras,
            "light": bpy.data.lights,
            "img": bpy.data.images,
            "tex": bpy.data.textures,
            "ng": bpy.data.node_groups,
            "act": bpy.data.actions,
        }

    @staticmethod
    def clean_name(name: str, prefix: str = "item") -> str:
        """Cleans the name to only English letters, numbers, and underscores"""
        # Keep only A-Z, a-z, 0-9 and underscores
        name = re.sub(r'[^A-Za-z0-9_]', '_', name)
        # Collapse multiple underscores
        name = re.sub(r'_+', '_', name)
        # Remove leading/trailing underscores
        name = name.strip('_')
        # Prepend prefix if name starts with number or underscore
        if not name or re.match(r'^[^A-Za-z]', name):
            name = f"{prefix}_{name}"
        return name

    @staticmethod
    def ensure_unique(name: str, existing_names: set) -> str:
        """Appends _01, _02, etc., if name already exists"""
        if name not in existing_names:
            existing_names.add(name)
            return name

        counter = 1
        new_name = f"{name}_{counter:02d}"
        while new_name in existing_names:
            counter += 1
            new_name = f"{name}_{counter:02d}"
        existing_names.add(new_name)
        return new_name

    # Calls the Code
    def rename_all(self):
        """Rename all objects, materials, collections, etc., in the scene"""
        for prefix, datablock in self.data_blocks.items():
            existing_names = set()
            for item in datablock:
                old_name = item.name
                base_name = self.clean_name(old_name, prefix=prefix)
                new_name = self.ensure_unique(base_name, existing_names)
                if old_name != new_name:
                    print(f"Renaming {prefix.upper()}: {old_name} -> {new_name}")
                    item.name = new_name


# --------------------------
# Usage
# --------------------------
if __name__ == "__main__":
    fix_naming = MayaNamingConvention()
    fix_naming.rename_all()
