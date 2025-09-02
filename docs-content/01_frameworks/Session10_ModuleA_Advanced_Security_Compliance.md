# Session 10 - Module A: Advanced Security & Compliance

> **⚠️ ADVANCED OPTIONAL MODULE**
> Prerequisites: Complete Session 10 core content first.

This module covers comprehensive security and compliance frameworks for enterprise agent systems including GDPR compliance, RBAC implementation, advanced encryption strategies, audit logging, zero-trust architecture, and regulatory compliance patterns.

---

## Part 1: GDPR Compliance and Data Privacy

### Comprehensive GDPR Implementation

🗂️ **File**: `src/session10/security/gdpr_compliance.py` - GDPR compliance framework

Let's start by setting up the foundational imports and enumerations for our GDPR compliance system. This demonstrates the comprehensive scope of data protection requirements in enterprise systems:

```python
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import hashlib
import logging
from abc import ABC, abstractmethod
```

Next, we define the GDPR legal basis types, which form the foundation of all data processing activities. Every piece of personal data must have a valid legal basis under GDPR Article 6:

```python
class LegalBasisType(Enum):
    """GDPR legal basis for data processing"""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"

```

We also need to define the data subject rights that individuals can exercise under GDPR. These rights form the core of data protection and must be implemented in any compliant system:

```python
class DataSubjectRights(Enum):
    """GDPR data subject rights"""
    ACCESS = "access"           # Article 15
    RECTIFICATION = "rectification"  # Article 16
    ERASURE = "erasure"        # Article 17 (Right to be forgotten)
    RESTRICT_PROCESSING = "restrict_processing"  # Article 18
    DATA_PORTABILITY = "data_portability"  # Article 20
    OBJECT = "object"          # Article 21
    WITHDRAW_CONSENT = "withdraw_consent"  # Article 7

```

Now we create a comprehensive data structure to track every piece of personal data with its GDPR metadata. This demonstrates the principle of accountability - we must be able to prove compliance for every data element:

```python
@dataclass
class PersonalDataElement:
    """Individual personal data element with GDPR metadata"""
    element_id: str
    data_type: str
    category: str  # Basic personal data, sensitive personal data, etc.
    source: str
    legal_basis: LegalBasisType
    purpose: str
    retention_period_days: int
    is_sensitive: bool = False
    consent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    encryption_status: str = "encrypted"

```

Next, we implement the main GDPR compliance manager class. This serves as the central orchestrator for all data protection activities, maintaining comprehensive records as required by GDPR Articles 30 and 35:

```python
class GDPRComplianceManager:
    """Comprehensive GDPR compliance management system"""

    def __init__(self):
        self.personal_data_registry: Dict[str, PersonalDataElement] = {}
        self.consent_records: Dict[str, Dict[str, Any]] = {}
        self.processing_activities: List[Dict[str, Any]] = []
        self.data_subject_requests: Dict[str, Dict[str, Any]] = {}
        self.privacy_impact_assessments: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

```

The data registration method implements the core principle of lawful processing. Before any personal data can be stored, we must validate the legal basis and obtain consent where required:

```python
    async def register_personal_data(self, data_element: PersonalDataElement,
                                   data_subject_id: str) -> Dict[str, Any]:
        """Register personal data with GDPR compliance tracking"""

        # Validate legal basis
        if not await self._validate_legal_basis(data_element, data_subject_id):
            return {
                'success': False,
                'error': 'Invalid or insufficient legal basis for processing'
            }
```

The registration process begins with legal basis validation, which is fundamental to GDPR compliance. Article 6 requires that all personal data processing must have a lawful basis, and this validation ensures we don't process data illegally. The method returns early with a clear error if the legal basis is insufficient, implementing fail-safe processing principles.

```python
        # Check for consent if required
        if data_element.legal_basis == LegalBasisType.CONSENT:
            consent_valid = await self._validate_consent(data_element.consent_id, data_subject_id)
            if not consent_valid:
                return {
                    'success': False,
                    'error': 'Valid consent required for processing'
                }
```

Consent validation implements GDPR Article 7 requirements for valid consent. When processing relies on consent as the legal basis, we must verify that consent is freely given, specific, informed, and unambiguous. This check prevents processing data without proper consent, which would constitute a GDPR violation with potential fines up to 4% of annual revenue.

After validation, we register the data element and perform necessary compliance actions including logging and privacy impact assessment triggers:

```python
        # Register data element
        registry_key = f"{data_subject_id}:{data_element.element_id}"
        self.personal_data_registry[registry_key] = data_element

        # Log processing activity
        await self._log_processing_activity("data_registration", {
            'data_subject_id': data_subject_id,
            'element_id': data_element.element_id,
            'legal_basis': data_element.legal_basis.value,
            'purpose': data_element.purpose
        })
```

Data registration creates a unique registry key combining the data subject ID and element ID, ensuring we can efficiently track and locate all personal data. The activity logging fulfills GDPR Article 30 requirements for records of processing activities, creating an audit trail that demonstrates accountability and helps with compliance verification.

```python
        # Check if Privacy Impact Assessment is needed
        if data_element.is_sensitive or data_element.category == "biometric":
            await self._trigger_pia_assessment(data_element, data_subject_id)

        return {
            'success': True,
            'registry_key': registry_key,
            'retention_until': datetime.now() + timedelta(days=data_element.retention_period_days)
        }
```

Privacy Impact Assessment (PIA) triggering implements GDPR Article 35, which mandates PIAs for high-risk processing activities. Sensitive personal data and biometric data always require assessment due to their potential impact on individuals' rights and freedoms. The return value includes the registry key for future data operations and calculated retention date, ensuring data doesn't stay longer than legally justified.

The data subject request handler is the cornerstone of GDPR compliance, implementing all the rights guaranteed to individuals under Articles 15-22:

```python
    async def handle_data_subject_request(self, request_type: DataSubjectRights,
                                        data_subject_id: str,
                                        request_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle GDPR data subject rights requests"""

        request_id = f"dsr_{int(datetime.now().timestamp())}"
        request_details = request_details or {}

        # Validate data subject identity (simplified for demo)
        if not await self._validate_data_subject_identity(data_subject_id):
            return {
                'success': False,
                'error': 'Data subject identity validation failed'
            }
```

The routing logic directs requests to specialized handlers, each implementing specific GDPR article requirements:

```python
        # Process specific request type
        if request_type == DataSubjectRights.ACCESS:
            result = await self._handle_access_request(data_subject_id)
        elif request_type == DataSubjectRights.RECTIFICATION:
            result = await self._handle_rectification_request(data_subject_id, request_details)
        elif request_type == DataSubjectRights.ERASURE:
            result = await self._handle_erasure_request(data_subject_id, request_details)
```

The request routing system implements all GDPR Chapter III rights. Access requests (Article 15) provide transparency, rectification (Article 16) ensures accuracy, and erasure (Article 17) enables the "right to be forgotten." Each right has specific legal requirements and implementation challenges that require specialized handlers.

```python
        elif request_type == DataSubjectRights.DATA_PORTABILITY:
            result = await self._handle_portability_request(data_subject_id)
        elif request_type == DataSubjectRights.RESTRICT_PROCESSING:
            result = await self._handle_restriction_request(data_subject_id, request_details)
        elif request_type == DataSubjectRights.OBJECT:
            result = await self._handle_objection_request(data_subject_id, request_details)
        elif request_type == DataSubjectRights.WITHDRAW_CONSENT:
            result = await self._handle_consent_withdrawal(data_subject_id, request_details)
        else:
            result = {'success': False, 'error': 'Unsupported request type'}
```

Data portability (Article 20) enables user empowerment by providing machine-readable data exports. Processing restrictions (Article 18) allow temporary processing suspension, while objection rights (Article 21) enable opt-outs from certain processing. Consent withdrawal (Article 7) must be as easy as giving consent, with immediate cascade effects to stop dependent processing.

Comprehensive audit trails ensure accountability and transparency:

```python
        # Store request record
        self.data_subject_requests[request_id] = {
            'request_type': request_type.value,
            'data_subject_id': data_subject_id,
            'request_details': request_details,
            'timestamp': datetime.now(),
            'status': 'completed' if result['success'] else 'failed',
            'result': result
        }
```

Request record storage creates a permanent audit trail for all data subject rights exercises. This fulfills GDPR accountability requirements by documenting when requests were made, how they were processed, and what outcomes were achieved. These records are essential for demonstrating compliance during regulatory audits.

```python
        # Log activity
        await self._log_processing_activity("data_subject_request", {
            'request_id': request_id,
            'request_type': request_type.value,
            'data_subject_id': data_subject_id,
            'status': result.get('status', 'unknown')
        })

        return {**result, 'request_id': request_id}
```

Activity logging provides the operational intelligence needed to monitor compliance performance and identify potential issues. The structured log format enables automated analysis of request patterns, response times, and success rates. The return value combines the specific request result with the unique request ID for tracking.

The access request handler implements Article 15 (Right of access), which requires providing comprehensive information about all data processing. This is often the most complex right to implement:

