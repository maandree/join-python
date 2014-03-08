#!/usr/bin/python3
'''
join python – Join-calculus for Python
Copyright © 2014  Mattias Andrée (maandree@member.fsf.org)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from join import *

import time


@fragment
def f1():
    pass

@fragment
def f2():
    pass

@fragment
def f3():
    pass


def unordered_f123():
    (case, (jargs, jkwargs, jrc)) = unordered_join((f1,), f2, (f3,))
    return case

def unordered():
    f1()
    f2()
    f3()
    return unordered_f123()


print('Expecting 0,1,2 uniformally random')
print([unordered() for _ in range(100)])
print()


def ordered_f123():
    (case, (jargs, jkwargs, jrc)) = ordered_join((f1,), f2, (f3,))
    return case

def ordered():
    f1()
    f2()
    f3()
    return ordered_f123()


print('Expecting 0 exclusively')
print([ordered() for _ in range(100)])
print()


@puresignal
def sig():
    time.sleep(0.25)
    print('  first')
    return 'correct signal return'

print('Testing signals')
s = sig()
print('  last')
print('  signal returned: ' + s.join())
print()



@fragment
@puresignal
def fsig1(value):
    pass

@fragment
@puresignal
def fsig2(value):
    pass

@fragment
@puresignal
def fsig3(value):
    pass

def unjoining(index):
    if index == 0:  fsig1(1)
    if index == 1:  fsig2(2)
    if index == 2:  fsig3(3)
    (case, (jargs, jkwargs, jrc)) = ordered_join((fsig1,), (fsig2,), (fsig3,))
    if index != 0:  fsig1(1)
    if index != 1:  fsig2(2)
    if index != 2:  fsig3(3)
    print(' ', *jargs)
    time.sleep(0.25)

print('Testing internal unjoining and signal fragments, expecting 1,2,1')
unjoining(0)
unjoining(1)
unjoining(2)
print()


def c(value):
    print('  Not last (but often ordered): %i' % value)
    time.sleep(1)

print('Testing concurrently')
concurrently(lambda : c(0), lambda : c(1), lambda : c(2), lambda : c(3))
print('  Last (delayed c:a 1 s)')
print()


print('Testing concurrently with @signal and @puresignal')
concurrently(signal(lambda : c(0)), signal(lambda : c(1)), puresignal(lambda : c(2)), puresignal(lambda : c(3)))
print('  Last (delayed c:a 1 s)')
print()


@signal
def fsig1(value):
    pass

@signal
def fsig2(value):
    pass

@signal
def fsig3(value):
    pass

def unjoining(index):
    if index == 0:  fsig1(1)
    if index == 1:  fsig2(2)
    if index == 2:  fsig3(3)
    (case, (jargs, jkwargs, jrc)) = ordered_join((fsig1,), (fsig2,), (fsig3,))
    if index != 0:  fsig1(1)
    if index != 1:  fsig2(2)
    if index != 2:  fsig3(3)
    print(' ', *jargs)
    time.sleep(0.25)

print('Testing @signal, expecting 1,2,1')
unjoining(0)
unjoining(1)
unjoining(2)
print()


class C:
    def __init__(self, value):
        self.value = value
    
    @joinmethod
    @fragment
    def f(self, v):
        print('  %i' % (self.value + v))

f1 = C(1).f
f2 = C(2).f

print('Testing @joinmethod, expecting 11,22')
f1(10)
f2(20)
print()

