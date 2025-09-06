# blender_to_maya

import sys
sys.path.append(r"C:\Users\Mpho\Desktop\blender_to_maya\maya_scripts")

import importlib
import material_translator
importlib.reload(material_translator)  # refresh if you edit code

material_translator.main(r"C:\Users\Mpho\Desktop\blender_to_maya\to_maya\test_scene.json")