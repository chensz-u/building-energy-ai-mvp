from __future__ import annotations

from collections import defaultdict
from math import sqrt
from statistics import mean, pstdev
from typing import Any, Iterable


class EnergyAnalysisTools:
    """Small deterministic analysis tools over normalized energy observations."""

    def __init__(self, rows: Iterable[dict[str, Any]]):
        self.rows = [dict(row) for row in rows]

    def energy_trend(self, building_id: str) -> dict[str, Any]:
        rows = self._for_building(building_id)
        buckets: dict[str, list[float]] = defaultdict(list)
        for row in rows:
            buckets[str(row["timestamp"])[:10]].append(float(row["energy_kwh"]))
        points = [
            {"date": date, "energy_kwh": round(sum(values), 2), "sample_count": len(values)}
            for date, values in sorted(buckets.items())
        ]
        return {
            "building_id": building_id,
            "points": points,
            "evidence": {"sample_count": len(rows), "total_energy_kwh": round(sum(float(row["energy_kwh"]) for row in rows), 2)},
        }

    def locate_anomalies(self, building_id: str) -> dict[str, Any]:
        rows = self._for_building(building_id)
        values = [float(row["energy_kwh"]) for row in rows]
        baseline = mean(values)
        spread = pstdev(values) if len(values) > 1 else 0.0
        threshold = baseline + max(1.0, 1.5 * spread)
        anomalies = [
            {"timestamp": row["timestamp"], "energy_kwh": float(row["energy_kwh"]), "threshold_kwh": round(threshold, 2)}
            for row in rows if float(row["energy_kwh"]) > threshold
        ]
        return {
            "building_id": building_id,
            "anomalies": anomalies,
            "evidence": {"sample_count": len(rows), "baseline_mean_kwh": round(baseline, 2), "threshold_kwh": round(threshold, 2)},
        }

    def weather_energy_correlation(self, building_id: str) -> dict[str, Any]:
        rows = self._for_building(building_id)
        temperatures = [float(row["temperature_c"]) for row in rows]
        energy = [float(row["energy_kwh"]) for row in rows]
        temperature_mean = mean(temperatures)
        energy_mean = mean(energy)
        numerator = sum((x - temperature_mean) * (y - energy_mean) for x, y in zip(temperatures, energy))
        denominator = sqrt(sum((x - temperature_mean) ** 2 for x in temperatures) * sum((y - energy_mean) ** 2 for y in energy))
        correlation = 0.0 if denominator == 0 else numerator / denominator
        return {
            "building_id": building_id,
            "pearson_correlation": round(correlation, 4),
            "evidence": {"sample_count": len(rows), "temperature_range_c": [min(temperatures), max(temperatures)], "energy_range_kwh": [min(energy), max(energy)]},
        }

    def _for_building(self, building_id: str) -> list[dict[str, Any]]:
        rows = [row for row in self.rows if row["building_id"] == building_id]
        if not rows:
            raise ValueError(f"No readings found for building_id={building_id}")
        return rows

