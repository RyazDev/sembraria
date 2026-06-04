-- ====================================================================
-- SEMBRARIA — 02 Schema principal (idempotente)
-- Tablas: users, farms, analyses, results, alerts, market_prices
-- ====================================================================
-- Este script es idempotente: usa CREATE TABLE IF NOT EXISTS, y para los
-- tipos ENUM (que no tienen IF NOT EXISTS hasta PG 17) usa un patron
-- DROP + CREATE dentro de un DO block.

-- === Tipos ENUM (idempotente) ===
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('productor', 'cooperativa', 'extensionista', 'gobierno');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE farm_status AS ENUM ('activa', 'en_analisis', 'inactiva');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE analysis_status AS ENUM ('pending', 'processing', 'completed', 'failed');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE alert_type AS ENUM ('estres_hidrico', 'deforestacion', 'precio', 'clima', 'normal');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE alert_severity AS ENUM ('critica', 'alta', 'media', 'baja');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- === Tabla de usuarios ===
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'productor',
    organization VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    sms_notifications BOOLEAN NOT NULL DEFAULT false,
    email_notifications BOOLEAN NOT NULL DEFAULT true,
    whatsapp_notifications BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- === Tabla de fincas ===
CREATE TABLE IF NOT EXISTS farms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    municipio VARCHAR(100) NOT NULL,
    geom GEOMETRY(POLYGON, 4326) NOT NULL,
    area_ha NUMERIC(10, 2) NOT NULL,
    status farm_status NOT NULL DEFAULT 'activa',
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_area_positive CHECK (area_ha > 0)
);

CREATE INDEX IF NOT EXISTS idx_farms_user_id ON farms(user_id);
CREATE INDEX IF NOT EXISTS idx_farms_municipio ON farms(municipio);
CREATE INDEX IF NOT EXISTS idx_farms_geom ON farms USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_farms_status ON farms(status);

-- === Tabla de analisis ===
CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    cultivo VARCHAR(50) NOT NULL,
    status analysis_status NOT NULL DEFAULT 'pending',
    hectares_aptas NUMERIC(10, 2),
    hectares_totales NUMERIC(10, 2),
    porcentaje_apto NUMERIC(5, 2),
    criterios JSONB,
    execution_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_analyses_farm_id ON analyses(farm_id);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_cultivo ON analyses(cultivo);
CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);

-- === Tabla de resultados ===
CREATE TABLE IF NOT EXISTS results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID UNIQUE NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    png_path VARCHAR(500),
    pdf_path VARCHAR(500),
    geojson_path VARCHAR(500),
    png_url VARCHAR(500),
    summary JSONB,
    criteria JSONB,
    slope_breakdown JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_results_analysis_id ON results(analysis_id);

-- === Tabla de alertas ===
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farm_id UUID REFERENCES farms(id) ON DELETE CASCADE,
    type alert_type NOT NULL,
    severity alert_severity NOT NULL DEFAULT 'media',
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    affected_hectares NUMERIC(10, 2),
    is_read BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    read_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_farm_id ON alerts(farm_id);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(type);
CREATE INDEX IF NOT EXISTS idx_alerts_is_read ON alerts(is_read);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);

-- === Tabla de precios de mercado ===
CREATE TABLE IF NOT EXISTS market_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    producto VARCHAR(50) NOT NULL,
    precio_cop_kg NUMERIC(12, 2) NOT NULL,
    unidad VARCHAR(20) NOT NULL DEFAULT 'COP/kg',
    fuente VARCHAR(100) NOT NULL,
    cambio_porcentual NUMERIC(5, 2),
    municipio VARCHAR(100),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_market_prices_producto ON market_prices(producto);
CREATE INDEX IF NOT EXISTS idx_market_prices_recorded_at ON market_prices(recorded_at DESC);

-- === Tabla de tokens invalidados (para logout) ===
CREATE TABLE IF NOT EXISTS revoked_tokens (
    jti VARCHAR(255) PRIMARY KEY,
    revoked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- === Trigger para updated_at (idempotente con CREATE OR REPLACE) ===
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_users_updated_at ON users;
CREATE TRIGGER set_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

DROP TRIGGER IF EXISTS set_farms_updated_at ON farms;
CREATE TRIGGER set_farms_updated_at BEFORE UPDATE ON farms
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

SELECT 'Schema OK: ' || count(*) || ' tablas' AS status
FROM information_schema.tables
WHERE table_schema = 'public';
