#!/usr/bin/env python3
"""
AEGIS-X Target Classifier
Intelligent target type detection with self-learning capabilities
"""

import re
import os
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class TargetType(Enum):
    WEB = "web"
    MOBILE = "mobile"
    FILE = "file"
    NETWORK = "network"
    CODE = "code"
    UNKNOWN = "unknown"

@dataclass
class ClassificationResult:
    target: str
    target_type: TargetType
    confidence: float
    reasoning: str
    metadata: Dict[str, Any]
    learning_notes: List[str]

class VulnerabilityClassifier:
    """
    Intelligent vulnerability classifier for severity and type classification
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.VulnerabilityClassifier")
        self.severity_patterns = self._load_severity_patterns()
    
    def _load_severity_patterns(self) -> Dict[str, Any]:
        """Load vulnerability severity patterns"""
        return {
            "critical": {
                "keywords": ["remote code execution", "rce", "command injection", "sql injection", "authentication bypass"],
                "cvss_range": (9.0, 10.0)
            },
            "high": {
                "keywords": ["xss", "csrf", "privilege escalation", "path traversal", "file upload"],
                "cvss_range": (7.0, 8.9)
            },
            "medium": {
                "keywords": ["information disclosure", "weak encryption", "session fixation"],
                "cvss_range": (4.0, 6.9)
            },
            "low": {
                "keywords": ["version disclosure", "directory listing", "weak password policy"],
                "cvss_range": (0.1, 3.9)
            }
        }
    
    async def classify_vulnerability(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Classify vulnerability severity and type"""
        title = finding.get("title", "").lower()
        description = finding.get("description", "").lower()
        
        # Default classification
        classification = {
            "severity": "medium",
            "type": "unknown",
            "confidence": 0.5,
            "cvss_score": 5.0,
            "category": "other"
        }
        
        # Check severity patterns
        for severity, patterns in self.severity_patterns.items():
            for keyword in patterns["keywords"]:
                if keyword in title or keyword in description:
                    classification["severity"] = severity
                    classification["cvss_score"] = (patterns["cvss_range"][0] + patterns["cvss_range"][1]) / 2
                    classification["confidence"] = 0.8
                    break
        
        # Determine vulnerability type
        if any(keyword in title or keyword in description for keyword in ["sql", "injection"]):
            classification["type"] = "sql_injection"
            classification["category"] = "injection"
        elif any(keyword in title or keyword in description for keyword in ["xss", "cross-site"]):
            classification["type"] = "xss"
            classification["category"] = "injection"
        elif any(keyword in title or keyword in description for keyword in ["csrf", "cross-site request"]):
            classification["type"] = "csrf"
            classification["category"] = "broken_authentication"
        elif any(keyword in title or keyword in description for keyword in ["rce", "command injection"]):
            classification["type"] = "command_injection"
            classification["category"] = "injection"
        
        return classification

