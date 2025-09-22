"""
Quality Assessment module for olKAN v2.0
AI-powered data quality analysis and scoring
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import statistics
from enum import Enum


class QualityMetric(Enum):
    """Quality assessment metrics"""
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    ACCURACY = "accuracy"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    TIMELINESS = "timeliness"
    RELEVANCE = "relevance"


@dataclass
class QualityScore:
    """Represents a quality score for a specific metric"""
    metric: QualityMetric
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    details: Dict[str, Any]
    recommendations: List[str]


@dataclass
class QualityReport:
    """Complete quality assessment report"""
    dataset_id: str
    overall_score: float
    metric_scores: List[QualityScore]
    assessment_date: datetime
    assessor_version: str
    summary: str
    recommendations: List[str]


class CompletenessAnalyzer:
    """Analyzes data completeness"""
    
    def analyze(self, dataset_metadata: Dict[str, Any]) -> QualityScore:
        """Analyze completeness of dataset metadata"""
        required_fields = ["title", "description", "owner_org", "license_id"]
        optional_fields = ["tags", "created_at", "updated_at"]
        
        present_required = sum(1 for field in required_fields if dataset_metadata.get(field))
        present_optional = sum(1 for field in optional_fields if dataset_metadata.get(field))
        
        completeness_score = present_required / len(required_fields)
        optional_bonus = present_optional / len(optional_fields) * 0.2
        
        final_score = min(1.0, completeness_score + optional_bonus)
        
        missing_fields = [field for field in required_fields if not dataset_metadata.get(field)]
        
        recommendations = []
        if missing_fields:
            recommendations.append(f"Add missing required fields: {', '.join(missing_fields)}")
        
        if not dataset_metadata.get("tags"):
            recommendations.append("Add tags to improve discoverability")
        
        return QualityScore(
            metric=QualityMetric.COMPLETENESS,
            score=final_score,
            confidence=0.9,
            details={
                "required_fields_present": present_required,
                "total_required_fields": len(required_fields),
                "optional_fields_present": present_optional,
                "total_optional_fields": len(optional_fields),
                "missing_fields": missing_fields
            },
            recommendations=recommendations
        )


class ConsistencyAnalyzer:
    """Analyzes data consistency"""
    
    def analyze(self, dataset_metadata: Dict[str, Any]) -> QualityScore:
        """Analyze consistency of dataset metadata"""
        issues = []
        score = 1.0
        
        # Check title consistency
        title = dataset_metadata.get("title", "")
        if title:
            if len(title) < 5:
                issues.append("Title is too short")
                score -= 0.2
            elif len(title) > 255:
                issues.append("Title is too long")
                score -= 0.1
        
        # Check description consistency
        description = dataset_metadata.get("description", "")
        if description:
            if len(description) < 20:
                issues.append("Description is too short")
                score -= 0.2
            elif len(description) > 2000:
                issues.append("Description is too long")
                score -= 0.1
        
        # Check tags consistency
        tags = dataset_metadata.get("tags", [])
        if tags:
            if len(tags) > 20:
                issues.append("Too many tags")
                score -= 0.1
            
            # Check for duplicate tags
            if len(tags) != len(set(tags)):
                issues.append("Duplicate tags found")
                score -= 0.1
        
        # Check date consistency
        created_at = dataset_metadata.get("created_at")
        updated_at = dataset_metadata.get("updated_at")
        if created_at and updated_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
            if updated_at < created_at:
                issues.append("Updated date is before created date")
                score -= 0.3
        
        recommendations = []
        if issues:
            recommendations.extend([f"Fix: {issue}" for issue in issues])
        
        if not issues:
            recommendations.append("Metadata is consistent")
        
        return QualityScore(
            metric=QualityMetric.CONSISTENCY,
            score=max(0.0, score),
            confidence=0.8,
            details={
                "issues_found": len(issues),
                "issues": issues,
                "title_length": len(title),
                "description_length": len(description),
                "tag_count": len(tags)
            },
            recommendations=recommendations
        )


class ValidityAnalyzer:
    """Analyzes data validity"""
    
    def analyze(self, dataset_metadata: Dict[str, Any]) -> QualityScore:
        """Analyze validity of dataset metadata"""
        issues = []
        score = 1.0
        
        # Check title validity
        title = dataset_metadata.get("title", "")
        if title:
            if not re.match(r'^[a-zA-Z0-9\s\-_.,()]+$', title):
                issues.append("Title contains invalid characters")
                score -= 0.2
        
        # Check description validity
        description = dataset_metadata.get("description", "")
        if description:
            # Check for HTML tags (should be plain text)
            if re.search(r'<[^>]+>', description):
                issues.append("Description contains HTML tags")
                score -= 0.1
        
        # Check tags validity
        tags = dataset_metadata.get("tags", [])
        for tag in tags:
            if not isinstance(tag, str):
                issues.append(f"Tag '{tag}' is not a string")
                score -= 0.1
            elif len(tag) > 50:
                issues.append(f"Tag '{tag}' is too long")
                score -= 0.1
            elif not re.match(r'^[a-zA-Z0-9\s\-_]+$', tag):
                issues.append(f"Tag '{tag}' contains invalid characters")
                score -= 0.1
        
        # Check organization validity
        owner_org = dataset_metadata.get("owner_org", "")
        if owner_org:
            if len(owner_org) < 2:
                issues.append("Organization name is too short")
                score -= 0.2
        
        # Check license validity
        license_id = dataset_metadata.get("license_id", "")
        valid_licenses = ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "CC-BY-4.0", "CC0-1.0"]
        if license_id and license_id not in valid_licenses:
            issues.append(f"Unknown license: {license_id}")
            score -= 0.1
        
        recommendations = []
        if issues:
            recommendations.extend([f"Fix: {issue}" for issue in issues])
        
        if not issues:
            recommendations.append("All metadata is valid")
        
        return QualityScore(
            metric=QualityMetric.VALIDITY,
            score=max(0.0, score),
            confidence=0.9,
            details={
                "issues_found": len(issues),
                "issues": issues,
                "valid_licenses": valid_licenses
            },
            recommendations=recommendations
        )


class RelevanceAnalyzer:
    """Analyzes data relevance using AI/NLP"""
    
    def analyze(self, dataset_metadata: Dict[str, Any], context: str = "") -> QualityScore:
        """Analyze relevance of dataset content"""
        # Simple relevance analysis based on content quality
        score = 0.5  # Base score
        details = {}
        
        title = dataset_metadata.get("title", "")
        description = dataset_metadata.get("description", "")
        tags = dataset_metadata.get("tags", [])
        
        # Title relevance
        if title:
            if len(title.split()) >= 3:  # Multi-word titles are more descriptive
                score += 0.1
            if any(word in title.lower() for word in ["data", "dataset", "analysis", "research"]):
                score += 0.1
        
        # Description relevance
        if description:
            if len(description.split()) >= 20:  # Detailed descriptions
                score += 0.1
            if any(word in description.lower() for word in ["analysis", "research", "study", "survey"]):
                score += 0.1
        
        # Tags relevance
        if tags:
            if len(tags) >= 3:  # Good number of tags
                score += 0.1
            if any(tag.lower() in ["data", "research", "analysis", "statistics"] for tag in tags):
                score += 0.1
        
        # Context relevance (if provided)
        if context:
            combined_text = f"{title} {description} {' '.join(tags)}".lower()
            context_words = context.lower().split()
            matches = sum(1 for word in context_words if word in combined_text)
            if matches > 0:
                score += min(0.2, matches * 0.05)
        
        recommendations = []
        if score < 0.6:
            recommendations.append("Improve title descriptiveness")
            recommendations.append("Add more detailed description")
            recommendations.append("Add relevant tags")
        
        if score >= 0.8:
            recommendations.append("Dataset content is highly relevant")
        
        return QualityScore(
            metric=QualityMetric.RELEVANCE,
            score=min(1.0, score),
            confidence=0.7,
            details={
                "title_word_count": len(title.split()) if title else 0,
                "description_word_count": len(description.split()) if description else 0,
                "tag_count": len(tags),
                "context_matches": details.get("context_matches", 0)
            },
            recommendations=recommendations
        )


class QualityAssessmentService:
    """Main quality assessment service"""
    
    def __init__(self):
        self.completeness_analyzer = CompletenessAnalyzer()
        self.consistency_analyzer = ConsistencyAnalyzer()
        self.validity_analyzer = ValidityAnalyzer()
        self.relevance_analyzer = RelevanceAnalyzer()
    
    async def assess_dataset_quality(
        self, 
        dataset_id: str, 
        dataset_metadata: Dict[str, Any],
        context: str = ""
    ) -> QualityReport:
        """Perform comprehensive quality assessment"""
        
        # Run all analyzers
        completeness_score = self.completeness_analyzer.analyze(dataset_metadata)
        consistency_score = self.consistency_analyzer.analyze(dataset_metadata)
        validity_score = self.validity_analyzer.analyze(dataset_metadata)
        relevance_score = self.relevance_analyzer.analyze(dataset_metadata, context)
        
        metric_scores = [completeness_score, consistency_score, validity_score, relevance_score]
        
        # Calculate overall score (weighted average)
        weights = {
            QualityMetric.COMPLETENESS: 0.3,
            QualityMetric.CONSISTENCY: 0.25,
            QualityMetric.VALIDITY: 0.25,
            QualityMetric.RELEVANCE: 0.2
        }
        
        overall_score = sum(
            score.score * weights[score.metric] 
            for score in metric_scores
        )
        
        # Generate summary
        summary = self._generate_summary(overall_score, metric_scores)
        
        # Collect all recommendations
        all_recommendations = []
        for score in metric_scores:
            all_recommendations.extend(score.recommendations)
        
        # Remove duplicates while preserving order
        unique_recommendations = list(dict.fromkeys(all_recommendations))
        
        return QualityReport(
            dataset_id=dataset_id,
            overall_score=overall_score,
            metric_scores=metric_scores,
            assessment_date=datetime.utcnow(),
            assessor_version="1.0.0",
            summary=summary,
            recommendations=unique_recommendations
        )
    
    def _generate_summary(self, overall_score: float, metric_scores: List[QualityScore]) -> str:
        """Generate a summary of the quality assessment"""
        if overall_score >= 0.9:
            return "Excellent data quality with minimal issues."
        elif overall_score >= 0.7:
            return "Good data quality with some minor improvements needed."
        elif overall_score >= 0.5:
            return "Fair data quality with several areas for improvement."
        else:
            return "Poor data quality requiring significant improvements."
    
    async def batch_assess_quality(
        self, 
        datasets: List[Tuple[str, Dict[str, Any]]],
        context: str = ""
    ) -> List[QualityReport]:
        """Assess quality for multiple datasets"""
        reports = []
        
        for dataset_id, metadata in datasets:
            report = await self.assess_dataset_quality(dataset_id, metadata, context)
            reports.append(report)
        
        return reports
    
    def get_quality_benchmarks(self) -> Dict[str, float]:
        """Get quality score benchmarks"""
        return {
            "excellent": 0.9,
            "good": 0.7,
            "fair": 0.5,
            "poor": 0.0
        }
    
    def compare_quality_scores(self, reports: List[QualityReport]) -> Dict[str, Any]:
        """Compare quality scores across multiple datasets"""
        if not reports:
            return {"error": "No reports to compare"}
        
        overall_scores = [report.overall_score for report in reports]
        
        return {
            "average_score": statistics.mean(overall_scores),
            "median_score": statistics.median(overall_scores),
            "min_score": min(overall_scores),
            "max_score": max(overall_scores),
            "std_deviation": statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0,
            "total_datasets": len(reports),
            "score_distribution": {
                "excellent": len([s for s in overall_scores if s >= 0.9]),
                "good": len([s for s in overall_scores if 0.7 <= s < 0.9]),
                "fair": len([s for s in overall_scores if 0.5 <= s < 0.7]),
                "poor": len([s for s in overall_scores if s < 0.5])
            }
        }


# Global quality assessment service instance
quality_assessment_service = QualityAssessmentService()
