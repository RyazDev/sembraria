-- ====================================================================
-- SEMBRARIA — 07 Audit Log (trazabilidad profesional)
-- Tabla append-only para registrar eventos sensibles: login, fincas
-- creadas, analisis lanzados, alertas marcadas, etc.
-- ====================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(64) NOT NULL,
    resource VARCHAR(64) NOT NULL,
    resource_id VARCHAR(64),
    ip_address INET,
    user_agent VARCHAR(500),
    request_id VARCHAR(64),
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indices para queries frecuentes
CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_log(resource);
CREATE INDEX IF NOT EXISTS idx_audit_resource_id ON audit_log(resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_request_id ON audit_log(request_id);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at DESC);

-- Indices compuestos
CREATE INDEX IF NOT EXISTS idx_audit_user_created ON audit_log(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_action_created ON audit_log(action, created_at DESC);

-- Comentarios
COMMENT ON TABLE audit_log IS 'Registro append-only de eventos sensibles para trazabilidad';
COMMENT ON COLUMN audit_log.action IS 'Verbo en pasado: login, create_farm, analyze, etc.';
COMMENT ON COLUMN audit_log.resource IS 'Tipo de recurso afectado: user, farm, analysis, etc.';
COMMENT ON COLUMN audit_log.details IS 'Metadata extra en formato JSON';

SELECT 'Audit log OK: ' || count(*) || ' registros existentes' AS status
FROM audit_log;
