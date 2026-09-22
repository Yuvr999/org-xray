import re
from typing import Tuple, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from app.models.demand import RoutingMethod


# Seed training dataset for ML Classifier Scaffold
SEED_TRAINING_DATA = [
    # Technical
    ("Request for 5 high-performance Linux GPU servers for AI training", "Technical"),
    ("Purchase Macbook Pro laptops for the engineering department", "Technical"),
    ("AWS cloud infrastructure monthly billing upgrade", "Technical"),
    ("Software subscription renewal for JetBrains and GitHub Copilot", "Technical"),
    ("Network router replacement and optical fiber cables", "Technical"),
    ("Database storage expansion on PostgreSQL cluster", "Technical"),
    ("Monitor and peripheral accessories for developers", "Technical"),
    
    # Finance
    ("External audit services for Q3 compliance report", "Finance"),
    ("Tax advisory retainer and GST audit consulting fee", "Finance"),
    ("Payroll management software license annual payment", "Finance"),
    ("Accounting system data migration and ledger audit", "Finance"),
    ("Financial reporting tool subscription for finance team", "Finance"),
    ("Corporate banking gateway integration charges", "Finance"),
    
    # PR
    ("Public relations agency retainer fee for product launch", "PR"),
    ("Press release distribution and media event sponsorship", "PR"),
    ("Marketing campaign banner printing and event booth", "PR"),
    ("Brand ambassador promotion and ad placement", "PR"),
    ("Social media advertising budget allocation Q4", "PR"),
    ("Conference sponsorship and company promotional swag", "PR"),
]


class DemandRoutingPipeline:
    def __init__(self, confidence_threshold: float = 0.75):
        self.confidence_threshold = confidence_threshold
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
        self.model = LogisticRegression(C=1.0, max_iter=200)
        self._is_trained = False
        self._train_ml_scaffold()

    def _train_ml_scaffold(self):
        texts = [item[0] for item in SEED_TRAINING_DATA]
        labels = [item[1] for item in SEED_TRAINING_DATA]
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)
        self._is_trained = True

    def classify_rule(self, text: str) -> Tuple[str, float]:
        text_lower = text.lower()
        
        tech_keywords = [
            "server", "laptop", "software", "license", "cloud", "aws", "hardware", 
            "macbook", "gpu", "monitor", "cpu", "network", "router", "database", "dev", "tech"
        ]
        finance_keywords = [
            "audit", "payroll", "tax", "accounting", "consulting", "financial", "budget", "billing", "ledger", "bank"
        ]
        pr_keywords = [
            "campaign", "press", "event", "booth", "media", "branding", "sponsorship", "ad", "advertising", "pr", "marketing"
        ]
        
        tech_score = sum(1 for k in tech_keywords if k in text_lower)
        fin_score = sum(1 for k in finance_keywords if k in text_lower)
        pr_score = sum(1 for k in pr_keywords if k in text_lower)
        
        scores = {"Technical": tech_score, "Finance": fin_score, "PR": pr_score}
        max_dept = max(scores, key=scores.get)
        max_score = scores[max_dept]
        
        if max_score > 0:
            confidence = min(0.60 + (max_score * 0.15), 0.95)
            return max_dept, confidence
        
        return "General", 0.50

    def classify_ml(self, text: str) -> Tuple[str, float]:
        if not self._is_trained:
            return self.classify_rule(text)
            
        X = self.vectorizer.transform([text])
        probs = self.model.predict_proba(X)[0]
        max_idx = probs.argmax()
        predicted_class = self.model.classes_[max_idx]
        confidence = float(probs[max_idx])
        
        return str(predicted_class), confidence

    def route_demand(self, title: str, description: str) -> Dict[str, Any]:
        combined_text = f"{title} {description}"
        
        # 1. Attempt ML Classification
        ml_dept, ml_conf = self.classify_ml(combined_text)
        
        if ml_conf >= self.confidence_threshold:
            return {
                "routed_department": ml_dept,
                "confidence": round(ml_conf, 4),
                "method": RoutingMethod.ML,
                "explanation": f"Classified by ML classifier model with high confidence ({ml_conf:.2%})."
            }
            
        # 2. Fallback to Rule-based Classifier if ML confidence below threshold
        rule_dept, rule_conf = self.classify_rule(combined_text)
        
        if rule_dept != "General":
            return {
                "routed_department": rule_dept,
                "confidence": round(rule_conf, 4),
                "method": RoutingMethod.RULE,
                "explanation": f"ML confidence ({ml_conf:.2%}) was below threshold {self.confidence_threshold}. Routed via deterministic keyword rules."
            }
            
        # 3. Flag for Human / General Review
        return {
            "routed_department": "General",
            "confidence": 0.50,
            "method": RoutingMethod.HUMAN,
            "explanation": f"Low classification confidence ({ml_conf:.2%}). Marked for manual human review and assignment."
        }


routing_pipeline = DemandRoutingPipeline()
