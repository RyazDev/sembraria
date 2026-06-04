-- ====================================================================
-- SEMBRARIA — 04 Poligono del departamento de Caqueta (idempotente)
--
-- IMPORTANTE - Trazabilidad:
--   La geometria incluida aqui es una APROXIMACION rectangular del
--   departamento (bounding box oficial). Para un despliegue en
--   produccion, ejecutar scripts/data/fetch_caqueta_boundary.py
--   que descarga el GeoJSON oficial del DANE.
--
--   El bbox aproximado cubre:
--     Longitud: -76.3 a -73.6  (Oeste a Este)
--     Latitud:  -0.7 a  2.3    (Sur a Norte)
-- ====================================================================

DROP TABLE IF EXISTS caqueta_boundary CASCADE;

CREATE TABLE caqueta_boundary (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    data_provenance VARCHAR(50) NOT NULL DEFAULT 'approximate',
    source_url TEXT NULL,
    fetched_at TIMESTAMPTZ NULL,
    notes TEXT NULL
);

-- Poligono simplificado del departamento de Caqueta
-- (Cobertura aproximada: -76.3 a -73.6 lon, -0.7 a 2.3 lat)
-- NOTA: este poligono rectangular es MOCK. Para un poligono real,
-- ejecutar scripts/data/fetch_caqueta_boundary.py
INSERT INTO caqueta_boundary (nombre, geom, data_provenance, source_url, notes) VALUES (
    'Caqueta',
    ST_GeomFromText(
        'MULTIPOLYGON((
            (-76.3 -0.7, -73.6 -0.7, -73.6 2.3, -76.3 2.3, -76.3 -0.7)
        ))',
        4326
    ),
    'approximate',
    NULL,
    'Poligono rectangular de fallback (bounding box oficial). Reemplazar con GeoJSON DANE ejecutando scripts/data/fetch_caqueta_boundary.py'
);

CREATE INDEX IF NOT EXISTS idx_caqueta_geom ON caqueta_boundary USING GIST(geom);

-- Funcion helper para validar si un punto o poligono esta dentro de Caqueta
CREATE OR REPLACE FUNCTION is_within_caqueta(geom_geom GEOMETRY)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN ST_Within(
        geom_geom::geometry,
        (SELECT geom FROM caqueta_boundary LIMIT 1)
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION is_within_caqueta IS 'Verifica si la geometria esta dentro del departamento de Caqueta (aproximacion rectangular)';

COMMENT ON COLUMN caqueta_boundary.data_provenance IS
    'approximate = bbox oficial; dane = poligono real descargado del DANE; manual = poligono custom';
COMMENT ON COLUMN caqueta_boundary.source_url IS
    'URL de la fuente original del poligono (DANE, IGAC, etc.)';

SELECT 'Caqueta boundary OK: ' || ST_AsText(ST_Centroid(geom)) AS status
FROM caqueta_boundary
LIMIT 1;
