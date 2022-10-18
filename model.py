import math
import sys

# - Fuel particle -
# heat_content = 0                      # h
# tot_mineral_content = 0               # S_T, fraction!
# eff_mineral_content = 0               # S_e, fraction!
# particle_density = 0                  # ρ_p

# - Fuel array -
# surface_area_vol_ratio = 0            # σ
# oven_dry_fuel_load = 0                # w_0 (lb/ft^2)
# fuel_bed_depth = 0                    # δ
# dead_fuel_moisture_extinction = 0     # M_x, fraction!

# - Environmental -
# moisture_fraction = 0                 # M_f, fraction!
# midflame_wind_speed = 0               # U
# slope = 1
# slope_steepness = math.tan(slope)     # tan φ, fraction!

# - Required -
# SAV, fuel load, bed depth, dead fuel moisture of extinction.
# Slope, wind speed, moisture content is environmental (variables)
# Moisture content varies... set at < 20%
"""
Basic fire model (homogeneous fuels)
Input and output speeds are in ft/min
"""
def basic_spread_rate(heat_content=8000, tot_mineral_content=0.0555, eff_mineral_content=0.010,
    oven_dry_particle_density=32, surface_area_vol_ratio = 0, oven_dry_fuel_load = 0, packing_ratio = 0,
    fuel_bed_depth = 0, dead_fuel_moisture_extinction = 0, moisture_fraction = 0.1,
    midflame_wind_speed = 0, slope = 0):

    if (not packing_ratio and not oven_dry_fuel_load):
        sys.exit()

    slope_steepness = math.tan(slope)

    # - Equations
    net_fuel_load = oven_dry_fuel_load * (1 - tot_mineral_content)      # w_n
    oven_dry_bulk_density = oven_dry_fuel_load / fuel_bed_depth         # ρ_b
    if not packing_ratio:
        packing_ratio = oven_dry_bulk_density / oven_dry_particle_density            # β

    optimum_packing_ratio = 3.348 * (surface_area_vol_ratio ** -0.8189) # β_op
    maximum_reaction_vel = (surface_area_vol_ratio ** 1.5) * ((495 + 0.0594 * (surface_area_vol_ratio ** 1.5)) ** -1)

    mineral_damping_coeff = min(0.174 * (eff_mineral_content ** -0.19), 1)      # η_s
    r_M = min(moisture_fraction / dead_fuel_moisture_extinction, 1)
    moisture_damping_content = 1 - (2.59 * r_M) + 5.11 * (r_M ** 2) - 3.52 * (r_M ** 3)    # η_M

    propagating_flux_ratio = ((192 + 0.2595 * surface_area_vol_ratio) ** -1) * math.exp((0.792 + 0.681 * (surface_area_vol_ratio ** 0.5)) * (packing_ratio + 0.1))

    # wind factor
    E = 0.715 * math.exp(-3.59 * (10 ** -4) * surface_area_vol_ratio)
    B = 0.02526 * (surface_area_vol_ratio ** 0.54)
    C = 7.47 * math.exp(-0.133 * (surface_area_vol_ratio ** 0.55))
    wind_factor = C * (midflame_wind_speed ** B) * ((packing_ratio / optimum_packing_ratio) ** -E)

    eff_heating_num = math.exp(-138/surface_area_vol_ratio)
    heat_preignition = 250 + 1116 * moisture_fraction      # Q_ig
    slope_factor = 5.275 * (packing_ratio ** -0.3) * (slope_steepness ** 2)

    A = 133 * (surface_area_vol_ratio ** -0.7913)
    optimum_reaction_velocity = maximum_reaction_vel * ((packing_ratio / optimum_packing_ratio) ** A) * math.exp(A * (1 - packing_ratio / optimum_packing_ratio))
    reaction_intensity = optimum_reaction_velocity * net_fuel_load * heat_content * moisture_damping_content * mineral_damping_coeff

    rate = reaction_intensity * propagating_flux_ratio * (1 + wind_factor + slope_factor) / (oven_dry_bulk_density * eff_heating_num * heat_preignition)

    return rate

# consult pages 10-12 of fuel models guide for bed depth
if __name__ == '__main__':

    rate = basic_spread_rate(
        # oven_dry_fuel_load=1.7,
        oven_dry_fuel_load=0.0596878,
        surface_area_vol_ratio=1606,
        packing_ratio=0.00885,
        dead_fuel_moisture_extinction=0.2,
        fuel_bed_depth=0.6,
        slope=0,
        midflame_wind_speed=440,
        moisture_fraction=0.05
    )
    print(rate)