#use jom to compile these on windows
#this variant assembles separate object files (helps with dead code elimination at link stage)

build: assemble	
#aslink -b VECTORS=0x0 -b CODE=0x80 -m -ml -i -u megawin_test2.rel megawin_test.rel
#build using test.lnk file
#manual build command here also work. The key is to have the 'out' file
#aslink -f test
	aslink -m -i -u -w out megawin_test megawin_test2 variables -b VECTORS=0x0 -b CODE=0x80 -e

assemble:
	as8051 -l -o -s -g megawin_test.s 
	as8051 -l -o -s -g -a megawin_test2.s
	as8051 -l -o -s -g -a variables.s
#as8051 -l -o -s -g -a asxxxx_REG_MG72F6D17.s

clean:
	del *hlr *lst *ihx *map *rel *rst *sym