class TargetClassifier:
    """
    Intelligent target classifier that learns from past classifications
    and improves its accuracy over time.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.Classifier")
        self.learning_data = self._load_learning_data()
        self.classification_patterns = self._initialize_patterns()
        
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load learning data from previous classifications"""
        learning_file = Path("learn/classification_history.json")
        
        if learning_file.exists():
            try:
                with open(learning_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load learning data: {e}")
        
        return {
            "classification_history": [],
            "pattern_success_rates": {},
            "improvement_notes": []
        }
    
    def _initialize_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize classification patterns with learning feedback"""
        return {
            "web": [
                {
                    "pattern": r"^https?://",
                    "confidence": 0.9,
                    "description": "HTTP/HTTPS URL"
                },
                {
                    "pattern": r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    "confidence": 0.8,
                    "description": "Domain name"
                },
                {
                    "pattern": r"^\*\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    "confidence": 0.85,
                    "description": "Wildcard domain"
                },
                {
                    "pattern": r"api\.|admin\.|staging\.|dev\.|test\.",
                    "confidence": 0.7,
                    "description": "API or admin subdomain"
                }
            ],
            "mobile": [
                {
                    "pattern": r"play\.google\.com/store/apps",
                    "confidence": 0.95,
                    "description": "Google Play Store URL"
                },
                {
                    "pattern": r"apps\.apple\.com",
                    "confidence": 0.95,
                    "description": "Apple App Store URL"
                },
                {
                    "pattern": r"\.apk$",
                    "confidence": 0.9,
                    "description": "Android APK file"
                },
                {
                    "pattern": r"\.ipa$",
                    "confidence": 0.9,
                    "description": "iOS IPA file"
                },
                {
                    "pattern": r"\.aab$",
                    "confidence": 0.85,
                    "description": "Android App Bundle"
                }
            ],
            "file": [
                {
                    "pattern": r"\.(js|json|xml|yaml|yml|env|config|conf|ini|properties)$",
                    "confidence": 0.8,
                    "description": "Configuration or script file"
                },
                {
                    "pattern": r"\.(pdf|doc|docx|xls|xlsx|ppt|pptx)$",
                    "confidence": 0.7,
                    "description": "Document file"
                },
                {
                    "pattern": r"\.(zip|tar|gz|rar|7z)$",
                    "confidence": 0.75,
                    "description": "Archive file"
                },
                {
                    "pattern": r"^\.\/|^\/",
                    "confidence": 0.6,
                    "description": "Local file path"
                }
            ],
            "network": [
                {
                    "pattern": r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",
                    "confidence": 0.9,
                    "description": "IPv4 address"
                },
                {
                    "pattern": r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$",
                    "confidence": 0.95,
                    "description": "IPv4 CIDR range"
                },
                {
                    "pattern": r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$",
                    "confidence": 0.9,
                    "description": "IPv6 address"
                },
                {
                    "pattern": r":\d{1,5}$",
                    "confidence": 0.6,
                    "description": "Port specification"
                }
            ],
            "code": [
                {
                    "pattern": r"^github:",
                    "confidence": 0.95,
                    "description": "GitHub repository reference"
                },
                {
                    "pattern": r"^gitlab:",
                    "confidence": 0.95,
                    "description": "GitLab repository reference"
                },
                {
                    "pattern": r"^bitbucket:",
                    "confidence": 0.95,
                    "description": "Bitbucket repository reference"
                },
                {
                    "pattern": r"github\.com/",
                    "confidence": 0.9,
                    "description": "GitHub URL"
                },
                {
                    "pattern": r"gitlab\.com/",
                    "confidence": 0.9,
                    "description": "GitLab URL"
                }
            ]
        }
    
    def classify(self, target: str) -> ClassificationResult:
        """
        Classify a target with self-reflection and learning
        """
        self.logger.info(f"🔍 Classifying target: {target}")
        
        # Analyze target against all patterns
        classification_scores = {}
        reasoning_details = []
        
        for target_type, patterns in self.classification_patterns.items():
            max_confidence = 0
            best_match = None
            
            for pattern_info in patterns:
                pattern = pattern_info["pattern"]
                base_confidence = pattern_info["confidence"]
                
                if re.search(pattern, target, re.IGNORECASE):
                    # Apply learning adjustments
                    adjusted_confidence = self._apply_learning_adjustments(
                        target_type, pattern, base_confidence
                    )
                    
                    if adjusted_confidence > max_confidence:
                        max_confidence = adjusted_confidence
                        best_match = pattern_info
            
            if max_confidence > 0:
                classification_scores[target_type] = {
                    "confidence": max_confidence,
                    "pattern": best_match
                }
        
        # Determine best classification
        if not classification_scores:
            result = ClassificationResult(
                target=target,
                target_type=TargetType.UNKNOWN,
                confidence=0.0,
                reasoning="No matching patterns found",
                metadata={},
                learning_notes=["Consider adding new patterns for this target type"]
            )
        else:
            best_type = max(classification_scores.keys(), 
                          key=lambda x: classification_scores[x]["confidence"])
            best_score = classification_scores[best_type]
            
            result = ClassificationResult(
                target=target,
                target_type=TargetType(best_type),
                confidence=best_score["confidence"],
                reasoning=f"Matched pattern: {best_score['pattern']['description']}",
                metadata={
                    "all_scores": classification_scores,
                    "matched_pattern": best_score["pattern"]["pattern"]
                },
                learning_notes=self._generate_learning_notes(target, best_type, classification_scores)
            )
        
        # Log classification with self-reflection
        self._log_classification_with_reflection(result)
        
        # Store for learning
        self._store_classification_for_learning(result)
        
        return result
    
    def _apply_learning_adjustments(self, target_type: str, pattern: str, base_confidence: float) -> float:
        """Apply learning-based adjustments to confidence scores"""
        pattern_key = f"{target_type}:{pattern}"
        
        if pattern_key in self.learning_data.get("pattern_success_rates", {}):
            success_rate = self.learning_data["pattern_success_rates"][pattern_key]
            # Adjust confidence based on historical success rate
            adjustment = (success_rate - 0.5) * 0.2  # Max ±0.1 adjustment
            adjusted_confidence = min(1.0, max(0.0, base_confidence + adjustment))
            
            self.logger.debug(f"Applied learning adjustment: {base_confidence} → {adjusted_confidence}")
            return adjusted_confidence
        
        return base_confidence
    
    def _generate_learning_notes(self, target: str, best_type: str, all_scores: Dict[str, Any]) -> List[str]:
        """Generate learning notes for future improvement"""
        notes = []
        
        # Check for ambiguous classifications
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1]["confidence"], reverse=True)
        if len(sorted_scores) > 1:
            best_confidence = sorted_scores[0][1]["confidence"]
            second_confidence = sorted_scores[1][1]["confidence"]
            
            if best_confidence - second_confidence < 0.2:
                notes.append(f"Ambiguous classification: {sorted_scores[0][0]} ({best_confidence:.2f}) vs {sorted_scores[1][0]} ({second_confidence:.2f})")
        
        # Check for low confidence
        if sorted_scores and sorted_scores[0][1]["confidence"] < 0.7:
            notes.append("Low confidence classification - consider adding more specific patterns")
        
        # Domain-specific learning notes
        if best_type == "web":
            parsed = urlparse(target if target.startswith('http') else f'http://{target}')
            if parsed.path and len(parsed.path) > 1:
                notes.append("Web target has specific path - may indicate API endpoint")
        
        return notes
    
    def _log_classification_with_reflection(self, result: ClassificationResult):
        """Log classification with self-reflection"""
        self.logger.info(f"📝 Target classified as: {result.target_type.value.upper()}")
        self.logger.info(f"🎯 Confidence: {result.confidence:.2f}")
        self.logger.info(f"💭 Reasoning: {result.reasoning}")
        
        # Self-reflection questions
        reflection_questions = [
            "Why did I choose this classification?",
            "What could go wrong with this classification?",
            "What did I learn from similar targets before?",
            "How can I improve this classification in the future?"
        ]
        
        for question in reflection_questions:
            self.logger.debug(f"🤔 Self-reflection: {question}")
        
        # Log learning notes
        for note in result.learning_notes:
            self.logger.info(f"📚 Learning note: {note}")
    
    def _store_classification_for_learning(self, result: ClassificationResult):
        """Store classification result for future learning"""
        classification_entry = {
            "target": result.target,
            "classified_type": result.target_type.value,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            "timestamp": str(datetime.now()),
            "learning_notes": result.learning_notes
        }
        
        self.learning_data["classification_history"].append(classification_entry)
        
        # Save learning data
        learning_file = Path("learn/classification_history.json")
        learning_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(learning_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save learning data: {e}")
    
    def update_pattern_success_rate(self, target: str, target_type: str, pattern: str, success: bool):
        """Update success rate for a specific pattern based on hunt results"""
        pattern_key = f"{target_type}:{pattern}"
        
        if pattern_key not in self.learning_data["pattern_success_rates"]:
            self.learning_data["pattern_success_rates"][pattern_key] = 0.5  # Start neutral
        
        current_rate = self.learning_data["pattern_success_rates"][pattern_key]
        
        # Simple learning rate adjustment
        learning_rate = 0.1
        if success:
            new_rate = current_rate + (1.0 - current_rate) * learning_rate
        else:
            new_rate = current_rate - current_rate * learning_rate
        
        self.learning_data["pattern_success_rates"][pattern_key] = new_rate
        
        self.logger.info(f"📊 Updated pattern success rate: {pattern_key} → {new_rate:.3f}")
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics for analysis"""
        history = self.learning_data.get("classification_history", [])
        
        if not history:
            return {"total_classifications": 0}
        
        type_counts = {}
        confidence_sum = 0
        
        for entry in history:
            target_type = entry["classified_type"]
            type_counts[target_type] = type_counts.get(target_type, 0) + 1
            confidence_sum += entry["confidence"]
        
        return {
            "total_classifications": len(history),
            "type_distribution": type_counts,
            "average_confidence": confidence_sum / len(history),
            "pattern_success_rates": self.learning_data.get("pattern_success_rates", {})
        }
    
    def suggest_new_patterns(self, failed_targets: List[str]) -> List[Dict[str, Any]]:
        """Suggest new patterns based on failed classifications"""
        suggestions = []
        
        for target in failed_targets:
            # Analyze common patterns in failed targets
            if re.search(r'\.onion$', target):
                suggestions.append({
                    "target_type": "web",
                    "pattern": r'\.onion$',
                    "confidence": 0.8,
                    "description": "Tor hidden service",
                    "reasoning": "Dark web target detection"
                })
            
            if re.search(r'docker\.|k8s\.|kubernetes\.', target):
                suggestions.append({
                    "target_type": "network",
                    "pattern": r'docker\.|k8s\.|kubernetes\.',
                    "confidence": 0.75,
                    "description": "Container/orchestration service",
                    "reasoning": "Modern infrastructure target"
                })
        
        return suggestions

# Import datetime at the top of the file
from datetime import datetime