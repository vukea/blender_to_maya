import sys
from pathlib import Path
import importlib


class BlenderToMayaPipeline:
    def __init__(self, scripts_path):
        self.scripts_path = Path(scripts_path)
        if str(self.scripts_path) not in sys.path:
            sys.path.append(str(self.scripts_path))

    def run_all(self):
        self.run_delete_unused_data()
        self.run_legacy_material_cleaner()
        self.run_node_cleaner()
        self.run_naming_convention()
        self.run_unpack_textures()
        self.run_fbx_export()
        self.run_material_exporter()
        print("\nAll modules processed successfully!")

    # ------------------------------------------------
    # Individual steps
    # ------------------------------------------------

    def run_delete_unused_data(self):
        try:
            import blender_delete_unused_data
            importlib.reload(blender_delete_unused_data)
            print("Running DeleteFloatingNodes.clean_all()")
            blender_delete_unused_data.DeleteFloatingNodes.clean_all()
        except Exception as e:
            print(f"Error in blender_delete_unused_data: {e}")

    def run_legacy_material_cleaner(self):
        try:
            import blender_legacy_material_cleaner
            importlib.reload(blender_legacy_material_cleaner)
            print("Running LegacyMaterialCleaner.clean_scene_materials()")
            cleaner = blender_legacy_material_cleaner.LegacyMaterialCleaner()
            cleaner.clean_scene_materials()
        except Exception as e:
            print(f"Error in blender_legacy_material_cleaner: {e}")

    def run_node_cleaner(self):
        try:
            import blender_node_cleaner
            importlib.reload(blender_node_cleaner)
            print("Running MaterialNodeCleaner.clean_materials()")
            node_cleaner = blender_node_cleaner.MaterialNodeCleaner()
            node_cleaner.clean_materials()
        except Exception as e:
            print(f"Error in blender_node_cleaner: {e}")

    def run_naming_convention(self):
        try:
            import blender_naming_convention
            importlib.reload(blender_naming_convention)
            print("Running MayaNamingConvention.rename_all()")
            fix_naming = blender_naming_convention.MayaNamingConvention()
            fix_naming.rename_all()
        except Exception as e:
            print(f"Error in blender_naming_convention: {e}")

    def run_unpack_textures(self):
        try:
            import blender_unpack_textures
            importlib.reload(blender_unpack_textures)
            print("Running TextureUnpacker.unpack_all()")
            unpacker = blender_unpack_textures.TextureUnpacker()
            unpacker.unpack_all()
        except Exception as e:
            print(f"Error in blender_unpack_textures: {e}")

    def run_fbx_export(self):
        try:
            import blender_fbx_export
            importlib.reload(blender_fbx_export)
            print("Running FBXExporter.export_all()")
            exporter = blender_fbx_export.FBXExporter()
            exporter.export_all()
        except Exception as e:
            print(f"Error in blender_fbx_export: {e}")

    def run_material_exporter(self):
        try:
            import blender_material_exporter
            importlib.reload(blender_material_exporter)
            print("Running MaterialCollector.run()")
            collector = blender_material_exporter.MaterialCollector()
            collector.run()
        except Exception as e:
            print(f"Error in blender_material_exporter: {e}")


# -------------------------------
# Usage
# -------------------------------
if __name__ == "__main__":
    pipeline = BlenderToMayaPipeline(
        r"C:\Users\Mpho\Documents\blender_to_maya\blender_to_maya\blender_scripts"
    )
    pipeline.run_all()
