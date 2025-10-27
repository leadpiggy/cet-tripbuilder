"""
S3 File Manager Service

Handles all file operations with AWS S3 bucket (cet-uploads).
Provides upload, download, listing, and deletion functionality.
Supports both direct uploads and pre-signed URLs for GHL webhooks.

Configuration:
- Bucket: cet-uploads (us-east-1)
- Tag-based public access: Files with Public=yes tag are publicly readable
- Pre-signed URLs expire in 1 hour by default
"""

import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from datetime import datetime
import io

load_dotenv()


class S3FileManager:
    """Manages file operations with AWS S3 bucket"""
    
    def __init__(self):
        """Initialize S3 client with credentials from .env"""
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket = os.getenv('AWS_S3_BUCKET', 'cet-uploads')
    
    def upload_file(self, file_obj, s3_path, content_type=None, make_public=False):
        """
        Upload file to S3
        
        Args:
            file_obj: File object or bytes
            s3_path: Destination path in S3 bucket
            content_type: MIME type (e.g., 'image/jpeg', 'application/pdf')
            make_public: If True, add Public=yes tag for public access
        
        Returns:
            bool: True if successful, False otherwise
        """
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        if make_public:
            extra_args['Tagging'] = 'Public=yes'
        
        try:
            self.s3.upload_fileobj(file_obj, self.bucket, s3_path, ExtraArgs=extra_args)
            return True
        except ClientError as e:
            print(f"Upload error: {e}")
            return False
    
    def generate_upload_url(self, s3_path, content_type='application/pdf', expiration=3600):
        """
        Generate pre-signed URL for direct uploads (for GHL webhooks)
        
        Args:
            s3_path: Destination path in S3
            content_type: MIME type
            expiration: URL validity in seconds (default 1 hour)
        
        Returns:
            str: Pre-signed upload URL or None if error
        """
        try:
            url = self.s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': s3_path,
                    'ContentType': content_type
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"URL generation error: {e}")
            return None
    
    def generate_download_url(self, s3_path, expiration=3600):
        """
        Generate temporary download URL (for private files)
        
        Args:
            s3_path: File path in S3
            expiration: URL validity in seconds (default 1 hour)
        
        Returns:
            str: Pre-signed download URL or None if error
        """
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': s3_path},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Download URL error: {e}")
            return None
    
    def get_public_url(self, s3_path):
        """
        Get public URL for files tagged with Public=yes
        
        Args:
            s3_path: File path in S3
        
        Returns:
            str: Public S3 URL
        """
        return f"https://{self.bucket}.s3.amazonaws.com/{s3_path}"
    
    def delete_file(self, s3_path):
        """
        Delete file from S3
        
        Args:
            s3_path: File path in S3
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=s3_path)
            return True
        except ClientError as e:
            print(f"Delete error: {e}")
            return False
    
    def list_files(self, prefix):
        """
        List all files under prefix
        
        Args:
            prefix: Directory path in S3 (e.g., 'trips/Greece 2025/')
        
        Returns:
            list: List of file objects
        """
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            return response.get('Contents', [])
        except ClientError as e:
            print(f"List error: {e}")
            return []
    
    def file_exists(self, s3_path):
        """
        Check if file exists in S3
        
        Args:
            s3_path: File path in S3
        
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            self.s3.head_object(Bucket=self.bucket, Key=s3_path)
            return True
        except ClientError:
            return False
    
    def get_file_metadata(self, s3_path):
        """
        Get metadata for a file in S3
        
        Args:
            s3_path: File path in S3
        
        Returns:
            dict: File metadata (size, content_type, last_modified) or None
        """
        try:
            response = self.s3.head_object(Bucket=self.bucket, Key=s3_path)
            return {
                'size': response.get('ContentLength'),
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag')
            }
        except ClientError as e:
            print(f"Metadata error: {e}")
            return None
    
    def build_s3_path(self, trip_name, passenger_name, file_type, filename):
        """
        Build standardized S3 path for file storage
        
        Args:
            trip_name: Trip name (e.g., "Greece 2025")
            passenger_name: Passenger full name (e.g., "John Doe")
            file_type: Type of file (passports, signatures, documents)
            filename: Original filename
        
        Returns:
            str: Formatted S3 path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize names for S3 paths
        safe_trip = trip_name.replace('/', '_').replace(' ', '_')
        safe_passenger = passenger_name.replace('/', '_').replace(' ', '_')
        
        # Extract file extension
        ext = os.path.splitext(filename)[1]
        
        # Build path: trips/{trip}/passengers/{name}/{type}/{file}
        s3_path = f"trips/{safe_trip}/passengers/{safe_passenger}/{file_type}/{timestamp}{ext}"
        
        return s3_path


# Global instance for easy import
file_manager = S3FileManager()