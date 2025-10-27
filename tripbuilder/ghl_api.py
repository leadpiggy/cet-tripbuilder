"""
GoHighLevel API Wrapper for TripBuilder

Simplified wrapper focused on the essential endpoints needed for TripBuilder:
- Contacts (search, create, update, delete)
- Opportunities (create, update, get, search, update_stage, upsert_custom_field)
- Pipelines (get all with stages)
- Custom Fields (get by location)

Based on GHL API v2.0 (Version: 2021-07-28)
"""

import requests
import time
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin


class GoHighLevelAPIError(Exception):
    """Custom exception for GHL API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data


class GoHighLevelAPI:
    """
    GoHighLevel API v2.0 Wrapper for TripBuilder
    
    Attributes:
        location_id (str): GHL location/sub-account ID
        api_key (str): API authentication token (Bearer)
        base_url (str): API base URL
        session (requests.Session): Persistent HTTP session
    """
    
    def __init__(self, location_id: str, api_key: str, base_url: str = "https://services.leadconnectorhq.com"):
        self.location_id = location_id
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Version": "2021-07-28",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request to GHL API"""
        self._rate_limit()
        
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data if not files else None,
                params=params,
                files=files
            )
            
            # Handle success
            if response.status_code in [200, 201, 202, 204]:
                if response.content:
                    try:
                        return response.json()
                    except:
                        return {"success": True, "content": response.text}
                return {"success": True}
            
            # Handle errors
            error_msg = f"API request failed with status {response.status_code}"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_msg = error_data["message"]
                elif "error" in error_data:
                    error_msg = error_data["error"]
            except:
                error_msg += f": {response.text}"
            
            raise GoHighLevelAPIError(
                message=error_msg,
                status_code=response.status_code,
                response_data=response.json() if response.text else None
            )
        
        except requests.RequestException as e:
            raise GoHighLevelAPIError(f"Network error: {str(e)}")
    
    # =====================================================================
    # CONTACTS
    # =====================================================================
    
    def create_contact(self, **kwargs) -> Dict:
        """
        Create a new contact in GHL.
        
        Args:
            firstname, lastname, email, phone, address1, city, state, 
            postal_code, country, company_name, website, tags, source, etc.
        
        Returns:
            Dict: {'contact': {...}}
        """
        data = {"locationId": self.location_id}
        
        # Map common fields
        field_mapping = {
            'firstname': 'firstName',
            'lastname': 'lastName',
            'address': 'address1',
            'postal_code': 'postalCode',
            'company_name': 'companyName'
        }
        
        for key, value in kwargs.items():
            if value is not None:
                ghl_key = field_mapping.get(key, key)
                if key == 'tags' and isinstance(value, list):
                    data[ghl_key] = ','.join(value)
                else:
                    data[ghl_key] = value
        
        return self._make_request("POST", "contacts/", data)
    
    def get_contact(self, contact_id: str) -> Dict:
        """Get a contact by ID"""
        return self._make_request("GET", f"contacts/{contact_id}")
    
    def update_contact(self, contact_id: str, **kwargs) -> Dict:
        """Update a contact"""
        data = kwargs
        return self._make_request("PUT", f"contacts/{contact_id}", data)
    
    def delete_contact(self, contact_id: str) -> Dict:
        """Delete a contact"""
        return self._make_request("DELETE", f"contacts/{contact_id}")
    
    def search_contacts(self, query: Optional[str] = None, limit: int = 100, offset: int = 0, **filters) -> Dict:
        """
        Search and filter contacts.
        
        Returns:
            Dict: {'contacts': [...], 'total': N}
        """
        params = {
            "locationId": self.location_id,
            "limit": limit,
            "offset": offset
        }
        
        if query:
            params["query"] = query
        
        params.update(filters)
        
        return self._make_request("GET", "contacts/", params=params)
    
    # =====================================================================
    # OPPORTUNITIES
    # =====================================================================
    
    def create_opportunity(self, data: Dict) -> Dict:
        """
        Create an opportunity.
        
        Required fields:
            - name
            - pipelineId
            - stageId
            - contactId
            - locationId
        
        Returns:
            Dict: Opportunity data with 'id'
        """
        if 'locationId' not in data:
            data['locationId'] = self.location_id
        
        return self._make_request("POST", "opportunities/", data)
    
    def get_opportunity(self, opportunity_id: str) -> Dict:
        """Get an opportunity by ID"""
        return self._make_request("GET", f"opportunities/{opportunity_id}")
    
    def update_opportunity(self, opportunity_id: str, data: Dict) -> Dict:
        """Update an opportunity"""
        return self._make_request("PUT", f"opportunities/{opportunity_id}", data)
    
    def delete_opportunity(self, opportunity_id: str) -> Dict:
        """Delete an opportunity"""
        return self._make_request("DELETE", f"opportunities/{opportunity_id}")
    
    def search_opportunities(self, pipeline_id: Optional[str] = None, stage_id: Optional[str] = None, limit: int = 100, page: int = 1, **kwargs) -> Dict:
        """
        Search opportunities using POST /opportunities/search endpoint.
        
        Args:
            pipeline_id: Filter by pipeline ID
            stage_id: Filter by pipeline stage ID
            limit: Number of results per page (max 500, default 100)
            page: Page number for pagination
            **kwargs: Additional parameters (filters, sort, query, etc.)
        
        Returns:
            Dict: {'opportunities': [...], 'total': N, ...}
        """
        # Build request body
        body = {
            "locationId": self.location_id,
            "limit": min(limit, 500),  # API max is 500
            "page": page,
            "filters": []
        }
        
        # Add pipeline filter if provided
        if pipeline_id:
            body["filters"].append({
                "field": "pipeline_id",
                "operator": "eq",
                "value": pipeline_id
            })
        
        # Add stage filter if provided
        if stage_id:
            body["filters"].append({
                "field": "pipeline_stage_id",
                "operator": "eq",
                "value": stage_id
            })
        
        # Merge any additional body parameters
        body.update(kwargs)
        
        return self._make_request("POST", "opportunities/search", data=body)
    
    def update_opportunity_stage(self, opportunity_id: str, stage_id: str) -> Dict:
        """Move opportunity to a new stage"""
        data = {"stageId": stage_id}
        return self._make_request("PUT", f"opportunities/{opportunity_id}/status", data)
    
    def upsert_opportunity_custom_field(self, opportunity_id: str, field_key: str, value: Any) -> Dict:
        """
        Update a custom field value on an opportunity.
        
        Args:
            opportunity_id: The opportunity ID
            field_key: Field key (e.g., 'opportunity.passportnumber')
            value: Field value
        """
        data = {
            "customFields": {
                field_key: value
            }
        }
        return self._make_request("PUT", f"opportunities/{opportunity_id}/upsert", data)
    
    # =====================================================================
    # PIPELINES
    # =====================================================================
    
    def get_pipelines(self) -> Dict:
        """
        Get all pipelines with their stages.
        
        Returns:
            Dict: {'pipelines': [{'id': ..., 'name': ..., 'stages': [...]}]}
        """
        params = {"locationId": self.location_id}
        return self._make_request("GET", "opportunities/pipelines", params=params)
    
    # =====================================================================
    # CUSTOM FIELDS
    # =====================================================================
    
    def get_custom_fields(self, location_id: Optional[str] = None, model: Optional[str] = None) -> Dict:
        """
        Get custom field definitions.
        
        Args:
            location_id: Location ID (uses instance location_id if not provided)
            model: Filter by model ('opportunity' or 'contact')
        
        Returns:
            Dict: {'customFields': [...]}
        """
        loc_id = location_id or self.location_id
        params = {}
        
        if model:
            params["model"] = model
        
        return self._make_request("GET", f"locations/{loc_id}/customFields", params=params)
    
    # =====================================================================
    # UTILITY METHODS
    # =====================================================================
    
    def format_phone_e164(self, phone: str, country_code: str = "1") -> str:
        """Format phone number to E.164 standard"""
        import re
        # Remove all non-numeric characters
        digits = re.sub(r'\D', '', phone)
        
        # Add country code if not present
        if not digits.startswith(country_code):
            digits = country_code + digits
        
        return f"+{digits}"


