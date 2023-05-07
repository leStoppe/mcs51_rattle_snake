#lestoppe 2023-06-05 (rattle_snake.py)
# Use this script with 8051 assembly and ASXXXX assembler. This program will 
# check for common assembly issues and report errors. The goals are
#	1. Missing the # in an immediate constant. This will result in the instruction accessing memory instead.
#	2. using the wrong segment address in an instruction (bit address in a byte instruction, internal ram high used in direct mode for e.g.)
#	3. report code, ram space usage. Call depth (a bit hard)
#	4. Eventually generate a python script and kernel assembly tailored to the user assembly for interactive testing.
#
#	When linking use the following options (aslink -m -i -u -w) for compatibility

import re
import argparse
import os

def check_files_existance(input_file_list):
	for file in input_file_list:		
		if (not os.path.isfile (file)):
			print ("Error! File \'{0}\' not found".format(file))
			exit()


# Opens a single asm file (passed as arg) and checks for issue type #1 (refer above)
# the main culprits
re_immediate_number = re.compile (r"^\s*(MOV|ADD|ADDC|SUBB|ANL|ORL|XRL|CJNE|XCH)\s+.+\,\s*(\d+)")
# less probable but possible ones (unary operators and ones where it's operand1)
re_immediate_number2 = re.compile(r"^\s*(PUSH|POP|INC|DEC|CLR|SETB|CPL)\s+(\d+)")
def lint_check_immediate_numbers (asm_file_name):
	# allowed numbers, plain (20), prefixed (0b, 0B, 0o, 0O, 0q, 0Q, 0d, 0D, 0h, 0H,0x,0X)
	fh_asm = open(asm_file_name, 'r')
	issue_list = []
	for counter, line in enumerate(fh_asm):
		line = line.upper()
		if (re_immediate_number.search(line)):
			issue_list.append([counter+1, line])
		elif(re_immediate_number2.search(line) ):
			issue_list.append([counter+1, line])
	print ("Linting [imm const check] {0} , found {1} issues".format (asm_file_name, len(issue_list) )  )
	if (len(issue_list) > 0):
		print (">These lines have numerals without a # prefix. Is this intended to be an address ?")
		for issues in issue_list:
			print ("\t[{0}] {1}".format(issues[0], issues[1]) )

	fh_asm.close()

# opens a map file that aslink generates to get the areas and their stats
# always have the following areas, even if they're empty. It helps to minimize unintentional mistakes related to memory access
# looks for specific areas :
#	VECTORS : holds the reset vectors
#	CODE	: the flash codesegment where all the code fits in
#	IRAML	: lower internal ram (0-7Fh). Can be accessed in direct/indirect modes. Hold the registers, the bit ram and scratch area
#	IRAMH	: upper internal ram (0x80 - 0xFFh). Can be accessed indirectly only. The same address range in direct mode accesses SFRs. Big risk of typo
#	BITRAM	: IRAML (20h to 30h) are bit accessible as 0h-7FH. Risk of using bit address in byte instruction.
#	XRAM	: internal xtended ram (varies with chip). Range starts from 0, so there is risk of using this in iram or code instructions.
#			Additionally there is also a risk of exceeding available memory.

re_match_areas = re.compile(r"^(VECTORS|CODE|IRAML|IRAMH|BITRAM|XRAM)\s+([0-9A-Fa-f]+)\s+([0-9A-Fa-f]+)")
re_match_area_symbols = re.compile(r"([0-9A-Fa-f]{4})\s\s([a-zA-Z0-9_\.\$]+)")
def get_map_areas_size(map_file):
	fh_mapfile = open(map_file, 'r')
	area_list = []
	for line in fh_mapfile:
		match = re_match_areas.search(line)
		if (match):
			temp_dict = {}
			temp_dict['area'] = match.groups()[0]
			temp_dict['base_address'] = match.groups()[1]
			temp_dict['size'] = match.groups()[2]
			temp_dict['symbols'] = []
			area_list.append(temp_dict)
			continue

		#skip checking for symbols within an area before the first valid area is found
		if (len(area_list) == 0):
			continue

		#check for symbols defined in the last area match
		match2 = re_match_area_symbols.search(line)
		if (match2):
			symbol_name = match2.groups()[0]
			symbol_address = match2.groups()[1]
			area_list[-1]['symbols'].append([symbol_name, symbol_address])
	fh_mapfile.close()
	return area_list

def summarize_area_usage (area_data):
	print ("---------------------- Areas summary ------------------------")
	print ("Area\t\tStart\t\tSize")
	for item in area_data:
		print ("{0}\t\t0x{1}\t\t0x{2}".format(item['area'], item['base_address'], item['size'] ))
	print ("-------------------------------------------------------------")

def get_symbols_per_area (area_data):
	area_map = {}

	for item in area_data:
		area_name = item['area']
		area_symbols = []
		for symbols in item['symbols']:
			area_symbols.append(symbols[1])
		area_map[area_name] = area_symbols
	return area_map

#check for iram high range variables being used in direct access (this is invalid)
#direct mem is operand 2
re_mem_acces_irh_direct = re.compile(r"^\s*(MOV|ADD|XCH|ADDC|SUBB|ANL|ORL|XRL|CJNE)\s+[a-zA-Z0-9\@_]+\,\s*([a-zA-Z0-9_\.\$]+)")
#direct mem is operand 1
re_mem_acces_irh_direct2= re.compile(r"^\s*(MOV|PUSH|POP|INC|DEC|ANL|ORL|XRL|DJNZ)\s+([a-zA-Z0-9_\.\$]+)")
def lint_check_memory_access_types (asm_file_name, area_symbols):
	fh_asm = open (asm_file_name, 'r')
	issue_list = []
	for counter, line in enumerate(fh_asm):
		line = line.upper()
		match1 = re_mem_acces_irh_direct.search(line)
		if (match1):
			op2_name = match1.groups()[1]
			if (op2_name in area_symbols['IRAMH']):
				issue_list.append([counter+1, line])

		match2 = re_mem_acces_irh_direct2.search(line)

		if (match2):
			op2_name = match2.groups()[1]
			if (op2_name in area_symbols['IRAMH']):
				issue_list.append([counter+1, line])
	fh_asm.close()

	print ("Linting [high iram range direct access check] {0} , found {1} issues".format (asm_file_name, len(issue_list) )  )
	if (len(issue_list) > 0):
		print (">These instructions attempts to access the high iram range in direct mode. Please fix!")
		for issues in issue_list:
			print ("\t[{0}] {1}".format(issues[0], issues[1]) )


# setup the argument parser, get the arguments and call respective functions
parser = argparse.ArgumentParser(
			prog='rattle_snake.py',
			description='A simple python linter for 8051 assembly. Works with ASXXXX assembler',
			epilog='------')

parser.add_argument('--map_file', metavar='map_file', type=str,
			action='store', nargs=1,
			help='output map file generated by aslink')
parser.add_argument('--asm_file', metavar='asm_file', type=str,
			action='store', nargs='+',
			help='input assembly file to be linted')

args = parser.parse_args()

#print (args.map_file)
#print (args.asm_file)
check_files_existance(args.map_file)
check_files_existance(args.asm_file)

area_data = get_map_areas_size(args.map_file[0]) 
summarize_area_usage(area_data)
area_symbols = get_symbols_per_area(area_data)


#print (get_map_areas_size(args.map_file[0]))
lint_check_immediate_numbers(args.asm_file[0])
lint_check_memory_access_types(args.asm_file[0], area_symbols)