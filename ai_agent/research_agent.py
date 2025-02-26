from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import StringPromptTemplate
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from transformers import pipeline
import torch

class ResearchAssistant:
    def __init__(self, model_name: str = "gpt-4"):
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.tools = self._initialize_tools()
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.text_classifier = pipeline("text-classification")
        self.anomaly_detector = IsolationForest(random_state=42)
        
    def _initialize_tools(self) -> List[Tool]:
        tools = [
            Tool(
                name="data_analysis",
                func=self._analyze_dataset,
                description="Analyze scientific datasets and extract insights"
            ),
            Tool(
                name="similarity_search",
                func=self._find_similar_datasets,
                description="Find similar datasets based on metadata and content"
            ),
            Tool(
                name="quality_assessment",
                func=self._assess_data_quality,
                description="Assess the quality and reliability of scientific data"
            ),
            Tool(
                name="advanced_analytics",
                func=self._perform_advanced_analytics,
                description="Perform advanced statistical analysis and machine learning"
            ),
            Tool(
                name="text_analysis",
                func=self._analyze_text_data,
                description="Analyze text data using NLP techniques"
            ),
            Tool(
                name="anomaly_detection",
                func=self._detect_anomalies,
                description="Detect anomalies in numerical datasets"
            )
        ]
        return tools
    
    def _analyze_dataset(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        try:
            analysis_results = {
                "row_count": len(dataset),
                "column_count": len(dataset.columns),
                "missing_values": dataset.isnull().sum().to_dict(),
                "basic_stats": dataset.describe().to_dict(),
                "correlations": dataset.corr().to_dict() if dataset.select_dtypes(include=[np.number]).columns.any() else None,
                "data_types": dataset.dtypes.to_dict(),
                "unique_values": {col: dataset[col].nunique() for col in dataset.columns}
            }
            return analysis_results
        except Exception as e:
            return {"error": str(e)}
    
    def _perform_advanced_analytics(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        try:
            numerical_cols = dataset.select_dtypes(include=[np.number]).columns
            if len(numerical_cols) < 2:
                return {"error": "Insufficient numerical columns for advanced analytics"}
            
            # Prepare data
            X = dataset[numerical_cols]
            X = StandardScaler().fit_transform(X)
            
            # Perform PCA
            pca = PCA(n_components=min(3, len(numerical_cols)))
            pca_result = pca.fit_transform(X)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=min(5, len(dataset)), random_state=42)
            clusters = kmeans.fit_predict(X)
            
            return {
                "pca_explained_variance": pca.explained_variance_ratio_.tolist(),
                "pca_components": pca_result.tolist(),
                "clustering_labels": clusters.tolist(),
                "cluster_centers": kmeans.cluster_centers_.tolist()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_text_data(self, text_data: List[str]) -> Dict[str, Any]:
        try:
            results = {
                "sentiment_analysis": self.sentiment_analyzer(text_data),
                "classification": self.text_classifier(text_data),
                "text_stats": {
                    "avg_length": sum(len(text) for text in text_data) / len(text_data),
                    "total_words": sum(len(text.split()) for text in text_data)
                }
            }
            return results
        except Exception as e:
            return {"error": str(e)}
    
    def _detect_anomalies(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        try:
            numerical_data = dataset.select_dtypes(include=[np.number])
            if numerical_data.empty:
                return {"error": "No numerical data for anomaly detection"}
            
            # Fit and predict anomalies
            predictions = self.anomaly_detector.fit_predict(numerical_data)
            anomaly_indices = np.where(predictions == -1)[0]
            
            return {
                "anomaly_count": len(anomaly_indices),
                "anomaly_indices": anomaly_indices.tolist(),
                "anomaly_scores": self.anomaly_detector.score_samples(numerical_data).tolist()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def process_research_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            results = {}
            if "analysis" in query.lower():
                results["basic_analysis"] = self._analyze_dataset(context["dataset"])
            if "advanced" in query.lower():
                results["advanced_analysis"] = self._perform_advanced_analytics(context["dataset"])
            if "text" in query.lower() and "text_data" in context:
                results["text_analysis"] = self._analyze_text_data(context["text_data"])
            if "anomaly" in query.lower():
                results["anomaly_detection"] = self._detect_anomalies(context["dataset"])
            if "quality" in query.lower():
                results["quality_assessment"] = self._assess_data_quality(context["dataset"])
            
            return results
        except Exception as e:
            return {"error": str(e)}
