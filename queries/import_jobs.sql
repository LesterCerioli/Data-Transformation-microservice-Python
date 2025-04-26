-- Cria o tipo ENUM para status de importação
CREATE TYPE import_status AS ENUM (
    'PENDING',
    'PROCESSING',
    'COMPLETED',
    'FAILED',
    'CANCELLED'
);

-- Tabela de jobs de importação
CREATE TABLE import_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_org_id UUID NOT NULL,
    destination_org_id UUID NOT NULL,
    status import_status NOT NULL DEFAULT 'PENDING',
    parameters JSONB NOT NULL,
    created_by UUID NOT NULL,
    callback_url TEXT,
    records_processed INTEGER DEFAULT 0,
    total_records INTEGER,
    message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_audited BOOLEAN NOT NULL DEFAULT FALSE
);

-- Índices para melhorar consultas frequentes
CREATE INDEX idx_import_jobs_source_org ON import_jobs (source_org_id);
CREATE INDEX idx_import_jobs_destination_org ON import_jobs (destination_org_id);
CREATE INDEX idx_import_jobs_status ON import_jobs (status);

-- Gatilho para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_import_jobs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_import_jobs_updated_at
BEFORE UPDATE ON import_jobs
FOR EACH ROW
EXECUTE FUNCTION update_import_jobs_updated_at();