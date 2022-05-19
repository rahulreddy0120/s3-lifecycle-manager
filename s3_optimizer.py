#!/usr/bin/env python3
"""
AWS S3 Lifecycle Optimizer
Identifies S3 buckets without lifecycle policies and recommends optimizations
"""

import boto3
import yaml
import csv
import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

class S3LifecycleOptimizer:
    def __init__(self, config_file='config.yaml'):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.s3_client = boto3.client('s3')
        self.cloudwatch = boto3.client('cloudwatch')
        
    def get_all_buckets(self):
        """Get all S3 buckets"""
        response = self.s3_client.list_buckets()
        return response['Buckets']
    
    def get_bucket_lifecycle(self, bucket_name):
        """Get lifecycle configuration for a bucket"""
        try:
            response = self.s3_client.get_bucket_lifecycle_configuration(
                Bucket=bucket_name
            )
            return response.get('Rules', [])
        except self.s3_client.exceptions.NoSuchLifecycleConfiguration:
            return None
        except Exception as e:
            print(f"   ⚠️  Error getting lifecycle for {bucket_name}: {e}")
            return None
    
    def get_bucket_size(self, bucket_name):
        """Get bucket size from CloudWatch metrics"""
        try:
            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=[
                    {'Name': 'BucketName', 'Value': bucket_name},
                    {'Name': 'StorageType', 'Value': 'StandardStorage'}
                ],
                StartTime=datetime.now() - timedelta(days=2),
                EndTime=datetime.now(),
                Period=86400,
                Statistics=['Average']
            )
            
            if response['Datapoints']:
                size_bytes = response['Datapoints'][0]['Average']
                return size_bytes
            return 0
        except Exception as e:
            return 0
    
    def get_bucket_object_count(self, bucket_name):
        """Get number of objects in bucket"""
        try:
            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='NumberOfObjects',
                Dimensions=[
                    {'Name': 'BucketName', 'Value': bucket_name},
                    {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
                ],
                StartTime=datetime.now() - timedelta(days=2),
                EndTime=datetime.now(),
                Period=86400,
                Statistics=['Average']
            )
            
            if response['Datapoints']:
                return int(response['Datapoints'][0]['Average'])
            return 0
        except Exception:
            return 0
    
    def calculate_current_cost(self, size_bytes, storage_class='standard'):
        """Calculate current monthly storage cost"""
        size_gb = size_bytes / (1024 ** 3)
        cost_per_gb = self.config['analysis']['storage_costs'][storage_class]
        return size_gb * cost_per_gb
    
    def recommend_lifecycle_policy(self, bucket_name, size_bytes, object_count):
        """Generate lifecycle policy recommendation"""
        size_gb = size_bytes / (1024 ** 3)
        
        if size_gb < 1:
            return None, 0  # Too small to optimize
        
        current_cost = self.calculate_current_cost(size_bytes, 'standard')
        
        # Determine best strategy based on bucket characteristics
        if 'log' in bucket_name.lower() or 'backup' in bucket_name.lower():
            # Logs/backups: aggressive archival
            recommendation = {
                'strategy': 'Intelligent-Tiering + Glacier',
                'transitions': [
                    {'days': 30, 'storage_class': 'INTELLIGENT_TIERING'},
                    {'days': 90, 'storage_class': 'GLACIER_IR'}
                ],
                'estimated_cost': size_gb * 0.004,  # Mostly Glacier
                'savings_percentage': 83
            }
        elif 'archive' in bucket_name.lower():
            # Archives: immediate deep archive
            recommendation = {
                'strategy': 'Deep Archive',
                'transitions': [
                    {'days': 0, 'storage_class': 'DEEP_ARCHIVE'}
                ],
                'estimated_cost': size_gb * 0.00099,
                'savings_percentage': 96
            }
        else:
            # General purpose: Intelligent-Tiering
            recommendation = {
                'strategy': 'Intelligent-Tiering',
                'transitions': [
                    {'days': 30, 'storage_class': 'INTELLIGENT_TIERING'}
                ],
                'estimated_cost': size_gb * 0.0025,
                'savings_percentage': 89
            }
        
        savings = current_cost - recommendation['estimated_cost']
        return recommendation, savings
    
    def audit_buckets(self):
        """Audit all S3 buckets for lifecycle policies"""
        print("🗂️  S3 Lifecycle Optimization Audit")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        buckets = self.get_all_buckets()
        print(f"\nFound {len(buckets)} buckets")
        
        audit_results = []
        total_size = 0
        total_cost = 0
        total_savings = 0
        buckets_without_lifecycle = 0
        
        for bucket in buckets:
            bucket_name = bucket['Name']
            print(f"\n📦 Analyzing: {bucket_name}")
            
            # Get lifecycle policy
            lifecycle = self.get_bucket_lifecycle(bucket_name)
            has_lifecycle = lifecycle is not None
            
            # Get bucket metrics
            size_bytes = self.get_bucket_size(bucket_name)
            object_count = self.get_bucket_object_count(bucket_name)
            size_gb = size_bytes / (1024 ** 3)
            
            current_cost = self.calculate_current_cost(size_bytes)
            
            print(f"   Size: {size_gb:.2f} GB")
            print(f"   Objects: {object_count:,}")
            print(f"   Lifecycle Policy: {'✅ Yes' if has_lifecycle else '❌ No'}")
            print(f"   Current Cost: ${current_cost:.2f}/month")
            
            # Generate recommendation if no lifecycle
            recommendation = None
            savings = 0
            if not has_lifecycle and size_gb > 1:
                recommendation, savings = self.recommend_lifecycle_policy(
                    bucket_name, size_bytes, object_count
                )
                if recommendation:
                    print(f"   💡 Recommendation: {recommendation['strategy']}")
                    print(f"   💰 Potential Savings: ${savings:.2f}/month ({recommendation['savings_percentage']}%)")
                    buckets_without_lifecycle += 1
                    total_savings += savings
            
            total_size += size_bytes
            total_cost += current_cost
            
            audit_results.append({
                'bucket_name': bucket_name,
                'size_gb': round(size_gb, 2),
                'object_count': object_count,
                'has_lifecycle': has_lifecycle,
                'current_cost': round(current_cost, 2),
                'recommendation': recommendation['strategy'] if recommendation else 'N/A',
                'potential_savings': round(savings, 2)
            })
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 Summary")
        print("=" * 70)
        print(f"Total Buckets: {len(buckets)}")
        print(f"Buckets without Lifecycle: {buckets_without_lifecycle}")
        print(f"Total Storage: {total_size / (1024**4):.2f} TB")
        print(f"Current Monthly Cost: ${total_cost:.2f}")
        print(f"Potential Monthly Savings: ${total_savings:.2f}")
        print(f"Potential Annual Savings: ${total_savings * 12:.2f}")
        
        return audit_results
    
    def generate_lifecycle_policy(self, recommendation):
        """Generate S3 lifecycle policy JSON"""
        rules = []
        
        for i, transition in enumerate(recommendation['transitions']):
            rule = {
                'Id': f'OptimizationRule{i+1}',
                'Status': 'Enabled',
                'Transitions': [
                    {
                        'Days': transition['days'],
                        'StorageClass': transition['storage_class']
                    }
                ]
            }
            rules.append(rule)
        
        return {'Rules': rules}
    
    def apply_lifecycle_policy(self, bucket_name, policy, dry_run=True):
        """Apply lifecycle policy to bucket"""
        if dry_run:
            print(f"[DRY RUN] Would apply policy to {bucket_name}:")
            print(json.dumps(policy, indent=2))
            return True
        
        try:
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration=policy
            )
            print(f"✅ Applied lifecycle policy to {bucket_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to apply policy to {bucket_name}: {e}")
            return False
    
    def export_to_csv(self, results, output_file):
        """Export audit results to CSV"""
        with open(output_file, 'w', newline='') as f:
            fieldnames = ['bucket_name', 'size_gb', 'object_count', 'has_lifecycle',
                         'current_cost', 'recommendation', 'potential_savings']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\n✅ Report saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='AWS S3 Lifecycle Optimizer')
    parser.add_argument('--mode', choices=['audit', 'recommend', 'apply'],
                       required=True, help='Operation mode')
    parser.add_argument('--config', default='config.yaml', help='Config file')
    parser.add_argument('--output', help='Output CSV file')
    parser.add_argument('--bucket', help='Specific bucket name')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    optimizer = S3LifecycleOptimizer(config_file=args.config)
    
    if args.mode == 'audit':
        results = optimizer.audit_buckets()
        if args.output:
            optimizer.export_to_csv(results, args.output)
    
    elif args.mode == 'recommend':
        results = optimizer.audit_buckets()
        if args.output:
            optimizer.export_to_csv(results, args.output)
    
    elif args.mode == 'apply':
        print("Apply mode not yet implemented")

if __name__ == '__main__':
    main()
