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

import random
import threading


class puresignal:
    '''
    Function decorator for signals, functions that run asynchronously
    '''
    def __init__(self, f):
        '''
        Constructor
        
        @param  f:(*..., **...)→¿R?  The decorated function
        '''
        self.f = f
    
    
    def __call__(self, *args, **kwargs):
        '''
        Function invocation method
        
        @param   args:*...     Positional arguments
        @param   kwargs:**...  Named arguments
        @return  :join()→¿R?   Object with an argumentless function, `join`, that
                               joins with the signal and returns the signals return.
                               This is an extension to join-calculus
        '''
        class signal_:
            def __init__(self, f):
                def f_():
                    self.rc = f(*args, **kwargs)
                self.rc = None
                self.t = threading.Thread(target = f_)
                self.t.start()
            def join(self):
                self.t.join()
                return self.rc
        return signal_(self.f)



class fragment:
    '''
    Function decorator for fragments, functions that can be joined
    '''
    def __init__(self, f):
        '''
        Constructor
        
        @param  f:(...)→¿R?  The decorated function
        '''
        self.f = f
        self.queue = []
        self.condition = threading.Condition()
    
    
    def __call__(self, *args, **kwargs):
        '''
        Function invocation method
        
        @param   args:*...     Positional arguments
        @param   kwargs:**...  Named arguments
        @return  :¿R?          The value returned by the functon
        '''
        rc = self.f(*args, **kwargs)
        self.condition.acquire()
        self.queue.append((args, kwargs, rc))
        self.condition.notify()
        self.condition.release()
        return rc
    
    
    def unjoin(self, args, kwargs, rc):
        '''
        Used internally be the module to revert non-selected fragments in join-switches
        
        @param  args:tuple<...>        Positional arguments
        @param  kwargs:dict<str, ...>  Named arguments
        @param  rc:¿R?                 The returned value
        '''
        self.condition.acquire()
        self.queue.insert(0, (args, kwargs, rc))
        self.condition.notify()
        self.condition.release()



class signal(fragment):
    '''
    Shorthand for @fragment @puresignal
    '''
    def __init__(self, f):
        '''
        Constructor
        
        @param  f:(...)→¿R?  The decorated function
        '''
        fragment.__init__(self, puresignal(f))



def join(*fs):
    '''
    Join with fragments
    
    @param   fs:*fragment  The fragments
    @return  :list<(args:tuple<...>, kwargs:dict<str, ...>, rc:¿R?)>
                     The positional arguments and named arguments with which the fragments were
                     invoked and the values returned (extension to join-calculus) by those invocations
    
    -- OR --
    
    @param   f:fragment  The fragment
    @return  :(args:tuple<...>, kwargs:dict<str, ...>, rc:¿R?)
                     The positional arguments and named arguments with which the fragment as
                     invoked and the value returned (extension to join-calculus) by that invocation
    '''
    rc = []
    for f in fs:
        f.condition.acquire()
        if not len(f.queue):
            f.condition.wait()
        rc.append(f.queue.pop(0))
        f.condition.release()
    return rc[0] if len(fs) == 1 else rc



def ordered_join(*f_groups):
    '''
    Ordered join-switch, joins with the first group of fragments that returns.
    If there are matched fragments groups that have already returned, the one
    that appears first the case set is selected.
    
    @param   f_groups:*itr<fragment>  The fragments groups
    @return  :(int, (args:tuple<...>, kwargs:dict<str, ...>, rc:¿R?)|list<←>)
                     The index (zero-based) of the selected case and the positional arguments, and
                     arguments with which the fragments were invoked and the value returned (extension
                     to join-calculus) by those invocations (as a list of not exactly one fragement)
    '''
    condition = threading.Condition()
    rc, done = None, False
    index = 0
    for f_group in f_groups:
        def join_(fs, index):
            nonlocal rc, done, condition
            params = join(*fs)
            already_done = done
            if not already_done:
                condition.acquire()
            if not done:
                rc = (index, params)
                done = True
                condition.notify()
                condition.release()
            else:
                if not already_done:
                    condition.release()
                if len(fs) == 1:
                    fs[0].unjoin(*params)
                else:
                    for i, f in enumerate(fs):
                        f.unjoin(*(params[i]))
        threading.Thread(target = join_, args = (f_group, index)).start()
        index += 1
    condition.acquire()
    if not done:
        condition.wait()
    condition.release()
    return rc



def unordered_join(*f_groups):
    '''
    Ordered join-switch, joins with the first group of fragments that returns.
    If there are matched fragments groups that have already returned, one is
    selected at random, uniformally.
    
    @param   f_groups:*itr<fragment>  The fragments groups
    @return  :(int, (args:tuple<...>, kwargs:dict<str, ...>, rc:¿R?)|list<←>)
                     The index (zero-based) of the selected case and the positional arguments, and
                     arguments with which the fragments were invoked and the value returned (extension
                     to join-calculus) by those invocations (as a list of not exactly one fragement)
    '''
    ready = [i for i, fs in enumerate(f_groups) if all([len(f.queue) for f in fs])]
    if len(ready):
        i = ready[random.randrange(len(ready))]
        return (i, join(*(f_groups[i])))
    else:
        return ordered_join(*f_groups)



def concurrently(*fs):
    '''
    Run a set of functions concurrently and wait for all of them to return
    
    @param  fs:*()→void  The functions to run
    '''
    ts = [threading.Thread(target = f) for f in fs]
    for t in ts:
        t.start()
    for t in ts:
        t.join()



def joinmethod(f):
    '''
    Make a fragment of signal an instance method rather than a static method
    
    @param   f:(self, *..., **...)→¿R?  The static method
    @return  f:(self, *..., **...)→¿R?  The method made into a instance method
    '''
    return lambda self, *args, **kwargs : f(self, *args, **kwargs)

