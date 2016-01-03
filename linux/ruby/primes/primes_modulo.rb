#!/usr/bin/env ruby

primes = []

print "Input max: "

(2..gets.to_i).each{|n|
    prime = true
    primes.each{|p|
        prime = false if n % p == 0
    }
    primes.push(n) if prime
}

puts "Primes are: "

primes.each{|p|
    puts p
}
