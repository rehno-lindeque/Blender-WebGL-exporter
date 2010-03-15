#!BPY

"""
Name: 'WebGL JavaScript (.js)'
Blender: 244
Group: 'Export'
Tooltip: 'WebGL JavaScript'
""" 

# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
# Copyright (C) 2010 Dennis Ippel
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

__author__ = "Dennis Ippel"
__url__ = ("http://www.rozengain.com")
__version__ = "0.1"

__bpydoc__ = """

For more information please go to:
http://www.rozengain.com
"""
import Blender
from Blender import *
import bpy
import bpy
import os
from Blender.BGL import *

EVENT_NOEVENT = 1
EVENT_DRAW = 2
EVENT_EXIT = 3
EVENT_EXPORT = 4
EVENT_BROWSEFILE = 5

file_button = Draw.Create("")
engine_menu = Draw.Create(1)
export_all = None
exp_normals = Draw.Create("")

def export_scenejs(class_name, mesh):
	s = "var BlenderExport = {};\n"
	s += "BlenderExport.%s = function() {\n" % (class_name)
	s += "return SceneJs.geometry({\n"
	s += "type: \'%s\',\n" % (class_name)
	
	vertices = "vertices : ["
	indices = "indices : ["
	indexcount = 0;
	print len(mesh.faces)
	for f in mesh.faces:
		vertices += "[%.3f,%.3f,%.3f],[%.3f,%.3f,%.3f],[%.3f,%.3f,%.3f]," % (f.verts[0].co.x, f.verts[0].co.y, f.verts[0].co.z,f.verts[1].co.x, f.verts[1].co.y, f.verts[1].co.z,f.verts[2].co.x, f.verts[2].co.y, f.verts[2].co.z)
		indices += "[%i,%i,%i]," % (indexcount,indexcount+1,indexcount+2)
		indexcount += 3
	
	indices += "],\n";
	vertices += "],\n";

	s += vertices
	s += indices
	
	if(exp_normals == 1):
		s += "normals : ["
		for v in mesh.verts: 
			s += "[%.3f, %.3f, %.3f]," % (v.no.x, v.no.y, v.no.z)
	
		s += "],\n"
	if (mesh.vertexColors):
		s += "colors : ["
		for face in mesh.faces:
			for (vert, color) in zip(face.verts, face.col):
				s += "[%.3f,%.3f,%.3f,%.3f]," % ( color.r / 255.0, color.g / 255.0, color.b / 255.0, color.a / 255.0)
		s += "]\n"
	if (mesh.faceUV):
		s += "texCoords : ["
		for face in mesh.faces:
			s += "[%.3f,%.3f],[%.3f,%.3f],[%.3f,%.3f]," % (face.uv[0][0], face.uv[0][1], face.uv[1][0], face.uv[1][1], face.uv[2][0], face.uv[2][1])
				
		s += "]\n"
	
	s += "});\n};"
	
	return s

def export_native(class_name, mesh):
	s = "var BlenderExport = {};\n"
	s += "BlenderExport.%s = {};\n" % (class_name)
	
	vertices = "BlenderExport.%s.vertices = [" % (class_name)
	indices = "BlenderExport.%s.indices = [" % (class_name)
	indexcount = 0;
	print len(mesh.faces)
	for f in mesh.faces:
		vertices += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (f.verts[0].co.x, f.verts[0].co.y, f.verts[0].co.z,f.verts[1].co.x, f.verts[1].co.y, f.verts[1].co.z,f.verts[2].co.x, f.verts[2].co.y, f.verts[2].co.z)
		indices += "%i,%i,%i," % (indexcount,indexcount+1,indexcount+2)
		indexcount += 3
	
	indices += "];\n";
	vertices += "];\n";

	s += vertices
	s += indices
	
	if(exp_normals == 1):
		s += "BlenderExport.%s.normals = [" % (class_name)
		for v in mesh.verts: 
			s += "%.3f, %.3f, %.3f," % (v.no.x, v.no.y, v.no.z)
	
		s += "];\n"
	if (mesh.vertexColors):
		s += "BlenderExport.%s.colors = [" % (class_name)
		for face in mesh.faces:
			for (vert, color) in zip(face.verts, face.col):
				s += "%.3f,%.3f,%.3f,%.3f," % ( color.r / 255.0, color.g / 255.0, color.b / 255.0, color.a / 255.0)
		s += "];\n"
	if (mesh.faceUV):
		s += "BlenderExport.%s.texCoords = [" % (class_name)
		for face in mesh.faces:
			s += "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (face.uv[0][0], face.uv[0][1], face.uv[1][0], face.uv[1][1], face.uv[2][0], face.uv[2][1])
				
		s += "];\n"
	
	return s

def export_glge(class_name, ob):
	print "export_glge"

def event(evt, val):
	if (evt == Draw.QKEY and not val):
		Draw.Exit()

def bevent(evt):
	global EVENT_NOEVENT,EVENT_DRAW,EVENT_EXIT
	
	if (evt == EVENT_EXIT):
		Draw.Exit()
	elif (evt== EVENT_DRAW):
		Draw.Redraw()
	elif (evt== EVENT_EXPORT):
		out = file(file_button.val, 'w')
		sce = bpy.data.scenes.active
		ob = sce.objects.active
		mesh = Mesh.New()        
		mesh.getFromObject(ob.name)
		class_name = ob.name.replace(".", "")
		data_string = ""

		if (engine_menu.val == 1):
			data_string = export_native(class_name, mesh)
		elif(engine_menu.val == 2):
			data_string = export_scenejs(class_name, mesh)
		elif(engine_menu.val == 3):
			data_string = export_glge(class_name, mesh)
		elif(engine_menu.val == 4):
			data_string = export_copperlicht(class_name, mesh)

		out.write(data_string)
		out.close()
		
		Draw.PupMenu("Export Successful")
	elif (evt== EVENT_BROWSEFILE):
		Window.FileSelector(FileSelected,"Export .js", exp_file_name)
		Draw.Redraw(1)

def FileSelected(file_name):
	global file_button
	
	if file_name != '':
		file_button.val = file_name
	else:
		cutils.Debug.Debug('ERROR: filename is empty','ERROR')


def draw():
	global file_button, exp_file_name
	global engine_menu, engine_name, exp_normals
	global EVENT_NOEVENT, EVENT_DRAW, EVENT_EXIT, EVENT_EXPORT
	exp_file_name = ""

	glClear(GL_COLOR_BUFFER_BIT)
	glRasterPos2i(40, 240)

	logoImage = Image.Load(Get('scriptsdir')+sys.sep+'AS3Export'+sys.sep+'AS3Export.png')
	Draw.Image(logoImage, 40, 155)
	
	engine_name = "Native WebGL%x1|SceneJS%x2"
	engine_menu = Draw.Menu(engine_name, EVENT_NOEVENT, 40, 100, 200, 20, engine_menu.val, "Choose your engine")

	file_button = Draw.String('File location: ', EVENT_NOEVENT, 40, 70, 250, 20, file_button.val, 255) 
	Draw.PushButton('...', EVENT_BROWSEFILE, 300, 70, 30, 20, 'browse file')
	exp_normals = Draw.Toggle('Export normals', EVENT_NOEVENT, 40, 45, 200, 20, 0)
	
	Draw.Button("Export",EVENT_EXPORT , 40, 20, 80, 18)
	Draw.Button("Exit",EVENT_EXIT , 140, 20, 80, 18)
	
Draw.Register(draw, event, bevent)
	
#filename = os.path.splitext(Blender.Get('filename'))[0]
#Blender.Window.FileSelector(write_obj, "Export", '%s.js' % filename)