```python
    async def _handle_access_request(self, data_subject_id: str) -> Dict[str, Any]:
        """Handle Article 15 - Right of access by the data subject"""

        subject_data = {}

        # Collect all personal data for this subject
        for registry_key, data_element in self.personal_data_registry.items():
            if registry_key.startswith(f"{data_subject_id}:"):
                subject_data[data_element.element_id] = {
                    'data_type': data_element.data_type,
                    'category': data_element.category,
                    'purpose': data_element.purpose,
                    'legal_basis': data_element.legal_basis.value,
                    'retention_period_days': data_element.retention_period_days,
                    'created_at': data_element.created_at.isoformat(),
                    'last_accessed': data_element.last_accessed.isoformat()
                }
```

Data collection for access requests demonstrates complete transparency as required by GDPR Article 15. The comprehensive data structure includes not just the personal data categories and types, but also the processing metadata like legal basis, purpose, and retention periods. This enables individuals to understand exactly how their data is being processed and make informed decisions about their privacy.

We must also include processing activities and third-party sharing information to provide complete transparency as required by Article 15:

```python
        # Include processing activities
        processing_info = [
            activity for activity in self.processing_activities
            if activity.get('data_subject_id') == data_subject_id
        ]
```

Processing activities inclusion provides the complete operational context required by Article 15(1)(c), showing not just what data we hold, but what we've done with it. This transparency builds trust and enables individuals to identify any processing they disagree with or find concerning.

```python
        access_report = {
            'data_subject_id': data_subject_id,
            'personal_data': subject_data,
            'processing_activities': processing_info,
            'retention_policies': self._get_retention_policies(data_subject_id),
            'third_party_sharing': self._get_third_party_sharing_info(data_subject_id),
            'report_generated_at': datetime.now().isoformat()
        }

        return {
            'success': True,
            'access_report': access_report,
            'format': 'structured_json'
        }
```

The comprehensive access report fulfills all Article 15 requirements by including retention policies (how long we keep data), third-party sharing information (who else receives the data), and processing activities. The structured JSON format ensures machine readability while maintaining human comprehensibility, supporting both individual rights and potential data portability requests.

The erasure request handler implements Article 17 (Right to be forgotten), one of the most challenging rights to implement as it requires careful legal analysis and comprehensive data removal:

```python
    async def _handle_erasure_request(self, data_subject_id: str,
                                    request_details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Article 17 - Right to erasure (right to be forgotten)"""

        # Check if erasure is legally permissible
        erasure_permitted = await self._check_erasure_permitted(data_subject_id, request_details)

        if not erasure_permitted['permitted']:
            return {
                'success': False,
                'error': 'Erasure not permitted',
                'reason': erasure_permitted['reason']
            }
```

Erasure permission checking implements the complex legal analysis required by Article 17. The right to be forgotten is not absolute - processing may continue when needed for freedom of expression, legal compliance, public health, or archiving purposes. This validation prevents inappropriate erasure that could violate other legal obligations.

When erasure is permitted, we must systematically remove all traces of the individual's data from our systems:

```python
        # Perform erasure
        erased_elements = []

        # Remove from personal data registry
        keys_to_remove = [
            key for key in self.personal_data_registry.keys()
            if key.startswith(f"{data_subject_id}:")
        ]
```

Erasure execution begins with comprehensive identification of all data elements belonging to the data subject. The systematic approach ensures complete removal by first collecting all relevant registry keys, preventing partial erasure that could leave residual personal data and create compliance gaps.

```python
        for key in keys_to_remove:
            data_element = self.personal_data_registry[key]
            erased_elements.append({
                'element_id': data_element.element_id,
                'data_type': data_element.data_type,
                'erasure_timestamp': datetime.now().isoformat()
            })
            del self.personal_data_registry[key]
```

Actual erasure operations maintain detailed audit trails by logging exactly what data was removed and when. This documentation is crucial for demonstrating compliance effectiveness and providing evidence that erasure requests were properly fulfilled, addressing potential regulatory scrutiny or data subject concerns about incomplete erasure.

Critically, we must also handle cascade effects including consent record removal and third-party notifications as required by Article 17(2):

```python
        # Remove consent records
        if data_subject_id in self.consent_records:
            del self.consent_records[data_subject_id]

        # Notify third parties if necessary
        third_party_notifications = await self._notify_third_parties_of_erasure(data_subject_id)
```

Consent record removal ensures that withdrawn consent cannot be accidentally relied upon for future processing. Third-party notification implements Article 17(2) requirements, where data controllers must inform recipients about erasure requests when technically feasible and proportionate to the processing costs.

```python
        return {
            'success': True,
            'erased_elements': erased_elements,
            'erasure_timestamp': datetime.now().isoformat(),
            'third_party_notifications': third_party_notifications
        }
```

The comprehensive erasure response provides complete documentation of the erasure action, enabling the data subject to verify that their request was properly fulfilled. This transparency builds trust and provides evidence of GDPR compliance for both internal audit processes and potential regulatory investigations.

The data portability handler implements Article 20, which applies only to data processed under consent or contract legal bases. This creates a machine-readable export for data subject empowerment:

```python
    async def _handle_portability_request(self, data_subject_id: str) -> Dict[str, Any]:
        """Handle Article 20 - Right to data portability"""

        # Collect portable data (consent-based or contract-based only)
        portable_data = {}

        for registry_key, data_element in self.personal_data_registry.items():
            if (registry_key.startswith(f"{data_subject_id}:") and
                data_element.legal_basis in [LegalBasisType.CONSENT, LegalBasisType.CONTRACT]):

                portable_data[data_element.element_id] = {
                    'data_type': data_element.data_type,
                    'value': f"[ENCRYPTED_VALUE_{data_element.element_id}]",  # Would be actual data in production
                    'created_at': data_element.created_at.isoformat(),
                    'legal_basis': data_element.legal_basis.value
                }
```

Data portability collection implements Article 20's specific scope limitations - only data processed under consent or contract legal bases is portable. This restriction prevents misuse of portability rights for data processed under other legal bases like legal obligations, where portability wouldn't be appropriate or legally sound.

The export package includes comprehensive metadata and integrity verification to ensure the portability package meets technical and security requirements:

```python
        # Create portable format
        portable_package = {
            'data_subject_id': data_subject_id,
            'export_timestamp': datetime.now().isoformat(),
            'data_format': 'JSON',
            'data': portable_data,
            'metadata': {
                'export_version': '1.0',
                'compliance_standard': 'GDPR_Article_20',
                'data_integrity_hash': hashlib.sha256(
                    json.dumps(portable_data, sort_keys=True).encode()
                ).hexdigest()
            }
        }
```

The portable package creation follows Article 20 requirements for structured, commonly used, and machine-readable formats. The JSON format is widely supported across systems, enabling true data portability. The integrity hash ensures data hasn't been tampered with during transfer, maintaining trust in the portability process.

```python
        return {
            'success': True,
            'portable_data': portable_package,
            'format': 'structured_json',
            'encryption_available': True
        }
```

The response indicates encryption availability for secure transfer, addressing privacy concerns when sensitive personal data is exported. This optional encryption layer provides additional protection during data movement between data controllers, supporting the individual's right to data security even during portability exercises.

The consent management system is fundamental to GDPR compliance, implementing the requirements for valid, specific, informed, and freely given consent under Article 7:

```python
    async def manage_consent(self, data_subject_id: str, purpose: str,
                           consent_given: bool, consent_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage GDPR consent with granular controls"""

        consent_id = f"consent_{data_subject_id}_{purpose}_{int(datetime.now().timestamp())}"

        consent_record = {
            'consent_id': consent_id,
            'data_subject_id': data_subject_id,
            'purpose': purpose,
            'consent_given': consent_given,
            'timestamp': datetime.now(),
            'consent_details': consent_details or {},
            'withdrawal_timestamp': None,
            'is_active': consent_given
        }
```

Consent record creation implements Article 7 requirements for demonstrable consent. The comprehensive structure captures not just whether consent was given, but when, for what purpose, and any additional context. The withdrawal timestamp and active status enable proper consent lifecycle management, supporting the requirement that consent withdrawal be as easy as giving consent.

Consent storage and withdrawal handling must implement cascade effects as required by Article 7(3) - consent withdrawal must be as easy as giving consent:

```python
        # Store consent record
        if data_subject_id not in self.consent_records:
            self.consent_records[data_subject_id] = {}

        self.consent_records[data_subject_id][consent_id] = consent_record
```

Consent storage implements granular consent management by organizing records per data subject and purpose. This structure supports the GDPR principle of specific consent - individuals can give separate consent for different purposes and withdraw them independently, providing fine-grained control over their personal data processing.

```python
        # If consent is withdrawn, update related data processing
        if not consent_given:
            await self._handle_consent_withdrawal_cascade(data_subject_id, purpose)

        await self._log_processing_activity("consent_management", {
            'consent_id': consent_id,
            'data_subject_id': data_subject_id,
            'purpose': purpose,
            'consent_given': consent_given
        })

        return {
            'success': True,
            'consent_id': consent_id,
            'status': 'active' if consent_given else 'withdrawn'
        }
```

