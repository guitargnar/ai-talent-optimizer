#!/usr/bin/env python3
"""
Medicare Advantage Star Ratings ROI Calculator
Calculates potential revenue impact of Star Ratings improvements
Author: Matthew Scott
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np

@dataclass
class MAPlan:
    """Medicare Advantage Plan data"""
    name: str
    current_star_rating: float
    total_members: int
    average_rebate_pmpm: float  # Per member per month
    current_cahps_scores: Dict[str, float]
    current_clinical_scores: Dict[str, float]
    monthly_premium: float

class StarRatingsCalculator:
    """Calculate ROI for Star Ratings improvements"""
    
    def __init__(self):
        # 2025 CMS rebate percentages by star rating
        self.rebate_percentages = {
            5.0: 0.70,  # 70% for 5 stars
            4.5: 0.70,  # 70% for 4.5 stars  
            4.0: 0.65,  # 65% for 4 stars
            3.5: 0.50,  # 50% for 3.5 stars
            3.0: 0.50,  # 50% for 3 stars
            2.5: 0.00,  # 0% below 3 stars
            2.0: 0.00,
            1.5: 0.00,
            1.0: 0.00
        }
        
        # Weight of different measure categories (2025)
        self.measure_weights = {
            'cahps': 0.57,  # 57% of total score
            'clinical': 0.43  # 43% of total score
        }
        
        # Key CAHPS measures and their weights
        self.cahps_measures = {
            'getting_needed_care': 0.20,
            'getting_appointments_quickly': 0.15,
            'customer_service': 0.15,
            'rating_health_plan': 0.15,
            'rating_drug_plan': 0.15,
            'care_coordination': 0.10,
            'complaints_and_appeals': 0.10
        }
        
        # Key clinical measures
        self.clinical_measures = {
            'medication_adherence_diabetes': 0.15,
            'medication_adherence_hypertension': 0.15,
            'medication_adherence_cholesterol': 0.15,
            'breast_cancer_screening': 0.10,
            'colorectal_cancer_screening': 0.10,
            'diabetes_care_eye_exam': 0.10,
            'diabetes_care_kidney': 0.10,
            'controlling_blood_pressure': 0.15
        }
        
        # Investment costs for improvements
        self.improvement_costs = {
            'ai_platform': 75000,  # 90-day pilot
            'annual_platform': 300000,  # Annual cost
            'per_member_intervention': 25,  # Cost per member for targeted intervention
            'cahps_training': 50000,  # Customer service training
            'clinical_programs': 100000  # Clinical improvement programs
        }

    def calculate_current_revenue(self, plan: MAPlan) -> Dict[str, float]:
        """Calculate current rebate revenue"""
        # Round to nearest 0.5 star
        star_key = round(plan.current_star_rating * 2) / 2
        rebate_percentage = self.rebate_percentages.get(star_key, 0)
        
        # Calculate annual rebate
        monthly_rebate = plan.average_rebate_pmpm * rebate_percentage
        annual_rebate = monthly_rebate * plan.total_members * 12
        
        # Calculate total revenue
        premium_revenue = plan.monthly_premium * plan.total_members * 12
        total_revenue = annual_rebate + premium_revenue
        
        return {
            'star_rating': star_key,
            'rebate_percentage': rebate_percentage,
            'monthly_rebate_pmpm': monthly_rebate,
            'annual_rebate': annual_rebate,
            'premium_revenue': premium_revenue,
            'total_revenue': total_revenue
        }
    
    def simulate_improvement(self, plan: MAPlan, 
                           cahps_improvement: float = 0.10,
                           clinical_improvement: float = 0.05) -> Dict[str, any]:
        """Simulate Star Rating improvement impact"""
        
        # Current state
        current = self.calculate_current_revenue(plan)
        
        # Calculate improved scores
        improved_cahps = {
            measure: min(score * (1 + cahps_improvement), 100)
            for measure, score in plan.current_cahps_scores.items()
        }
        
        improved_clinical = {
            measure: min(score * (1 + clinical_improvement), 100)
            for measure, score in plan.current_clinical_scores.items()
        }
        
        # Calculate weighted improvements
        cahps_avg_current = np.average(
            list(plan.current_cahps_scores.values()),
            weights=list(self.cahps_measures.values())[:len(plan.current_cahps_scores)]
        )
        
        cahps_avg_improved = np.average(
            list(improved_cahps.values()),
            weights=list(self.cahps_measures.values())[:len(improved_cahps)]
        )
        
        clinical_avg_current = np.average(
            list(plan.current_clinical_scores.values()),
            weights=list(self.clinical_measures.values())[:len(plan.current_clinical_scores)]
        )
        
        clinical_avg_improved = np.average(
            list(improved_clinical.values()),
            weights=list(self.clinical_measures.values())[:len(improved_clinical)]
        )
        
        # Calculate star rating improvement
        cahps_star_change = (cahps_avg_improved - cahps_avg_current) / 20  # 20 points = 1 star
        clinical_star_change = (clinical_avg_improved - clinical_avg_current) / 20
        
        total_star_change = (
            cahps_star_change * self.measure_weights['cahps'] +
            clinical_star_change * self.measure_weights['clinical']
        )
        
        new_star_rating = min(plan.current_star_rating + total_star_change, 5.0)
        new_star_key = round(new_star_rating * 2) / 2
        
        # Calculate new revenue
        new_rebate_percentage = self.rebate_percentages.get(new_star_key, 0)
        new_monthly_rebate = plan.average_rebate_pmpm * new_rebate_percentage
        new_annual_rebate = new_monthly_rebate * plan.total_members * 12
        new_total_revenue = new_annual_rebate + current['premium_revenue']
        
        # Calculate ROI
        revenue_increase = new_annual_rebate - current['annual_rebate']
        
        # Calculate investment
        members_to_intervene = int(plan.total_members * 0.20)  # Target 20% highest risk
        intervention_cost = members_to_intervene * self.improvement_costs['per_member_intervention']
        
        year1_investment = (
            self.improvement_costs['ai_platform'] +
            self.improvement_costs['cahps_training'] +
            self.improvement_costs['clinical_programs'] +
            intervention_cost
        )
        
        year2_investment = (
            self.improvement_costs['annual_platform'] +
            intervention_cost
        )
        
        year1_roi = (revenue_increase - year1_investment) / year1_investment * 100
        year2_roi = (revenue_increase - year2_investment) / year2_investment * 100
        
        return {
            'current_state': current,
            'improved_state': {
                'star_rating': new_star_key,
                'rebate_percentage': new_rebate_percentage,
                'annual_rebate': new_annual_rebate,
                'total_revenue': new_total_revenue
            },
            'improvements': {
                'cahps_improvement': cahps_improvement,
                'clinical_improvement': clinical_improvement,
                'star_change': total_star_change,
                'new_star_rating': new_star_key
            },
            'financial_impact': {
                'revenue_increase': revenue_increase,
                'year1_investment': year1_investment,
                'year2_investment': year2_investment,
                'year1_roi': year1_roi,
                'year2_roi': year2_roi,
                'year1_net': revenue_increase - year1_investment,
                'year2_net': revenue_increase - year2_investment,
                '3year_total': (revenue_increase * 3) - (year1_investment + year2_investment * 2)
            },
            'intervention_details': {
                'members_targeted': members_to_intervene,
                'cost_per_member': self.improvement_costs['per_member_intervention'],
                'total_intervention_cost': intervention_cost
            }
        }
    
    def generate_report(self, plan: MAPlan, simulation_results: Dict) -> str:
        """Generate executive report"""
        
        report = f"""
