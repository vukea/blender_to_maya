import bpy
import json
import os
import math

class MaterialCollector:
    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    @staticmethod
    def get_socket_default(socket):
        """Return default value (color: [R,G,B], scalar: float/vector)."""
        if socket.is_linked:
            return None
        if hasattr(socket, "default_value"):
            val = socket.default_value
            if isinstance(val, float):
                return float(val)
            elif hasattr(val, "__len__"):  # Vector/Color/Other array
                return [float(v) for v in val[:3]]
        return None

    @staticmethod
    def categorize_node(node):
        """Categorize nodes for later pipeline usage, MIX node is dynamic."""
        # Dynamic categorization for MIX node
        if node.type == "MIX":
            a_sock = node.inputs.get("A")
            if a_sock:
                if a_sock.type == 'RGBA':
                    return "Color Node"
                elif a_sock.type == 'VALUE':
                    return "Float Node"
                elif a_sock.type == 'VECTOR':
                    return "Vector Node"
                elif a_sock.type == 'SHADER':
                    return "Shader Node"
            return "Other"
        if node.type in {"BSDF_PRINCIPLED", "MIX_SHADER"}:
            return "Shader Node"
        elif node.type in {"TEX_IMAGE", "MIX_RGB", "HUE_SAT", "INVERT", "RGB", "TEX_NOISE", "TEX_CHECKER", "VALTORGB"}:
            return "Color Node"
        elif node.type == "VALUE":
            return "Float Node"
        elif node.type in {"MAPPING", "NORMAL_MAP", "BUMP"}:
            return "Vector Node"
        return "Other"

    # ------------------------------------------------------------
    # Node Recorders
    # ------------------------------------------------------------
    def record_node(self, node):
        ncat = self.categorize_node(node)

        # --- Image Texture ---
        if node.type == "TEX_IMAGE":
            if not node.image or not node.image.filepath:
                return None

            # Absolute path
            abs_path = bpy.path.abspath(node.image.filepath)

            # Determine category based on the slot it drives
            # Check if this image texture eventually drives Base Color, Emission, or Normal
            # We'll use a default mapping for simplicity
            category = "Other"
            for out in node.outputs:
                for link in out.links:
                    to_node = link.to_node
                    to_sock = link.to_socket
                    if to_node.type == "BSDF_PRINCIPLED":
                        if to_sock.name in {"Base Color", "Emission"}:
                            category = "Color Node"
                        elif to_sock.name == "Normal":
                            category = "Color Node"  # keep Normal as Color for now
                        else:
                            category = "Float Node"
                    elif to_node.type == "MIX_SHADER":
                        # You can extend logic for mix shaders if needed
                        pass

            record = {
                "source_type": "node",
                "node_type": "Image Texture",
                "category": category,  # Color Node or Float Node
                "file_path": abs_path
            }

            # Record vector input if connected
            if "Vector" in node.inputs and node.inputs["Vector"].is_linked:
                sub_node = node.inputs["Vector"].links[0].from_node
                if self.categorize_node(sub_node) == "Vector Node":
                    sub = self.record_node(sub_node)
                    if sub:
                        record["vector"] = sub

            return record



        # --- RGB (Color Node) ---
        if node.type == "RGB":
            return {
                "source_type": "node",
                "node_type": "RGB",
                "category": ncat,
                "color": [float(c) for c in node.outputs[0].default_value[:3]]
            }

        # --- Noise Texture (Color Node) ---
        if node.type == "TEX_NOISE":
            record = {
                "source_type": "node",
                "node_type": "Noise Texture",
                "category": ncat,
            }
            for pname in ["Scale", "Detail", "Lacunarity", "Distortion"]:
                sock = node.inputs.get(pname)
                if sock:
                    if sock.is_linked:
                        from_node = sock.links[0].from_node
                        sub = self.record_node(from_node)
                        record[pname.lower()] = sub if sub else {
                            "source_type": "node", "node_type": from_node.type}
                    else:
                        record[pname.lower()] = self.get_socket_default(sock)
            return record

        # --- Checker Texture (Color Node) ---
        if node.type == "TEX_CHECKER":
            record = {
                "source_type": "node",
                "node_type": "Checker Texture",
                "category": ncat,
            }
            for pname in ["Color1", "Color2", "Scale"]:
                sock = node.inputs.get(pname)
                if sock:
                    if sock.is_linked:
                        from_node = sock.links[0].from_node
                        sub = self.record_node(from_node)
                        record[pname.lower()] = sub if sub else {
                            "source_type": "node", "node_type": from_node.type}
                    else:
                        record[pname.lower()] = self.get_socket_default(sock)
            return record

        # --- Mix Node (dynamic type) ---
        if node.type == "MIX":
            a_sock = node.inputs.get("A")
            if a_sock:
                if a_sock.type == 'RGBA':
                    mix_label = "Mix Color"
                elif a_sock.type == 'VALUE':
                    mix_label = "Mix Float"
                elif a_sock.type == 'VECTOR':
                    mix_label = "Mix Vector"
                elif a_sock.type == 'SHADER':
                    mix_label = "Mix Shader"
                else:
                    mix_label = "Mix"
            else:
                mix_label = "Mix"
            record = {
                "source_type": "node",
                "node_type": mix_label,
                "category": ncat,
                "blend_type": getattr(node, "blend_type", None)
            }
            fac_sock = node.inputs.get("Factor")
            if fac_sock:
                if fac_sock.is_linked:
                    from_node = fac_sock.links[0].from_node
                    sub = self.record_node(from_node)
                    record["fac"] = sub if sub else {
                        "source_type": "node", "node_type": from_node.type}
                else:
                    record["fac"] = {"source_type": "default",
                                     "value": self.get_socket_default(fac_sock)}
            for key in ["A", "B"]:
                sock = node.inputs.get(key)
                if sock:
                    if sock.is_linked:
                        from_node = sock.links[0].from_node
                        sub = self.record_node(from_node)
                        if sub:
                            record[key] = sub
                        else:
                            record[key] = {
                                "source_type": "node", "node_type": from_node.type}
                    else:
                        record[key] = {"source_type": "default",
                                       "value": self.get_socket_default(sock)}
            return record

        # --- MixRGB (legacy, Blender <4.0) ---
        if node.type == "MIX_RGB":
            record = {
                "source_type": "node",
                "node_type": "Mix Color",
                "category": ncat,
                "blend_type": getattr(node, "blend_type", "MIX")
            }
            fac_sock = node.inputs.get("Fac")
            if fac_sock:
                if fac_sock.is_linked:
                    from_node = fac_sock.links[0].from_node
                    sub = self.record_node(from_node)
                    record["fac"] = sub if sub else {
                        "source_type": "node", "node_type": from_node.type}
                else:
                    record["fac"] = {"source_type": "default",
                                     "value": self.get_socket_default(fac_sock)}
            for key, sock_name in [("A", "Color1"), ("B", "Color2")]:
                sock = node.inputs.get(sock_name)
                if sock:
                    if sock.is_linked:
                        from_node = sock.links[0].from_node
                        sub = self.record_node(from_node)
                        if sub:
                            record[key] = sub
                        else:
                            record[key] = {
                                "source_type": "node", "node_type": from_node.type}
                    else:
                        record[key] = {"source_type": "default",
                                       "value": self.get_socket_default(sock)}
            return record

        # --- Invert Color ---
        if node.type == "INVERT":
            record = {
                "source_type": "node",
                "node_type": "Invert",
                "category": ncat,
            }
            fac_sock = node.inputs.get("Fac")
            if fac_sock:
                if fac_sock.is_linked:
                    from_node = fac_sock.links[0].from_node
                    sub = self.record_node(from_node)
                    record["fac"] = sub if sub else {
                        "source_type": "node", "node_type": from_node.type}
                else:
                    record["fac"] = {"source_type": "default",
                                     "value": self.get_socket_default(fac_sock)}
            color_sock = node.inputs.get("Color")
            if color_sock and color_sock.is_linked:
                from_node = color_sock.links[0].from_node
                sub = self.record_node(from_node)
                if sub:
                    record["input"] = sub
                else:
                    record["input"] = {
                        "source_type": "node", "node_type": from_node.type}
            return record

        # --- Hue/Saturation/Value ---
        if node.type == "HUE_SAT":
            record = {
                "source_type": "node",
                "node_type": "HueSatVal",
                "category": ncat,
            }
            for pname in ["Hue", "Saturation", "Value", "Fac"]:
                sock = node.inputs.get(pname)
                if sock:
                    if sock.is_linked:
                        from_node = sock.links[0].from_node
                        sub = self.record_node(from_node)
                        record[pname.lower()] = sub if sub else {
                            "source_type": "node", "node_type": from_node.type}
                    else:
                        record[pname.lower()] = {"source_type": "default",
                                                 "value": self.get_socket_default(sock)}
            color_sock = node.inputs.get("Color")
            if color_sock and color_sock.is_linked:
                from_node = color_sock.links[0].from_node
                sub = self.record_node(from_node)
                if sub:
                    record["input"] = sub
                else:
                    record["input"] = {
                        "source_type": "node", "node_type": from_node.type}
            return record

        # --- Color Ramp (Color Node) ---
        if node.type == "VALTORGB":
            record = {
                "source_type": "node",
                "node_type": "Color Ramp",
                "category": ncat,
                "elements": []
            }
            # Record the ramp stops
            for elem in node.color_ramp.elements:
                record["elements"].append({
                    "position": float(elem.position),
                    "color": [float(c) for c in elem.color[:3]]
                })
            # Record the input if linked or value if default
            input_sock = node.inputs.get("Fac")
            if input_sock:
                if input_sock.is_linked:
                    from_node = input_sock.links[0].from_node
                    sub = self.record_node(from_node)
                    record["input"] = sub if sub else {"source_type": "node", "node_type": from_node.type}
                else:
                    record["input"] = {"source_type": "default", "value": self.get_socket_default(input_sock)}
            return record

        # --- Normal Map ---
        if node.type == "NORMAL_MAP":
            record = {
                "source_type": "node",
                "node_type": "Normal Map",
                "category": ncat,
                "strength": node.inputs["Strength"].default_value if not node.inputs["Strength"].is_linked else {
                    "source_type": "node"}
            }
            if node.inputs["Color"].is_linked:
                from_node = node.inputs["Color"].links[0].from_node
                sub = self.record_node(from_node)
                if sub:
                    record["input"] = sub
                else:
                    record["input"] = {
                        "source_type": "node", "node_type": from_node.type}
            return record

        # --- Bump ---
        if node.type == "BUMP":
            record = {
                "source_type": "node",
                "node_type": "Bump",
                "category": ncat,
                "strength": node.inputs["Strength"].default_value if not node.inputs["Strength"].is_linked else {
                    "source_type": "node"}
            }
            if node.inputs["Height"].is_linked:
                from_node = node.inputs["Height"].links[0].from_node
                sub = self.record_node(from_node)
                if sub:
                    record["input"] = sub
                else:
                    record["input"] = {
                        "source_type": "node", "node_type": from_node.type}
            return record

        # --- Value ---
        if node.type == "VALUE":
            return {
                "source_type": "node",
                "node_type": "Value",
                "category": ncat,
                "value": node.outputs[0].default_value
            }

        # --- Mapping ---
        if node.type == "MAPPING":
            record = {
                "source_type": "node",
                "node_type": "Mapping",
                "category": ncat
            }
            for sock_name, key in [("Location", "location"), ("Rotation", "rotation"), ("Scale", "scale")]:
                sock = node.inputs.get(sock_name)
                if sock:
                    val = [float(v) for v in sock.default_value[:3]]
                    if sock_name == "Rotation":
                        val = [round(math.degrees(x), 6) for x in val]
                    record[key] = val
            return record

        return {"source_type": "node", "node_type": node.type, "category": ncat}

    # ------------------------------------------------------------
    # Principled BSDF Recorder
    # ------------------------------------------------------------
    def record_principled(self, node):
        data = {}

        def add(name, socket_name, expected_node_categories):
            if socket_name not in node.inputs:
                return
            sock = node.inputs[socket_name]
            if sock.is_linked:
                from_node = sock.links[0].from_node
                sub = self.record_node(from_node)
                if sub:
                    # Override category based on expected usage
                    if name in ["Base Color", "Emission Color", "Subsurface Color"]:
                        sub["category"] = "Color Node"
                    elif name in ["Roughness", "Metallic", "Transmission Weight", "Subsurface Weight", "Alpha"]:
                        sub["category"] = "Float Node"
                    data[name] = sub
                else:
                    data[name] = {"source_type": "node", "node_type": from_node.type}
            else:
                default = self.get_socket_default(sock)
                data[name] = {"source_type": "default", "value": default}



        channels = [
            ("Base Color", "Base Color", ["Color Node", "Float Node"]),
            ("Roughness", "Roughness", ["Float Node", "Color Node"]),
            ("Metallic", "Metallic", ["Float Node", "Color Node"]),
            ("Alpha", "Alpha", ["Float Node", "Color Node"]),
            ("Subsurface Weight", "Subsurface Weight", ["Float Node", "Color Node"]),
            ("Subsurface Radius", "Subsurface Radius", ["Vector Node"]),
            ("Transmission Weight", "Transmission Weight", ["Float Node","Color Node"]),
            ("Emission Color", "Emission Color", ["Color Node", "Float Node"]),
            ("Emission Strength", "Emission Strength", ["Float Node","Color Node"]),
        ]


        for ch, socket_name, nodecats in channels:
            add(ch, socket_name, nodecats)

        if "Normal" in node.inputs and node.inputs["Normal"].is_linked:
            from_node = node.inputs["Normal"].links[0].from_node
            if self.categorize_node(from_node) == "Vector Node":
                sub = self.record_node(from_node)
                if sub:
                    data["Normal"] = sub
            else:
                data["Normal"] = {"source_type": "node", "node_type": from_node.type}

        return {
            "shader": "Principled BSDF",
            "channels": data
        }

    # ------------------------------------------------------------
    # Mix Shader Recorder
    # ------------------------------------------------------------
    def record_mixshader(self, node):
        data = {"shader": "Mix Shader", "shaders": []}
        fac_sock = node.inputs.get("Fac")
        if fac_sock:
            if fac_sock.is_linked:
                from_node = fac_sock.links[0].from_node
                if self.categorize_node(from_node) in ["Float Node", "Color Node"]:
                    sub = self.record_node(from_node)
                    data["fac"] = sub if sub else {"source_type": "node", "node_type": from_node.type}
                else:
                    data["fac"] = {"source_type": "node", "node_type": from_node.type}
            else:
                data["fac"] = {"source_type": "default", "value": self.get_socket_default(fac_sock)}
        for sock in node.inputs:
            if sock.type == 'SHADER' and sock != node.outputs.get("Shader"):
                if sock.is_linked:
                    from_node = sock.links[0].from_node
                    if from_node.type == "BSDF_PRINCIPLED":
                        data["shaders"].append(self.record_principled(from_node))
                    else:
                        data["shaders"].append(None)
                else:
                    data["shaders"].append(None)
        return data

    # ------------------------------------------------------------
    # Walk Materials
    # ------------------------------------------------------------
    def record_material(self, mat):
        if not mat.use_nodes:
            return None
        ntree = mat.node_tree
        out = next((n for n in ntree.nodes if n.type == "OUTPUT_MATERIAL"), None)
        if not out:
            return None
        surf = out.inputs.get("Surface")
        if not surf or not surf.is_linked:
            return None
        from_node = surf.links[0].from_node
        if from_node.type == "BSDF_PRINCIPLED":
            return self.record_principled(from_node)
        elif from_node.type == "MIX_SHADER":
            mix_data = self.record_mixshader(from_node)
            return mix_data if mix_data else None
        else:
            return None

    # ------------------------------------------------------------
    # Main Collector
    # ------------------------------------------------------------
    def collect_all_materials(self):
        results = {}
        for mat in bpy.data.materials:
            rec = self.record_material(mat)
            if rec:
                results[mat.name] = rec
        return results

    # ------------------------------------------------------------
    # Run and Save JSON (auto path)
    # ------------------------------------------------------------
    def run_and_save_json(self, output_path=None):
        """
        Save JSON to the current .blend's folder in 'to_maya' with the same name as the .blend file,
        unless output_path is given.
        """
        # If output_path is not provided, compute it based on the current .blend
        if output_path is None:
            blend_path = bpy.data.filepath
            if not blend_path:
                raise RuntimeError("Please save your Blender file first!")
            blend_dir = os.path.dirname(blend_path)
            blend_base = os.path.splitext(os.path.basename(blend_path))[0]
            output_folder = os.path.join(blend_dir, "to_maya")
            output_path = os.path.join(output_folder, f"{blend_base}.json")

        mats_json = self.collect_all_materials()
        print(json.dumps(mats_json, indent=4))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(mats_json, f, indent=4)
        print(f"Materials JSON saved to: {output_path}")

    # ------------------------------------------------------------
    # "run" Entrypoint for batch scripts
    # ------------------------------------------------------------
    def run(self):
        self.run_and_save_json()


if __name__ == "__main__":
    collector = MaterialCollector()
    collector.run_and_save_json()  # <--- No arguments needed!