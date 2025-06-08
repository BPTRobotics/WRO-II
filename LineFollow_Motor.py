def get_direction(l, m, r):
    total = l + m + r
    if total == 0:
        return 0.0, 0.0  # No signal, no movement
    
    # Normalize the weights
    l_norm = l / total
    m_norm = m / total
    r_norm = r / total

    # Direction: weighted average (-1 for left, 0 for middle, 1 for right)
    direction = (-1 * l_norm) + (0 * m_norm) + (1 * r_norm)

    # Speed is based on total signal strength, normalized to [0,1]
    max_signal = max(l, m, r)
    speed = total / (3 * max_signal) if max_signal != 0 else 0.0

    return direction, speed
