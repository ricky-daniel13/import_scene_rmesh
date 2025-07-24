meta:
  id: room_mesh
  title: SCP Containment Breach room mesh format
  endian: le

doc: SCP Containment Breach room mesh format.

enums:
  texture_type:
    0: none
    1: opaque
    2: lightmap
    3: transparent
  
  entity_type:
    0: none
    1: opaque
    2: lightmap
    3: transparent

types:
  blitz_str:
    seq:
      - id: len
        type: u4
      - id: value
        type: str
        size: len
        encoding: UTF-8

  v2:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4

  v3:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4

  v3i:
    seq:
      - id: x
        type: u4
      - id: y
        type: u4
      - id: z
        type: u4

  color:
    seq:
      - id: r
        type: u1
      - id: g
        type: u1
      - id: b
        type: u1

  texture:
    seq:
      - id: mat_type
        type: u1
        enum: texture_type
      - id: texture_name
        type: blitz_str
        if: mat_type != texture_type::none

  vertex:
    seq:
      - id: position
        type: v3
      - id: uv1
        type: v2
      - id: uv2
        type: v2
      - id: color
        type: color

  submesh:
    seq:
      - id: lightmap
        type: texture
      - id: texture
        type: texture
      - id: vertex_count
        type: u4
      - id: vertices
        type: vertex
        repeat: expr
        repeat-expr: vertex_count
      - id: index_count
        type: u4
      - id: indices
        type: v3i
        repeat: expr
        repeat-expr: index_count

  inv_submesh:
    seq:
      - id: vertex_count
        type: u4
      - id: vertices
        type: v3
        repeat: expr
        repeat-expr: vertex_count
      - id: index_count
        type: u4
      - id: indices
        type: v3i
        repeat: expr
        repeat-expr: index_count

  box:
    seq:
      - id: vertex_count
        type: u4
      - id: vertices
        type: v3
        repeat: expr
        repeat-expr: vertex_count
      - id: index_count
        type: u4
      - id: indices
        type: v3i
        repeat: expr
        repeat-expr: index_count

  triggerbox:
    seq:
      - id: box_count
        type: u4
      - id: boxes
        type: box
        repeat: expr
        repeat-expr: box_count
      - id: triggerbox_name
        type: blitz_str

  model:
    seq:
      - id: model_name
        type: blitz_str
      - id: position
        type: v3
      - id: rotation
        type: v3
      - id: scale
        type: v3
        
  mesh:
    seq:
      - id: position
        type: v3
      - id: model_name
        type: blitz_str
      - id: rotation
        type: v3
      - id: scale
        type: v3
      - id: has_collision
        type: u1
      - id: fx
        type: s4
      - id: texture
        type: blitz_str

  light:
    seq:
      - id: position
        type: v3
      - id: range
        type: f4
      - id: color
        type: blitz_str
      - id: intensity
        type: f4
  light_fix:
    seq:
      - id: position
        type: v3
      - id: color
        type: blitz_str
      - id: intensity
        type: f4
      - id: range
        type: f4
  spotlight:
    seq:
      - id: position
        type: v3
      - id: range
        type: f4
      - id: color
        type: blitz_str
      - id: intensity
        type: f4
      - id: angles
        type: blitz_str
      - id: inner_cone_angle
        type: s4
      - id: outter_cone_angle
        type: s4
  soundemitter:
    seq:
      - id: position
        type: v3
      - id: sound_index
        type: u4
      - id: range
        type: f4
  screen:
    seq:
      - id: position
        type: v3
      - id: screen_texture
        type: blitz_str
  save_screen:
    seq:
      - id: position
        type: v3
      - id: model
        type: blitz_str
      - id: rotation
        type: v3
      - id: scale
        type: v3
      - id: screen_texture
        type: blitz_str

  waypoint:
    seq:
      - id: position
        type: v3

  playerstart:
    seq:
      - id: position
        type: v3
      - id: angles
        type: blitz_str

  point_entity:
    seq:
      - id: entity_type
        type: blitz_str
      - id: entity
        type:
          switch-on: entity_type.value
          cases:
            '"model"': model
            '"mesh"': mesh
            '"light"': light
            '"light_fix"': light_fix
            '"soundemitter"': soundemitter
            '"screen"': screen
            '"save_screen"': save_screen
            '"waypoint"': waypoint
            '"playerstart"': playerstart
            '"spotlight"': spotlight

seq:
  - id: room_mesh_type
    type: blitz_str
  - id: mesh_count
    type: u4
  - id: submeshes
    type: submesh
    repeat: expr
    repeat-expr: mesh_count
  - id: inv_mesh_count
    type: u4
  - id: inv_submeshes
    type: inv_submesh
    repeat: expr
    repeat-expr: inv_mesh_count
  - id: triggerbox_count
    type: u4
    if: room_mesh_type.value == "RoomMesh.HasTriggerBox"
  - id: triggerboxes
    type: triggerbox
    repeat: expr
    repeat-expr: triggerbox_count
    if: room_mesh_type.value == "RoomMesh.HasTriggerBox"
  - id: point_count
    type: u4
  - id: entities
    type: point_entity
    repeat: expr
    repeat-expr: point_count