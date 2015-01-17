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

from math import radians, sin, cos
import bpy
from bpy.props import EnumProperty, IntProperty, FloatProperty

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, fullList, match_long_repeat

from mathutils import Vector


def mk_hex_grid(p, m, n, angle):
    alpha = radians(angle)

    sin_alpha = sin(alpha)
    cos_alpha = cos(alpha)
    
    vertices = []
    k = 0
    verts = dict()
    for i in range(m):
        sz = i%3
        for j in range(n):
            if j%3 == sz:
                continue
            x = j*p*sin_alpha;
            y = p*(i + j*cos_alpha)
            verts[(i,j)] = k
            k += 1
            vertices.append((x,y, 0.0))
    
    edges = []
    
    for i in range(m):
        j = (i+1)%3
        while j+1 < n:
            v1 = verts[(i,j)]
            v2 = verts[(i,j+1)]
            edges.append((v1,v2))
            j += 3
    
    for i in range(m-1):
        j = i%3 + 1
        while j < n:
            v1 = verts[(i,j)]
            v2 = verts[(i+1,j-1)]
            edges.append((v1,v2))
            j += 3
    
    for i in range(m-1):
        j = (i+2)%3
        while j < n:
            v1 = verts[(i,j)]
            v2 = verts[(i+1,j)]
            edges.append((v1,v2))
            j += 3
    
    faces = []
    i = 0
    while i+2 < m:
        j = i%3 + 1
        while j+1 < n:
            v1 = verts[(i,j)]
            v2 = verts[(i,j+1)]
            v3 = verts[(i+1,j+1)]
            v4 = verts[(i+2,j)]
            v5 = verts[(i+2,j-1)]
            v6 = verts[(i+1,j-1)]
            faces.append((v1,v2,v3,v4,v5,v6))
            j += 3
        i += 1
    
    return vertices, edges, faces
    

def mk_trig_grid(p, m, n, angle):
    alpha = radians(angle)
    
    sin_alpha = sin(alpha)
    cos_alpha = cos(alpha)
    
    vertices = []
    k = 0
    verts = dict()
    for i in range(m):
        for j in range(n):
            x = j*p*sin_alpha;
            y = p*(i + j*cos_alpha)
            verts[(i,j)] = k
            k += 1
            vertices.append((x,y, 0.0))
    
    edges = []
    for i in range(m):
        for j in range(n):
            v1 = verts.get((i,j), None)
            v2 = verts.get((i,j+1), None)
            v3 = verts.get((i+1,j), None)
            if v1 is not None and v2 is not None:
                edges.append((v1,v2))
            if v2 is not None and v3 is not None:
                edges.append((v2,v3))
            if v3 is not None and v1 is not None:
                edges.append((v3,v1))
    
    faces = []
    for i in range(m):
        for j in range(n):
            v1 = verts.get((i,j), None)
            v2 = verts.get((i,j+1), None)
            v3 = verts.get((i+1,j+1), None)
            v4 = verts.get((i+1,j), None)
            
            if v1 is not None and v2 is not None and v3 is not None and v4 is not None:
                faces.append((v1,v2,v4))
                faces.append((v2,v3,v4))

    return vertices, edges, faces

class SvHexGridNode(bpy.types.Node, SverchCustomTreeNode):
    ''' Hexagonal grid '''
    bl_idname = 'SvHexGridNode'
    bl_label = 'Hex grid'
    bl_icon = 'OUTLINER_OB_EMPTY'

    step_ = FloatProperty(name="Step",
                description="Grid step",
                default=1.0, min=0.0,
                update=updateNode)
    m_ = IntProperty(name="Size U",
                description="Size of grid in the first dimension",
                default=10, min=2,
                update=updateNode)
    n_ = IntProperty(name="Size V",
                description="Size of grid in the second dimension",
                default=10, min=2,
                update=updateNode)
    angle_ = FloatProperty(name="Angle",
                description="Main angle of the grid",
                default=60.0, min=0.0, max=180.0,
                update=updateNode)

    modes = [
            ("hex", "Hex", "Hexagonal grid", 1),
            ("tri", "Trig", "Triangular grid", 2),
            ]

    mode = EnumProperty(items=modes, default="hex", update=updateNode)

    func_dict = {'hex': mk_hex_grid, 'tri': mk_trig_grid}

    def sv_init(self, context):
        self.inputs.new('StringsSocket', "Step").prop_name = 'step_'
        self.inputs.new('StringsSocket', "M").prop_name = 'm_'
        self.inputs.new('StringsSocket', "N").prop_name = 'n_'
        self.inputs.new('StringsSocket', "Alpha").prop_name = 'angle_'

        self.outputs.new('VerticesSocket', "Vertices")
        self.outputs.new('StringsSocket', "Edges")
        self.outputs.new('StringsSocket', "Polygons")

    def draw_buttons(self, context, layout):
        layout.prop(self, "mode", expand=True)

    def process(self):

        steps = self.inputs["Step"].sv_get()[0]
        ms = self.inputs["M"].sv_get()[0]
        ns = self.inputs["N"].sv_get()[0]
        angles = self.inputs["Alpha"].sv_get()[0]

        params = match_long_repeat([steps, ms, ns, angles])
        result_vertices = []
        result_edges = []
        result_faces = []

        func = self.func_dict[self.mode]

        for step, m, n, angle in zip(*params):
            new_vertices, new_edges, new_faces = func(step, m, n, angle)
            result_vertices.append(new_vertices)
            result_edges.append(new_edges)
            result_faces.append(new_faces)

        # outputs
        if self.outputs['Vertices'].is_linked:
            self.outputs['Vertices'].sv_set(result_vertices)

        if self.outputs['Edges'].is_linked:
            self.outputs['Edges'].sv_set(result_edges)

        if self.outputs['Polygons'].is_linked:
            self.outputs['Polygons'].sv_set(result_faces)

    def update_socket(self, context):
        self.update()


def register():
    bpy.utils.register_class(SvHexGridNode)


def unregister():
    bpy.utils.unregister_class(SvHexGridNode)

