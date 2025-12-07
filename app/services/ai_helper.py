"""
AI Assistant Helper using OpenAI ChatGPT API
Provides intelligent responses for security, data science, and IT operations
"""

import os
import requests
import json

# Set your OpenAI API key
OPENAI_API_KEY = "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"


def call_chatgpt(prompt, domain="general", max_tokens=500):
    """
    Call ChatGPT API with a prompt

    Args:
        prompt (str): User's question or prompt
        domain (str): Domain context (cybersecurity, data_science, it_operations)
        max_tokens (int): Maximum response length

    Returns:
        tuple: (success: bool, response: str)
    """

    # Domain-specific system messages
    system_messages = {
        "cybersecurity": """You are a cybersecurity expert assistant. Provide clear, 
        actionable advice on security incidents, threat analysis, and best practices. 
        Keep responses concise and practical.""",

        "data_science": """You are a data science expert assistant. Help with dataset 
        analysis, statistical explanations, visualization suggestions, and data insights. 
        Explain concepts clearly for students and professionals.""",

        "it_operations": """You are an IT operations expert assistant. Provide guidance 
        on ticket management, troubleshooting, IT best practices, and resolution strategies. 
        Keep responses practical and solution-oriented.""",

        "general": """You are a helpful AI assistant for a multi-domain intelligence 
        platform. Provide clear, accurate, and actionable information."""
    }

    try:
        # Validate API key
        if not OPENAI_API_KEY or OPENAI_API_KEY == "":
            return False, "API key not configured. Please set OPENAI_API_KEY."

        # Prepare the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_messages.get(domain, system_messages["general"])},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        # Make the API call
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        # Check for successful response
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content'].strip()
            return True, message

        elif response.status_code == 401:
            return False, "Invalid API key. Please check your OpenAI API key."

        elif response.status_code == 429:
            return False, "API rate limit exceeded. Please try again later."

        elif response.status_code == 500:
            return False, "OpenAI service error. Please try again later."

        else:
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            return False, f"API Error: {error_message}"

    except requests.exceptions.Timeout:
        return False, "Request timed out. Please try again."

    except requests.exceptions.ConnectionError:
        return False, "Connection error. Please check your internet connection."

    except Exception as e:
        return False, f"Error: {str(e)}"


def get_security_advice(incident_description):
    """
    Get security advice for a specific incident

    Args:
        incident_description (str): Description of the security incident

    Returns:
        tuple: (success: bool, advice: str)
    """
    prompt = f"""Analyze this cybersecurity incident and provide:
1. Severity assessment
2. Immediate actions to take
3. Prevention measures for the future

Incident: {incident_description}"""

    return call_chatgpt(prompt, domain="cybersecurity", max_tokens=400)


def get_data_insights(dataset_info):
    """
    Get insights about a dataset

    Args:
        dataset_info (str): Information about the dataset

    Returns:
        tuple: (success: bool, insights: str)
    """
    prompt = f"""Provide insights and analysis suggestions for this dataset:

{dataset_info}

Include:
1. Potential analysis approaches
2. Visualization recommendations
3. Key metrics to explore"""

    return call_chatgpt(prompt, domain="data_science", max_tokens=400)


def get_it_solution(ticket_description):
    """
    Get IT troubleshooting advice

    Args:
        ticket_description (str): Description of the IT issue

    Returns:
        tuple: (success: bool, solution: str)
    """
    prompt = f"""Provide troubleshooting steps for this IT issue:

Issue: {ticket_description}

Include:
1. Possible root causes
2. Step-by-step resolution
3. Prevention tips"""

    return call_chatgpt(prompt, domain="it_operations", max_tokens=400)


def chat_with_ai(message, domain="general", conversation_history=None):
    """
    General chat interface with conversation history support

    Args:
        message (str): User's message
        domain (str): Domain context
        conversation_history (list): Previous messages in format [{"role": "user/assistant", "content": "..."}]

    Returns:
        tuple: (success: bool, response: str)
    """

    system_messages = {
        "cybersecurity": "You are a cybersecurity expert assistant.",
        "data_science": "You are a data science expert assistant.",
        "it_operations": "You are an IT operations expert assistant.",
        "general": "You are a helpful AI assistant."
    }

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        # Build messages array with history
        messages = [{"role": "system", "content": system_messages.get(domain, system_messages["general"])}]

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": message})

        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return True, result['choices'][0]['message']['content'].strip()
        else:
            return False, f"Error: {response.status_code}"

    except Exception as e:
        return False, f"Error: {str(e)}"