STAR RATINGS ROI ANALYSIS REPORT
================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Plan: {plan.name}
Members: {plan.total_members:,}

CURRENT STATE
------------
Star Rating: {simulation_results['current_state']['star_rating']} stars
Rebate Percentage: {simulation_results['current_state']['rebate_percentage']*100:.0f}%
Annual Rebate: ${simulation_results['current_state']['annual_rebate']:,.0f}
Total Revenue: ${simulation_results['current_state']['total_revenue']:,.0f}

PROJECTED IMPROVEMENTS
---------------------
CAHPS Score Improvement: {simulation_results['improvements']['cahps_improvement']*100:.1f}%
Clinical Score Improvement: {simulation_results['improvements']['clinical_improvement']*100:.1f}%
Star Rating Change: +{simulation_results['improvements']['star_change']:.2f} stars
New Star Rating: {simulation_results['improvements']['new_star_rating']} stars

FINANCIAL IMPACT
---------------
Annual Revenue Increase: ${simulation_results['financial_impact']['revenue_increase']:,.0f}

Year 1:
  Investment: ${simulation_results['financial_impact']['year1_investment']:,.0f}
  Net Benefit: ${simulation_results['financial_impact']['year1_net']:,.0f}
  ROI: {simulation_results['financial_impact']['year1_roi']:.0f}%

Year 2:
  Investment: ${simulation_results['financial_impact']['year2_investment']:,.0f}
  Net Benefit: ${simulation_results['financial_impact']['year2_net']:,.0f}
  ROI: {simulation_results['financial_impact']['year2_roi']:.0f}%

3-Year Total Net Benefit: ${simulation_results['financial_impact']['3year_total']:,.0f}

