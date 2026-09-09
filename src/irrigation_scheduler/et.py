"""Crop evapotranspiration (ETc) calculation module."""

def calculate_etc(eto: float, kc: float) -> float:
    """Calculate crop evapotranspiration (ETc) based on reference evapotranspiration (ETo) and crop coefficient (Kc).
    
    Args:
        eto (float): Reference evapotranspiration (ETo) in mm/day.
        kc (float): Crop coefficient (Kc), dimensionless.
    
    Returns:
        float: Crop evapotranspiration (ETc) in mm/day.
    """
    
    if eto < 0:
        raise ValueError("Reference evapotranspiration (ETo) must be greater than or equal to zero.")
    
    if kc < 0:
        raise ValueError("Crop coefficient (Kc) must be greater than or equal to zero.")
    
    etc = eto * kc
    return etc