# Privacy and compliance framework
from typing import Dict, Any, List
import time
from datetime import datetime, timedelta


class PrivacyComplianceManager:
    """Comprehensive privacy and compliance manager for enterprise RAG systems."""
    
    def __init__(self, compliance_config: Dict[str, Any]):
        self.config = compliance_config
        
        # Compliance frameworks
        self.frameworks = {
            'gdpr': GDPRComplianceHandler(compliance_config.get('gdpr', {})),
            'hipaa': HIPAAComplianceHandler(compliance_config.get('hipaa', {})),
            'sox': SOXComplianceHandler(compliance_config.get('sox', {})),
            'ccpa': CCPAComplianceHandler(compliance_config.get('ccpa', {}))
        }
        
        # Data classification and handling
        self.data_classifier = DataClassifier()
        self.pii_detector = PIIDetector()
        self.data_anonymizer = DataAnonymizer()
        
        # Audit logging
        self.audit_logger = ComplianceAuditLogger(compliance_config.get('audit', {}))
        
    async def process_data_with_compliance(self, data: Dict[str, Any],
                                         compliance_requirements: List[str]) -> Dict[str, Any]:
        """Process data while ensuring compliance with specified requirements."""
        
        processing_result = {
            'original_data_id': data.get('id'),
            'compliance_checks': {},
            'data_modifications': [],
            'audit_entries': []
        }
        
        # Classify data
        data_classification = await self.data_classifier.classify_data(data)
        processing_result['data_classification'] = data_classification
        
        # Detect PII/PHI
        pii_detection = await self.pii_detector.detect_sensitive_data(data)
        processing_result['sensitive_data_detected'] = pii_detection
        
        # Apply compliance frameworks
        processed_data = data.copy()
        for framework in compliance_requirements:
            if framework in self.frameworks:
                compliance_result = await self.frameworks[framework].process_data(
                    processed_data, data_classification, pii_detection
                )
                
                processing_result['compliance_checks'][framework] = compliance_result
                
                if not compliance_result['compliant']:
                    # Apply necessary modifications
                    processed_data = await self._apply_compliance_modifications(
                        processed_data, compliance_result['required_actions']
                    )
                    processing_result['data_modifications'].extend(
                        compliance_result['required_actions']
                    )
        
        # Log compliance processing
        audit_entry = await self.audit_logger.log_compliance_processing(
            data.get('id'), compliance_requirements, processing_result
        )
        processing_result['audit_entries'].append(audit_entry)
        
        return {
            'processed_data': processed_data,
            'compliance_result': processing_result,
            'compliant': all(
                check['compliant'] for check in processing_result['compliance_checks'].values()
            )
        }
    
    async def _apply_compliance_modifications(self, data: Dict[str, Any], 
                                            required_actions: List[Dict]) -> Dict[str, Any]:
        """Apply required compliance modifications to data."""
        
        modified_data = data.copy()
        
        for action in required_actions:
            action_type = action.get('action')
            
            if action_type == 'anonymize_pii':
                modified_data = await self.data_anonymizer.anonymize_pii(
                    modified_data, action.get('fields', [])
                )
            elif action_type == 'encrypt_fields':
                modified_data = await self._encrypt_sensitive_fields(
                    modified_data, action.get('fields', [])
                )
            elif action_type == 'remove_fields':
                for field in action.get('fields', []):
                    modified_data.pop(field, None)
            elif action_type == 'mask_data':
                modified_data = await self._mask_sensitive_data(
                    modified_data, action.get('fields', [])
                )
        
        return modified_data
    
    async def _encrypt_sensitive_fields(self, data: Dict[str, Any], 
                                       fields: List[str]) -> Dict[str, Any]:
        """Encrypt sensitive fields in data."""
        
        encrypted_data = data.copy()
        
        for field in fields:
            if field in encrypted_data:
                # Simple encryption placeholder - use proper encryption in production
                original_value = str(encrypted_data[field])
                encrypted_value = f"ENCRYPTED:{hash(original_value)}"
                encrypted_data[field] = encrypted_value
        
        return encrypted_data
    
    async def _mask_sensitive_data(self, data: Dict[str, Any], 
                                  fields: List[str]) -> Dict[str, Any]:
        """Mask sensitive data fields."""
        
        masked_data = data.copy()
        
        for field in fields:
            if field in masked_data:
                original_value = str(masked_data[field])
                if len(original_value) > 4:
                    masked_value = original_value[:2] + '*' * (len(original_value) - 4) + original_value[-2:]
                else:
                    masked_value = '*' * len(original_value)
                masked_data[field] = masked_value
        
        return masked_data


