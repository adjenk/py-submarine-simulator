from __future__ import annotations
from typing import Union, Callable, Literal
from collections.abc import Sequence, Iterator
import itertools
import functools
import operator

class Vec[T]:
    components: list[T]

    def __init__(self, *args):
        self.components = args
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            self.components = args[0]

    def __getitem__(self, idx: int) -> T:
        return self.components[idx]

    def __setitem__(self, idx: int, val: T):
        self.components[idx] = val

    def __len__(self):
        return len(self.components)

    def __repr__(self):
        return f"Vector({', '.join(map(str, self.components))})"

    def __iter__(self) -> Iterator[T]:
        return iter(self.components)

    def _expand_other(self, other: Union[Vec[T],T]) -> Vec[T]:
        if isinstance(other, Vec):
            return other
        elif isinstance(other, Sequence):
            return Vec(other)
        else:
            return Vec([other]*len(self.components))

    def __rmul__(self, other) -> Vec:
        return self.__mul__(other)

    @staticmethod
    def _make_expanded_other(f: Callable) -> Callable:
        #return functools.partialmethod(f,) # TODO shorter alternative
        @functools.wraps(f)
        def _f(self, *args, **kwargs) -> Any:
            return f(self, self._expand_other(args[0]), *args[1:], **kwargs)
        return _f

    @staticmethod
    def _fmap(f: Callable[T,T]) -> Callable[T,Vec]:
        def _map(vec: Vec[T]) -> Vec[T]: 
            return Vec([*map(f, vec.components)])
        return _map

    @staticmethod
    def _fmap2(f: Callable[T,T]) -> Callable[T,Vec[T]]:
        def _map2_1(vec1: Vec[T]) -> Vec[T]: 
            def _map2_2(vec2: Vec[T]) -> Vec[T]: 
                return Vec([*itertools.starmap(f, zip(vec1.components, vec2.components))])
            return _map2_2
        return _map2_1

    def magnitude(self) -> T:
        return sum(self**2)

    def direction(self) -> Vec[T]:
        return self / self.magnitude()

    def __neg__(self) -> Vec[T]:
        return self._fmap(operator.neg)(self)

    @_make_expanded_other
    def __add__(self, other: Vec) -> Vec:
        return self._fmap2(operator.add)(self)(other)

    @_make_expanded_other
    def __sub__(self, other: Vec) -> Vec:
        return self._fmap2(operator.add)(self)(-other)

    @_make_expanded_other
    def __mul__(self, other: Vec) -> float:
        return sum(self._fmap2(operator.mul)(self)(other).components)

    @_make_expanded_other
    def __truediv__(self, other: Vec) -> Vec:
        return self._fmap2(operator.truediv)(self)(other)

    def __pow__(self, p: int) -> float:
        return sum(self._fmap(lambda x: x**p)(self).components)

    @_make_expanded_other
    def __iadd__(self, other: Vec):
        # preserve subclass type by updating components in place
        self.components = list(self._fmap2(operator.add)(self)(other).components)
        return self

class VecXZ[T](Vec[T]):
    '''for 2d position, force, velocity, acceleration vectors'''
    @property
    def x(self) -> T:
        return self.components[0]

    @property
    def z(self) -> T:
        return self.components[1]

class VecX[T](Vec[T]):
    '''for 2d line length vectors'''
    @property
    def x(self) -> T:
        return self.components[0]

class VecY[T](Vec[T]): 
    '''for 2d angle vectors'''
    @property
    def y(self) -> T:
        return self.components[0]

class VecXYZ[T](Vec[T]):
    '''for 3d position, force, velocity, acceleration vectors'''
    @property
    def x(self) -> T:
        return self.components[0]

    @property
    def y(self) -> T:
        return self.components[1]

    @property
    def z(self) -> T:
        return self.components[3]
