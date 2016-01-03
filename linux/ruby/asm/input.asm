0b12           push	r11
0412           push	r4
0441           mov	sp, r4
2452           add	#0x4, r4
3150 e0ff      add	#0xffe0, sp
3b40 2045      mov	#0x4520, r11
073c           jmp	$+0x10
1b53           inc	r11
8f11           sxt	r15
0f12           push	r15
0312           push	#0x0
b012 6424      call	#0x2464
2152           add	#0x4, sp
6f4b           mov.b	@r11, r15
4f93           tst.b	r15
f623           jnz	$-0x12
3012 0a00      push	#0xa
0312           push	#0x0
b012 6424      call	#0x2464
2152           add	#0x4, sp
3012 1f00      push	#0x1f
3f40 dcff      mov	#0xffdc, r15
0f54           add	r4, r15
0f12           push	r15
2312           push	#0x2
b012 6424      call	#0x2464
3150 0600      add	#0x6, sp
b490 520e dcff cmp	#0xe52, -0x24(r4)
0520           jnz	$+0xc
3012 7f00      push	#0x7f
b012 6424      call	#0x2464
2153           incd	sp
3150 2000      add	#0x20, sp
3441           pop	r4
3b41           pop	r11
3041           ret
1e41 0200      mov	0x2(sp), r14
0212           push	sr
0f4e           mov	r14, r15
8f10           swpb	r15
024f           mov	r15, sr
32d0 0080      bis	#0x8000, sr
b012 1000      call	#0x10
3241           pop	sr
3041           ret
d21a 189a      call	&0x9a18
22dc           bis	@r12, sr
45b9           bit.b	r9, r5
4279           subc.b	r9, sr
2d55           add	@r5, r13
858e a4a2      sub	r14, -0x5d5c(r5)
67d7           bis.b	@r7, r7
14ae a119      dadd	0x19a1(r14), r4
76f6           and.b	@r6+, r6
42cb           bic.b	r11, sr
1c04 0efa      rrc	-0x5f2(r12)
a61b           invalid	@r6
74a7           dadd.b	@r7+, r4
416b           addc.b	r11, sp
d237           jge	$-0x5a
a253 22e4      incd	&0xe422
66af           dadd.b	@r15, r6
c1a5 938b      dadd.b	r5, -0x746d(sp)
8971 9b88      subc	sp, -0x7765(r9)
fa9b 6674      cmp.b	@r11+, 0x7466(r10)
4e21           jnz	$+0x29e
2a6b           addc	@r11, r10
b143 9151      mov	#-0x1, 0x5191(sp)
3dcc           bic	@r12+, r13
a6f5 daa7      and	@r5, -0x5826(r6)
db3f           jmp	$-0x48
8d3c           jmp	$+0x11c
4d18           rrc.b	r13
4736           jge	$-0x370
dfa6 459a 2461 dadd.b	-0x65bb(r6), 0x6124(r15)
921d 3291      sxt	&0x9132
14e6 8157      xor	0x5781(r6), r4
b0fe 2ddd      and	@r14+, -0x22d3(pc)
400b           reti	pc
8688 6310      sub	r8, 0x1063(r6)
3ab3           bit	#-0x1, r10
612b           jnc	$-0x13c
0bd9           bis	r9, r11
483f           jmp	$-0x16e
4e04           rrc.b	r14
5870 4c38      subc.b	0x384c(pc), r8
c93c           jmp	$+0x194
ff36           jge	$-0x200
0e01           rra	r14
7f3e           jmp	$-0x300
fa55 aeef      add.b	@r5+, -0x1052(r10)
051c           rrc	r5
242c           jc	$+0x4a
3c56           add	@r6+, r12
13af e57b      dadd	0x7be5(r15), 4
8abf 3040      bit	r15, 0x4030(r10)
c537           jge	$-0x74
656e           addc.b	@r14, r5
8278 9af9      subc	r8, &0xf99a
9d02 be83      call	-0x7c42(r13)
b38c e181      sub	@r12+, 8
3ad8           bis	@r8+, r10
395a           add	@r10+, r9
fce3 4f03      xor.b	#-0x1, 0x34f(r12)
8ec9 9395      bic	r9, -0x6a6d(r14)
4a15           rra.b	r10
ce3b           jl	$-0x62
fd1e           call	@r13+
7779           subc.b	@r9+, r7
c9c3 5ff2      bic.b	#0x0, -0xda1(r9)
3dc7           bic	@r7+, r13
5953           add.b	#0x1, r9
8826           jz	$-0x2ee
d0b5 d9f8 639e bit.b	-0x727(r5), -0x619d(pc)
e970 01cd      subc.b	@pc, -0x32ff(r9)
2119           rra	@sp
ca6a d12c      addc.b	r10, 0x2cd1(r10)
97e2 7538 96c5 xor	&0x3875, -0x3a6a(r7)
8f28           jnc	$+0x120
d682 1be5 ab20 sub.b	&0xe51b, 0x20ab(r6)
7389           sub.b	@r9+, 4
48aa           dadd.b	r10, r8
1fa3           dinc	r15
472f           jc	$-0x170
a564 de2d      addc	@r4, 0x2dde(r5)
b710           swpb	@r7+
9081 5205 8d44 sub	0x552(sp), 0x448d(pc)
cff4 bc2e      and.b	r4, 0x2ebc(r15)
577a d5f4      subc.b	-0xb2b(r10), r7
a851 c243      add	@sp, 0x43c2(r8)
277d           subc	@r13, r7
a4ca 1e6b      bic	@r10, 0x6b1e(r4)
0000           rrc	pc
0000           rrc	pc
