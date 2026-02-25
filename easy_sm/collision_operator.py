import bpy
import bmesh

class UE_COLLISION_OT_Generate(bpy.types.Operator):
    """Generates Convex Hull collisions for all selected meshes"""
    bl_idname = "object.ue_generate_collisions"
    bl_label = "Generate Collisions"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        prefix = scene.ue_col_prefix
        
        selected_objs = context.selected_objects
        if not selected_objs:
            self.report({'WARNING'}, "No objects selected!")
            return {'CANCELLED'}

        generated_count = 0

        # Save current active object to restore later
        original_active = context.view_layer.objects.active



        for obj in selected_objs:
            if obj.type == 'MESH':
                # Determine base name for collision naming
                base_name = obj.name
                
                # Create a temporary container to extract the evaluated mesh
                temp_col_name = f"TEMP_{prefix}_{base_name}"

                col_mesh = bpy.data.meshes.new(temp_col_name)
                col_obj = bpy.data.objects.new(temp_col_name, col_mesh)
                
                # Link newly created collision object to the active collection
                context.collection.objects.link(col_obj)



                # Set transform to match original
                col_obj.matrix_world = obj.matrix_world
                
                # We need to evaluate modifiers (like subdivisions) if they exist, to get accurate bounds
                depsgraph = context.evaluated_depsgraph_get()
                eval_obj = obj.evaluated_get(depsgraph)
                eval_mesh = eval_obj.to_mesh()

                bm = bmesh.new()
                bm.from_mesh(eval_mesh)

                if scene.ue_col_separate_parts:
                    # Separate bm into disconnected components (islands)
                    # Create face maps for islands
                    islands = []
                    faces_left = set(bm.faces)
                    
                    while faces_left:
                        island = set()
                        # start with a random face
                        f = faces_left.pop()
                        island.add(f)
                        
                        queue = [f]
                        while queue:
                            current_f = queue.pop(0)
                            # check connected faces through edges
                            for e in current_f.edges:
                                for linked_f in e.link_faces:
                                    if linked_f in faces_left:
                                        faces_left.remove(linked_f)
                                        island.add(linked_f)
                                        queue.append(linked_f)
                        
                        islands.append(island)
                else:
                    islands = [set(bm.faces)]

                part_idx = 1
                for island in islands:
                    if not island:
                        continue
                        
                    bm_part = bmesh.new()
                    
                    # For UCX we just need vertices
                    verts_set = set()
                    for f in island:
                        for v in f.verts:
                            verts_set.add(v)
                            
                    verts_list = list(verts_set)
                    
                    if prefix == 'UCX':
                        for v in verts_list:
                            bm_part.verts.new(v.co)
                        
                        bm_part.verts.ensure_lookup_table()
                        if len(bm_part.verts) >= 4:
                            ret = bmesh.ops.convex_hull(bm_part, input=bm_part.verts)
                            
                            # Clean up unused and interior points that were left floating
                            del_geom = ret.get("geom_unused", []) + ret.get("geom_interior", [])
                            del_verts = list({ele for ele in del_geom if isinstance(ele, bmesh.types.BMVert)})
                            if del_verts:
                                bmesh.ops.delete(bm_part, geom=del_verts, context='VERTS')
                        else:
                            bm_part.free()
                            continue
                            
                    elif prefix in {'UBX', 'USP', 'UCP'}:
                        co_list = [v.co for v in verts_list]
                        min_x = min([co[0] for co in co_list])
                        max_x = max([co[0] for co in co_list])
                        min_y = min([co[1] for co in co_list])
                        max_y = max([co[1] for co in co_list])
                        min_z = min([co[2] for co in co_list])
                        max_z = max([co[2] for co in co_list])
                        
                        dx = max_x - min_x
                        dy = max_y - min_y
                        dz = max_z - min_z
                        
                        cx = (max_x + min_x) / 2
                        cy = (max_y + min_y) / 2
                        cz = (max_z + min_z) / 2

                        if prefix == 'UBX':
                            bmesh.ops.create_cube(bm_part, size=1.0)
                            bmesh.ops.scale(bm_part, vec=(dx, dy, dz), verts=bm_part.verts)
                            
                        elif prefix == 'USP':
                            radius = max(dx, dy, dz) / 2.0
                            bmesh.ops.create_uvsphere(bm_part, u_segments=16, v_segments=8, radius=radius)
                            
                        elif prefix == 'UCP':
                            radius = max(dx, dy) / 2.0
                            height = dz
                            if height < radius * 2:
                                height = radius * 2
                            
                            cyl_height = height - (2 * radius)
                            if cyl_height < 0:
                                cyl_height = 0
                                
                            bmesh.ops.create_uvsphere(bm_part, u_segments=16, v_segments=16, radius=radius)
                            
                            for v in bm_part.verts:
                                if v.co.z > 0.01:
                                    v.co.z += cyl_height / 2
                                elif v.co.z < -0.01:
                                    v.co.z -= cyl_height / 2
                                    
                        bmesh.ops.translate(bm_part, vec=(cx, cy, cz), verts=bm_part.verts)

                    # Create object for this part
                    if scene.ue_col_separate_parts:
                        # enumerate parts if separated
                        part_col_name = f"{prefix}_{base_name}_{part_idx:02d}"
                    elif scene.ue_col_suffix:
                        part_col_name = f"{prefix}_{base_name}_01"
                    else:
                        part_col_name = f"{prefix}_{base_name}"

                    part_col_mesh = bpy.data.meshes.new(part_col_name)
                    part_col_obj = bpy.data.objects.new(part_col_name, part_col_mesh)
                    context.collection.objects.link(part_col_obj)
                    part_col_obj.parent = obj
                    part_col_obj.matrix_parent_inverse = obj.matrix_world.inverted()
                    part_col_obj.matrix_world = obj.matrix_world
                    
                    bm_part.to_mesh(part_col_mesh)
                    bm_part.free()
                    
                    if prefix == 'UCX' and scene.ue_col_decimate_ratio < 1.0:
                        bpy.ops.object.select_all(action='DESELECT')
                        part_col_obj.select_set(True)
                        context.view_layer.objects.active = part_col_obj
                        
                        mod = part_col_obj.modifiers.new(name="Decimate_UCX", type='DECIMATE')
                        mod.ratio = scene.ue_col_decimate_ratio
                        bpy.ops.object.modifier_apply(modifier="Decimate_UCX")

                    part_col_obj.display_type = 'BOUNDS'
                    part_col_obj.show_bounds = True
                    part_idx += 1
                    generated_count += 1

                bm.free()
                eval_obj.to_mesh_clear()
                
                # Cleanup the originally created empty col_obj since we recreate them in the loop
                bpy.data.objects.remove(col_obj, do_unlink=True)
                bpy.data.meshes.remove(col_mesh, do_unlink=True)

        # Restore original selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_objs:
            obj.select_set(True)
        
        if original_active:
            context.view_layer.objects.active = original_active

        self.report({'INFO'}, f"Generated {generated_count} collision objects!")
        return {'FINISHED'}

classes = (
    UE_COLLISION_OT_Generate,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
