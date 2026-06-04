-- =====================================================================
-- SembrarIA — Migracion 09: trazabilidad de version del modelo
-- en results.
--
-- Cada resultado de analisis registra la version del algoritmo que lo
-- produjo. Asi, si cambia la metodologia (zonal_extraction.py), podemos:
--   1. Reproducir resultados historicos
--   2. Detectar drift entre versiones
--   3. Documentar que 'este analisis fue generado con v1.0.0'
-- =====================================================================

ALTER TABLE results
    ADD COLUMN IF NOT EXISTS model_version VARCHAR(32) NULL;

ALTER TABLE results
    ADD COLUMN IF NOT EXISTS model_algorithm VARCHAR(64) NULL DEFAULT 'zonal_majority_v1';

ALTER TABLE results
    ADD COLUMN IF NOT EXISTS raster_inputs JSONB NULL;

ALTER TABLE results
    ADD COLUMN IF NOT EXISTS config_snapshot JSONB NULL;

-- Marcar resultados existentes con la version por defecto
UPDATE results
SET model_version = 'v1.0.0-legacy',
    model_algorithm = COALESCE(model_algorithm, 'zonal_majority_v1')
WHERE model_version IS NULL;

COMMENT ON COLUMN results.model_version IS 'Version del codigo que produjo este resultado (semver o similar)';
COMMENT ON COLUMN results.model_algorithm IS 'Nombre del algoritmo: zonal_majority_v1, etc.';
COMMENT ON COLUMN results.raster_inputs IS 'Snapshot de los rasters usados (nombre, version, hash)';
COMMENT ON COLUMN results.config_snapshot IS 'Snapshot de la config al momento del analisis';
