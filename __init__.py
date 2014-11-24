#  ***** BEGIN GPL LICENSE BLOCK *****
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
#  along with this program; if not, see <http://www.gnu.org/licenses/>
#  and write to the Free Software Foundation, Inc., 51 Franklin Street,
#  Fifth Floor, Boston, MA  02110-1301, USA..
#
#  The Original Code is Copyright (C) 2013-2014 by Gorodetskiy Nikita  ###
#  All rights reserved.
#
#  Contact:      sverchok-b3d@ya.ru    ###
#  Information:  http://nikitron.cc.ua/sverchok_en.html   ###
#
#  The Original Code is: all of this file.
#
#  Contributor(s):
#     Nedovizin Alexander (aka Cfyzzz)
#     Gorodetskiy Nikita (aka Nikitron)
#     Linus Yng (aka Ly29)
#     Agustin Jimenez (aka AgustinJB)
#     Dealga McArdle (aka Zeffii)
#     Konstantin Vorobiew (aka Kosvor)
#
#  ***** END GPL LICENSE BLOCK *****
#
# -*- coding: utf-8 -*-

bl_info = {
    "name": "Sverchok",
    "author": (
        "sverchok-b3d@ya.ru, "
        "Cfyzzz, Nikitron, Ly29, "
        "AgustinJB, Zeffii, Kosvor,"
    ),
    "version": (0, 5, 0, 7),
    "blender": (2, 7, 2),
    "location": "Nodes > CustomNodesTree > Add user nodes",
    "description": "Parametric node-based geometry programming",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Nodes/Sverchok",
    "tracker_url": (
        "http://www.blenderartists.org/forum/showthread.php?272679"
        "-Addon-WIP-Sverchok-parametric-tool-for-architects"),
    "category": "Node"}

import sys
import importlib
import os

# monkey patch the sverchok name, I am sure there is a better way to do this.

if __name__ != "sverchok":
    sys.modules["sverchok"] = sys.modules[__name__]
    
skip_dirs = ["old_nodes", "docs", "node_scripts", "__pycache__"]
current_path = os.path.dirname(__file__)
imported_modules = []


settings = importlib.import_module(".settings", __name__)
imported_modules.append(settings)


def get_all_imports():
    """
    Should return full python import path to module like:
    sverchok.nodes.vector.math
    adapated from my implementation in animationdes nodes 
    /ly
    """
    def get_path(base):
        b, t = os.path.split(base)
        if __name__ == t:
            return ["sverchok"]
        else:
            return get_path(b) + [t]

    for root, dirs, files in os.walk(current_path):
        if any(s_d in root for s_d in skip_dirs):
            continue
        path = ".".join(get_path(root))
        for f in filter(lambda f:f.endswith(".py"), files):
            name = f[:-3]
            if not name == "__init__":
                yield path + "." + name

for mod_name in get_all_imports():
    print(mod_name)
    mod = importlib.import_module(mod_name)
    imported_modules.append(mod)

old_nodes = importlib.import_module("sverchok.old_nodes")
imported_modules.append(old_nodes)

    
reload_event = bool("bpy" in locals())

if reload_event:   
    import nodeitems_utils
    #  reload the base modules
    #  then reload nodes after the node module as been reloaded
    for im in imported_modules:
        importlib.reload(im)
    old_nodes.reload_old()
    menu.reload_menu()

import bpy

sv_ascii_logo = """\
      ::::::  :::   ::: :::::::: :::::::   ::::::  :::  :::  ::::::  :::  ::: 
    :+:  :+: :+:   :+: :+:      :+:  :+: :+:  :+: :+:  :+: :+:  :+: :+: :+:   
   +:+      +:+   +:+ +:+      +:+  +:+ +:+      +:+  +:+ +:+  +:+ +:+ :+     
  +#+++#++ +#+   +:+ +#+++#   +#+++#:  +#+      +#+++#++ +#+  +:+ +#+++       
      +#+  +#+ +#+  +#+      +#+  +#+ +#+      +#+  +#+ +#+  +#+ +#+ #+       
#+#  #+#   #+#+#   #+#      #+#  #+# #+#  #+# #+#  #+# #+#  #+# #+# #+#       
######      #     ######## ###  ###  ######  ###  ###  ######  ###  ###       
"""

def register():
    bpy.utils.register_module(__name__)
    bpy.utils.register_module("sverchok")
    for m in imported_modules:
        if hasattr(m, "register"):
            m.register()
    # this is used to access preferences, should/could be hidden
    # in an interface
    data_structure.SVERCHOK_NAME = __name__
    print("** Have a nice day with sverchok  **\n")
    #print(sv_ascii_logo)   
    
    if reload_event:
        data_structure.RELOAD_EVENT = True
        print("Sverchok is reloaded, press update")


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.utils.unregister_module("sverchok")
    for m in reversed(imported_modules):
        if hasattr(m, "unregister"):
            m.unregister()
    