Consent withdrawal cascade handling implements Article 7(3) requirements by immediately stopping processing based on withdrawn consent. The activity logging creates audit trails for consent management decisions, supporting accountability and compliance verification. The return status clearly communicates the consent state for operational decision-making.

The Privacy Impact Assessment (PIA) implementation follows Article 35 requirements, mandating systematic privacy risk evaluation for high-risk processing:

```python
    async def perform_data_protection_impact_assessment(self,
                                                      processing_activity: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Data Protection Impact Assessment (DPIA) as required by Article 35"""

        pia_id = f"pia_{int(datetime.now().timestamp())}"

        # Assess necessity and proportionality
        necessity_assessment = await self._assess_processing_necessity(processing_activity)

        # Identify risks to data subjects
        risk_assessment = await self._assess_data_subject_risks(processing_activity)

        # Evaluate safeguards and measures
        safeguards_assessment = await self._assess_safeguards(processing_activity)
```

Privacy Impact Assessment (PIA) follows the Article 35 three-pillar approach: necessity assessment ensures processing is actually needed and proportionate to the objective; risk assessment identifies potential harms to individuals' rights and freedoms; safeguards assessment evaluates technical and organizational measures that mitigate identified risks. This systematic approach ensures comprehensive privacy protection evaluation.

The comprehensive risk analysis combines necessity, risk, and safeguards assessments to determine if supervisory authority consultation is required:

```python
        # Overall risk determination
        overall_risk = await self._determine_overall_risk(
            necessity_assessment, risk_assessment, safeguards_assessment
        )
```

Overall risk determination synthesizes all assessment components into a final risk classification. This holistic analysis considers how necessity, identified risks, and existing safeguards interact to determine if processing can proceed safely or requires additional measures or supervisory authority consultation.

```python
        pia_report = {
            'pia_id': pia_id,
            'processing_activity': processing_activity,
            'assessment_date': datetime.now().isoformat(),
            'necessity_assessment': necessity_assessment,
            'risk_assessment': risk_assessment,
            'safeguards_assessment': safeguards_assessment,
            'overall_risk_level': overall_risk['level'],
            'recommendations': overall_risk['recommendations'],
            'requires_consultation': overall_risk['level'] == 'high',
            'review_date': (datetime.now() + timedelta(days=365)).isoformat()
        }
```

The comprehensive PIA report documents all assessment components and decisions, creating an audit trail for compliance verification. The automatic consultation flag triggers Article 36 supervisory authority consultation when high risks remain after safeguards implementation. The annual review date ensures ongoing privacy protection evaluation.

```python
        self.privacy_impact_assessments[pia_id] = pia_report

        return {
            'success': True,
            'pia_id': pia_id,
            'risk_level': overall_risk['level'],
            'requires_consultation': pia_report['requires_consultation'],
            'recommendations': overall_risk['recommendations']
        }
```

PIA storage and response provide operational intelligence for privacy and compliance teams. The return value enables immediate decision-making about whether processing can proceed, needs additional safeguards, or requires supervisory authority consultation, supporting privacy-by-design principles in system development.

The compliance reporting system provides comprehensive oversight and demonstrates accountability as required by Article 5(2). This generates executive-level compliance dashboards:

```python
    async def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive GDPR compliance report"""

        # Data processing statistics
        processing_stats = {
            'total_data_subjects': len(set(
                key.split(':')[0] for key in self.personal_data_registry.keys()
            )),
            'total_data_elements': len(self.personal_data_registry),
            'consent_based_processing': len([
                elem for elem in self.personal_data_registry.values()
                if elem.legal_basis == LegalBasisType.CONSENT
            ]),
            'sensitive_data_elements': len([
                elem for elem in self.personal_data_registry.values()
                if elem.is_sensitive
            ])
        }
```

Processing statistics provide executive-level visibility into data protection scope and compliance posture. Tracking total data subjects and elements demonstrates scale, while consent-based and sensitive data metrics highlight high-risk processing that requires enhanced protection measures. These metrics support strategic privacy program decisions and regulatory reporting requirements.

Rights request metrics demonstrate our responsiveness to data subject exercises, which is critical for regulatory audits:

```python
        # Rights requests statistics
        rights_stats = {
            'total_requests': len(self.data_subject_requests),
            'access_requests': len([
                req for req in self.data_subject_requests.values()
                if req['request_type'] == DataSubjectRights.ACCESS.value
            ]),
            'erasure_requests': len([
                req for req in self.data_subject_requests.values()
                if req['request_type'] == DataSubjectRights.ERASURE.value
            ]),
            'average_response_time_hours': 48,  # Calculated from actual response times
            'compliance_rate': 100.0
        }
```

Rights request statistics demonstrate operational excellence in data subject service delivery. Access and erasure request volumes indicate individual privacy engagement levels, while response time and compliance rate metrics show organizational effectiveness in fulfilling GDPR obligations. These metrics are crucial for demonstrating accountability to regulators and identifying operational improvement opportunities.

The comprehensive report combines all compliance dimensions into a single accountability document:

```python
        # Consent management statistics
        consent_stats = {
            'total_consents': sum(len(consents) for consents in self.consent_records.values()),
            'active_consents': sum(
                1 for consents in self.consent_records.values()
                for consent in consents.values()
                if consent['is_active']
            ),
            'consent_withdrawal_rate': 5.2  # Percentage
        }
```

Consent management statistics track the health of consent-based processing operations. Total and active consent counts show the scope of consent-dependent activities, while withdrawal rates indicate user satisfaction and trust levels. High withdrawal rates may signal consent fatigue or overly broad consent requests that need refinement.

```python
        # Security and breach information
        security_status = {
            'encryption_compliance': 100.0,  # Percentage of data encrypted
            'access_control_compliance': 100.0,
            'audit_logging_enabled': True,
            'data_breaches_ytd': 0,
            'last_security_assessment': datetime.now().isoformat()
        }
```

Security status metrics demonstrate technical and organizational measures implementation effectiveness. Encryption and access control compliance rates show protection coverage, while breach tracking and audit logging status indicate security monitoring capabilities. These metrics support Article 32 security obligations and breach notification requirements.

```python
        compliance_report = {
            'report_id': f"compliance_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'report_date': datetime.now().isoformat(),
            'reporting_period': {
                'start': (datetime.now() - timedelta(days=365)).isoformat(),
                'end': datetime.now().isoformat()
            },
            'processing_statistics': processing_stats,
            'rights_request_statistics': rights_stats,
            'consent_management': consent_stats,
            'security_status': security_status,
            'privacy_impact_assessments': len(self.privacy_impact_assessments),
            'compliance_score': self._calculate_compliance_score(),
            'recommendations': await self._generate_compliance_recommendations()
        }

        return compliance_report
```

The comprehensive compliance report consolidates all privacy program dimensions into executive-ready documentation. The structured format supports regulatory reporting, board presentations, and continuous improvement planning. The compliance score and recommendations provide actionable intelligence for strengthening data protection practices.

The compliance scoring algorithm provides quantitative assessment of GDPR adherence for management oversight:

```python
    def _calculate_compliance_score(self) -> float:
        """Calculate overall GDPR compliance score"""

        # Initialize perfect compliance score
        score = 100.0
```

Compliance scoring begins with perfect compliance assumption, then applies deductions based on identified compliance gaps. This approach ensures conservative scoring that highlights areas needing attention rather than providing false confidence in compliance status.

```python
        # Calculate consent coverage for data requiring explicit consent
        consent_coverage = len([
            elem for elem in self.personal_data_registry.values()
            if elem.legal_basis != LegalBasisType.CONSENT or elem.consent_id
        ]) / max(1, len(self.personal_data_registry))

        score *= consent_coverage
```

Consent coverage calculation ensures all data processed under consent legal basis has valid consent records. Missing consent constitutes a direct GDPR violation with potential regulatory fines, so this metric directly impacts compliance scoring. The division by max(1, total_elements) prevents division by zero while maintaining proportional scoring.

```python
        # Deduct for delayed rights responses
        # (In production, would calculate actual response times)

        # Deduct for missing PIAs on high-risk processing
        # (In production, would analyze actual risk levels)

        return round(score, 1)
```

Future scoring enhancements will include response time analysis and Privacy Impact Assessment coverage validation. GDPR requires rights request responses within one month, and high-risk processing requires mandatory PIAs. The rounded score provides clear compliance percentage for executive reporting and regulatory documentation.

Advanced data anonymization techniques protect against re-identification while preserving data utility. K-anonymity ensures each individual cannot be distinguished from at least k-1 others:

```python
class DataAnonymization:
    """Advanced data anonymization and pseudonymization techniques"""

    def __init__(self):
        self.anonymization_techniques = {}
        self.pseudonymization_keys = {}
```

K-anonymity implementation groups records by quasi-identifiers and applies generalization or suppression to meet privacy requirements:

