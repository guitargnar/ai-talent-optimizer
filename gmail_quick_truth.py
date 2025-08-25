#!/usr/bin/env python3
"""
Gmail Quick Truth Analysis - Fast analysis of job application emails
"""

import pickle
import os
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import re

def quick_analysis():
    """Quick analysis of Gmail for job applications"""
    
    # Load existing token
    if not os.path.exists('token.pickle'):
        print("❌ No token.pickle found. Run gmail_oauth_integration.py first")
        return
        
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
    
    if creds.expired:
        creds.refresh(Request())
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('gmail', 'v1', credentials=creds)
    
    print("🔍 GMAIL TRUTH ANALYSIS")
    print("="*60)
    
    # 1. Check sent emails with "matthew scott" and resume keywords
    print("\n📤 SENT APPLICATIONS (Last 30 days):")
    print("-"*40)
    
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y/%m/%d')
    
    # Search for sent job applications
    sent_query = f'in:sent after:{thirty_days_ago} (resume OR application OR "cover letter" OR "matthew scott")'
    
    try:
        sent_results = service.users().messages().list(
            userId='me',
            q=sent_query,
            maxResults=100
        ).execute()
        
        sent_messages = sent_results.get('messages', [])
        print(f"Found {len(sent_messages)} sent job-related emails")
        
        sent_companies = []
        for msg in sent_messages[:20]:  # Analyze first 20
            try:
                message = service.users().messages().get(userId='me', id=msg['id']).execute()
                headers = message['payload'].get('headers', [])
                
                to_email = ''
                subject = ''
                date = ''
                
                for header in headers:
                    if header['name'] == 'To':
                        to_email = header['value']
                    elif header['name'] == 'Subject':
                        subject = header['value']
                    elif header['name'] == 'Date':
                        date = header['value']
                
                if to_email:
                    # Extract company from email
                    company_match = re.search(r'@([\w\.-]+)', to_email)
                    if company_match:
                        company = company_match.group(1).replace('.com', '').replace('.io', '')
                        sent_companies.append(company)
                        print(f"  ✉️  {company}: {to_email}")
                        print(f"     Subject: {subject[:50]}...")
                        
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error searching sent emails: {e}")
    
    # 2. Check for responses
    print("\n📥 RESPONSES RECEIVED:")
    print("-"*40)
    
    # Search for common response patterns
    response_queries = [
        'subject:"thank you for applying"',
        'subject:"application received"', 
        'subject:"interview"',
        'subject:"next steps"',
        '"we have received your application"',
        '"unfortunately"'
    ]
    
    all_responses = []
    for query in response_queries:
        try:
            results = service.users().messages().list(
                userId='me',
                q=f'{query} after:{thirty_days_ago}',
                maxResults=20
            ).execute()
            
            messages = results.get('messages', [])
            for msg in messages:
                try:
                    message = service.users().messages().get(userId='me', id=msg['id']).execute()
                    headers = message['payload'].get('headers', [])
                    
                    from_email = ''
                    subject = ''
                    
                    for header in headers:
                        if header['name'] == 'From':
                            from_email = header['value']
                        elif header['name'] == 'Subject':
                            subject = header['value']
                    
                    if from_email and subject:
                        all_responses.append({
                            'from': from_email,
                            'subject': subject,
                            'query': query
                        })
                        
                except Exception:
                    continue
                    
        except Exception as e:
            continue
    
    # Deduplicate and display responses
    seen = set()
    interview_count = 0
    rejection_count = 0
    acknowledgment_count = 0
    
    for resp in all_responses:
        key = resp['from'] + resp['subject']
        if key not in seen:
            seen.add(key)
            
            # Categorize
            subject_lower = resp['subject'].lower()
            if 'interview' in subject_lower or 'next steps' in subject_lower:
                print(f"  🎯 INTERVIEW: {resp['from'][:50]}")
                print(f"     {resp['subject'][:60]}")
                interview_count += 1
            elif 'unfortunately' in subject_lower or 'regret' in subject_lower:
                print(f"  ❌ REJECTION: {resp['from'][:50]}")
                print(f"     {resp['subject'][:60]}")
                rejection_count += 1
            else:
                print(f"  ✅ ACKNOWLEDGMENT: {resp['from'][:50]}")
                print(f"     {resp['subject'][:60]}")
                acknowledgment_count += 1
    
    # 3. Check BCC tracking
    print("\n📋 BCC TRACKING CHECK:")
    print("-"*40)
    
    bcc_query = 'to:matthewdscott7+jobapps@gmail.com'
    try:
        bcc_results = service.users().messages().list(
            userId='me',
            q=bcc_query,
            maxResults=50
        ).execute()
        
        bcc_messages = bcc_results.get('messages', [])
        print(f"Found {len(bcc_messages)} BCC tracking emails")
        
    except Exception as e:
        print(f"Error checking BCC: {e}")
    
    # 4. Summary
    print("\n📊 SUMMARY:")
    print("="*60)
    print(f"Sent Applications: {len(sent_messages)}")
    print(f"Total Responses: {len(seen)}")
    print(f"  - Interview Invitations: {interview_count}")
    print(f"  - Rejections: {rejection_count}")
    print(f"  - Acknowledgments: {acknowledgment_count}")
    
    if len(sent_messages) > 0:
        response_rate = (len(seen) / len(sent_messages)) * 100
        print(f"Response Rate: {response_rate:.1f}%")
        
        interview_rate = (interview_count / len(sent_messages)) * 100
        print(f"Interview Rate: {interview_rate:.1f}%")
    
    print("\n💡 KEY INSIGHTS:")
    if interview_count == 0:
        print("  ⚠️  No interview invitations found in last 30 days")
        print("  💡 Consider: Following up on sent applications")
        print("  💡 Consider: Adjusting resume/cover letter approach")
    
    if len(sent_companies) > 0:
        print(f"\n🏢 Companies Applied To: {', '.join(set(sent_companies)[:10])}")

if __name__ == "__main__":
    quick_analysis()