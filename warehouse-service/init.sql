-- Initialisation de la base de données PostgreSQL pour le warehouse
-- Ce script crée les tables nécessaires pour stocker les données historiques et d'audit

-- Création de la base de données (déjà créée via Docker)
-- CREATE DATABASE data_warehouse;

-- Connexion à la base de données
-- \c data_warehouse;

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Extension pour les fonctions de date/heure avancées
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ==================== TABLES DE MÉTADONNÉES ====================

-- Table des sources de données
CREATE TABLE IF NOT EXISTS data_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'database', 'api', 'file', 'stream'
    connection_config JSONB,
    status VARCHAR(20) DEFAULT 'active',
    last_sync TIMESTAMP,
    sync_frequency VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des schémas de données
CREATE TABLE IF NOT EXISTS data_schemas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES data_sources(id),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    schema_definition JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== TABLES DE DONNÉES BRUTES ====================

-- Table pour les données ingérées (staging)
CREATE TABLE IF NOT EXISTS raw_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES data_sources(id),
    schema_id UUID REFERENCES data_schemas(id),
    data JSONB NOT NULL,
    metadata JSONB,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT false,
    processing_timestamp TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_raw_data_source_id ON raw_data(source_id);
CREATE INDEX IF NOT EXISTS idx_raw_data_ingestion_timestamp ON raw_data(ingestion_timestamp);
CREATE INDEX IF NOT EXISTS idx_raw_data_processed ON raw_data(processed);
CREATE INDEX IF NOT EXISTS idx_raw_data_created_at ON raw_data(created_at);

-- ==================== TABLES DE DONNÉES TRANSFORMÉES ====================

-- Table pour les données transformées
CREATE TABLE IF NOT EXISTS transformed_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    raw_data_id UUID REFERENCES raw_data(id),
    transformation_type VARCHAR(100) NOT NULL,
    transformation_config JSONB,
    data JSONB NOT NULL,
    quality_score DECIMAL(5,2),
    transformation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les données transformées
CREATE INDEX IF NOT EXISTS idx_transformed_data_raw_data_id ON transformed_data(raw_data_id);
CREATE INDEX IF NOT EXISTS idx_transformed_data_transformation_type ON transformed_data(transformation_type);
CREATE INDEX IF NOT EXISTS idx_transformed_data_transformation_timestamp ON transformed_data(transformation_timestamp);

-- ==================== TABLES DE CONTRÔLE QUALITÉ ====================

-- Table pour les résultats de contrôle qualité
CREATE TABLE IF NOT EXISTS quality_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_id UUID NOT NULL, -- Peut référencer raw_data ou transformed_data
    data_type VARCHAR(20) NOT NULL, -- 'raw' ou 'transformed'
    check_type VARCHAR(100) NOT NULL,
    check_config JSONB,
    result JSONB NOT NULL,
    quality_score DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'completed', -- 'completed', 'failed', 'pending'
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les contrôles qualité
CREATE INDEX IF NOT EXISTS idx_quality_checks_data_id ON quality_checks(data_id);
CREATE INDEX IF NOT EXISTS idx_quality_checks_check_type ON quality_checks(check_type);
CREATE INDEX IF NOT EXISTS idx_quality_checks_executed_at ON quality_checks(executed_at);

-- ==================== TABLES DE RÉCONCILIATION ====================

-- Table pour les résultats de réconciliation
CREATE TABLE IF NOT EXISTS reconciliation_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_data_id UUID NOT NULL,
    target_data_id UUID NOT NULL,
    reconciliation_type VARCHAR(100) NOT NULL,
    reconciliation_config JSONB,
    matches JSONB,
    duplicates JSONB,
    merged_data JSONB,
    confidence_score DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'completed',
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour la réconciliation
CREATE INDEX IF NOT EXISTS idx_reconciliation_source_data_id ON reconciliation_results(source_data_id);
CREATE INDEX IF NOT EXISTS idx_reconciliation_target_data_id ON reconciliation_results(target_data_id);
CREATE INDEX IF NOT EXISTS idx_reconciliation_executed_at ON reconciliation_results(executed_at);

-- ==================== TABLES D'ANALYSE RCA ====================

-- Table pour les analyses RCA
CREATE TABLE IF NOT EXISTS rca_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_type VARCHAR(100) NOT NULL,
    problem_description TEXT NOT NULL,
    affected_metrics JSONB,
    analysis_config JSONB,
    root_causes JSONB,
    contributing_factors JSONB,
    recommendations JSONB,
    confidence_score DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'completed',
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les analyses RCA
CREATE INDEX IF NOT EXISTS idx_rca_analyses_analysis_type ON rca_analyses(analysis_type);
CREATE INDEX IF NOT EXISTS idx_rca_analyses_executed_at ON rca_analyses(executed_at);