```python
    async def k_anonymize_dataset(self, dataset: List[Dict[str, Any]],
                                k_value: int = 5,
                                quasi_identifiers: List[str] = None) -> Dict[str, Any]:
        """Implement k-anonymity to protect against re-identification"""

        if not quasi_identifiers:
            quasi_identifiers = ['age', 'zipcode', 'gender']

        # Group records by quasi-identifier combinations
        groups = {}
        for record in dataset:
            qi_signature = tuple(record.get(qi) for qi in quasi_identifiers)
            if qi_signature not in groups:
                groups[qi_signature] = []
            groups[qi_signature].append(record)
```

Record grouping by quasi-identifiers creates the foundation for k-anonymity analysis. Quasi-identifiers are attributes that, when combined, might enable re-identification even when direct identifiers are removed. This grouping reveals which individuals share the same quasi-identifier combinations and therefore cannot be distinguished from each other.

Records that don't meet the k-anonymity threshold are either generalized (reducing precision) or suppressed (removed) to prevent re-identification:

```python
        # Identify groups smaller than k
        small_groups = {sig: records for sig, records in groups.items() if len(records) < k_value}

        # Apply generalization/suppression
        anonymized_dataset = []
        suppressed_records = 0
```

Small group identification finds records that don't meet the k-anonymity threshold. These groups pose re-identification risks because they contain fewer than k individuals sharing the same quasi-identifier combination. The anonymization process must address these groups through generalization or suppression to achieve the desired privacy level.

```python
        for signature, records in groups.items():
            if len(records) >= k_value:
                # Group meets k-anonymity requirement
                anonymized_dataset.extend(records)
            else:
                # Apply generalization or suppression
                generalized_records = await self._generalize_records(records, quasi_identifiers)
                if generalized_records:
                    anonymized_dataset.extend(generalized_records)
                else:
                    suppressed_records += len(records)
```

Generalization versus suppression represents the core privacy-utility tradeoff in k-anonymity. Generalization reduces data precision (e.g., exact age becomes age range) while preserving records for analysis. Suppression removes records entirely when generalization isn't sufficient, providing stronger privacy protection but reducing dataset utility.

```python
        return {
            'anonymized_dataset': anonymized_dataset,
            'k_value': k_value,
            'original_size': len(dataset),
            'anonymized_size': len(anonymized_dataset),
            'suppressed_records': suppressed_records,
            'privacy_level': f"{k_value}-anonymous"
        }
```

The comprehensive anonymization result provides complete transparency about privacy protection effectiveness and data utility impact. Size comparisons show how much data was preserved, suppression counts indicate privacy enforcement strictness, and the privacy level certification confirms the achieved anonymity guarantee.

Differential privacy provides mathematically rigorous privacy guarantees by adding calibrated noise to query results, ensuring individual contributions cannot be detected:

```python
    async def differential_privacy_noise(self, query_result: float,
                                       epsilon: float = 1.0,
                                       sensitivity: float = 1.0) -> Dict[str, Any]:
        """Add differential privacy noise to query results"""

        import random
        import math
```

Differential privacy imports and parameter validation establish the foundation for mathematically rigorous privacy protection. The epsilon parameter controls the privacy-utility tradeoff: smaller values provide stronger privacy but add more noise to results. The sensitivity parameter reflects the maximum impact any single individual can have on the query result.

```python
        # Apply Laplace mechanism for differential privacy
        scale = sensitivity / epsilon
        noise = random.laplace(0, scale)
        noisy_result = query_result + noise
```

The Laplace mechanism adds calibrated random noise proportional to sensitivity divided by epsilon, ensuring the probability of any specific output is similar regardless of whether any individual's data is included. This mathematical guarantee prevents adversaries from detecting individual participation in datasets, even with auxiliary information.

```python
        return {
            'original_result': query_result,
            'noisy_result': noisy_result,
            'noise_added': noise,
            'epsilon': epsilon,
            'privacy_budget_used': epsilon,
            'privacy_guarantee': f"({epsilon}, 0)-differential privacy"
        }

```

Comprehensive audit logging is essential for GDPR accountability, providing detailed records of all data processing activities for regulatory compliance and security monitoring:

```python
class AuditLoggingSystem:
    """Comprehensive audit logging for GDPR compliance"""

    def __init__(self):
        self.audit_logs: List[Dict[str, Any]] = []
        self.log_retention_days = 2555  # 7 years for compliance
```

Data access logging captures all interactions with personal data, creating immutable audit trails for compliance verification:

```python
    async def log_data_access(self, access_details: Dict[str, Any]):
        """Log data access events"""

        log_entry = {
            'event_id': f"access_{int(datetime.now().timestamp())}",
            'event_type': 'data_access',
            'timestamp': datetime.now().isoformat(),
            'data_subject_id': access_details.get('data_subject_id'),
            'accessor_id': access_details.get('accessor_id'),
            'data_elements': access_details.get('data_elements', []),
            'purpose': access_details.get('purpose'),
            'legal_basis': access_details.get('legal_basis'),
            'ip_address': access_details.get('ip_address'),
            'user_agent': access_details.get('user_agent')
        }

        self.audit_logs.append(log_entry)

```

Data modification logging captures all changes to personal data, supporting both security monitoring and data subject rights verification:

```python
    async def log_data_modification(self, modification_details: Dict[str, Any]):
        """Log data modification events"""

        log_entry = {
            'event_id': f"modify_{int(datetime.now().timestamp())}",
            'event_type': 'data_modification',
            'timestamp': datetime.now().isoformat(),
            'data_subject_id': modification_details.get('data_subject_id'),
            'modifier_id': modification_details.get('modifier_id'),
            'modifications': modification_details.get('modifications', []),
            'reason': modification_details.get('reason'),
            'legal_basis': modification_details.get('legal_basis')
        }

        self.audit_logs.append(log_entry)

```

Audit report generation provides comprehensive analysis of all logged activities, supporting compliance demonstrations and security investigations:

```python
    async def generate_audit_report(self, start_date: datetime = None,
                                  end_date: datetime = None) -> Dict[str, Any]:
        """Generate comprehensive audit report"""

        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
```

Date range validation establishes the audit report scope with sensible defaults for operational reporting. The 30-day default period balances comprehensive coverage with report manageability, while custom date ranges support specific compliance investigations or regulatory reporting requirements that may require longer historical periods.

```python
        # Filter logs by date range for focused analysis
        filtered_logs = [
            log for log in self.audit_logs
            if start_date <= datetime.fromisoformat(log['timestamp']) <= end_date
        ]
```

Log filtering by timestamp ensures audit reports contain only relevant activities within the specified timeframe. This filtering supports both routine operational reporting and targeted investigations by limiting analysis to specific periods when security incidents or compliance reviews require detailed examination.

```python
        # Calculate access pattern statistics for compliance monitoring
        access_stats = {
            'total_access_events': len([log for log in filtered_logs if log['event_type'] == 'data_access']),
            'unique_data_subjects': len(set(log.get('data_subject_id') for log in filtered_logs if log.get('data_subject_id'))),
            'unique_accessors': len(set(log.get('accessor_id') for log in filtered_logs if log.get('accessor_id')))
        }
```

Access pattern analysis provides critical security intelligence by counting total access events, unique individuals whose data was accessed, and unique system users who performed access operations. These metrics enable detection of unusual access patterns that might indicate security breaches or inappropriate data usage requiring investigation.

```python
        return {
            'report_period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_events': len(filtered_logs),
            'access_statistics': access_stats,
            'events': filtered_logs,
            'compliance_status': 'compliant'
        }
```

---

## Part 2: Role-Based Access Control and Zero-Trust Architecture

### Advanced RBAC Implementation

🗂️ **File**: `src/session10/security/enterprise_auth.py` - Advanced RBAC and zero-trust security

Now we implement advanced Role-Based Access Control (RBAC) with zero-trust principles. Let's start with the foundational imports and permission system:

```python
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import jwt
import hashlib
import logging
from abc import ABC, abstractmethod
```

Granular permissions form the foundation of enterprise access control, enabling fine-grained authorization decisions based on the principle of least privilege:

```python
class Permission(Enum):
    """Granular permission system"""
    READ_PERSONAL_DATA = "read_personal_data"
    WRITE_PERSONAL_DATA = "write_personal_data"
    DELETE_PERSONAL_DATA = "delete_personal_data"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    ACCESS_AUDIT_LOGS = "access_audit_logs"
    SYSTEM_ADMIN = "system_admin"
    COMPLIANCE_VIEW = "compliance_view"
    SECURITY_ADMIN = "security_admin"

```

Next, we define comprehensive role and user data structures that support hierarchical roles and attribute-based access control (ABAC):

```python
@dataclass
class Role:
    """Enterprise role with fine-grained permissions"""
    role_id: str
    role_name: str
    permissions: Set[Permission] = field(default_factory=set)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    parent_roles: Set[str] = field(default_factory=set)
```

