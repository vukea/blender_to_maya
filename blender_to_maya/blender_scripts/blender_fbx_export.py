import bpy
import os

class FBXExporter:
    def __init__(self):
        self.progress = 0.0

    def _update_progress(self, value, message=""):
        self.progress = value
        bpy.context.window_manager.progress_update(int(self.progress))
        if message:
            print(f"[{int(self.progress)}%] {message}")

    def export_all(self):
        wm = bpy.context.window_manager
        wm.progress_begin(0, 100)
        try:
            # Step 1: Validate blend file
            self._update_progress(10, "Checking blend file path")
            blend_path = bpy.data.filepath
            if not blend_path:
                raise RuntimeError("Please save your .blend file first.")

            # Step 2: Get paths
            self._update_progress(30, "Preparing export directory")
            blend_dir = os.path.dirname(blend_path)
            blend_name = os.path.splitext(os.path.basename(blend_path))[0]
            export_dir = os.path.join(blend_dir, "to_maya")
            os.makedirs(export_dir, exist_ok=True)
            fbx_path = os.path.join(export_dir, f"{blend_name}.fbx")

            # Step 3: Export FBX
            self._update_progress(70, "Exporting FBX")
            bpy.ops.export_scene.fbx(
                filepath=fbx_path,
                use_selection=False,        # export everything
                apply_unit_scale=True,
                bake_space_transform=False,
                add_leaf_bones=False,
                bake_anim=False             # no animation
            )

            # Step 4: Done
            self._update_progress(100, f"Exported FBX to {fbx_path}")
            print(f"✅ Export complete: {fbx_path}")

        finally:
            wm.progress_end()


# Example usage:
if __name__ == "__main__":
    exporter = FBXExporter()
    exporter.export_all()

