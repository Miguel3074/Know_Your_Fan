import os
import base64
import json
import re
from openai import OpenAI

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def validate_document(document_base64, doc_type, user_info=None):
    """
    Validate the document using OpenAI's vision capabilities.
    
    Args:
        document_base64: Base64 encoded image/document
        doc_type: Type of document (ID, CPF, etc.)
        user_info: Dictionary with user information to verify against
    
    Returns:
        Dictionary with validation results
    """
    prompt = f"This is a {doc_type} document for verification purposes. "
    
    if user_info:
        prompt += "Please verify if the following information matches what's in the document: "
        for key, value in user_info.items():
            prompt += f"{key}: {value}, "
    
    prompt += ("Please analyze this document carefully and extract the following information: "
               "1. Document type (confirm it's the claimed type) "
               "2. Full name on the document "
               "3. Document number/ID "
               "4. Issuing date or expiration date (if visible) "
               "5. A validation score from 0.0 to 1.0 indicating how confident you are this is a genuine document "
               "6. Any signs of tampering or fraud "
               "Return results in JSON format with keys: document_type, full_name, document_number, date, "
               "validation_score, potential_fraud, and reasoning")
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{document_base64}"}
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=800
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Add validation timestamp
        result['timestamp'] = str(VALIDATION_SCORE_THRESHOLD)
        
        # If we have user info, add a verification flag
        if user_info and 'full_name' in user_info and 'full_name' in result:
            name_match = calculate_name_similarity(user_info['full_name'], result['full_name'])
            result['name_match_score'] = name_match
            result['name_verified'] = name_match > NAME_MATCH_THRESHOLD
        
        return result
    
    except Exception as e:
        return {
            "error": str(e),
            "validation_score": 0.0,
            "potential_fraud": True,
            "reasoning": "Error occurred during validation"
        }

def validate_esports_profile(profile_url, platform, username=None):
    """
    Validate an esports profile using OpenAI to determine relevance to esports.
    
    Args:
        profile_url: URL of the esports profile
        platform: Platform name (Steam, Battlenet, etc.)
        username: Username of the profile
    
    Returns:
        Dictionary with validation results including relevance score
    """
    prompt = (f"I'm verifying if this {platform} profile ({profile_url}) belongs to someone "
              f"who is genuinely interested in esports. "
              f"The profile username is: {username if username else 'unknown'}. "
              "Please analyze the URL and provide the following information: "
              "1. Verify if this is a real {platform} profile URL "
              "2. Indicate how relevant this profile appears to be to esports (scale 0.0 to 1.0) "
              "3. Extract any esports teams or games mentioned "
              "4. Look for any red flags or suspicious elements "
              "Return the results in a JSON format with these keys: is_valid_url, relevance_score, "
              "esports_elements, suspicious_elements")
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in esports profile validation."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Normalize the result structure
        if 'relevance_score' not in result:
            result['relevance_score'] = 0.0
        
        if 'is_valid_url' not in result:
            # Try to determine if it's valid with regex
            result['is_valid_url'] = bool(re.match(r'^https?://', profile_url))
        
        if 'esports_elements' not in result:
            result['esports_elements'] = []
        
        return result
    
    except Exception as e:
        return {
            "error": str(e),
            "is_valid_url": False,
            "relevance_score": 0.0,
            "esports_elements": [],
            "suspicious_elements": ["Failed to analyze profile"]
        }

def analyze_social_media(platform_data, platform):
    """
    Analyze social media data to identify esports-related interests.
    
    Args:
        platform_data: Dictionary with social media data
        platform: Platform name (twitter, facebook, etc.)
    
    Returns:
        Dictionary with analysis results
    """
    prompt = (f"Analyze this {platform} profile data to identify esports-related interests, "
              f"teams followed, and general level of engagement with esports content. "
              f"Here's the data: {json.dumps(platform_data)}. "
              "Provide: "
              "1. An esports_engagement_score from 0.0 to 1.0 "
              "2. List of identified esports teams or brands the user follows/interacts with "
              "3. List of esports games the user shows interest in "
              "4. Overall assessment of this user's authenticity as an esports fan "
              "Return results in JSON format.")
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in analyzing social media profiles."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        
        return json.loads(response.choices[0].message.content)
    
    except Exception as e:
        return {
            "error": str(e),
            "esports_engagement_score": 0.0,
            "teams": [],
            "games": [],
            "authenticity_assessment": "Could not analyze profile data"
        }

# Constants for validation thresholds
VALIDATION_SCORE_THRESHOLD = 0.7  # Minimum score to consider document valid
NAME_MATCH_THRESHOLD = 0.8  # Minimum score to consider name match valid

def calculate_name_similarity(name1, name2):
    """Simple function to calculate name similarity between 0 and 1."""
    # Convert to lowercase and split into words
    words1 = set(name1.lower().split())
    words2 = set(name2.lower().split())
    
    # Calculate Jaccard similarity
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0