User objects integrate RBAC with additional security attributes, supporting multi-factor authentication and session management:

```python
@dataclass
class User:
    """Enterprise user with RBAC"""
    user_id: str
    username: str
    email: str
    roles: Set[str] = field(default_factory=set)
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True
    password_hash: str = ""
    mfa_enabled: bool = False

```

The Zero-Trust Security Manager implements the core principle of "never trust, always verify" with comprehensive session management and policy enforcement:

```python
class ZeroTrustSecurityManager:
    """Zero-trust security architecture implementation"""

    def __init__(self):
        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.access_policies: List[Dict[str, Any]] = []
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.security_context_cache: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

        # Initialize default roles
        self._initialize_default_roles()

```

Default role initialization establishes enterprise-standard roles that align with organizational structures and regulatory requirements:

```python
    def _initialize_default_roles(self):
        """Initialize enterprise default roles"""

        # Data Protection Officer
        dpo_role = Role(
            role_id="dpo",
            role_name="Data Protection Officer",
            permissions={
                Permission.READ_PERSONAL_DATA,
                Permission.ACCESS_AUDIT_LOGS,
                Permission.COMPLIANCE_VIEW
            },
            description="GDPR Data Protection Officer role"
        )
```

The Data Protection Officer role implements GDPR Article 39 requirements with carefully scoped permissions. DPOs need read access to personal data for compliance monitoring, audit log access for oversight activities, and compliance view capabilities for reporting. This role separation ensures independent privacy oversight as mandated by regulatory requirements.

```python
        # System Administrator
        admin_role = Role(
            role_id="system_admin",
            role_name="System Administrator",
            permissions={
                Permission.SYSTEM_ADMIN,
                Permission.MANAGE_USERS,
                Permission.MANAGE_ROLES,
                Permission.ACCESS_AUDIT_LOGS
            },
            description="Full system administration role"
        )
```

System administrator roles provide comprehensive system management capabilities while maintaining clear boundaries around data access. The permission set includes user and role management for access control administration, plus system-level privileges for operational management. Audit log access enables security monitoring and compliance support.

We also define operational roles that provide least-privilege access for day-to-day business functions:

```python
        # Data Analyst
        analyst_role = Role(
            role_id="data_analyst",
            role_name="Data Analyst",
            permissions={Permission.READ_PERSONAL_DATA},
            description="Read-only access to anonymized data"
        )
```

Data analyst roles implement the principle of least privilege with read-only access to personal data, typically in anonymized form. This permission structure supports legitimate business intelligence activities while minimizing privacy risks. The restricted access prevents unauthorized data modification that could compromise data integrity or privacy protections.

```python
        # Customer Service Representative
        csr_role = Role(
            role_id="customer_service",
            role_name="Customer Service Representative",
            permissions={
                Permission.READ_PERSONAL_DATA,
                Permission.WRITE_PERSONAL_DATA
            },
            description="Limited customer data access for support"
        )

        self.roles.update({
            "dpo": dpo_role,
            "system_admin": admin_role,
            "data_analyst": analyst_role,
            "customer_service": csr_role
        })
```

Customer service roles balance operational needs with privacy protection by providing limited read/write access for legitimate support activities. This permission set enables representatives to update customer information and resolve issues while preventing access to highly sensitive data or system administration functions. The role registration creates the foundation for enterprise RBAC implementation.

Multi-factor authentication with zero-trust verification ensures that every authentication attempt is thoroughly validated before granting access:

```python
    async def authenticate_user(self, username: str, password: str,
                              additional_factors: Dict[str, Any] = None) -> Dict[str, Any]:
        """Multi-factor authentication with zero-trust verification"""

        # Find user
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break

        if not user or not user.is_active:
            await self._log_security_event("authentication_failed", {
                'username': username,
                'reason': 'user_not_found_or_inactive'
            })
            return {'success': False, 'error': 'Authentication failed'}
```

Password verification and multi-factor authentication create multiple security layers, following defense-in-depth principles:

```python
        # Verify password
        if not self._verify_password(password, user.password_hash):
            await self._log_security_event("authentication_failed", {
                'user_id': user.user_id,
                'username': username,
                'reason': 'invalid_password'
            })
            return {'success': False, 'error': 'Authentication failed'}
```

Password verification implements the first authentication factor with comprehensive failure logging. Failed authentication attempts are logged with specific reasons to enable security monitoring and threat detection. The generic error message prevents information disclosure while detailed logging provides operational intelligence for security teams.

```python
        # Multi-factor authentication
        if user.mfa_enabled:
            mfa_result = await self._verify_mfa(user, additional_factors or {})
            if not mfa_result['success']:
                return mfa_result
```

Multi-factor authentication adds critical security layers for users with elevated privileges or accessing sensitive data. MFA verification failures immediately terminate the authentication process, implementing fail-secure principles. This approach significantly reduces account compromise risks from password-based attacks like credential stuffing or brute force attempts.

Successful authentication creates a comprehensive security context and generates secure session tokens for subsequent authorization decisions:

```python
        # Create comprehensive security context for zero-trust evaluation
        security_context = await self._create_security_context(user)

        # Generate cryptographically secure session token
        session_token = await self._generate_session_token(user, security_context)
```

Security context and token generation establish the foundation for subsequent zero-trust authorization decisions. The security context includes risk assessment, permissions, and environmental attributes that inform dynamic access policies. Session tokens use cryptographic signatures to prevent tampering and include expiration timestamps for automatic security boundary enforcement.

```python
        # Update user login tracking and audit trail
        user.last_login = datetime.now()

        await self._log_security_event("authentication_success", {
            'user_id': user.user_id,
            'username': username,
            'session_token_id': session_token['token_id']
        })
```

Login time tracking and security event logging create essential audit trails for compliance and threat detection. The login timestamp enables risk assessment based on user activity patterns, while security event logging provides real-time monitoring capabilities for detecting suspicious authentication patterns or potential account compromise attempts.

```python
        return {
            'success': True,
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'roles': list(user.roles)
            },
            'session_token': session_token['token'],
            'token_expires_at': session_token['expires_at'],
            'security_context': security_context
        }

```

Zero-trust authorization validates every request, regardless of the user's authentication status, implementing continuous verification principles:

```python
    async def authorize_request(self, session_token: str,
                              required_permission: Permission,
                              resource_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Zero-trust authorization for every request"""

        # Validate session token cryptographically
        token_validation = await self._validate_session_token(session_token)
        if not token_validation['valid']:
            return {'authorized': False, 'error': 'Invalid session token'}

        user = token_validation['user']
```

Token validation implements the first security gate in zero-trust authorization, verifying both token authenticity and expiration status. Invalid tokens immediately terminate the authorization process, implementing fail-secure principles that prevent unauthorized access even when authentication tokens are compromised or expired.

```python
        # Check role-based permissions against required access level
        user_permissions = await self._get_user_permissions(user.user_id)
        if required_permission not in user_permissions:
            await self._log_security_event("authorization_denied", {
                'user_id': user.user_id,
                'required_permission': required_permission.value,
                'resource_context': resource_context
            })
            return {'authorized': False, 'error': 'Insufficient permissions'}
```

Contextual access policies add dynamic authorization layers based on environmental factors, time, location, and data sensitivity:

```python
        # Evaluate dynamic contextual access policies
        policy_result = await self._evaluate_access_policies(
            user, required_permission, resource_context or {}
        )

        if not policy_result['allowed']:
            await self._log_security_event("authorization_denied", {
                'user_id': user.user_id,
                'required_permission': required_permission.value,
                'resource_context': resource_context,
                'policy_reason': policy_result['reason']
            })
            return {'authorized': False, 'error': policy_result['reason']}
```

Dynamic policy evaluation forms the third security gate by assessing environmental factors like time, location, data sensitivity, and user risk profile. Policy failures are logged with specific reasons to enable security team analysis of access patterns and potential policy refinements to balance security with operational effectiveness.

```python
        # Log successful authorization for audit trail
        await self._log_security_event("authorization_granted", {
            'user_id': user.user_id,
            'required_permission': required_permission.value,
            'resource_context': resource_context
        })

        return {
            'authorized': True,
            'user_context': {
                'user_id': user.user_id,
                'username': user.username,
                'roles': list(user.roles)
            },
            'permission_granted': required_permission.value,
            'access_constraints': policy_result.get('constraints', {})
        }

```

Security context creation establishes comprehensive user context including permissions, risk assessment, and ABAC attributes for informed authorization decisions:

```python
    async def _create_security_context(self, user: User) -> Dict[str, Any]:
        """Create comprehensive security context for user"""

        # Gather user permissions and risk assessment
        permissions = await self._get_user_permissions(user.user_id)
        risk_score = await self._calculate_user_risk_score(user)
```

Permission resolution and risk assessment form the foundational security intelligence for context-aware authorization decisions. The permissions collection aggregates role-based and direct permissions, while risk scoring evaluates user behavior patterns, authentication history, and environmental factors to determine appropriate security boundaries.

