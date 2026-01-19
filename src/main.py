"""
FTC Compliance Checker Actor for Apify
Analyzes social media posts for FTC influencer marketing compliance violations
"""

from apify import Actor
from openai import OpenAI
import json


class ComplianceAnalyzer:
    """Analyzes posts for FTC compliance violations using AI"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def analyze_post(self, post_data: dict) -> dict:
        """Analyze a single post for FTC compliance"""
        
        prompt = f"""You are an FTC compliance expert analyzing influencer marketing content.

Analyze this social media post for FTC disclosure violations per 16 CFR Part 255:

Platform: {post_data['platform']}
Influencer: @{post_data['influencer']['username']} ({post_data['influencer']['followers']:,} followers)
Caption: {post_data['post']['caption']}
Hashtags: {', '.join(post_data['post'].get('hashtags', []))}

Determine:
1. Is there a material connection (sponsorship/partnership) implied?
2. Is there adequate disclosure of this connection?
3. What specific violations exist, if any?
4. How severe is the violation?

Respond in JSON format:
{{
    "has_violation": boolean,
    "violation_type": "missing_disclosure" | "insufficient_disclosure" | "hidden_disclosure" | "none",
    "severity": "critical" | "high" | "medium" | "low" | "none",
    "confidence": 0-100,
    "reasoning": "detailed explanation",
    "ftc_guidelines": ["relevant guideline citations"],
    "recommendation": "what should be done"
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an FTC compliance expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            Actor.log.error(f"AI analysis failed: {str(e)}")
            return {
                "has_violation": False,
                "violation_type": "none",
                "severity": "none",
                "confidence": 0,
                "reasoning": f"Analysis failed: {str(e)}",
                "ftc_guidelines": [],
                "recommendation": "Manual review required"
            }


class RiskScorer:
    """Calculates risk scores for violations"""
    
    @staticmethod
    def calculate_risk_score(post_data: dict, analysis: dict) -> dict:
        """Calculate comprehensive risk score"""
        
        if not analysis.get('has_violation'):
            return {
                "risk_score": 0,
                "risk_level": "none",
                "factors": {}
            }
        
        # Base score from severity
        severity_scores = {
            "critical": 100,
            "high": 75,
            "medium": 50,
            "low": 25,
            "none": 0
        }
        base_score = severity_scores.get(analysis.get('severity', 'none'), 0)
        
        # Reach factor (follower count)
        followers = post_data['influencer']['followers']
        if followers >= 1000000:
            reach_multiplier = 1.5
        elif followers >= 500000:
            reach_multiplier = 1.3
        elif followers >= 100000:
            reach_multiplier = 1.2
        else:
            reach_multiplier = 1.0
        
        # Engagement factor
        engagement = post_data['post'].get('engagement', {})
        likes = engagement.get('likes', 0)
        engagement_rate = (likes / followers * 100) if followers > 0 else 0
        
        if engagement_rate >= 5:
            engagement_multiplier = 1.3
        elif engagement_rate >= 3:
            engagement_multiplier = 1.2
        else:
            engagement_multiplier = 1.0
        
        # Calculate final score
        risk_score = min(100, int(base_score * reach_multiplier * engagement_multiplier))
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = "critical"
        elif risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 40:
            risk_level = "medium"
        elif risk_score >= 20:
            risk_level = "low"
        else:
            risk_level = "none"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "factors": {
                "base_score": base_score,
                "reach_multiplier": reach_multiplier,
                "engagement_multiplier": engagement_multiplier,
                "engagement_rate": round(engagement_rate, 2)
            }
        }


class FinancialCalculator:
    """Calculates financial exposure for violations"""
    
    @staticmethod
    def calculate_exposure(post_data: dict, risk_score: int) -> dict:
        """Calculate estimated financial exposure"""
        
        if risk_score == 0:
            return {
                "ftc_fine": 0,
                "legal_costs": 0,
                "reputation_damage": 0,
                "total_exposure": 0
            }
        
        # Base FTC fine
        base_fine = 50000
        
        # Scale by risk score
        ftc_fine = int(base_fine * (risk_score / 100) * 2)
        
        # Legal costs
        if risk_score >= 80:
            legal_costs = 500000
        elif risk_score >= 60:
            legal_costs = 250000
        else:
            legal_costs = 100000
        
        # Reputation damage (based on reach)
        followers = post_data['influencer']['followers']
        reputation_damage = int(followers * 2)  # $2 per follower
        
        total_exposure = ftc_fine + legal_costs + reputation_damage
        
        return {
            "ftc_fine": ftc_fine,
            "legal_costs": legal_costs,
            "reputation_damage": reputation_damage,
            "total_exposure": total_exposure
        }


async def main():
    """Main Actor entry point"""
    
    async with Actor:
        # Get input
        actor_input = await Actor.get_input() or {}
        posts = actor_input.get('posts', [])
        openai_api_key = actor_input.get('openaiApiKey')
        detailed_analysis = actor_input.get('detailedAnalysis', True)
        risk_threshold = actor_input.get('riskThreshold', 50)
        
        if not posts:
            Actor.log.error('No posts provided in input')
            return
        
        if not openai_api_key:
            Actor.log.error('OpenAI API key is required')
            return
        
        Actor.log.info(f'Starting FTC compliance analysis for {len(posts)} posts')
        
        # Initialize analyzers
        analyzer = ComplianceAnalyzer(openai_api_key)
        
        # Process each post
        results = []
        violations_count = 0
        total_exposure = 0
        
        for idx, post in enumerate(posts, 1):
            Actor.log.info(f'Analyzing post {idx}/{len(posts)}: {post.get("id")}')
            
            try:
                # AI compliance analysis
                analysis = analyzer.analyze_post(post)
                
                # Risk scoring
                risk_data = RiskScorer.calculate_risk_score(post, analysis)
                
                # Financial exposure
                financial_data = FinancialCalculator.calculate_exposure(
                    post, 
                    risk_data['risk_score']
                )
                
                # Compile result
                result = {
                    "post_id": post['id'],
                    "platform": post['platform'],
                    "url": post.get('url', ''),
                    "influencer_username": post['influencer']['username'],
                    "influencer_followers": post['influencer']['followers'],
                    "has_violation": analysis['has_violation'],
                    "violation_type": analysis['violation_type'],
                    "severity": analysis['severity'],
                    "risk_score": risk_data['risk_score'],
                    "risk_level": risk_data['risk_level'],
                    "estimated_exposure": financial_data['total_exposure'],
                    "ftc_fine": financial_data['ftc_fine'],
                    "legal_costs": financial_data['legal_costs'],
                    "reputation_damage": financial_data['reputation_damage'],
                    "confidence": analysis['confidence']
                }
                
                # Add detailed analysis if requested
                if detailed_analysis:
                    result['reasoning'] = analysis['reasoning']
                    result['ftc_guidelines'] = analysis['ftc_guidelines']
                    result['recommendation'] = analysis['recommendation']
                    result['risk_factors'] = risk_data['factors']
                
                # Filter by risk threshold
                if risk_data['risk_score'] >= risk_threshold:
                    results.append(result)
                    
                    if analysis['has_violation']:
                        violations_count += 1
                        total_exposure += financial_data['total_exposure']
                    
                    Actor.log.info(f'✓ Post {post["id"]}: Risk={risk_data["risk_score"]}, Violation={analysis["has_violation"]}')
                else:
                    Actor.log.info(f'○ Post {post["id"]}: Below threshold (score={risk_data["risk_score"]})')
                
            except Exception as e:
                Actor.log.error(f'Failed to analyze post {post.get("id")}: {str(e)}')
                continue
        
        # Save results to dataset
        await Actor.push_data(results)
        
        # Log summary
        Actor.log.info('=' * 60)
        Actor.log.info('ANALYSIS COMPLETE')
        Actor.log.info(f'Posts analyzed: {len(posts)}')
        Actor.log.info(f'Violations detected: {violations_count}')
        Actor.log.info(f'Total exposure: ${total_exposure:,}')
        Actor.log.info(f'Results saved: {len(results)} posts')
        Actor.log.info('=' * 60)
        
        # Set output
        await Actor.set_value('OUTPUT', {
            "summary": {
                "posts_analyzed": len(posts),
                "violations_detected": violations_count,
                "total_exposure": total_exposure,
                "results_count": len(results)
            },
            "results": results
        })
