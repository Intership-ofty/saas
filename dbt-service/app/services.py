"""
Services métier pour le service DBT
"""

import pandas as pd
import numpy as np
import asyncio
import logging
import uuid
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import psutil

from models import (
    TransformationType, KPIMetric, KPICalculation, 
    TransformationHistory, ServiceMetrics, DataQualityMetrics
)

logger = logging.getLogger(__name__)

class DataTransformationService:
    """Service de transformation de données"""
    
    def __init__(self):
        self.transformation_history = []
        self.start_time = datetime.now()
    
    async def execute_transformation(
        self, 
        data: List[Dict], 
        transformation_type: TransformationType,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Exécute une transformation de données"""
        
        start_time = time.time()
        transformation_id = str(uuid.uuid4())
        
        try:
            df = pd.DataFrame(data)
            input_records = len(df)
            
            # Application de la transformation selon le type
            if transformation_type == TransformationType.CLEAN:
                transformed_df = await self._clean_data(df, parameters)
            elif transformation_type == TransformationType.NORMALIZE:
                transformed_df = await self._normalize_data(df, parameters)
            elif transformation_type == TransformationType.AGGREGATE:
                transformed_df = await self._aggregate_data(df, parameters)
            elif transformation_type == TransformationType.JOIN:
                transformed_df = await self._join_data(df, parameters)
            elif transformation_type == TransformationType.FILTER:
                transformed_df = await self._filter_data(df, parameters)
            elif transformation_type == TransformationType.PIVOT:
                transformed_df = await self._pivot_data(df, parameters)
            else:
                transformed_df = df
            
            output_records = len(transformed_df)
            execution_time = time.time() - start_time
            
            # Calcul des métriques
            metrics = {
                "input_records": input_records,
                "output_records": output_records,
                "records_filtered": input_records - output_records,
                "transformation_type": transformation_type.value,
                "execution_time": execution_time
            }
            
            # Enregistrement dans l'historique
            history_entry = TransformationHistory(
                transformation_id=transformation_id,
                transformation_type=transformation_type,
                input_records=input_records,
                output_records=output_records,
                execution_time=execution_time,
                status="completed",
                timestamp=datetime.now()
            )
            self.transformation_history.append(history_entry)
            
            return {
                "transformation_id": transformation_id,
                "transformed_data": transformed_df.to_dict('records'),
                "metrics": metrics,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la transformation {transformation_id}: {str(e)}")
            execution_time = time.time() - start_time
            
            # Enregistrement de l'erreur
            history_entry = TransformationHistory(
                transformation_id=transformation_id,
                transformation_type=transformation_type,
                input_records=len(data) if data else 0,
                output_records=0,
                execution_time=execution_time,
                status="failed",
                timestamp=datetime.now(),
                error_message=str(e)
            )
            self.transformation_history.append(history_entry)
            
            raise e
    
    async def _clean_data(self, df: pd.DataFrame, parameters: Optional[Dict] = None) -> pd.DataFrame:
        """Nettoie les données"""
        # Suppression des doublons
        if parameters and parameters.get("remove_duplicates", False):
            df = df.drop_duplicates()
        
        # Gestion des valeurs manquantes
        if parameters and "missing_value_strategy" in parameters:
            strategy = parameters["missing_value_strategy"]
            if strategy == "drop":
                df = df.dropna()
            elif strategy == "fill":
                fill_value = parameters.get("fill_value", 0)
                df = df.fillna(fill_value)
        
        # Nettoyage des chaînes de caractères
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            if parameters and parameters.get("trim_strings", False):
                df[col] = df[col].astype(str).str.strip()
            if parameters and parameters.get("lowercase_strings", False):
                df[col] = df[col].astype(str).str.lower()
        
        return df
    
    async def _normalize_data(self, df: pd.DataFrame, parameters: Optional[Dict] = None) -> pd.DataFrame:
        """Normalise les données"""
        if not parameters:
            return df
        
        # Normalisation des colonnes numériques
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if parameters.get("normalize_numeric", False):
                # Normalisation min-max
                min_val = df[col].min()
                max_val = df[col].max()
                if max_val > min_val:
                    df[col] = (df[col] - min_val) / (max_val - min_val)
        
        # Normalisation des dates
        date_columns = df.select_dtypes(include=['datetime64']).columns
        for col in date_columns:
            if parameters.get("normalize_dates", False):
                df[f"{col}_normalized"] = (df[col] - df[col].min()).dt.days
        
        return df
    
    async def _aggregate_data(self, df: pd.DataFrame, parameters: Optional[Dict] = None) -> pd.DataFrame:
        """Agrège les données"""
        if not parameters:
            return df
        
        group_by = parameters.get("group_by", [])
        aggregations = parameters.get("aggregations", {})
        
        if group_by and aggregations:
            result = df.groupby(group_by).agg(aggregations).reset_index()
            return result
        
        return df
    
    async def _join_data(self, df: pd.DataFrame, parameters: Optional[Dict] = None) -> pd.DataFrame:
        """Joint des données"""
        # Pour la démo, retourne les données telles quelles
        # Dans un vrai système, on récupérerait les données à joindre depuis la base
        return df
    
    async def _filter_data(self, df: pd.DataFrame, parameters: Optional[Dict] = None) -> pd.DataFrame:
        """Filtre les données"""
        if not parameters:
            return df
        
        filters = parameters.get("filters", {})
        for column, condition in filters.items():
            if column in df.columns:
                if condition["operator"] == "equals":
                    df = df[df[column] == condition["value"]]
                elif condition["operator"] == "greater_than":
                    df = df[df[column] > condition["value"]]
                elif condition["operator"] == "less_than":
                    df = df[df[column] < condition["value"]]
                elif condition["operator"] == "contains":
                    df = df[df[column].str.contains(condition["value"], na=False)]
        
        return df
    
    async def _pivot_data(self, df: pd.DataFrame, parameters: Optional[Dict] = None) -> pd.DataFrame:
        """Pivote les données"""
        if not parameters:
            return df
        
        index = parameters.get("index")
        columns = parameters.get("columns")
        values = parameters.get("values")
        
        if index and columns and values:
            result = df.pivot_table(index=index, columns=columns, values=values, aggfunc='sum')
            return result.reset_index()
        
        return df
    
    async def normalize_data(self, data: List[Dict], normalization_rules: Dict[str, Any]) -> List[Dict]:
        """Normalise les données selon des règles spécifiques"""
        df = pd.DataFrame(data)
        
        for rule in normalization_rules.get("rules", []):
            field_name = rule["field_name"]
            if field_name in df.columns:
                if rule["normalization_type"] == "uppercase":
                    df[field_name] = df[field_name].astype(str).str.upper()
                elif rule["normalization_type"] == "lowercase":
                    df[field_name] = df[field_name].astype(str).str.lower()
                elif rule["normalization_type"] == "trim":
                    df[field_name] = df[field_name].astype(str).str.strip()
                elif rule["normalization_type"] == "format_date":
                    df[field_name] = pd.to_datetime(df[field_name], errors='coerce')
        
        return df.to_dict('records')
    
    async def get_transformation_history(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Récupère l'historique des transformations"""
        return [
            history.dict() for history in self.transformation_history[offset:offset+limit]
        ]
    
    async def get_transformation_by_id(self, transformation_id: str) -> Optional[Dict]:
        """Récupère une transformation par son ID"""
        for history in self.transformation_history:
            if history.transformation_id == transformation_id:
                return history.dict()
        return None
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques du service"""
        total_transformations = len(self.transformation_history)
        successful_transformations = len([t for t in self.transformation_history if t.status == "completed"])
        failed_transformations = total_transformations - successful_transformations
        
        avg_execution_time = 0
        if successful_transformations > 0:
            avg_execution_time = sum(t.execution_time for t in self.transformation_history if t.status == "completed") / successful_transformations
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "total_transformations": total_transformations,
            "successful_transformations": successful_transformations,
            "failed_transformations": failed_transformations,
            "average_execution_time": avg_execution_time,
            "uptime_seconds": uptime,
            "memory_usage_mb": psutil.virtual_memory().used / 1024 / 1024,
            "cpu_usage_percent": psutil.cpu_percent(),
            "last_updated": datetime.now().isoformat()
        }

class KPIService:
    """Service de calcul de KPI"""
    
    async def calculate_kpis(self, data: List[Dict], metrics: List[KPIMetric]) -> Dict[str, Any]:
        """Calcule les KPI demandés"""
        df = pd.DataFrame(data)
        results = {}
        
        for metric in metrics:
            if metric == KPIMetric.COUNT:
                results["count"] = len(df)
            elif metric == KPIMetric.SUM:
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                results["sum"] = {col: df[col].sum() for col in numeric_columns}
            elif metric == KPIMetric.AVG:
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                results["average"] = {col: df[col].mean() for col in numeric_columns}
            elif metric == KPIMetric.MIN:
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                results["min"] = {col: df[col].min() for col in numeric_columns}
            elif metric == KPIMetric.MAX:
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                results["max"] = {col: df[col].max() for col in numeric_columns}
            elif metric == KPIMetric.MEDIAN:
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                results["median"] = {col: df[col].median() for col in numeric_columns}
            elif metric == KPIMetric.STANDARD_DEVIATION:
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                results["std_dev"] = {col: df[col].std() for col in numeric_columns}
        
        return results
