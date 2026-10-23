"""Tính độ lệch thời gian đèn xanh cho hành lang ưu tiên một chiều."""


def travel_time_seconds(distance_m: float, speed_kmh: float) -> float:
    """Tính thời gian di chuyển L/V, với L (m) và V (km/h)."""
    if distance_m < 0:
        raise ValueError("Khoảng cách không thể âm")
    if speed_kmh <= 0:
        raise ValueError("Tốc độ phải lớn hơn 0")
    return distance_m / (speed_kmh / 3.6)


def corridor_offsets(spacing_m: list[float], speed_kmh: float, cycle_s: float) -> list[float]:
    """Offset mỗi nút so với nút đầu, lấy modulo chu kỳ.

    Chỉ là giá trị khởi tạo một chiều (bỏ qua tốc độ thay đổi, hàng chờ).
    """
    if cycle_s <= 0:
        raise ValueError("Chu kỳ phải lớn hơn 0")
    offsets = [0.0]
    cumulative = 0.0
    for distance in spacing_m:
        cumulative += travel_time_seconds(distance, speed_kmh)
        offsets.append(cumulative % cycle_s)
    return offsets
