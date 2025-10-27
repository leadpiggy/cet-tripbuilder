"""
Vendor Sync Service
Manages bidirectional synchronization between TripVendor records and GHL dropdown options.

This service ensures that:
1. Vendors in the database are reflected in GHL custom field dropdown
2. Vendors from GHL are imported to the database
3. Changes to vendors (create/delete) update GHL dropdown options

Used by: SQLAlchemy event listeners, GHL sync service, vendor CRUD routes
"""

from tripbuilder.models import db, TripVendor
from tripbuilder.ghl_api import GoHighLevelAPI
import os


class VendorSyncService:
    """Manage vendor ↔ GHL dropdown sync"""
    
    # GHL custom field key for trip vendor dropdown
    VENDOR_FIELD_KEY = 'opportunity.tripvendor'
    
    def __init__(self, ghl_api=None):
        """
        Initialize vendor sync service
        
        Args:
            ghl_api: GoHighLevelAPI instance (optional, will create if not provided)
        """
        if ghl_api:
            self.ghl_api = ghl_api
        else:
            # Create GHL API instance
            api_token = os.getenv('GHL_API_TOKEN')
            if not api_token:
                raise ValueError("GHL_API_TOKEN not found in environment")
            self.ghl_api = GoHighLevelAPI(api_token)
        
        self.location_id = os.getenv('GHL_LOCATION_ID')
        if not self.location_id:
            raise ValueError("GHL_LOCATION_ID not found in environment")
    
    def sync_vendors_to_ghl(self):
        """
        Update GHL opportunity.tripvendor dropdown options to match database.
        
        This overwrites all dropdown options in GHL with current database vendors.
        Use carefully - this is a complete replacement, not a merge.
        
        Returns:
            int: Number of vendor names synced to GHL
        """
        try:
            # Get all vendors from database
            vendors = TripVendor.query.order_by(TripVendor.name).all()
            vendor_names = [v.name for v in vendors]
            
            print(f"Syncing {len(vendor_names)} vendors to GHL dropdown...")
            
            # Update GHL custom field dropdown options
            success = self.ghl_api.update_custom_field_options(
                field_key=self.VENDOR_FIELD_KEY,
                options=vendor_names,
                location_id=self.location_id
            )
            
            if success:
                print(f"✅ Successfully synced {len(vendor_names)} vendors to GHL")
                return len(vendor_names)
            else:
                print("❌ Failed to sync vendors to GHL")
                return 0
                
        except Exception as e:
            print(f"Error syncing vendors to GHL: {e}")
            raise
    
    def sync_vendors_from_ghl(self):
        """
        Import vendors from GHL dropdown to database.
        
        This creates TripVendor records for any options in the GHL dropdown
        that don't already exist in the database. Existing vendors are not modified.
        
        Returns:
            int: Number of new vendors imported from GHL
        """
        try:
            # Get dropdown options from GHL
            field_options = self.ghl_api.get_custom_field_options(
                field_key=self.VENDOR_FIELD_KEY,
                location_id=self.location_id
            )
            
            if not field_options:
                print("No vendor options found in GHL dropdown")
                return 0
            
            print(f"Found {len(field_options)} vendor options in GHL...")
            
            new_vendors_count = 0
            for option_value in field_options:
                # Skip empty values
                if not option_value or not option_value.strip():
                    continue
                
                # Check if vendor already exists
                existing = TripVendor.query.filter_by(name=option_value).first()
                if not existing:
                    # Create new vendor
                    vendor = TripVendor(name=option_value.strip())
                    db.session.add(vendor)
                    new_vendors_count += 1
                    print(f"  + Importing vendor: {option_value}")
            
            # Commit all new vendors
            db.session.commit()
            
            if new_vendors_count > 0:
                print(f"✅ Imported {new_vendors_count} new vendors from GHL")
            else:
                print("✅ No new vendors to import (all GHL vendors already in database)")
            
            return new_vendors_count
            
        except Exception as e:
            db.session.rollback()
            print(f"Error syncing vendors from GHL: {e}")
            raise
    
    def add_vendor_to_ghl(self, vendor):
        """
        Add a single vendor to GHL dropdown options.
        
        This appends the vendor name to the existing dropdown options in GHL.
        Called automatically by SQLAlchemy event listener after vendor creation.
        
        Args:
            vendor: TripVendor instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current dropdown options
            current_options = self.ghl_api.get_custom_field_options(
                field_key=self.VENDOR_FIELD_KEY,
                location_id=self.location_id
            )
            
            # Add new vendor if not already in list
            if vendor.name not in current_options:
                current_options.append(vendor.name)
                
                # Update GHL with new options list
                success = self.ghl_api.update_custom_field_options(
                    field_key=self.VENDOR_FIELD_KEY,
                    options=current_options,
                    location_id=self.location_id
                )
                
                if success:
                    print(f"✅ Added vendor '{vendor.name}' to GHL dropdown")
                    return True
                else:
                    print(f"❌ Failed to add vendor '{vendor.name}' to GHL dropdown")
                    return False
            else:
                print(f"Vendor '{vendor.name}' already exists in GHL dropdown")
                return True
                
        except Exception as e:
            print(f"Error adding vendor to GHL: {e}")
            return False
    
    def remove_vendor_from_ghl(self, vendor):
        """
        Remove a single vendor from GHL dropdown options.
        
        This removes the vendor name from the dropdown options in GHL.
        Called automatically by SQLAlchemy event listener before vendor deletion.
        
        Args:
            vendor: TripVendor instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current dropdown options
            current_options = self.ghl_api.get_custom_field_options(
                field_key=self.VENDOR_FIELD_KEY,
                location_id=self.location_id
            )
            
            # Remove vendor if in list
            if vendor.name in current_options:
                current_options.remove(vendor.name)
                
                # Update GHL with new options list
                success = self.ghl_api.update_custom_field_options(
                    field_key=self.VENDOR_FIELD_KEY,
                    options=current_options,
                    location_id=self.location_id
                )
                
                if success:
                    print(f"✅ Removed vendor '{vendor.name}' from GHL dropdown")
                    return True
                else:
                    print(f"❌ Failed to remove vendor '{vendor.name}' from GHL dropdown")
                    return False
            else:
                print(f"Vendor '{vendor.name}' not found in GHL dropdown")
                return True
                
        except Exception as e:
            print(f"Error removing vendor from GHL: {e}")
            return False
    
    def verify_sync(self):
        """
        Verify that database vendors match GHL dropdown options.
        
        Useful for troubleshooting sync issues.
        
        Returns:
            dict: Sync status with details
        """
        try:
            # Get vendors from database
            db_vendors = set(v.name for v in TripVendor.query.all())
            
            # Get vendors from GHL
            ghl_vendors = set(self.ghl_api.get_custom_field_options(
                field_key=self.VENDOR_FIELD_KEY,
                location_id=self.location_id
            ))
            
            # Find differences
            only_in_db = db_vendors - ghl_vendors
            only_in_ghl = ghl_vendors - db_vendors
            in_both = db_vendors & ghl_vendors
            
            status = {
                'in_sync': len(only_in_db) == 0 and len(only_in_ghl) == 0,
                'total_db': len(db_vendors),
                'total_ghl': len(ghl_vendors),
                'in_both': len(in_both),
                'only_in_db': list(only_in_db),
                'only_in_ghl': list(only_in_ghl)
            }
            
            # Print status
            if status['in_sync']:
                print(f"✅ Vendors in sync: {len(in_both)} vendors match")
            else:
                print(f"⚠️  Vendors out of sync:")
                print(f"   Database only: {len(only_in_db)} vendors")
                print(f"   GHL only: {len(only_in_ghl)} vendors")
                if only_in_db:
                    print(f"   DB vendors not in GHL: {', '.join(only_in_db)}")
                if only_in_ghl:
                    print(f"   GHL vendors not in DB: {', '.join(only_in_ghl)}")
            
            return status
            
        except Exception as e:
            print(f"Error verifying sync: {e}")
            raise


# Convenience function for quick access
def get_vendor_sync_service():
    """Get a VendorSyncService instance"""
    return VendorSyncService()