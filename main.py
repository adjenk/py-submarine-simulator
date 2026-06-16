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

    def force(self, f, angle) -> VecXZ:
        xf = f*math.cos(angle)
        zf = f*math.sin(angle)
        return VecXZ(xf, zf)

    def draw(self, surface, pos, angle):
        ox = -80
        oz = 0

        rx = ox * math.cos(angle) - oz * math.sin(angle)
        rz = ox * math.sin(angle) + oz * math.cos(angle)

        pg.draw.circle(
            surface,
            (255, 0, 0),
            (int(pos.x + rx) + 400, int(pos.z + rz) + 300),
            5
        )


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

class ConningTower(Polygon):
    def __init__(self, s, a):
        self.s = s
        self.a = a
        self.points = [
            VecXZ(-10, -45),
            VecXZ( 10, -45),
            VecXZ( 10, -15),
            VecXZ(-10, -15)
        ]

    def draw(self, surface, pos, angle):
        pts = []
        for p in self.points:
            rx = p.x * math.cos(angle) - p.z * math.sin(angle)
            rz = p.x * math.sin(angle) + p.z * math.cos(angle)
            pts.append((int(pos.x + rx) + 400, int(pos.z + rz) + 300))

        pg.draw.polygon(surface, (180,180,160), pts)

    
class Submarine(BuoyantPolygon, VisualPolygon, PolygonGroup):
    mass = 50000.0  # kg
    volume = math.pi * 80 * 20
    moment_of_inertia = 0.25 * 50000 * (80**2 + 20**2)  # for an ellipse

    def __init__(self, s: VecXZ, a: VecY, v: VecXZ = VecXZ(.0,.0)):
        self.s = s
        self.a = a
        self.v = v
        self.omega = 0.0  # angular velocity (radians/sec)

        hull = Hull()
        prop = Propeller(VecXZ(.0,.0), -self.a)

        # Explicitly create the list of polygons
        self._polys = [hull, prop]

        self._polys.append(ConningTower(self.s, self.a))

    def apply_torque(self, t: float):
        self.omega += t / self.moment_of_inertia

    def draw(self, surface):
        # draw the hull
        self._polys[0].draw(surface, self.s, self.a.y)

        # draw other parts (propeller, periscope, etc.)
        for poly in self._polys[1:]:
            poly.draw(surface, self.s, self.a.y)

    def tick(self, dt: float = 1/60):
        # apply drag force: F_d = 0.5 * cd * p * A * v^2
        cd = 0.04  # drag coefficient for a streamlined hull
        p = 1.0    # fluid density (pixel units)
        A = 40     # projected frontal area (hull height in pixels)
        drag_x = -0.5 * cd * p * A * self.v.x * abs(self.v.x)
        drag_z = -0.5 * cd * p * A * self.v.z * abs(self.v.z)
        self.apply_force(VecXZ(drag_x, drag_z))

        # update position from velocity
        self.s = VecXZ(
            self.s.x + self.v.x * dt,
            self.s.z + self.v.z * dt
        )

         # update angle from angular velocity
        self.a = VecY(self.a.y + self.omega * dt)

        # apply angular drag
        self.omega *= 0.90

        # wrap around screen bounds (origin is screen centre)
        self.s = VecXZ(
            (self.s.x + 400) % 800 - 400,
            (self.s.z + 300) % 600 - 300
        )

        # apply drag (horizontal only)
        self.v = VecXZ(self.v.x * 0.98, 0.0)

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
            submarine.apply_torque(-3000000)
        if keys[pg.K_RIGHT]:
            submarine.apply_torque(3000000)
        if keys[pg.K_UP]:
            thrust = 500000
            submarine.apply_force(submarine._polys[1].force(thrust, submarine.a.y))
        if keys[pg.K_DOWN]:
            thrust = 500000
            submarine.apply_force(submarine._polys[1].force(-thrust, submarine.a.y))
        if keys[pg.K_q]:
            break

#        submarine.apply_buoyant_force(1.0, VecXZ(0, -0.5))
#        submarine.apply_force(VecXZ(0, math.pi * 80 * 20 * 0.5))  # match buoyancy exactly

        # print(f"v={submarine.v.x:.3f},{submarine.v.z:.3f} s={submarine.s.x:.3f},{submarine.s.z:.3f} a={submarine.a.y:.3f} omega={submarine.omega:.3f}")
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

