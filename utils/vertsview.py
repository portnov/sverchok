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

import math
import time
from math import pi

import bpy

from data_structure import Vector_generate, Matrix_generate, SvGetOutputSocket

callback_dict = {}
SpaceView3D = bpy.types.SpaceView3D

from bgl import (
    glEnable, glDisable, glBegin, glEnd,
    Buffer, GL_FLOAT, GL_BYTE, GL_INT,
    glGetIntegerv, glGetFloatv,
    glColor3f, glVertex3f, glColor4f, glPointSize, glLineWidth,
    glLineStipple, glPolygonStipple, glHint, glShadeModel,
    #
    GL_MATRIX_MODE, GL_MODELVIEW_MATRIX, GL_MODELVIEW, GL_PROJECTION,
    glMatrixMode, glLoadMatrixf, glPushMatrix, glPopMatrix, glLoadIdentity,
    glGenLists, glNewList, glEndList, glCallList, glFlush, GL_COMPILE,
    #
    GL_POINTS, GL_POINT_SIZE, GL_POINT_SMOOTH, GL_POINT_SMOOTH_HINT,
    GL_LINE, GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP, GL_LINE_STIPPLE,
    GL_POLYGON, GL_POLYGON_STIPPLE, GL_TRIANGLES, GL_QUADS,
    GL_NICEST, GL_FASTEST, GL_FLAT, GL_SMOOTH, GL_LINE_SMOOTH_HINT)

# ------------------------------------------------------------------------ #
# parts taken from  "Math Vis (Console)" addon, author Campbell Barton     #
# ------------------------------------------------------------------------ #



def tag_redraw_all_view3d():
    context = bpy.context

    # Py cant access notifers
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()


def callback_enable(n_id):
    global callback_dict
    if n_id in callback_dict:
        return
    args = (n_id,)
    handle_view = SpaceView3D.draw_handler_add(
        draw_callback_view, args, 'WINDOW', 'POST_VIEW')
    
    print("loaded vertsview for {}".format(n_id))
    callback_dict[n_id] = handle_view
    tag_redraw_all_view3d()


def callback_disable_all():
    global callback_dict
    temp_list = list(callback_dict.keys())
    for name in temp_list:
        if name:
            callback_disable(name)


def callback_disable(n_id):
    global callback_dict
    handle_view = callback_dict.get(n_id, None)
    if not handle_view:
        return

    SpaceView3D.draw_handler_remove(handle_view, 'WINDOW')
    del callback_dict[n_id]
    tag_redraw_all_view3d()



def draw_callback_view(n_id):

    ''' vertices '''

    glEnable(GL_POINT_SIZE)
    glEnable(GL_POINT_SMOOTH)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
    # glHint(GL_POINT_SMOOTH_HINT, GL_FASTEST)

    
    data = []
    ng = bpy.data.node_groups.get(n_id)
    if not ng:
        callback_disable(n_id)
        
    node = ng.nodes.active
    if node:
        print("found node {}".format(node.name))
        sockets = [s for s in node.outputs if s.bl_idname == "VerticesSocket"]
        for s in sockets:
            verts = SvGetOutputSocket(s)
            if verts:
                data = verts
                break
    if not data:
        return

    glPointSize(3)
    glColor3f(1, 0, 0)
    glBegin(GL_POINTS)
    
    for obj in data:
        for vec in obj:
            glVertex3f(*vec)
    glEnd()

    glDisable(GL_POINT_SIZE)
    glDisable(GL_POINT_SMOOTH)

    # has drawn once with success.


def unregister():
    callback_disable_all()
