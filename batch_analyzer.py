"""
LCSC Electronics Batch Analysis - Enhanced with CSV Writing
Extends existing Smart Analysis to process multiple emails and write results to CSV
Uses functional programming style consistent with existing codebase
"""

import time
import re
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple
from collections import Counter
from pathlib import Path

from streaming_utils import StreamingEventCollector


def extract_intent_from_response(ai_response: str) -> Tuple[str, str]:
    """Extract primary intent and confidence from AI response"""
    primary_intent = "Unknown"
    confidence_level = "Unknown"
    
    try:
        intent_pattern = r'##\s*Intent Classification(.*?)(?=##|$)'
        intent_match = re.search(intent_pattern, ai_response, re.DOTALL | re.IGNORECASE)
        
        if intent_match:
            intent_content = intent_match.group(1).strip()
            
            primary_match = re.search(r'Primary Intent:\s*([^\n]+)', intent_content, re.IGNORECASE)
            if primary_match:
                primary_intent = primary_match.group(1).strip()
            
            confidence_match = re.search(r'Confidence:\s*([^\n]+)', intent_content, re.IGNORECASE)
            if confidence_match:
                confidence_level = confidence_match.group(1).strip()
    
    except Exception:
        pass
    
    return primary_intent, confidence_level


def extract_order_id_from_response(ai_response: str) -> str:
    """Extract order ID from AI response"""
    try:
        logistics_pattern = r'##\s*Logistics/Order Status(.*?)(?=##|$)'
        logistics_match = re.search(logistics_pattern, ai_response, re.DOTALL | re.IGNORECASE)
        
        if logistics_match:
            logistics_content = logistics_match.group(1).strip()
            order_match = re.search(r'Order ID:\s*([^\n]+)', logistics_content, re.IGNORECASE)
            if order_match:
                return order_match.group(1).strip()
    except Exception:
        pass
    
    return ""


