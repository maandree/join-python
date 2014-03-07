#!/usr/bin/python3
# -*- python -*-
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

import time
import threading


class signal:
    def __init__(self, f):
        self.f = f
    
    def __call__(self, *args, **kwargs):
        threading.Thread(target = self.f, args = args, kwargs = kwargs).start()


class joinable:
    def __init__(self, f):
        self.f = f
        self.queue = []
        self.condition = threading.Condition()
    
    def __call__(self, *args, **kwargs):
        self.f(*args, **kwargs)
        self.condition.acquire()
        self.queue.append((args, kwargs))
        self.condition.notify()
        self.condition.release()


def join(f):
    f.condition.acquire()
    f.condition.wait()
    (jargs, jkwargs) = f.queue.pop(0)
    f.condition.release()
    return (jargs, jkwargs)


class test:
    @signal
    def signal(f, *args):
        f(*args)
    
    @joinable
    def joinable(*args, **kwargs):
        pass
    
    def join(param):
        (jargs, jkwargs) = join(test.joinable)
        print(param, dict(jkwargs), *jargs)


test.signal(test.join, 'join')
time.sleep(1)
test.joinable('arg1', 'arg2', a = 'A', b = 'B')