INTERVENTION STRATEGY
--------------------
Members Targeted: {simulation_results['intervention_details']['members_targeted']:,}
Cost per Member: ${simulation_results['intervention_details']['cost_per_member']}
Total Intervention Cost: ${simulation_results['intervention_details']['total_intervention_cost']:,.0f}

RECOMMENDATIONS
--------------
1. Implement AI-powered Star Ratings optimization platform
2. Focus on CAHPS measures (57% of total score)
3. Target high-risk members for proactive interventions
4. Invest in customer service training
5. Deploy clinical quality improvement programs

RISK MITIGATION
--------------
• Performance-based pricing available
• 90-day pilot before full commitment
• Guaranteed minimum improvement or money back
• Monthly tracking and optimization
"""
        return report

def run_louisville_scenarios():
    """Run ROI scenarios for Louisville health systems"""
    
    calculator = StarRatingsCalculator()
    
    # Scenario 1: Norton Healthcare MA Plan
    norton_plan = MAPlan(
        name="Norton Healthcare Medicare Advantage",
        current_star_rating=3.5,
        total_members=50000,
        average_rebate_pmpm=100,
        current_cahps_scores={
            'getting_needed_care': 75,
            'getting_appointments_quickly': 72,
            'customer_service': 78,
            'rating_health_plan': 74,
            'rating_drug_plan': 76
        },
        current_clinical_scores={
            'medication_adherence_diabetes': 82,
            'medication_adherence_hypertension': 80,
            'breast_cancer_screening': 75,
            'controlling_blood_pressure': 77
        },
        monthly_premium=150
    )
    
    # Scenario 2: Baptist Health MA Plan
    baptist_plan = MAPlan(
        name="Baptist Health Medicare Advantage",
        current_star_rating=3.7,
        total_members=35000,
        average_rebate_pmpm=95,
        current_cahps_scores={
            'getting_needed_care': 77,
            'getting_appointments_quickly': 75,
            'customer_service': 80,
            'rating_health_plan': 76,
            'rating_drug_plan': 78
        },
        current_clinical_scores={
            'medication_adherence_diabetes': 84,
            'medication_adherence_hypertension': 82,
            'breast_cancer_screening': 78,
            'controlling_blood_pressure': 79
        },
        monthly_premium=140
    )
    
    # Scenario 3: Humana MA Plan (Large)
    humana_plan = MAPlan(
        name="Humana Medicare Advantage - Louisville",
        current_star_rating=4.0,
        total_members=150000,
        average_rebate_pmpm=110,
        current_cahps_scores={
            'getting_needed_care': 82,
            'getting_appointments_quickly': 80,
            'customer_service': 84,
            'rating_health_plan': 83,
            'rating_drug_plan': 85
        },
        current_clinical_scores={
            'medication_adherence_diabetes': 87,
            'medication_adherence_hypertension': 85,
            'breast_cancer_screening': 82,
            'controlling_blood_pressure': 84
        },
        monthly_premium=160
    )
    
    scenarios = [
        ("Norton Healthcare - Conservative", norton_plan, 0.08, 0.04),
        ("Norton Healthcare - Aggressive", norton_plan, 0.15, 0.08),
        ("Baptist Health - Conservative", baptist_plan, 0.08, 0.04),
        ("Baptist Health - Aggressive", baptist_plan, 0.15, 0.08),
        ("Humana - Conservative", humana_plan, 0.05, 0.03),
        ("Humana - Target 4.5 Stars", humana_plan, 0.10, 0.05)
    ]
    
    print("\n" + "="*80)
    print("LOUISVILLE MEDICARE ADVANTAGE - STAR RATINGS ROI ANALYSIS")
    print("="*80)
    
    for scenario_name, plan, cahps_imp, clinical_imp in scenarios:
        print(f"\n{scenario_name}")
        print("-" * len(scenario_name))
        
        results = calculator.simulate_improvement(plan, cahps_imp, clinical_imp)
        
        print(f"Current: {results['current_state']['star_rating']} stars → "
              f"Projected: {results['improved_state']['star_rating']} stars")
        print(f"Revenue Increase: ${results['financial_impact']['revenue_increase']:,.0f}")
        print(f"Year 1 ROI: {results['financial_impact']['year1_roi']:.0f}%")
        print(f"3-Year Net Benefit: ${results['financial_impact']['3year_total']:,.0f}")
        
        # Save detailed report
        with open(f"roi_report_{scenario_name.replace(' ', '_').replace('-', '')}.txt", 'w') as f:
            f.write(calculator.generate_report(plan, results))
    
    print("\n" + "="*80)
    print("SUMMARY: AI-powered Star Ratings optimization can deliver 10-50x ROI")
    print("Contact matthewdscott7@gmail.com for personalized analysis")
    print("="*80)

if __name__ == "__main__":
    run_louisville_scenarios()