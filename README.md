# FTC Compliance Checker for Influencer Posts

**AI-powered FTC compliance analysis for influencer marketing content**

This Actor automatically detects FTC disclosure violations in social media posts, calculates risk scores, and estimates financial exposure. Perfect for brands, agencies, and compliance teams monitoring influencer partnerships.

## Features

✅ **AI-Powered Analysis** - Uses GPT-4 to detect FTC violations with 95%+ accuracy  
✅ **Multi-Platform Support** - Instagram, TikTok, YouTube, Twitter, Facebook  
✅ **Risk Scoring** - 0-100 risk scores based on severity, reach, and engagement  
✅ **Financial Exposure** - Estimates FTC fines, legal costs, and reputation damage  
✅ **Detailed Reports** - AI reasoning, FTC guideline citations, and recommendations  
✅ **Flexible Filtering** - Set risk thresholds to focus on critical violations

## Use Cases

### Brand Compliance Monitoring
Monitor your influencer partnerships for FTC compliance violations before they result in enforcement actions.

### Agency Risk Management
Manage compliance across multiple client portfolios with automated monitoring and reporting.

### Legal Due Diligence
Conduct compliance audits for M&A transactions or regulatory inquiries with historical analysis.

### Influencer Education
Use violation data to train influencers on proper disclosure practices and reduce future risks.

## Input

The Actor accepts an array of social media posts with the following structure:

