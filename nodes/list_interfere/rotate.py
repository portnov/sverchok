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
from bpy.props import BoolProperty, IntProperty, StringProperty

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, changable_sockets, match_long_repeat


def rotate(l, y=1):
   if len(l) == 0:
      return l
   y = y % len(l)
   return list(l[y:]) + list(l[:y])

class ListRotateNode(bpy.types.Node, SverchCustomTreeNode):
    ''' List Reverse Node '''
    bl_idname = 'ListRotateNode'
    bl_label = 'List Reverse'
    bl_icon = 'OUTLINER_OB_EMPTY'

    level = IntProperty(name='Level',
                default=2, min=1,
                update=updateNode)
    shift = IntProperty(name='Shift', 
                default=1, min=0,
                update=updateNode)
    unwrap = BoolProperty(name='Unwrap',
                description="Output merged list instead of list of lists",
                default=True,
                update=updateNode)
#     typ = StringProperty(name='typ',
#                          default='')
#     newsock = BoolProperty(name='newsock',
#                            default=False)

    def draw_buttons(self, context, layout):
        layout.prop(self, "level")
        layout.prop(self, "unwrap")

    def sv_init(self, context):
        self.inputs.new('StringsSocket', "data", "data")
        self.inputs.new('StringsSocket', "shift").prop_name = "shift"
        self.outputs.new('StringsSocket', 'data', 'data')

    def update(self):
        if self.inputs['data'].is_linked:
            # adaptive socket
            inputsocketname = 'data'
            outputsocketname = ['data']
            changable_sockets(self, inputsocketname, outputsocketname)

    def process(self):
        if self.inputs['data'].is_linked and self.outputs['data'].is_linked:
            data = self.inputs['data'].sv_get()
            shifts = self.inputs['shift'].sv_get()[0]
            result = []
            print("S:", shifts)
            parameters = match_long_repeat([data, shifts])
            #print("P:", parameters)
            for lst, shift in zip(*parameters):
#                 for shift in shifts:
                print("Lst:", len(lst))
                print("Shifts:", shift)
                r = self._process(lst, shift, self.level-1)
                print("R:", len(r))
                if self.unwrap:
                    result.extend(r)
                else:
                    result.append(r)
            self.outputs['data'].sv_set(result)

    def _process(self, lst, shift, level):
        print("_process:", len(lst), shift, level)
        if level > 0:
            out = []
            for l in lst:
                out.append(self._process(l, shift, level-1))
            return out
        elif type(lst) == list:
            return rotate(lst, shift)
#         elif type(list) in [type(tuple())]:
#             return list[::-1]


def register():
    bpy.utils.register_class(ListRotateNode)


def unregister():
    bpy.utils.unregister_class(ListRotateNode)

