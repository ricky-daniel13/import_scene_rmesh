# import_scene_rmesh
Blender importer for the RMesh format from SCP: Containment Breach. Requires installing the "kaitaistruct" package. You can do this by going to your Blender installation, and running pip install through the python .exe in pyhton/bin.

## Installation

### Step 1: Install Required Dependencies

The addon requires the `kaitaistruct` Python package. To install it:

1. Navigate to your Blender installation directory
2. Locate the Python executable at `python/bin/python.exe` (Windows) or equivalent path on your system
3. On Windows: Open Command Prompt and run:
  ```cmd
  "C:\Program Files\Blender Foundation\Blender [version]\[version]\python\bin\python.exe" -m pip install kaitaistruct
  ```

### Step 2: Install the Addon

1. Download the addon files
2. In Blender, go to `Edit` → `Preferences` → `Add-ons`
3. Click `Install...` and select the addon file

## Usage

1. In Blender, go to `File` → `Import` → `RMesh (.rmesh)`
2. Navigate to your room file
3. Adjust settings and import
4. The scene will be imported into your current Blender project

# license
SCP Containment Breach, its source code and the source code for this addon are licensed under Creative Commons Attribution-ShareAlike 3.0 License.
http://creativecommons.org/licenses/by-sa/3.0/
