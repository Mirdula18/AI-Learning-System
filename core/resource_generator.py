"""
core/resource_generator.py
EXCLUSIVE: Automatic learning resource generation using LLM
Generates documents, videos, articles, and links for topics
"""

import os
import json
import logging
from typing import List, Dict
from .models import TopicResource

logger = logging.getLogger(__name__)


def generate_topic_resources(topic_name: str, skill_level: str = 'beginner') -> List[Dict]:
    """
    Generate learning resources for a topic using LLM
    
    Args:
        topic_name: Name of the topic/subject
        skill_level: User's skill level (beginner/intermediate/advanced)
    
    Returns:
        List of resource dictionaries with title, type, url, description
    """
    try:
        # Try to use available LLM API
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            logger.warning("No LLM API key found. Using fallback resource generation.")
            return _generate_fallback_resources(topic_name, skill_level)
        
        # Use Gemini if available
        if os.getenv('GEMINI_API_KEY'):
            return _generate_with_gemini(topic_name, skill_level)
        # Use Claude if available
        elif os.getenv('ANTHROPIC_API_KEY'):
            return _generate_with_claude(topic_name, skill_level)
        else:
            return _generate_fallback_resources(topic_name, skill_level)
            
    except Exception as e:
        logger.error(f"Error generating resources for {topic_name}: {str(e)}")
        return _generate_fallback_resources(topic_name, skill_level)


def _generate_with_gemini(topic_name: str, skill_level: str) -> List[Dict]:
    """Generate resources using Google Gemini API"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""You are an expert educational resource curator. Generate a curated list of the BEST learning resources for the topic: "{topic_name}" for a {skill_level} learner.

For each resource, provide:
1. Title (the actual name of the resource)
2. Type (document/video/article/link)
3. URL (real, working URL - use actual websites like official docs, YouTube, Medium, etc.)
4. Description (2-3 sentences about what the resource covers)

Generate 5-7 high-quality resources. Mix different types (at least 1 document, 1-2 videos, 1-2 articles).

IMPORTANT: Return ONLY valid JSON in this exact format (no markdown, no extra text):
{{
  "resources": [
    {{
      "title": "Resource Title",
      "type": "document",
      "url": "https://example.com/resource",
      "description": "What this resource teaches"
    }}
  ]
}}

Types must be one of: document, video, article, link
URLs must be real and accessible."""

        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean up markdown code blocks if present
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
            result_text = result_text.strip()
        
        # Parse JSON response
        data = json.loads(result_text)
        resources = data.get('resources', [])
        
        # Validate and clean resources
        valid_resources = []
        for resource in resources:
            if all(k in resource for k in ['title', 'type', 'url', 'description']):
                # Ensure type is valid
                if resource['type'] in ['document', 'video', 'article', 'link']:
                    valid_resources.append(resource)
        
        logger.info(f"Generated {len(valid_resources)} resources for {topic_name} using Gemini")
        return valid_resources
        
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return _generate_fallback_resources(topic_name, skill_level)