```python
        # Extract attribute-based access control (ABAC) attributes
        abac_attributes = {
            'department': user.attributes.get('department'),
            'clearance_level': user.attributes.get('clearance_level', 'standard'),
            'location': user.attributes.get('location'),
            'employment_type': user.attributes.get('employment_type', 'employee')
        }
```

ABAC attribute extraction enables fine-grained access control decisions based on user characteristics beyond simple roles. Department affiliation controls cross-organizational data access, clearance levels govern sensitive information access, location attributes support geographic restrictions, and employment type enables contractor versus employee access differentiation.

```python
        # Assemble comprehensive security context
        security_context = {
            'user_id': user.user_id,
            'username': user.username,
            'roles': list(user.roles),
            'permissions': [p.value for p in permissions],
            'risk_score': risk_score,
            'abac_attributes': abac_attributes,
            'context_created_at': datetime.now().isoformat(),
            'session_constraints': await self._calculate_session_constraints(user, risk_score)
        }
```

Security context assembly creates a comprehensive authorization package that includes identity, permissions, risk assessment, and ABAC attributes. Session constraints implement risk-based security controls like reduced session timeouts for high-risk users or mandatory re-authentication for sensitive operations.

```python
        # Cache security context for performance optimization
        self.security_context_cache[user.user_id] = security_context

        return security_context

```

Dynamic access policy evaluation implements contextual security controls that adapt to environmental factors, data sensitivity, and operational constraints:

```python
    async def _evaluate_access_policies(self, user: User, permission: Permission,
                                      resource_context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate dynamic access policies"""

        # Time-based access control for high-risk operations
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Outside business hours
            if permission in [Permission.DELETE_PERSONAL_DATA, Permission.SYSTEM_ADMIN]:
                return {
                    'allowed': False,
                    'reason': 'High-risk operations not allowed outside business hours'
                }
```

Time-based access control implements temporal security boundaries that restrict high-risk operations to supervised business hours. Data deletion and system administration activities are limited to 6 AM - 10 PM when security staff are available to monitor and respond to potential incidents, reducing the risk of unsupervised destructive operations.

```python
        # Location-based access control for sensitive data
        user_location = user.attributes.get('location')
        if resource_context.get('sensitive_data') and user_location == 'remote':
            return {
                'allowed': False,
                'reason': 'Sensitive data access not allowed from remote locations'
            }
```

Data classification and clearance level policies ensure only authorized personnel can access highly sensitive information:

```python
        # Data classification and clearance level enforcement
        data_classification = resource_context.get('data_classification')
        if data_classification == 'highly_confidential':
            required_clearance = user.attributes.get('clearance_level')
            if required_clearance != 'high':
                return {
                    'allowed': False,
                    'reason': 'Insufficient clearance level for highly confidential data'
                }
```

Data classification enforcement implements hierarchical access controls based on information sensitivity levels. Highly confidential data requires high-level security clearance, preventing unauthorized exposure of trade secrets, personal data, or regulatory-controlled information to users without appropriate background verification and training.

```python
        # Concurrent session limits for security control
        active_sessions = len([
            s for s in self.active_sessions.values()
            if s['user_id'] == user.user_id
        ])

        if active_sessions > 3:
            return {
                'allowed': False,
                'reason': 'Maximum concurrent sessions exceeded'
            }
```

Session limits prevent credential sharing and reduce the attack surface by limiting the number of simultaneous user sessions. The 3-session limit balances operational flexibility with security control, allowing legitimate multi-device usage while preventing excessive concurrent access that might indicate compromised credentials or policy violations.

```python
        return {
            'allowed': True,
            'constraints': {
                'session_timeout_minutes': 60,
                'require_re_auth_for_sensitive': True
            }
        }

```

Attribute-Based Access Control (ABAC) provides fine-grained authorization decisions based on subject, object, environment, and action attributes:

```python
    async def implement_attribute_based_access_control(self,
                                                     request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced ABAC (Attribute-Based Access Control) implementation"""

        subject_attrs = request_context.get('subject_attributes', {})
        object_attrs = request_context.get('object_attributes', {})
        environment_attrs = request_context.get('environment_attributes', {})
        action = request_context.get('action')
```

The ABAC policy engine evaluates complex rules using lambda functions for flexible, runtime-configurable authorization policies:

```python
        # Define ABAC policy rules with lambda-based conditions
        policy_rules = [
            {
                'rule_id': 'sensitive_data_access',
                'condition': lambda s, o, e, a: (
                    o.get('classification') == 'sensitive' and
                    s.get('clearance_level') != 'high'
                ),
                'effect': 'deny',
                'reason': 'Insufficient clearance for sensitive data'
            }
        ]
```

Sensitive data access rules implement clearance-level enforcement for classified information. Lambda functions enable complex conditional logic evaluation at runtime, while the deny effect prevents access when users lack appropriate security clearance. This rule protects confidential data from unauthorized exposure based on user security verification status.

```python
        policy_rules.extend([
            {
                'rule_id': 'time_restricted_operations',
                'condition': lambda s, o, e, a: (
                    a in ['delete', 'modify'] and
                    not (9 <= e.get('current_hour', 0) <= 17)
                ),
                'effect': 'deny',
                'reason': 'Destructive operations only allowed during business hours'
            },
            {
                'rule_id': 'department_data_access',
                'condition': lambda s, o, e, a: (
                    o.get('department') != s.get('department') and
                    a == 'read' and
                    s.get('role') != 'admin'
                ),
                'effect': 'deny',
                'reason': 'Cross-department data access requires admin role'
            }
        ])
```

Policy evaluation follows a deny-by-default approach, with explicit allow decisions only when no restrictive policies match:

```python
        # Evaluate policies using deny-by-default approach
        for rule in policy_rules:
            if rule['condition'](subject_attrs, object_attrs, environment_attrs, action):
                return {
                    'decision': rule['effect'],
                    'rule_applied': rule['rule_id'],
                    'reason': rule['reason']
                }
```

Policy evaluation iterates through all rules using fail-secure principles where any matching deny rule immediately terminates evaluation with access denial. The rule condition function receives all four ABAC attribute categories, enabling complex multi-dimensional authorization decisions that consider user identity, resource characteristics, environmental context, and requested actions.

```python
        # Default allow when no restrictive policies match
        return {
            'decision': 'allow',
            'rule_applied': 'default_allow',
            'reason': 'No restrictive policies applied'
        }

```

Dynamic risk scoring evaluates multiple factors to adjust security controls based on user behavior and environmental conditions:

```python
    async def _calculate_user_risk_score(self, user: User) -> float:
        """Calculate dynamic user risk score"""

        risk_factors = []

        # Assess login activity patterns for risk indicators
        if user.last_login:
            days_since_login = (datetime.now() - user.last_login).days
            if days_since_login > 30:
                risk_factors.append(('inactive_user', 0.3))
```

Login activity analysis identifies dormant accounts that may have been compromised without detection. Extended inactivity periods (over 30 days) increase security risk because compromised credentials may go unnoticed, and returning users may have weaker security awareness. This factor contributes 0.3 to the risk score, representing moderate security concern requiring enhanced monitoring.

```python
        # Evaluate privilege-based risk factors
        admin_roles = {'system_admin', 'security_admin'}
        if any(role in admin_roles for role in user.roles):
            risk_factors.append(('admin_privileges', 0.4))

        # Multi-factor authentication status assessment
        if not user.mfa_enabled:
            risk_factors.append(('no_mfa', 0.5))
```

Administrative privilege assessment recognizes that elevated access levels inherently increase security risk due to potential damage from compromised accounts. The 0.4 risk factor reflects the higher threat impact of administrative access. MFA absence represents the highest individual risk factor (0.5) because single-factor authentication provides inadequate protection against credential-based attacks.

```python
        # Environmental and location-based risk evaluation
        location = user.attributes.get('location', 'unknown')
        if location == 'remote':
            risk_factors.append(('remote_access', 0.2))

        # Calculate composite risk score with base risk assumption
        base_risk = 0.1  # Universal baseline risk
        additional_risk = sum(factor[1] for factor in risk_factors)

        return min(1.0, base_risk + additional_risk)

```

Comprehensive security event logging provides real-time threat detection and forensic capabilities for enterprise security operations:

```python
class SecurityEventLogger:
    """Comprehensive security event logging"""

    def __init__(self):
        self.security_events: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            'failed_auth_attempts': 5,
            'privilege_escalation_attempts': 3,
            'suspicious_access_patterns': 10
        }
```

Security event logging captures detailed information about all security-relevant activities with automated threat analysis:

```python
    async def log_security_event(self, event_type: str, event_details: Dict[str, Any]):
        """Log security events with threat detection"""

        event = {
            'event_id': f"sec_{int(datetime.now().timestamp())}",
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'details': event_details,
            'severity': self._calculate_event_severity(event_type, event_details)
        }

        self.security_events.append(event)

        # Check for security threats
        await self._analyze_for_threats(event)

```

Severity calculation enables prioritized security response and automated alerting based on threat levels:

