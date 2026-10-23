"""Các phép tính tổng hợp cơ bản; chưa phải bộ đọc output SUMO."""


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("Không thể lấy trung bình danh sách rỗng")
    return sum(values) / len(values)


def reduction_percent(baseline: float, greenwave: float) -> float:
    """Tỷ lệ giảm so với baseline; số âm nghĩa là greenwave kém hơn."""
    if baseline <= 0:
        raise ValueError("Giá trị baseline phải dương")
    return 100 * (baseline - greenwave) / baseline