def _generate_with_claude(topic_name: str, skill_level: str) -> List[Dict]:
    """Generate resources using Anthropic Claude API"""
    try:
        from anthropic import Anthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        client = Anthropic(api_key=api_key)
        
        prompt = f"""You are an expert educational resource curator. Generate a curated list of the BEST learning resources for the topic: "{topic_name}" for a {skill_level} learner.

For each resource, provide:
1. Title (the actual name of the resource)
2. Type (document/video/article/link)
3. URL (real, working URL - use actual websites like official docs, YouTube, Medium, etc.)
4. Description (2-3 sentences about what the resource covers)

Generate 5-7 high-quality resources. Mix different types (at least 1 document, 1-2 videos, 1-2 articles).

IMPORTANT: Return ONLY valid JSON in this exact format:
{{
  "resources": [
    {{
      "title": "Resource Title",
      "type": "document",
      "url": "https://example.com/resource",
      "description": "What this resource teaches"
    }}
  ]
}}

Types must be one of: document, video, article, link"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        result_text = message.content[0].text.strip()
        
        # Parse JSON response
        data = json.loads(result_text)
        resources = data.get('resources', [])
        
        # Validate resources
        valid_resources = []
        for resource in resources:
            if all(k in resource for k in ['title', 'type', 'url', 'description']):
                if resource['type'] in ['document', 'video', 'article', 'link']:
                    valid_resources.append(resource)
        
        logger.info(f"Generated {len(valid_resources)} resources for {topic_name} using Claude")
        return valid_resources
        
    except Exception as e:
        logger.error(f"Claude API error: {str(e)}")
        return _generate_fallback_resources(topic_name, skill_level)


def _generate_fallback_resources(topic_name: str, skill_level: str) -> List[Dict]:
    """
    Fallback resource generation using predefined templates
    Used when LLM API is unavailable
    """
    topic_lower = topic_name.lower()
    
    # Create sensible default resources based on common patterns
    resources = [
        {
            "title": f"Official {topic_name} Documentation",
            "type": "document",
            "url": f"https://www.google.com/search?q={topic_name.replace(' ', '+')}+official+documentation",
            "description": f"Comprehensive official documentation and reference guide for {topic_name}. Great starting point for {skill_level} learners."
        },
        {
            "title": f"{topic_name} Tutorial for Beginners",
            "type": "video",
            "url": f"https://www.youtube.com/results?search_query={topic_name.replace(' ', '+')}+tutorial+{skill_level}",
            "description": f"Video tutorial covering the fundamentals of {topic_name}. Perfect for visual learners at {skill_level} level."
        },
        {
            "title": f"Complete {topic_name} Guide",
            "type": "article",
            "url": f"https://www.google.com/search?q={topic_name.replace(' ', '+')}+complete+guide",
            "description": f"In-depth article covering key concepts and best practices in {topic_name}."
        },
        {
            "title": f"{topic_name} Cheat Sheet",
            "type": "document",
            "url": f"https://www.google.com/search?q={topic_name.replace(' ', '+')}+cheat+sheet+pdf",
            "description": f"Quick reference guide with essential {topic_name} commands and concepts."
        },
        {
            "title": f"Interactive {topic_name} Exercises",
            "type": "link",
            "url": f"https://www.google.com/search?q={topic_name.replace(' ', '+')}+interactive+exercises",
            "description": f"Hands-on practice exercises to reinforce your {topic_name} skills."
        }
    ]
    
    logger.info(f"Generated {len(resources)} fallback resources for {topic_name}")
    return resources


def save_resources_for_topic(topic_name: str, skill_level: str = 'beginner') -> int:
    """
    Generate and save resources for a topic to the database
    
    Args:
        topic_name: Name of the topic
        skill_level: User's skill level
    
    Returns:
        Number of resources created
    """
    try:
        # Check if resources already exist for this topic
        existing_count = TopicResource.objects.filter(topic=topic_name).count()
        
        if existing_count > 0:
            logger.info(f"Resources already exist for topic: {topic_name} ({existing_count} resources)")
            return existing_count
        
        # Generate resources using LLM
        resources_data = generate_topic_resources(topic_name, skill_level)
        
        if not resources_data:
            logger.warning(f"No resources generated for topic: {topic_name}")
            return 0
        
        # Save resources to database
        created_count = 0
        for index, resource in enumerate(resources_data):
            try:
                TopicResource.objects.create(
                    topic=topic_name,
                    title=resource['title'],
                    description=resource['description'],
                    resource_type=resource['type'],
                    url=resource['url'],
                    order=index + 1
                )
                created_count += 1
            except Exception as e:
                logger.error(f"Error saving resource: {str(e)}")
                continue
        
        logger.info(f"Created {created_count} resources for topic: {topic_name}")
        return created_count
        
    except Exception as e:
        logger.error(f"Error in save_resources_for_topic: {str(e)}")
        return 0


def generate_resources_for_roadmap(roadmap_data: Dict, skill_level: str = 'beginner') -> Dict:
    """
    Generate resources for all topics in a roadmap
    
    Args:
        roadmap_data: Roadmap dictionary with learning_path
        skill_level: User's skill level
    
    Returns:
        Dictionary with statistics about generated resources
    """
    stats = {
        'total_topics': 0,
        'topics_processed': 0,
        'total_resources_created': 0,
        'failed_topics': []
    }
    
    try:
        learning_path = roadmap_data.get('learning_path', [])
        stats['total_topics'] = len(learning_path)
        
        for topic_data in learning_path:
            # Extract topic name from various possible formats
            topic_name = topic_data.get('topic') or topic_data.get('name') or topic_data.get('title')
            
            if not topic_name:
                continue
            
            try:
                # Generate and save resources for this topic
                resources_count = save_resources_for_topic(topic_name, skill_level)
                stats['topics_processed'] += 1
                stats['total_resources_created'] += resources_count
                
            except Exception as e:
                logger.error(f"Failed to generate resources for {topic_name}: {str(e)}")
                stats['failed_topics'].append(topic_name)
        
        logger.info(f"Roadmap resource generation complete: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error in generate_resources_for_roadmap: {str(e)}")
        return stats
