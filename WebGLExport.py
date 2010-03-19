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
__version__ = "0.2"

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
animation_button = Draw.Create(0)
animation_start = Draw.Create(0)
animation_end = Draw.Create(0)

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
		vertices += "[%.2f,%.2f,%.2f],[%.2f,%.2f,%.2f],[%.2f,%.2f,%.2f]," % (f.verts[0].co.x, f.verts[0].co.y, f.verts[0].co.z,f.verts[1].co.x, f.verts[1].co.y, f.verts[1].co.z,f.verts[2].co.x, f.verts[2].co.y, f.verts[2].co.z)
		indices += "[%i,%i,%i]," % (indexcount,indexcount+1,indexcount+2)
		indexcount += 3
	
	indices += "],\n";
	vertices += "],\n";

	s += vertices
	s += indices
	
	if(exp_normals == 1):
		s += "normals : ["
		for v in mesh.verts: 
			s += "[%.2f, %.2f, %.2f]," % (v.no.x, v.no.y, v.no.z)
	
		s += "],\n"
	if (mesh.vertexColors):
		s += "colors : ["
		for face in mesh.faces:
			for (vert, color) in zip(face.verts, face.col):
				s += "[%.2f,%.2f,%.2f,%.2f]," % ( color.r / 255.0, color.g / 255.0, color.b / 255.0, color.a / 255.0)
		s += "]\n"
	if (mesh.faceUV):
		s += "texCoords : ["
		for face in mesh.faces:
			s += "[%.2f,%.2f],[%.2f,%.2f],[%.2f,%.2f]," % (face.uv[0][0], face.uv[0][1], face.uv[1][0], face.uv[1][1], face.uv[2][0], face.uv[2][1])
				
		s += "]\n"
	
	s += "});\n};"
	
	return s

def export_native(class_name, mesh):
	s = "var BlenderExport = {};\n"
	s += "BlenderExport.%s = {};\n" % (class_name)
	
	vertices = "BlenderExport.%s.vertices = [" % (class_name)
	indices = "BlenderExport.%s.indices = [" % (class_name)
	indexcount = 0;
	
	for f in mesh.faces:
		vertices += "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f," % (f.verts[0].co.x, f.verts[0].co.y, f.verts[0].co.z,f.verts[1].co.x, f.verts[1].co.y, f.verts[1].co.z,f.verts[2].co.x, f.verts[2].co.y, f.verts[2].co.z)
		#indices += "%i,%i,%i," % (indexcount,indexcount+1,indexcount+2)
		indexcount += 3
	
	indices += "];\n";
	vertices += "];\n";

	s += vertices
	s += indices
	
	indexcount -= 3
	s += "for(var i=0;i<%s;i++) BlenderExport.%s.indices.push(i);\n" % (indexcount, class_name)
	
	if(exp_normals == 1):
		s += "BlenderExport.%s.normals = [" % (class_name)
		for v in mesh.verts: 
			s += "%.2f, %.2f, %.2f," % (v.no.x, v.no.y, v.no.z)
	
		s += "];\n"
	if (mesh.vertexColors):
		s += "BlenderExport.%s.colors = [" % (class_name)
		for face in mesh.faces:
			for (vert, color) in zip(face.verts, face.col):
				s += "%.2f,%.2f,%.2f,%.2f," % ( color.r / 255.0, color.g / 255.0, color.b / 255.0, color.a / 255.0)
		s += "];\n"
	if (mesh.faceUV):
		s += "BlenderExport.%s.texCoords = [" % (class_name)
		for face in mesh.faces:
			s += "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f," % (face.uv[0][0], face.uv[0][1], face.uv[1][0], face.uv[1][1], face.uv[2][0], face.uv[2][1])
		s += "];\n"

	if animation_button.val:
		s += "BlenderExport.%s.frames = [" % (class_name)
		sce = bpy.data.scenes.active
		activeObj = sce.objects.active
		matrix = activeObj.getMatrix('worldspace')

		for frame in xrange(animation_start.val, animation_end.val):
			Blender.Set('curframe', frame)
			tmpMesh = Mesh.New()
			tmpMesh.getFromObject(activeObj.name)
			tmpMesh.transform(matrix)
			s+= "["
			for f in tmpMesh.faces:
				for v in f.verts:
					s += "%.2f,%.2f,%.2f," % (v.co.x, v.co.y, v.co.z)
			
			s += "],"
		s += "];"
	
	return s

def export_glge_js(class_name, mesh):
	s = "var BlenderExport = {};\n"
	s += "BlenderExport.%s = function() {\n" % (class_name)
	s += "var obj=new GLGE.Object(\'%s\');\n"  % (class_name)
	s += "var mesh=new GLGE.Mesh();\n" 
	vertices = "mesh.setPositions(["
	normals = "mesh.setNormals(["
	uvs = "mesh.setUV(["
	indices = "mesh.setFaces(["
	indexcount = 0;
	for f in mesh.faces:
		vertices += "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f," % (f.verts[0].co.x, f.verts[0].co.y, f.verts[0].co.z,f.verts[1].co.x, f.verts[1].co.y, f.verts[1].co.z,f.verts[2].co.x, f.verts[2].co.y, f.verts[2].co.z)
		if (f.smooth):
			normals += "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f," % (f.verts[0].no.x, f.verts[0].no.y, f.verts[0].no.z,f.verts[1].no.x, f.verts[1].no.y, f.verts[1].no.z,f.verts[2].no.x, f.verts[2].no.y, f.verts[2].no.z)
		else:
			normals += "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f," % (f.no.x, f.no.y, f.no.z,f.no.x, f.no.y, f.no.z,f.no.x, f.no.y, f.no.z)
		if (mesh.faceUV):
			uvs += "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f," % (f.uv[0][0], f.uv[0][1], f.uv[1][0], f.uv[1][1], f.uv[2][0], f.uv[2][1])
		indices += "%i,%i,%i," % (indexcount,indexcount+1,indexcount+2)
		indexcount += 3
		
	indicies=indices[:len(indices)-1]
	normals=normals[:len(normals)-1]
	if (mesh.faceUV):
		uvs=uvs[:len(uvs)-1]
	vertices=vertices[:len(vertices)-1]
	
	indices += "]);\n";
	normals += "]);\n";
	uvs += "]);\n";
	vertices += "]);\n";
	
	s += vertices
	s += normals
	if (mesh.faceUV):
		s += uvs
	s += indices
	
	s += "var material=new GLGE.Material();\n"
	s += "obj.setMaterial(material);\n"
	s += "obj.setMesh(mesh);\n"
	s += "return obj;\n};"
	print s
	return s
	