-- ==================== TABLES DE MÉTRIQUES ET KPI ====================

-- Table pour les métriques système
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_unit VARCHAR(50),
    service_name VARCHAR(100),
    tags JSONB,
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les métriques système
CREATE INDEX IF NOT EXISTS idx_system_metrics_metric_name ON system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_metrics_service_name ON system_metrics(service_name);
CREATE INDEX IF NOT EXISTS idx_system_metrics_measured_at ON system_metrics(measured_at);

-- Table pour les KPI
CREATE TABLE IF NOT EXISTS kpi_values (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    kpi_name VARCHAR(100) NOT NULL,
    kpi_value DECIMAL(15,4) NOT NULL,
    kpi_unit VARCHAR(50),
    calculation_method VARCHAR(100),
    data_source VARCHAR(100),
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les KPI
CREATE INDEX IF NOT EXISTS idx_kpi_values_kpi_name ON kpi_values(kpi_name);
CREATE INDEX IF NOT EXISTS idx_kpi_values_period_start ON kpi_values(period_start);
CREATE INDEX IF NOT EXISTS idx_kpi_values_calculated_at ON kpi_values(calculated_at);

-- ==================== TABLES D'AUDIT ET LOGS ====================

-- Table d'audit pour les opérations
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(100),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les logs d'audit
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);

-- Table pour les logs applicatifs
CREATE TABLE IF NOT EXISTS application_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level VARCHAR(20) NOT NULL,
    service VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    context JSONB,
    trace_id VARCHAR(100),
    user_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les logs applicatifs
CREATE INDEX IF NOT EXISTS idx_application_logs_level ON application_logs(level);
CREATE INDEX IF NOT EXISTS idx_application_logs_service ON application_logs(service);
CREATE INDEX IF NOT EXISTS idx_application_logs_timestamp ON application_logs(timestamp);

-- ==================== TABLES D'ALERTES ====================

-- Table pour les règles d'alerte
CREATE TABLE IF NOT EXISTS alert_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    condition_expression TEXT NOT NULL,
    threshold_value DECIMAL(15,4),
    severity VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    is_enabled BOOLEAN DEFAULT true,
    service_name VARCHAR(100),
    metric_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour les alertes générées
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_id UUID REFERENCES alert_rules(id),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'resolved', 'acknowledged', 'suppressed'
    service_name VARCHAR(100),
    metric_name VARCHAR(100),
    current_value DECIMAL(15,4),
    threshold_value DECIMAL(15,4),
    metadata JSONB,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les alertes
CREATE INDEX IF NOT EXISTS idx_alerts_rule_id ON alerts(rule_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);

-- ==================== TABLES DE CONFIGURATION ====================

