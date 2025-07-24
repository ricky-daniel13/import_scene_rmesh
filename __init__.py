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


class ImportRMeshOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.rmesh"
    bl_label = "RMesh (.rmesh)"
    bl_options = {'UNDO'}

    # Add import options as properties

    use_imp_mats: bpy.props.BoolProperty(name="Import Materials", default=True)
    use_ents: bpy.props.BoolProperty(name="Import Entities as empties", default=True)
    use_lightmaps: bpy.props.BoolProperty(name="Import Lightmaps", default=True)
    use_ue: bpy.props.BoolProperty(name="Ultimate Edition Compatibility", default=True)

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
                bm.verts.new((vert.x,vert.z,vert.y))

            bm.verts.ensure_lookup_table()
            bm.verts.index_update()

            added_idxs = 0

            for i in range(rmesh.submeshes[submesh].index_count):
                idxs = rmesh.submeshes[submesh].indices[i]
                # bm.faces.new([bm.verts[idxs.z],bm.verts[idxs.y],bm.verts[idxs.x]])
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

        if(self.use_ents):
            ent_parent = object_utils.object_data_add(context, None, name="entities")
            ent_parent.parent = obj_parent
            for i in range(rmesh.point_count):
                ent_name = str(i) + "_" + rmesh.entities[i].entity_type.value
                if(rmesh.entities[i].entity_type.value == u"model"):
                    ent_name = ent_name + "_" + rmesh.entities[i].entity.model_name.value
                ent = object_utils.object_data_add(context, None, name=ent_name)
                ent.location = (rmesh.entities[i].entity.position.x, rmesh.entities[i].entity.position.z, rmesh.entities[i].entity.position.y)
                ent.parent = ent_parent

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

