# Helper scripts and reference project workspace for 8051 assembly with ASXXXX toolkit
	This repository contains a reference makefile and area defintions for use with the as8051 assembler suite. It also contains scripts to make assembly level 8051 development less error prone.

	Dependencies:
	 1. JOM to run the makefile in Windows (https://wiki.qt.io/Jom)
	 2. ASXXXX assembler/linker suite (https://shop-pdp.net/ashtml/). This is a well documented FOSS friendly suite.
	 3. Python 3 to run the scripts

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

# Motivations
	1. The primary dev tool for 8051 derivatives like Megawin or Nuvoton is the Keil IDE. The free version is limited to 2K code space. One of the goals was to find a FOSS friendly dev environment with no such limitations. 
		1. Additional goal was to use something that's supported on multiple platforms.
		2. This repo was tested on Windows10 but it doesn't have an OS dependency. Linux dev environment can use the Makefile without JOM. ASXXXX is cross-platform, so is Python. 
		3.The only limitation is the Megawin COM ISP tool which is released only for Windows. There is a way to implement it in python but as of now I have no plans to develop it.
	2. Assembly programming was targetted because there aren't any good FOSS C compilers. SDCC generates code but it has a few limitations and the generated asm is suboptimal
		1. The 8051 assembly/arch is pretty simple, so ALPs aren't diffcult to write.
		2. At the same time, the arch isn't optimized for the C language. Manually assembly seems to be a LOT more compact
		3. The main cause of frustration with 8051 assembly IMO comes from accidentl misuse of addresses (bit address used in a byte instruction for e.g.) or improper syntax for an immediate value. The accompanying linting script and the area restrictions should help with this