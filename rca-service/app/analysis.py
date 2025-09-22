"""
Services d'analyse RCA et de corrélation
"""

import pandas as pd
import numpy as np
import asyncio
import logging
import uuid
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import psutil
import json

logger = logging.getLogger(__name__)

class RCAAnalysisService:
    """Service d'analyse des causes racines"""
    
    def __init__(self):
        self.analysis_history = []
        self.start_time = datetime.now()
    
    async def perform_rca_analysis(
        self,
        data: List[Dict],
        problem_description: str,
        affected_metrics: List[str],
        time_window: Optional[Dict[str, Any]] = None,
        analysis_depth: int = 3,
        include_correlations: bool = True,
        include_trend_analysis: bool = True,
        include_anomaly_detection: bool = True
    ) -> Dict[str, Any]:
        """Effectue une analyse des causes racines complète"""
        
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        try:
            df = pd.DataFrame(data)
            
            # Résumé du problème
            problem_summary = await self._generate_problem_summary(
                problem_description, affected_metrics, df
            )
            
            # Analyse des causes racines
            root_causes = await self._identify_root_causes(
                df, affected_metrics, analysis_depth
            )
            
            # Facteurs contributifs
            contributing_factors = await self._identify_contributing_factors(
                df, affected_metrics
            )
            
            # Analyses supplémentaires
            correlation_analysis = None
            if include_correlations:
                correlation_analysis = await self._analyze_correlations(
                    df, affected_metrics
                )
            
            trend_analysis = None
            if include_trend_analysis and time_window:
                trend_analysis = await self._analyze_trends(
                    df, time_window, affected_metrics
                )
            
            anomaly_analysis = None
            if include_anomaly_detection:
                anomaly_analysis = await self._detect_anomalies(
                    df, affected_metrics
                )
            
            # Recommandations
            recommendations = await self._generate_recommendations(
                root_causes, contributing_factors, correlation_analysis
            )
            
            # Score de confiance
            confidence_score = await self._calculate_confidence_score(
                root_causes, contributing_factors, correlation_analysis
            )
            
            execution_time = time.time() - start_time
            
            # Enregistrement dans l'historique
            self.analysis_history.append({
                "analysis_id": analysis_id,
                "problem_description": problem_description,
                "affected_metrics": affected_metrics,
                "root_causes_count": len(root_causes),
                "confidence_score": confidence_score,
                "execution_time": execution_time,
                "timestamp": datetime.now(),
                "status": "completed"
            })
            
            return {
                "analysis_id": analysis_id,
                "problem_summary": problem_summary,
                "root_causes": root_causes,
                "contributing_factors": contributing_factors,
                "correlation_analysis": correlation_analysis,
                "trend_analysis": trend_analysis,
                "anomaly_analysis": anomaly_analysis,
                "recommendations": recommendations,
                "confidence_score": confidence_score,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse RCA {analysis_id}: {str(e)}")
            raise e
    
    async def _generate_problem_summary(
        self,
        problem_description: str,
        affected_metrics: List[str],
        df: pd.DataFrame
    ) -> str:
        """Génère un résumé du problème"""
        
        summary = f"Problème identifié: {problem_description}\n"
        summary += f"Métriques affectées: {', '.join(affected_metrics)}\n"
        summary += f"Données analysées: {len(df)} enregistrements\n"
        
        # Statistiques des métriques affectées
        for metric in affected_metrics:
            if metric in df.columns:
                if df[metric].dtype in ['int64', 'float64']:
                    summary += f"- {metric}: moyenne={df[metric].mean():.2f}, écart-type={df[metric].std():.2f}\n"
        
        return summary
    
    async def _identify_root_causes(
        self,
        df: pd.DataFrame,
        affected_metrics: List[str],
        analysis_depth: int
    ) -> List[Dict[str, Any]]:
        """Identifie les causes racines potentielles"""
        
        root_causes = []
        
        # Analyse de variance pour les métriques numériques
        for metric in affected_metrics:
            if metric in df.columns and df[metric].dtype in ['int64', 'float64']:
                # Calcul de l'écart par rapport à la moyenne
                mean_val = df[metric].mean()
                std_val = df[metric].std()
                
                # Identification des valeurs aberrantes
                outliers = df[np.abs(df[metric] - mean_val) > 2 * std_val]
                
                if len(outliers) > 0:
                    root_causes.append({
                        "type": "statistical_anomaly",
                        "metric": metric,
                        "description": f"Valeurs aberrantes détectées dans {metric}",
                        "severity": "high" if len(outliers) > len(df) * 0.1 else "medium",
                        "evidence": {
                            "outlier_count": len(outliers),
                            "outlier_percentage": len(outliers) / len(df) * 100,
                            "mean_deviation": np.mean(np.abs(outliers[metric] - mean_val))
                        },
                        "confidence": 0.8
                    })
        
        # Analyse des corrélations entre métriques
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 1:
            correlation_matrix = df[numeric_columns].corr()
            
            for metric in affected_metrics:
                if metric in correlation_matrix.columns:
                    # Recherche de corrélations fortes
                    strong_correlations = correlation_matrix[metric].abs().sort_values(ascending=False)
                    strong_correlations = strong_correlations[strong_correlations > 0.7]
                    strong_correlations = strong_correlations[strong_correlations.index != metric]
                    
                    if len(strong_correlations) > 0:
                        for correlated_metric, correlation_value in strong_correlations.items():
                            root_causes.append({
                                "type": "correlation_issue",
                                "metric": metric,
                                "description": f"Corrélation forte avec {correlated_metric}",
                                "severity": "medium",
                                "evidence": {
                                    "correlated_metric": correlated_metric,
                                    "correlation_value": correlation_value,
                                    "correlation_strength": "strong" if correlation_value > 0.8 else "moderate"
                                },
                                "confidence": correlation_value
                            })
        
        # Analyse des patterns temporels si une colonne de date est présente
        date_columns = df.select_dtypes(include=['datetime64']).columns
        if len(date_columns) > 0 and len(affected_metrics) > 0:
            time_patterns = await self._analyze_time_patterns(df, date_columns[0], affected_metrics)
            root_causes.extend(time_patterns)
        
        return root_causes[:analysis_depth]  # Limiter au nombre demandé
    
    async def _identify_contributing_factors(
        self,
        df: pd.DataFrame,
        affected_metrics: List[str]
    ) -> List[Dict[str, Any]]:
        """Identifie les facteurs contributifs"""
        
        contributing_factors = []
        
        # Analyse des valeurs manquantes
        missing_data_analysis = df.isnull().sum()
        high_missing_fields = missing_data_analysis[missing_data_analysis > len(df) * 0.1]
        
        for field, missing_count in high_missing_fields.items():
            contributing_factors.append({
                "type": "data_quality",
                "factor": f"Données manquantes dans {field}",
                "impact": "medium",
                "evidence": {
                    "missing_count": missing_count,
                    "missing_percentage": missing_count / len(df) * 100
                },
                "recommendation": "Améliorer la collecte de données pour ce champ"
            })
        
        # Analyse de la variance des métriques
        for metric in affected_metrics:
            if metric in df.columns and df[metric].dtype in ['int64', 'float64']:
                variance = df[metric].var()
                coefficient_of_variation = np.sqrt(variance) / df[metric].mean() if df[metric].mean() != 0 else 0
                
                if coefficient_of_variation > 1.0:  # Haute variabilité
                    contributing_factors.append({
                        "type": "high_variability",
                        "factor": f"Haute variabilité dans {metric}",
                        "impact": "medium",
                        "evidence": {
                            "coefficient_of_variation": coefficient_of_variation,
                            "variance": variance
                        },
                        "recommendation": "Investiguer les sources de variabilité"
                    })
        
        return contributing_factors
    
    async def _analyze_correlations(
        self,
        df: pd.DataFrame,
        affected_metrics: List[str]
    ) -> Dict[str, Any]:
        """Analyse les corrélations entre variables"""
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) < 2:
            return {"message": "Pas assez de colonnes numériques pour l'analyse de corrélation"}
        
        correlation_matrix = df[numeric_columns].corr()
        
        # Identification des corrélations significatives
        significant_correlations = []
        for i, col1 in enumerate(correlation_matrix.columns):
            for j, col2 in enumerate(correlation_matrix.columns):
                if i < j:  # Éviter les doublons
                    corr_value = correlation_matrix.loc[col1, col2]
                    if abs(corr_value) > 0.5:  # Corrélation modérée à forte
                        significant_correlations.append({
                            "variable1": col1,
                            "variable2": col2,
                            "correlation": corr_value,
                            "strength": "strong" if abs(corr_value) > 0.8 else "moderate"
                        })
        
        return {
            "correlation_matrix": correlation_matrix.to_dict(),
            "significant_correlations": significant_correlations,
            "summary": f"{len(significant_correlations)} corrélations significatives trouvées"
        }
    
    async def _analyze_trends(
        self,
        df: pd.DataFrame,
        time_window: Dict[str, Any],
        affected_metrics: List[str]
    ) -> Dict[str, Any]:
        """Analyse les tendances temporelles"""
        
        # Pour la démo, on simule une analyse de tendance
        trends = []
        
        for metric in affected_metrics:
            if metric in df.columns and df[metric].dtype in ['int64', 'float64']:
                # Simulation d'une tendance
                trend_direction = "increasing" if np.random.random() > 0.5 else "decreasing"
                trend_strength = np.random.uniform(0.1, 0.9)
                
                trends.append({
                    "metric": metric,
                    "trend_direction": trend_direction,
                    "trend_strength": trend_strength,
                    "significance": "high" if trend_strength > 0.7 else "medium"
                })
        
        return {
            "trends": trends,
            "time_window": time_window,
            "summary": f"Analyse des tendances pour {len(affected_metrics)} métriques"
        }
    
    async def _detect_anomalies(
        self,
        df: pd.DataFrame,
        affected_metrics: List[str]
    ) -> Dict[str, Any]:
        """Détecte les anomalies dans les données"""
        
        anomalies = []
        
        for metric in affected_metrics:
            if metric in df.columns and df[metric].dtype in ['int64', 'float64']:
                # Détection statistique d'anomalies
                Q1 = df[metric].quantile(0.25)
                Q3 = df[metric].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[metric] < lower_bound) | (df[metric] > upper_bound)]
                
                if len(outliers) > 0:
                    anomalies.append({
                        "metric": metric,
                        "anomaly_count": len(outliers),
                        "anomaly_percentage": len(outliers) / len(df) * 100,
                        "bounds": {
                            "lower": lower_bound,
                            "upper": upper_bound
                        }
                    })
        
        return {
            "anomalies": anomalies,
            "total_anomalies": sum(a["anomaly_count"] for a in anomalies),
            "summary": f"{len(anomalies)} métriques avec anomalies détectées"
        }
    
    async def _generate_recommendations(
        self,
        root_causes: List[Dict[str, Any]],
        contributing_factors: List[Dict[str, Any]],
        correlation_analysis: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Génère des recommandations basées sur l'analyse"""
        
        recommendations = []
        
        # Recommandations basées sur les causes racines
        for cause in root_causes:
            if cause["type"] == "statistical_anomaly":
                recommendations.append(
                    f"Investiguer les valeurs aberrantes dans {cause['metric']} - "
                    f"{cause['evidence']['outlier_count']} anomalies détectées"
                )
            elif cause["type"] == "correlation_issue":
                recommendations.append(
                    f"Analyser la relation entre {cause['metric']} et "
                    f"{cause['evidence']['correlated_metric']}"
                )
        
        # Recommandations basées sur les facteurs contributifs
        for factor in contributing_factors:
            if factor["type"] == "data_quality":
                recommendations.append(factor["recommendation"])
            elif factor["type"] == "high_variability":
                recommendations.append(factor["recommendation"])
        
        # Recommandations générales
        if correlation_analysis and correlation_analysis.get("significant_correlations"):
            recommendations.append(
                "Mettre en place un monitoring des variables corrélées"
            )
        
        recommendations.append("Implémenter un système d'alertes proactives")
        recommendations.append("Créer des tableaux de bord de monitoring en temps réel")
        
        return list(set(recommendations))  # Supprimer les doublons
    
    async def _calculate_confidence_score(
        self,
        root_causes: List[Dict[str, Any]],
        contributing_factors: List[Dict[str, Any]],
        correlation_analysis: Optional[Dict[str, Any]]
    ) -> float:
        """Calcule le score de confiance de l'analyse"""
        
        base_score = 0.5
        
        # Bonus pour les causes racines identifiées
        if root_causes:
            avg_cause_confidence = np.mean([cause.get("confidence", 0.5) for cause in root_causes])
            base_score += avg_cause_confidence * 0.3
        
        # Bonus pour les facteurs contributifs
        if contributing_factors:
            base_score += 0.1
        
        # Bonus pour l'analyse de corrélation
        if correlation_analysis and correlation_analysis.get("significant_correlations"):
            base_score += 0.1
        
        return min(1.0, base_score)
    
    async def _analyze_time_patterns(
        self,
        df: pd.DataFrame,
        time_column: str,
        affected_metrics: List[str]
    ) -> List[Dict[str, Any]]:
        """Analyse les patterns temporels"""
        
        patterns = []
        
        try:
            # Conversion de la colonne de temps si nécessaire
            if not pd.api.types.is_datetime64_any_dtype(df[time_column]):
                df[time_column] = pd.to_datetime(df[time_column], errors='coerce')
            
            # Analyse des tendances par métrique
            for metric in affected_metrics:
                if metric in df.columns and df[metric].dtype in ['int64', 'float64']:
                    # Tri par temps et calcul de la tendance
                    df_sorted = df.sort_values(time_column)
                    if len(df_sorted) > 1:
                        # Régression linéaire simple pour détecter la tendance
                        x = np.arange(len(df_sorted))
                        y = df_sorted[metric].values
                        
                        if not np.isnan(y).all():
                            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                            
                            if abs(r_value) > 0.5:  # Corrélation significative avec le temps
                                patterns.append({
                                    "type": "temporal_pattern",
                                    "metric": metric,
                                    "description": f"Tendance temporelle détectée dans {metric}",
                                    "severity": "medium",
                                    "evidence": {
                                        "slope": slope,
                                        "correlation": r_value,
                                        "p_value": p_value,
                                        "trend_direction": "increasing" if slope > 0 else "decreasing"
                                    },
                                    "confidence": abs(r_value)
                                })
        
        except Exception as e:
            logger.warning(f"Erreur lors de l'analyse des patterns temporels: {str(e)}")
        
        return patterns
    
    async def analyze_trends(
        self,
        data: List[Dict],
        time_field: str,
        metrics: List[str],
        trend_period: str = "daily"
    ) -> Dict[str, Any]:
        """Analyse des tendances temporelles détaillées"""
        
        df = pd.DataFrame(data)
        trends = []
        
        try:
            df[time_field] = pd.to_datetime(df[time_field])
            
            for metric in metrics:
                if metric in df.columns and df[metric].dtype in ['int64', 'float64']:
                    # Agrégation par période
                    if trend_period == "daily":
                        df_agg = df.groupby(df[time_field].dt.date)[metric].agg(['mean', 'std', 'count'])
                    elif trend_period == "weekly":
                        df_agg = df.groupby(df[time_field].dt.to_period('W'))[metric].agg(['mean', 'std', 'count'])
                    elif trend_period == "monthly":
                        df_agg = df.groupby(df[time_field].dt.to_period('M'))[metric].agg(['mean', 'std', 'count'])
                    else:
                        df_agg = df.groupby(df[time_field].dt.date)[metric].agg(['mean', 'std', 'count'])
                    
                    # Calcul de la tendance
                    if len(df_agg) > 1:
                        x = np.arange(len(df_agg))
                        y = df_agg['mean'].values
                        
                        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                        
                        trends.append({
                            "metric": metric,
                            "period": trend_period,
                            "trend_slope": slope,
                            "correlation": r_value,
                            "significance": p_value,
                            "trend_strength": abs(r_value),
                            "data_points": len(df_agg)
                        })
        
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des tendances: {str(e)}")
            raise e
        
        return {
            "trends": trends,
            "analysis_period": trend_period,
            "total_metrics_analyzed": len(trends)
        }
    
    async def detect_anomalies(
        self,
        data: List[Dict],
        anomaly_fields: List[str],
        detection_method: str = "statistical"
    ) -> Dict[str, Any]:
        """Détection d'anomalies avancée"""
        
        df = pd.DataFrame(data)
        anomalies = []
        
        try:
            for field in anomaly_fields:
                if field in df.columns and df[field].dtype in ['int64', 'float64']:
                    if detection_method == "statistical":
                        # Méthode statistique (IQR)
                        Q1 = df[field].quantile(0.25)
                        Q3 = df[field].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        
                        outliers = df[(df[field] < lower_bound) | (df[field] > upper_bound)]
                        
                        anomalies.append({
                            "field": field,
                            "method": "statistical",
                            "anomaly_count": len(outliers),
                            "anomaly_indices": outliers.index.tolist(),
                            "bounds": {"lower": lower_bound, "upper": upper_bound}
                        })
                    
                    elif detection_method == "isolation_forest":
                        # Isolation Forest
                        scaler = StandardScaler()
                        X = scaler.fit_transform(df[[field]].fillna(0))
                        
                        iso_forest = IsolationForest(contamination=0.1, random_state=42)
                        anomaly_labels = iso_forest.fit_predict(X)
                        
                        anomaly_indices = df.index[anomaly_labels == -1].tolist()
                        
                        anomalies.append({
                            "field": field,
                            "method": "isolation_forest",
                            "anomaly_count": len(anomaly_indices),
                            "anomaly_indices": anomaly_indices
                        })
        
        except Exception as e:
            logger.error(f"Erreur lors de la détection d'anomalies: {str(e)}")
            raise e
        
        return {
            "anomalies": anomalies,
            "detection_method": detection_method,
            "total_anomalies": sum(a["anomaly_count"] for a in anomalies)
        }
    
    async def analyze_impact(
        self,
        data: List[Dict],
        problem_events: List[Dict[str, Any]],
        impact_metrics: List[str]
    ) -> Dict[str, Any]:
        """Analyse de l'impact des problèmes"""
        
        df = pd.DataFrame(data)
        impact_analysis = []
        
        for event in problem_events:
            event_time = event.get("timestamp")
            event_type = event.get("type", "unknown")
            
            # Simulation de l'analyse d'impact
            impact_scores = {}
            for metric in impact_metrics:
                if metric in df.columns:
                    # Calcul d'un score d'impact simulé
                    impact_scores[metric] = np.random.uniform(0, 1)
            
            impact_analysis.append({
                "event_type": event_type,
                "event_time": event_time,
                "impact_scores": impact_scores,
                "overall_impact": np.mean(list(impact_scores.values())) if impact_scores else 0
            })
        
        return {
            "impact_analysis": impact_analysis,
            "total_events_analyzed": len(problem_events),
            "metrics_analyzed": impact_metrics
        }
    
    async def predict_failure(
        self,
        data: List[Dict],
        model: str = "isolation_forest",
        warning_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Prédiction des échecs futurs"""
        
        df = pd.DataFrame(data)
        
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_columns) == 0:
                return {"error": "Aucune colonne numérique trouvée pour la prédiction"}
            
            # Préparation des données
            X = df[numeric_columns].fillna(0)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            if model == "isolation_forest":
                detector = IsolationForest(contamination=0.1, random_state=42)
                anomaly_scores = -detector.score_samples(X_scaled)
            else:
                # Méthode par défaut: détection statistique
                anomaly_scores = np.mean(np.abs(X_scaled), axis=1)
            
            # Normalisation des scores
            anomaly_scores = (anomaly_scores - np.min(anomaly_scores)) / (np.max(anomaly_scores) - np.min(anomaly_scores))
            
            # Identification des risques
            high_risk_indices = np.where(anomaly_scores > warning_threshold)[0]
            
            predictions = []
            for i, score in enumerate(anomaly_scores):
                predictions.append({
                    "record_index": i,
                    "failure_probability": score,
                    "risk_level": "high" if score > warning_threshold else "medium" if score > 0.5 else "low"
                })
            
            return {
                "predictions": predictions,
                "high_risk_count": len(high_risk_indices),
                "warning_threshold": warning_threshold,
                "model_used": model
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {str(e)}")
            raise e
    
    async def get_analysis_history(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Récupère l'historique des analyses"""
        return self.analysis_history[offset:offset+limit]
    
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict]:
        """Récupère une analyse par son ID"""
        for analysis in self.analysis_history:
            if analysis["analysis_id"] == analysis_id:
                return analysis
        return None
    
    async def generate_report(
        self,
        analysis_id: str,
        format: str = "json",
        include_visualizations: bool = True
    ) -> Dict[str, Any]:
        """Génère un rapport d'analyse"""
        
        analysis = await self.get_analysis_by_id(analysis_id)
        if not analysis:
            raise ValueError(f"Analyse {analysis_id} non trouvée")
        
        report = {
            "analysis_id": analysis_id,
            "report_format": format,
            "generated_at": datetime.now().isoformat(),
            "analysis_summary": analysis,
            "include_visualizations": include_visualizations
        }
        
        return report
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques du service"""
        total_analyses = len(self.analysis_history)
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "total_rca_analyses": total_analyses,
            "uptime_seconds": uptime,
            "memory_usage_mb": psutil.virtual_memory().used / 1024 / 1024,
            "cpu_usage_percent": psutil.cpu_percent(),
            "last_updated": datetime.now().isoformat()
        }

class CorrelationAnalysisService:
    """Service d'analyse de corrélation"""
    
    def __init__(self):
        self.analysis_history = []
    
    async def analyze_correlations(
        self,
        data: List[Dict],
        variables: List[str],
        method: str = "pearson",
        significance_threshold: float = 0.05,
        min_correlation_strength: float = 0.3
    ) -> Dict[str, Any]:
        """Analyse les corrélations entre variables"""
        
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        try:
            df = pd.DataFrame(data)
            
            # Vérification des variables disponibles
            available_vars = [var for var in variables if var in df.columns]
            if len(available_vars) < 2:
                raise ValueError("Au moins 2 variables doivent être disponibles")
            
            # Sélection des colonnes numériques
            numeric_vars = []
            for var in available_vars:
                if df[var].dtype in ['int64', 'float64']:
                    numeric_vars.append(var)
            
            if len(numeric_vars) < 2:
                raise ValueError("Au moins 2 variables numériques sont requises")
            
            # Calcul de la matrice de corrélation
            correlation_matrix = {}
            significant_correlations = []
            correlation_strength = {}
            
            for i, var1 in enumerate(numeric_vars):
                correlation_matrix[var1] = {}
                
                for j, var2 in enumerate(numeric_vars):
                    if i <= j:  # Éviter les doublons
                        if method == "pearson":
                            corr, p_value = pearsonr(df[var1].dropna(), df[var2].dropna())
                        elif method == "spearman":
                            corr, p_value = spearmanr(df[var1].dropna(), df[var2].dropna())
                        else:
                            corr = df[var1].corr(df[var2], method=method)
                            p_value = 0.05  # Approximation
                        
                        correlation_matrix[var1][var2] = corr
                        correlation_matrix[var2][var1] = corr  # Symétrie
                        
                        # Identification des corrélations significatives
                        if abs(corr) >= min_correlation_strength and p_value <= significance_threshold:
                            significant_correlations.append({
                                "variable1": var1,
                                "variable2": var2,
                                "correlation": corr,
                                "p_value": p_value,
                                "strength": self._get_correlation_strength(abs(corr))
                            })
            
            # Classification de la force des corrélations
            for var in numeric_vars:
                correlations = [abs(corr) for corr in correlation_matrix[var].values() if not np.isnan(corr)]
                if correlations:
                    max_corr = max(correlations)
                    correlation_strength[var] = self._get_correlation_strength(max_corr)
            
            # Génération d'insights
            insights = self._generate_correlation_insights(significant_correlations, correlation_strength)
            
            execution_time = time.time() - start_time
            
            # Enregistrement dans l'historique
            self.analysis_history.append({
                "analysis_id": analysis_id,
                "method": method,
                "variables_analyzed": len(numeric_vars),
                "significant_correlations": len(significant_correlations),
                "execution_time": execution_time,
                "timestamp": datetime.now()
            })
            
            return {
                "analysis_id": analysis_id,
                "correlation_matrix": correlation_matrix,
                "significant_correlations": significant_correlations,
                "correlation_strength": correlation_strength,
                "insights": insights,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de corrélation {analysis_id}: {str(e)}")
            raise e
    
    def _get_correlation_strength(self, correlation_value: float) -> str:
        """Détermine la force de la corrélation"""
        abs_corr = abs(correlation_value)
        
        if abs_corr >= 0.8:
            return "very_strong"
        elif abs_corr >= 0.6:
            return "strong"
        elif abs_corr >= 0.4:
            return "moderate"
        elif abs_corr >= 0.2:
            return "weak"
        else:
            return "very_weak"
    
    def _generate_correlation_insights(
        self,
        significant_correlations: List[Dict],
        correlation_strength: Dict[str, str]
    ) -> List[str]:
        """Génère des insights basés sur les corrélations"""
        
        insights = []
        
        # Insight sur le nombre de corrélations significatives
        insights.append(f"{len(significant_correlations)} corrélations significatives détectées")
        
        # Insight sur les variables les plus corrélées
        if significant_correlations:
            strongest_corr = max(significant_correlations, key=lambda x: abs(x['correlation']))
            insights.append(
                f"Corrélation la plus forte: {strongest_corr['variable1']} et "
                f"{strongest_corr['variable2']} (r={strongest_corr['correlation']:.3f})"
            )
        
        # Insight sur les variables avec corrélations multiples
        var_counts = {}
        for corr in significant_correlations:
            for var in [corr['variable1'], corr['variable2']]:
                var_counts[var] = var_counts.get(var, 0) + 1
        
        if var_counts:
            most_correlated_var = max(var_counts, key=var_counts.get)
            insights.append(
                f"Variable la plus corrélée: {most_correlated_var} "
                f"({var_counts[most_correlated_var]} corrélations)"
            )
        
        return insights
