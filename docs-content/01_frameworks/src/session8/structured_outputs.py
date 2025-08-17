# Structured Output and Type Safety for Agno Agents
# Pydantic models and type-safe agent implementations

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from agno import Agent
import json


class MarketAnalysis(BaseModel):
    """Structured output for market analysis"""
    company_name: str = Field(description="Company being analyzed")
    market_cap: Optional[float] = Field(description="Market capitalization in USD")
    key_metrics: List[str] = Field(description="Important financial metrics")
    risk_factors: List[str] = Field(description="Identified risk factors") 
    recommendation: str = Field(description="Investment recommendation")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Analysis confidence")
    analysis_date: datetime = Field(default_factory=datetime.now)


class StructuredAnalystAgent(Agent):
    """Financial analyst agent with structured output"""
    
    def __init__(self):
        super().__init__(
            name="structured_analyst",
            model="gpt-4o",
            response_model=MarketAnalysis,  # Enforce structured output
            instructions="""
            You are a financial analyst. Analyze the given company and 
            return your analysis in the specified structured format.
            Be thorough but concise in your analysis.
            """
        )


class ComplianceReport(BaseModel):
    """Structured output for compliance reports"""
    report_id: str = Field(description="Unique report identifier")
    audit_date: datetime = Field(default_factory=datetime.now)
    compliance_status: str = Field(description="Overall compliance status")
    violations_found: List[str] = Field(description="List of compliance violations")
    recommendations: List[str] = Field(description="Recommended actions")
    risk_level: str = Field(description="Risk level: LOW, MEDIUM, HIGH, CRITICAL")
    next_audit_date: datetime = Field(description="Recommended next audit date")


class ComplianceAgent(Agent):
    """Compliance monitoring agent with structured reporting"""
    
    def __init__(self):
        super().__init__(
            name="compliance_monitor",
            model="gpt-4o",
            response_model=ComplianceReport,
            instructions="""
            You are a compliance officer. Review the provided information
            and generate a comprehensive compliance report in the structured format.
            Focus on regulatory requirements and risk assessment.
            """
        )


class PerformanceMetrics(BaseModel):
    """Structured performance metrics"""
    metric_name: str = Field(description="Name of the performance metric")
    current_value: float = Field(description="Current metric value")
    target_value: float = Field(description="Target metric value")
    variance_percentage: float = Field(description="Variance from target as percentage")
    trend: str = Field(description="Trend direction: IMPROVING, STABLE, DECLINING")
    last_updated: datetime = Field(default_factory=datetime.now)


class PerformanceReport(BaseModel):
    """Structured performance report"""
    report_period: str = Field(description="Reporting period (e.g., Q4 2024)")
    overall_score: float = Field(ge=0.0, le=100.0, description="Overall performance score")
    metrics: List[PerformanceMetrics] = Field(description="Individual performance metrics")
    key_achievements: List[str] = Field(description="Key achievements during period")
    areas_for_improvement: List[str] = Field(description="Areas needing improvement")
    action_items: List[str] = Field(description="Recommended action items")


class PerformanceAnalystAgent(Agent):
    """Performance analysis agent with structured reporting"""
    
    def __init__(self):
        super().__init__(
            name="performance_analyst",
            model="gpt-4o",
            response_model=PerformanceReport,
            instructions="""
            You are a performance analyst. Analyze the provided performance data
            and generate a comprehensive structured report. Include quantitative
            metrics, trends, and actionable recommendations.
            """
        )


# Example usage functions
def demonstrate_structured_analysis():
    """Demonstrate structured market analysis"""
    analyst_agent = StructuredAnalystAgent()
    
    # The response is guaranteed to match MarketAnalysis schema
    analysis = analyst_agent.run("Analyze Tesla's current market position")
    
    # Type-safe access to structured data
    print(f"Company: {analysis.company_name}")
    print(f"Recommendation: {analysis.recommendation}")
    print(f"Confidence: {analysis.confidence_score:.2%}")
    print(f"Risk Factors: {', '.join(analysis.risk_factors)}")
    
    # Structured data can be easily serialized for APIs
    analysis_json = analysis.model_dump_json()
    print(f"JSON Output: {analysis_json}")
    
    return analysis


def demonstrate_compliance_reporting():
    """Demonstrate structured compliance reporting"""
    compliance_agent = ComplianceAgent()
    
    compliance_data = """
    Company: TechCorp Inc.
    Recent Activities: Data processing for EU customers, financial reporting, employee data handling
    Regulations: GDPR, SOX, CCPA
    Last Audit: 6 months ago
    """
    
    report = compliance_agent.run(f"Generate compliance report for: {compliance_data}")
    
    print(f"Compliance Status: {report.compliance_status}")
    print(f"Risk Level: {report.risk_level}")
    print(f"Violations Found: {len(report.violations_found)}")
    
    return report


def demonstrate_performance_analysis():
    """Demonstrate structured performance analysis"""
    performance_agent = PerformanceAnalystAgent()
    
    performance_data = """
    Q4 2024 Performance Data:
    - Revenue: $2.5M (Target: $2.8M)
    - Customer Satisfaction: 4.2/5 (Target: 4.5/5)
    - System Uptime: 99.5% (Target: 99.9%)
    - Response Time: 150ms (Target: 100ms)
    - Team Productivity: 85% (Target: 90%)
    """
    
    report = performance_agent.run(f"Analyze performance data: {performance_data}")
    
    print(f"Overall Score: {report.overall_score}/100")
    print(f"Number of Metrics: {len(report.metrics)}")
    print(f"Key Achievements: {len(report.key_achievements)}")
    
    return report


# Utility functions for working with structured data
def export_to_json(structured_data: BaseModel, filename: str):
    """Export structured data to JSON file"""
    with open(filename, 'w') as f:
        f.write(structured_data.model_dump_json(indent=2))
    print(f"Data exported to {filename}")


def validate_structured_response(response_data: dict, model_class: BaseModel):
    """Validate response data against Pydantic model"""
    try:
        validated_data = model_class(**response_data)
        return True, validated_data
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    print("=== Structured Output Demonstrations ===")
    
    # Demonstrate market analysis
    print("\n1. Market Analysis:")
    market_analysis = demonstrate_structured_analysis()
    
    # Demonstrate compliance reporting
    print("\n2. Compliance Reporting:")
    compliance_report = demonstrate_compliance_reporting()
    
    # Demonstrate performance analysis
    print("\n3. Performance Analysis:")
    performance_report = demonstrate_performance_analysis()
    
    # Export examples
    export_to_json(market_analysis, "market_analysis.json")
    export_to_json(compliance_report, "compliance_report.json")
    export_to_json(performance_report, "performance_report.json")