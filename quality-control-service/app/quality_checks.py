"""
Services de contrôle qualité et détection d'anomalies
"""

import pandas as pd
import numpy as np
import asyncio
import logging
import uuid
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.neighbors import LocalOutlierFactor
import psutil
import re

logger = logging.getLogger(__name__)

class QualityCheckService:
    """Service de contrôle qualité des données"""
    
    def __init__(self):
        self.quality_check_history = []
        self.start_time = datetime.now()
    
    async def perform_quality_check(
        self,
        data: List[Dict],
        quality_rules: List[Dict[str, Any]],
        data_source: str = "unknown",
        check_anomalies: bool = True,
        check_duplicates: bool = True,
        check_completeness: bool = True,
        check_consistency: bool = True,
        check_validity: bool = True
    ) -> Dict[str, Any]:
        """Effectue un contrôle qualité complet"""
        
        start_time = time.time()
        check_id = str(uuid.uuid4())
        
        try:
            df = pd.DataFrame(data)
            total_records = len(df)
            
            issues_found = []
            anomalies = []
            duplicates = []
            completeness_report = {}
            consistency_report = {}
            validity_report = {}
            recommendations = []
            
            # Vérification de complétude
            if check_completeness:
                completeness_report = await self.check_completeness(
                    data, self._extract_required_fields(quality_rules)
                )
                issues_found.extend(completeness_report.get("issues", []))
                recommendations.extend(completeness_report.get("recommendations", []))
            
            # Vérification de cohérence
            if check_consistency:
                consistency_report = await self.check_consistency(
                    data, quality_rules
                )
                issues_found.extend(consistency_report.get("issues", []))
                recommendations.extend(consistency_report.get("recommendations", []))
            
            # Vérification de validité
            if check_validity:
                validity_report = await self.check_validity(
                    data, quality_rules
                )
                issues_found.extend(validity_report.get("issues", []))
                recommendations.extend(validity_report.get("recommendations", []))
            
            # Détection de doublons
            if check_duplicates:
                duplicates = await self._find_duplicates(df, quality_rules)
                if duplicates:
                    issues_found.append({
                        "type": "duplicates",
                        "count": len(duplicates),
                        "severity": "medium"
                    })
                    recommendations.append("Supprimer ou fusionner les enregistrements dupliqués")
            
            # Détection d'anomalies
            if check_anomalies:
                anomalies = await self._detect_anomalies_simple(df, quality_rules)
                if anomalies:
                    issues_found.append({
                        "type": "anomalies",
                        "count": len(anomalies),
                        "severity": "high"
                    })
                    recommendations.append("Examiner les enregistrements anormaux")
            
            # Calcul du score de qualité global
            quality_score = await self._calculate_quality_score(
                total_records, issues_found, completeness_report, 
                consistency_report, validity_report
            )
            
            execution_time = time.time() - start_time
            
            # Enregistrement dans l'historique
            self.quality_check_history.append({
                "check_id": check_id,
                "data_source": data_source,
                "total_records": total_records,
                "quality_score": quality_score,
                "issues_count": len(issues_found),
                "execution_time": execution_time,
                "timestamp": datetime.now(),
                "status": "completed"
            })
            
            return {
                "check_id": check_id,
                "total_records": total_records,
                "quality_score": quality_score,
                "issues_found": issues_found,
                "anomalies": anomalies,
                "duplicates": duplicates,
                "completeness_report": completeness_report,
                "consistency_report": consistency_report,
                "validity_report": validity_report,
                "recommendations": list(set(recommendations)),
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du contrôle qualité {check_id}: {str(e)}")
            raise e
    
    async def check_completeness(
        self,
        data: List[Dict],
        required_fields: List[str]
    ) -> Dict[str, Any]:
        """Vérifie la complétude des données"""
        
        df = pd.DataFrame(data)
        completeness_issues = []
        field_completeness = {}
        
        for field in required_fields:
            if field in df.columns:
                null_count = df[field].isnull().sum()
                empty_count = (df[field] == "").sum()
                total_missing = null_count + empty_count
                completeness_rate = (len(df) - total_missing) / len(df) * 100
                
                field_completeness[field] = {
                    "completeness_rate": completeness_rate,
                    "missing_count": total_missing,
                    "null_count": null_count,
                    "empty_count": empty_count
                }
                
                if completeness_rate < 90:  # Seuil de 90%
                    completeness_issues.append({
                        "type": "incomplete_field",
                        "field": field,
                        "completeness_rate": completeness_rate,
                        "missing_count": total_missing,
                        "severity": "high" if completeness_rate < 70 else "medium"
                    })
        
        overall_completeness = np.mean([fc["completeness_rate"] for fc in field_completeness.values()]) if field_completeness else 100
        
        recommendations = []
        if overall_completeness < 95:
            recommendations.append("Améliorer la collecte de données pour les champs obligatoires")
        if any(fc["completeness_rate"] < 80 for fc in field_completeness.values()):
            recommendations.append("Mettre en place des validations côté source")
        
        return {
            "overall_completeness": overall_completeness,
            "field_completeness": field_completeness,
            "issues": completeness_issues,
            "recommendations": recommendations
        }
    
    async def check_consistency(
        self,
        data: List[Dict],
        rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Vérifie la cohérence des données"""
        
        df = pd.DataFrame(data)
        consistency_issues = []
        
        for rule in rules:
            if rule.get("type") == "cross_field_validation":
                field1 = rule.get("field1")
                field2 = rule.get("field2")
                condition = rule.get("condition")
                
                if field1 in df.columns and field2 in df.columns:
                    if condition == "field1_greater_than_field2":
                        violations = df[df[field1] <= df[field2]]
                        if len(violations) > 0:
                            consistency_issues.append({
                                "type": "cross_field_violation",
                                "rule": f"{field1} > {field2}",
                                "violations_count": len(violations),
                                "severity": "medium"
                            })
            
            elif rule.get("type") == "value_range":
                field = rule.get("field")
                min_value = rule.get("min_value")
                max_value = rule.get("max_value")
                
                if field in df.columns:
                    if min_value is not None:
                        below_min = df[df[field] < min_value]
                        if len(below_min) > 0:
                            consistency_issues.append({
                                "type": "value_below_minimum",
                                "field": field,
                                "violations_count": len(below_min),
                                "min_value": min_value,
                                "severity": "high"
                            })
                    
                    if max_value is not None:
                        above_max = df[df[field] > max_value]
                        if len(above_max) > 0:
                            consistency_issues.append({
                                "type": "value_above_maximum",
                                "field": field,
                                "violations_count": len(above_max),
                                "max_value": max_value,
                                "severity": "high"
                            })
        
        recommendations = []
        if consistency_issues:
            recommendations.append("Mettre en place des validations métier plus strictes")
            recommendations.append("Examiner les données sources pour comprendre les incohérences")
        
        return {
            "issues": consistency_issues,
            "recommendations": recommendations
        }
    
    async def check_validity(
        self,
        data: List[Dict],
        rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Vérifie la validité des données"""
        
        df = pd.DataFrame(data)
        validity_issues = []
        
        for rule in rules:
            if rule.get("type") == "email_validation":
                field = rule.get("field")
                if field in df.columns:
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    invalid_emails = df[~df[field].astype(str).str.match(email_pattern, na=False)]
                    if len(invalid_emails) > 0:
                        validity_issues.append({
                            "type": "invalid_email",
                            "field": field,
                            "invalid_count": len(invalid_emails),
                            "severity": "medium"
                        })
            
            elif rule.get("type") == "phone_validation":
                field = rule.get("field")
                if field in df.columns:
                    phone_pattern = r'^\+?[\d\s\-\(\)]{10,}$'
                    invalid_phones = df[~df[field].astype(str).str.match(phone_pattern, na=False)]
                    if len(invalid_phones) > 0:
                        validity_issues.append({
                            "type": "invalid_phone",
                            "field": field,
                            "invalid_count": len(invalid_phones),
                            "severity": "medium"
                        })
            
            elif rule.get("type") == "date_validation":
                field = rule.get("field")
                if field in df.columns:
                    try:
                        pd.to_datetime(df[field], errors='coerce')
                        invalid_dates = df[pd.to_datetime(df[field], errors='coerce').isna()]
                        if len(invalid_dates) > 0:
                            validity_issues.append({
                                "type": "invalid_date",
                                "field": field,
                                "invalid_count": len(invalid_dates),
                                "severity": "high"
                            })
                    except:
                        validity_issues.append({
                            "type": "date_parsing_error",
                            "field": field,
                            "severity": "high"
                        })
        
        recommendations = []
        if validity_issues:
            recommendations.append("Mettre en place des formats de données standardisés")
            recommendations.append("Ajouter des validations côté client")
        
        return {
            "issues": validity_issues,
            "recommendations": recommendations
        }
    
    async def validate_schema(
        self,
        data: List[Dict],
        expected_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valide le schéma des données"""
        
        if not data:
            return {"valid": True, "issues": []}
        
        actual_fields = set(data[0].keys())
        expected_fields = set(expected_schema.get("fields", {}).keys())
        
        issues = []
        
        # Champs manquants
        missing_fields = expected_fields - actual_fields
        if missing_fields:
            issues.append({
                "type": "missing_fields",
                "fields": list(missing_fields),
                "severity": "high"
            })
        
        # Champs supplémentaires
        extra_fields = actual_fields - expected_fields
        if extra_fields:
            issues.append({
                "type": "extra_fields",
                "fields": list(extra_fields),
                "severity": "low"
            })
        
        # Validation des types de données
        type_issues = []
        for field, expected_type in expected_schema.get("fields", {}).items():
            if field in actual_fields:
                sample_value = data[0].get(field)
                if sample_value is not None:
                    actual_type = type(sample_value).__name__
                    if actual_type != expected_type:
                        type_issues.append({
                            "field": field,
                            "expected_type": expected_type,
                            "actual_type": actual_type
                        })
        
        if type_issues:
            issues.append({
                "type": "type_mismatch",
                "details": type_issues,
                "severity": "medium"
            })
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "actual_fields": list(actual_fields),
            "expected_fields": list(expected_fields)
        }
    
    async def _find_duplicates(
        self,
        df: pd.DataFrame,
        rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Trouve les doublons dans les données"""
        
        duplicates = []
        duplicate_fields = []
        
        # Extraction des champs pour la détection de doublons
        for rule in rules:
            if rule.get("type") == "duplicate_detection":
                duplicate_fields = rule.get("fields", [])
                break
        
        if duplicate_fields:
            # Recherche de doublons exacts
            exact_duplicates = df[df.duplicated(subset=duplicate_fields, keep=False)]
            if len(exact_duplicates) > 0:
                duplicates.extend(exact_duplicates.to_dict('records'))
        
        return duplicates
    
    async def _detect_anomalies_simple(
        self,
        df: pd.DataFrame,
        rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Détection simple d'anomalies"""
        
        anomalies = []
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            # Détection des valeurs aberrantes avec IQR
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
            if len(outliers) > 0:
                anomalies.extend(outliers.to_dict('records'))
        
        return anomalies
    
    async def _calculate_quality_score(
        self,
        total_records: int,
        issues_found: List[Dict],
        completeness_report: Dict,
        consistency_report: Dict,
        validity_report: Dict
    ) -> float:
        """Calcule le score de qualité global"""
        
        base_score = 100.0
        
        # Pénalités selon le type et la gravité des problèmes
        for issue in issues_found:
            severity = issue.get("severity", "medium")
            if severity == "high":
                base_score -= 10
            elif severity == "medium":
                base_score -= 5
            else:
                base_score -= 2
        
        # Pénalité pour la complétude
        completeness = completeness_report.get("overall_completeness", 100)
        if completeness < 95:
            base_score -= (95 - completeness) * 0.5
        
        return max(0, base_score)
    
    async def _extract_required_fields(self, rules: List[Dict[str, Any]]) -> List[str]:
        """Extrait les champs requis des règles"""
        required_fields = []
        for rule in rules:
            if rule.get("type") == "required_field":
                required_fields.append(rule.get("field"))
        return required_fields
    
    async def generate_quality_report(
        self,
        data: List[Dict],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un rapport de qualité détaillé"""
        
        df = pd.DataFrame(data)
        
        report = {
            "summary": {
                "total_records": len(df),
                "total_fields": len(df.columns),
                "data_types": df.dtypes.to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum()
            },
            "field_statistics": {},
            "quality_metrics": {}
        }
        
        # Statistiques par champ
        for column in df.columns:
            report["field_statistics"][column] = {
                "null_count": df[column].isnull().sum(),
                "unique_count": df[column].nunique(),
                "data_type": str(df[column].dtype)
            }
            
            if df[column].dtype in ['int64', 'float64']:
                report["field_statistics"][column].update({
                    "min": df[column].min(),
                    "max": df[column].max(),
                    "mean": df[column].mean(),
                    "std": df[column].std()
                })
        
        return report
    
    async def get_quality_check_history(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Récupère l'historique des contrôles qualité"""
        return self.quality_check_history[offset:offset+limit]
    
    async def get_quality_check_by_id(self, check_id: str) -> Optional[Dict]:
        """Récupère un contrôle qualité par son ID"""
        for check in self.quality_check_history:
            if check["check_id"] == check_id:
                return check
        return None
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques du service"""
        total_checks = len(self.quality_check_history)
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "total_quality_checks": total_checks,
            "uptime_seconds": uptime,
            "memory_usage_mb": psutil.virtual_memory().used / 1024 / 1024,
            "cpu_usage_percent": psutil.cpu_percent(),
            "last_updated": datetime.now().isoformat()
        }

class AnomalyDetectionService:
    """Service de détection d'anomalies avancées"""
    
    def __init__(self):
        self.detection_history = []
    
    async def detect_anomalies(
        self,
        data: List[Dict],
        method: str = "isolation_forest",
        contamination: float = 0.1,
        features: List[str] = [],
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Détecte les anomalies avec différents algorithmes"""
        
        start_time = time.time()
        detection_id = str(uuid.uuid4())
        
        try:
            df = pd.DataFrame(data)
            total_records = len(df)
            
            # Préparation des features
            if not features:
                features = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not features:
                return {
                    "detection_id": detection_id,
                    "total_records": total_records,
                    "anomalies_detected": 0,
                    "anomaly_scores": [],
                    "anomalous_records": [],
                    "confidence_scores": [],
                    "execution_time": time.time() - start_time
                }
            
            # Normalisation des données
            scaler = StandardScaler()
            X = scaler.fit_transform(df[features].fillna(0))
            
            # Application de l'algorithme de détection
            if method == "isolation_forest":
                detector = IsolationForest(contamination=contamination, random_state=42)
                anomaly_scores = detector.fit_predict(X)
                anomaly_scores = -detector.score_samples(X)  # Scores d'anomalie
            elif method == "local_outlier_factor":
                detector = LocalOutlierFactor(contamination=contamination)
                anomaly_scores = detector.fit_predict(X)
                anomaly_scores = -detector.negative_outlier_factor_
            else:
                # Méthode par défaut: détection statistique
                anomaly_scores = self._statistical_anomaly_detection(df[features])
            
            # Identification des anomalies
            anomalous_indices = np.where(anomaly_scores > threshold)[0]
            anomalous_records = df.iloc[anomalous_indices].to_dict('records')
            
            # Calcul des scores de confiance
            confidence_scores = np.clip(anomaly_scores / np.max(anomaly_scores), 0, 1)
            
            execution_time = time.time() - start_time
            
            # Enregistrement dans l'historique
            self.detection_history.append({
                "detection_id": detection_id,
                "method": method,
                "total_records": total_records,
                "anomalies_detected": len(anomalous_records),
                "execution_time": execution_time,
                "timestamp": datetime.now()
            })
            
            return {
                "detection_id": detection_id,
                "total_records": total_records,
                "anomalies_detected": len(anomalous_records),
                "anomaly_scores": anomaly_scores.tolist(),
                "anomalous_records": anomalous_records,
                "confidence_scores": confidence_scores.tolist(),
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection d'anomalies {detection_id}: {str(e)}")
            raise e
    
    def _statistical_anomaly_detection(self, df: pd.DataFrame) -> np.ndarray:
        """Détection d'anomalies basée sur les statistiques"""
        scores = np.zeros(len(df))
        
        for column in df.columns:
            if df[column].dtype in ['int64', 'float64']:
                # Score basé sur l'écart par rapport à la moyenne
                mean = df[column].mean()
                std = df[column].std()
                if std > 0:
                    column_scores = np.abs(df[column] - mean) / std
                    scores += column_scores
        
        return scores / len(df.columns) if len(df.columns) > 0 else scores