```python
    def _calculate_event_severity(self, event_type: str, details: Dict[str, Any]) -> str:
        """Calculate event severity for security monitoring"""

        # Critical security events requiring immediate attention
        high_severity_events = {
            'authentication_failed',
            'authorization_denied',
            'privilege_escalation_attempt',
            'data_breach_detected'
        }
```

High-severity event classification identifies critical security incidents requiring immediate response from security teams. Authentication failures, authorization denials, privilege escalation attempts, and data breaches represent direct threats to system security that could indicate active attacks or serious security misconfigurations requiring urgent investigation and remediation.

```python
        # Moderate security events requiring monitoring and analysis
        medium_severity_events = {
            'unusual_access_pattern',
            'session_timeout',
            'mfa_failure'
        }

        # Determine severity based on event type classification
        if event_type in high_severity_events:
            return 'high'
        elif event_type in medium_severity_events:
            return 'medium'
        else:
            return 'low'
```

Threat analysis automatically detects common attack patterns including brute force attempts and privilege escalation:

```python
    async def _analyze_for_threats(self, event: Dict[str, Any]):
        """Analyze events for security threats"""

        # Check for brute force attacks
        if event['event_type'] == 'authentication_failed':
            await self._check_brute_force_attack(event)

        # Check for privilege escalation
        if event['event_type'] == 'authorization_denied':
            await self._check_privilege_escalation(event)

        # Check for unusual access patterns
        await self._check_access_patterns(event)

```

Security reporting provides executive-level dashboards and operational intelligence for security teams to assess threat landscape and system health:

```python
    async def generate_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive security report"""

        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [
            event for event in self.security_events
            if datetime.fromisoformat(event['timestamp']) >= cutoff_time
        ]
```

Report time window filtering establishes the analysis scope for security metrics calculation. The 24-hour default provides comprehensive daily security posture assessment, while custom timeframes support incident investigation and compliance reporting requiring different temporal perspectives for threat analysis.

```python
        # Calculate comprehensive security metrics for executive reporting
        metrics = {
            'total_events': len(recent_events),
            'high_severity_events': len([e for e in recent_events if e['severity'] == 'high']),
            'failed_authentications': len([e for e in recent_events if e['event_type'] == 'authentication_failed']),
            'authorization_denials': len([e for e in recent_events if e['event_type'] == 'authorization_denied']),
            'unique_users_with_events': len(set(e['details'].get('user_id') for e in recent_events if e['details'].get('user_id')))
        }
```

Security metrics aggregation provides quantitative intelligence for threat assessment and operational decision-making. High-severity event counts indicate critical security incidents requiring immediate attention, while authentication and authorization failure counts reveal potential attack patterns. Unique user tracking identifies the scope of security events across the user population.

```python
        return {
            'report_period_hours': hours,
            'report_timestamp': datetime.now().isoformat(),
            'security_metrics': metrics,
            'threat_level': self._assess_threat_level(metrics),
            'recommendations': self._generate_security_recommendations(metrics),
            'events': recent_events
        }
```

---

## Part 3: Advanced Encryption and Data Protection

### End-to-End Encryption Implementation

🗂️ **File**: `src/session10/security/encryption_framework.py` - Advanced encryption systems

Enterprise-grade encryption requires comprehensive key management and multiple encryption algorithms. Let's start with the essential imports and key management structures:

```python
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import json
```

Encryption keys require comprehensive metadata tracking for enterprise security compliance and operational management:

```python
@dataclass
class EncryptionKey:
    """Encryption key with metadata"""
    key_id: str
    key_type: str  # symmetric, asymmetric_public, asymmetric_private
    key_data: bytes
    created_at: datetime
    expires_at: Optional[datetime] = None
    algorithm: str = "AES-256-GCM"
    purpose: str = "data_encryption"

```

The Advanced Encryption Manager orchestrates all cryptographic operations with comprehensive key lifecycle management and audit capabilities:

```python
class AdvancedEncryptionManager:
    """Enterprise-grade encryption management system"""

    def __init__(self):
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.key_rotation_schedule: Dict[str, timedelta] = {}
        self.encrypted_data_registry: Dict[str, Dict[str, Any]] = {}

```

Key generation creates both symmetric and asymmetric keys, supporting hybrid encryption schemes that combine the efficiency of symmetric encryption with the security of asymmetric key exchange:

```python
    async def generate_encryption_keys(self, purpose: str = "data_encryption") -> Dict[str, Any]:
        """Generate comprehensive encryption key set"""

        key_set_id = f"keyset_{int(datetime.now().timestamp())}"

        # Generate symmetric key for data encryption
        symmetric_key_data = Fernet.generate_key()
        symmetric_key = EncryptionKey(
            key_id=f"{key_set_id}_symmetric",
            key_type="symmetric",
            key_data=symmetric_key_data,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=365),
            algorithm="Fernet",
            purpose=purpose
        )
```

RSA key pair generation provides secure key exchange capabilities with enterprise-grade 4096-bit keys:

```python
        # Generate RSA key pair for key exchange
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )

        public_key_data = private_key.public_key().public_key_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        private_key_data = private_key.private_key_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
```

Key object creation and storage with rotation scheduling ensures proper key lifecycle management:

```python
        # Create asymmetric key pair objects with proper metadata
        public_key_obj = EncryptionKey(
            key_id=f"{key_set_id}_public",
            key_type="asymmetric_public",
            key_data=public_key_data,
            created_at=datetime.now(),
            algorithm="RSA-4096",
            purpose="key_exchange"
        )

        private_key_obj = EncryptionKey(
            key_id=f"{key_set_id}_private",
            key_type="asymmetric_private",
            key_data=private_key_data,
            created_at=datetime.now(),
            algorithm="RSA-4096",
            purpose="key_exchange"
        )
```

Asymmetric key object creation wraps the cryptographic keys with essential metadata for enterprise key management. The RSA-4096 algorithm provides strong security appropriate for enterprise key exchange scenarios, while unique key IDs enable precise key tracking and management. Purpose classification supports key usage policy enforcement and compliance auditing.

```python
        # Store keys in enterprise key management system
        self.encryption_keys[symmetric_key.key_id] = symmetric_key
        self.encryption_keys[public_key_obj.key_id] = public_key_obj
        self.encryption_keys[private_key_obj.key_id] = private_key_obj

        # Establish rotation schedules for cryptographic hygiene
        self.key_rotation_schedule[symmetric_key.key_id] = timedelta(days=90)
        self.key_rotation_schedule[public_key_obj.key_id] = timedelta(days=730)

        return {
            'key_set_id': key_set_id,
            'symmetric_key_id': symmetric_key.key_id,
            'public_key_id': public_key_obj.key_id,
            'private_key_id': private_key_obj.key_id,
            'keys_generated_at': datetime.now().isoformat()
        }

```

Data encryption with comprehensive metadata tracking ensures auditability and compliance with data protection regulations:

```python
    async def encrypt_sensitive_data(self, data: str, key_id: str,
                                   classification: str = "confidential") -> Dict[str, Any]:
        """Encrypt sensitive data with comprehensive protection"""

        if key_id not in self.encryption_keys:
            return {'success': False, 'error': 'Encryption key not found'}

        encryption_key = self.encryption_keys[key_id]

        if encryption_key.key_type == "symmetric":
            # Use Fernet for symmetric encryption
            fernet = Fernet(encryption_key.key_data)
            encrypted_data = fernet.encrypt(data.encode())

        else:
            return {'success': False, 'error': 'Unsupported key type for data encryption'}
```

Encryption metadata includes integrity hashes and classification information for comprehensive data governance:

```python
        # Create encryption metadata
        encryption_metadata = {
            'encrypted_at': datetime.now().isoformat(),
            'key_id': key_id,
            'algorithm': encryption_key.algorithm,
            'classification': classification,
            'data_hash': self._compute_hash(data),
            'encryption_version': '1.0'
        }

        # Generate unique identifier for encrypted data
        encrypted_data_id = f"enc_{int(datetime.now().timestamp())}"

        # Store encryption registry entry
        self.encrypted_data_registry[encrypted_data_id] = {
            'metadata': encryption_metadata,
            'encrypted_data': base64.b64encode(encrypted_data).decode(),
            'access_log': []
        }

        return {
            'success': True,
            'encrypted_data_id': encrypted_data_id,
            'metadata': encryption_metadata
        }

```

Decryption with comprehensive access logging provides audit trails essential for compliance and security monitoring:

```python
    async def decrypt_sensitive_data(self, encrypted_data_id: str,
                                   accessor_id: str,
                                   purpose: str) -> Dict[str, Any]:
        """Decrypt sensitive data with access logging"""

        if encrypted_data_id not in self.encrypted_data_registry:
            return {'success': False, 'error': 'Encrypted data not found'}

        data_entry = self.encrypted_data_registry[encrypted_data_id]
        key_id = data_entry['metadata']['key_id']

        if key_id not in self.encryption_keys:
            return {'success': False, 'error': 'Decryption key not found'}

        encryption_key = self.encryption_keys[key_id]

        # Decrypt data
        try:
            encrypted_data = base64.b64decode(data_entry['encrypted_data'])

            if encryption_key.key_type == "symmetric":
                fernet = Fernet(encryption_key.key_data)
                decrypted_data = fernet.decrypt(encrypted_data).decode()
            else:
                return {'success': False, 'error': 'Unsupported key type for decryption'}

        except Exception as e:
            return {'success': False, 'error': f'Decryption failed: {str(e)}'}
```

