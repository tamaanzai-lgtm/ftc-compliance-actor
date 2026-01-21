"""FTC Compliance Checker Actor for Apify"""

from apify import Actor
from openai import OpenAI
import json


async def main():
    """Main Actor entry point"""
    
    async with Actor:
        # Get input
        actor_input = await Actor.get_input() or {}
        post_text = actor_input.get('postText', '')
        platform = actor_input.get('platform', 'instagram')
        username = actor_input.get('influencerUsername', 'unknown')
        followers = actor_input.get('followerCount', 0)
        openai_api_key = actor_input.get('openaiApiKey')
        
        if not post_text:
            Actor.log.error('No post text provided')
            return
        
        if not openai_api_key:
            Actor.log.error('OpenAI API key required')
            return
        
        Actor.log.info(f'Analyzing post from @{username} on {platform}')
        
        try:
            # AI compliance analysis
            client = OpenAI(api_key=openai_api_key)
            
            prompt = f"""Analyze this social media post for FTC disclosure violations:

Platform: {platform}
Influencer: @{username} ({followers:,} followers)
Post: {post_text}

Determine if there's a material connection that requires disclosure per FTC guidelines.

Respond in JSON:
{{
    "has_violation": boolean,
    "violation_type": "missing_disclosure|insufficient_disclosure|hidden_disclosure|none",
    "severity": "critical|high|medium|low|none",
    "confidence": 0-100,
    "reasoning": "explanation",
    "recommendation": "what to do"
}}"""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an FTC compliance expert. Respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Calculate risk score
            severity_scores = {"critical": 100, "high": 75, "medium": 50, "low": 25, "none": 0}
            base_score = severity_scores.get(analysis.get('severity', 'none'), 0)
            
            reach_multiplier = 1.5 if followers >= 1000000 else 1.3 if followers >= 500000 else 1.2 if followers >= 100000 else 1.0
            risk_score = min(100, int(base_score * reach_multiplier))
            
            # Calculate financial exposure
            ftc_fine = int(50000 * (risk_score / 100) * 2) if risk_score > 0 else 0
            legal_costs = 500000 if risk_score >= 80 else 250000 if risk_score >= 60 else 100000 if risk_score > 0 else 0
            reputation_damage = int(followers * 2) if risk_score > 0 else 0
            total_exposure = ftc_fine + legal_costs + reputation_damage
            
            # Compile result
            result = {
                "post_text": post_text,
                "platform": platform,
                "influencer_username": username,
                "influencer_followers": followers,
                "has_violation": analysis['has_violation'],
                "violation_type": analysis['violation_type'],
                "severity": analysis['severity'],
                "risk_score": risk_score,
                "estimated_exposure": total_exposure,
                "ftc_fine": ftc_fine,
                "legal_costs": legal_costs,
                "reputation_damage": reputation_damage,
                "confidence": analysis['confidence'],
                "reasoning": analysis['reasoning'],
                "recommendation": analysis['recommendation']
            }
            
            # Save result
            await Actor.push_data(result)
            
            Actor.log.info('=' * 60)
            Actor.log.info(f'ANALYSIS COMPLETE')
            Actor.log.info(f'Violation: {analysis["has_violation"]}')
            Actor.log.info(f'Risk Score: {risk_score}')
            Actor.log.info(f'Exposure: ${total_exposure:,}')
            Actor.log.info('=' * 60)
            
        except Exception as e:
            Actor.log.error(f'Analysis failed: {str(e)}')
            raise
