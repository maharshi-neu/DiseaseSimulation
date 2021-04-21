import unittest
import numpy as np

from main.Particle import Particle
from main.util import *


class TestSim(unittest.TestCase):

    def test_random_angle(self):
        value = random_angle()
        self.assertTrue(value, 0 <= value <= 2 * np.pi)

    def test_euclidean_distance(self):
        value, _, _ = euclidean_distance(-7,-4, 17,6.5)
        value = np.round(value, 3)
        self.assertEqual(value, 26.196)

    def test_bounce_particle(self):
        x, y = 1, 5.3
        p1 = Particle(x, y, 2, 0)
        p2 = Particle(x, y + .1, 2, 0)

        bounce_particle(p1, p2, 0, 0)

        self.assertNotEqual(p1.x, p2.x)
        self.assertNotEqual(p1.y, p2.y)

    def test_bounce_wall(self):
        x, y = 10, 3
        wall_vector = {
                'l': 10,
                't': 0,
                'r': 20,
                'b': 10
                }
        p1 = Particle(x, y, 2, 0)
        angle = p1.angle

        bounce_wall(p1, wall_vector)

        self.assertNotEqual(p1.angle, angle)

    def test_build_walls(self):
        o = build_walls(5, 0, 800, 0, 600)
        eo = {
                'l': 5,
                't': 5,
                'r': 795,
                'b': 595,
                'x0': 0,
                'y0': 0,
                'x1': 800,
                'y1': 600
                }

        self.assertEqual(o, eo)

    def test_random_coord(self):
        o = random_coord(10, 30, 2)

        self.assertTrue(o, 10 <= o <= 30)

    def test_calculate_r_naught(self):
        o = calculate_r_naught([1,5,3,2], 1.2)

        self.assertEqual(o, 0.67)

    def test_uniform_probability(self):
        o = uniform_probability()
        self.assertTrue(o, 0 <= o <= 1)

    def test_make_grid_array(self):
        o = make_grid_array(2,3)
        eo = {
                0: {
                    0: [], 1: [], 2: []
                    },
                1: {
                    0: [], 1: [], 2: []
                    }
                }
        self.assertEqual(o, eo)

    def test_which_grid(self):
        o = which_grid(2, 15, 2, 23)
        eo = (11, 7)

        self.assertEqual(o, eo)


if __name__ == '__main__':
    unittest.main()
