# import struct
import struct
import sys
import argparse
import os

def printwrite(file, string):
	file.write('\n'+string)
	print('\n'+string)
	
def read_string_ht3(file):
	byte = b'\x10'
	counter = 0
	
	ret = "none"
		
	pos_start = file.tell()
		
	while byte != b'\x00':
		
		byte = file.read(1)
		counter += 1;
			
		if counter > 256:
			break
						
	file.seek(pos_start, 0)
						
	ret = str(file.read(counter).decode("utf-8")).rstrip('\0')
	
	return ret

#116 - space (double matrix 3x3, position)
		

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument ('name', nargs='?')
	namespace = parser.parse_args()
	
	input_file = namespace.name
	output_file = namespace.name[:-4] + ".txt"
	output_dir = namespace.name[:-4] + "\\"
	
	os.makedirs('{}'.format(namespace.name[:-4]), exist_ok=True)
	
	#writefile = open('output.txt','w')
	#printwrite(writefile, str(namespace.name))

	with open (input_file,'r+b') as file:
		writefile = open(output_file,'w')
		
		file.seek(156, 1) #WDB, type 406, ещё что-нибудь
		type = struct.unpack("<i",file.read(4))[0]
		
		sections_def = []
		sections = []
		
		if (type == 407):
			section_length = struct.unpack("<i",file.read(4))[0]
			file.seek(8, 1) # Default
			names_count = struct.unpack("<i",file.read(4))[0]
			
			for i in range(names_count):
				section_type = struct.unpack("<i",file.read(4))[0]
				section_addr = struct.unpack("<i",file.read(4))[0]
				section_name_addr = struct.unpack("<i",file.read(4))[0]
				
				current_offset = file.tell();	
				file.seek(section_name_addr, 0)		
				block_name = read_string_ht3(file)
				
				file.seek(section_addr, 0)
				real_type = struct.unpack("<i",file.read(4))[0]
				block_length = struct.unpack("<i",file.read(4))[0]
				file.seek(current_offset, 0)
				
				printwrite(writefile,'type: '+str(section_type))
				printwrite(writefile,'real type: '+str(real_type))
				printwrite(writefile,'block_length: '+str(block_length))
				printwrite(writefile,'offset: '+str(section_addr))
				printwrite(writefile,'name offset: '+str(section_name_addr))
				printwrite(writefile,'name: '+ block_name)
				printwrite(writefile, '\n')
				
				
				sections.append( (section_type, section_addr, section_name_addr, block_name, len(block_name) + 1, real_type) )
				
		for i in range(len(sections)):
			#section[0] - block type
			#section[1] - offset
			#section[2] - name offset
			#section[3] - name
			#section[4] - name length
			#section[5] - real type (не то, что в начале файла, а то, что действительно записано по смещению)
			#видимо, тип, указанный в section[0] - и есть настоящий тип, а section[5] - подтип, разновидность блока
			
			if sections[i][5] == 116:
				name = ""
				
				if (len(sections[i][3]) > 0):
					name = sections[i][3]
				else:
					name = ("Untitled_" + str(sections[i][1]))
			
				output_obj = open((output_dir + name + ".obj"),'w')
				
				printwrite(output_obj, "o " + name)
				output_obj.write('\n')
				
				file.seek(sections[i][1] + 4, 0) #к блоку 
				
				file.seek(12, 1)
				file.seek(sections[i][4], 1) #skip name
				file.seek(32, 1)
				
				file.seek(72, 1) #матрица
				
				x = round(struct.unpack('<d',file.read(8))[0], 6)
				y = round(struct.unpack('<d',file.read(8))[0], 6)
				z = round(struct.unpack('<d',file.read(8))[0], 6)
				
				printwrite(output_obj, f"v {x} {y} {z}")
				
				printwrite(writefile, '\n')				
			
			if sections[i][5] == 309 or sections[i][5] == 310: #312, указанный в начале файла, обычно равен 309
				name = ""
				
				if (len(sections[i][3]) > 0):
					name = sections[i][3]
				else:
					name = ("Untitled_" + str(sections[i][1]))
			
				output_obj = open((output_dir + name + ".obj"),'w')
				
				file.seek(sections[i][1] + 4, 0) #к блоку
				
				block_length = struct.unpack("<i",file.read(4))[0]
				
				file.seek(sections[i][4], 1) #skip name
				verts_type = struct.unpack("<i",file.read(4))[0] #что-то
				
				vertices_len = struct.unpack('<i',file.read(4))[0]
				
				vertices_len1 = (int((block_length - 16 - sections[i][4]) / 32))
				
				vertices = []
				uvs = []
				
				print(str(vertices_len))
				print(str(file.tell()))
				
				if (vertices_len > 256000):
					break
				else:
					printwrite(output_obj, "# verts, block type " + str(sections[i][5]) + ", verts type " + str(verts_type) + ", verts " + str(vertices_len) + ", position " + str(sections[i][1]))
					
					if (verts_type == 274):
						printwrite(output_obj, "o " + name)
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							nx = round(struct.unpack('<f',file.read(4))[0], 6)
							ny = round(struct.unpack('<f',file.read(4))[0], 6)
							nz = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							uvs.append((u, v))
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							#printwrite(writefile, f"vn {nx} {ny} {nz}")
							
							#output_obj.write('\n')
					elif (verts_type == 338):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							uvs.append((u, v))
							
							nx = round(struct.unpack('<f',file.read(4))[0], 6)
							file.seek(4, 1)
							ny = round(struct.unpack('<f',file.read(4))[0], 6)
							nz = round(struct.unpack('<f',file.read(4))[0], 6)
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							
					elif (verts_type == 514):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							uvs.append((u, v))
							
							u1 = round(struct.unpack('<f',file.read(4))[0], 6)
							v1 = round(struct.unpack('<f',file.read(4))[0], 6)
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							#printwrite(writefile, f"vn {nx} {ny} {nz}")
							
							#output_obj.write('\n')
							
					elif (verts_type == 530):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							uvs.append((u, v))
							
							nx = round(struct.unpack('<f',file.read(4))[0], 6)
							ny = round(struct.unpack('<f',file.read(4))[0], 6)
							nz = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(4, 1)
							file.seek(4, 1)
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							
					elif (verts_type == 594):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							nx = round(struct.unpack('<f',file.read(4))[0], 6)
							ny = round(struct.unpack('<f',file.read(4))[0], 6)
							nz = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(4, 1)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u1 = round(struct.unpack('<f',file.read(4))[0], 6)
							v1 = round(struct.unpack('<f',file.read(4))[0], 6)
							
							uvs.append((u, v))
							
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							
					elif (verts_type == 786):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							nx = round(struct.unpack('<f',file.read(4))[0], 6)
							ny = round(struct.unpack('<f',file.read(4))[0], 6)
							nz = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(16, 1)
							
							uvs.append((u, v))
							
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							
					elif (verts_type == 1042):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							nx = round(struct.unpack('<f',file.read(4))[0], 6)
							ny = round(struct.unpack('<f',file.read(4))[0], 6)
							nz = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(24, 1)
							
							uvs.append((u, v))
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							#printwrite(writefile, f"vn {nx} {ny} {nz}")
							
							
					elif (verts_type == 4370):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(4, 1)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							uvs.append((u, v))
							
							nx = round(struct.unpack('<f',file.read(4))[0], 6)
							ny = round(struct.unpack('<f',file.read(4))[0], 6)
							nz = round(struct.unpack('<f',file.read(4))[0], 6)
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							#printwrite(writefile, f"vn {nx} {ny} {nz}")
							
					elif (verts_type == 4434):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(4, 1)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							uvs.append((u, v))
							
							nx = round(struct.unpack('<f',file.read(4))[0], 6)
							file.seek(4, 1)
							ny = round(struct.unpack('<f',file.read(4))[0], 6)
							nz = round(struct.unpack('<f',file.read(4))[0], 6)
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							#printwrite(writefile, f"vn {nx} {ny} {nz}")
							
					elif (verts_type == 4626):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(4, 1)
							
							v2 = round(struct.unpack('<f',file.read(4))[0], 6)
							v3 = round(struct.unpack('<f',file.read(4))[0], 6)					
							v4 = round(struct.unpack('<f',file.read(4))[0], 6)
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							u1 = round(struct.unpack('<f',file.read(4))[0], 6)
							v1 = round(struct.unpack('<f',file.read(4))[0], 6)
							#v8 = round(struct.unpack('<f',file.read(4))[0], 6)
							
							uvs.append((u, 1 - v))
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							#printwrite(writefile, f"vn {nx} {ny} {nz}")
							
					elif (verts_type == 4882):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(4, 1)
							
							v2 = round(struct.unpack('<f',file.read(4))[0], 6)
							v3 = round(struct.unpack('<f',file.read(4))[0], 6)					
							v4 = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u2 = round(struct.unpack('<f',file.read(4))[0], 6)
							v2 = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u3 = round(struct.unpack('<f',file.read(4))[0], 6)
							v3 = round(struct.unpack('<f',file.read(4))[0], 6)
							#v8 = round(struct.unpack('<f',file.read(4))[0], 6)
							
							uvs.append((u, 1 - v))
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							#printwrite(writefile, f"vn {nx} {ny} {nz}")
						
							
					elif (verts_type == 5202):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
								
							file.seek(52, 1)
							
							printwrite(output_obj, f"v {x} {y} {z}")
							
					elif (verts_type == 8466):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							nx = round(struct.unpack('<f',file.read(4))[0], 6)
							ny = round(struct.unpack('<f',file.read(4))[0], 6)
							nz = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(24, 1)
							
							uvs.append((u, v))
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							#printwrite(writefile, f"vn {nx} {ny} {nz}")
							
					elif (verts_type == 8530):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							nx = round(struct.unpack('<f',file.read(4))[0], 6)
							ny = round(struct.unpack('<f',file.read(4))[0], 6)
							nz = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(4, 1)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(12, 1)
							
							uvs.append((u, v))
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							#printwrite(writefile, f"vn {nx} {ny} {nz}")
							
					elif (verts_type == 8722):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							nx = round(struct.unpack('<f',file.read(4))[0], 6)
							ny = round(struct.unpack('<f',file.read(4))[0], 6)
							nz = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(20, 1)
							
							uvs.append((u, v))
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							#printwrite(writefile, f"vn {nx} {ny} {nz}")
							
					elif (verts_type == 3416834):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							nx = round(struct.unpack('<f',file.read(4))[0], 6)
							ny = round(struct.unpack('<f',file.read(4))[0], 6)
							nz = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(4, 1)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(12, 1)
							
							uvs.append((u, v))
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							#printwrite(writefile, f"vn {nx} {ny} {nz}")
							
							
					elif (verts_type == 3420930): #4882
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(4, 1)
							
							v2 = round(struct.unpack('<f',file.read(4))[0], 6)
							v3 = round(struct.unpack('<f',file.read(4))[0], 6)					
							v4 = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u2 = round(struct.unpack('<f',file.read(4))[0], 6)
							v2 = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u3 = round(struct.unpack('<f',file.read(4))[0], 6)
							v3 = round(struct.unpack('<f',file.read(4))[0], 6)
							#v8 = round(struct.unpack('<f',file.read(4))[0], 6)
							
							uvs.append((u, 1 - v))
							
							printwrite(output_obj, f"v {x} {y} {z}")
							#printwrite(output_obj, f"vt {u} {v}")
							#printwrite(writefile, f"vn {nx} {ny} {nz}")
						
							
					elif (verts_type == 5506066):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							v2 = round(struct.unpack('<f',file.read(4))[0], 6)
							v3 = round(struct.unpack('<f',file.read(4))[0], 6)					
							v4 = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							uvs.append((u, 1 - v))
							
							file.seek(36, 1)
							
							printwrite(output_obj, f"v {x} {y} {z}")
						
					elif (verts_type == 5510162):
						printwrite(output_obj, "o " + sections[i][3])
						output_obj.write('\n')
						
						for i in range(vertices_len):
						
							x = round(struct.unpack('<f',file.read(4))[0], 6)
							y = round(struct.unpack('<f',file.read(4))[0], 6)
							z = round(struct.unpack('<f',file.read(4))[0], 6)
							
							file.seek(4, 1) #int
							
							nx = round(struct.unpack('<f',file.read(4))[0], 6)
							ny = round(struct.unpack('<f',file.read(4))[0], 6)
							nz = round(struct.unpack('<f',file.read(4))[0], 6)
							
							u = round(struct.unpack('<f',file.read(4))[0], 6)
							v = round(struct.unpack('<f',file.read(4))[0], 6)
							
							uvs.append((u, 1 - v))
							
							file.seek(36, 1)

							printwrite(output_obj, f"v {x} {y} {z}")
						
					else:
						print("(!!!) unknown verts type: " + str(verts_type))
						break
					
					for i in range(len(uvs)):
						printwrite(output_obj, f"vt {uvs[i][0]} {uvs[i][1]}")
						
						
				print("faces data")
				print(str(file.tell()))
				
				#fc_1 = file.tell()
				
				mesh_type = struct.unpack("<i",file.read(4))[0]
				printwrite(output_obj, "# faces, block type " + str(mesh_type) + ", position " + str(file.tell()))
				printwrite(output_obj, "s 1")
				#print("type: " + str(mesh_type))
				mesh_section_length = struct.unpack("<i",file.read(4))[0]
				print("section length: " + str(mesh_section_length))
				mesh_num_256 = struct.unpack("<i",file.read(4))[0]
				file.seek(1, 1)
				
				#faces_count = 0
				
				#if (fc_1 == 73084):
				#	faces_count = 55
				#else:
				#	faces_count  = struct.unpack("<i",file.read(4))[0]
				
				faces_count = struct.unpack("<i",file.read(4))[0]
				
				print("faces count: " + str(faces_count))
				
				
				if (faces_count > 256000):
					break
					print("error")
					print(str(file.tell()))
				else:	
					output_obj.write('\n')
					if (mesh_type == 312):
						for i in range(int(faces_count / 3)):
							
							f1_r = struct.unpack("<H",file.read(2))[0]
							f2_r = struct.unpack("<H",file.read(2))[0]
							f3_r = struct.unpack("<H",file.read(2))[0]
								
							f1 = 0
							f2 = 0
							f3 = 0
								
							if (f1_r + 2 < vertices_len):
								f1 = f1_r + 1
							else:
								f1 = -1
									
							if (f2_r + 2 < vertices_len):
								f2 = f2_r + 1
							else:
								f2 = -1
									
							if (f3_r + 2 < vertices_len):
								f3 = f3_r + 1
							else:
								f3 = -1
								
								
							printwrite(output_obj, f"f {f1}/{f1} {f2}/{f2} {f3}/{f3}")
							#printwrite(output_obj, f"f {f1}/{f1}/{f1} {f2}/{f2}/{f2} {f3}/{f3}/{f3}")
					elif (mesh_type == 313): #needs to be fixed
						for i in range(int(faces_count / 3)):
							
							f1_r = struct.unpack("<H",file.read(2))[0]
							f2_r = struct.unpack("<H",file.read(2))[0]
							f3_r = struct.unpack("<H",file.read(2))[0]
								
							f1 = 0
							f2 = 0
							f3 = 0
								
							if (f1_r + 2 < vertices_len):
								f1 = f1_r + 1
							else:
								f1 = -1
									
							if (f2_r + 2 < vertices_len):
								f2 = f2_r + 1
							else:
								f2 = -1
									
							if (f3_r + 2 < vertices_len):
								f3 = f3_r + 1
							else:
								f3 = -1
								
								
							printwrite(output_obj, f"f {f1}/{f1} {f2}/{f2} {f3}/{f3}")
							
					output_obj.write('\n')
				#if (fc_1 == 73084):
				#	break
				
							#f1_r = struct.unpack("<H",file.read(2))[0]
							#f2_r = struct.unpack("<H",file.read(2))[0]
							#f3_r = struct.unpack("<H",file.read(2))[0]
							#f4_r = struct.unpack("<H",file.read(2))[0]
								
							#f1 = 0
							#f2 = 0
							#f3 = 0
							#f4 = 0
								
							#if (f1_r + 2 < vertices_len):
							#	f1 = f1_r + 1
							#else:
							#	f1 = -1
									
							#if (f2_r + 2 < vertices_len):
							#	f2 = f2_r + 1
							#else:
							#	f2 = -1
									
							#if (f3_r + 2 < vertices_len):
							#	f3 = f3_r + 1
							#else:
							#	f3 = -1
								
							#if (f4_r + 2 < vertices_len):
							#	f4 = f4_r + 1
							#else:
							#	f4 = -1
				