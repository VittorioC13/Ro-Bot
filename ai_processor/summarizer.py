"""
AI Summarizer for Robotics Daily Report System
Uses DeepSeek API to generate article summaries
"""

import os
from openai import OpenAI
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleSummarizer:
    """
    Generates AI-powered summaries for robotics articles using DeepSeek
    """

    def __init__(self, model: str = 'deepseek-chat'):
        """
        Initialize summarizer

        Args:
            model: DeepSeek model to use (default: deepseek-chat)
        """
        self.model = model
        self.api_key = os.getenv('DEEPSEEK_API_KEY')

        if not self.api_key:
            logger.warning("DeepSeek API key not set. Summarization will not work.")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )

    def generate_summary(self, article_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate a concise summary for an article

        Args:
            article_data: Dictionary containing article information
                          (title, excerpt, full_text, url)

        Returns:
            Generated summary as string, or None if generation failed
        """
        if not self.client:
            logger.error("DeepSeek API client not configured")
            return None

        try:
            # Build content for summarization
            title = article_data.get('title', '')
            excerpt = article_data.get('excerpt', '')
            full_text = article_data.get('full_text', '')

            # Use excerpt or full text if available
            content = full_text if full_text else excerpt

            if not content:
                logger.warning(f"No content to summarize for article: {title}")
                return None

            # Create prompt
            prompt = self._build_prompt(title, content)

            # Call DeepSeek API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert robotics journalist who creates concise, informative summaries of robotics news articles."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.5
            )

            summary = response.choices[0].message.content.strip()

            logger.info(f"Generated summary for: {title[:50]}...")
            return summary

        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            return None

    def _build_prompt(self, title: str, content: str) -> str:
        """
        Build prompt for GPT-4

        Args:
            title: Article title
            content: Article content

        Returns:
            Formatted prompt string
        """
        # Limit content length to avoid token limits
        max_content_length = 2000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        prompt = f"""
Summarize this robotics article in 2-3 concise sentences. Focus on:
- What was announced, discovered, or developed
- Why it matters to the robotics field
- Key technical details or implications

Title: {title}

Content: {content}

Provide only the summary, without any introduction or extra text.
"""
        return prompt

    def generate_key_insights(self, article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate structured key insights for an article

        Args:
            article_data: Dictionary containing article information

        Returns:
            Dictionary with key insights, or None if generation failed
        """
        if not self.client:
            return None

        try:
            title = article_data.get('title', '')
            excerpt = article_data.get('excerpt', '')
            full_text = article_data.get('full_text', '')

            content = full_text if full_text else excerpt

            if not content:
                return None

            # Limit content
            if len(content) > 2000:
                content = content[:2000] + "..."

            prompt = f"""
Analyze this robotics article and extract key insights in JSON format:

Title: {title}
Content: {content}

Provide a JSON object with these fields:
- companies: List of companies mentioned
- technologies: List of technologies discussed
- applications: List of robotics applications
- significance: One sentence on why this matters

Return only valid JSON, no additional text.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a robotics analyst extracting structured insights from articles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )

            # Parse response as JSON
            import json
            insights = json.loads(response.choices[0].message.content.strip())

            return insights

        except Exception as e:
            logger.error(f"Key insights generation failed: {str(e)}")
            return None
