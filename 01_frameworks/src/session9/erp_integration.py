"""
ERP System Integration for Enterprise Agent Systems

This module provides comprehensive adapters for integrating with Enterprise Resource
Planning (ERP) systems including SAP, Oracle ERP, Microsoft Dynamics, and other
enterprise systems commonly used in large organizations.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import hashlib
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ERPSystem(Enum):
    """Supported ERP systems."""
    SAP_S4HANA = "sap_s4hana"
    SAP_ECC = "sap_ecc"
    ORACLE_ERP_CLOUD = "oracle_erp_cloud"
    MICROSOFT_DYNAMICS = "microsoft_dynamics"
    NETSUITE = "netsuite"
    WORKDAY = "workday"
    GENERIC = "generic"

class ERPModule(Enum):
    """ERP functional modules."""
    FINANCE = "finance"
    PROCUREMENT = "procurement"
    MANUFACTURING = "manufacturing"
    SALES = "sales"
    INVENTORY = "inventory"
    HR = "hr"
    CRM = "crm"
    PROJECT_MANAGEMENT = "project_management"

@dataclass
class ERPTransaction:
    """Represents an ERP transaction."""
    transaction_id: str
    transaction_type: str
    module: ERPModule
    data: Dict[str, Any]
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None

@dataclass
class ERPBusinessObject:
    """Represents an ERP business object (customer, vendor, material, etc.)."""
    object_type: str
    object_id: str
    attributes: Dict[str, Any]
    last_modified: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    master_data_source: str = ""

class SAPIntegrationAdapter:
    """Advanced adapter for SAP ERP system integration with comprehensive features."""
    
    def __init__(self, base_url: str, credentials: Dict[str, Any], 
                 system_type: ERPSystem = ERPSystem.SAP_S4HANA):
        self.base_url = base_url.rstrip('/')
        self.credentials = credentials
        self.system_type = system_type
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.token_expires: Optional[datetime] = None
        self.csrf_token: Optional[str] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # SAP-specific configuration
        self.odata_service_root = "/sap/opu/odata/sap"
        self.rest_service_root = "/sap/bc/rest"
        self.max_batch_size = 100
        self.request_timeout = 30
        
        # Connection pooling and performance settings
        self.connection_limits = {
            "total": 50,
            "per_host": 10,
            "keepalive_timeout": 30
        }
        
        # Retry and error handling
        self.retry_config = {
            "max_attempts": 3,
            "backoff_factor": 2,
            "retriable_status_codes": [503, 504, 429]
        }
    
    async def connect(self) -> bool:
        """Establish connection to SAP system with advanced configuration."""
        try:
            connector = aiohttp.TCPConnector(
                limit=self.connection_limits["total"],
                limit_per_host=self.connection_limits["per_host"],
                keepalive_timeout=self.connection_limits["keepalive_timeout"],
                enable_cleanup_closed=True,
                ssl=False if "localhost" in self.base_url else True
            )
            
            timeout = aiohttp.ClientTimeout(total=self.request_timeout)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "User-Agent": "EnterpriseAgent-SAP/1.0",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            )
            
            # Authenticate and get tokens
            return await self.authenticate(self.credentials)
            
        except Exception as e:
            self.logger.error(f"SAP connection failed: {e}")
            return False
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with SAP using OAuth 2.0 or Basic Auth."""
        auth_type = credentials.get("type", "oauth2")
        
        try:
            if auth_type == "oauth2":
                return await self._oauth2_authenticate(credentials)
            elif auth_type == "basic":
                return await self._basic_authenticate(credentials)
            elif auth_type == "saml":
                return await self._saml_authenticate(credentials)
            else:
                self.logger.error(f"Unsupported SAP auth type: {auth_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"SAP authentication failed: {e}")
            return False
    
    async def _oauth2_authenticate(self, credentials: Dict[str, Any]) -> bool:
        """OAuth 2.0 authentication for SAP systems."""
        auth_url = urljoin(self.base_url, "/oauth/token")
        
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "scope": credentials.get("scope", "read write")
        }
        
        async with self.session.post(auth_url, data=auth_data) as response:
            if response.status == 200:
                token_data = await response.json()
                self.auth_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                
                # Update session headers
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                # Get CSRF token for data modification operations
                await self._get_csrf_token()
                
                self.logger.info("SAP OAuth2 authentication successful")
                return True
            else:
                self.logger.error(f"SAP OAuth2 auth failed: {response.status}")
                return False
    
    async def _basic_authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Basic authentication for SAP systems."""
        import base64
        username = credentials["username"]
        password = credentials["password"]
        
        credentials_str = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials_str.encode()).decode()
        
        self.session.headers.update({
            "Authorization": f"Basic {encoded_credentials}"
        })
        
        # Test authentication
        test_url = urljoin(self.base_url, "/sap/bc/rest/test")
        try:
            async with self.session.get(test_url) as response:
                if response.status in [200, 404]:  # 404 is OK, means auth worked
                    await self._get_csrf_token()
                    self.logger.info("SAP Basic authentication successful")
                    return True
        except:
            pass
        
        return False
    
    async def _saml_authenticate(self, credentials: Dict[str, Any]) -> bool:
        """SAML authentication for SAP systems."""
        # Simplified SAML flow - in production, use proper SAML library
        saml_endpoint = credentials.get("saml_endpoint")
        username = credentials["username"]
        password = credentials["password"]
        
        # This would involve proper SAML assertion creation and exchange
        # For demo purposes, we'll simulate successful SAML auth
        self.auth_token = f"saml_token_{hashlib.md5(username.encode()).hexdigest()}"
        self.token_expires = datetime.now() + timedelta(hours=8)
        
        self.session.headers.update({
            "Authorization": f"SAML {self.auth_token}"
        })
        
        self.logger.info("SAP SAML authentication successful")
        return True
    
    async def _get_csrf_token(self):
        """Get CSRF token required for SAP data modification operations."""
        try:
            csrf_url = urljoin(self.base_url, "/sap/bc/rest/csrf")
            headers = {"X-CSRF-Token": "fetch"}
            
            async with self.session.get(csrf_url, headers=headers) as response:
                if response.status == 200:
                    self.csrf_token = response.headers.get("X-CSRF-Token")
                    self.logger.debug("CSRF token obtained")
        except Exception as e:
            self.logger.warning(f"Failed to get CSRF token: {e}")
    
    async def execute_operation(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute SAP operation with comprehensive error handling."""
        if not await self._ensure_authenticated():
            raise Exception("Authentication required")
        
        operation_map = {
            "get_customer": self._get_customer_data,
            "create_customer": self._create_customer,
            "update_customer": self._update_customer,
            "get_purchase_order": self._get_purchase_order,
            "create_purchase_order": self._create_purchase_order,
            "get_material": self._get_material_data,
            "get_financial_data": self._get_financial_data,
            "execute_bapi": self._execute_bapi,
            "read_odata_service": self._read_odata_service,
            "batch_operation": self._execute_batch_operation
        }
        
        if operation not in operation_map:
            raise ValueError(f"Unknown SAP operation: {operation}")
        
        try:
            return await operation_map[operation](params)
        except Exception as e:
            self.logger.error(f"SAP operation '{operation}' failed: {e}")
            raise
    
    async def _ensure_authenticated(self) -> bool:
        """Ensure valid authentication token."""
        if not self.auth_token:
            return await self.authenticate(self.credentials)
        
        # Check token expiration
        if self.token_expires and datetime.now() >= self.token_expires:
            self.logger.info("Token expired, re-authenticating")
            return await self.authenticate(self.credentials)
        
        return True
    
    async def _get_customer_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve customer data from SAP."""
        customer_id = params.get("customer_id")
        if not customer_id:
            raise ValueError("customer_id is required")
        
        # Use SAP OData service for customer data
        service_url = f"{self.base_url}{self.odata_service_root}/ZCustomerService"
        entity_url = f"{service_url}/CustomerSet('{customer_id}')"
        
        async with self.session.get(entity_url) as response:
            if response.status == 200:
                data = await response.json()
                return self._transform_customer_data(data)
            elif response.status == 404:
                return {"error": "Customer not found", "customer_id": customer_id}
            else:
                error_text = await response.text()
                raise Exception(f"SAP API error: {response.status} - {error_text}")
    
    async def _create_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create new customer in SAP."""
        customer_data = params.get("customer_data", {})
        
        # Validate required fields
        required_fields = ["name", "country", "city"]
        for field in required_fields:
            if field not in customer_data:
                raise ValueError(f"Required field missing: {field}")
        
        # Prepare SAP customer structure
        sap_customer = self._prepare_sap_customer_data(customer_data)
        
        service_url = f"{self.base_url}{self.odata_service_root}/ZCustomerService/CustomerSet"
        headers = {"X-CSRF-Token": self.csrf_token} if self.csrf_token else {}
        
        async with self.session.post(service_url, json=sap_customer, headers=headers) as response:
            if response.status == 201:
                created_customer = await response.json()
                return {
                    "success": True,
                    "customer_id": created_customer.get("CustomerID"),
                    "message": "Customer created successfully"
                }
            else:
                error_text = await response.text()
                raise Exception(f"Customer creation failed: {response.status} - {error_text}")
    
    async def _get_purchase_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve purchase order data from SAP."""
        po_number = params.get("po_number")
        if not po_number:
            raise ValueError("po_number is required")
        
        service_url = f"{self.base_url}{self.odata_service_root}/ZPurchaseOrderService"
        entity_url = f"{service_url}/PurchaseOrderSet('{po_number}')"
        
        # Include line items
        expand_options = "$expand=LineItems"
        full_url = f"{entity_url}?{expand_options}"
        
        async with self.session.get(full_url) as response:
            if response.status == 200:
                data = await response.json()
                return self._transform_purchase_order_data(data)
            else:
                error_text = await response.text()
                raise Exception(f"Purchase order retrieval failed: {response.status} - {error_text}")
    
    async def _execute_bapi(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SAP BAPI (Business Application Programming Interface)."""
        bapi_name = params.get("bapi_name")
        bapi_params = params.get("parameters", {})
        
        if not bapi_name:
            raise ValueError("bapi_name is required")
        
        # BAPI execution endpoint
        bapi_url = f"{self.base_url}{self.rest_service_root}/bapi/{bapi_name}"
        
        request_payload = {
            "parameters": bapi_params,
            "tables": params.get("tables", {}),
            "commit": params.get("commit", True)
        }
        
        headers = {"X-CSRF-Token": self.csrf_token} if self.csrf_token else {}
        
        async with self.session.post(bapi_url, json=request_payload, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return {
                    "success": result.get("return_code", "") == "S",
                    "messages": result.get("messages", []),
                    "data": result.get("export_parameters", {}),
                    "tables": result.get("tables", {})
                }
            else:
                error_text = await response.text()
                raise Exception(f"BAPI execution failed: {response.status} - {error_text}")
    
    async def _execute_batch_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multiple SAP operations in a single batch request."""
        operations = params.get("operations", [])
        if not operations:
            raise ValueError("operations list is required")
        
        if len(operations) > self.max_batch_size:
            raise ValueError(f"Batch size exceeds maximum of {self.max_batch_size}")
        
        batch_boundary = f"batch_{int(time.time())}"
        changeset_boundary = f"changeset_{int(time.time())}"
        
        batch_content = self._build_batch_request(operations, batch_boundary, changeset_boundary)
        
        batch_url = f"{self.base_url}{self.odata_service_root}/$batch"
        headers = {
            "Content-Type": f"multipart/mixed; boundary={batch_boundary}",
            "X-CSRF-Token": self.csrf_token
        }
        
        async with self.session.post(batch_url, data=batch_content, headers=headers) as response:
            if response.status == 202:
                batch_response = await response.text()
                return self._parse_batch_response(batch_response)
            else:
                error_text = await response.text()
                raise Exception(f"Batch operation failed: {response.status} - {error_text}")
    
    def _build_batch_request(self, operations: List[Dict[str, Any]], 
                           batch_boundary: str, changeset_boundary: str) -> str:
        """Build OData batch request content."""
        # Simplified batch request builder
        # In production, use proper OData batch formatting library
        content_parts = [f"--{batch_boundary}"]
        
        for i, operation in enumerate(operations):
            content_parts.extend([
                f"Content-Type: application/http",
                f"Content-Transfer-Encoding: binary",
                f"Content-ID: {i + 1}",
                "",
                f"{operation.get('method', 'GET')} {operation.get('url', '')} HTTP/1.1",
                "Content-Type: application/json",
                "",
                json.dumps(operation.get('data', {})) if operation.get('data') else "",
                ""
            ])
        
        content_parts.append(f"--{batch_boundary}--")
        return "\r\n".join(content_parts)
    
    def _parse_batch_response(self, response_content: str) -> Dict[str, Any]:
        """Parse OData batch response."""
        # Simplified response parser
        # In production, use proper OData batch response parser
        return {
            "batch_processed": True,
            "operations_count": response_content.count("HTTP/1.1"),
            "raw_response": response_content[:1000]  # Truncated for demo
        }
    
    def _transform_customer_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform SAP customer data to standardized format."""
        d = raw_data.get("d", raw_data)
        
        return {
            "customer_id": d.get("CustomerID"),
            "name": d.get("Name1"),
            "name2": d.get("Name2", ""),
            "country": d.get("Country"),
            "region": d.get("Region"),
            "city": d.get("City"),
            "postal_code": d.get("PostalCode"),
            "street": d.get("Street"),
            "phone": d.get("Telephone"),
            "email": d.get("Email"),
            "currency": d.get("Currency"),
            "payment_terms": d.get("PaymentTerms"),
            "credit_limit": d.get("CreditLimit"),
            "created_date": d.get("CreatedOn"),
            "last_modified": d.get("ChangedOn")
        }
    
    def _prepare_sap_customer_data(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare customer data in SAP format."""
        return {
            "Name1": customer_data["name"],
            "Name2": customer_data.get("name2", ""),
            "Country": customer_data["country"],
            "Region": customer_data.get("region", ""),
            "City": customer_data["city"],
            "PostalCode": customer_data.get("postal_code", ""),
            "Street": customer_data.get("street", ""),
            "Telephone": customer_data.get("phone", ""),
            "Email": customer_data.get("email", ""),
            "Currency": customer_data.get("currency", "USD"),
            "PaymentTerms": customer_data.get("payment_terms", "30"),
            "CreditLimit": str(customer_data.get("credit_limit", 0))
        }
    
    def _transform_purchase_order_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform SAP purchase order data to standardized format."""
        d = raw_data.get("d", raw_data)
        
        line_items = []
        if "LineItems" in d:
            for item in d["LineItems"].get("results", []):
                line_items.append({
                    "line_number": item.get("LineNumber"),
                    "material_id": item.get("MaterialID"),
                    "quantity": item.get("Quantity"),
                    "unit": item.get("Unit"),
                    "price": item.get("Price"),
                    "total_value": item.get("TotalValue")
                })
        
        return {
            "po_number": d.get("PurchaseOrder"),
            "vendor_id": d.get("VendorID"),
            "vendor_name": d.get("VendorName"),
            "po_date": d.get("PODate"),
            "total_value": d.get("TotalValue"),
            "currency": d.get("Currency"),
            "status": d.get("Status"),
            "line_items": line_items
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check SAP system health and connectivity."""
        try:
            if not self.session:
                return {"healthy": False, "error": "No session established"}
            
            # Test basic connectivity
            test_url = f"{self.base_url}/sap/bc/rest/healthcheck"
            start_time = time.time()
            
            async with self.session.get(test_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                response_time = (time.time() - start_time) * 1000
                
                return {
                    "healthy": response.status in [200, 404],
                    "status_code": response.status,
                    "response_time_ms": round(response_time, 2),
                    "sap_system_type": self.system_type.value,
                    "authentication_valid": bool(self.auth_token),
                    "csrf_token_available": bool(self.csrf_token)
                }
        
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "sap_system_type": self.system_type.value
            }
    
    async def disconnect(self) -> bool:
        """Disconnect from SAP system."""
        try:
            if self.session:
                await self.session.close()
            
            self.auth_token = None
            self.token_expires = None
            self.csrf_token = None
            self.session = None
            
            self.logger.info("Disconnected from SAP system")
            return True
            
        except Exception as e:
            self.logger.error(f"Error disconnecting from SAP: {e}")
            return False

class OracleERPAdapter:
    """Adapter for Oracle ERP Cloud integration."""
    
    def __init__(self, base_url: str, credentials: Dict[str, Any]):
        self.base_url = base_url.rstrip('/')
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def connect(self) -> bool:
        """Connect to Oracle ERP Cloud."""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"Content-Type": "application/json"}
            )
            return await self.authenticate(self.credentials)
        except Exception as e:
            self.logger.error(f"Oracle ERP connection failed: {e}")
            return False
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with Oracle ERP Cloud."""
        username = credentials.get("username")
        password = credentials.get("password")
        
        if not username or not password:
            return False
        
        import base64
        auth_string = f"{username}:{password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        self.session.headers.update({
            "Authorization": f"Basic {encoded_auth}"
        })
        
        # Test authentication
        test_url = f"{self.base_url}/fscmRestApi/resources/11.13.18.05/fusionTaxonomy/metadata"
        try:
            async with self.session.get(test_url) as response:
                if response.status == 200:
                    self.logger.info("Oracle ERP authentication successful")
                    return True
        except:
            pass
        
        return False
    
    async def execute_operation(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute Oracle ERP operation."""
        operation_map = {
            "get_supplier": self._get_supplier,
            "create_invoice": self._create_invoice,
            "get_purchase_orders": self._get_purchase_orders
        }
        
        if operation not in operation_map:
            raise ValueError(f"Unknown Oracle ERP operation: {operation}")
        
        return await operation_map[operation](params)
    
    async def _get_supplier(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get supplier information from Oracle ERP."""
        supplier_id = params.get("supplier_id")
        url = f"{self.base_url}/fscmRestApi/resources/11.13.18.05/suppliers/{supplier_id}"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Oracle ERP supplier query failed: {response.status}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Oracle ERP system health."""
        try:
            test_url = f"{self.base_url}/fscmRestApi/resources/11.13.18.05/fusionTaxonomy/metadata"
            async with self.session.get(test_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                return {
                    "healthy": response.status == 200,
                    "status_code": response.status,
                    "system_type": "Oracle ERP Cloud"
                }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "system_type": "Oracle ERP Cloud"
            }
    
    async def disconnect(self) -> bool:
        """Disconnect from Oracle ERP."""
        if self.session:
            await self.session.close()
        return True

# Example usage and testing
async def demo_erp_integration():
    """Demonstrate ERP system integration."""
    
    print("\n=== ERP Integration Demo ===")
    
    # SAP Integration Demo
    sap_config = {
        "base_url": "https://sap-demo.company.com",
        "credentials": {
            "type": "oauth2",
            "client_id": "sap_client_demo",
            "client_secret": "sap_secret_demo"
        }
    }
    
    sap_adapter = SAPIntegrationAdapter(
        sap_config["base_url"], 
        sap_config["credentials"]
    )
    
    try:
        print("Connecting to SAP system...")
        if await sap_adapter.connect():
            print("✓ SAP connection successful")
            
            # Test health check
            health = await sap_adapter.health_check()
            print(f"SAP Health: {health}")
            
            # Test customer data retrieval
            try:
                customer_data = await sap_adapter.execute_operation(
                    "get_customer", 
                    {"customer_id": "CUST001"}
                )
                print(f"Customer Data: {customer_data}")
            except Exception as e:
                print(f"Customer query failed: {e}")
            
            # Test BAPI execution
            try:
                bapi_result = await sap_adapter.execute_operation(
                    "execute_bapi",
                    {
                        "bapi_name": "BAPI_CUSTOMER_GETDETAIL",
                        "parameters": {"CUSTOMERNO": "CUST001"}
                    }
                )
                print(f"BAPI Result: {bapi_result}")
            except Exception as e:
                print(f"BAPI execution failed: {e}")
                
        else:
            print("✗ SAP connection failed")
    
    finally:
        await sap_adapter.disconnect()
    
    # Oracle ERP Integration Demo
    oracle_config = {
        "base_url": "https://oracle-erp.company.com",
        "credentials": {
            "username": "oracle_user",
            "password": "oracle_password"
        }
    }
    
    oracle_adapter = OracleERPAdapter(
        oracle_config["base_url"],
        oracle_config["credentials"]
    )
    
    try:
        print("\nConnecting to Oracle ERP system...")
        if await oracle_adapter.connect():
            print("✓ Oracle ERP connection successful")
            
            health = await oracle_adapter.health_check()
            print(f"Oracle ERP Health: {health}")
        else:
            print("✗ Oracle ERP connection failed")
    
    finally:
        await oracle_adapter.disconnect()

if __name__ == "__main__":
    asyncio.run(demo_erp_integration())