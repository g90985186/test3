from typing import Dict, List, Optional, Any
import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from .base import BaseAIModel, ModelResponse
from .manager import ModelManager

logger = logging.getLogger(__name__)

class ModelBenchmark:
    """Benchmarking system for evaluating model performance."""
    
    def __init__(
        self,
        model_manager: ModelManager,
        benchmark_dir: str = "app/ai/benchmarks"
    ):
        self.model_manager = model_manager
        self.benchmark_dir = Path(benchmark_dir)
        self.benchmark_dir.mkdir(parents=True, exist_ok=True)
        self.results: Dict[str, Dict[str, Any]] = {}
    
    async def run_benchmark(
        self,
        model_name: str,
        test_cases: List[Dict[str, Any]],
        metrics: List[str] = ["latency", "accuracy", "throughput"],
        num_runs: int = 3
    ) -> Dict[str, Any]:
        """Run benchmark tests for a model."""
        model = await self.model_manager.get_model(model_name)
        if not model:
            raise ValueError(f"Model {model_name} not found")
        
        results = {
            "model_name": model_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "test_cases": []
        }
        
        try:
            # Run each test case multiple times
            for test_case in test_cases:
                case_results = []
                
                for run in range(num_runs):
                    start_time = datetime.now()
                    
                    # Generate response
                    response = await model.generate(
                        test_case["prompt"],
                        **test_case.get("parameters", {})
                    )
                    
                    # Calculate metrics
                    latency = (datetime.now() - start_time).total_seconds()
                    accuracy = self._calculate_accuracy(
                        response.content,
                        test_case.get("expected_output", "")
                    )
                    
                    case_results.append({
                        "run": run + 1,
                        "latency": latency,
                        "accuracy": accuracy,
                        "response": response.content,
                        "confidence": response.confidence
                    })
                
                # Calculate average metrics
                avg_latency = sum(r["latency"] for r in case_results) / num_runs
                avg_accuracy = sum(r["accuracy"] for r in case_results) / num_runs
                
                results["test_cases"].append({
                    "test_case": test_case["name"],
                    "average_latency": avg_latency,
                    "average_accuracy": avg_accuracy,
                    "runs": case_results
                })
            
            # Calculate overall metrics
            results["metrics"] = {
                "average_latency": sum(
                    tc["average_latency"] for tc in results["test_cases"]
                ) / len(results["test_cases"]),
                "average_accuracy": sum(
                    tc["average_accuracy"] for tc in results["test_cases"]
                ) / len(results["test_cases"]),
                "throughput": len(test_cases) / sum(
                    tc["average_latency"] for tc in results["test_cases"]
                )
            }
            
            # Save results
            self._save_results(model_name, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error running benchmark for model {model_name}: {str(e)}")
            raise
    
    def _calculate_accuracy(
        self,
        actual: str,
        expected: str
    ) -> float:
        """Calculate accuracy between actual and expected output."""
        # Simple string similarity (can be improved with more sophisticated metrics)
        actual_words = set(actual.lower().split())
        expected_words = set(expected.lower().split())
        
        if not expected_words:
            return 1.0
        
        intersection = actual_words.intersection(expected_words)
        return len(intersection) / len(expected_words)
    
    def _save_results(
        self,
        model_name: str,
        results: Dict[str, Any]
    ) -> None:
        """Save benchmark results to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{model_name}_{timestamp}.json"
            filepath = self.benchmark_dir / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Saved benchmark results to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving benchmark results: {str(e)}")
    
    async def compare_models(
        self,
        model_names: List[str],
        test_cases: List[Dict[str, Any]],
        metrics: List[str] = ["latency", "accuracy", "throughput"]
    ) -> Dict[str, Any]:
        """Compare performance of multiple models."""
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "models": {},
            "metrics": {}
        }
        
        try:
            # Run benchmarks for each model
            for model_name in model_names:
                results = await self.run_benchmark(
                    model_name,
                    test_cases,
                    metrics
                )
                comparison["models"][model_name] = results["metrics"]
            
            # Calculate comparison metrics
            for metric in metrics:
                values = [
                    results["metrics"][metric]
                    for results in comparison["models"].values()
                ]
                comparison["metrics"][metric] = {
                    "best": max(values),
                    "worst": min(values),
                    "average": sum(values) / len(values),
                    "variance": sum((x - sum(values) / len(values)) ** 2 for x in values) / len(values)
                }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing models: {str(e)}")
            raise
    
    def get_benchmark_history(
        self,
        model_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get benchmark history for a model or all models."""
        try:
            history = []
            
            # Get all benchmark files
            pattern = f"{model_name}_*.json" if model_name else "*.json"
            for filepath in self.benchmark_dir.glob(pattern):
                with open(filepath, "r", encoding="utf-8") as f:
                    results = json.load(f)
                    history.append(results)
            
            # Sort by timestamp
            history.sort(key=lambda x: x["timestamp"], reverse=True)
            return history
            
        except Exception as e:
            logger.error(f"Error getting benchmark history: {str(e)}")
            return [] 