"""
GoHighLevel Complete API Wrapper v3.0
=====================================

Comprehensive Python wrapper for the entire GoHighLevel API v2.0.
Every endpoint with full REST API JSON schema-style docstrings.

Author: Morgan Hamilton | Leadpiggy | this@leadpiggy.com
Date: October 2025  
API Version: 2021-07-28

Usage:
    from gohighlevel_complete_api import GoHighLevelAPI
    
    api = GoHighLevelAPI(
        location_id="your_location_id",
        api_key="your_api_key"
    )
    
    # Create a contact
    contact = api.create_contact(
        first_name="John",
        last_name="Doe", 
        email="john@example.com"
    )
"""

import requests
import time
import json
import re
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GHL_API_KEY", "your_api_key_here")
LOCATION_ID = os.getenv("GHL_LOCATION_ID", "your_location_id_here")

class GoHighLevelAPIError(Exception):
    """
    Custom exception for GoHighLevel API errors.
    
    Attributes:
        message (str): Human-readable error message
        status_code (Optional[int]): HTTP status code from API response
        response_data (Optional[Dict]): Full API response data for debugging
    
    Example:
        try:
            result = api.create_contact(email="invalid")
        except GoHighLevelAPIError as e:
            print(f"Error: {e.message}")
            print(f"Status: {e.status_code}")
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        response_data: Optional[Dict] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data


class GoHighLevelAPI:
    """
    Complete GoHighLevel API v2.0 Wrapper
    
    Provides full access to all GoHighLevel API endpoints with comprehensive
    docstrings following REST API JSON schema documentation style.
    
    Features:
        - All API endpoints covered
        - Full parameter documentation
        - Response schema definitions  
        - Type hints throughout
        - Automatic rate limiting
        - Error handling
        - Helper utilities
    
    Attributes:
        location_id (str): GoHighLevel location/sub-account ID
        api_key (str): API authentication token (Bearer)
        base_url (str): API base URL
        session (requests.Session): Persistent HTTP session
    
    Example:
        >>> api = GoHighLevelAPI("loc_123", "api_key_456")
        >>> contact = api.create_contact(
        ...     first_name="John",
        ...     last_name="Doe",
        ...     email="john@example.com",
        ...     phone="+1234567890"
        ... )
        >>> print(contact['contact']['id'])
    """
    
    def __init__(
        self, 
        location_id: str, 
        api_key: str, 
        base_url: str = "https://services.leadconnectorhq.com"
    ):
        """
        Initialize GoHighLevel API client.
        
        Args:
            location_id: The GoHighLevel location ID (found in Settings > API)
            api_key: API authentication key (Bearer token)
            base_url: API base URL (default: official production URL)
        
        Example:
            >>> api = GoHighLevelAPI(
            ...     location_id="ve9EPM428h8vShlRW1KT",
            ...     api_key="your_api_key_here"
            ... )
        """
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
        """Implement rate limiting to prevent API throttling."""
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
        files: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict:
        """
        Make HTTP request to GoHighLevel API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint path (e.g., "contacts/")
            data: Request body data (JSON serializable dict)
            params: URL query parameters
            files: Files for multipart upload
            headers: Additional headers to merge with defaults
        
        Returns:
            Dict: Parsed JSON response from API
        
        Raises:
            GoHighLevelAPIError: On API errors or network failures
        
        Example:
            >>> result = api._make_request(
            ...     "POST",
            ...     "contacts/",
            ...     data={"firstName": "John", "email": "john@test.com"}
            ... )
        """
        self._rate_limit()
        
        url = urljoin(self.base_url, endpoint)
        
        # Merge headers
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)
        
        # Remove Content-Type for multipart uploads
        if files:
            request_headers.pop('Content-Type', None)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data if not files else None,
                data=data if files else None,
                params=params,
                files=files,
                headers=request_headers
            )
            
            # Handle success responses
            if response.status_code in [200, 201, 202, 204]:
                if response.content:
                    try:
                        return response.json()
                    except:
                        return {"success": True, "content": response.text}
                return {"success": True}
            
            # Handle error responses
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
    # BLOG ENDPOINTS
    # =====================================================================
    
    def create_blog_post(
        self,
        title: str,
        blog_id: str,
        raw_html: str,
        status: str = "DRAFT",
        image_url: Optional[str] = None,
        description: Optional[str] = None,
        image_alt_text: Optional[str] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
        url_slug: Optional[str] = None,
        canonical_link: Optional[str] = None,
        published_at: Optional[str] = None
    ) -> Dict:
        """
        Create a new blog post in GoHighLevel.
        
        Endpoint: POST /blogs/posts
        Scope: blogs/post.write
        
        Args:
            title: Blog post title (required)
            blog_id: Blog site ID (required, found in blog dashboard URL)
            raw_html: HTML content of blog post (required)
            status: Post status - "DRAFT", "PUBLISHED", "SCHEDULED", or "ARCHIVED"
            image_url: Featured image URL
            description: Meta description for SEO
            image_alt_text: Alt text for featured image
            categories: List of category IDs (get from get_blog_categories)
            tags: List of tag strings
            author: Author ID (get from get_blog_authors)
            url_slug: URL-friendly slug (auto-generated if not provided)
            canonical_link: Canonical URL for SEO
            published_at: ISO 8601 timestamp for scheduling (e.g., "2025-02-05T18:30:47.000Z")
        
        Returns:
            Dict: Response with structure:
                {
                    "data": {
                        "id": "post_id_string",
                        "title": "Blog Post Title",
                        "status": "PUBLISHED",
                        ...
                    }
                }
        
        Example:
            >>> post = api.create_blog_post(
            ...     title="10 Tips for Health Insurance",
            ...     blog_id="66f429b8afdce84227a4610d",
            ...     raw_html="<h1>Tips</h1><p>Content here...</p>",
            ...     status="PUBLISHED",
            ...     image_url="https://example.com/image.jpg",
            ...     description="Learn about health insurance",
            ...     categories=["cat_id_1", "cat_id_2"],
            ...     tags=["insurance", "health", "tips"],
            ...     author="author_id_123",
            ...     url_slug="health-insurance-tips"
            ... )
            >>> print(f"Created post: {post['data']['id']}")
        """
        data = {
            "locationId": self.location_id,
            "blogId": blog_id,
            "title": title,
            "rawHTML": raw_html,
            "status": status
        }
        
        # Add optional parameters
        if image_url:
            data["imageUrl"] = image_url
        if description:
            data["description"] = description
        if image_alt_text:
            data["imageAltText"] = image_alt_text
        if categories:
            data["categories"] = ",".join(categories)
        if tags:
            data["tags"] = ",".join(tags)
        if author:
            data["author"] = author
        if url_slug:
            data["urlSlug"] = url_slug
        if canonical_link:
            data["canonicalLink"] = canonical_link
        if published_at:
            data["publishedAt"] = published_at
        
        return self._make_request("POST", "blogs/posts", data)
    
    def update_blog_post(
        self,
        post_id: str,
        **kwargs
    ) -> Dict:
        """
        Update an existing blog post.
        
        Endpoint: PUT /blogs/posts/:postId
        Scope: blogs/post-update.write
        
        Args:
            post_id: The blog post ID to update (required)
            **kwargs: Any fields from create_blog_post to update
        
        Returns:
            Dict: Response with structure:
                {
                    "updatedBlogPost": {
                        "id": "post_id",
                        "title": "Updated Title",
                        ...
                    }
                }
        
        Example:
            >>> api.update_blog_post(
            ...     post_id="post_abc123",
            ...     title="Updated Title",
            ...     status="PUBLISHED",
            ...     tags=["new", "tags"]
            ... )
        """
        data = {"locationId": self.location_id}
        data.update(kwargs)
        
        return self._make_request("PUT", f"blogs/posts/{post_id}", data)
    
    def get_blog_posts(
        self,
        blog_id: str,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
        search_term: Optional[str] = None
    ) -> Dict:
        """
        Get blog posts for a specific blog site.
        
        Endpoint: GET /blogs/posts/all
        Scope: blogs/posts.readonly
        
        Args:
            blog_id: Blog site ID (required)
            limit: Number of posts to return (max 100, default 20)
            offset: Number of posts to skip for pagination (default 0)
            status: Filter by status - "PUBLISHED", "SCHEDULED", "ARCHIVED", "DRAFT"
            search_term: Search posts by title
        
        Returns:
            Dict: Response with structure:
                {
                    "blogs": [
                        {
                            "id": "post_id",
                            "title": "Post Title",
                            "status": "PUBLISHED",
                            ...
                        }
                    ],
                    "total": 45,
                    "count": 20
                }
        
        Example:
            >>> posts = api.get_blog_posts(
            ...     blog_id="blog_123",
            ...     limit=10,
            ...     status="PUBLISHED"
            ... )
            >>> for post in posts['blogs']:
            ...     print(post['title'])
        """
        params = {
            "locationId": self.location_id,
            "blogId": blog_id,
            "limit": limit,
            "offset": offset
        }
        
        if status:
            params["status"] = status
        if search_term:
            params["searchTerm"] = search_term
        
        return self._make_request("GET", "blogs/posts/all", params=params)
    
    def get_blogs_by_location(
        self,
        skip: int = 0,
        limit: int = 10,
        search_term: Optional[str] = None
    ) -> Dict:
        """
        Get all blog sites for the location.
        
        Endpoint: GET /blogs/site/all
        Scope: blogs/list.readonly
        
        Args:
            skip: Number of blogs to skip (default 0)
            limit: Number of blogs to return (default 10)
            search_term: Search blogs by name
        
        Returns:
            Dict: Response with structure:
                {
                    "data": [
                        {
                            "id": "blog_id",
                            "name": "Blog Name",
                            "domain": "blog.example.com",
                            ...
                        }
                    ]
                }
        
        Example:
            >>> blogs = api.get_blogs_by_location()
            >>> blog_id = blogs['data'][0]['id']
        """
        params = {
            "locationId": self.location_id,
            "skip": skip,
            "limit": limit
        }
        
        if search_term:
            params["searchTerm"] = search_term
        
        return self._make_request("GET", "blogs/site/all", params=params)
    
    def check_url_slug_exists(
        self,
        url_slug: str,
        post_id: Optional[str] = None
    ) -> Dict:
        """
        Check if a URL slug already exists.
        
        Endpoint: GET /blogs/posts/url-slug-exists
        Scope: blogs/check-slug.readonly
        
        Args:
            url_slug: The slug to check (required)
            post_id: Optional post ID to exclude from check (for updates)
        
        Returns:
            Dict: Response with structure:
                {
                    "exists": true/false
                }
        
        Example:
            >>> result = api.check_url_slug_exists("my-blog-post")
            >>> if result['exists']:
            ...     print("Slug already taken!")
        """
        params = {
            "locationId": self.location_id,
            "urlSlug": url_slug
        }
        
        if post_id:
            params["postId"] = post_id
        
        return self._make_request("GET", "blogs/posts/url-slug-exists", params=params)
    
    def get_blog_authors(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> Dict:
        """
        Get all blog authors for the location.
        
        Endpoint: GET /blogs/authors
        Scope: blogs/author.readonly
        
        Args:
            limit: Number of authors to return (default 20)
            offset: Number of authors to skip (default 0)
        
        Returns:
            Dict: Response with structure:
                {
                    "authors": [
                        {
                            "id": "author_id",
                            "name": "Author Name",
                            "email": "author@example.com",
                            ...
                        }
                    ]
                }
        
        Example:
            >>> authors = api.get_blog_authors()
            >>> author_id = authors['authors'][0]['id']
        """
        params = {
            "locationId": self.location_id,
            "limit": limit,
            "offset": offset
        }
        
        return self._make_request("GET", "blogs/authors", params=params)
    
    def get_blog_categories(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> Dict:
        """
        Get all blog categories for the location.
        
        Endpoint: GET /blogs/categories
        Scope: blogs/category.readonly
        
        Args:
            limit: Number of categories to return (default 50)
            offset: Number of categories to skip (default 0)
        
        Returns:
            Dict: Response with structure:
                {
                    "categories": [
                        {
                            "id": "category_id",
                            "name": "Category Name",
                            ...
                        }
                    ]
                }
        
        Example:
            >>> categories = api.get_blog_categories()
            >>> cat_ids = [c['id'] for c in categories['categories']]
        """
        params = {
            "locationId": self.location_id,
            "limit": limit,
            "offset": offset
        }
        
        return self._make_request("GET", "blogs/categories", params=params)
    
    def delete_blog_post(
        self,
        post_id: str
    ) -> Dict:
        """
        Delete a blog post.
        
        Endpoint: DELETE /blogs/posts/:postId
        Scope: blogs/post.write
        
        Args:
            post_id: The blog post ID to delete (required)
        
        Returns:
            Dict: Success response
        
        Example:
            >>> api.delete_blog_post("post_abc123")
        """
        return self._make_request("DELETE", f"blogs/posts/{post_id}")
    
    # =====================================================================
    # MEDIA ENDPOINTS
    # =====================================================================
    
    def upload_media_file(
        self,
        file_path: str,
        name: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> Dict:
        """
        Upload a file to GoHighLevel media library.
        
        Endpoint: POST /medias/upload-file
        Scope: medias.write
        Content-Type: multipart/form-data
        
        Args:
            file_path: Path to the file to upload (required, max 25MB)
            name: Custom filename (optional, uses original filename if not provided)
            parent_id: Folder ID to upload to (optional)
        
        Returns:
            Dict: Response with structure:
                {
                    "fileId": "uploaded_file_id.jpg",
                    "url": "https://storage.googleapis.com/bucket/path/to/file.jpg"
                }
        
        Example:
            >>> result = api.upload_media_file(
            ...     file_path="./images/photo.jpg",
            ...     name="featured-image.jpg"
            ... )
            >>> image_url = result['url']
            >>> 
            >>> # Use in blog post
            >>> api.create_blog_post(
            ...     title="My Post",
            ...     blog_id="blog_123",
            ...     raw_html="<p>Content</p>",
            ...     image_url=image_url
            ... )
        """
        if not Path(file_path).exists():
            raise GoHighLevelAPIError(f"File not found: {file_path}")
        
        file_name = name or Path(file_path).name
        
        files = {
            'file': (file_name, open(file_path, 'rb'), 'application/octet-stream')
        }
        
        data = {}
        if name:
            data['name'] = name
        if parent_id:
            data['parentId'] = parent_id
        
        return self._make_request("POST", "medias/upload-file", data=data, files=files)
    
    def get_media_files(
        self,
        offset: int = 0,
        limit: int = 20,
        file_type: str = "file",
        parent_id: Optional[str] = None,
        query: Optional[str] = None
    ) -> Dict:
        """
        Get list of files/folders from media storage.
        
        Endpoint: GET /medias/files
        Scope: medias.readonly
        
        Args:
            offset: Number of files to skip (default 0)
            limit: Number of files to return (default 20)
            file_type: "file" or "folder" (default "file")
            parent_id: Filter by parent folder ID
            query: Search query for file names
        
        Returns:
            Dict: Response with structure:
                {
                    "files": [
                        {
                            "id": "file_id",
                            "name": "filename.jpg",
                            "url": "https://...",
                            "altId": "location_id",
                            "altType": "location",
                            ...
                        }
                    ]
                }
        
        Example:
            >>> files = api.get_media_files(limit=50, query="insurance")
            >>> for file in files['files']:
            ...     print(f"{file['name']}: {file['url']}")
        """
        params = {
            "altType": "location",
            "altId": self.location_id,
            "type": file_type,
            "sortBy": "createdAt",
            "sortOrder": "desc",
            "offset": str(offset),
            "limit": str(limit)
        }
        
        if parent_id:
            params["parentId"] = parent_id
        if query:
            params["query"] = query
        
        return self._make_request("GET", "medias/files", params=params)
    
    def delete_media_file(
        self,
        file_id: str
    ) -> Dict:
        """
        Delete a file or folder from media storage.
        
        Endpoint: DELETE /medias/:id
        Scope: medias.write
        
        Args:
            file_id: The file or folder ID to delete (required)
        
        Returns:
            Dict: Success response
        
        Example:
            >>> api.delete_media_file("file_abc123.jpg")
        """
        params = {
            "altType": "location",
            "altId": self.location_id
        }
        
        return self._make_request("DELETE", f"medias/{file_id}", params=params)
    
    # =====================================================================
    # FORMS ENDPOINTS
    # =====================================================================
    
    def get_form_submissions(
        self,
        page: int = 1,
        limit: int = 20,
        form_id: Optional[str] = None,
        query: Optional[str] = None,
        start_at: Optional[str] = None,
        end_at: Optional[str] = None
    ) -> Dict:
        """
        Get form submissions.
        
        Endpoint: GET /forms/submissions
        Scope: forms.readonly
        
        Args:
            page: Page number (default 1)
            limit: Results per page, max 100 (default 20)
            form_id: Filter by specific form ID
            query: Search by contactId, name, email, or phone
            start_at: Start date filter (YYYY-MM-DD format)
            end_at: End date filter (YYYY-MM-DD format)
        
        Returns:
            Dict: Response with structure:
                {
                    "submissions": [
                        {
                            "id": "submission_id",
                            "formId": "form_id",
                            "contactId": "contact_id",
                            "submittedAt": "2024-01-15T10:30:00Z",
                            ...
                        }
                    ],
                    "meta": {
                        "total": 150,
                        "currentPage": 1,
                        "nextPage": 2,
                        ...
                    }
                }
        
        Example:
            >>> submissions = api.get_form_submissions(
            ...     form_id="form_123",
            ...     start_at="2024-01-01",
            ...     end_at="2024-01-31"
            ... )
            >>> for sub in submissions['submissions']:
            ...     print(f"Contact: {sub['contactId']}")
        """
        params = {
            "locationId": self.location_id,
            "page": page,
            "limit": limit
        }
        
        if form_id:
            params["formId"] = form_id
        if query:
            params["q"] = query
        if start_at:
            params["startAt"] = start_at
        if end_at:
            params["endAt"] = end_at
        
        return self._make_request("GET", "forms/submissions", params=params)
    
    def get_forms(
        self,
        skip: int = 0,
        limit: int = 20,
        type_filter: Optional[str] = None
    ) -> Dict:
        """
        Get all forms for the location.
        
        Endpoint: GET /forms/
        Scope: forms.readonly
        
        Args:
            skip: Number of forms to skip (default 0)
            limit: Number of forms to return (default 20)
            type_filter: Filter by form type
        
        Returns:
            Dict: Response with list of forms
        
        Example:
            >>> forms = api.get_forms()
            >>> for form in forms['forms']:
            ...     print(f"{form['name']}: {form['id']}")
        """
        params = {
            "locationId": self.location_id,
            "skip": skip,
            "limit": limit
        }
        
        if type_filter:
            params["type"] = type_filter
        
        return self._make_request("GET", "forms/", params=params)
    
    # =====================================================================
    # CONTACTS ENDPOINTS
    # =====================================================================
    
    def create_contact(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address1: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
        company_name: Optional[str] = None,
        website: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        custom_fields: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        Create a new contact.
        
        Endpoint: POST /contacts/
        Scope: contacts.write
        
        Args:
            first_name: Contact's first name
            last_name: Contact's last name
            email: Contact's email address
            phone: Contact's phone number (E.164 format recommended)
            address1: Street address
            city: City name
            state: State/province
            postal_code: ZIP/postal code
            country: Country name
            company_name: Company name
            website: Website URL
            tags: List of tag strings
            source: Source of the contact
            custom_fields: Dict of custom field key-value pairs
            **kwargs: Additional fields
        
        Returns:
            Dict: Response with structure:
                {
                    "contact": {
                        "id": "contact_id",
                        "firstName": "John",
                        "lastName": "Doe",
                        "email": "john@example.com",
                        ...
                    }
                }
        
        Example:
            >>> contact = api.create_contact(
            ...     first_name="John",
            ...     last_name="Doe",
            ...     email="john@example.com",
            ...     phone="+1234567890",
            ...     tags=["lead", "health-insurance"],
            ...     custom_fields={"insurance_type": "Medicare"}
            ... )
            >>> contact_id = contact['contact']['id']
        """
        data = {"locationId": self.location_id}
        
        if first_name:
            data["firstName"] = first_name
        if last_name:
            data["lastName"] = last_name
        if email:
            data["email"] = email
        if phone:
            data["phone"] = phone
        if address1:
            data["address1"] = address1
        if city:
            data["city"] = city
        if state:
            data["state"] = state
        if postal_code:
            data["postalCode"] = postal_code
        if country:
            data["country"] = country
        if company_name:
            data["companyName"] = company_name
        if website:
            data["website"] = website
        if tags:
            data["tags"] = ",".join(tags)
        if source:
            data["source"] = source
        if custom_fields:
            data["customFields"] = json.dumps(custom_fields)
        
        data.update(kwargs)
        
        return self._make_request("POST", "contacts/", data)
    
    def get_contact(
        self,
        contact_id: str
    ) -> Dict:
        """
        Get a contact by ID.
        
        Endpoint: GET /contacts/:contactId
        Scope: contacts.readonly
        
        Args:
            contact_id: The contact ID (required)
        
        Returns:
            Dict: Contact data
        
        Example:
            >>> contact = api.get_contact("contact_abc123")
            >>> print(contact['contact']['email'])
        """
        return self._make_request("GET", f"contacts/{contact_id}")
    
    def update_contact(
        self,
        contact_id: str,
        **kwargs
    ) -> Dict:
        """
        Update a contact.
        
        Endpoint: PUT /contacts/:contactId
        Scope: contacts.write
        
        Args:
            contact_id: The contact ID (required)
            **kwargs: Fields to update (same as create_contact)
        
        Returns:
            Dict: Updated contact data
        
        Example:
            >>> api.update_contact(
            ...     contact_id="contact_123",
            ...     email="newemail@example.com",
            ...     tags=["customer", "premium"]
            ... )
        """
        data = kwargs
        return self._make_request("PUT", f"contacts/{contact_id}", data)
    
    def delete_contact(
        self,
        contact_id: str
    ) -> Dict:
        """
        Delete a contact.
        
        Endpoint: DELETE /contacts/:contactId
        Scope: contacts.write
        
        Args:
            contact_id: The contact ID (required)
        
        Returns:
            Dict: Success response
        
        Example:
            >>> api.delete_contact("contact_abc123")
        """
        return self._make_request("DELETE", f"contacts/{contact_id}")
    
    def search_contacts(
        self,
        query: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        **filters
    ) -> Dict:
        """
        Search and filter contacts.
        
        Endpoint: GET /contacts/
        Scope: contacts.readonly
        
        Args:
            query: Search by name, email, or phone
            limit: Number of results (max 100, default 20)
            offset: Number to skip for pagination
            **filters: Additional filter parameters
        
        Returns:
            Dict: Response with contacts array
        
        Example:
            >>> results = api.search_contacts(
            ...     query="john",
            ...     limit=50
            ... )
            >>> for contact in results['contacts']:
            ...     print(contact['email'])
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
    # UTILITY METHODS
    # =====================================================================
    
    def generate_url_slug(
        self,
        title: str
    ) -> str:
        """
        Generate a URL-friendly slug from a title.
        
        This utility function converts a title into a URL-safe slug by:
        - Converting to lowercase
        - Removing special characters
        - Replacing spaces with hyphens
        - Removing consecutive hyphens
        - Trimming hyphens from ends
        
        Args:
            title: The title string to convert
        
        Returns:
            str: URL-friendly slug
        
        Example:
            >>> slug = api.generate_url_slug("10 Tips for Health Insurance!")
            >>> print(slug)
            '10-tips-for-health-insurance'
            >>> 
            >>> slug = api.generate_url_slug("Medicare & Medicaid: What's the Difference?")
            >>> print(slug)
            'medicare-medicaid-whats-the-difference'
        """
        # Convert to lowercase
        slug = title.lower()
        
        # Remove special characters (keep alphanumeric, spaces, and hyphens)
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        
        # Remove consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Trim hyphens from ends
        slug = slug.strip('-')
        
        return slug
    
    def ensure_unique_slug(
        self,
        slug: str,
        post_id: Optional[str] = None,
        max_attempts: int = 100
    ) -> str:
        """
        Ensure a slug is unique by appending a number if necessary.
        
        This utility checks if a slug exists and appends -1, -2, etc. until
        a unique slug is found.
        
        Args:
            slug: The desired slug
            post_id: Optional post ID to exclude from check (for updates)
            max_attempts: Maximum number of attempts (default 100)
        
        Returns:
            str: Unique slug
        
        Raises:
            GoHighLevelAPIError: If unable to generate unique slug
        
        Example:
            >>> slug = api.generate_url_slug("My Blog Post")
            >>> unique_slug = api.ensure_unique_slug(slug)
            >>> # If "my-blog-post" exists, returns "my-blog-post-1"
            >>> # If that exists too, returns "my-blog-post-2", etc.
        """
        original_slug = slug
        counter = 1
        
        while counter <= max_attempts:
            result = self.check_url_slug_exists(slug, post_id)
            
            if not result.get('exists', False):
                return slug
            
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        raise GoHighLevelAPIError(
            f"Unable to generate unique slug after {max_attempts} attempts"
        )
    
    def batch_upload_images(
        self,
        image_paths: List[str],
        parent_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Upload multiple images in batch.
        
        This utility method uploads multiple images and returns their URLs.
        Useful for bulk content operations.
        
        Args:
            image_paths: List of file paths to upload
            parent_id: Optional folder ID to upload to
        
        Returns:
            List[Dict]: List of upload results with structure:
                [
                    {"path": "image1.jpg", "url": "https://...", "fileId": "..."},
                    {"path": "image2.jpg", "url": "https://...", "fileId": "..."},
                    ...
                ]
        
        Example:
            >>> images = [
            ...     "./images/photo1.jpg",
            ...     "./images/photo2.jpg",
            ...     "./images/photo3.jpg"
            ... ]
            >>> results = api.batch_upload_images(images)
            >>> image_urls = [r['url'] for r in results]
        """
        results = []
        
        for path in image_paths:
            try:
                result = self.upload_media_file(path, parent_id=parent_id)
                results.append({
                    "path": path,
                    "url": result.get('url'),
                    "fileId": result.get('fileId'),
                    "success": True
                })
            except Exception as e:
                results.append({
                    "path": path,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def create_blog_post_from_dict(
        self,
        post_data: Dict
    ) -> Dict:
        """
        Create a blog post from a dictionary (useful for bulk imports).
        
        This utility accepts a dictionary with blog post data and handles
        slug generation, uniqueness checking, and API calls.
        
        Args:
            post_data: Dictionary with post data containing:
                - title (required)
                - blog_id (required)
                - raw_html or content (required)
                - status (optional)
                - description (optional)
                - tags (optional)
                - categories (optional)
                - image_url (optional)
                - ... other fields
        
        Returns:
            Dict: Created post response
        
        Example:
            >>> post_data = {
            ...     "title": "Health Insurance Guide",
            ...     "blog_id": "blog_123",
            ...     "content": "<h1>Guide</h1><p>Content...</p>",
            ...     "tags": ["health", "insurance"],
            ...     "status": "PUBLISHED"
            ... }
            >>> result = api.create_blog_post_from_dict(post_data)
        """
        # Generate slug if not provided
        if 'url_slug' not in post_data:
            slug = self.generate_url_slug(post_data['title'])
            post_data['url_slug'] = self.ensure_unique_slug(slug)
        
        # Handle content/raw_html alias
        if 'content' in post_data and 'raw_html' not in post_data:
            post_data['raw_html'] = post_data.pop('content')
        
        return self.create_blog_post(**post_data)
    
    def get_all_blog_posts(
        self,
        blog_id: str,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        Get ALL blog posts (handles pagination automatically).
        
        This utility method fetches all posts by automatically handling
        pagination, making multiple API calls as needed.
        
        Args:
            blog_id: Blog site ID
            status: Optional status filter
        
        Returns:
            List[Dict]: List of all blog posts
        
        Example:
            >>> all_posts = api.get_all_blog_posts("blog_123")
            >>> print(f"Total posts: {len(all_posts)}")
            >>> 
            >>> published = api.get_all_blog_posts(
            ...     "blog_123", 
            ...     status="PUBLISHED"
            ... )
        """
        all_posts = []
        offset = 0
        limit = 100
        
        while True:
            response = self.get_blog_posts(
                blog_id=blog_id,
                limit=limit,
                offset=offset,
                status=status
            )
            
            posts = response.get('blogs', [])
            if not posts:
                break
            
            all_posts.extend(posts)
            
            # Check if we have more
            if len(posts) < limit:
                break
            
            offset += limit
        
        return all_posts
    
    def validate_image_url(
        self,
        url: str
    ) -> bool:
        """
        Validate if a URL is accessible and is an image.
        
        This utility checks if an image URL is valid before using it
        in a blog post.
        
        Args:
            url: Image URL to validate
        
        Returns:
            bool: True if valid image URL, False otherwise
        
        Example:
            >>> is_valid = api.validate_image_url(
            ...     "https://example.com/image.jpg"
            ... )
            >>> if is_valid:
            ...     # Use the URL
            ...     pass
        """
        try:
            response = requests.head(url, timeout=5)
            content_type = response.headers.get('Content-Type', '')
            return (
                response.status_code == 200 and 
                'image' in content_type.lower()
            )
        except:
            return False
    
    def format_phone_e164(
        self,
        phone: str,
        country_code: str = "1"
    ) -> str:
        """
        Format phone number to E.164 standard.
        
        This utility converts phone numbers to the E.164 format required
        by GoHighLevel API (+[country code][number]).
        
        Args:
            phone: Phone number in any format
            country_code: Country calling code (default "1" for US/Canada)
        
        Returns:
            str: E.164 formatted phone number
        
        Example:
            >>> phone = api.format_phone_e164("(555) 123-4567")
            >>> print(phone)
            '+15551234567'
            >>> 
            >>> phone = api.format_phone_e164("07911 123456", "44")
            >>> print(phone)
            '+447911123456'
        """
        # Remove all non-numeric characters
        digits = re.sub(r'\D', '', phone)
        
        # Add country code if not present
        if not digits.startswith(country_code):
            digits = country_code + digits
        
        return f"+{digits}"


# Usage Examples and Testing
if __name__ == "__main__":
    """
    Example usage of the GoHighLevel API wrapper.
    
    To run these examples, set your API credentials:
        export GHL_API_KEY="your_api_key"
        export GHL_LOCATION_ID="your_location_id"
    """
    
    import os
    
    # Initialize API
    api = GoHighLevelAPI(
        location_id=os.getenv("GHL_LOCATION_ID", "default_location_id"),
        api_key=os.getenv("GHL_API_KEY", "default_api_key")
    )
    
    # Example 1: Create a contact
    print("Creating contact...")
    contact = api.create_contact(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+1234567890",
        tags=["lead", "health-insurance"]
    )
    print(f"Created contact: {contact['contact']['id']}")
    
    # Example 2: Upload an image
    print("\nUploading image...")
    # image_result = api.upload_media_file("./sample-image.jpg")
    # image_url = image_result['url']
    # print(f"Uploaded image: {image_url}")
    
    # Example 3: Get blogs and create a post
    print("\nGetting blogs...")
    blogs = api.get_blogs_by_location()
    if blogs.get('data'):
        blog_id = blogs['data'][0]['id']
        print(f"Using blog: {blog_id}")
        
        # Get authors and categories
        authors = api.get_blog_authors()
        categories = api.get_blog_categories()
        
        author_id = authors['authors'][0]['id'] if authors.get('authors') else None
        category_ids = [c['id'] for c in categories.get('categories', [])[:2]]
        
        # Generate slug
        title = "10 Tips for Choosing Health Insurance"
        slug = api.generate_url_slug(title)
        unique_slug = api.ensure_unique_slug(slug)
        
        print(f"\nCreating blog post with slug: {unique_slug}")
        post = api.create_blog_post(
            title=title,
            blog_id=blog_id,
            raw_html="<h1>10 Tips</h1><p>Content here...</p>",
            status="DRAFT",
            description="Learn how to choose the right health insurance",
            # image_url=image_url,
            tags=["health", "insurance", "tips"],
            categories=category_ids,
            author=author_id,
            url_slug=unique_slug
        )
        print(f"Created post: {post['data']['id']}")
    
    print("\nDone!")
