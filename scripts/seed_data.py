import csv
import os
from pathlib import Path

import psycopg


database_url = os.environ["DATABASE_URL"]
csv_path = Path(__file__).parents[1] / "data" / "energy_readings_sample.csv"

with psycopg.connect(database_url) as connection, connection.cursor() as cursor:
    with csv_path.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            cursor.execute(
                """INSERT INTO energy_readings (observed_at, building_id, energy_kwh, temperature_c, hvac_energy_kwh, supply_temp_c, return_temp_c)
                   VALUES (%(observed_at)s, %(building_id)s, %(energy_kwh)s, %(temperature_c)s, %(hvac_energy_kwh)s, %(supply_temp_c)s, %(return_temp_c)s)
                   ON CONFLICT (observed_at, building_id) DO UPDATE SET energy_kwh = EXCLUDED.energy_kwh,
                       temperature_c = EXCLUDED.temperature_c, hvac_energy_kwh = EXCLUDED.hvac_energy_kwh,
                       supply_temp_c = EXCLUDED.supply_temp_c, return_temp_c = EXCLUDED.return_temp_c""",
                row,
            )
    connection.commit()

