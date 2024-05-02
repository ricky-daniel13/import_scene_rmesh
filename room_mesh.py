# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class RoomMesh(KaitaiStruct):
    """SCP Containment Breach room mesh format."""

    class TextureType(Enum):
        none = 0
        opaque = 1
        lightmap = 2
        transparent = 3

    class EntityType(Enum):
        none = 0
        opaque = 1
        lightmap = 2
        transparent = 3
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.room_mesh_type = RoomMesh.BlitzStr(self._io, self, self._root)
        self.mesh_count = self._io.read_u4le()
        self.submeshes = []
        for i in range(self.mesh_count):
            self.submeshes.append(RoomMesh.Submesh(self._io, self, self._root))

        self.inv_mesh_count = self._io.read_u4le()
        self.inv_submeshes = []
        for i in range(self.inv_mesh_count):
            self.inv_submeshes.append(RoomMesh.InvSubmesh(self._io, self, self._root))

        if self.room_mesh_type.value == u"RoomMesh.HasTriggerBox":
            self.triggerbox_count = self._io.read_u4le()

        if self.room_mesh_type.value == u"RoomMesh.HasTriggerBox":
            self.triggerboxes = []
            for i in range(self.triggerbox_count):
                self.triggerboxes.append(RoomMesh.Triggerbox(self._io, self, self._root))


        self.point_count = self._io.read_u4le()
        self.entities = []
        for i in range(self.point_count):
            self.entities.append(RoomMesh.PointEntity(self._io, self, self._root))

        self.eof = RoomMesh.BlitzStr(self._io, self, self._root)

    class Vertex(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = RoomMesh.V3(self._io, self, self._root)
            self.uv1 = RoomMesh.V2(self._io, self, self._root)
            self.uv2 = RoomMesh.V2(self._io, self, self._root)
            self.color = RoomMesh.Color(self._io, self, self._root)


    class PointEntity(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.entity_type = RoomMesh.BlitzStr(self._io, self, self._root)
            _on = self.entity_type.value
            if _on == u"model":
                self.entity = RoomMesh.Model(self._io, self, self._root)
            elif _on == u"light":
                self.entity = RoomMesh.Light(self._io, self, self._root)
            elif _on == u"soundemitter":
                self.entity = RoomMesh.Soundemitter(self._io, self, self._root)
            elif _on == u"screen":
                self.entity = RoomMesh.Screen(self._io, self, self._root)
            elif _on == u"waypoint":
                self.entity = RoomMesh.Waypoint(self._io, self, self._root)
            elif _on == u"playerstart":
                self.entity = RoomMesh.Playerstart(self._io, self, self._root)
            elif _on == u"spotlight":
                self.entity = RoomMesh.Spotlight(self._io, self, self._root)


    class Model(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.model_name = RoomMesh.BlitzStr(self._io, self, self._root)
            self.position = RoomMesh.V3(self._io, self, self._root)
            self.rotation = RoomMesh.V3(self._io, self, self._root)
            self.scale = RoomMesh.V3(self._io, self, self._root)


    class V2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()


    class Playerstart(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = RoomMesh.V3(self._io, self, self._root)
            self.angles = RoomMesh.BlitzStr(self._io, self, self._root)


    class Color(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.r = self._io.read_u1()
            self.g = self._io.read_u1()
            self.b = self._io.read_u1()


    class Waypoint(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = RoomMesh.V3(self._io, self, self._root)


    class Spotlight(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = RoomMesh.V3(self._io, self, self._root)
            self.range = self._io.read_f4le()
            self.color = RoomMesh.BlitzStr(self._io, self, self._root)
            self.intensity = self._io.read_f4le()
            self.angles = RoomMesh.BlitzStr(self._io, self, self._root)
            self.inner_cone_angle = self._io.read_s4le()
            self.outter_cone_angle = self._io.read_s4le()


    class Screen(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = RoomMesh.V3(self._io, self, self._root)
            self.screen_texture = RoomMesh.BlitzStr(self._io, self, self._root)


    class InvSubmesh(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vertex_count = self._io.read_u4le()
            self.vertices = []
            for i in range(self.vertex_count):
                self.vertices.append(RoomMesh.V3(self._io, self, self._root))

            self.index_count = self._io.read_u4le()
            self.indices = []
            for i in range(self.index_count):
                self.indices.append(RoomMesh.V3i(self._io, self, self._root))



    class BlitzStr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len = self._io.read_u4le()
            self.value = (self._io.read_bytes(self.len)).decode(u"UTF-8")


    class V3i(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_u4le()
            self.y = self._io.read_u4le()
            self.z = self._io.read_u4le()


    class Box(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vertex_count = self._io.read_u4le()
            self.vertices = []
            for i in range(self.vertex_count):
                self.vertices.append(RoomMesh.V3(self._io, self, self._root))

            self.index_count = self._io.read_u4le()
            self.indices = []
            for i in range(self.index_count):
                self.indices.append(RoomMesh.V3i(self._io, self, self._root))



    class V3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()


    class Triggerbox(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.box_count = self._io.read_u4le()
            self.boxes = []
            for i in range(self.box_count):
                self.boxes.append(RoomMesh.Box(self._io, self, self._root))

            self.triggerbox_name = RoomMesh.BlitzStr(self._io, self, self._root)


    class Light(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = RoomMesh.V3(self._io, self, self._root)
            self.range = self._io.read_f4le()
            self.color = RoomMesh.BlitzStr(self._io, self, self._root)
            self.intensity = self._io.read_f4le()


    class Texture(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mat_type = KaitaiStream.resolve_enum(RoomMesh.TextureType, self._io.read_u1())
            self.texture_name = RoomMesh.BlitzStr(self._io, self, self._root)


    class Soundemitter(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = RoomMesh.V3(self._io, self, self._root)
            self.sound_index = self._io.read_u4le()
            self.range = self._io.read_f4le()


    class Submesh(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.textures = []
            for i in range(2):
                self.textures.append(RoomMesh.Texture(self._io, self, self._root))

            self.vertex_count = self._io.read_u4le()
            self.vertices = []
            for i in range(self.vertex_count):
                self.vertices.append(RoomMesh.Vertex(self._io, self, self._root))

            self.index_count = self._io.read_u4le()
            self.indices = []
            for i in range(self.index_count):
                self.indices.append(RoomMesh.V3i(self._io, self, self._root))




