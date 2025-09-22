"""
Client Zingg pour la réconciliation et le matching d'entités
"""

import pandas as pd
import numpy as np
import asyncio
import logging
import uuid
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from fuzzywuzzy import fuzz, process
import psutil

logger = logging.getLogger(__name__)

class ZinggClient:
    """Client pour les opérations Zingg"""
    
    def __init__(self):
        self.reconciliation_history = []
        self.start_time = datetime.now()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    async def reconcile_entities(
        self,
        data: List[Dict],
        matching_config: Dict[str, Any],
        entity_type: str,
        threshold: float = 0.8,
        deduplication: bool = True,
        merge_strategy: str = "latest_wins"
    ) -> Dict[str, Any]:
        """Réconcilie et fusionne les entités"""
        
        start_time = time.time()
        reconciliation_id = str(uuid.uuid4())
        
        try:
            df = pd.DataFrame(data)
            original_records = len(df)
            
            # Étape 1: Déduplication si demandée
            if deduplication:
                df = await self._deduplicate_dataframe(df, matching_config)
            
            deduplicated_records = len(df)
            
            # Étape 2: Matching des entités
            matches = await self._find_entity_matches(df, matching_config, threshold)
            matched_pairs = len(matches)
            
            # Étape 3: Fusion des entités matchées
            merged_records = await self._merge_matched_entities(
                df, matches, merge_strategy
            )
            
            # Calcul des scores de confiance
            confidence_scores = await self._calculate_confidence_scores(matches)
            
            execution_time = time.time() - start_time
            
            # Enregistrement dans l'historique
            self.reconciliation_history.append({
                "reconciliation_id": reconciliation_id,
                "entity_type": entity_type,
                "original_records": original_records,
                "deduplicated_records": deduplicated_records,
                "matched_pairs": matched_pairs,
                "execution_time": execution_time,
                "timestamp": datetime.now(),
                "status": "completed"
            })
            
            return {
                "reconciliation_id": reconciliation_id,
                "original_records": original_records,
                "deduplicated_records": deduplicated_records,
                "matched_pairs": matched_pairs,
                "merged_records": merged_records,
                "confidence_scores": confidence_scores,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la réconciliation {reconciliation_id}: {str(e)}")
            raise e
    
    async def _deduplicate_dataframe(
        self, 
        df: pd.DataFrame, 
        config: Dict[str, Any]
    ) -> pd.DataFrame:
        """Supprime les doublons exacts et similaires"""
        
        # Suppression des doublons exacts
        df = df.drop_duplicates()
        
        # Suppression des doublons similaires
        similarity_fields = config.get("similarity_fields", [])
        threshold = config.get("similarity_threshold", 0.9)
        
        if similarity_fields:
            # Utilisation de l'algorithme de Levenshtein pour les chaînes
            to_remove = set()
            
            for i in range(len(df)):
                if i in to_remove:
                    continue
                    
                for j in range(i + 1, len(df)):
                    if j in to_remove:
                        continue
                    
                    similarity_score = await self._calculate_record_similarity(
                        df.iloc[i], df.iloc[j], similarity_fields
                    )
                    
                    if similarity_score >= threshold:
                        to_remove.add(j)
            
            df = df.drop(df.index[list(to_remove)])
        
        return df
    
    async def _find_entity_matches(
        self,
        df: pd.DataFrame,
        config: Dict[str, Any],
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Trouve les correspondances entre entités"""
        
        matches = []
        matching_fields = config.get("matching_fields", [])
        
        if not matching_fields:
            return matches
        
        # Parcours des paires d'entités
        for i in range(len(df)):
            for j in range(i + 1, len(df)):
                similarity_score = await self._calculate_record_similarity(
                    df.iloc[i], df.iloc[j], matching_fields
                )
                
                if similarity_score >= threshold:
                    matches.append({
                        "entity_1_index": i,
                        "entity_2_index": j,
                        "entity_1_id": df.iloc[i].get("id", str(i)),
                        "entity_2_id": df.iloc[j].get("id", str(j)),
                        "similarity_score": similarity_score,
                        "matching_fields": matching_fields
                    })
        
        return matches
    
    async def _calculate_record_similarity(
        self,
        record1: pd.Series,
        record2: pd.Series,
        fields: List[str]
    ) -> float:
        """Calcule la similarité entre deux enregistrements"""
        
        similarities = []
        
        for field in fields:
            if field in record1 and field in record2:
                val1 = str(record1[field]).strip().lower()
                val2 = str(record2[field]).strip().lower()
                
                if val1 and val2:
                    # Similarité de chaînes avec fuzzy matching
                    similarity = fuzz.ratio(val1, val2) / 100.0
                    similarities.append(similarity)
        
        if similarities:
            return np.mean(similarities)
        else:
            return 0.0
    
    async def _merge_matched_entities(
        self,
        df: pd.DataFrame,
        matches: List[Dict[str, Any]],
        merge_strategy: str
    ) -> List[Dict[str, Any]]:
        """Fusionne les entités matchées"""
        
        merged_records = []
        processed_indices = set()
        
        for match in matches:
            idx1 = match["entity_1_index"]
            idx2 = match["entity_2_index"]
            
            if idx1 in processed_indices or idx2 in processed_indices:
                continue
            
            record1 = df.iloc[idx1].to_dict()
            record2 = df.iloc[idx2].to_dict()
            
            # Fusion selon la stratégie
            if merge_strategy == "latest_wins":
                merged_record = await self._merge_latest_wins(record1, record2)
            elif merge_strategy == "first_wins":
                merged_record = await self._merge_first_wins(record1, record2)
            elif merge_strategy == "concatenate":
                merged_record = await self._merge_concatenate(record1, record2)
            else:
                merged_record = record1  # Par défaut
            
            merged_record["_merged_from"] = [record1.get("id"), record2.get("id")]
            merged_record["_similarity_score"] = match["similarity_score"]
            
            merged_records.append(merged_record)
            processed_indices.update([idx1, idx2])
        
        # Ajout des enregistrements non matchés
        for i, row in df.iterrows():
            if i not in processed_indices:
                merged_records.append(row.to_dict())
        
        return merged_records
    
    async def _merge_latest_wins(self, record1: Dict, record2: Dict) -> Dict:
        """Stratégie de fusion: le plus récent gagne"""
        # Pour la démo, on suppose que record2 est plus récent
        merged = record1.copy()
        for key, value in record2.items():
            if value is not None and value != "":
                merged[key] = value
        return merged
    
    async def _merge_first_wins(self, record1: Dict, record2: Dict) -> Dict:
        """Stratégie de fusion: le premier gagne"""
        merged = record1.copy()
        for key, value in record2.items():
            if key not in merged or merged[key] is None or merged[key] == "":
                merged[key] = value
        return merged
    
    async def _merge_concatenate(self, record1: Dict, record2: Dict) -> Dict:
        """Stratégie de fusion: concaténation"""
        merged = {}
        for key in set(record1.keys()) | set(record2.keys()):
            val1 = record1.get(key, "")
            val2 = record2.get(key, "")
            
            if val1 and val2:
                merged[key] = f"{val1} | {val2}"
            elif val1:
                merged[key] = val1
            else:
                merged[key] = val2
        
        return merged
    
    async def _calculate_confidence_scores(self, matches: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcule les scores de confiance"""
        if not matches:
            return {}
        
        scores = [match["similarity_score"] for match in matches]
        
        return {
            "average_confidence": np.mean(scores),
            "min_confidence": np.min(scores),
            "max_confidence": np.max(scores),
            "std_confidence": np.std(scores),
            "high_confidence_count": len([s for s in scores if s > 0.9]),
            "medium_confidence_count": len([s for s in scores if 0.7 <= s <= 0.9]),
            "low_confidence_count": len([s for s in scores if s < 0.7])
        }
    
    async def find_matches(
        self,
        data: List[Dict[str, Any]],
        matching_config: Dict[str, Any],
        threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Trouve les correspondances sans fusion"""
        
        df = pd.DataFrame(data)
        matches = await self._find_entity_matches(df, matching_config, threshold)
        
        return matches
    
    async def deduplicate_data(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Déduplique les données"""
        
        df = pd.DataFrame(data)
        deduplicated_df = await self._deduplicate_dataframe(df, config)
        
        return deduplicated_df.to_dict('records')
    
    async def validate_matches(
        self,
        matches: List[Dict[str, Any]],
        rules: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Valide les matches selon des règles"""
        
        validated_matches = []
        
        for match in matches:
            is_valid = True
            validation_errors = []
            
            # Vérification du score de similarité
            min_score = rules.get("min_similarity_score", 0.8)
            if match.get("similarity_score", 0) < min_score:
                is_valid = False
                validation_errors.append(f"Score de similarité trop faible: {match.get('similarity_score', 0)}")
            
            # Autres règles de validation...
            
            match["is_valid"] = is_valid
            match["validation_errors"] = validation_errors
            validated_matches.append(match)
        
        return validated_matches
    
    async def train_model(
        self,
        training_data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Entraîne un modèle de matching"""
        
        # Pour la démo, on simule un entraînement
        model_info = {
            "model_id": str(uuid.uuid4()),
            "training_records": len(training_data),
            "model_type": config.get("model_type", "similarity_based"),
            "accuracy": 0.95,  # Simulation
            "training_time": 120.5,  # Simulation
            "timestamp": datetime.now().isoformat()
        }
        
        return model_info
    
    async def get_reconciliation_history(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Récupère l'historique des réconciliations"""
        return self.reconciliation_history[offset:offset+limit]
    
    async def get_reconciliation_by_id(self, reconciliation_id: str) -> Optional[Dict]:
        """Récupère une réconciliation par son ID"""
        for reconciliation in self.reconciliation_history:
            if reconciliation["reconciliation_id"] == reconciliation_id:
                return reconciliation
        return None
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques du service"""
        total_reconciliations = len(self.reconciliation_history)
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "total_reconciliations": total_reconciliations,
            "uptime_seconds": uptime,
            "memory_usage_mb": psutil.virtual_memory().used / 1024 / 1024,
            "cpu_usage_percent": psutil.cpu_percent(),
            "last_updated": datetime.now().isoformat()
        }
