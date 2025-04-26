-- 1. Primeiro crie o tipo ENUM se ele não existir
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'transfer_status') THEN
        CREATE TYPE transfer_status AS ENUM (
            'PENDING',
            'PROCESSING',
            'COMPLETED',
            'FAILED'
        );
    END IF;
END$$;

-- 2. Crie a extensão pgcrypto para gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 3. Crie a tabela transfer_logs (versão corrigida)
CREATE TABLE transfer_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_id UUID NOT NULL,
    source_org_id UUID NOT NULL,
    destination_org_id UUID NOT NULL,
    status transfer_status NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_details JSONB,
    audit_log JSONB
);

-- Adicione o comentário separadamente (sintaxe correta para PostgreSQL)
COMMENT ON TABLE transfer_logs IS 'Audit log for medical record transfers between organizations';

-- 4. Crie os índices
CREATE INDEX idx_transfer_logs_record_id ON transfer_logs (record_id);
CREATE INDEX idx_transfer_logs_source_org ON transfer_logs (source_org_id);
CREATE INDEX idx_transfer_logs_destination_org ON transfer_logs (destination_org_id);
CREATE INDEX idx_transfer_logs_status ON transfer_logs (status);

-- 5. Crie a função do trigger (corrigida)
CREATE OR REPLACE FUNCTION update_transfer_logs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 6. Crie o trigger
CREATE TRIGGER trigger_update_transfer_logs_updated_at
BEFORE UPDATE ON transfer_logs
FOR EACH ROW
EXECUTE FUNCTION update_transfer_logs_updated_at();