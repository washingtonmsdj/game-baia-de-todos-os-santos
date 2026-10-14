"""Regressões do contato lateral; não aprovam navegação da B81."""
import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/world'))
from character_slide import lateral_contact, project_slide
from slice_geometry import capsule_distances


def rectangle(a, b, c, d):
    return np.array([[a, b, c], [a, c, d]], dtype=float)


class CharacterSlideRegression(unittest.TestCase):
    def setUp(self):
        self.wall = rectangle([0,-2,0], [0,2,0], [0,2,2], [0,-2,2])
        self.cap = rectangle([0,-2,1], [1,-2,1], [1,2,1], [0,2,1])
        self.previous = np.array([-.31, 0, .015])
        self.proposed = np.array([-.25, .1, .015])
        self.witness = np.array([-.27, .075, .015])

    def contact(self, tri, previous=None, proposed=None, witness=None):
        return lateral_contact(self.previous if previous is None else previous,
                               self.proposed if proposed is None else proposed,
                               self.witness if witness is None else witness,
                               tri, .30, 1.80, .015)

    def test_horizontal_face_first_tie_does_not_disable_lateral_slide(self):
        tri = np.concatenate([self.cap, self.wall])
        distances = capsule_distances(self.witness, tri, .30, 1.80)
        old_index = int(np.argmin(distances))
        old_normal = np.cross(tri[old_index,1]-tri[old_index,0], tri[old_index,2]-tri[old_index,0])
        self.assertAlmostEqual(np.linalg.norm(old_normal[:2]), 0)
        contact = self.contact(tri)
        self.assertIsNotNone(contact)
        self.assertGreaterEqual(contact['index'], 2)
        np.testing.assert_allclose(contact['normal'], [-1,0,0])

    def test_projection_stays_on_initial_side_and_has_clearance(self):
        contact = self.contact(self.wall)
        slide = project_slide(self.previous, self.proposed, contact['normal'])
        np.testing.assert_allclose(slide, [-.31,.1,.015])
        for t in np.linspace(0,1,101):
            self.assertGreaterEqual(capsule_distances(self.previous+(slide-self.previous)*t,self.wall).min(), .30-.015)

    def test_floor_only_is_not_lateral_contact(self):
        self.assertIsNone(self.contact(self.cap))

    def test_distant_wall_is_not_selected_to_force_success(self):
        self.assertIsNone(self.contact(self.wall + [5,0,0]))

    def test_moving_away_does_not_project_into_wall(self):
        self.assertIsNone(self.contact(self.wall, proposed=np.array([-.4,.1,.015])))

    def test_opposite_winding_has_same_physical_normal(self):
        np.testing.assert_allclose(self.contact(self.wall[:,::-1])['normal'], [-1,0,0])

    def test_corner_remains_blocked_by_second_wall(self):
        second = rectangle([-2,0,0], [2,0,0], [2,0,2], [-2,0,2])
        tri = np.concatenate([self.wall,second])
        previous=np.array([-.31,-.31,.015]);proposed=np.array([-.25,-.25,.015]);witness=np.array([-.27,-.27,.015])
        contact=self.contact(tri,previous,proposed,witness)
        slide=project_slide(previous,proposed,contact['normal'])
        self.assertLess(capsule_distances(slide,tri).min(), .30-.015)
        # O CCD do controller deve rejeitar esta proposta; projeção não é aprovação.

    def test_tangency_is_not_solid_contact(self):
        self.assertIsNone(self.contact(self.wall,witness=np.array([-.30,.075,.015])))

    def test_degenerate_triangles_are_not_normals(self):
        self.assertIsNone(self.contact(np.zeros((1,3,3))))

    def test_deep_ccd_sample_is_refined_to_lateral_contact(self):
        tri=np.concatenate([self.cap,self.wall])
        contact=self.contact(tri,proposed=np.array([.2,.1,.015]),witness=np.array([.1,.075,.015]))
        self.assertIsNotNone(contact)
        np.testing.assert_allclose(contact['normal'],[-1,0,0])
        self.assertLess(contact['selection_point'][0],0)
        self.assertAlmostEqual(contact['distance'],.30-.015,places=7)

    def test_invalid_initial_overlap_is_not_recovered_by_slide(self):
        self.assertIsNone(self.contact(self.wall,previous=np.array([-.2,0,.015])))


if __name__ == '__main__':
    unittest.main()
