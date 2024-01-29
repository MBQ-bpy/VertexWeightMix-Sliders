import bpy

bl_info = {
    "name": "VertexWeightMix Sliders",
    "description": "This add-on allows you to access the influence of Vertex Weight Mix modifiers in Blender, even when they are collapsed.",
    "author": "MBQ",
    "version": (1, 0),
    "blender": (3, 6, 7),
    "location": "Properties Space > Modifier Tab",
    "category": "Object",
}

vertex_group_items = []
def vertex_group_items_callback(scene, context):
    global vertex_group_items
    vertex_group_items.clear()
    
    vertex_group_items.append(('__NEW__', "New", ''))
    vertex_group_items.append(('', "", ""))
    
    ob = context.active_object
    if ob == None:
        return []
    for index, vg in enumerate(ob.vertex_groups):
        vertex_group_items.append((vg.name, vg.name, ''))
    
    return vertex_group_items

class VWMS_Add(bpy.types.Operator):
    bl_idname = "object.vwms_add"
    bl_label = "Add"
    bl_description = "Quickly add a Vertex Weight Mix modifier"
    bl_options = {'REGISTER', 'UNDO'}
    
    vertex_group : bpy.props.EnumProperty(items=vertex_group_items_callback, name="Vertex Group")
    vertex_group_new_name : bpy.props.StringProperty(name="Name", default="Group")
    
    items = [
        ('SET', "Replace", ""),
        ('ADD', "Add", ""),
        ('SUB', "Subtract", ""),
        ('MUL', "Multiply", ""),
    ]
    mix_mode : bpy.props.EnumProperty(items=items, name="Mix Mode")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        self.layout.prop(self, 'vertex_group')
        if self.vertex_group == '__NEW__':
            self.layout.prop(self, 'vertex_group_new_name')
        
        self.layout.prop(self, 'mix_mode')
    
    def execute(self, context):
        ob = context.active_object
        if ob == None:
            return {'CANCELLED'}
        
        if self.vertex_group == '__NEW__':
            vg_new = ob.vertex_groups.new(name=self.vertex_group_new_name)
            vg_name = vg_new.name
        else:
            vg_name = self.vertex_group
        
        mod = ob.modifiers.new(vg_name, 'VERTEX_WEIGHT_MIX')
        
        mod.vertex_group_a = vg_name
        mod.default_weight_b = 0.5
        mod.mix_mode = self.mix_mode
        mod.mix_set = 'ALL'
        mod.show_expanded = False
        
        return {'FINISHED'}

class VWMS_Show(bpy.types.Operator):
    bl_idname = "object.vwms_show"
    bl_label = "Show"
    bl_description = "Check the vertex group of this modifier in weight paint mode right now"
    bl_options = {'REGISTER', 'UNDO'}
    
    vertex_group : bpy.props.StringProperty(name="Vertex Group")
    
    def execute(self, context):
        ob = context.active_object
        if ob == None:
            return {'CANCELLED'}
        
        if self.vertex_group not in ob.vertex_groups.keys():
            return {'CANCELLED'}
        
        ob.vertex_groups.active = ob.vertex_groups[self.vertex_group]
        
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        
        return {'FINISHED'}

class VWMS_PT_Panel(bpy.types.Panel):
    bl_label = "VertexWeightMix Sliders"
    
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "modifier"
    bl_options = {"DEFAULT_CLOSED"}
    
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        if ob == None:
            return False
        
        if ob.type != 'MESH':
            return False
        
        return True
    
    def draw_header(self, context):
        self.layout.label(text="", icon='PLUGIN')
    
    def draw(self, context):
        ob = context.active_object
        if ob == None:
            return
        
        self.layout.operator(VWMS_Add.bl_idname)
        
        for mod in ob.modifiers:
            if mod.type != 'VERTEX_WEIGHT_MIX':
                continue
            
            if mod.vertex_group_a != '' and mod.vertex_group_b == '':
                prop_id = 'default_weight_b'
            elif mod.vertex_group_a != '' and mod.vertex_group_b != '':
                prop_id = 'mask_constant'
            else:
                continue
            
            row = self.layout.row(align=True)
            
            if mod.show_expanded:
                row.prop(mod, 'show_expanded', text="", icon='RIGHTARROW')
            
            row.prop(mod, prop_id, text=mod.name)
            
            if ob.mode == 'WEIGHT_PAINT' and ob.vertex_groups.active.name == mod.vertex_group_a:
                row.label(text="", icon='HIDE_OFF')
            else:
                op = row.operator(VWMS_Show.bl_idname, text="", icon='VIEWZOOM')
                op.vertex_group = mod.vertex_group_a

def register():
    bpy.utils.register_class(VWMS_PT_Panel)
    
    bpy.utils.register_class(VWMS_Add)
    bpy.utils.register_class(VWMS_Show)

def unregister():
    bpy.utils.unregister_class(VWMS_PT_Panel)
    
    bpy.utils.unregister_class(VWMS_Add)
    bpy.utils.unregister_class(VWMS_Show)

if __name__ == "__main__":
    register()
