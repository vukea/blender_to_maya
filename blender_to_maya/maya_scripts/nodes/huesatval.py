import maya.cmds as cmds

INPUT_TYPES = {
    "input": "color",
    "hueShift": "float",
    "saturation": "float",
    "gamma": "float",
}
DEFAULT_OUTPUT = "outColor"

class HueSatVal:
    NODE_TYPE = "aiColorCorrect"

    @classmethod
    def create(cls, name, params):
        node = cmds.shadingNode(cls.NODE_TYPE, asUtility=True, name=name)
        print(f"[hsv] Created node: {node}")

        # Set defaults
        hue = params.get("hue", {}).get("value", 0.5)
        saturation = params.get("saturation", {}).get("value", 1.0)
        value = params.get("value", {}).get("value", 1.0)

        try:
            cmds.setAttr(f"{node}.hueShift", hue - 0.5)  # Blender 0.5 -> Maya 0
            print(f"[hsv] {node}.hueShift = {hue - 0.5}")
        except:
            pass

        try:
            cmds.setAttr(f"{node}.saturation", saturation)
            print(f"[hsv] {node}.saturation = {saturation}")
        except:
            pass

        try:
            cmds.setAttr(f"{node}.gamma", value)
            print(f"[hsv] {node}.gamma = {value}")
        except:
            pass

        # Connect input if available
        input_node = params.get("input")
        if input_node:
            child_node = input_node.get("node")
            if child_node:
                try:
                    cmds.connectAttr(f"{child_node}.outColor", f"{node}.input", force=True)
                    print(f"[hsv] Connected {child_node}.outColor → {node}.input")
                except:
                    pass

        return node
