bl_info = {
	"name": "Rmesh Importer",
	"description": "Imports SCP:CB rmesh files",
	"author": "señorDane",
	"version": (0,0,4),
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
    #use_prevent_faces: bpy.props.BoolProperty(name="Prevent duplicated faces", default=True)
    use_imp_mats: bpy.props.BoolProperty(name="Import Materials", default=True)
    use_ents: bpy.props.BoolProperty(name="Import Entities as empties", default=True)
    #use_option2: bpy.props.BoolProperty(name="Option 2", default=False)
    #float_option: bpy.props.FloatProperty(name="Float Option", default=0.0, min=0.0, max=1.0)


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
                mat_name = rmesh.submeshes[submesh].textures[1].texture_name.value.split(".")[0]
                mat_pat = os.path.join(Path(filepath).parent, rmesh.submeshes[submesh].textures[1].texture_name.value)

                if mat_name not in mats:
                    mat = bpy.data.materials.new(name=mat_name)
                    # obj.data.materials.append(mat)
                    mats[mat_name] = mat
                    # Set the material to use the Principled BSDF shader
                    mat.use_nodes = True
                    nodes = mat.node_tree.nodes
                    principled_bsdf = nodes.get("Principled BSDF")
                    if principled_bsdf is None:
                        principled_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
                    material_output = nodes.get("Material Output")
                    if material_output is None:
                        material_output = nodes.new(type="ShaderNodeOutputMaterial")
                    links = mat.node_tree.links
                    links.new(principled_bsdf.outputs["BSDF"], material_output.inputs["Surface"])

                    print("Loading texture at path: " + mat_pat)
                    image = bpy.data.images.load(mat_pat)
                    texture = bpy.data.textures.new(name=mat_name, type='IMAGE')
                    texture.image = image
                    texture_node = nodes.new(type="ShaderNodeTexImage")
                    texture_node.image = image
                    links.new(texture_node.outputs["Color"], principled_bsdf.inputs["Base Color"])


        obj_parent = object_utils.object_data_add(context, None, name=Path(filepath).stem)
        mesh_parent = obj_parent
        if(self.use_ents):
            mesh_parent = object_utils.object_data_add(context, None, name="meshes")
            mesh_parent.parent = obj_parent

        for submesh in range(rmesh.mesh_count):
            mat_name = rmesh.submeshes[submesh].textures[1].texture_name.value.split(".")[0]
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
    bl_idname = "PT_RMeshImporter"
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

