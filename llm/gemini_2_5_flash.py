"""Gemini 2.5 Flash LLM module."""

import os
import google.generativeai as genai
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def llm(question: str, system_prompt: Optional[str] = None) -> str:
    """
    Generate response using Gemini 2.5 Flash model
    
    Parameters
    ----------
    question : str
        User's question or prompt
    system_prompt : Optional[str]
        System prompt to guide the model's behavior (optional)
    
    Returns
    -------
    str
        Generated response from Gemini model
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GEMINI_API")
        if not api_key:
            return "Error: GEMINI_API key not found in environment variables"
        
        genai.configure(api_key=api_key)
        
        # Initialize model (Gemini 2.5 Flash)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Add system prompt if provided
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {question}"
        else:
            full_prompt = question
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        return response.text
        
    except Exception as e:
        return f"Error generating response: {str(e)}"

if __name__ == "__main__":
    # Test code
    print("=== Gemini 2.5 Flash Test ===")
    
    # Basic question test
    test_question = "What is the difference between Python lists and tuples?"
    print(f"Question: {test_question}")
    response = llm(test_question)
    print(f"Answer: {response}\n")
    
    # Test with system prompt
    system_prompt = "You are a helpful AI assistant. Please provide concise and clear answers."
    test_question2 = "Hi my name is Jun."
    print(f"System prompt: {system_prompt}")
    print(f"Question: {test_question2}")
    response2 = llm(test_question2, system_prompt)
    print(f"Answer: {response2}")