import bpy
import os

class TextureUnpacker:
    def __init__(self):
        # Determine the directory of the current .blend file
        self.blend_dir = os.path.dirname(bpy.data.filepath)
        if not self.blend_dir:
            # If the blend file isn't saved yet, default to home directory
            self.blend_dir = os.path.expanduser("~")
            print("Blend file not saved. Using home directory instead.")

    def unpack_all(self):
        """Unpack only packed images into Blender's default 'textures' folder with progress bar."""
        images = [img for img in bpy.data.images if img.packed_file]  # only packed images
        total = len(images)

        if total == 0:
            print("No packed images found. All images are already unpacked.")
            return

        wm = bpy.context.window_manager
        wm.progress_begin(0, total)

        for i, img in enumerate(images):
            img.unpack(method='WRITE_LOCAL')
            print(f"Unpacked: {img.name}")
            wm.progress_update(i + 1)

        wm.progress_end()
        print(f"Total unpacked images: {total}")


# Usage:
if __name__ == "__main__":
    unpacker = TextureUnpacker()
    unpacker.unpack_all()
