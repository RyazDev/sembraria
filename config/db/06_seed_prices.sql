-- ====================================================================
-- SEMBRARIA — 06 Seed Precios de mercado (idempotente)
-- Datos mock basados en FEDECACAO y MinAgricultura 2026
-- ====================================================================
-- Si los precios ya existen (mismo producto + mismo precio + mismo
-- municipio + misma fecha), no se duplican. Para re-sembrar limpio,
-- ejecutar antes: TRUNCATE market_prices, alerts RESTART IDENTITY;

INSERT INTO market_prices (producto, precio_cop_kg, unidad, fuente, cambio_porcentual, municipio, recorded_at) VALUES
    -- Precios actuales (mock 2026)
    ('cacao',     12500.00, 'COP/kg',    'FEDECACAO',         8.20, 'Nacional',   now() - interval '0 day'),
    ('platano',    1800.00, 'COP/kg',    'MinAgricultura',    3.10, 'Nacional',   now() - interval '0 day'),
    ('yuca',       1200.00, 'COP/kg',    'MinAgricultura',   -1.20, 'Nacional',   now() - interval '0 day'),
    ('panela',     4500.00, 'COP/kg',    'FEDEPANELA',        5.40, 'Nacional',   now() - interval '0 day'),
    ('cafe',       9800.00, 'COP/kg',    'FNC',                2.80, 'Nacional',   now() - interval '0 day'),
    ('leche',      2800.00, 'COP/litro', 'MinAgricultura',    0.00, 'Nacional',   now() - interval '0 day'),
    ('maiz',       1600.00, 'COP/kg',    'FENALCE',            2.10, 'Nacional',   now() - interval '0 day'),
    ('caucho',     4500.00, 'COP/kg',    'MinAgricultura',    1.50, 'Nacional',   now() - interval '0 day'),
    -- Precios historicos (ultimos 7 dias)
    ('cacao',     12300.00, 'COP/kg',    'FEDECACAO',         0.00, 'Nacional',   now() - interval '1 day'),
    ('cacao',     12100.00, 'COP/kg',    'FEDECACAO',        -1.20, 'Nacional',   now() - interval '2 day'),
    ('cacao',     11800.00, 'COP/kg',    'FEDECACAO',         1.50, 'Nacional',   now() - interval '3 day'),
    ('platano',    1780.00, 'COP/kg',    'MinAgricultura',    0.50, 'Nacional',   now() - interval '1 day'),
    ('platano',    1750.00, 'COP/kg',    'MinAgricultura',   -0.30, 'Nacional',   now() - interval '2 day'),
    ('yuca',       1230.00, 'COP/kg',    'MinAgricultura',    0.80, 'Nacional',   now() - interval '1 day'),
    -- Alerta demo
    ('cacao',     13500.00, 'COP/kg',    'FEDECACAO',         8.00, 'Florencia',  now() - interval '0 day')
ON CONFLICT DO NOTHING;

-- Para que el ON CONFLICT funcione necesitamos un constraint unico:
-- (producto, precio_cop_kg, municipio, date(recorded_at)).
-- Lo creamos solo si no existe.
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_market_prices_seed'
    ) THEN
        ALTER TABLE market_prices
        ADD CONSTRAINT uq_market_prices_seed
        UNIQUE (producto, precio_cop_kg, municipio, recorded_at);
    END IF;
END $$;

SELECT 'Seed precios: ' || count(*) || ' registros' AS total FROM market_prices;

-- Alertas demo para el productor (idempotente: usa subselect para evitar duplicados)
INSERT INTO alerts (user_id, farm_id, type, severity, title, message, affected_hectares, is_read)
SELECT
    '11111111-1111-1111-1111-111111111111'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'estres_hidrico'::alert_type,
    'critica'::alert_severity,
    'Estres hidrico detectado',
    'Riegue en las proximas 48 horas. Lluvia prevista para jueves segun ERA5.',
    3.2,
    false
WHERE NOT EXISTS (
    SELECT 1 FROM alerts WHERE title = 'Estres hidrico detectado'
);

INSERT INTO alerts (user_id, farm_id, type, severity, title, message, affected_hectares, is_read)
SELECT
    '11111111-1111-1111-1111-111111111111'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'deforestacion'::alert_type,
    'alta'::alert_severity,
    'Cambio de uso de suelo cercano',
    '2.1 ha deforestadas a 800m de su finca. Puede afectar certificacion EUDR.',
    2.1,
    false
WHERE NOT EXISTS (
    SELECT 1 FROM alerts WHERE title = 'Cambio de uso de suelo cercano'
);

INSERT INTO alerts (user_id, farm_id, type, severity, title, message, affected_hectares, is_read)
SELECT
    '11111111-1111-1111-1111-111111111111'::uuid,
    NULL,
    'precio'::alert_type,
    'media'::alert_severity,
    'Precio del cacao subio 8%',
    'FEDECACAO: $12,500/kg. Buen momento para planificar cosecha.',
    NULL,
    true
WHERE NOT EXISTS (
    SELECT 1 FROM alerts WHERE title = 'Precio del cacao subio 8%'
);

SELECT 'Seed alertas: ' || count(*) || ' registros' AS total FROM alerts;
