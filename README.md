import sys
import importlib

# Add your scripts folder
sys.path.append(r"C:\Users\Mpho\Documents\blender_to_maya\blender_to_maya\maya_scripts")

# Import (or reload) reader
import reader
importlib.reload(reader)

# Set JSON path manually
json_path = r"C:\Users\Mpho\Desktop\blender_to_maya\to_maya\test_scene.json"

# Run the scene reader
reader.read_scene(json_path)
