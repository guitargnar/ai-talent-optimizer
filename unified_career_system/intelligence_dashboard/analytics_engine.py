#!/usr/bin/env python3
"""
Performance Analytics Engine
Advanced analytics and predictive insights for career optimization
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np
from collections import defaultdict, Counter
import statistics

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from unified_career_system.data_layer.master_database import MasterDatabase

class AnalyticsEngine:
    """Advanced analytics for career automation performance"""
    
    def __init__(self):
        self.db = MasterDatabase()
        
        # Analytics configuration
        self.metrics = {
            'response_rate': {'target': 15, 'weight': 0.3},
            'interview_rate': {'target': 10, 'weight': 0.4},
            'offer_rate': {'target': 5, 'weight': 0.3},
            'application_velocity': {'target': 50, 'weight': 0.2},
            'ml_accuracy': {'target': 80, 'weight': 0.2}
        }
        
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive analytics report"""
        print("\n📊 GENERATING COMPREHENSIVE ANALYTICS...")
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'executive_summary': self._generate_executive_summary(),
            'performance_metrics': self._calculate_performance_metrics(),
            'trend_analysis': self._analyze_trends(),
            'company_insights': self._analyze_companies(),
            'optimization_recommendations': self._generate_recommendations(),
            'predictive_analysis': self._predictive_analysis(),
            'roi_analysis': self._calculate_roi()
        }
        
        return report
    
    def _generate_executive_summary(self) -> Dict:
        """Generate executive summary"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Key metrics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_applications,
                COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) as total_responses,
                COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews,
                COUNT(CASE WHEN response_type = 'offer' THEN 1 END) as offers
            FROM master_applications
        """)
        
        metrics = cursor.fetchone()
        
        # Time metrics
        cursor.execute("""
            SELECT 
                MIN(applied_at) as first_application,
                MAX(applied_at) as last_application,
                julianday(MAX(applied_at)) - julianday(MIN(applied_at)) as days_active
            FROM master_applications
        """)
        
        time_metrics = cursor.fetchone()
        
        conn.close()
        
        summary = {
            'total_applications': metrics[0],
            'total_responses': metrics[1],
            'interviews_scheduled': metrics[2],
            'offers_received': metrics[3],
            'response_rate': round(metrics[1] * 100.0 / max(metrics[0], 1), 1),
            'interview_rate': round(metrics[2] * 100.0 / max(metrics[0], 1), 1),
            'offer_rate': round(metrics[3] * 100.0 / max(metrics[0], 1), 1),
            'days_active': int(time_metrics[2]) if time_metrics[2] else 0,
            'daily_average': round(metrics[0] / max(time_metrics[2], 1), 1) if time_metrics[2] else 0
        }
        
        # Add performance grade
        summary['performance_grade'] = self._calculate_grade(summary)
        
        return summary
    
    def _calculate_grade(self, metrics: Dict) -> str:
        """Calculate overall performance grade"""
        score = 0
        
        # Response rate (0-30 points)
        if metrics['response_rate'] >= 20:
            score += 30
        elif metrics['response_rate'] >= 15:
            score += 25
        elif metrics['response_rate'] >= 10:
            score += 20
        elif metrics['response_rate'] >= 5:
            score += 10
        
        # Interview rate (0-40 points)
        if metrics['interview_rate'] >= 15:
            score += 40
        elif metrics['interview_rate'] >= 10:
            score += 35
        elif metrics['interview_rate'] >= 7:
            score += 25
        elif metrics['interview_rate'] >= 5:
            score += 15
        
        # Daily average (0-30 points)
        if metrics['daily_average'] >= 30:
            score += 30
        elif metrics['daily_average'] >= 20:
            score += 25
        elif metrics['daily_average'] >= 10:
            score += 15
        elif metrics['daily_average'] >= 5:
            score += 10
        
        # Convert to grade
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        else:
            return 'C-'
    
    def _calculate_performance_metrics(self) -> Dict:
        """Calculate detailed performance metrics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        metrics = {}
        
        # Application metrics by time period
        for period_name, days in [('last_7_days', 7), ('last_30_days', 30), ('last_90_days', 90)]:
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as applications,
                    COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) as responses,
                    COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews,
                    COUNT(CASE WHEN response_type = 'offer' THEN 1 END) as offers
                FROM master_applications
                WHERE datetime(applied_at) > datetime('now', '-{days} days')
            """)
            
            result = cursor.fetchone()
            metrics[period_name] = {
                'applications': result[0],
                'responses': result[1],
                'interviews': result[2],
                'offers': result[3],
                'response_rate': round(result[1] * 100.0 / max(result[0], 1), 1),
                'interview_rate': round(result[2] * 100.0 / max(result[0], 1), 1)
            }
        
        # Channel performance
        cursor.execute("""
            SELECT 
                application_channel,
                COUNT(*) as total,
                COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) as responses,
                COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews
            FROM master_applications
            GROUP BY application_channel
        """)
        
        metrics['by_channel'] = {}
        for row in cursor.fetchall():
            metrics['by_channel'][row[0]] = {
                'total': row[1],
                'responses': row[2],
                'interviews': row[3],
                'effectiveness': round(row[3] * 100.0 / max(row[1], 1), 1)
            }
        
        conn.close()
        return metrics
    
    def _analyze_trends(self) -> Dict:
        """Analyze application and response trends"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        trends = {}
        
        # Weekly trends
        cursor.execute("""
            SELECT 
                strftime('%Y-W%W', applied_at) as week,
                COUNT(*) as applications,
                COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) as responses,
                COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews
            FROM master_applications
            GROUP BY week
            ORDER BY week DESC
            LIMIT 12
        """)
        
        weekly_data = []
        for row in cursor.fetchall():
            weekly_data.append({
                'week': row[0],
                'applications': row[1],
                'responses': row[2],
                'interviews': row[3],
                'response_rate': round(row[2] * 100.0 / max(row[1], 1), 1)
            })
        
        trends['weekly'] = weekly_data
        
        # Calculate trend direction
        if len(weekly_data) >= 2:
            recent = weekly_data[0]['response_rate']
            previous = weekly_data[1]['response_rate']
            
            if recent > previous * 1.1:
                trends['direction'] = 'improving'
            elif recent < previous * 0.9:
                trends['direction'] = 'declining'
            else:
                trends['direction'] = 'stable'
        
        # Best performing days
        cursor.execute("""
            SELECT 
                CASE strftime('%w', applied_at)
                    WHEN '0' THEN 'Sunday'
                    WHEN '1' THEN 'Monday'
                    WHEN '2' THEN 'Tuesday'
                    WHEN '3' THEN 'Wednesday'
                    WHEN '4' THEN 'Thursday'
                    WHEN '5' THEN 'Friday'
                    WHEN '6' THEN 'Saturday'
                END as day_name,
                COUNT(*) as applications,
                COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews,
                ROUND(
                    COUNT(CASE WHEN response_type = 'interview' THEN 1 END) * 100.0 / 
                    COUNT(*), 1
                ) as interview_rate
            FROM master_applications
            GROUP BY strftime('%w', applied_at)
            ORDER BY interview_rate DESC
        """)
        
        trends['best_days'] = [dict(zip(['day', 'applications', 'interviews', 'rate'], row)) 
                               for row in cursor.fetchall()]
        
        # Best performing hours
        cursor.execute("""
            SELECT 
                strftime('%H', applied_at) as hour,
                COUNT(*) as applications,
                COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews,
                ROUND(
                    COUNT(CASE WHEN response_type = 'interview' THEN 1 END) * 100.0 / 
                    COUNT(*), 1
                ) as interview_rate
            FROM master_applications
            GROUP BY hour
            HAVING COUNT(*) >= 3
            ORDER BY interview_rate DESC
            LIMIT 5
        """)
        
        trends['best_hours'] = [dict(zip(['hour', 'applications', 'interviews', 'rate'], row)) 
                                for row in cursor.fetchall()]
        
        conn.close()
        return trends
    
    def _analyze_companies(self) -> Dict:
        """Analyze company-specific insights"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        insights = {}
        
        # Top responsive companies
        cursor.execute("""
            SELECT 
                company,
                COUNT(*) as applications,
                COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) as responses,
                COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews,
                AVG(julianday(response_received_at) - julianday(applied_at)) as avg_response_days
            FROM master_applications
            GROUP BY company
            HAVING COUNT(*) >= 1
            ORDER BY 
                CAST(COUNT(CASE WHEN response_type = 'interview' THEN 1 END) AS FLOAT) / COUNT(*) DESC,
                COUNT(*) DESC
            LIMIT 10
        """)
        
        insights['top_companies'] = []
        for row in cursor.fetchall():
            insights['top_companies'].append({
                'company': row[0],
                'applications': row[1],
                'responses': row[2],
                'interviews': row[3],
                'interview_rate': round(row[3] * 100.0 / row[1], 1),
                'avg_response_days': round(row[4], 1) if row[4] else None
            })
        
        # Company categories
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN company IN ('Anthropic', 'OpenAI', 'DeepMind', 'Meta AI', 'Google') THEN 'Big Tech AI'
                    WHEN company IN ('Scale AI', 'Databricks', 'Weights & Biases') THEN 'AI Infrastructure'
                    WHEN company IN ('Figma', 'Notion', 'Stripe', 'Plaid') THEN 'Tech Unicorns'
                    WHEN company IN ('Cedar', 'Zocdoc', 'Oscar Health') THEN 'Healthcare Tech'
                    ELSE 'Other'
                END as category,
                COUNT(*) as applications,
                COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews
            FROM master_applications
            GROUP BY category
        """)
        
        insights['by_category'] = {}
        for row in cursor.fetchall():
            insights['by_category'][row[0]] = {
                'applications': row[1],
                'interviews': row[2],
                'effectiveness': round(row[2] * 100.0 / max(row[1], 1), 1)
            }
        
        conn.close()
        return insights
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Get current metrics
        summary = self._generate_executive_summary()
        trends = self._analyze_trends()
        companies = self._analyze_companies()
        
        # Response rate recommendations
        if summary['response_rate'] < 10:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Response Rate',
                'issue': f"Low response rate ({summary['response_rate']}%)",
                'recommendation': "Focus on higher-quality, more targeted applications",
                'actions': [
                    "Increase customization in cover letters",
                    "Apply to jobs within 48 hours of posting",
                    "Focus on companies with proven response history"
                ]
            })
        
        # Volume recommendations
        if summary['daily_average'] < 10:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Application Volume',
                'issue': f"Low daily application rate ({summary['daily_average']}/day)",
                'recommendation': "Increase application volume to hit targets",
                'actions': [
                    "Set up automated discovery for new jobs",
                    "Batch applications in morning and evening sessions",
                    "Use templates for similar roles"
                ]
            })
        
        # Timing recommendations
        if trends.get('best_days'):
            best_day = trends['best_days'][0]['day']
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Timing Optimization',
                'issue': "Suboptimal application timing",
                'recommendation': f"Focus applications on {best_day}s",
                'actions': [
                    f"Schedule batch applications for {best_day}",
                    "Apply during business hours (9am-5pm)",
                    "Avoid late Friday applications"
                ]
            })
        
        # Company recommendations
        if companies.get('top_companies'):
            top_company = companies['top_companies'][0]
            if top_company['interview_rate'] > 20:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Company Focus',
                    'issue': "Not leveraging high-response companies",
                    'recommendation': f"Prioritize companies like {top_company['company']}",
                    'actions': [
                        f"Find more roles at {top_company['company']}",
                        "Look for similar companies in same sector",
                        "Customize heavily for these high-value targets"
                    ]
                })
        
        # Channel recommendations
        metrics = self._calculate_performance_metrics()
        if metrics.get('by_channel'):
            best_channel = max(metrics['by_channel'].items(), 
                             key=lambda x: x[1]['effectiveness'])
            if best_channel[1]['effectiveness'] > 15:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'category': 'Channel Optimization',
                    'issue': "Not optimizing application channels",
                    'recommendation': f"Prioritize {best_channel[0]} applications",
                    'actions': [
                        f"Route more applications through {best_channel[0]}",
                        "Test effectiveness of other channels",
                        "Track channel performance weekly"
                    ]
                })
        
        return recommendations
    
    def _predictive_analysis(self) -> Dict:
        """Generate predictive insights"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        predictions = {}
        
        # Calculate current trajectory
        cursor.execute("""
            SELECT 
                COUNT(*) as applications,
                COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews
            FROM master_applications
            WHERE datetime(applied_at) > datetime('now', '-30 days')
        """)
        
        recent = cursor.fetchone()
        current_rate = recent[1] / max(recent[0], 1) if recent[0] > 0 else 0
        
        # Project future outcomes
        predictions['30_day_projection'] = {
            'expected_applications': int(recent[0] if recent[0] else 0),
            'expected_interviews': int(recent[0] * current_rate) if recent[0] else 0,
            'expected_offers': int(recent[0] * current_rate * 0.3) if recent[0] else 0,
            'confidence': 'medium'
        }
        
        # Calculate probability of success
        if current_rate > 0:
            # Binomial probability of getting at least one offer
            n_applications = predictions['30_day_projection']['expected_applications']
            p_offer = current_rate * 0.3  # 30% of interviews convert to offers
            
            # Probability of at least one offer
            prob_no_offer = (1 - p_offer) ** n_applications
            prob_at_least_one = 1 - prob_no_offer
            
            predictions['success_probability'] = {
                'one_offer': round(prob_at_least_one * 100, 1),
                'multiple_offers': round((1 - prob_no_offer - n_applications * p_offer * prob_no_offer) * 100, 1)
            }
        
        # Time to offer prediction
        if current_rate > 0:
            applications_needed = int(1 / (current_rate * 0.3))  # For one offer
            days_needed = int(applications_needed / max(recent[0] / 30, 1))
            
            predictions['time_to_offer'] = {
                'estimated_days': days_needed,
                'applications_needed': applications_needed,
                'confidence': 'medium' if recent[0] > 30 else 'low'
            }
        
        conn.close()
        return predictions
    
    def _calculate_roi(self) -> Dict:
        """Calculate ROI of automation system"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get application metrics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_applications,
                AVG(julianday(response_received_at) - julianday(applied_at)) as avg_response_time
            FROM master_applications
        """)
        
        metrics = cursor.fetchone()
        
        roi = {
            'time_saved': {
                'hours_automated': metrics[0] * 0.5,  # 30 min per manual application
                'days_saved': round(metrics[0] * 0.5 / 8, 1),
                'value_at_100_per_hour': metrics[0] * 50
            },
            'efficiency_gains': {
                'applications_per_day': round(metrics[0] / 30, 1) if metrics[0] else 0,
                'vs_manual_rate': 'systems',  # 5-10 manual vs 50+ automated
                'multiplier': 'processes'
            },
            'quality_improvements': {
                'ats_optimization': 'Automated',
                'keyword_matching': 'ML-powered',
                'customization': 'Template-based'
            }
        }
        
        conn.close()
        return roi
    
    def display_analytics_report(self):
        """Display comprehensive analytics report"""
        report = self.generate_comprehensive_report()
        
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE ANALYTICS REPORT")
        print("="*80)
        
        # Executive Summary
        summary = report['executive_summary']
        print(f"\n📋 EXECUTIVE SUMMARY")
        print("-" * 40)
        print(f"Performance Grade: {summary['performance_grade']}")
        print(f"Total Applications: {summary['total_applications']}")
        print(f"Response Rate: {summary['response_rate']}%")
        print(f"Interview Rate: {summary['interview_rate']}%")
        print(f"Daily Average: {summary['daily_average']} applications/day")
        
        # Trends
        trends = report['trend_analysis']
        print(f"\n📈 TREND ANALYSIS")
        print("-" * 40)
        print(f"Direction: {trends.get('direction', 'Unknown').upper()}")
        if trends.get('best_days'):
            print(f"Best Day: {trends['best_days'][0]['day']} ({trends['best_days'][0]['rate']}% interview rate)")
        if trends.get('best_hours'):
            print(f"Best Hour: {trends['best_hours'][0]['hour']}:00 ({trends['best_hours'][0]['rate']}% interview rate)")
        
        # Company Insights
        companies = report['company_insights']
        print(f"\n🏢 TOP COMPANIES")
        print("-" * 40)
        for company in companies.get('top_companies', [])[:3]:
            print(f"{company['company']}: {company['interview_rate']}% interview rate ({company['interviews']}/{company['applications']})")
        
        # Recommendations
        print(f"\n💡 TOP RECOMMENDATIONS")
        print("-" * 40)
        for rec in report['optimization_recommendations'][:3]:
            print(f"\n[{rec['priority']}] {rec['category']}")
            print(f"Issue: {rec['issue']}")
            print(f"Action: {rec['recommendation']}")
            for action in rec['actions'][:2]:
                print(f"  • {action}")
        
        # Predictions
        predictions = report['predictive_analysis']
        print(f"\n🔮 PREDICTIVE INSIGHTS")
        print("-" * 40)
        if predictions.get('30_day_projection'):
            proj = predictions['30_day_projection']
            print(f"30-Day Projection:")
            print(f"  • Expected Interviews: {proj['expected_interviews']}")
            print(f"  • Expected Offers: {proj['expected_offers']}")
        
        if predictions.get('success_probability'):
            prob = predictions['success_probability']
            print(f"Success Probability:")
            print(f"  • One Offer: {prob['one_offer']}%")
            print(f"  • Multiple Offers: {prob['multiple_offers']}%")
        
        # ROI
        roi = report['roi_analysis']
        print(f"\n💰 ROI ANALYSIS")
        print("-" * 40)
        print(f"Time Saved: {roi['time_saved']['days_saved']} days")
        print(f"Value Created: ${roi['time_saved']['value_at_100_per_hour']:,}")
        print(f"Efficiency Gain: {roi['efficiency_gains']['applications_per_day']} apps/day")
        
        print("\n" + "="*80)
        print(f"Report Generated: {report['generated_at']}")
        print("="*80)

def main():
    """Run analytics engine"""
    engine = AnalyticsEngine()
    engine.display_analytics_report()

if __name__ == "__main__":
    main()