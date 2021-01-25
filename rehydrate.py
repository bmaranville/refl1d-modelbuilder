from refl1d import names
from collections.abc import Callable
from typing import Any

deserializable = [n for n in names.__dict__ if hasattr(names.__dict__[n], 'to_dict')]

def dict_generator(indict, pre=None):
    pre = pre[:] if pre else []
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in dict_generator(value, pre + [key]):
                    yield d
            elif isinstance(value, list) or isinstance(value, tuple):
                for v in value:
                    for d in dict_generator(v, pre + [key]):
                        yield d
            else:
                yield pre + [key, value]
    else:
        yield pre + [indict]
        
def dict_walk(indict, callback):
    """ callback is a function that takes arguments (key, value) and returns something """
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in dict_walk(value, callback):
                    yield d
            elif isinstance(value, list) or isinstance(value, tuple):
                for v in value:
                    for d in dict_walk(v, callback):
                        yield d
            else:
                yield callback(key, value)

def get_types(serialized):
    types = set(list(dict_walk(m[0], lambda k,v: v if k=="type" else None)))
    types.discard(None)
    return types

TYPES = {
 'Bounded',
 'Experiment',
 'Magnetism',
 'NeutronProbe',
 'Parameter',
 'PolarizedNeutronProbe',
 'SLD',
 'Slab',
 'Stack',
 'Unbounded',
 'Vacuum'
}
 
from bumps.bounds import Bounds, init_bounds

from refl1d.names import Slab, Parameter, SLD, Stack, Experiment, NeutronProbe, Magnetism, Experiment, PolarizedNeutronProbe, Vacuum
from refl1d import names
import numpy as np

class Deserializer(object):
    def __init__(self):
        self.refs = {}
        self.deferred = {}

    def rehydrate(self, obj):
        if isinstance(obj, dict):
            obj = obj.copy()
            for key,value in obj.items():
                obj[key] = self.rehydrate(value)
            t = obj.pop('type', None)
            if t is not None and hasattr(self, t):
                #hydrated = getattr(self, t)(obj)
                hydrated = self.instantiate(t, obj)
                return hydrated
            else:
                return obj
        elif isinstance(obj, list):
            return [self.rehydrate(v) for v in obj]
        elif isinstance(obj, tuple):
            return tuple(self.rehydrate(v) for v in obj)
        else:
            return obj

    def instantiate(self, typename, serialized):
        s = serialized.copy()
        id = s.pop("id", None)
        hydrated = getattr(self, typename)(s)
        if id is not None and not id in self.refs:
            self.refs[id] = hydrated
        return hydrated

    def Parameter(self, s):
        s["bounds"] = s["bounds"]["limits"]
        return Parameter(**s)
        
    def Slab(self, s):           
        return Slab(**s)

    def SLD(self, s):
        return SLD(**s)
        
    def Stack(self, s):
        # this keyword is not expected by the constructor:
        s.pop("interface", None)
        layers = s.pop("layers", None)
        obj = Stack(**s)
        if layers is not None:
            obj.add(layers)
        return obj

    def Magnetism(self, s):
        return Magnetism(**s)

    def Experiment(self, s):
        return Experiment(**s)

    def NeutronProbe(self, s):
        for attr in ['T', 'dT', 'L', 'dL', 'R', 'dR']:
            if s[attr] is not None:
                s[attr] = np.array(s[attr], dtype='float')
        R, dR = s.pop('R'), s.pop('dR')
        if R is not None and dR is not None:
            s['data'] = [R, dR]
        return NeutronProbe(**s)

    def PolarizedNeutronProbe(self, s):
        mm, mp, pm, pp = s.pop('mm'), s.pop('mp'), s.pop('pm'), s.pop('pp')
        s['xs'] = [mm, mp, pm, pp]
        return PolarizedNeutronProbe(**s)

    def Vacuum(self, s):
        return Vacuum(**s)
            
