bl_info = {
    "name": "Render Buddy",
    "description": "",
    "author": "whoisryosuke",
    "version": (0, 0, 3),
    "blender": (2, 80, 0),
    "location": "Properties > Output",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

import bpy

from bpy.props import (IntProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )

# Global plugin properties
class PluginProperties(PropertyGroup):

    test_resolution: IntProperty(
        name = "Test Resolution",
        description="Temporary resolution for test renders",
        default = 50,
        min = 10,
        max = 100
        )

# The UI Panel in Render View
class ExportPresetsPanel(Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Render Buddy"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        state = scene.render_buddy

        row = layout.row()
        row.prop(scene, "camera")

        # Big render button
        layout.label(text="Test Render:")
        row = layout.row()
        row.operator("export_options.test_render")
        row = layout.row()
        row.prop(state, "test_resolution")

        layout.label(text="Export Presets")
        # Create two columns, by using a split layout.
        split = layout.split()

        def draw_operator(layout, label, resolution_x, resolution_y):
            op = layout.operator("export_options.set_resolution", text=label)
            op.resolution_x = resolution_x
            op.resolution_y = resolution_y

        # First column
        col = split.column()
        col.label(text="1080p:")
        draw_operator(col, "1080p Square", 1080, 1080)
        draw_operator(col, "1080p Vertical", 1080, 1920)
        draw_operator(col, "1080p Widescreen", 1920, 1080)

        # Second column, aligned
        col = split.column()
        col.label(text="4k:")
        draw_operator(col, "4k Square", 3840, 3840)
        draw_operator(col, "4k Vertical", 2160, 3840)
        draw_operator(col, "4k Widescreen", 3840, 2160)

class EXPORT_OPTIONS_set_resolution(Operator):
    bl_idname = "export_options.set_resolution"
    bl_label = "Set Resolution"
    bl_description = "Sets Resolution to given dimensions"
    bl_options = {"UNDO"}

    resolution_x: IntProperty(
        name="Resolution X",
        description="Number of horizontal pixels in the rendered image",
        default=1920,
        min=1,
    )

    resolution_y: IntProperty(
        name="Resolution Y",
        description="Number of vertical pixels in the rendered image",
        default=1080,
        min=1,
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        context.scene.render.resolution_x = self.resolution_x
        context.scene.render.resolution_y = self.resolution_y
        return {"FINISHED"}

class EXPORT_OPTIONS_test_render(Operator):
    bl_idname = "export_options.test_render"
    bl_label = "Test Render"
    bl_description = "Renders at 50% then returns prev. settings"

    def execute(self, context: bpy.types.Context) -> set[str]:
        # Preserve prev settings
        # Make sure to copy any properties of classes
        import copy
        prev_reso_percent = copy.copy(context.scene.render.resolution_percentage)
        prev_file_path = copy.copy(context.scene.render.filepath)
        
        # Set to 50%
        context.scene.render.resolution_percentage = 50

        # Make a filename based on current `.blend` file
        import os
        output_dir = os.path.dirname(bpy.data.filepath)
        filename_dirty = os.path.basename(bpy.data.filepath)
        filename = filename_dirty.replace(".blend", "")
        file_type = context.scene.render.image_settings.file_format
        output_file_pattern_string = filename + "-%s." + file_type

        # Get the current time to append to filename
        from datetime import datetime
        now = datetime.now() # current date and time
        time = now.strftime("%H-%M-%S")

        # Render and save to file
        context.scene.render.filepath = os.path.join(output_dir, (output_file_pattern_string % time))
        bpy.ops.render.render(write_still = bpy.data.is_saved)

        # Return settings
        context.scene.render.resolution_percentage = prev_reso_percent
        context.scene.render.filepath = prev_file_path
        
        return {"FINISHED"}

classes = (
    PluginProperties,
    ExportPresetsPanel,
    EXPORT_OPTIONS_test_render,
    EXPORT_OPTIONS_set_resolution,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # bpy.utils.register_classes_factory(classes)
        
    bpy.types.Scene.render_buddy = PointerProperty(type=PluginProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    # bpy.utils.register_classes_factory(classes)
        
    del bpy.types.Scene.render_buddy


if __name__ == "__main__":
    register()