# Convenience class structure for organized access
class ContactsAPI:
    def __init__(self, api):
        self.api = api
    
    def create(self, **kwargs):
        return self.api.create_contact(**kwargs)
    
    def get(self, contact_id):
        return self.api.get_contact(contact_id)
    
    def update(self, contact_id, **kwargs):
        return self.api.update_contact(contact_id, **kwargs)
    
    def delete(self, contact_id):
        return self.api.delete_contact(contact_id)
    
    def search(self, query=None, **kwargs):
        return self.api.search_contacts(query, **kwargs)


class OpportunitiesAPI:
    def __init__(self, api):
        self.api = api
    
    def create(self, data):
        return self.api.create_opportunity(data)
    
    def get(self, opportunity_id):
        return self.api.get_opportunity(opportunity_id)
    
    def update(self, opportunity_id, data):
        return self.api.update_opportunity(opportunity_id, data)
    
    def delete(self, opportunity_id):
        return self.api.delete_opportunity(opportunity_id)
    
    def search(self, **kwargs):
        return self.api.search_opportunities(**kwargs)
    
    def update_stage(self, opportunity_id, stage_id):
        return self.api.update_opportunity_stage(opportunity_id, stage_id)
    
    def upsert_custom_field(self, opportunity_id, field_key, value):
        return self.api.upsert_opportunity_custom_field(opportunity_id, field_key, value)


class CustomFieldsAPI:
    def __init__(self, api):
        self.api = api
    
    def get_by_location(self, location_id=None, model=None):
        return self.api.get_custom_fields(location_id, model)


# Add convenience properties to main API class
def _add_convenience_apis(api_instance):
    """Add convenience API accessors"""
    api_instance.contacts = ContactsAPI(api_instance)
    api_instance.opportunities = OpportunitiesAPI(api_instance)
    api_instance.custom_fields = CustomFieldsAPI(api_instance)
    return api_instance


# Override __init__ to add convenience APIs
_original_init = GoHighLevelAPI.__init__
def _new_init(self, *args, **kwargs):
    _original_init(self, *args, **kwargs)
    _add_convenience_apis(self)

GoHighLevelAPI.__init__ = _new_init
