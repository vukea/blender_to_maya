from PySide6 import QtWidgets, QtCore
import subprocess
import os
import maya.cmds as cmds

# -------------------------
# Backend: Blender runner
# -------------------------
class BlenderSceneRunner:
    def __init__(self, blender_base_path=r"C:\Program Files\Blender Foundation"):
        """
        Initialize the runner. Automatically finds the latest Blender version if available.
        """
        self.blender_exe = self.find_latest_blender(blender_base_path)
        if not self.blender_exe:
            raise FileNotFoundError("No Blender installation found on the system.")

    def find_latest_blender(self, base_path):
        """
        Search for the latest Blender version in the given folder (Windows).
        Returns the path to blender.exe or None if not found.
        """
        if not os.path.exists(base_path):
            return None
        versions = []
        for name in os.listdir(base_path):
            exe_path = os.path.join(base_path, name, "blender.exe")
            if os.path.isfile(exe_path):
                versions.append((name, exe_path))
        if not versions:
            return None
        # Sort by folder name descending (e.g., Blender 4.0 > Blender 3.6)
        versions.sort(key=lambda x: x[0], reverse=True)
        return versions[0][1]

    def run_blender_script(self, blend_file, blender_script, status_callback=None):
        """
        Run Blender in background mode with the specified .blend file and Python script.
        Returns the path to the resulting FBX.
        """
        if status_callback:
            status_callback("Initializing Blender...")

        if not os.path.exists(blend_file):
            raise FileNotFoundError(f"Blend file not found: {blend_file}")
        if not os.path.exists(blender_script):
            raise FileNotFoundError(f"Blender script not found: {blender_script}")
        if not os.path.exists(self.blender_exe):
            raise FileNotFoundError(f"Blender executable not found: {self.blender_exe}")

        # Run Blender in background mode
        subprocess.run([self.blender_exe, "--background", blend_file, "--python", blender_script], check=True)

        if status_callback:
            status_callback("Blender script finished.")

        # Determine the FBX path in "to_maya" folder
        blend_folder = os.path.dirname(blend_file)
        blend_name = os.path.splitext(os.path.basename(blend_file))[0]
        fbx_path = os.path.join(blend_folder, "to_maya", f"{blend_name}.fbx")

        if not os.path.exists(fbx_path):
            raise FileNotFoundError(f"FBX not found after Blender export: {fbx_path}")

        return fbx_path

    def import_fbx_to_maya(self, fbx_path, status_callback=None):
        """
        Import the FBX into the current Maya scene.
        """
        if status_callback:
            status_callback("Importing FBX into Maya...")

        cmds.file(
            fbx_path,
            i=True,
            type="FBX",
            ignoreVersion=True,
            mergeNamespacesOnClash=False,
            options="fbx",
            pr=True,
            importTimeRange="combine"
        )

        if status_callback:
            status_callback("Done importing!")
            
# -------------------------
# UI: Blender Importer
# -------------------------
class BlenderImporterUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(BlenderImporterUI, self).__init__(parent)
        self.setWindowTitle("Blender Importer")
        self.setMinimumWidth(400)
        self.blend_file = ""

        self.runner = BlenderSceneRunner()  # Backend instance

        self.build_ui()
        self.show()

    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # File selection
        file_layout = QtWidgets.QHBoxLayout()
        self.file_line_edit = QtWidgets.QLineEdit()
        self.file_line_edit.setReadOnly(True)
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_line_edit)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)

        # Status label
        self.status_label = QtWidgets.QLabel("")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.import_objects_btn = QtWidgets.QPushButton("Import Objects")
        self.import_materials_btn = QtWidgets.QPushButton("Import Materials")
        btn_layout.addWidget(self.import_objects_btn)
        btn_layout.addWidget(self.import_materials_btn)
        layout.addLayout(btn_layout)

        # Connect button
        self.import_objects_btn.clicked.connect(self.import_objects)

    def browse_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Blender File", "", "Blender Files (*.blend)"
        )
        if file_path:
            self.blend_file = file_path
            self.file_line_edit.setText(file_path)

    def update_status(self, message):
        self.status_label.setText(message)
        QtWidgets.QApplication.processEvents()  # Refresh UI

    def import_objects(self):
        if not self.blend_file:
            self.update_status("Please select a Blender file!")
            return

        # Disable buttons
        self.import_objects_btn.setEnabled(False)
        self.import_materials_btn.setEnabled(False)

        try:
            blender_script = r"O:\philips_zenith_tvc_25021901\work\_global\blender\scripts\blender_to_maya\blender_scripts\blender_to_maya.py"
            fbx_path = self.runner.run_blender_script(self.blend_file, blender_script, status_callback=self.update_status)
            self.runner.import_fbx_to_maya(fbx_path, status_callback=self.update_status)
        except Exception as e:
            self.update_status(str(e))

        # Re-enable buttons
        self.import_objects_btn.setEnabled(True)
        self.import_materials_btn.setEnabled(True)

# -------------------------
# Show the UI
# -------------------------
if __name__ == "__main__":
    try:
        ui.close()
    except:
        pass

    ui = BlenderImporterUI()
