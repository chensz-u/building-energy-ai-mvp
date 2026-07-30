from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row


class PostgresEnergyRepository:
    def __init__(self, database_url: str):
        self.database_url = database_url

    def load_rows(self) -> list[dict[str, Any]]:
        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT observed_at AS timestamp, building_id, energy_kwh, temperature_c,
                              hvac_energy_kwh, supply_temp_c, return_temp_c
                       FROM energy_readings ORDER BY observed_at"""
                )
                return list(cursor.fetchall())

