-- ====================================================================
-- SEMBRARIA — 01 Extensiones
-- Habilita PostGIS para soporte geoespacial
-- ====================================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- Para gen_random_uuid()

-- Verificar instalacion
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis') THEN
        RAISE EXCEPTION 'PostGIS no esta instalado. Ejecuta scripts\install-postgis.bat';
    END IF;
END $$;

SELECT 'PostGIS version: ' || PostGIS_Version() AS status;
