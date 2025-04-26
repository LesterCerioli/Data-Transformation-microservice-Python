-- Garantir que a extensão uuid-ossp está disponível
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criar a tabela organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(100) NOT NULL,
    cmj VARCHAR(18),
    cin VARCHAR(18),
    CONSTRAINT uni_organizations_cmj UNIQUE (cmj)
);

-- Criar índices adicionais
CREATE INDEX idx_organizations_deleted_at ON organizations (deleted_at);

-- Criar função de trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_organizations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Criar trigger para atualizar automaticamente updated_at
CREATE TRIGGER trigger_update_organizations_updated_at
BEFORE UPDATE ON organizations
FOR EACH ROW
EXECUTE FUNCTION update_organizations_updated_at();