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
    (case, (jargs, jkwargs, jrc)) = unordered_join((f1,), (f2,), (f3,))
    return case

def ordered_f123():
    (case, (jargs, jkwargs, jrc)) = ordered_join((f1,), (f2,), (f3,))
    return case

def unordered():
    f1()
    f2()
    f3()
    return unordered_f123()

def ordered():
    f1()
    f2()
    f3()
    return ordered_f123()


print('Expecting 0,1,2 uniformally random')
print([unordered() for _ in range(100)])

print('Expecting 0 exclusively')
print([ordered() for _ in range(100)])