class GDPRComplianceHandler:
    """GDPR compliance handler for RAG systems."""
    
    def __init__(self, gdpr_config: Dict[str, Any]):
        self.config = gdpr_config
        self.lawful_basis = gdpr_config.get('lawful_basis', 'legitimate_interest')
        self.data_retention_days = gdpr_config.get('retention_days', 365)
        
    async def process_data(self, data: Dict[str, Any],
                          classification: Dict[str, Any],
                          pii_detection: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for GDPR compliance."""
        
        compliance_result = {
            'compliant': True,
            'required_actions': [],
            'gdpr_checks': {}
        }
        
        # Check for personal data
        if pii_detection.get('contains_pii', False):
            compliance_result['gdpr_checks']['personal_data_detected'] = True
            
            # Check consent/lawful basis
            consent_check = await self._check_consent(data, pii_detection)
            compliance_result['gdpr_checks']['consent'] = consent_check
            
            if not consent_check['valid']:
                compliance_result['compliant'] = False
                compliance_result['required_actions'].append({
                    'action': 'obtain_consent',
                    'reason': 'No valid consent for personal data processing'
                })
            
            # Check data minimization
            minimization_check = await self._check_data_minimization(data, classification)
            compliance_result['gdpr_checks']['data_minimization'] = minimization_check
            
            if not minimization_check['compliant']:
                compliance_result['required_actions'].append({
                    'action': 'minimize_data',
                    'fields_to_remove': minimization_check['excessive_fields']
                })
            
            # Check retention period
            retention_check = await self._check_retention_period(data)
            compliance_result['gdpr_checks']['retention'] = retention_check
            
            if not retention_check['compliant']:
                compliance_result['required_actions'].append({
                    'action': 'schedule_deletion',
                    'retention_expires': retention_check['expiry_date']
                })
        
        return compliance_result
    
    async def _check_consent(self, data: Dict[str, Any], 
                           pii_detection: Dict[str, Any]) -> Dict[str, bool]:
        """Check if valid consent exists for personal data processing."""
        
        # Check if consent is recorded
        consent_record = data.get('consent_record', {})
        
        # Validate consent criteria
        valid_consent = (
            consent_record.get('freely_given', False) and
            consent_record.get('specific', False) and
            consent_record.get('informed', False) and
            consent_record.get('unambiguous', False) and
            not consent_record.get('withdrawn', False)
        )
        
        return {
            'valid': valid_consent,
            'consent_timestamp': consent_record.get('timestamp'),
            'lawful_basis': self.lawful_basis,
            'consent_method': consent_record.get('method', 'unknown')
        }
    
    async def _check_data_minimization(self, data: Dict[str, Any], 
                                     classification: Dict[str, Any]) -> Dict[str, Any]:
        """Check if data collection follows minimization principle."""
        
        # Identify potentially excessive fields
        excessive_fields = []
        
        # Check for unnecessary personal data fields
        sensitive_fields = ['ssn', 'phone_number', 'personal_address', 'birth_date']
        for field in sensitive_fields:
            if field in data and not self._is_field_necessary(field, data):
                excessive_fields.append(field)
        
        return {
            'compliant': len(excessive_fields) == 0,
            'excessive_fields': excessive_fields,
            'data_purpose': classification.get('purpose', 'unknown')
        }
    
    async def _check_retention_period(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if data retention period is compliant."""
        
        creation_date = data.get('created_at', time.time())
        if isinstance(creation_date, str):
            creation_date = datetime.fromisoformat(creation_date).timestamp()
        
        retention_expiry = creation_date + (self.data_retention_days * 24 * 60 * 60)
        current_time = time.time()
        
        return {
            'compliant': current_time < retention_expiry,
            'expiry_date': datetime.fromtimestamp(retention_expiry).isoformat(),
            'days_remaining': max(0, int((retention_expiry - current_time) / (24 * 60 * 60)))
        }
    
    def _is_field_necessary(self, field: str, data: Dict[str, Any]) -> bool:
        """Check if a field is necessary for the stated purpose."""
        
        data_purpose = data.get('purpose', 'general')
        
        # Define necessary fields for different purposes
        necessary_fields = {
            'customer_service': ['name', 'email', 'phone_number'],
            'marketing': ['name', 'email'],
            'analytics': ['anonymized_id'],
            'general': ['name', 'email']
        }
        
        return field in necessary_fields.get(data_purpose, [])
    
    async def handle_data_subject_request(self, request_type: str,
                                        subject_id: str) -> Dict[str, Any]:
        """Handle GDPR data subject requests."""
        
        if request_type == 'access':
            return await self._handle_access_request(subject_id)
        elif request_type == 'erasure':
            return await self._handle_erasure_request(subject_id)
        elif request_type == 'rectification':
            return await self._handle_rectification_request(subject_id)
        elif request_type == 'portability':
            return await self._handle_portability_request(subject_id)
        else:
            return {'error': f'Unsupported request type: {request_type}'}
    
    async def _handle_access_request(self, subject_id: str) -> Dict[str, Any]:
        """Handle data subject access request."""
        
        # Retrieve all data for the subject
        subject_data = await self._retrieve_subject_data(subject_id)
        
        return {
            'request_type': 'access',
            'subject_id': subject_id,
            'data': subject_data,
            'processing_purposes': self._get_processing_purposes(subject_data),
            'data_categories': self._categorize_personal_data(subject_data),
            'response_deadline': (datetime.now() + timedelta(days=30)).isoformat()
        }
    
    async def _handle_erasure_request(self, subject_id: str) -> Dict[str, Any]:
        """Handle right to erasure (right to be forgotten) request."""
        
        # Check if erasure is legally required
        erasure_assessment = await self._assess_erasure_requirements(subject_id)
        
        if erasure_assessment['erasure_required']:
            # Perform data erasure
            erasure_result = await self._perform_data_erasure(subject_id)
            
            return {
                'request_type': 'erasure',
                'subject_id': subject_id,
                'erasure_completed': erasure_result['success'],
                'data_deleted': erasure_result.get('deleted_records', 0),
                'completion_date': datetime.now().isoformat()
            }
        else:
            return {
                'request_type': 'erasure',
                'subject_id': subject_id,
                'erasure_declined': True,
                'reason': erasure_assessment['reason']
            }
    
    # Placeholder methods
    async def _retrieve_subject_data(self, subject_id: str):
        return {'id': subject_id, 'data': 'placeholder'}
    
    def _get_processing_purposes(self, data):
        return ['service_provision', 'analytics']
    
    def _categorize_personal_data(self, data):
        return ['contact_information', 'usage_data']
    
    async def _assess_erasure_requirements(self, subject_id: str):
        return {'erasure_required': True, 'reason': 'No legal obligation to retain'}
    
    async def _perform_data_erasure(self, subject_id: str):
        return {'success': True, 'deleted_records': 5}
    
    async def _handle_rectification_request(self, subject_id: str):
        return {'request_type': 'rectification', 'status': 'processed'}
    
    async def _handle_portability_request(self, subject_id: str):
        return {'request_type': 'portability', 'status': 'processed'}


class HIPAAComplianceHandler:
    """HIPAA compliance handler for healthcare RAG systems."""
    
    def __init__(self, hipaa_config: Dict[str, Any]):
        self.config = hipaa_config
        
    async def process_data(self, data: Dict[str, Any],
                          classification: Dict[str, Any],
                          pii_detection: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for HIPAA compliance."""
        
        compliance_result = {
            'compliant': True,
            'required_actions': [],
            'hipaa_checks': {}
        }
        
        # Check for PHI (Protected Health Information)
        phi_check = await self._detect_phi(data)
        compliance_result['hipaa_checks']['phi_detected'] = phi_check
        
        if phi_check['contains_phi']:
            # Check encryption requirements
            encryption_check = await self._check_encryption_requirements(data)
            compliance_result['hipaa_checks']['encryption'] = encryption_check
            
            if not encryption_check['compliant']:
                compliance_result['compliant'] = False
                compliance_result['required_actions'].append({
                    'action': 'encrypt_phi',
                    'fields': encryption_check['unencrypted_phi_fields']
                })
            
            # Check access controls
            access_control_check = await self._check_access_controls(data)
            compliance_result['hipaa_checks']['access_controls'] = access_control_check
            
            if not access_control_check['compliant']:
                compliance_result['compliant'] = False
                compliance_result['required_actions'].append({
                    'action': 'implement_access_controls',
                    'requirements': access_control_check['missing_controls']
                })
        
        return compliance_result
    
    async def _detect_phi(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect Protected Health Information in data."""
        
        phi_indicators = [
            'medical_record_number', 'patient_id', 'diagnosis', 'treatment',
            'medication', 'health_status', 'insurance_info'
        ]
        
        phi_fields_found = []
        for field in phi_indicators:
            if field in data:
                phi_fields_found.append(field)
        
        return {
            'contains_phi': len(phi_fields_found) > 0,
            'phi_fields': phi_fields_found,
            'phi_categories': self._categorize_phi(phi_fields_found)
        }
    
    def _categorize_phi(self, phi_fields: List[str]) -> List[str]:
        """Categorize types of PHI found."""
        
        categories = []
        if any(field in phi_fields for field in ['diagnosis', 'treatment', 'medication']):
            categories.append('medical_information')
        if any(field in phi_fields for field in ['patient_id', 'medical_record_number']):
            categories.append('identifiers')
        if 'insurance_info' in phi_fields:
            categories.append('payment_information')
        
        return categories
    
    async def _check_encryption_requirements(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check HIPAA encryption requirements."""
        
        # Check if PHI fields are encrypted
        phi_fields = ['medical_record_number', 'patient_id', 'diagnosis']
        unencrypted_fields = []
        
        for field in phi_fields:
            if field in data:
                value = str(data[field])
                if not value.startswith('ENCRYPTED:'):
                    unencrypted_fields.append(field)
        
        return {
            'compliant': len(unencrypted_fields) == 0,
            'unencrypted_phi_fields': unencrypted_fields,
            'encryption_standard': 'AES-256'
        }
    
    async def _check_access_controls(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check HIPAA access control requirements."""
        
        required_controls = ['authentication', 'authorization', 'audit_logging']
        missing_controls = []
        
        access_metadata = data.get('access_metadata', {})
        
        for control in required_controls:
            if not access_metadata.get(f'{control}_enabled', False):
                missing_controls.append(control)
        
        return {
            'compliant': len(missing_controls) == 0,
            'missing_controls': missing_controls,
            'current_controls': list(access_metadata.keys())
        }


# Placeholder classes for other compliance frameworks
class SOXComplianceHandler:
    def __init__(self, config):
        self.config = config
    
    async def process_data(self, data, classification, pii_detection):
        return {'compliant': True, 'required_actions': [], 'sox_checks': {}}


class CCPAComplianceHandler:
    def __init__(self, config):
        self.config = config
    
    async def process_data(self, data, classification, pii_detection):
        return {'compliant': True, 'required_actions': [], 'ccpa_checks': {}}


class DataClassifier:
    """Classify data based on sensitivity and content type."""
    
    async def classify_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify data into categories."""
        
        classification = {
            'sensitivity_level': 'medium',
            'data_categories': ['general'],
            'purpose': 'general_processing'
        }
        
        # Check for sensitive data indicators
        sensitive_indicators = ['ssn', 'credit_card', 'medical', 'financial']
        
        if any(indicator in str(data).lower() for indicator in sensitive_indicators):
            classification['sensitivity_level'] = 'high'
            classification['data_categories'].append('sensitive')
        
        return classification


class PIIDetector:
    """Detect personally identifiable information in data."""
    
    async def detect_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect PII/PHI in data."""
        
        pii_fields = []
        data_str = str(data).lower()
        
        # Simple PII detection patterns
        pii_patterns = {
            'email': '@' in data_str,
            'phone': any(char.isdigit() for char in data_str) and len([c for c in data_str if c.isdigit()]) >= 10,
            'ssn': 'ssn' in data_str or 'social security' in data_str,
            'address': any(word in data_str for word in ['street', 'avenue', 'road', 'boulevard'])
        }
        
        for pii_type, detected in pii_patterns.items():
            if detected:
                pii_fields.append(pii_type)
        
        return {
            'contains_pii': len(pii_fields) > 0,
            'pii_types': pii_fields,
            'confidence_score': 0.8 if pii_fields else 0.1
        }


class DataAnonymizer:
    """Anonymize sensitive data while preserving utility."""
    
    async def anonymize_pii(self, data: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """Anonymize PII fields in data."""
        
        anonymized_data = data.copy()
        
        for field in fields:
            if field in anonymized_data:
                original_value = anonymized_data[field]
                # Simple anonymization - use proper techniques in production
                anonymized_value = f"ANON_{hash(str(original_value)) % 10000}"
                anonymized_data[field] = anonymized_value
        
        return anonymized_data


class ComplianceAuditLogger:
    """Audit logger for compliance activities."""
    
    def __init__(self, audit_config: Dict[str, Any]):
        self.config = audit_config
        self.audit_log = []
        
    async def log_compliance_processing(self, data_id: str, 
                                      requirements: List[str], 
                                      processing_result: Dict[str, Any]) -> str:
        """Log compliance processing activity."""
        
        audit_entry = {
            'audit_id': f"audit_{int(time.time())}_{len(self.audit_log)}",
            'timestamp': datetime.now().isoformat(),
            'data_id': data_id,
            'compliance_requirements': requirements,
            'processing_result': processing_result,
            'compliance_status': 'compliant' if all(
                check.get('compliant', False) 
                for check in processing_result.get('compliance_checks', {}).values()
            ) else 'non_compliant'
        }
        
        self.audit_log.append(audit_entry)
        
        return audit_entry['audit_id']
    
    def get_audit_trail(self, data_id: str = None) -> List[Dict[str, Any]]:
        """Get audit trail for specific data or all data."""
        
        if data_id:
            return [entry for entry in self.audit_log if entry['data_id'] == data_id]
        else:
            return self.audit_log.copy()