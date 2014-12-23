# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import IntProperty, FloatProperty, EnumProperty, StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


opposites = {'Integer': 'Float', 'Float': 'Integer'}


class SliderNode(bpy.types.Node, SverchCustomTreeNode):
    ''' Integer '''
    bl_idname = 'SliderNode'
    bl_label = 'Slider Node'
    bl_icon = 'OUTLINER_OB_EMPTY'

    number_repr = StringProperty(default="")

    imax = IntProperty(
        name='imax', description='maximum',
        default=1000,
        update=updateNode)

    imin = IntProperty(
        name='imin', description='minimum',
        default=-1000,
        update=updateNode)

    fmax = FloatProperty(
        name='fmax', description='maximum',
        default=10.0,
        update=updateNode)

    fmin = FloatProperty(
        name='fmin', description='minimum',
        default=-10.0,
        update=updateNode)

    def updateSockets(self, context):
        mode = self.number_mode
        output = self.outputs[mode]
        output_disable = self.outputs[opposites.get(mode)]
        output.enabled = True
        output_disable.enabled = False        

    mode_options = [
        ("Integer", "Integer", "", 0),
        ("Float", "Float", "", 1),
    ]

    number_mode = EnumProperty(
        items=mode_options,
        name="Type of number",
        description="offers choice between int or float",
        default="Integer",
        update=updateSockets)

    def draw_label(self):
        return str(self.number_repr)
        # else:
        #     return self.bl_label

    def draw_buttons_ext(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, 'number_mode')

        row = layout.row(align=True)
        if self.number_mode == 'Integer':
            row.prop(self, 'imax')
            row.prop(self, 'imin')
        else:
            row.prop(self, 'fmax')
            row.prop(self, 'fmin')

    def sv_init(self, context):
        self.outputs.new('StringsSocket', "Integer", "Integer").enabled = True
        self.outputs.new('StringsSocket', "Float", "Float").enabled = False

    def process(self):
        found_num = 20
        mode = self.number_mode
        output = self.outputs[mode]
        if output.is_linked:
            output.sv_set([[found_num]])


def register():
    bpy.utils.register_class(SliderNode)


def unregister():
    bpy.utils.unregister_class(SliderNode)
