from __future__ import annotations
import numpy as np
from scipy.io import netcdf_file
import pygame as pg

class Bathymetry:
    # World scale: pixels per degree of longitude/latitude
    # Dover Strait is ~4 degrees wide, we want ~3200px world width
    PIXELS_PER_DEGREE = 800

    def __init__(self, path: str):
        f = netcdf_file(path, 'r', mmap=False)
        self.lats = f.variables['lat'][:].copy()
        self.lons = f.variables['lon'][:].copy()
        self.depth = f.variables['elevation'][:].copy()  # negative = ocean
        f.close()

        self.lat_min = self.lats.min()
        self.lon_min = self.lons.min()

        # prerender the seabed as a surface
        self.surface = self._render()

    def _depth_to_color(self, d: float) -> tuple:
        # d is negative for ocean, 0 or positive for land
        if d >= 0:
            return (34, 139, 34)  # land, green
        # scale depth: 0m = light blue, -60m = dark blue (Dover max ~60m)
        t = max(0.0, min(1.0, abs(d) / 60.0))
        r = int(0   + (0  - 0  ) * t)
        g = int(100 + (20 - 100) * t)
        b = int(200 + (100- 200) * t)
        return (r, g, b)

    def _render(self) -> pg.Surface:
        h, w = self.depth.shape
        surf = pg.Surface((w, h))
        for y in range(h):
            for x in range(w):
                surf.set_at((x, y), self._depth_to_color(self.depth[y, x]))
        # scale up to world pixel size
        world_w = int((self.lons.max() - self.lons.min()) * self.PIXELS_PER_DEGREE)
        world_h = int((self.lats.max() - self.lats.min()) * self.PIXELS_PER_DEGREE)
        return pg.transform.scale(surf, (world_w, world_h))

    def world_to_pixel(self, lon: float, lat: float) -> tuple[int, int]:
        x = int((lon - self.lon_min) * self.PIXELS_PER_DEGREE)
        y = int((self.lats.max() - lat) * self.PIXELS_PER_DEGREE)  # flip y
        return x, y

    def draw(self, screen: pg.Surface, camera: VecXZ):
        # camera is the world offset — blit the prerendered surface offset by camera
        screen.blit(self.surface, (int(camera.x), int(camera.z)))
