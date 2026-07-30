CREATE TABLE IF NOT EXISTS energy_readings (
    observed_at TIMESTAMPTZ NOT NULL,
    building_id TEXT NOT NULL,
    energy_kwh NUMERIC(12, 2) NOT NULL CHECK (energy_kwh >= 0),
    temperature_c NUMERIC(5, 2) NOT NULL,
    hvac_energy_kwh NUMERIC(12, 2) NOT NULL CHECK (hvac_energy_kwh >= 0),
    supply_temp_c NUMERIC(5, 2) NOT NULL,
    return_temp_c NUMERIC(5, 2) NOT NULL,
    PRIMARY KEY (observed_at, building_id)
);

CREATE INDEX IF NOT EXISTS idx_energy_readings_building_time ON energy_readings (building_id, observed_at);

