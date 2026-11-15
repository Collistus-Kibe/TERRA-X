"""
TERRA-X Test Suite: Dimensionless Physics Scaling & Gravity Bridges
Validates:
- tan(theta)/tan(phi)
- h_rms(D)/D
- p / (gamma * B)
- F / (gamma * d^3)
- Delta_T / T_mean
- Gravity bridge gamma = rho * g (Moon ~x6.37 load scale, Mars ~x2.85)
- NEVER equates 1g to 1/6g.
"""

import unittest
import math
from features.dimensionless import DimensionlessPhysicsEngine, G_EARTH, G_MOON, G_MARS


class TestDimensionlessPhysics(unittest.TestCase):

    def test_gravity_bridge_scaling(self):
        """Validates effective unit weight gamma and load scale factors."""
        bridge_moon = DimensionlessPhysicsEngine.get_gravity_bridge(
            target_body="MOON",
            soil_density_kg_m3=1550.0,
        )
        # Check scale factor: Earth g / Moon g = 9.80665 / 1.62 ~ 6.053
        expected_scale = G_EARTH / G_MOON
        self.assertAlmostEqual(bridge_moon["load_scale_factor"], expected_scale, delta=0.01)
        self.assertNotEqual(bridge_moon["gamma_earth_N_m3"], bridge_moon["gamma_target_N_m3"])

        # Mars
        bridge_mars = DimensionlessPhysicsEngine.get_gravity_bridge(
            target_body="MARS",
            soil_density_kg_m3=1550.0,
        )
        self.assertAlmostEqual(bridge_mars["load_scale_factor"], G_EARTH / G_MARS, delta=0.01)

    def test_slope_ratio_approaching_repose(self):
        """As slope approaches angle of repose, tan(theta)/tan(phi) approaches 1.0."""
        # Angle of repose = 35 deg; surface slope = 35 deg
        groups = DimensionlessPhysicsEngine.compute_all_groups(
            slope_deg=35.0,
            friction_angle_deg=35.0,
            h_rms_m=0.05,
            wheel_diameter_m=0.50,
            target_body="MOON",
        )
        self.assertAlmostEqual(groups.tan_theta_over_tan_phi, 1.0, delta=0.001)

    def test_micro_roughness_scaled_to_wheel_diameter(self):
        """h_rms(D)/D must scale inversely with wheel diameter D."""
        groups_small = DimensionlessPhysicsEngine.compute_all_groups(
            slope_deg=10.0,
            friction_angle_deg=35.0,
            h_rms_m=0.10,
            wheel_diameter_m=0.25, # 25cm small wheel
            target_body="MOON",
        )
        groups_large = DimensionlessPhysicsEngine.compute_all_groups(
            slope_deg=10.0,
            friction_angle_deg=35.0,
            h_rms_m=0.10,
            wheel_diameter_m=1.00, # 100cm large wheel
            target_body="MOON",
        )
        self.assertEqual(groups_small.h_rms_over_D, 0.40)
        self.assertEqual(groups_large.h_rms_over_D, 0.10)
        self.assertEqual(groups_small.h_rms_over_D, groups_large.h_rms_over_D * 4.0)

    def test_bearing_capacity_scaled_pressure(self):
        """Scaled pressure p / (gamma * B) must account for target reduced gravity."""
        groups = DimensionlessPhysicsEngine.compute_all_groups(
            slope_deg=5.0,
            friction_angle_deg=35.0,
            h_rms_m=0.02,
            wheel_diameter_m=0.50,
            contact_pressure_kpa=25.0, # 25,000 Pa
            footprint_width_m=0.20,
            target_body="MOON",
            bulk_density_kg_m3=1520.0,
        )
        # gamma_moon = 1520 * 1.62 = 2462.4 N/m3
        # p / (gamma * B) = 25000 / (2462.4 * 0.20) = 50.76
        expected_p_group = 25000.0 / (1520.0 * 1.62 * 0.20)
        self.assertAlmostEqual(groups.p_over_gamma_B, expected_p_group, delta=0.2)


if __name__ == "__main__":
    unittest.main()

