from __future__ import annotations
from typing import Any, Union
import abc
from math import pi as PI, sqrt, sin, cos, atan2
from vec import VecXZ, VecY, VecX
from polytope import SizePolygon

class BuoyantPolygon(SizePolygon):
    def apply_buoyant_force(self, p: float, g: Union[VecXZ,float]):
        if isinstance(g, (int, float)):
            g = VecXZ(.0, g)

        # weight of displaced fluid 
        # use -g to flip the vector direction
        self.apply_force(-p*self.volume*g) 
