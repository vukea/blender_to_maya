import maya.cmds as cmds

def create(data):
    """Create a file texture node"""
    file_path = data.get("file_path")
    node = cmds.shadingNode("file", asTexture=True)
    place2d = cmds.shadingNode("place2dTexture", asUtility=True)

    # Auto-connect placement node
    cmds.defaultNavigation(connectToExisting=True, source=place2d, destination=node)

    # Set file path
    cmds.setAttr(f"{node}.fileTextureName", file_path, type="string")

    print(f" → Created {node} (Image Texture) [{file_path}]")
    return node
