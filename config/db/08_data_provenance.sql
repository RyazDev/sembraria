-- =====================================================================
-- SembrarIA — Migracion 08: trazabilidad de datos sinteticos en
-- market_prices y alerts.
--
-- Cualquier registro pre-existente se considera sintetico (datos del
-- seed/scripts). Cuando se conecten fuentes reales (FEDECACAO, FNC,
-- MinAgricultura via API/Scraping) los nuevos registros deberan
-- insertarse con is_synthetic=false.
-- =====================================================================

ALTER TABLE market_prices
    ADD COLUMN IF NOT EXISTS is_synthetic BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE market_prices
    ADD COLUMN IF NOT EXISTS source_url TEXT NULL;

ALTER TABLE market_prices
    ADD COLUMN IF NOT EXISTS fetched_at TIMESTAMPTZ NULL;

-- Marcar todas las filas existentes como sinteticas (el seed las creo).
-- Las nuevas inserciones deberan pasar is_synthetic=false explicitamente
-- si vienen de una fuente real.
UPDATE market_prices
SET is_synthetic = TRUE
WHERE is_synthetic IS DISTINCT FROM TRUE;

-- Indice para filtrar rapido por origen
CREATE INDEX IF NOT EXISTS idx_market_prices_synthetic
    ON market_prices (is_synthetic, recorded_at DESC);

-- Comentario en la columna para que sea visible en psql \d
COMMENT ON COLUMN market_prices.is_synthetic IS
    'TRUE = dato generado internamente (seed/script). FALSE = dato scrapeado de fuente real.';
COMMENT ON COLUMN market_prices.source_url IS
    'URL de la fuente real si is_synthetic=FALSE. NULL para datos sinteticos.';

-- Hacer lo mismo para alerts (los 3 alerts de seed son sinteticos)
ALTER TABLE alerts
    ADD COLUMN IF NOT EXISTS is_synthetic BOOLEAN NOT NULL DEFAULT TRUE;

UPDATE alerts
SET is_synthetic = TRUE
WHERE is_synthetic IS DISTINCT FROM TRUE;

COMMENT ON COLUMN alerts.is_synthetic IS
    'TRUE = alerta generada por el seed/reglas internas. FALSE = alerta de proveedor externo (IDEAM, etc).';
