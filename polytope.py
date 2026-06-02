from __future__ import annotations
from typing import Any, override
import abc
from math import pi as PI, sqrt, sin, cos, atan2
import operator
import functools
from vec import Vec, VecXZ, VecY, VecX

class Polytope(abc.ABC): # or, "Pylotope"
    '''The most abstract and all inclusive type for an arbitrary n-dimensional physical object'''
    s: Vec # displacement
    a: Vec # angle, orientation (not direction of movement)
    v: Vec # velocity

    def apply_force(self, f: Vec):
        self.v += f / self.mass

class PolytopeGroup(Polytope, Vec[Polytope], abc.ABC):
    '''A Polytope that owns multiple child Polytopes, all positioned relative to its origin'''
    pass

class Polygon(Polytope):
    '''A 2D physical object'''
    s: VecXZ # we use Z for vertical position in aeronautical engineering
    a: VecY  # rotation around the y axis

class SizePolygon(Polygon):
    d: Vec # dimensions (size/volume)

    @property
    def volume(self):
        return functools.reduce(operator.mul, self.d)

class MassPolygon(SizePolygon):
    p: float # density

    @property
    def mass(self):
        return self.volume*self.p

    def apply_gravitational_force(self, g: Union[VecXZ,float]):
        '''Takes a gravity acceleration vector'''
        if isinstance(g, (int, float)):
            g = VecXZ(.0, g)

        self.apply_force(self.mass*g) # TODO check that vector math expansion will work here

class PolygonGroup(Polygon, PolytopeGroup):
    def __init__(self, *polys):
        super().__init__()
        self._polys = list(polys)

# === SHAPES ==

class Line(SizePolygon):
    d: VecX # line width

class Circle(SizePolygon):
    _diameter: Line

    @property
    def diameter(self) -> float:
        return self._diameter.d.x

    @property
    def radius(self) -> float:
        return self.diameter / 2

    @property
    @override
    def volume(self) -> float:
        '''The volume, or area of the circle'''
        return PI*self.radius**2

class Cylinder(SizePolygon):
    cap: Circle
    line: Line # the line of the cylinder length
    
    @property
    @override
    def volume(self) -> float:
        return self.line.volume*self.cap.volume
    
    
