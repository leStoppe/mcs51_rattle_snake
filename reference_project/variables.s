.title memory allocations

; the bank specification lets the linker know where to place the areas and what the limits are
.bank IRAML (BASE=0x00, SIZE=0x7F)
.bank IRAMH (BASE=0x80, SIZE=0x7F)
.bank BITRAM (BASE=0x00, SIZE=0x7F)
.bank XRAM (BASE=0x00, SIZE=0x8F)
;.bank SFRBIT (BASE=0x80, SIZE=0x7F)
;.bank SFRBYTE (BASE=0x80, SIZE=0x7F)

.area IRAML (ABS, OVR, DSEG, BANK=IRAML)
; the variable naming conventions aren't critical but it helps to identify the type of memory to the user
; the segment names are critical. They'll be used by the linting script to validate memory accesses
;.org 0x0
	IRL_VAR1 = .
		.rmb 1
	IRL_VAR2 = .
		.rmb 1
.end

.area IRAMH (ABS, OVR, DSEG, BANK=IRAMH)
;.org 0x80
	IRH_VAR1 = .
		.rmb 1
	IRH_VAR2 = .
		.rmb 1

.end

.area BITRAM (ABS, OVR, DSEG, BANK=BITRAM)
;.org 0x00
	BIT_VAR1 = .
		.rmb 1
	BIT_VAR2 = .
		.rmb 1
.end

.area XRAM (ABS, OVR, DSEG, BANK=XRAM)
;.org 0x00
	XR_VAR1 = .
		.rmb 1
	XR_VAR2 = .
		.rmb 1
.end

;placeholder for SFR definitions. Use this to restirct certain instructions to SFRBIT and BITRAM
;.area SFRBIT (ABS, OVR, DSEG, BANK=SFRBIT)
;	;without a dummy variable, aslink would skip this area
;	DUMMY_SFRBIT = .
;.end

;placeholder for SFR byte definitions. Use this to restrict certain instructions (ram direct) SFRBYTE and IRAML
;.area SFRBYTE (ABS, OVR, DSEG, BANK=SFRBYTE)
	;without a dummy variable, aslink would skip this area
;	DUMMY_SFRBYTE = .

;.end