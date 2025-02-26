from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import hashlib
import json
from pydantic import BaseModel, validator
import re

class DatasetValidator:
    def __init__(self):
        self.validation_rules = {}
        self.validation_history = []
    
    def add_rule(self, column: str, rule_type: str, parameters: Dict[str, Any]):
        """Add a validation rule for a specific column"""
        if column not in self.validation_rules:
            self.validation_rules[column] = []
        
        self.validation_rules[column].append({
            "type": rule_type,
            "parameters": parameters
        })
    
    def validate_dataset(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Validate entire dataset against defined rules"""
        validation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_rows": len(dataset),
            "column_results": {},
            "overall_validity": True
        }
        
        for column, rules in self.validation_rules.items():
            if column not in dataset.columns:
                validation_results["column_results"][column] = {
                    "error": "Column not found in dataset"
                }
                validation_results["overall_validity"] = False
                continue
            
            column_results = self._validate_column(dataset[column], rules)
            validation_results["column_results"][column] = column_results
            
            if not column_results["is_valid"]:
                validation_results["overall_validity"] = False
        
        self.validation_history.append(validation_results)
        return validation_results
    
    def _validate_column(self, column: pd.Series, rules: List[Dict]) -> Dict[str, Any]:
        """Validate a single column against its rules"""
        results = {
            "is_valid": True,
            "rule_results": []
        }
        
        for rule in rules:
            rule_result = self._apply_rule(column, rule["type"], rule["parameters"])
            results["rule_results"].append(rule_result)
            
            if not rule_result["is_valid"]:
                results["is_valid"] = False
        
        return results
    
    def _apply_rule(self, column: pd.Series, rule_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a specific validation rule to a column"""
        result = {
            "rule_type": rule_type,
            "is_valid": True,
            "details": {}
        }
        
        try:
            if rule_type == "type_check":
                result["is_valid"] = column.dtype == parameters["expected_type"]
                result["details"]["actual_type"] = str(column.dtype)
            
            elif rule_type == "range_check":
                min_val = parameters.get("min")
                max_val = parameters.get("max")
                if min_val is not None:
                    result["is_valid"] &= column.min() >= min_val
                if max_val is not None:
                    result["is_valid"] &= column.max() <= max_val
                result["details"]["min"] = column.min()
                result["details"]["max"] = column.max()
            
            elif rule_type == "unique_check":
                duplicates = column.duplicated().sum()
                result["is_valid"] = duplicates == 0
                result["details"]["duplicate_count"] = int(duplicates)
            
            elif rule_type == "pattern_check":
                pattern = parameters["pattern"]
                matches = column.str.match(pattern).all()
                result["is_valid"] = matches
                result["details"]["non_matching"] = int((~column.str.match(pattern)).sum())
            
            elif rule_type == "missing_check":
                missing = column.isnull().sum()
                threshold = parameters.get("threshold", 0)
                result["is_valid"] = missing <= threshold
                result["details"]["missing_count"] = int(missing)
            
            elif rule_type == "categorical_check":
                allowed_values = set(parameters["allowed_values"])
                invalid_values = set(column.unique()) - allowed_values
                result["is_valid"] = len(invalid_values) == 0
                result["details"]["invalid_values"] = list(invalid_values)
            
        except Exception as e:
            result["is_valid"] = False
            result["details"]["error"] = str(e)
        
        return result
    
    def get_validation_history(self) -> List[Dict[str, Any]]:
        """Retrieve validation history"""
        return self.validation_history
    
    def export_rules(self, filepath: str):
        """Export validation rules to a file"""
        with open(filepath, 'w') as f:
            json.dump(self.validation_rules, f, indent=2)
    
    def import_rules(self, filepath: str):
        """Import validation rules from a file"""
        with open(filepath, 'r') as f:
            self.validation_rules = json.load(f)
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report"""
        if not self.validation_history:
            return {"error": "No validation history available"}
        
        latest_validation = self.validation_history[-1]
        historical_stats = self._calculate_historical_stats()
        
        return {
            "latest_validation": latest_validation,
            "historical_stats": historical_stats,
            "rule_coverage": self._calculate_rule_coverage(),
            "validation_trend": self._calculate_validation_trend()
        }
    
    def _calculate_historical_stats(self) -> Dict[str, Any]:
        """Calculate statistical metrics from validation history"""
        total_validations = len(self.validation_history)
        success_rate = sum(1 for v in self.validation_history if v["overall_validity"]) / total_validations
        
        return {
            "total_validations": total_validations,
            "success_rate": success_rate,
            "last_successful": next(
                (v["timestamp"] for v in reversed(self.validation_history) if v["overall_validity"]),
                None
            )
        }
    
    def _calculate_rule_coverage(self) -> Dict[str, Any]:
        """Calculate rule coverage metrics"""
        total_columns = len(self.validation_rules)
        rules_per_column = {
            column: len(rules) for column, rules in self.validation_rules.items()
        }
        
        return {
            "total_columns": total_columns,
            "total_rules": sum(rules_per_column.values()),
            "rules_per_column": rules_per_column
        }
    
    def _calculate_validation_trend(self) -> List[Dict[str, Any]]:
        """Calculate validation trend over time"""
        return [
            {
                "timestamp": v["timestamp"],
                "validity": v["overall_validity"],
                "total_errors": sum(
                    1 for col_result in v["column_results"].values()
                    if not col_result.get("is_valid", False)
                )
            }
            for v in self.validation_history
        ]
