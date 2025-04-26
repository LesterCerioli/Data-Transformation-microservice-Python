-- Cria a extensão pgcrypto para gen_random_uuid() (PostgreSQL 13+)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Tabela de registros médicos
CREATE TABLE medical_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL,
    organization_id UUID NOT NULL,
    record_data JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_anonymous BOOLEAN NOT NULL DEFAULT FALSE
);

-- Índices para melhorar consultas frequentes
CREATE INDEX idx_medical_records_patient_id ON medical_records (patient_id);
CREATE INDEX idx_medical_records_organization_id ON medical_records (organization_id);

-- Gatilho para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_medical_records_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_medical_records_updated_at
BEFORE UPDATE ON medical_records
FOR EACH ROW
EXECUTE FUNCTION update_medical_records_updated_at();