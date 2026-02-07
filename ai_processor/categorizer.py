"""
AI Categorizer for Robotics Daily Report System
Uses DeepSeek API to automatically categorize articles
"""

import os
from openai import OpenAI
from typing import List, Dict, Tuple, Optional
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleCategorizer:
    """
    Automatically categorizes robotics articles into predefined categories using DeepSeek
    """

    # Predefined categories matching database
    CATEGORIES = [
        'Humanoid Robots',
        'Drones & Aerial Systems',
        'Industrial Automation',
        'AGVs & AMRs',
        'AI & Software',
        'Research & Academia',
        'Business & Funding',
        'Healthcare Robotics',
        'Agricultural Robotics',
        'Consumer Robotics'
    ]

    def __init__(self, model: str = 'deepseek-chat'):
        """
        Initialize categorizer

        Args:
            model: DeepSeek model to use (default: deepseek-chat)
        """
        self.model = model
        self.api_key = os.getenv('DEEPSEEK_API_KEY')

        if not self.api_key:
            logger.warning("DeepSeek API key not set. Categorization will not work.")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )

    def categorize_article(self, article_data: Dict) -> List[Tuple[str, float]]:
        """
        Categorize an article into 1-3 relevant categories

        Args:
            article_data: Dictionary containing article information (title, excerpt)

        Returns:
            List of tuples: (category_name, confidence_score)
            Returns empty list if categorization fails
        """
        if not self.client:
            logger.error("DeepSeek API client not configured")
            return []

        try:
            title = article_data.get('title', '')
            excerpt = article_data.get('excerpt', '')
            content = f"{title}. {excerpt}"

            if not content.strip():
                logger.warning("No content to categorize")
                return []

            # Create prompt
            prompt = self._build_prompt(content)

            # Call DeepSeek API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert robotics analyst who categorizes robotics news articles into appropriate categories."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )

            # Parse response
            result_text = response.choices[0].message.content.strip()
            categories = self._parse_categories(result_text)

            logger.info(f"Categorized article '{title[:50]}...' into: {[c[0] for c in categories]}")
            return categories

        except Exception as e:
            logger.error(f"Categorization failed: {str(e)}")
            return []

    def _build_prompt(self, content: str) -> str:
        """
        Build prompt for GPT-4 categorization

        Args:
            content: Article title and excerpt

        Returns:
            Formatted prompt string
        """
        categories_list = '\n'.join([f"- {cat}" for cat in self.CATEGORIES])

        prompt = f"""
Categorize this robotics article into 1-3 most relevant categories from the list below.
Provide categories in order of relevance with confidence scores (0.0-1.0).

Available categories:
{categories_list}

Article: {content[:500]}

Respond in JSON format:
{{
  "categories": [
    {{"name": "Category Name", "confidence": 0.95}},
    {{"name": "Category Name", "confidence": 0.80}}
  ]
}}

Only include categories that are truly relevant. Respond with valid JSON only.
"""
        return prompt

    def _parse_categories(self, response_text: str) -> List[Tuple[str, float]]:
        """
        Parse GPT-4 response into category list

        Args:
            response_text: Raw response from GPT-4

        Returns:
            List of (category_name, confidence_score) tuples
        """
        try:
            # Try to parse as JSON
            data = json.loads(response_text)

            categories = []
            for cat in data.get('categories', []):
                name = cat.get('name', '')
                confidence = float(cat.get('confidence', 0.0))

                # Validate category exists
                if name in self.CATEGORIES:
                    categories.append((name, confidence))
                else:
                    logger.warning(f"Invalid category returned: {name}")

            return categories[:3]  # Max 3 categories

        except json.JSONDecodeError:
            # Fallback: try to extract categories from text
            logger.warning("Failed to parse JSON response, attempting text parsing")
            return self._fallback_parse(response_text)

    def _fallback_parse(self, text: str) -> List[Tuple[str, float]]:
        """
        Fallback parser if JSON parsing fails

        Args:
            text: Response text

        Returns:
            List of (category_name, confidence_score) tuples
        """
        categories = []

        # Look for category names in text
        for category in self.CATEGORIES:
            if category.lower() in text.lower():
                # Assign default confidence based on order found
                confidence = 0.9 if len(categories) == 0 else 0.7
                categories.append((category, confidence))

                if len(categories) >= 3:
                    break

        return categories

    def get_category_suggestions(self, content: str) -> Dict[str, float]:
        """
        Get confidence scores for all categories

        Args:
            content: Article content

        Returns:
            Dictionary mapping category names to confidence scores
        """
        if not self.client:
            return {}

        try:
            categories_list = '\n'.join([f"- {cat}" for cat in self.CATEGORIES])

            prompt = f"""
Rate how relevant this article is to each category (0.0-1.0 score):

Article: {content[:500]}

Categories:
{categories_list}

Respond in JSON format with all categories:
{{
  "Category Name": 0.XX,
  ...
}}
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a robotics categorization expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content.strip())
            return result

        except Exception as e:
            logger.error(f"Category suggestions failed: {str(e)}")
            return {}
