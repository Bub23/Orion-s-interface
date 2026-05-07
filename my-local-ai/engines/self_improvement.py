import json
import os
from datetime import datetime
from config import DATA_DIR

class SelfImprovementEngine:
    """Orion learns from outputs and improves execution."""
    
    def __init__(self):
        self.improvement_log = os.path.join(DATA_DIR, "improvement_log.json")
        self.strategy_history = self._load_history()
    
    def _load_history(self):
        """Load improvement history."""
        if os.path.exists(self.improvement_log):
            with open(self.improvement_log, 'r') as f:
                return json.load(f)
        return {"iterations": [], "best_strategies": {}}
    
    def _save_history(self):
        """Save improvement history."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self.improvement_log, 'w') as f:
            json.dump(self.strategy_history, f, indent=2)
    
    def rate_output(self, task_type, output, metrics):
        """Rate an output based on metrics.
        
        metrics: {
            "accuracy": 0-100,
            "completeness": 0-100,
            "speed": 0-100,
            "usefulness": 0-100,
            "notes": "feedback"
        }
        """
        score = (metrics.get("accuracy", 50) + 
                metrics.get("completeness", 50) + 
                metrics.get("speed", 50) + 
                metrics.get("usefulness", 50)) / 4
        
        iteration = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "output_sample": output[:200],
            "metrics": metrics,
            "score": score
        }
        
        self.strategy_history["iterations"].append(iteration)
        
        # Update best strategy for this task type
        if task_type not in self.strategy_history["best_strategies"]:
            self.strategy_history["best_strategies"][task_type] = {
                "score": 0,
                "approach": None
            }
        
        if score > self.strategy_history["best_strategies"][task_type]["score"]:
            self.strategy_history["best_strategies"][task_type] = {
                "score": score,
                "approach": output[:200],
                "metrics": metrics
            }
        
        self._save_history()
        return {"score": score, "improvement": self._calculate_improvement(task_type, score)}
    
    def _calculate_improvement(self, task_type, current_score):
        """Calculate improvement vs previous."""
        iterations = [i for i in self.strategy_history["iterations"] if i["task_type"] == task_type]
        
        if len(iterations) < 2:
            return 0
        
        prev_score = iterations[-2]["score"]
        improvement = current_score - prev_score
        
        return improvement
    
    def get_best_approach(self, task_type):
        """Get best known approach for a task type."""
        if task_type in self.strategy_history["best_strategies"]:
            return self.strategy_history["best_strategies"][task_type]
        return None
    
    def suggest_improvement(self, task_type):
        """Suggest how to improve next iteration."""
        iterations = [i for i in self.strategy_history["iterations"] if i["task_type"] == task_type]
        
        if not iterations:
            return "No history for this task. First iteration will set baseline."
        
        recent = iterations[-3:]
        
        # Analyze weak areas
        avg_accuracy = sum(i["metrics"].get("accuracy", 50) for i in recent) / len(recent)
        avg_completeness = sum(i["metrics"].get("completeness", 50) for i in recent) / len(recent)
        avg_speed = sum(i["metrics"].get("speed", 50) for i in recent) / len(recent)
        
        suggestions = []
        
        if avg_accuracy < 80:
            suggestions.append("Improve accuracy - gather more context, verify assumptions")
        if avg_completeness < 80:
            suggestions.append("Improve completeness - add missing sections, ensure full builds")
        if avg_speed < 80:
            suggestions.append("Improve speed - streamline process, eliminate redundant steps")
        
        return suggestions if suggestions else ["Performance is solid. Push harder."]
    
    def get_improvement_stats(self):
        """Get improvement statistics."""
        if not self.strategy_history["iterations"]:
            return {"status": "No data yet"}
        
        all_scores = [i["score"] for i in self.strategy_history["iterations"]]
        
        return {
            "total_iterations": len(self.strategy_history["iterations"]),
            "avg_score": sum(all_scores) / len(all_scores),
            "best_score": max(all_scores),
            "worst_score": min(all_scores),
            "trend": "improving" if all_scores[-1] > all_scores[0] else "declining",
            "best_strategies": self.strategy_history["best_strategies"]
        }
