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

from math import pi, degrees, floor, ceil, copysign
import numpy as np
import bpy
from bpy.props import BoolProperty, IntProperty, FloatProperty, EnumProperty
from mathutils import Matrix, Vector

from sverchok.node_tree import SverchCustomTreeNode, MatrixSocket, StringsSocket
from sverchok.data_structure import (updateNode, fullList, match_long_repeat,
                            Matrix_listing, Matrix_generate, match_cross,
                            SvGetSocketAnyType, SvSetSocketAnyType)

def is_matrix(lst):
    return len(lst) == 4 and len(lst[0]) == 4

def is_matrix_list(x):
    return type(x) == list and isinstance(x[0], Matrix)

def listify(m1,m2):
    if isinstance(m1, Matrix):
        m1 = [m1]
    if isinstance(m2, Matrix):
        m2 = [m2]
    return m1, m2

def householder(u):
    ''' Householder reflection matrix '''
    x,y,z = u[0], u[1], u[2]
    m = Matrix([[x*x, x*y, x*z, 0], [x*y, y*y, y*z, 0], [x*z, y*z, z*z, 0], [0,0,0,0]])
    h = Matrix() - 2*m
    return h

def autorotate_householder(e1, xx):
    ''' A matrix of transformation which will transform xx vector into e1. 
    See http://en.wikipedia.org/wiki/QR_decomposition '''

    def get_sign():
        for x in e1:
            if x != 0.0:
                return -copysign(1, x)
        return 1

    alpha = xx.length * get_sign()
    u = xx - alpha*e1
    v = u.normalized()
    q = householder(v)
    return q

def autorotate_quaternion(e1, xx):
    rot = xx.rotation_difference(e1).to_matrix().to_4x4()
    return rot

def Matrix_degenerate(ms):
    return [[ j[:] for j in M ] for M in ms]

def matched(fn, m1, m2):
    m1,m2 = listify(m1,m2)
    result = []
    for mx1, mx2 in zip(*match_long_repeat([m1,m2])):
        result.append(fn(mx1,mx2))
    return result

class Multiply(object):
    inputs = [
            ('MatrixSocket', 'Matrix1'),
            ('MatrixSocket', 'Matrix2')
        ]
    outputs = [
            ('MatrixSocket', 'Matrix')
        ]
    
    @staticmethod
    def process(m1, m2):
        result = matched(lambda mx1,mx2: mx1*mx2, m1, m2)
        return [result]

class Add(object):
    inputs = [
            ('MatrixSocket', 'Matrix1'),
            ('MatrixSocket', 'Matrix2')
        ]
    outputs = [
            ('MatrixSocket', 'Matrix')
        ]
    
    @staticmethod
    def process(m1, m2):
        result = matched(lambda mx1,mx2: mx1+mx2, m1, m2)
        return [result]

class QR(object):
    inputs = [
            ('MatrixSocket', 'Matrix')
        ]
    outputs = [
            ('MatrixSocket', 'Q'),
            ('MatrixSocket', 'R')
        ]
    
    @staticmethod
    def process(m):
        matrix = np.array(m)
        q,r = np.linalg.qr(matrix)
        q = q.tolist()
        r = r.tolist()
        return [q, r]

class SVD(object):
    inputs = [
            ('MatrixSocket', 'Matrix')
        ]
    outputs = [
            ('MatrixSocket', 'U'),
            ('MatrixSocket', 'S'),
            ('MatrixSocket', 'V')
        ]
    
    @staticmethod
    def process(m):
        matrix = np.array(m)
        u,s,v = np.linalg.svd(m)
        u,s,v = u.tolist(), s.tolist(), v.tolist()
        s = Matrix([(s[0], 0.0, 0.0, 0.0), (0.0, s[1], 0.0, 0.0),
                    (0.0, 0.0, s[2], 0.0), (0.0, 0.0, 0.0, s[3])])
        return [u, s, v]

class Invert(object):
    inputs = [
            ('MatrixSocket', 'Matrix')
        ]
    outputs = [
            ('MatrixSocket', 'Matrix')
        ]

    @staticmethod
    def process(m):
        r = m.inverted()
        return [r]

