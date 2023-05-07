#leStoppe 2023-05-07 (megawin_8051_asm_header_extractor.py)
# ref. to the sample asm workspace in this repo. It uses the ASXXXX (AS8051) and aslink toolchain
# from https://shop-pdp.net/
#
# The megawin chips come with both code examples of all peripherals and headerfiles that are tailored
# for use with Keil. This script extracts the definitions and puts in an assembly file suited for
# the workspace. Pleae use this approach and also run checks with the linter script (rattle_snake.py)
# to avoid mistakes in the asm code. It'll make the assembly level development a lot easier. The 
# workspace also leverages configurations to check for incorrect memory accesses and size limits.

import re
import argparse
import os

def check_files_existance(input_file_list):
	for file in input_file_list:		
		if (not os.path.isfile (file)):
			print ("Error! File \'{0}\' not found".format(file))
			exit()

# Observations in the megawin header:
# 	1) name EQU value defines bitfields
#	2) name DATA value defines SFR memories
#	3) name BIT symbol.x defines a BIT accessible SFR. 
#		1) symbol.x is hardcoded into the assembler. Keil will have it but AS8051 may not.
#		2) have the script explicitly specify the symbol and address (need for linting and to ensure that all the available bit SFRs exist for the chip)
#	4) add an equ or a comment for 'name' in (3). IMO the symbol.x is a better way to show that an identifier is for a bit address

re_ifile_equ = re.compile(r"([a-zA-Z0-9_]+)\s+EQU\s+([a-fA-F0-9]+)")
re_ifile_dat = re.compile(r"([a-zA-Z0-9_]+)\s+DATA\s+([a-fA-F0-9]+)")
re_ifile_bit = re.compile(r"([a-zA-Z0-9_]+)\s+BIT\s+([a-zA-Z0-9\._]+)")
re_ifile_bit_dot_style = re.compile (r"\s+([a-zA-Z0-9_]+)\.(\d{1})$")
def extract_register_data(asm_include_file):
	fh_ifile = open(asm_include_file, 'r')
	results_dict = {}
	#hold the general equ defintions
	results_dict['equ'] = {}
	#holds the byte sfr address
	results_dict['dat'] = {}
	#holds the bit definitions (e.g. P02 BIT P0.2)
	results_dict['bitequ'] = {}
	#holds the bit sfr address
	results_dict['bit'] = {}

	for line in fh_ifile:
		match1 = re_ifile_equ.search(line)
		if (match1):
			def_name = match1.groups()[0]
			def_value = match1.groups()[1]
			def_value = int (def_value, 16)
			def_value = hex(def_value)
			results_dict['equ'][def_name] =def_value
			continue
		match1 = re_ifile_dat.search(line)
		if (match1):
			def_name = match1.groups()[0]
			def_value = match1.groups()[1]
			def_value = int (def_value, 16)
			def_value = hex(def_value)
			results_dict['dat'][def_name] = def_value
			continue
		match1 = re_ifile_bit.search(line)
		match2 = re_ifile_bit_dot_style.search(line)
		if (match1):
			def_name = match1.groups()[0]
			def_value = match1.groups()[1]
			results_dict['bitequ'][def_name] = def_value
			if (not match2):
				print("Error! BIT specification doesn't have a symbol.x definition")
				print(line)
				exit()
			sfr_base_name = match2.groups()[0]
			sfr_bit_offset= match2.groups()[1]
			address_final = int (results_dict['dat'][sfr_base_name], 16) + int (sfr_bit_offset, 16)
			results_dict['bit'][sfr_base_name + "." + sfr_bit_offset] = hex(address_final)
			continue
	fh_ifile.close()

	return results_dict

def generate_asxxxx_header_file(output_filename, register_data):
	fh_out = open(output_filename, 'w')
	fh_out.write (".title extracted_megawin_8051_header\n\n\n")

	fh_out.write(".bank SFRBIT (BASE=0x80, SIZE=0x7F)\n")
	fh_out.write(".bank SFRBYTE (BASE=0x80, SIZE=0x7F)\n\n")

	fh_out.write ("; The addresses are written relative to area base (0x80) to work around asxxxx limitations\n")
	fh_out.write (".area SFRBIT (ABS, OVR, DSEG, BANK=SFRBIT)\n\n")
	for counter, key in enumerate(register_data['bit']):
		address_offset = int ( register_data['bit'][key], 16) - int ("0x80", 16)
		address_offset = hex (address_offset)
		fh_out.write ("\t{0} = . + {1}\n".format(key, address_offset) )
	fh_out.write ("; {0} SFR bitname to ram address mappings insert".format(counter) )

	for counter, key in enumerate(register_data['bitequ']):
		#address_offset = int ( register_data['bitequ'][key], 16) - int ("0x80", 16)
		#address_offset = hex (address_offset)
		fh_out.write ("\t{0} .equ {1}\n".format(key, register_data['bitequ'][key]) )
	fh_out.write ("; {0} SFR fieldname to bitname mappings insert".format(counter) )
	fh_out.write ("\n.end\n")

	fh_out.write (".area SFRBYTE (ABS, OVR, DSEG, BANK=SFRBYTE)\n\n")
	for counter, key in enumerate(register_data['dat']):
		address_offset = int ( register_data['dat'][key], 16) - int ("0x80", 16)
		address_offset = hex (address_offset)
		fh_out.write ("\t{0} = . + {1}\n".format(key, address_offset) )
	fh_out.write ("; {0} SFR bytename to ram address mappings insert".format(counter) )

	for counter, key in enumerate(register_data['equ']):
		#address_offset = int ( register_data['bitequ'][key], 16) - int ("0x80", 16)
		#address_offset = hex (address_offset)
		fh_out.write ("\t{0} .equ {1}\n".format(key, register_data['equ'][key]) )
	fh_out.write ("; {0} SFR fieldname to bytename mappings insert".format(counter) )
	fh_out.write ("\n.end\n")

	fh_out.close()


# setup the argument parser, get the arguments and call respective functions
parser = argparse.ArgumentParser(
			prog='megawin_8051_asm_header_extractor.py',
			description='Converts the Keil based Megawin 8051 asm headerfile to work with ASXXXX assembler',
			epilog='------')

parser.add_argument('--input', metavar='input_file', type=str,
			action='store', nargs=1,
			help='Megawin 8051 asm include file')
parser.add_argument('--output', metavar='output_file', type=str,
			action='store', nargs=1,
			help='converted AS8051 compatible asm include file')

args = parser.parse_args()

print (args.input[0])
#sanity check
check_files_existance(args.input)
register_data = extract_register_data(args.input[0])

#dump the scrubbed data into the outputfile
generate_asxxxx_header_file(args.output[0], register_data)
