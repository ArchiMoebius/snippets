#!/usr/bin/env ruby
start = ARGV[1].to_i(base=16)
puts
File.open(ARGV[0]).each{|line|
	line = line.match(/^([ A-Za-z0-9]{4,15}) ([a-zA-Z]{2,6}.*$)/)
	asm = line[2]
	saveHex = line[1]
	hex = saveHex.gsub(/ /, '')
	printf("%x\t%s\t%s\n", start, saveHex, asm)
	start = start + hex.length / 2
}
