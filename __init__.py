bl_info = {
	"name": "Rmesh Importer",
	"description": "Imports SCP:CB rmesh files",
	"author": "señorDane",
	"version": (0,0,5),
	"blender": (3,0,0),
	"location": "File > Import > RMESH",
	"category": "Import"
}

if "bpy" in locals():
  import imp
  imp.reload(room_mesh)
  print("Reloaded multifiles")
else:
  from . import room_mesh
  print("Imported multifiles")

import bpy
from bpy_extras.io_utils import ImportHelper
import kaitaistruct
import bmesh
from pathlib import Path
from bpy_extras import object_utils
import mathutils
import os
import math


class ImportRMeshOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.rmesh"
    bl_label = "RMesh (.rmesh)"
    bl_options = {'UNDO'}

    # Add import options as properties

    use_imp_mats: bpy.props.BoolProperty(name="Import Materials", default=True)
    use_ents: bpy.props.BoolProperty(name="Import Entities", 
                                     description="Imports point entities as Empties.",
                                     default=True)
    use_lights_as_ents: bpy.props.BoolProperty(name="Use Blender Lights", 
                                               description="Imports light entities as Blender Lights instead of Empties.",
                                               default=False
                                               )
    use_mesh_as_name: bpy.props.BoolProperty(name="Mesh name as object name", 
                                             description="Sets the object name to the mesh name for model/mesh entities",
                                             default=False)
    use_lightmaps: bpy.props.BoolProperty(name="Import Lightmaps", default=False)
    use_ue: bpy.props.BoolProperty(name="UE Compatibility", 
                                   description="Accounts for Ultimate Edition RMESH files, which have a different slot for lightmaps and search for textures in a 'textures' folder.",
                                   default=False)
    
    base_scale: bpy.props.FloatProperty(
        name="Base Scale",
        description="(0.0075 for CB:HDEdition), (0.00390625 for Blitz3D CB)",
        default=0.0075,
        min=0.00390625,
        max=1.0,
        soft_min=0.00390625,
        soft_max=1.0,
        step=0.0005,
        precision=10
    )

    filename_ext = ".rmesh"
    filter_glob: bpy.props.StringProperty(default="*.rmesh", options={'HIDDEN'})

    def execute(self, context):
        filepath = self.filepath
        print("Importing RMESH from:", filepath)

        rmesh = room_mesh.RoomMesh.from_file(filepath)

        print("rmeshtype:", rmesh.room_mesh_type.value)
        print("submeshes:", rmesh.mesh_count)
        print("entities:", rmesh.point_count)

        mats = dict()
        #Creating mats first
        if (self.use_imp_mats):
            for submesh in range(rmesh.mesh_count):
                lm_texture = rmesh.submeshes[submesh].lightmap
                dif_texture = rmesh.submeshes[submesh].texture

                has_lm  = self.use_lightmaps and lm_texture.mat_type == room_mesh.RoomMesh.TextureType.lightmap
                if self.use_ue:
                    has_lm = self.use_lightmaps and lm_texture.mat_type != room_mesh.RoomMesh.TextureType.none

                print(f"Texture Slot 0 Type {lm_texture.mat_type}, Texture Slot 1 Type {dif_texture.mat_type}")
                print(f"Diffuse texture: {dif_texture.texture_name.value}, Lightmap texture: {lm_texture.texture_name.value if has_lm or lm_texture.mat_type == room_mesh.RoomMesh.TextureType.lightmap else 'None'}")

                diffuse_name = Path(dif_texture.texture_name.value).stem
                lightmap_name = f"_{Path(lm_texture.texture_name.value).stem}" if has_lm else ""
                mat_name = f"{diffuse_name}{lightmap_name}"

                if mat_name not in mats:
                    mat = bpy.data.materials.new(name=mat_name)
                    mats[mat_name] = mat
                    mat.use_nodes = True
                    nodes = mat.node_tree.nodes
                    links = mat.node_tree.links
                    nodes.clear()

                    # Core nodes
                    tex_image_diffuse = nodes.new(type="ShaderNodeTexImage")
                    tex_image_diffuse.label = "Diffuse"
                    tex_image_diffuse.name = "DiffuseTexture"
                    tex_image_diffuse.location = (-600, 300)

                    try:
                        base_path = Path(filepath).parent
                        diffuse_path = os.path.join(base_path, dif_texture.texture_name.value)
                        fallback_path = os.path.join(base_path, 'textures', dif_texture.texture_name.value)
                        if os.path.exists(diffuse_path):
                            tex_image_diffuse.image = bpy.data.images.load(diffuse_path)
                        elif self.use_ue and os.path.exists(fallback_path):
                            print(f"Found texture in UE textures folder: {fallback_path}")
                            tex_image_diffuse.image = bpy.data.images.load(fallback_path)
                        else:
                            raise FileNotFoundError(f"Could not find texture: {dif_texture.texture_name.value}")
                    
                    except:
                        print(f"Could not load diffuse texture: {diffuse_path}")

                    # UV map for diffuse (default is uv1)
                    uv_map_diffuse = nodes.new(type="ShaderNodeUVMap")
                    uv_map_diffuse.uv_map = "uv1"
                    uv_map_diffuse.location = (-800, 300)
                    links.new(uv_map_diffuse.outputs["UV"], tex_image_diffuse.inputs["Vector"])

                    # Setup Principled BSDF and output
                    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
                    bsdf.location = (0, 0)

                    output = nodes.new(type="ShaderNodeOutputMaterial")
                    output.location = (200, 0)
                    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
                    bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)

                    if has_lm:
                        # Load and connect lightmap
                        bsdf.inputs["Emission Strength"].default_value = 10.0
                        tex_image_lightmap = nodes.new(type="ShaderNodeTexImage")
                        tex_image_lightmap.label = "Lightmap"
                        tex_image_lightmap.name = "LightmapTexture"
                        tex_image_lightmap.location = (-600, 0)

                        try:
                            lightmap_path = os.path.join(Path(filepath).parent, lm_texture.texture_name.value)
                            tex_image_lightmap.image = bpy.data.images.load(lightmap_path)
                        except:
                            print(f"Could not load lightmap texture: {lightmap_path}")
                            continue

                        # UV2 map
                        uv_map_lightmap = nodes.new(type="ShaderNodeUVMap")
                        uv_map_lightmap.uv_map = "uv2"
                        uv_map_lightmap.location = (-800, 0)
                        links.new(uv_map_lightmap.outputs["UV"], tex_image_lightmap.inputs["Vector"])

                        # Multiply node
                        mix = nodes.new(type="ShaderNodeMixRGB")
                        mix.blend_type = 'MULTIPLY'
                        mix.inputs[0].default_value = 1.0  # Use full lightmap
                        mix.location = (-300, 200)

                        links.new(tex_image_diffuse.outputs["Color"], mix.inputs[1])
                        links.new(tex_image_lightmap.outputs["Color"], mix.inputs[2])

                        # Output to emission
                        links.new(mix.outputs["Color"], bsdf.inputs["Emission Color"])
                    else:
                        # No lightmap — use only diffuse
                        links.new(tex_image_diffuse.outputs["Color"], bsdf.inputs["Base Color"])


        obj_parent = object_utils.object_data_add(context, None, name=Path(filepath).stem)
        mesh_parent = obj_parent
        if(self.use_ents):
            mesh_parent = object_utils.object_data_add(context, None, name="meshes")
            mesh_parent.parent = obj_parent

        for submesh in range(rmesh.mesh_count):
            lm_texture = rmesh.submeshes[submesh].lightmap
            dif_texture = rmesh.submeshes[submesh].texture

            has_lm  = self.use_lightmaps and lm_texture.mat_type == room_mesh.RoomMesh.TextureType.lightmap
            if self.use_ue:
                has_lm = self.use_lightmaps and lm_texture.mat_type != room_mesh.RoomMesh.TextureType.none


            diffuse_name = Path(dif_texture.texture_name.value).stem
            lightmap_name = f"_{Path(lm_texture.texture_name.value).stem}" if has_lm else ""
            mat_name = f"{diffuse_name}{lightmap_name}"

            mesh = bpy.data.meshes.new("sm" + str(submesh) + "_" + mat_name)
            bm = bmesh.new()

            bm.loops.layers.uv.new("uv1")
            bm.loops.layers.uv.new("uv2")

            for i in range(rmesh.submeshes[submesh].vertex_count):
                vert = rmesh.submeshes[submesh].vertices[i].position
                scaled_pos = (vert.x * self.base_scale, vert.z * self.base_scale, vert.y * self.base_scale)
                bm.verts.new(scaled_pos)

            bm.verts.ensure_lookup_table()
            bm.verts.index_update()

            added_idxs = 0

            for i in range(rmesh.submeshes[submesh].index_count):
                idxs = rmesh.submeshes[submesh].indices[i]
                try:
                    bm.faces.new([bm.verts[idxs.z],bm.verts[idxs.y],bm.verts[idxs.x]])
                    added_idxs = added_idxs+1
                except:
                    print("Repeated face that would've crashed this import")
                    print("submesh: ", submesh)
                    print("submesh texture: ", rmesh.submeshes[submesh].textures[1].texture_name.value.split(".")[0])
                    print("faces: ", rmesh.submeshes[submesh].index_count)
                    print("f " + str(idxs.x)+"/"+str(idxs.y)+"/"+str(idxs.z))
                
            bm.faces.ensure_lookup_table()
            bm.faces.index_update()

            uv_layer1 = bm.loops.layers.uv["uv1"]
            uv_layer2 = bm.loops.layers.uv["uv2"]

            for i in range(added_idxs):
                for loop in bm.faces[i].loops:
                    loop_uv = loop[uv_layer1]
                    vert_idx = loop.vert.index

                    vertex = rmesh.submeshes[submesh].vertices[vert_idx]

                    loop_uv.uv = mathutils.Vector((vertex.uv1.x, 1-vertex.uv1.y))

                    loop_uv = loop[uv_layer2]
                    loop_uv.uv = mathutils.Vector((vertex.uv2.x, 1-vertex.uv2.y))

            bm.to_mesh(mesh)
            mesh.update()        

            new_object = object_utils.object_data_add(context, mesh)
            new_object.parent = mesh_parent

            if (self.use_imp_mats):
                new_object.data.materials.append(mats[mat_name])

        # Import invisible meshes here.
        # Todo -> import invisible meshes.

        # Import entities
        if(self.use_ents):
            ent_parent = object_utils.object_data_add(context, None, name="entities")
            ent_parent.parent = obj_parent
            
            for i in range(rmesh.point_count):
                entity = rmesh.entities[i]
                entity_type = entity.entity_type.value
                entity_data = entity.entity
                

                ent_name = f"{i}_{entity_type}"
                
                if entity_type in ["light", "light_fix", "spotlight"] and self.use_lights_as_ents:
                    # Create actual Blender light objects
                    if entity_type == "spotlight":
                        light_data = bpy.data.lights.new(name=f"{ent_name}_data", type='SPOT')
                        
                        # Set spotlight properties
                        light_data.energy = entity_data.intensity * 100  # Scale for Blender
                        light_data.spot_size = math.radians(entity_data.outter_cone_angle)
                        light_data.spot_blend = (entity_data.outter_cone_angle - entity_data.inner_cone_angle) / entity_data.outter_cone_angle
                        light_data.use_shadow = False


                        # Parse color string (assuming format like "255 128 64" or hex)
                        try:
                            color_str = entity_data.color.value
                            if color_str.startswith('#'):
                                # Hex color
                                color_val = int(color_str[1:], 16)
                                r = ((color_val >> 16) & 255) / 255.0
                                g = ((color_val >> 8) & 255) / 255.0
                                b = (color_val & 255) / 255.0
                            else:
                                # Space-separated RGB values
                                rgb = [float(x) / 255.0 for x in color_str.split()]
                                r, g, b = rgb[0], rgb[1], rgb[2]
                            light_data.color = (r, g, b)
                        except:
                            print(f"Could not parse spotlight color: {entity_data.color.value}")
                            light_data.color = (1.0, 1.0, 1.0)
                        
                        # Create object
                        ent = bpy.data.objects.new(ent_name, light_data)
                        context.collection.objects.link(ent)
                        
                        # Set position and rotation
                        ent.location = (entity_data.position.x * self.base_scale, 
                                  entity_data.position.z * self.base_scale, 
                                  entity_data.position.y * self.base_scale)
                        
                        # This might crash because i dont rememeber how angles are stored in rmesh files
                        try:
                            angles_str = entity_data.angles.value
                            angles = [math.radians(float(x)) for x in angles_str.split()]
                            if len(angles) >= 3:
                                # Convert from game rotation to Blender (may need adjustment)
                                ent.rotation_euler = (angles[0], angles[2], angles[1])
                        except:
                            print(f"Could not parse spotlight angles: {entity_data.angles.value}")
                        
                        # Add custom properties for spotlight-specific data
                        ent["inner_cone_angle"] = entity_data.inner_cone_angle
                        ent["outer_cone_angle"] = entity_data.outter_cone_angle
                        ent["range"] = entity_data.range
                        
                    else:  # light or light_fix
                        light_data = bpy.data.lights.new(name=f"{ent_name}_data", type='POINT')
                        light_data.use_shadow = False
                        
                        # Set light properties
                        if hasattr(entity_data, 'intensity'):
                            light_data.energy = entity_data.intensity * 100  # Scale for Blender
                        
                        # Parse color
                        try:
                            color_str = entity_data.color.value
                            if color_str.startswith('#'):
                                color_val = int(color_str[1:], 16)
                                r = ((color_val >> 16) & 255) / 255.0
                                g = ((color_val >> 8) & 255) / 255.0
                                b = (color_val & 255) / 255.0
                            else:
                                rgb = [float(x) / 255.0 for x in color_str.split()]
                                r, g, b = rgb[0], rgb[1], rgb[2]
                            light_data.color = (r, g, b)
                        except:
                            print(f"Could not parse light color: {entity_data.color.value}")
                            light_data.color = (1.0, 1.0, 1.0)
                        
                        # Create object
                        ent = bpy.data.objects.new(ent_name, light_data)
                        context.collection.objects.link(ent)
                        ent.location = (entity_data.position.x * self.base_scale, 
                                  entity_data.position.z * self.base_scale, 
                                  entity_data.position.y * self.base_scale)
                        
                        # Add custom properties
                        if hasattr(entity_data, 'range'):
                            ent["range"] = entity_data.range
                
                else:
                    ent = object_utils.object_data_add(context, None, name=ent_name)
                    
                    # Set position
                    
                    ent.location = (entity_data.position.x * self.base_scale, 
                                  entity_data.position.z * self.base_scale, 
                                  entity_data.position.y * self.base_scale)
                    
                    # Set rotation if available
                    if hasattr(entity_data, 'rotation'):
                        ent.rotation_mode = 'XYZ'
                        # print(f"Entity #{i} [{entity_type}]: x{entity_data.rotation.x} y{entity_data.rotation.y} z{entity_data.rotation.z}  ")
                        ent.rotation_euler = (math.radians(entity_data.rotation.x), 
                                    math.radians(entity_data.rotation.z), 
                                    math.radians(entity_data.rotation.y))

                    
                    # Set scale if available
                    if hasattr(entity_data, 'scale'):
                        ent.scale = (entity_data.scale.x, entity_data.scale.z, entity_data.scale.y)
                        #We don't scale the scale, we assume user is providing it scaled by ROOMSCALE
                    
                    # Add custom properties based on entity type
                    if entity_type == "model":
                        if self.use_mesh_as_name:
                            ent_name += f"_{entity_data.model_name.value}"
                        ent.name = ent_name
                        ent["model_name"] = entity_data.model_name.value
                        if hasattr(entity_data, 'fx'):
                            ent["fx"] = entity_data.fx
                    
                    elif entity_type == "mesh":
                        if self.use_mesh_as_name:
                            ent_name += f"_{entity_data.model_name.value}"
                        ent.name = ent_name
                        ent["model_name"] = entity_data.model_name.value
                        ent["has_collision"] = bool(entity_data.has_collision)
                        ent["fx"] = entity_data.fx
                        ent["texture"] = entity_data.texture.value
                    
                    elif entity_type == "screen":
                        ent["screen_texture"] = entity_data.screen_texture.value
                    
                    elif entity_type == "save_screen":
                        ent["model"] = entity_data.model.value
                        ent["screen_texture"] = entity_data.screen_texture.value
                    
                    elif entity_type == "soundemitter":
                        ent["sound_index"] = entity_data.sound_index
                        ent["range"] = entity_data.range
                    
                    elif entity_type == "waypoint":
                        # Waypoints only have position, which is already set
                        pass
                    
                    elif entity_type == "playerstart":
                        try:
                            angles_str = entity_data.angles.value
                            ent["angles"] = angles_str
                        except:
                            pass
                
                # Set parent
                ent.parent = ent_parent
                ent["entity_type"] = entity_type

        return {'FINISHED'}


class ImportRMeshPanel(bpy.types.Panel):
    bl_label = "RMesh Import"
    bl_idname = "_PT_RMeshImporter"
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'UI'
    bl_category = 'Import'

    def draw(self, context):
        layout = self.layout
        layout.operator("import_scene.rmesh")


def menu_func_import(self, context):
    self.layout.operator(ImportRMeshOperator.bl_idname)


def register():
    bpy.utils.register_class(ImportRMeshOperator)
    bpy.utils.register_class(ImportRMeshPanel)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportRMeshOperator)
    bpy.utils.unregister_class(ImportRMeshPanel)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