-- Table pour la configuration système
CREATE TABLE IF NOT EXISTS system_config (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    category VARCHAR(100),
    is_encrypted BOOLEAN DEFAULT false,
    updated_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour les utilisateurs (authentification basique)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user', -- 'admin', 'user', 'viewer', 'analyst'
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les utilisateurs
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ==================== VUES UTILES ====================

-- Vue pour les statistiques des données
CREATE OR REPLACE VIEW data_statistics AS
SELECT 
    ds.name as source_name,
    ds.type as source_type,
    COUNT(rd.id) as total_records,
    COUNT(CASE WHEN rd.processed = true THEN 1 END) as processed_records,
    COUNT(CASE WHEN rd.processed = false THEN 1 END) as pending_records,
    COUNT(CASE WHEN rd.error_message IS NOT NULL THEN 1 END) as error_records,
    MIN(rd.ingestion_timestamp) as first_ingestion,
    MAX(rd.ingestion_timestamp) as last_ingestion
FROM data_sources ds
LEFT JOIN raw_data rd ON ds.id = rd.source_id
GROUP BY ds.id, ds.name, ds.type;

-- Vue pour les métriques de qualité
CREATE OR REPLACE VIEW quality_metrics AS
SELECT 
    qc.check_type,
    AVG(qc.quality_score) as avg_quality_score,
    MIN(qc.quality_score) as min_quality_score,
    MAX(qc.quality_score) as max_quality_score,
    COUNT(*) as total_checks,
    COUNT(CASE WHEN qc.status = 'completed' THEN 1 END) as successful_checks,
    COUNT(CASE WHEN qc.status = 'failed' THEN 1 END) as failed_checks,
    DATE_TRUNC('day', qc.executed_at) as check_date
FROM quality_checks qc
GROUP BY qc.check_type, DATE_TRUNC('day', qc.executed_at);

-- ==================== FONCTIONS UTILITAIRES ====================

-- Fonction pour nettoyer les anciennes données
CREATE OR REPLACE FUNCTION cleanup_old_data(retention_days INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- Nettoyage des logs applicatifs anciens
    DELETE FROM application_logs 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 day' * retention_days;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Nettoyage des métriques anciennes
    DELETE FROM system_metrics 
    WHERE measured_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * retention_days;
    
    -- Nettoyage des alertes résolues anciennes
    DELETE FROM alerts 
    WHERE status = 'resolved' 
    AND resolved_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * retention_days;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour calculer les statistiques de qualité
CREATE OR REPLACE FUNCTION calculate_quality_stats()
RETURNS TABLE(
    check_type VARCHAR(100),
    avg_score DECIMAL(5,2),
    total_checks BIGINT,
    success_rate DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        qc.check_type,
        ROUND(AVG(qc.quality_score), 2) as avg_score,
        COUNT(*) as total_checks,
        ROUND(COUNT(CASE WHEN qc.status = 'completed' THEN 1 END) * 100.0 / COUNT(*), 2) as success_rate
    FROM quality_checks qc
    WHERE qc.executed_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
    GROUP BY qc.check_type
    ORDER BY avg_score DESC;
END;
$$ LANGUAGE plpgsql;

-- ==================== TRIGGERS ====================

-- Trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Application du trigger sur les tables qui ont updated_at
CREATE TRIGGER update_data_sources_updated_at 
    BEFORE UPDATE ON data_sources 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_schemas_updated_at 
    BEFORE UPDATE ON data_schemas 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alert_rules_updated_at 
    BEFORE UPDATE ON alert_rules 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== DONNÉES INITIALES ====================

-- Insertion des sources de données par défaut
INSERT INTO data_sources (name, type, connection_config, status) VALUES
('CRM System', 'api', '{"url": "https://crm.example.com/api", "auth_type": "bearer"}', 'active'),
('ERP System', 'database', '{"host": "erp-db.example.com", "port": 5432, "database": "erp"}', 'active'),
('Billing System', 'api', '{"url": "https://billing.example.com/api", "auth_type": "basic"}', 'active'),
('CDR Data', 'stream', '{"kafka_topic": "cdr-events", "bootstrap_servers": ["kafka:9092"]}', 'active'),
('OSS System', 'database', '{"host": "oss-db.example.com", "port": 3306, "database": "oss"}', 'active'),
('External Files', 'file', '{"path": "/data/external", "pattern": "*.csv"}', 'active')
ON CONFLICT DO NOTHING;

-- Insertion des règles d'alerte par défaut
INSERT INTO alert_rules (name, description, condition_expression, threshold_value, severity, service_name, metric_name) VALUES
('Data Quality Low', 'Alert when data quality score drops below threshold', 'quality_score < threshold', 90.0, 'warning', 'quality-control-service', 'data_quality_score'),
('Error Rate High', 'Alert when error rate exceeds threshold', 'error_rate > threshold', 5.0, 'critical', 'api-dashboard-service', 'error_rate'),
('Service Down', 'Alert when service is not responding', 'status != "healthy"', 0, 'critical', NULL, 'service_status'),
('Processing Delay', 'Alert when data processing is delayed', 'processing_delay > threshold', 300, 'warning', 'dbt-service', 'processing_delay')
ON CONFLICT DO NOTHING;

-- Insertion d'un utilisateur admin par défaut (mot de passe: admin123)
INSERT INTO users (username, email, password_hash, role, is_active) VALUES
('admin', 'admin@saas-platform.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeG4Vx5Q1vJ2K4YhO', 'admin', true)
ON CONFLICT (username) DO NOTHING;

-- ==================== COMMENTAIRES ====================

COMMENT ON TABLE data_sources IS 'Sources de données du système (API, base de données, fichiers, streams)';
COMMENT ON TABLE raw_data IS 'Données brutes ingérées depuis les sources';
COMMENT ON TABLE transformed_data IS 'Données transformées par les services de traitement';
COMMENT ON TABLE quality_checks IS 'Résultats des contrôles de qualité des données';
COMMENT ON TABLE reconciliation_results IS 'Résultats des opérations de réconciliation et déduplication';
COMMENT ON TABLE rca_analyses IS 'Analyses des causes racines des problèmes';
COMMENT ON TABLE system_metrics IS 'Métriques système et de performance';
COMMENT ON TABLE kpi_values IS 'Valeurs des indicateurs clés de performance';
COMMENT ON TABLE alerts IS 'Alertes générées par le système';
COMMENT ON TABLE audit_logs IS 'Logs d''audit des opérations utilisateur';
COMMENT ON TABLE application_logs IS 'Logs applicatifs des services';

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'Base de données warehouse initialisée avec succès!';
    RAISE NOTICE 'Tables créées: %', (
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
    );
END $$;
