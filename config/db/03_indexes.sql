-- ====================================================================
-- SEMBRARIA — 03 Indices adicionales (idempotente)
-- ====================================================================

-- Indices compuestos para queries frecuentes
CREATE INDEX IF NOT EXISTS idx_analyses_farm_cultivo ON analyses(farm_id, cultivo);
CREATE INDEX IF NOT EXISTS idx_farms_user_status ON farms(user_id, status);
CREATE INDEX IF NOT EXISTS idx_alerts_user_unread ON alerts(user_id, is_read, created_at DESC);

-- Vista materializada para estadísticas por municipio
DROP MATERIALIZED VIEW IF EXISTS mv_farm_stats_by_municipio CASCADE;
CREATE MATERIALIZED VIEW mv_farm_stats_by_municipio AS
SELECT
    municipio,
    COUNT(*) AS total_fincas,
    SUM(area_ha) AS area_total_ha,
    AVG(area_ha) AS area_promedio_ha
FROM farms
WHERE status = 'activa'
GROUP BY municipio;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_farm_stats_municipio ON mv_farm_stats_by_municipio(municipio);

SELECT 'Indices adicionales OK' AS status;
