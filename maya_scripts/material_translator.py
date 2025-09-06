import json
from material_builder import MaterialBuilder

JSON_PATH = r"C:\Users\Mpho\Desktop\blender_to_maya\to_maya\test_scene.json"

class MaterialTranslator:
    def __init__(self, json_path):
        self.json_path = json_path
        self.materials_data = {}

    def load_json(self):
        try:
            with open(self.json_path, 'r') as f:
                self.materials_data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")

    def build_materials(self):
        for mat_name, mat_data in self.materials_data.items():
            builder = MaterialBuilder(mat_name, mat_data)
            builder.build()

if __name__ == "__main__":
    translator = MaterialTranslator(JSON_PATH)
    translator.load_json()
    translator.build_materials()
