from __future__ import annotations
from typing import Any, override
import abc
import tomllib
import math
from vec import Vec, VecXZ, VecY
from polytope import Polygon, SizePolygon, PolygonGroup, Cylinder
from resistance import ResistantCylinder
from buoyancy import BuoyantPolygon
import pygame as pg

def hex_to_tuple(h: int) -> tuple[int,...]:
    l = []
    mask = 0xFF
    for i in range(int(math.log(h)/math.log(0xFF))+1):
        print(i, mask, h, h & mask)
        l = [(h & mask) >> i*8] + l
        mask <<= 8
    return tuple(l)


assert (r := hex_to_tuple(0x12)) == (18,), r
assert (r := hex_to_tuple(0x1234)) == (18,52), r
assert (r := hex_to_tuple(0x123456)) == (18,52,86), r

class VisualPolygon(SizePolygon, abc.ABC):
    @abc.abstractmethod
    def draw(self, surface: pg.Surface): # TODO allow origin point passed from parent
        pass

class VisualCylinder(VisualPolygon, Cylinder):
    @override
    def draw(self, surface: pg.Surface):
        pg.draw.rect(screen, (200, 200, 180), (400, 30, 300, 15))

class Propeller(Polygon):
    def __init__(self, s: VecXZ, a: VecY):
        self.s = s
        self.a = a

    def force(self, xa0, ya0, za0, f) -> tuple[float,float,float]:
        xa = xa0 + self.xa
        ya = ya0 + self.ya
        za = za0 + self.za

        # flip the direction to get forward force
        xf = -f*cos(za)*cos(ya)
        yf = -f*sin(za)
        zf = -f*cos(za)*sin(ya)

        return xf, yf, zf

    def draw(self, surface):
        pg.draw.circle(surface, (255, 0, 0), (int(self.s.x)+400 - 80, int(self.s.z)+300), 5)

class Hull(ResistantCylinder, VisualPolygon):
    def draw(self, surface, pos, angle):
        length = 160
        height = 40

        # Convert physics coords to screen coords
        x = int(pos.x) + 400
        y = int(pos.z) + 300

        # 1. Create a temporary surface for the hull
        image = pg.Surface((length, height), pg.SRCALPHA)

        # 2. Draw the ellipse onto that surface
        pg.draw.ellipse(image, (200, 200, 180), image.get_rect())

        # 3. Rotate the surface by the submarine's angle
        angle_degrees = -math.degrees(angle)
        rotated = pg.transform.rotate(image, angle_degrees)

        # 4. Center the rotated hull at (x, y)
        rect = rotated.get_rect(center=(x, y))

        # 5. Blit to the main surface
        surface.blit(rotated, rect)

    
class Submarine(VisualPolygon, PolygonGroup):
    def __init__(self, s: VecXZ, a: VecY, v: VecXZ = VecXZ(.0,.0)):
        self.s = s
        self.a = a
        self.v = v

        #hull = ResistantCylinder()
        hull = Hull()
        prop = Propeller(VecXZ(.0,.0), -self.a)

        # Explicitly create the list of polygons
        self._polys = [hull, prop]

        self._polys.append(Propeller(VecXZ(0,0), VecY(0)))

    def draw(self, surface):

        # draw the hull
        self._polys[0].draw(surface, self.s, self.a.y)

        # draw other parts (propeller, periscope, etc.)
        for poly in self._polys[1:]:
            poly.draw(surface)

    def tick(self, dt: float = 1/60):
        speed = 40

        # compute velocity
        # update position using existing velocity
        self.s = VecXZ(
            self.s.x + self.v.x * dt,
            self.s.z + self.v.z * dt
        )

        # update position (VecXZ is immutable → create new one)
        self.s = VecXZ(
            self.s.x + self.v.x * dt,
            self.s.z + self.v.z * dt
        )

    def rotate(self, da: float):
        self.a = VecY(self.a.y + da)


def main():

    with open('config.toml', 'rb') as cfg_file:
        cfg = tomllib.load(cfg_file)

    pg.init()
    pg.display.set_caption(cfg['screen']['title'])

    screen = pg.display.set_mode(cfg['screen']['d'])
    submarine = Submarine(VecXZ(.0,.0), VecY(.0))

    clock = pg.time.Clock()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                break

        dt = clock.get_time() / 1000.0

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            submarine.rotate(-0.05)
        if keys[pg.K_RIGHT]:
            submarine.rotate(0.05)
        if keys[pg.K_UP]:
            thrust = 20
            submarine.v = VecXZ(
                submarine.v.x + math.cos(submarine.a.y) * thrust * dt,
                submarine.v.z + math.sin(submarine.a.y) * thrust * dt
            )

        if keys[pg.K_DOWN]:
            pass
        if keys[pg.K_q]:
            break

        submarine.tick()

        # the background sky and water
        screen.fill(cfg['screen']['color'])
        pg.draw.rect(screen, (0, 0, 255), (0, 100, 800, 500))

        submarine.draw(screen)
        
        pg.display.flip()
        clock.tick(60)

    pg.quit()

if __name__ == '__main__':
    main()

