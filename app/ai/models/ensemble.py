from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from .base import BaseAIModel, ModelResponse
from .manager import ModelManager

logger = logging.getLogger(__name__)

class ModelEnsemble:
    """Ensemble system for combining multiple models."""
    
    def __init__(
        self,
        model_manager: ModelManager,
        ensemble_name: str,
        models: List[str],
        weights: Optional[Dict[str, float]] = None
    ):
        self.model_manager = model_manager
        self.ensemble_name = ensemble_name
        self.models = models
        self.weights = weights or {model: 1.0 for model in models}
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
    
    async def generate(
        self,
        prompt: str,
        strategy: str = "weighted_average",
        **kwargs
    ) -> ModelResponse:
        """Generate a response using the ensemble."""
        try:
            # Get responses from all models
            responses = []
            for model_name in self.models:
                model = await self.model_manager.get_model(model_name)
                if not model:
                    logger.warning(f"Model {model_name} not found in ensemble")
                    continue
                
                response = await model.generate(prompt, **kwargs)
                responses.append((model_name, response))
            
            if not responses:
                raise ValueError("No valid responses from ensemble models")
            
            # Combine responses based on strategy
            if strategy == "weighted_average":
                return await self._weighted_average(responses)
            elif strategy == "majority_vote":
                return await self._majority_vote(responses)
            elif strategy == "best_model":
                return await self._best_model(responses)
            else:
                raise ValueError(f"Unknown ensemble strategy: {strategy}")
            
        except Exception as e:
            logger.error(f"Error in ensemble generation: {str(e)}")
            raise
    
    async def _weighted_average(
        self,
        responses: List[tuple[str, ModelResponse]]
    ) -> ModelResponse:
        """Combine responses using weighted average."""
        total_weight = sum(self.weights[model_name] for model_name, _ in responses)
        weighted_confidence = 0.0
        weighted_content = ""
        
        for model_name, response in responses:
            weight = self.weights[model_name] / total_weight
            weighted_confidence += response.confidence * weight
            weighted_content += f"[{model_name}] {response.content}\n\n"
        
        return ModelResponse(
            content=weighted_content.strip(),
            confidence=weighted_confidence,
            processing_time=sum(r.processing_time for _, r in responses) / len(responses),
            model_name=self.ensemble_name,
            metadata={
                "strategy": "weighted_average",
                "models_used": [model_name for model_name, _ in responses],
                "weights": {model_name: self.weights[model_name] for model_name, _ in responses}
            }
        )
    
    async def _majority_vote(
        self,
        responses: List[tuple[str, ModelResponse]]
    ) -> ModelResponse:
        """Combine responses using majority vote."""
        # Group similar responses
        response_groups: Dict[str, List[tuple[str, ModelResponse]]] = {}
        
        for model_name, response in responses:
            # Simple similarity check (can be improved)
            content_key = response.content[:100]  # Use first 100 chars as key
            if content_key not in response_groups:
                response_groups[content_key] = []
            response_groups[content_key].append((model_name, response))
        
        # Find the largest group
        largest_group = max(response_groups.values(), key=len)
        
        # Combine responses from the largest group
        combined_content = "\n\n".join(
            f"[{model_name}] {response.content}"
            for model_name, response in largest_group
        )
        
        return ModelResponse(
            content=combined_content,
            confidence=len(largest_group) / len(responses),
            processing_time=sum(r.processing_time for _, r in responses) / len(responses),
            model_name=self.ensemble_name,
            metadata={
                "strategy": "majority_vote",
                "models_used": [model_name for model_name, _ in responses],
                "group_size": len(largest_group),
                "total_models": len(responses)
            }
        )
    
    async def _best_model(
        self,
        responses: List[tuple[str, ModelResponse]]
    ) -> ModelResponse:
        """Select the best model response based on confidence."""
        best_response = max(responses, key=lambda x: x[1].confidence)
        model_name, response = best_response
        
        return ModelResponse(
            content=response.content,
            confidence=response.confidence,
            processing_time=response.processing_time,
            model_name=self.ensemble_name,
            metadata={
                "strategy": "best_model",
                "selected_model": model_name,
                "models_considered": [model_name for model_name, _ in responses]
            }
        )
    
    def update_weights(self, new_weights: Dict[str, float]) -> None:
        """Update model weights in the ensemble."""
        for model_name, weight in new_weights.items():
            if model_name in self.models:
                self.weights[model_name] = weight
    
    def get_ensemble_info(self) -> Dict[str, Any]:
        """Get information about the ensemble."""
        return {
            "name": self.ensemble_name,
            "models": self.models,
            "weights": self.weights,
            "performance_metrics": self.performance_metrics
        }
    
    async def update_performance_metrics(
        self,
        model_name: str,
        success: bool,
        processing_time: float
    ) -> None:
        """Update performance metrics for a model."""
        if model_name not in self.performance_metrics:
            self.performance_metrics[model_name] = {
                "success_count": 0,
                "failure_count": 0,
                "total_processing_time": 0.0,
                "request_count": 0
            }
        
        metrics = self.performance_metrics[model_name]
        metrics["request_count"] += 1
        metrics["total_processing_time"] += processing_time
        
        if success:
            metrics["success_count"] += 1
        else:
            metrics["failure_count"] += 1 