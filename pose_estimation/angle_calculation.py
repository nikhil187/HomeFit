"""
Angle Calculation Module
Computes joint angles using geometric vector mathematics
"""

import math


def calculate_angle(point_a, point_b, point_c):
    """
    Calculate the angle at vertex point_b formed by three points.
    
    Uses vector dot product formula: θ = arccos((BA·BC) / (|BA|×|BC|))
    where BA = A - B and BC = C - B
    
    Args:
        point_a: First point [x, y]
        point_b: Vertex point [x, y] 
        point_c: Third point [x, y]
    
    Returns:
        Angle in degrees (0-180)
    """
    vector_ba = [point_a[0] - point_b[0], point_a[1] - point_b[1]]
    vector_bc = [point_c[0] - point_b[0], point_c[1] - point_b[1]]
    
    dot_product = vector_ba[0] * vector_bc[0] + vector_ba[1] * vector_bc[1]
    
    magnitude_ba = math.sqrt(vector_ba[0] ** 2 + vector_ba[1] ** 2)
    magnitude_bc = math.sqrt(vector_bc[0] ** 2 + vector_bc[1] ** 2)
    
    if magnitude_ba == 0 or magnitude_bc == 0:
        return 0.0
    
    cosine_angle = max(-1.0, min(1.0, dot_product / (magnitude_ba * magnitude_bc)))
    angle = math.degrees(math.acos(cosine_angle))
    
    return angle