# Helper scripts and reference project for 8051 assembly with ASXXXX toolkit
	use JOM to run the makefile in Windows

# rattle_snake.py
Simple Python 3 linting script for 8051 assembly code. Use with the ASXXXX assembler toolkit.

rattle_snake.py is the linting script (needs a map file and one or more asm files)

e.g.  python .\rattle_snake.py --map_file out.map --asm_file megawin_test.s megawin_test2.s

1. checks for invalid memory access types
	1. Byte memory access in bit instruction and vice versa
	2. Internal ram high (80h-FFh) in direct mode
	3. External ram with internal ram instructions

2. checks for immediate value typos (e.g. MOV A, 0x20 when #0x20 was intended)

# megawin_8051_asm_header_extractor.py
Python 3 script to extract register defintions from Megawin Keil assembly inc header file. It'll generate an include file compatible with AS8051. Put in into the assembly code with .include /filename/

e.g. python .\megawin_8051_asm_header_extractor.py --input REG_MG82F6D17.inc --output asxxxx_REG_MG72F6D17.s