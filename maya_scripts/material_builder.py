"""
material_builder.py
Builds a single material: creates aiStandardSurface, shading group, and wires channels.
"""

import maya.cmds as cmds
import traceback
from nodes import registry

# Mapping from Principled channels to aiStandardSurface attributes
ATTR_MAPPING = {
    "Base Color": "baseColor",
    "Roughness": "specularRoughness",
    "Metallic": "metalness",
    "Alpha": "opacity",
    "Subsurface Weight": "subsurface",
    "Subsurface Radius": "subsurfaceRadius",
    "Transmission Weight": "transmission",
    "Emission Color": "emissionColor",
    "Emission Strength": "emission",
}


def ensure_shader_and_sg(mat_name):
    """Ensure aiStandardSurface + shadingGroup exist."""
    shader_name = "{}_aiStandardSurface".format(mat_name)
    sg_name = "{}_SG".format(mat_name)

    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", asShader=True, name=shader_name)
        print("Created shader:", shader)
    else:
        shader = shader_name

    if not cmds.objExists(sg_name):
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg_name)
        print("Created shading group:", sg)
    else:
        sg = sg_name

    if not cmds.isConnected(shader + ".outColor", sg + ".surfaceShader"):
        cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader", force=True)

    return shader, sg


class MaterialBuilder:
    def __init__(self):
        self.registry = registry

    def build_material(self, mat_name, mat_json):
        shader_name, sg = ensure_shader_and_sg(mat_name)

        shader_type = mat_json.get("shader", "Principled BSDF")
        if not shader_type.lower().startswith("principled"):
            print("Skipping material '{}': only Principled BSDF supported.".format(mat_name))
            return

        channels = mat_json.get("channels", {})
        base_color_value_or_node = None

        for chan_name, chan_data in channels.items():
            target_attr = ATTR_MAPPING.get(chan_name)
            if not target_attr:
                print("Skipping unsupported channel:", chan_name)
                continue

            try:
                if chan_data.get("source_type") == "default":
                    self._assign_default(shader_name, target_attr, chan_data.get("value"))
                    if chan_name == "Base Color":
                        base_color_value_or_node = ("default", chan_data.get("value"))

                elif chan_data.get("source_type") == "node":
                    node_type = chan_data.get("node_type")
                    node_builder_cls = self.registry.get(node_type)

                    if not node_builder_cls:
                        print("No builder for node_type '{}', skipping.".format(node_type))
                        continue

                    node_builder = node_builder_cls()
                    output_plug = node_builder.build(chan_data, desired_attribute=target_attr, material_name=mat_name)

                    if output_plug:
                        dst = "{}.{}".format(shader_name, target_attr)
                        if not cmds.isConnected(output_plug, dst):
                            cmds.connectAttr(output_plug, dst, force=True)
                            print("Connected {} -> {}".format(output_plug, dst))

                    if chan_name == "Base Color":
                        base_color_value_or_node = ("node", output_plug)

            except Exception as e:
                print("ERROR processing channel '{}': {}".format(chan_name, e))
                traceback.print_exc()

        # Special rule: subsurface > 0 → subsurfaceColor = baseColor
        try:
            subsurface = channels.get("Subsurface Weight")
            subsurface_val = subsurface.get("value") if subsurface else 0

            if subsurface_val and float(subsurface_val) > 0 and base_color_value_or_node:
                if base_color_value_or_node[0] == "default":
                    val = base_color_value_or_node[1]
                    if isinstance(val, (list, tuple)):
                        cmds.setAttr(shader_name + ".subsurfaceColor", *val, type="double3")
                    else:
                        cmds.setAttr(shader_name + ".subsurfaceColor", val, val, val, type="double3")
                else:
                    cmds.connectAttr(base_color_value_or_node[1], shader_name + ".subsurfaceColor", force=True)

        except Exception as e:
            print("Error applying subsurface rule:", e)

    def _assign_default(self, shader_name, attribute, value):
        full_attr = "{}.{}".format(shader_name, attribute)
        if isinstance(value, (list, tuple)) and len(value) == 3:
            cmds.setAttr(full_attr, *value, type="double3")
        elif isinstance(value, (int, float)):
            cmds.setAttr(full_attr, float(value))
        else:
            print("Unsupported default type for", attribute, ":", value)