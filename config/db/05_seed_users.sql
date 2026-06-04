-- ====================================================================
-- SEMBRIA — 05 Seed Users (usuarios demo)
-- Password por defecto: "sembraria2026" (bcrypt 12 rounds)
-- ====================================================================
-- Hash real generado con bcrypt directamente (passlib es incompatible
-- con bcrypt 5+). Para regenerar:
--   python -c "import bcrypt; print(bcrypt.hashpw(b'sembraria2026', bcrypt.gensalt(12)).decode())"

INSERT INTO users (id, email, phone, full_name, hashed_password, role, organization, is_active) VALUES
    (
        '11111111-1111-1111-1111-111111111111',
        'productor@sembraria.demo',
        '+573001234567',
        'Brayan Cuellar',
        '$2b$12$HNZsb40WZodQ2Cmv98RDbu3BshGOacPX7pHJ9gS31Jl3Z3iDmaaA2',
        'productor',
        'UDLA Raices',
        true
    ),
    (
        '22222222-2222-2222-2222-222222222222',
        'cooperativa@sembraria.demo',
        '+573007654321',
        'Cooperativa Multiactiva El Doncello',
        '$2b$12$HNZsb40WZodQ2Cmv98RDbu3BshGOacPX7pHJ9gS31Jl3Z3iDmaaA2',
        'cooperativa',
        'COOAGRO',
        true
    )
ON CONFLICT (email) DO UPDATE SET hashed_password = EXCLUDED.hashed_password;

-- Finca demo para el productor
-- El area_ha se calcula desde la geometria en lugar de hardcodearla, para
-- que cualquier ajuste al poligono mantenga la consistencia.
INSERT INTO farms (id, user_id, name, municipio, geom, area_ha, status, notes) VALUES
    (
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        '11111111-1111-1111-1111-111111111111',
        'Finca La Esperanza',
        'Florencia',
        ST_GeomFromText(
            'POLYGON((
                -75.62 1.61, -75.61 1.61, -75.61 1.62, -75.62 1.62, -75.62 1.61
            ))',
            4326
        ),
        (ST_Area(ST_GeomFromText('POLYGON((-75.62 1.61, -75.61 1.61, -75.61 1.62, -75.62 1.62, -75.62 1.61))', 4326)::geography)/10000.0)::numeric(10,2),
        'activa',
        'Finca demo de cacao'
    )
ON CONFLICT (id) DO NOTHING;

SELECT 'Seed users: ' || count(*) AS total FROM users;
SELECT 'Seed farms: ' || count(*) AS total FROM farms;
