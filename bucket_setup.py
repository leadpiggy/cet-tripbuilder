import boto3
import os
from dotenv import load_dotenv
import json
from botocore.exceptions import ClientError

load_dotenv()

boto_user_pw = os.getenv("BOTO_USER_PW", "CETcrm2025!")
boto_user_name = os.getenv("BOTO_USER_NAME", "python-s3-setup")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)


# Configure session
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name='us-east-1'  # Change to your region
)

# Now use this session for AWS operations
s3 = session.client('s3')
iam = session.client('iam')

def setup_pdf_bucket(bucket_name):    
    try:
        # Create bucket
        print(f"Creating bucket: {bucket_name}")
        s3.create_bucket(Bucket=bucket_name)
        
        # Configure public access
        print("Configuring public access settings")
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )
        
        # Set bucket policy for public read access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadForPDFs",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    "Condition": {
                        "StringEquals": {
                            "s3:ExistingObjectTag/Public": "yes"
                        }
                    }
                }
            ]
        }
        
        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        
        # Configure CORS
        cors_configuration = {
            'CORSRules': [{
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': [],
                'MaxAgeSeconds': 3000
            }]
        }
        s3.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )
        
        # Enable versioning
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
        # Create IAM user for Cyberduck
        user_name = f"{bucket_name}-ftp-user"
        print(f"Creating IAM user: {user_name}")
        
        try:
            iam.create_user(UserName=user_name)
        except iam.exceptions.EntityAlreadyExistsException:
            print(f"User {user_name} already exists")
        
        # Attach S3 access policy
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3:DeleteObject"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            }]
        }
        
        policy_name = f"{bucket_name}-s3-access"
        try:
            iam.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document)
            )
        except iam.exceptions.EntityAlreadyExistsException:
            print(f"Policy {policy_name} already exists")
        
        policy_arn = f"arn:aws:iam::{boto3.client('sts').get_caller_identity()['Account']}:policy/{policy_name}"
        iam.attach_user_policy(
            UserName=user_name,
            PolicyArn=policy_arn
        )
        
        # Create access keys
        response = iam.create_access_key(UserName=user_name)
        access_key = response['AccessKey']['AccessKeyId']
        secret_key = response['AccessKey']['SecretAccessKey']
        
        # Generate Cyberduck connection profile
        cyberduck_profile = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Protocol</key>
            <string>s3</string>
            <key>Vendor</key>
            <string>aws</string>
            <key>Access Key ID</key>
            <string>{access_key}</string>
            <key>Secret Access Key</key>
            <string>{secret_key}</string>
            <key>Region</key>
            <string>{s3.meta.region_name}</string>
            <key>Bucket</key>
            <string>{bucket_name}</string>
        </dict>
        </plist>
        """
        
        # Save Cyberduck profile
        with open(f"{bucket_name}.cyberduckprofile", "w+") as f:
            f.write(cyberduck_profile)
        
        print("\n" + "="*50)
        print("SETUP COMPLETE")
        print("="*50)
        print(f"\nPDF Access URL: https://{bucket_name}.s3.amazonaws.com/")
        print(f"\nCyberduck Credentials:")
        print(f"  Access Key: {access_key}")
        print(f"  Secret Key: {secret_key}")
        print("\nCyberduck Profile saved to:", f"{bucket_name}.cyberduckprofile")
        print("\nInstructions:")
        print("1. Double-click the Cyberduck profile to add the connection")
        print("2. Drag-and-drop PDFs into Cyberduck to upload")
        print("3. To make a PDF public, add tag: Public=yes")
        print(f"4. Access PDF at: https://{bucket_name}.s3.amazonaws.com/FILENAME.pdf")
        
        return {
            'bucket': bucket_name,
            'access_key': access_key,
            'secret_key': secret_key,
            'region': s3.meta.region_name
        }
        
    except ClientError as e:
        print(f"Error: {e.response['Error']['Message']}")
        return None

if __name__ == "__main__":
    # Configure your bucket name (must be globally unique)
    bucket_name = "cet-uploads"  # CHANGE TO UNIQUE NAME

    resp = setup_pdf_bucket(bucket_name)
    print(resp)