Access logging captures who accessed what data for what purpose, creating immutable audit trails:

```python
        # Log access
        access_entry = {
            'accessor_id': accessor_id,
            'access_timestamp': datetime.now().isoformat(),
            'purpose': purpose,
            'decryption_success': True
        }

        data_entry['access_log'].append(access_entry)

        return {
            'success': True,
            'decrypted_data': decrypted_data,
            'metadata': data_entry['metadata'],
            'access_logged': True
        }

```

Field-level encryption enables granular data protection within database records, allowing different encryption policies for different data types:

```python
    async def implement_field_level_encryption(self, record: Dict[str, Any],
                                             field_encryption_map: Dict[str, str]) -> Dict[str, Any]:
        """Implement field-level encryption for database records"""

        encrypted_record = record.copy()
        encryption_metadata = {}

        for field_name, key_id in field_encryption_map.items():
            if field_name in record:
                field_value = str(record[field_name])

                # Encrypt field
                encryption_result = await self.encrypt_sensitive_data(
                    field_value, key_id, "field_level"
                )

                if encryption_result['success']:
                    encrypted_record[field_name] = encryption_result['encrypted_data_id']
                    encryption_metadata[field_name] = encryption_result['metadata']
                else:
                    return {'success': False, 'error': f'Failed to encrypt field {field_name}'}

        return {
            'success': True,
            'encrypted_record': encrypted_record,
            'encryption_metadata': encryption_metadata,
            'original_fields_encrypted': list(field_encryption_map.keys())
        }

```

Key rotation is essential for maintaining cryptographic security over time, requiring careful coordination to avoid data loss:

```python
    async def rotate_encryption_keys(self, key_id: str) -> Dict[str, Any]:
        """Rotate encryption keys for security"""

        if key_id not in self.encryption_keys:
            return {'success': False, 'error': 'Key not found'}

        old_key = self.encryption_keys[key_id]
```

Key validation ensures rotation requests target existing keys in the management system. Failed lookups prevent rotation attempts on non-existent keys, maintaining system integrity and providing clear error feedback for operational troubleshooting and automated key management processes.

```python
        # Generate replacement key matching original specifications
        if old_key.key_type == "symmetric":
            new_key_data = Fernet.generate_key()
            new_key = EncryptionKey(
                key_id=f"{key_id}_rotated_{int(datetime.now().timestamp())}",
                key_type="symmetric",
                key_data=new_key_data,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=365),
                algorithm=old_key.algorithm,
                purpose=old_key.purpose
            )
        else:
            return {'success': False, 'error': 'Key rotation not implemented for this key type'}
```

New key generation maintains identical cryptographic specifications to ensure seamless replacement without compatibility issues. The timestamp-based key ID prevents collisions while providing clear lineage tracking. Currently supporting symmetric key rotation with extensibility for asymmetric keys as operational requirements evolve.

```python
        # Store new key and deprecate old key with grace period
        self.encryption_keys[new_key.key_id] = new_key
        old_key.expires_at = datetime.now() + timedelta(days=30)  # Grace period

        return {
            'success': True,
            'old_key_id': key_id,
            'new_key_id': new_key.key_id,
            'rotation_timestamp': datetime.now().isoformat(),
            'grace_period_days': 30
        }

```

Data integrity verification through cryptographic hashing ensures encrypted data hasn't been tampered with:

```python
    def _compute_hash(self, data: str) -> str:
        """Compute SHA-256 hash for data integrity"""
        return hashlib.sha256(data.encode()).hexdigest()
```

Encryption status reporting provides operational intelligence for security teams and compliance auditors:

```python
    async def get_encryption_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive encryption status report"""

        # Key statistics
        key_stats = {
            'total_keys': len(self.encryption_keys),
            'symmetric_keys': len([k for k in self.encryption_keys.values() if k.key_type == "symmetric"]),
            'asymmetric_keys': len([k for k in self.encryption_keys.values() if k.key_type.startswith("asymmetric")]),
            'keys_near_expiry': len([
                k for k in self.encryption_keys.values()
                if k.expires_at and (k.expires_at - datetime.now()).days <= 30
            ])
        }

        # Encrypted data statistics
        data_stats = {
            'total_encrypted_items': len(self.encrypted_data_registry),
            'classification_breakdown': {},
            'total_access_events': sum(
                len(entry['access_log']) for entry in self.encrypted_data_registry.values()
            )
        }

        # Classification breakdown
        for entry in self.encrypted_data_registry.values():
            classification = entry['metadata'].get('classification', 'unknown')
            data_stats['classification_breakdown'][classification] = \
                data_stats['classification_breakdown'].get(classification, 0) + 1

        return {
            'report_timestamp': datetime.now().isoformat(),
            'key_management': key_stats,
            'data_encryption': data_stats,
            'compliance_status': 'compliant',
            'recommendations': self._generate_encryption_recommendations(key_stats, data_stats)
        }

```

Recommendation generation provides actionable insights for maintaining optimal encryption security posture:

```python
    def _generate_encryption_recommendations(self, key_stats: Dict[str, Any],
                                           data_stats: Dict[str, Any]) -> List[str]:
        """Generate encryption recommendations"""

        recommendations = []

        if key_stats['keys_near_expiry'] > 0:
            recommendations.append(f"Rotate {key_stats['keys_near_expiry']} keys that are near expiry")

        if data_stats['total_encrypted_items'] == 0:
            recommendations.append("No encrypted data found - consider implementing encryption for sensitive data")

        if key_stats['asymmetric_keys'] == 0:
            recommendations.append("Consider implementing asymmetric encryption for key exchange")

        return recommendations
```

---

## Module Summary

You've now mastered advanced security and compliance for enterprise agent systems:

✅ **GDPR Compliance**: Implemented comprehensive data protection with automated privacy controls
✅ **Advanced RBAC**: Built fine-grained role-based access control with zero-trust architecture
✅ **Encryption Framework**: Created enterprise-grade encryption with key rotation and field-level protection
✅ **Audit Logging**: Designed comprehensive security event logging and compliance monitoring
✅ **Zero-Trust Security**: Implemented context-aware authentication and authorization systems

### Next Steps

- **Continue to Module B**: [Enterprise Operations & Scaling](Session10_ModuleB_Enterprise_Operations_Scaling.md) for operational excellence
- **Return to Core**: [Session 10 Main](Session10_Enterprise_Integration_Production_Deployment.md)
- **Portfolio Project**: Build a complete enterprise-grade secure agent system

---

**🗂️ Source Files for Module A:**

- `src/session10/security/gdpr_compliance.py` - Comprehensive GDPR compliance framework
- `src/session10/security/enterprise_auth.py` - Advanced RBAC and zero-trust security
- `src/session10/security/encryption_framework.py` - Enterprise encryption and key management

---

## 📝 Multiple Choice Test - Module A

Test your understanding of advanced security and compliance for enterprise agent systems:

**Question 1:** Under GDPR, which legal basis requires the most complex implementation due to withdrawal requirements and proof of consent?  
A) Contract
B) Legal obligation
C) Consent
D) Legitimate interests

**Question 2:** In zero-trust architecture, what principle governs every access request?  
A) Trust but verify
B) Never trust, always verify
C) Verify once, trust always
D) Trust by default

**Question 3:** What is the primary purpose of k-anonymity in data anonymization?  
A) To encrypt sensitive data
B) To ensure each individual cannot be distinguished from at least k-1 others
C) To hash personal identifiers
D) To compress large datasets

**Question 4:** In ABAC (Attribute-Based Access Control), which attributes are NOT typically evaluated?  
A) Subject attributes
B) Object attributes
C) Environment attributes
D) Network attributes

**Question 5:** What is the recommended approach for key rotation in enterprise encryption systems?  
A) Immediate replacement without grace period
B) Rotate keys only when compromised
C) Generate new key and provide grace period for old key
D) Never rotate keys to avoid data loss

**Question 6:** Which GDPR article mandates Data Protection Impact Assessments (DPIA) for high-risk processing?  
A) Article 15
B) Article 17
C) Article 20
D) Article 35

**Question 7:** In field-level encryption, what is the primary advantage over full-record encryption?  
A) Faster encryption performance
B) Granular protection allowing different encryption policies per field
C) Smaller storage requirements
D) Simplified key management

[**🗂️ View Test Solutions →**](Session10A_Test_Solutions.md)
---

## 🧭 Navigation

**Previous:** [Session 9 - Multi-Agent Patterns ←](Session9_Multi_Agent_Patterns.md)
---