def export_glge_xml(class_name, mesh):
	s = "<?xml version=\"1.0\" ?>\n"
	s += "<glge>\n"
	s += "<mesh id=\"%s\">\n"  % (class_name)
	vertices = "<positions>"
	normals = "<normals>"
	uvs = "<uv>"
	indices = "<faces>"
	indexcount = 0;
	for f in mesh.faces:
		vertices += "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f," % (f.verts[0].co.x, f.verts[0].co.y, f.verts[0].co.z,f.verts[1].co.x, f.verts[1].co.y, f.verts[1].co.z,f.verts[2].co.x, f.verts[2].co.y, f.verts[2].co.z)
		if (f.smooth):
			normals += "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f," % (f.verts[0].no.x, f.verts[0].no.y, f.verts[0].no.z,f.verts[1].no.x, f.verts[1].no.y, f.verts[1].no.z,f.verts[2].no.x, f.verts[2].no.y, f.verts[2].no.z)
		else:
			normals += "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f," % (f.no.x, f.no.y, f.no.z,f.no.x, f.no.y, f.no.z,f.no.x, f.no.y, f.no.z)
		if (mesh.faceUV):
			uvs += "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f," % (f.uv[0][0], f.uv[0][1], f.uv[1][0], f.uv[1][1], f.uv[2][0], f.uv[2][1])
		indices += "%i,%i,%i," % (indexcount,indexcount+1,indexcount+2)
		indexcount += 3
	
	indicies=indices[:len(indices)-1]
	normals=normals[:len(normals)-1]
	uvs=uvs[:len(uvs)-1]
	vertices=vertices[:len(vertices)-1]
	
	indices += "</faces>\n";
	normals += "</normals>;\n";
	uvs += "</uv>\n";
	vertices += "</positions>\n";
	
	s += vertices
	s += normals
	if (mesh.faceUV):
		s += uvs
	s += indices
	
	s += "</mesh>\n"
	s += "</glge>"
	
	return s

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
			data_string = export_glge_js(class_name, mesh)
		elif(engine_menu.val == 4):
			data_string = export_glge_xml(class_name, mesh)
		elif(engine_menu.val == 5):
			data_string = export_copperlicht(class_name, mesh)

		out.write(data_string)
		out.close()
		
		Draw.PupMenu("Export Successful")
	elif (evt== EVENT_BROWSEFILE):
		if (engine_menu.val == 4):
			Window.FileSelector(FileSelected,"Export .xml", exp_file_name)
		else:
			Window.FileSelector(FileSelected,"Export .js", exp_file_name)
		Draw.Redraw(1)

def FileSelected(file_name):
	global file_button
	
	if file_name != '':
		file_button.val = file_name
	else:
		cutils.Debug.Debug('ERROR: filename is empty','ERROR')

def draw():
	global file_button, exp_file_name, animation_button, animation_start, animation_end
	global engine_menu, engine_name, exp_normals
	global EVENT_NOEVENT, EVENT_DRAW, EVENT_EXIT, EVENT_EXPORT
	exp_file_name = ""

	glClear(GL_COLOR_BUFFER_BIT)
	glRasterPos2i(40, 240)

	engine_name = "Native WebGL%x1|SceneJS%x2|GLGE JS%x3|GLGE XML%x4"
	engine_menu = Draw.Menu(engine_name, EVENT_NOEVENT, 40, 100, 200, 20, engine_menu.val, "Choose your engine")

	file_button = Draw.String('File location: ', EVENT_NOEVENT, 40, 70, 250, 20, file_button.val, 255) 
	Draw.PushButton('...', EVENT_BROWSEFILE, 300, 70, 30, 20, 'browse file')
	exp_normals = Draw.Toggle('Export normals', EVENT_NOEVENT, 40, 45, 200, 20, 0)
	
	anim_down = 0
	
	if animation_button.val == 1:
		anim_down = 1
	
	animation_button = Draw.Toggle('Export animation frames (native WebGL only)', EVENT_NOEVENT, 400, 70, 300, 20, animation_button.val, 'Export keyframe animation')
	animation_start = Draw.Number('Start frame', EVENT_NOEVENT, 400, 45, 160, 20, animation_start.val, 1, 9999)
	animation_end = Draw.Number('End frame', EVENT_NOEVENT, 400, 20, 160, 20, animation_end.val, 2, 9999)
	
	Draw.Button("Export",EVENT_EXPORT , 40, 20, 80, 18)
	Draw.Button("Exit",EVENT_EXIT , 140, 20, 80, 18)
	
Draw.Register(draw, event, bevent)
