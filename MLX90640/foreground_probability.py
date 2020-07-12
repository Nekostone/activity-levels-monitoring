import numpy as np

def residual_squares(est_background, mlx_measurement):
    return np.square(est_background - mlx_measurement)


def probability_from_residue(residual, steepness=1.5):  # probability that the measurement belongs to the background
    exp_term = np.exp(steepness*residual)
    denom = 1 + exp_term
    return 1 - 2/denom

def foreground_probability(cleaned_frame, original_frame, steepness=1.5):
    residue = residual_squares(cleaned_frame, original_frame)
    return probability_from_residue(residue, steepness)