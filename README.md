# Easy SM - Blender to Unreal Engine Export Addon

**Easy SM** is a lightweight, efficient Blender addon designed to streamline the process of preparing and exporting Static Meshes (SM) from Blender directly into Unreal Engine. It automates tedious tasks such as pivot centering, applying transforms, generating collisions, preparing Level of Detail (LODs), and exporting textures.

## Features

### 1. Export Settings
- **Batch Export**: Export multiple selected objects simultaneously. Each object is exported as an individual `.fbx` file.
- **Custom Export Path**: Define a specific directory for your `.fbx` exports. Defaults to `//UE_Export/` relative to your `.blend` file.
- **Add SM_ Prefix**: Automatically prepends `SM_` to the selected mesh, its LODs, and its collisions when enabled.
- **Apply Transforms**: Automatically applies Location, Rotation, and Scale before exporting to ensure 1.0 scale and 0.0 rotation in Unreal Engine.
- **Center to Origin**: Temporarily moves the object to the world origin `(0, 0, 0)` during export. This guarantees that the pivot point in Unreal Engine matches the object's origin in Blender.
- **Export Textures**: Automatically extracts and packages your material image textures into a `Textures` subfolder next to your exported FBX files.
- **Export Collisions**: Automatically detects and exports related collision meshes (e.g., `UCX_MyProp_01`, `UBX_MyProp`) alongside your asset.
- **Unreal-Optimized FBX Settings**: Uses optimal FBX export settings tailored for Unreal Engine (correct Z-up scaling, disabled leaf bones, proper smoothing).

### 2. Collision Generator
Automatically create standard Unreal Engine collision shapes directly in Blender based on your mesh's bounding box or geometry:
- **Available Collision Types**:
  - `UCX` (Convex Hull): Custom collision shape wrapping the mesh.
  - `UBX` (Box): Box collision.
  - `USP` (Sphere): Sphere collision.
  - `UCP` (Capsule): Capsule collision.
- **Decimate Ratio**: (For UCX only) Reduce the complexity of generated Convex Hull collisions to optimize performance.
- **Add Suffix**: Automatically appends an incremental suffix (e.g., `_01`, `_02`) to the collision name, useful for complex objects requiring multiple collision shapes.
- **Separate Loose Parts**: Automatically splits disconnected parts of a complex mesh and generates a fitted collision hull for each individual part.

### 3. LOD Generator
Easily generate Level of Detail (LOD) variations for your meshes to optimize game performance:
- **LOD Count**: Specify how many LOD levels to generate (up to 5).
- **Decimate Step**: Set the scaling multiplier for polygon count reduction per LOD level (e.g., `0.5` reduces triangles by half for each subsequent LOD).

## Installation

1. Download the `easy_sm` folder or as a `.zip` archive.
2. In Blender, go to `Edit` -> `Preferences` -> `Add-ons`.
3. Click `Install...` and select the `easy_sm.zip` file (or the `.py` script if single file).
4. Check the box next to **"Import-Export: Easy SM"** to enable the addon.

## How to Use

Once installed, open the right sidebar in the 3D Viewport by pressing **`N`**. You will find a new tab labeled **Easy SM**.

1. **Select Objects**: Select one or more Mesh objects in your scene that you wish to export.
2. **Setup Collisions & LODs**: Use the *Collision Generator* and *LOD Generator* panels to automatically create collisions and LOD groups for your selected objects if needed.
3. **Configure Settings**: Open the export panel and adjust settings like the export directory and whether to apply transforms.
4. **Export**: Click the large **Export Selected to UE** button. Each selected main object will be processed and exported as a properly formatted `.fbx` file, ready to be dropped into Unreal Engine.