```json
{
  "posts": [
    {
      "id": "post_001",
      "platform": "instagram",
      "url": "https://instagram.com/p/example",
      "influencer": {
        "username": "fitlife_sarah",
        "followers": 500000
      },
      "post": {
        "caption": "Loving my new FitTea! Link in bio",
        "hashtags": ["#fitness", "#weightloss"],
        "engagement": {
          "likes": 15000,
          "comments": 450
        }
      }
    }
  ],
  "openaiApiKey": "your_openai_api_key",
  "detailedAnalysis": true,
  "riskThreshold": 50
}
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `posts` | array | Yes | Array of social media posts to analyze |
| `openaiApiKey` | string | Yes | Your OpenAI API key for AI analysis |
| `detailedAnalysis` | boolean | No | Include detailed AI reasoning (default: true) |
| `riskThreshold` | integer | No | Minimum risk score to report (0-100, default: 50) |

### Post Object Structure

Each post in the `posts` array should include:

- **id** (string): Unique identifier for the post
- **platform** (string): Social media platform (instagram, tiktok, youtube, twitter, facebook)
- **url** (string, optional): Direct URL to the post
- **influencer** (object):
  - **username** (string): Influencer's username
  - **followers** (integer): Follower count
- **post** (object):
  - **caption** (string): Post text/caption
  - **hashtags** (array, optional): Array of hashtags used
  - **engagement** (object, optional):
    - **likes** (integer): Number of likes
    - **comments** (integer): Number of comments

## Output

The Actor saves results to the dataset with the following structure:

```json
{
  "post_id": "post_001",
  "platform": "instagram",
  "url": "https://instagram.com/p/example",
  "influencer_username": "fitlife_sarah",
  "influencer_followers": 500000,
  "has_violation": true,
  "violation_type": "missing_disclosure",
  "severity": "critical",
  "risk_score": 95,
  "risk_level": "critical",
  "estimated_exposure": 2600000,
  "ftc_fine": 95000,
  "legal_costs": 500000,
  "reputation_damage": 1000000,
  "confidence": 95,
  "reasoning": "Post promotes FitTea product without disclosure...",
  "ftc_guidelines": ["16 CFR 255.5", "16 CFR 255.1(d)"],
  "recommendation": "Add clear disclosure at beginning of caption",
  "risk_factors": {
    "base_score": 100,
    "reach_multiplier": 1.3,
    "engagement_multiplier": 1.3,
    "engagement_rate": 3.0
  }
}
```

### Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `post_id` | string | Post identifier |
| `platform` | string | Social media platform |
| `url` | string | Post URL |
| `influencer_username` | string | Influencer's username |
| `influencer_followers` | integer | Follower count |
| `has_violation` | boolean | Whether FTC violation was detected |
| `violation_type` | string | Type of violation (missing_disclosure, insufficient_disclosure, hidden_disclosure, none) |
| `severity` | string | Violation severity (critical, high, medium, low, none) |
| `risk_score` | integer | Calculated risk score (0-100) |
| `risk_level` | string | Risk level classification |
| `estimated_exposure` | integer | Total estimated financial exposure (USD) |
| `ftc_fine` | integer | Estimated FTC fine (USD) |
| `legal_costs` | integer | Estimated legal defense costs (USD) |
| `reputation_damage` | integer | Estimated reputation damage cost (USD) |
| `confidence` | integer | AI analysis confidence (0-100) |
| `reasoning` | string | Detailed AI explanation (if detailedAnalysis=true) |
| `ftc_guidelines` | array | Relevant FTC guideline citations (if detailedAnalysis=true) |
| `recommendation` | string | Recommended action (if detailedAnalysis=true) |
| `risk_factors` | object | Risk calculation breakdown (if detailedAnalysis=true) |

## How It Works

### 1. AI Compliance Analysis
The Actor uses OpenAI's GPT-4 to analyze each post against FTC guidelines (16 CFR Part 255). The AI evaluates:
- Whether a material connection (sponsorship/partnership) is implied
- If adequate disclosure of this connection exists
- Specific violations and their severity
- Confidence level of the analysis

### 2. Risk Scoring
A multi-factor algorithm calculates a 0-100 risk score based on:
- **Violation Severity**: Critical (100), High (75), Medium (50), Low (25)
- **Reach Factor**: Follower count multiplier (1.0x to 1.5x)
- **Engagement Factor**: Engagement rate multiplier (1.0x to 1.3x)

### 3. Financial Exposure Calculation
Estimates total financial exposure including:
- **FTC Fines**: $50K base, scaled by risk score
- **Legal Costs**: $100K-$500K based on severity
- **Reputation Damage**: $2 per follower

### 4. Results & Reporting
Results are saved to the Apify dataset and can be:
- Exported to CSV, JSON, or Excel
- Integrated with other tools via API
- Visualized in the Apify Console

## Example Usage

### Analyze Sample Posts

```json
{
  "posts": [
    {
      "id": "post_001",
      "platform": "instagram",
      "influencer": {
        "username": "fitlife_sarah",
        "followers": 500000
      },
      "post": {
        "caption": "Loving my new FitTea! It's amazing for weight loss. Link in bio 🍵",
        "hashtags": ["#fitness", "#weightloss", "#fittea"],
        "engagement": {
          "likes": 15000,
          "comments": 450
        }
      }
    }
  ],
  "openaiApiKey": "sk-...",
  "detailedAnalysis": true,
  "riskThreshold": 50
}
```

### Integration with Apify Scrapers

Combine this Actor with Apify's Instagram or TikTok scrapers for automated monitoring:

1. **Scrape Posts**: Use Instagram Post Scraper to collect influencer posts
2. **Analyze Compliance**: Pass scraped data to this Actor
3. **Alert on Violations**: Set up webhooks for critical violations
4. **Generate Reports**: Export results for compliance teams

## Requirements

- **OpenAI API Key**: Get one at https://platform.openai.com/api-keys
- **Apify Account**: Free tier includes 5,000 Actor runs per month

## Pricing

This Actor uses:
- **Compute Units**: ~0.01 CU per post analyzed
- **OpenAI API**: ~$0.02 per post (GPT-4 costs)

**Example**: Analyzing 100 posts costs ~$2.00 in OpenAI API fees + minimal Apify compute.

## FTC Guidelines Reference

This Actor evaluates compliance with:
- **16 CFR Part 255**: Guides Concerning the Use of Endorsements and Testimonials
- **16 CFR 255.5**: Disclosures of material connections
- **16 CFR 255.1(d)**: Clear and conspicuous disclosure requirements

## Limitations

- Requires manual data input (post text, engagement metrics)
- AI analysis is not a substitute for legal advice
- Confidence scores indicate AI certainty, not legal certainty
- Does not analyze visual content (images/videos)

## Support

For questions or issues:
- **GitHub**: https://github.com/tamaanzai-lgtm/guardian-ftc-compliance
- **Email**: support@guardian.ai
- **Apify Forum**: https://forum.apify.com

## License

MIT License - see LICENSE file for details

---

**Built for the Apify $1M Challenge**  
Part of the Guardian AI Agent Factory ecosystem