class Eigens(object):
    inputs = [
            ('MatrixSocket', 'Matrix')
        ]
    outputs = [
            ('StringsSocket', 'EigenValues'),
            ('VerticesSocket', 'EigenVectors')
        ]
    
    @staticmethod
    def process(m):
        matrix = np.array(m)
        w,v = np.linalg.eig(matrix)
        w = w.tolist()
        v = v.T.tolist()
        return [w,v]

class Householder(object):
    inputs = [
            ('VerticesSocket', 'Vector')
        ]
    
    outputs = [
            ('MatrixSocket', 'Matrix')
        ]

    @staticmethod
    def process(u):
        m = householder(Vector(u))
        return [m]

class Autorotate_Householder(object):
    inputs = [
            ('VerticesSocket', 'Vector'),
            ('VerticesSocket', 'TargetVector')
        ]

    outputs = [
            ('MatrixSocket', 'Matrix')
        ]

    @staticmethod
    def process(vectors, targets):
        xs = match_long_repeat([vectors, targets])
        result = []
        for vector, target in zip(*xs):
            m = autorotate_householder(Vector(target), Vector(vector))
            result.append(m)
        return [result]

class Autorotate_Quaternion(object):
    inputs = [
            ('VerticesSocket', 'Vector'),
            ('VerticesSocket', 'TargetVector')
        ]

    outputs = [
            ('MatrixSocket', 'Matrix')
        ]

    @staticmethod
    def process(vectors, targets):
        xs = match_long_repeat([vectors, targets])
        result = []
        for vector, target in zip(*xs):
            m = autorotate_quaternion(Vector(target), Vector(vector))
            result.append(m)
        return [result]

class MatrixMathNode(bpy.types.Node, SverchCustomTreeNode):
    ''' Interpolate between two matrices '''
    bl_idname = 'MatrixMathNode'
    bl_label = 'Matrix Math'
    bl_icon = 'OUTLINER_OB_EMPTY'

    modes = [
        ('Multiply', "Multiply", "Multiply matrices", 0),
        ('Add', "Add", "Add matrices", 1),
        ('QR', "QR decompose", "QR matrix decomposition", 3),
        ('SVD', "SVD decompose", "SVD matrix decomposition", 4),
        ('Eigen', "Eigendecomp", "Matrix eigenedecomposition", 5),
        ('Invert', "Invert", "Inverse matrix", 6),
        ('Householder', "Householder", "Householder reflection", 7),
        ('Autorotate_Householder', "Autorotate - Householder", "Calculate rotation to rotate one vector to another", 8),
        ('Autorotate_Quaternion', "Autorotate - Quaternions", "Calculate rotation to rotate one vector to another", 9),
    ]

    def update_mode(self, context):
        cls = globals()[self.mode]
        while len(self.inputs) > 0:
            self.inputs.remove(self.inputs[0])
        while len(self.outputs) > 0:
            self.outputs.remove(self.outputs[0])
        for icls, iname in cls.inputs:
            self.inputs.new(icls, iname)
        for ocls, oname in cls.outputs:
            self.outputs.new(ocls, oname)
        updateNode(self, context)

    mode = EnumProperty(name="Mode",
            items=modes,
            default='Multiply',
            update=update_mode)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'mode')

    def sv_init(self, context):
        self.update_mode(context)

    def process(self):
        if not any([self.outputs[name].is_linked for name in self.outputs.keys()]):
            return

        cls = globals()[self.mode]
        inputs = []
        for icls, iname in cls.inputs:
            input = self.inputs[iname].sv_get(default=[[]]) 
            if icls == 'MatrixSocket':
                if is_matrix(input[0]):
                    input = [Matrix_generate(input)]
                else:
                    input = [Matrix_generate(matrices) for matrices in input]
            inputs.append(input)

        parameters = match_cross(inputs)
        outputs = []
        for ps in zip(*parameters):
            outs = cls.process(*ps)
            outputs.append(outs)

        outputs = zip(*outputs)
        for (ocls,oname), out in zip(cls.outputs, outputs):
            if self.outputs[oname].is_linked:
                if ocls == 'MatrixSocket':
                    out = [Matrix_degenerate(m) for m in out]
                self.outputs[oname].sv_set(out)

def register():
    bpy.utils.register_class(MatrixMathNode)


def unregister():
    bpy.utils.unregister_class(MatrixMathNode)

