#!/usr/bin/env python3
"""
Model Value Analyzer - Identifies high-revenue generating Ollama models
Tests models with varying prompt complexity to determine real-world value
"""

import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple
import os

class ModelValueAnalyzer:
    def __init__(self):
        self.test_results = {}
        self.high_value_models = []
        
        # Define test prompts of increasing complexity
        self.test_prompts = {
            "simple": {
                "career": "Write a LinkedIn post about AI skills",
                "healthcare": "What is Medicare Advantage?",
                "coding": "Write a Python function to sort a list",
                "business": "How do I increase revenue?"
            },
            "moderate": {
                "career": "I'm a Senior Risk Management Professional at Humana with 10 years experience. Create a compelling narrative for why I should be hired as a Principal Engineer at a $400K salary, emphasizing my unique value proposition combining healthcare domain expertise with AI platform building.",
                "healthcare": "Analyze the impact of CMS Star Ratings cut point changes on Medicare Advantage plans' revenue, and provide specific strategies to optimize performance metrics for maximum reimbursement.",
                "coding": "Design a scalable microservices architecture for processing 1 million healthcare claims per day with real-time fraud detection, including technology stack recommendations and deployment strategy.",
                "business": "Create a detailed business plan for monetizing a collection of 60+ specialized AI models, including pricing strategy, target market analysis, and projected 6-month revenue."
            },
            "complex": {
                "career": """As Matthew Scott, a Senior Risk Management Professional II at Humana with 10+ years experience who has:
                - Built an AI platform with 117 Python modules and 86,000+ files while maintaining a demanding day job
                - Delivered $1.2M in annual savings through automation
                - Maintained 100% CMS/Medicare compliance with zero critical defects
                - Sent 73+ job applications with 0% response rate despite technical excellence
                
                Create a comprehensive strategy to break through the ATS/recruiter barrier and secure multiple $400K+ Principal/Staff Engineering offers within 30 days. Include specific companies to target, exact messaging strategies, and unconventional approaches that leverage my unique position.""",
                
                "healthcare": """Design a complete Medicare Advantage optimization system that:
                1. Predicts CMS Star Ratings cut points 6 months in advance with 95% accuracy
                2. Identifies $10M+ in recoverable revenue through HCC coding optimization
                3. Improves CAHPS scores by 0.5 stars through targeted interventions
                4. Reduces medication non-adherence by 25% using predictive analytics
                Provide specific implementation details, ROI calculations, and a 90-day deployment plan.""",
                
                "coding": """Create a production-ready AI-powered job application system that:
                1. Scrapes 500+ job boards in real-time
                2. Customizes applications using RAG and fine-tuned LLMs
                3. Tracks responses with 99.9% accuracy (eliminating false positives)
                4. Implements advanced ATS-beating strategies
                5. Sends 100+ applications daily with personalization
                Include complete code architecture, database schema, API design, and deployment configuration for Kubernetes.""",
                
                "business": """You have access to:
                - 60+ specialized Ollama models (healthcare, coding, career, music)
                - A proven AI platform with 117 Python modules
                - Deep healthcare industry knowledge and Humana connections
                - Demonstrated ability to deliver $1.2M+ in savings
                
                Design three separate $100K+ revenue streams that can be launched within 30 days with minimal capital investment. Include:
                - Specific customer acquisition strategies
                - Pricing models and revenue projections
                - Competitive differentiation
                - Scale-up plan to $1M ARR within 6 months"""
            }
        }
        
        # Models to test (grouped by category)
        self.model_groups = {
            "career": [
                "universal_career_strategist:latest",
                "linkedin-writer:latest",
                "action_crystallizer:latest",
                "matthews_strategic_accelerator_v2:latest"
            ],
            "healthcare": [
                "star_ratings_analyzer:latest",
                "cms_cut_point_predictor:latest",
                "medication_adherence_optimizer:latest",
                "hcc_coding_assistant:latest",
                "care_gap_identifier:latest"
            ],
            "coding": [
                "deepseek-coder-v2:16b",
                "python_expert:latest",
                "solution_architect:latest",
                "codellama:7b-instruct"
            ],
            "business": [
                "universal_corporate_navigator:latest",
                "command-r:35b",
                "qwen2.5:14b",
                "llama3.1:8b"
            ],
            "specialized": [
                "cross_model_synthesizer:latest",
                "chain_conductor_ai:latest",
                "analytical_expert_gemma:latest"
            ]
        }
    
    def query_model(self, model: str, prompt: str, timeout: int = 60) -> Tuple[str, float, bool]:
        """Query a model and return response, time taken, and success status"""
        try:
            start_time = time.time()
            
            # Run ollama with timeout
            result = subprocess.run(
                ["ollama", "run", model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                return result.stdout.strip(), elapsed_time, True
            else:
                return f"Error: {result.stderr}", elapsed_time, False
                
        except subprocess.TimeoutExpired:
            return "TIMEOUT", timeout, False
        except Exception as e:
            return f"Exception: {str(e)}", 0, False
    
    def evaluate_response_quality(self, response: str, complexity: str) -> Dict:
        """Evaluate response quality for revenue potential"""
        quality_metrics = {
            "length": len(response),
            "has_specifics": any(char.isdigit() for char in response),  # Contains numbers/metrics
            "has_structure": response.count('\n') > 5,  # Multi-paragraph
            "has_action_items": any(word in response.lower() for word in ['step', 'first', 'next', 'then', 'implement']),
            "has_technical_depth": any(term in response.lower() for term in ['api', 'database', 'algorithm', 'architecture', 'roi', 'revenue']),
            "timeout": response == "TIMEOUT",
            "error": response.startswith("Error") or response.startswith("Exception")
        }
        
        # Calculate quality score (0-100)
        score = 0
        if not quality_metrics["timeout"] and not quality_metrics["error"]:
            if quality_metrics["length"] > 100:
                score += 20
            if quality_metrics["length"] > 500:
                score += 20
            if quality_metrics["has_specifics"]:
                score += 20
            if quality_metrics["has_structure"]:
                score += 15
            if quality_metrics["has_action_items"]:
                score += 15
            if quality_metrics["has_technical_depth"]:
                score += 10
            
            # Complexity bonus
            if complexity == "complex":
                score = min(100, score * 1.2)
            elif complexity == "moderate":
                score = min(100, score * 1.1)
        
        quality_metrics["score"] = score
        quality_metrics["revenue_potential"] = self.assess_revenue_potential(response, score)
        
        return quality_metrics
    
    def assess_revenue_potential(self, response: str, quality_score: float) -> str:
        """Assess revenue generation potential"""
        if quality_score >= 80:
            if any(term in response.lower() for term in ['$', 'revenue', 'roi', 'savings', 'profit', 'monetize']):
                return "HIGH - Direct revenue generation capability"
            return "MEDIUM-HIGH - Strong technical/strategic value"
        elif quality_score >= 60:
            return "MEDIUM - Solid foundational value"
        elif quality_score >= 40:
            return "LOW-MEDIUM - Basic utility"
        else:
            return "LOW - Limited practical value"
    
    def test_model_category(self, category: str, models: List[str]):
        """Test all models in a category"""
        print(f"\n{'='*80}")
        print(f"Testing {category.upper()} Models")
        print(f"{'='*80}")
        
        for model in models:
            print(f"\n📊 Testing: {model}")
            model_results = {}
            
            for complexity in ["simple", "moderate", "complex"]:
                prompt = self.test_prompts[complexity].get(category, self.test_prompts[complexity]["business"])
                
                print(f"  🔹 {complexity.capitalize()} prompt... ", end="", flush=True)
                
                response, elapsed_time, success = self.query_model(
                    model, 
                    prompt,
                    timeout=30 if complexity == "simple" else 60 if complexity == "moderate" else 90
                )
                
                quality = self.evaluate_response_quality(response, complexity)
                
                model_results[complexity] = {
                    "success": success,
                    "time": elapsed_time,
                    "quality": quality,
                    "response_preview": response[:200] if success and not response == "TIMEOUT" else response
                }
                
                if success and not response == "TIMEOUT":
                    print(f"✅ Score: {quality['score']:.0f}/100 | {elapsed_time:.1f}s")
                else:
                    print(f"❌ {response}")
            
            # Calculate overall model value
            total_score = sum(r["quality"]["score"] for r in model_results.values())
            avg_score = total_score / 3
            
            self.test_results[model] = {
                "category": category,
                "results": model_results,
                "average_score": avg_score,
                "total_score": total_score
            }
            
            if avg_score >= 70:
                self.high_value_models.append({
                    "model": model,
                    "category": category,
                    "avg_score": avg_score,
                    "best_complexity": max(model_results.items(), key=lambda x: x[1]["quality"]["score"])[0]
                })
    
    def run_analysis(self):
        """Run complete analysis on all models"""
        print(f"\n🚀 Model Value Analysis Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Testing {sum(len(models) for models in self.model_groups.values())} models across {len(self.model_groups)} categories")
        
        for category, models in self.model_groups.items():
            self.test_model_category(category, models)
        
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print(f"\n{'='*80}")
        print(f"📈 HIGH-VALUE MODEL ANALYSIS REPORT")
        print(f"{'='*80}")
        
        # Sort high-value models by score
        self.high_value_models.sort(key=lambda x: x["avg_score"], reverse=True)
        
        print(f"\n🏆 TOP REVENUE-GENERATING MODELS:")
        print(f"{'='*80}")
        
        for i, model_info in enumerate(self.high_value_models[:10], 1):
            print(f"\n{i}. {model_info['model']}")
            print(f"   Category: {model_info['category'].upper()}")
            print(f"   Average Score: {model_info['avg_score']:.1f}/100")
            print(f"   Best Performance: {model_info['best_complexity']} complexity")
            
            # Get revenue potential from the model's best result
            best_result = self.test_results[model_info['model']]["results"][model_info['best_complexity']]
            print(f"   Revenue Potential: {best_result['quality']['revenue_potential']}")
        
        # Category analysis
        print(f"\n📊 CATEGORY PERFORMANCE:")
        print(f"{'='*80}")
        
        category_scores = {}
        for model, data in self.test_results.items():
            category = data["category"]
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(data["average_score"])
        
        for category, scores in category_scores.items():
            avg = sum(scores) / len(scores)
            print(f"\n{category.upper()}:")
            print(f"  Average Score: {avg:.1f}/100")
            print(f"  Best Model: {max((m for m in self.test_results if self.test_results[m]['category'] == category), key=lambda x: self.test_results[x]['average_score'])}")
        
        # Save detailed results
        self.save_results()
    
    def save_results(self):
        """Save detailed results to JSON file"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "high_value_models": self.high_value_models,
            "detailed_results": self.test_results,
            "summary": {
                "total_models_tested": len(self.test_results),
                "high_value_models_found": len(self.high_value_models),
                "top_performer": self.high_value_models[0] if self.high_value_models else None
            }
        }
        
        with open("model_value_analysis.json", "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: model_value_analysis.json")

if __name__ == "__main__":
    analyzer = ModelValueAnalyzer()
    analyzer.run_analysis()