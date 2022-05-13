import numpy as np
from pyfoil.classes import LiftingSurface

def test_square_wing():

    square_wing = LiftingSurface(rt_chord=1, 
                                 tip_chord=1, 
                                 span=5,  
                                 afoil='tests/square', 
                                 nsegs=40,
                                 units='m')

    assert np.isclose(square_wing.afoil_area, 1.0, rtol=1e-03, atol=1e-03)
    assert np.isclose(square_wing.calc_AR(), 5.0, rtol=1e-03, atol=1e-03)
    assert np.isclose(square_wing.calc_proj_wing_area(), 5.0, rtol=1e-03, atol=1e-03)
    assert np.isclose(square_wing.calc_actual_wing_area(), 5.0, rtol=1e-03, atol=1e-03)
    assert np.isclose(square_wing.calc_wing_volume(), 5, rtol=1e-03, atol=1e-03)