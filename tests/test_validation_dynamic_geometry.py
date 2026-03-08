from __future__ import annotations

import unittest

from core.validation.validator_gate import validate_layer_c_completeness


class DynamicGeometryValidationTest(unittest.TestCase):
    def test_single_tubs_uses_family_required_paths(self) -> None:
        config = {
            "geometry": {
                "structure": "single_tubs",
                "params": {"child_rmax": 12.0, "child_hz": 30.0},
                "root_name": "target",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Cu"], "volume_material_map": {"target": "G4_Cu"}},
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 1.0,
                "position": {"type": "vector", "value": [0.0, 0.0, 0.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertTrue(report.ok)
        self.assertNotIn("geometry.params.module_x", report.missing_required_paths)
        self.assertNotIn("geometry.params.module_y", report.missing_required_paths)
        self.assertNotIn("geometry.params.module_z", report.missing_required_paths)

    def test_single_tubs_reports_missing_family_params(self) -> None:
        config = {
            "geometry": {
                "structure": "single_tubs",
                "params": {"child_rmax": 12.0},
                "root_name": "target",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Cu"], "volume_material_map": {"target": "G4_Cu"}},
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 1.0,
                "position": {"type": "vector", "value": [0.0, 0.0, 0.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertFalse(report.ok)
        self.assertIn("geometry.params.child_hz", report.missing_required_paths)

    def test_single_sphere_uses_family_required_paths(self) -> None:
        config = {
            "geometry": {
                "structure": "single_sphere",
                "params": {"child_rmax": 50.0},
                "root_name": "sphere",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Pb"], "volume_material_map": {"sphere": "G4_Pb"}},
            "source": {
                "type": "point",
                "particle": "e-",
                "energy": 5.0,
                "position": {"type": "vector", "value": [0.0, 0.0, -200.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "hdf5", "path": "output/result.hdf5"},
        }
        report = validate_layer_c_completeness(config)
        self.assertTrue(report.ok)
        self.assertNotIn("geometry.params.module_x", report.missing_required_paths)
        self.assertNotIn("geometry.params.module_y", report.missing_required_paths)
        self.assertNotIn("geometry.params.module_z", report.missing_required_paths)

    def test_single_sphere_reports_missing_radius(self) -> None:
        config = {
            "geometry": {
                "structure": "single_sphere",
                "params": {},
                "root_name": "sphere",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Pb"], "volume_material_map": {"sphere": "G4_Pb"}},
            "source": {
                "type": "point",
                "particle": "e-",
                "energy": 5.0,
                "position": {"type": "vector", "value": [0.0, 0.0, -200.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "hdf5", "path": "output/result.hdf5"},
        }
        report = validate_layer_c_completeness(config)
        self.assertFalse(report.ok)
        self.assertIn("geometry.params.child_rmax", report.missing_required_paths)

    def test_single_orb_uses_family_required_paths(self) -> None:
        config = {
            "geometry": {
                "structure": "single_orb",
                "params": {"child_rmax": 35.0},
                "root_name": "orb",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Pb"], "volume_material_map": {"orb": "G4_Pb"}},
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 3.0,
                "position": {"type": "vector", "value": [0.0, 0.0, -20.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertTrue(report.ok)

    def test_single_orb_reports_missing_radius(self) -> None:
        config = {
            "geometry": {
                "structure": "single_orb",
                "params": {},
                "root_name": "orb",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Pb"], "volume_material_map": {"orb": "G4_Pb"}},
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 3.0,
                "position": {"type": "vector", "value": [0.0, 0.0, -20.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertFalse(report.ok)
        self.assertIn("geometry.params.child_rmax", report.missing_required_paths)

    def test_ring_graph_program_satisfies_geometry_completeness(self) -> None:
        config = {
            "geometry": {
                "structure": "ring",
                "graph_program": {
                    "nodes": [
                        {"id": "module", "type": "Box", "x": 8.0, "y": 10.0, "z": 2.0},
                        {
                            "id": "ring",
                            "type": "Ring",
                            "module": "module",
                            "n": 12,
                            "radius": 40.0,
                            "clearance": 1.0,
                        },
                    ],
                    "root": "ring",
                    "constraints": [],
                },
                "params": {},
                "root_name": "ring",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Cu"], "volume_material_map": {"ring": "G4_Cu"}},
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 1.0,
                "position": {"type": "vector", "value": [0.0, 0.0, 0.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertTrue(report.ok)
        self.assertNotIn("geometry.params.module_x", report.missing_required_paths)
        self.assertNotIn("geometry.params.module_y", report.missing_required_paths)
        self.assertNotIn("geometry.params.module_z", report.missing_required_paths)

    def test_ring_requires_graph_program(self) -> None:
        config = {
            "geometry": {
                "structure": "ring",
                "params": {},
                "root_name": "ring",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Cu"], "volume_material_map": {"ring": "G4_Cu"}},
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 1.0,
                "position": {"type": "vector", "value": [0.0, 0.0, 0.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertFalse(report.ok)
        self.assertIn("geometry.graph_program", report.missing_required_paths)

    def test_single_torus_uses_family_required_paths(self) -> None:
        config = {
            "geometry": {
                "structure": "single_torus",
                "params": {"torus_rtor": 60.0, "torus_rmax": 8.0},
                "root_name": "torus",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Cu"], "volume_material_map": {"torus": "G4_Cu"}},
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 1.0,
                "position": {"type": "vector", "value": [0.0, 0.0, 0.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertTrue(report.ok)
        self.assertNotIn("geometry.params.module_x", report.missing_required_paths)
        self.assertNotIn("geometry.params.module_y", report.missing_required_paths)
        self.assertNotIn("geometry.params.module_z", report.missing_required_paths)

    def test_single_torus_reports_missing_minor_radius(self) -> None:
        config = {
            "geometry": {
                "structure": "single_torus",
                "params": {"torus_rtor": 60.0},
                "root_name": "torus",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Cu"], "volume_material_map": {"torus": "G4_Cu"}},
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 1.0,
                "position": {"type": "vector", "value": [0.0, 0.0, 0.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertFalse(report.ok)
        self.assertIn("geometry.params.torus_rmax", report.missing_required_paths)

    def test_single_ellipsoid_uses_family_required_paths(self) -> None:
        config = {
            "geometry": {
                "structure": "single_ellipsoid",
                "params": {"ellipsoid_ax": 12.0, "ellipsoid_by": 18.0, "ellipsoid_cz": 24.0},
                "root_name": "ellipsoid",
                "feasible": None,
            },
            "materials": {
                "selected_materials": ["G4_WATER"],
                "volume_material_map": {"ellipsoid": "G4_WATER"},
            },
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 2.0,
                "position": {"type": "vector", "value": [0.0, 0.0, -50.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertTrue(report.ok)

    def test_single_ellipsoid_reports_missing_axis(self) -> None:
        config = {
            "geometry": {
                "structure": "single_ellipsoid",
                "params": {"ellipsoid_ax": 12.0, "ellipsoid_by": 18.0},
                "root_name": "ellipsoid",
                "feasible": None,
            },
            "materials": {
                "selected_materials": ["G4_WATER"],
                "volume_material_map": {"ellipsoid": "G4_WATER"},
            },
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 2.0,
                "position": {"type": "vector", "value": [0.0, 0.0, -50.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertFalse(report.ok)
        self.assertIn("geometry.params.ellipsoid_cz", report.missing_required_paths)

    def test_single_elltube_uses_family_required_paths(self) -> None:
        config = {
            "geometry": {
                "structure": "single_elltube",
                "params": {"elltube_ax": 12.0, "elltube_by": 18.0, "elltube_hz": 24.0},
                "root_name": "elltube",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Si"], "volume_material_map": {"elltube": "G4_Si"}},
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 2.0,
                "position": {"type": "vector", "value": [0.0, 0.0, -50.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertTrue(report.ok)

    def test_single_polyhedra_requires_sides(self) -> None:
        config = {
            "geometry": {
                "structure": "single_polyhedra",
                "params": {"z1": -20.0, "z2": 0.0, "z3": 20.0, "r1": 10.0, "r2": 12.0, "r3": 14.0},
                "root_name": "polyhedra",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Si"], "volume_material_map": {"polyhedra": "G4_Si"}},
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 2.0,
                "position": {"type": "vector", "value": [0.0, 0.0, -50.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertFalse(report.ok)
        self.assertIn("geometry.params.polyhedra_nsides", report.missing_required_paths)


if __name__ == "__main__":
    unittest.main()