def load_csv_data(csv_path: str) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Load CSV data and create email-ID to row index mapping
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        Tuple of (DataFrame, email_id_to_index_mapping)
    """
    try:
        # Read CSV with proper encoding handling
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        # Create mapping from email-id to DataFrame index
        email_id_mapping = {}
        for idx, row in df.iterrows():
            email_id = row.get('email-id', '')
            if email_id:
                # Store all indices for this email-id (in case of duplicates)
                if email_id not in email_id_mapping:
                    email_id_mapping[email_id] = []
                email_id_mapping[email_id].append(idx)
        
        print(f"📊 Loaded CSV with {len(df)} rows and {len(email_id_mapping)} unique email-IDs")
        return df, email_id_mapping
        
    except Exception as e:
        print(f"❌ Error loading CSV file: {e}")
        return None, {}


def update_csv_with_intents(csv_path: str, intent_results: Dict[str, str], backup: bool = True) -> bool:
    """
    Update CSV file with AI intent classifications
    
    Args:
        csv_path: Path to the CSV file
        intent_results: Dictionary mapping email-id to intent classification
        backup: Whether to create a backup of the original file
        
    Returns:
        bool: Success status
    """
    try:
        # Create backup if requested
        if backup:
            backup_path = csv_path.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
            df_backup = pd.read_csv(csv_path, encoding='utf-8-sig')
            df_backup.to_csv(backup_path, index=False, encoding='utf-8-sig')
            print(f"💾 Backup created: {backup_path}")
        
        # Load current CSV data
        df, email_id_mapping = load_csv_data(csv_path)
        if df is None:
            return False
        
        # Update ai-categ column
        updates_made = 0
        for email_id, intent in intent_results.items():
            if email_id in email_id_mapping:
                # Update all rows with this email-id
                for idx in email_id_mapping[email_id]:
                    df.at[idx, 'ai-categ'] = intent
                    updates_made += 1
                print(f"✅ Updated email-id {email_id}: {intent}")
            else:
                print(f"⚠️  Email-id {email_id} not found in CSV")
        
        # Write updated data back to CSV
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"💾 CSV updated successfully with {updates_made} changes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating CSV file: {e}")
        return False


def process_batch_emails_with_csv_update(email_functions: Dict, csv_path: str = "./intent/lcsc-emails-intent.csv", max_emails: int = None) -> Dict:
    """
    Process emails in batch and update CSV with intent classifications
    
    Args:
        email_functions: Email processing functions from email_manager
        csv_path: Path to the CSV file to update
        max_emails: Maximum number of emails to process (None for all)
        
    Returns:
        Dict: Batch processing results and statistics
    """
    # Verify CSV file exists
    if not Path(csv_path).exists():
        print(f"❌ CSV file not found: {csv_path}")
        return {"error": "CSV file not found"}
    
    emails = email_functions['get_emails']()
    total_emails = len(emails)
    
    # Limit emails if specified
    if max_emails and max_emails < total_emails:
        emails = emails[:max_emails]
        total_emails = max_emails
    
    print(f"\n🚀 Starting batch analysis of {total_emails} emails with CSV update...")
    print(f"📄 Target CSV: {csv_path}")
    print("="*80)
    
    results = []
    intent_results = {}  # email-id -> intent mapping for CSV update
    start_time = time.time()
    
    for i, email in enumerate(emails):
        email_id = email.get('email_id', '')
        print(f"📧 Processing email {i+1}/{total_emails}")
        print(f"   Email ID: {email_id}")
        print(f"   Sender: {email.get('sender', 'Unknown')}")
        
        email_start_time = time.time()
        
        try:
            # Use existing Smart Analysis functionality
            collector = StreamingEventCollector()
            
            # Process with existing streaming function
            for event in email_functions['process_with_ai_streaming'](email['content'], email.get('sender', '')):
                collector.add_event(event)
                
                if "error" in event:
                    raise Exception(event["error"])
            
            # Get AI response
            ai_response = collector.get_final_response()
            processing_time = time.time() - email_start_time
            
            if ai_response and ai_response != "No response generated. Please check the thinking process for details.":
                # Extract key information
                primary_intent, confidence_level = extract_intent_from_response(ai_response)
                order_id = extract_order_id_from_response(ai_response)
                
                # Store intent result for CSV update
                if email_id and primary_intent != "Unknown":
                    intent_results[email_id] = primary_intent
                
                result = {
                    'email_id': email_id,
                    'sender': email.get('sender', ''),
                    'status': 'completed',
                    'processing_time': processing_time,
                    'primary_intent': primary_intent,
                    'confidence_level': confidence_level,
                    'order_id': order_id,
                    'response_length': len(ai_response)
                }
                
                print(f"   ✅ Status: Completed")
                print(f"   🎯 Intent: {primary_intent}")
                print(f"   📊 Confidence: {confidence_level}")
                if order_id:
                    print(f"   📦 Order ID: {order_id}")
                print(f"   ⏱️  Time: {processing_time:.2f}s")
                
            else:
                result = {
                    'email_id': email_id,
                    'sender': email.get('sender', ''),
                    'status': 'failed',
                    'processing_time': processing_time,
                    'error': 'No AI response generated'
                }
                print(f"   ❌ Status: Failed - No AI response")
            
        except Exception as e:
            processing_time = time.time() - email_start_time
            result = {
                'email_id': email_id,
                'sender': email.get('sender', ''),
                'status': 'failed',
                'processing_time': processing_time,
                'error': str(e)
            }
            print(f"   ❌ Status: Failed - {str(e)}")
        
        results.append(result)
        print("-" * 80)
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.5)
    
    total_time = time.time() - start_time
    
    # Update CSV with intent results
    print(f"\n📝 Updating CSV with {len(intent_results)} intent classifications...")
    csv_update_success = update_csv_with_intents(csv_path, intent_results)
    
    # Generate statistics
    stats = generate_batch_statistics(results, total_time)
    stats['csv_update_success'] = csv_update_success
    stats['csv_updates_made'] = len(intent_results)
    
    # Print summary report
    print_batch_summary_report(stats)
    
    return {
        'results': results,
        'statistics': stats,
        'total_processing_time': total_time,
        'intent_results': intent_results,
        'csv_updated': csv_update_success
    }


    """
    Process emails in batch using existing Smart Analysis functionality
    
    Args:
        email_functions: Email processing functions from email_manager
        max_emails: Maximum number of emails to process (None for all)
        
    Returns:
        Dict: Batch processing results and statistics
    """
    emails = email_functions['get_emails']()
    total_emails = len(emails)
    
    # Limit emails if specified
    if max_emails and max_emails < total_emails:
        emails = emails[:max_emails]
        total_emails = max_emails
    
    print(f"\n🚀 Starting batch analysis of {total_emails} emails...")
    print("="*80)
    
    results = []
    start_time = time.time()
    
    for i, email in enumerate(emails):
        print(f"📧 Processing email {i+1}/{total_emails}")
        print(f"   Email ID: {email.get('email_id', 'Unknown')}")
        print(f"   Sender: {email.get('sender', 'Unknown')}")
        
        email_start_time = time.time()
        
        try:
            # Use existing Smart Analysis functionality
            collector = StreamingEventCollector()
            
            # Process with existing streaming function
            for event in email_functions['process_with_ai_streaming'](email['content'], email.get('sender', '')):
                collector.add_event(event)
                
                if "error" in event:
                    raise Exception(event["error"])
            
            # Get AI response
            ai_response = collector.get_final_response()
            processing_time = time.time() - email_start_time
            
            if ai_response and ai_response != "No response generated. Please check the thinking process for details.":
                # Extract key information
                primary_intent, confidence_level = extract_intent_from_response(ai_response)
                order_id = extract_order_id_from_response(ai_response)
                
                result = {
                    'email_id': email.get('email_id', ''),
                    'sender': email.get('sender', ''),
                    'status': 'completed',
                    'processing_time': processing_time,
                    'primary_intent': primary_intent,
                    'confidence_level': confidence_level,
                    'order_id': order_id,
                    'response_length': len(ai_response)
                }
                
                print(f"   ✅ Status: Completed")
                print(f"   🎯 Intent: {primary_intent}")
                print(f"   📊 Confidence: {confidence_level}")
                if order_id:
                    print(f"   📦 Order ID: {order_id}")
                print(f"   ⏱️  Time: {processing_time:.2f}s")
                
            else:
                result = {
                    'email_id': email.get('email_id', ''),
                    'sender': email.get('sender', ''),
                    'status': 'failed',
                    'processing_time': processing_time,
                    'error': 'No AI response generated'
                }
                print(f"   ❌ Status: Failed - No AI response")
            
        except Exception as e:
            processing_time = time.time() - email_start_time
            result = {
                'email_id': email.get('email_id', ''),
                'sender': email.get('sender', ''),
                'status': 'failed',
                'processing_time': processing_time,
                'error': str(e)
            }
            print(f"   ❌ Status: Failed - {str(e)}")
        
        results.append(result)
        print("-" * 80)
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.5)
    
    total_time = time.time() - start_time
    
    # Generate statistics
    stats = generate_batch_statistics(results, total_time)
    
    # Print summary report
    print_batch_summary_report(stats)
    
    return {
        'results': results,
        'statistics': stats,
        'total_processing_time': total_time
    }


def generate_batch_statistics(results: List[Dict], total_time: float) -> Dict:
    """Generate statistics from batch processing results"""
    completed = [r for r in results if r['status'] == 'completed']
    failed = [r for r in results if r['status'] == 'failed']
    
    # Intent distribution
    intent_counter = Counter()
    confidence_counter = Counter()
    
    for result in completed:
        if result.get('primary_intent'):
            intent_counter[result['primary_intent']] += 1
        if result.get('confidence_level'):
            confidence_counter[result['confidence_level']] += 1
    
    # Processing time statistics
    processing_times = [r['processing_time'] for r in results]
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    return {
        'total_emails': len(results),
        'completed_emails': len(completed),
        'failed_emails': len(failed),
        'success_rate': (len(completed) / len(results)) * 100 if results else 0,
        'total_processing_time': total_time,
        'average_processing_time': avg_processing_time,
        'intent_distribution': dict(intent_counter),
        'confidence_distribution': dict(confidence_counter),
        'orders_found': len([r for r in completed if r.get('order_id')]),
        'average_response_length': sum(r.get('response_length', 0) for r in completed) // max(1, len(completed))
    }


def print_batch_summary_report(stats: Dict):
    """Print comprehensive batch analysis summary to console"""
    print("\n" + "="*80)
    print("📊 BATCH ANALYSIS SUMMARY REPORT")
    print("="*80)
    
    # Basic Statistics
    print(f"📧 Total Emails: {stats['total_emails']}")
    print(f"✅ Successfully Processed: {stats['completed_emails']}")
    print(f"❌ Failed: {stats['failed_emails']}")
    print(f"📈 Success Rate: {stats['success_rate']:.1f}%")
    print(f"⏱️  Total Time: {stats['total_processing_time']:.2f} seconds")
    print(f"⚡ Average Time per Email: {stats['average_processing_time']:.2f} seconds")
    
    # CSV Update Status
    if 'csv_update_success' in stats:
        print(f"\n💾 CSV UPDATE STATUS")
        print("-" * 50)
        print(f"   Update Success: {'✅ Yes' if stats['csv_update_success'] else '❌ No'}")
        print(f"   Records Updated: {stats.get('csv_updates_made', 0)}")
    
    # Intent Classification Results
    if stats['intent_distribution']:
        print(f"\n🎯 INTENT CLASSIFICATION RESULTS")
        print("-" * 50)
        for intent, count in sorted(stats['intent_distribution'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['completed_emails']) * 100
            print(f"   {intent}: {count} emails ({percentage:.1f}%)")
    
    # Confidence Distribution
    if stats['confidence_distribution']:
        print(f"\n📊 CONFIDENCE LEVEL DISTRIBUTION")
        print("-" * 50)
        for confidence, count in sorted(stats['confidence_distribution'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['completed_emails']) * 100
            print(f"   {confidence}: {count} emails ({percentage:.1f}%)")
    
    # Order Processing
    if stats['orders_found'] > 0:
        print(f"\n📦 ORDER PROCESSING")
        print("-" * 50)
        print(f"   Orders Found: {stats['orders_found']}")
    
    # Response Statistics
    print(f"\n📝 RESPONSE STATISTICS")
    print("-" * 50)
    print(f"   Average Response Length: {stats['average_response_length']} characters")
    
    print("\n" + "="*80)
    print(f"📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)


def create_batch_processor_with_csv(email_functions: Dict, csv_path: str = "./intent/lcsc-emails-intent.csv"):
    """
    Create batch processing function with CSV update capability
    
    Args:
        email_functions: Email processing functions from email_manager
        csv_path: Path to the CSV file to update
        
    Returns:
        callable: Enhanced batch processing function
    """
    def run_batch_analysis_with_csv(max_emails: int = None):
        return process_batch_emails_with_csv_update(email_functions, csv_path, max_emails)
    
    return run_batch_analysis_with_csv


# Legacy function for backward compatibility
def process_batch_emails(email_functions: Dict, max_emails: int = None) -> Dict:
    """
    Original batch processing function (now with CSV update)
    Enhanced to include CSV writing functionality
    """
    return process_batch_emails_with_csv_update(email_functions, "./intent/lcsc-emails-intent.csv", max_emails)


def create_batch_processor(email_functions: Dict):
    """
    Original batch processor creator (now with CSV update)
    Enhanced to include CSV writing functionality
    """
    def run_batch_analysis(max_emails: int = None):
        return process_batch_emails(email_functions, max_emails)
    
    return run_batch_analysis
