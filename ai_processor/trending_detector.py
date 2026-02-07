"""
Trending Topic Detector for Robotics Daily Report System
Identifies trending companies, technologies, and topics from articles
"""

import os
from openai import OpenAI
from typing import List, Dict, Set
import logging
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendingDetector:
    """
    Extracts and tracks trending topics, companies, and technologies from articles
    """

    def __init__(self, model: str = 'deepseek-chat'):
        """
        Initialize trending detector

        Args:
            model: DeepSeek model to use (default: deepseek-chat)
        """
        self.model = model
        self.api_key = os.getenv('DEEPSEEK_API_KEY')

        if not self.api_key:
            logger.warning("DeepSeek API key not set. Trending detection will use fallback method.")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )

    def extract_topics(self, article_data: Dict) -> List[str]:
        """
        Extract relevant topics from an article

        Args:
            article_data: Dictionary containing article information

        Returns:
            List of topic strings (companies, technologies, concepts)
        """
        if self.client:
            return self._extract_with_ai(article_data)
        else:
            return self._extract_fallback(article_data)

    def _extract_with_ai(self, article_data: Dict) -> List[str]:
        """
        Extract topics using GPT-4

        Args:
            article_data: Article information

        Returns:
            List of extracted topics
        """
        try:
            title = article_data.get('title', '')
            excerpt = article_data.get('excerpt', '')
            content = f"{title}. {excerpt}"

            if not content.strip():
                return []

            prompt = f"""
Extract key topics from this robotics article. Focus on:
- Company names
- Robot models or product names
- Technologies (e.g., "computer vision", "LiDAR", "grasping")
- Application areas (e.g., "warehouse automation", "surgical robotics")

Article: {content[:800]}

Return only a JSON array of topic strings, like:
["Company Name", "Technology", "Application"]

Maximum 5-7 topics. Return only the JSON array, no additional text.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured information from robotics articles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )

            result_text = response.choices[0].message.content.strip()

            # Parse JSON array
            topics = json.loads(result_text)

            if isinstance(topics, list):
                # Clean and filter topics
                topics = [str(t).strip() for t in topics if t]
                topics = [t for t in topics if len(t) > 2 and len(t) < 50]
                logger.info(f"Extracted {len(topics)} topics: {topics}")
                return topics[:7]  # Max 7 topics

            return []

        except Exception as e:
            logger.error(f"AI topic extraction failed: {str(e)}")
            return self._extract_fallback(article_data)

    def _extract_fallback(self, article_data: Dict) -> List[str]:
        """
        Fallback topic extraction using pattern matching

        Args:
            article_data: Article information

        Returns:
            List of extracted topics
        """
        topics = set()

        title = article_data.get('title', '')
        excerpt = article_data.get('excerpt', '')
        text = f"{title} {excerpt}".lower()

        # Known robotics companies
        companies = [
            'boston dynamics', 'figure', 'tesla', 'nvidia', 'amazon robotics',
            'abb', 'fanuc', 'universal robots', 'agility robotics', 'waymo',
            'cruise', 'zoox', 'spot', 'atlas', 'optimus', 'digit'
        ]

        for company in companies:
            if company in text:
                # Capitalize properly
                topics.add(company.title())

        # Known technologies
        technologies = [
            'computer vision', 'lidar', 'machine learning', 'deep learning',
            'reinforcement learning', 'slam', 'path planning', 'grasping',
            'manipulation', 'autonomous navigation', 'sensor fusion'
        ]

        for tech in technologies:
            if tech in text:
                topics.add(tech.title())

        # Application areas
        applications = [
            'warehouse automation', 'delivery robots', 'surgical robotics',
            'agricultural robots', 'self-driving', 'humanoid robots',
            'industrial automation', 'collaborative robots', 'drones'
        ]

        for app in applications:
            if app in text:
                topics.add(app.title())

        return list(topics)[:7]

    def extract_companies(self, text: str) -> List[str]:
        """
        Extract company names from text

        Args:
            text: Article text

        Returns:
            List of company names
        """
        # Look for capitalized words/phrases that might be companies
        # This is a simple heuristic - AI method is better
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b'
        matches = re.findall(pattern, text)

        # Filter common words
        common_words = {'The', 'A', 'An', 'And', 'Or', 'But', 'In', 'On', 'At', 'To', 'For'}
        companies = [m for m in matches if m not in common_words]

        return list(set(companies))[:5]

    def batch_extract_topics(self, articles: List[Dict]) -> Dict[str, int]:
        """
        Extract topics from multiple articles and count mentions

        Args:
            articles: List of article dictionaries

        Returns:
            Dictionary mapping topic names to mention counts
        """
        topic_counts = {}

        for article in articles:
            topics = self.extract_topics(article)

            for topic in topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

        # Sort by count
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)

        return dict(sorted_topics)
