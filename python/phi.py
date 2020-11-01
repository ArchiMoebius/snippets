import sys
from sympy.solvers import solve
from sympy import Symbol
x = Symbol('x')


def gcd(a, b):
    while b:
        a, b=b, a%b
    return a
def phi(a):
    b=a-1
    c=0
    while b:
        if not gcd(a,b)-1:
            c+=1
        b-=1
    return c

for i in range(1, 100):
  ret = solve(2*x+1-i+phi(i), x)[0]
  sys.stdout.write("i: %d phi: %d\t2*k+1 = %d, k: %d\n" % (i, phi(i), 2*ret+1, ret))
  if i % 10 == 0:
    print

print
