import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    error_msg = "GEMINI_API_KEY not found in environment variables"
    logger.error(error_msg)
    raise ValueError(error_msg)

# Configure the API client
try:
    genai.configure(api_key=api_key)
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")
    raise

def get_answer(prompt: str, model: str = "models/gemini-1.5-flash", 
              temperature: float = 0.7) -> Dict[str, Any]:
    """
    Get an answer from the LLM with comprehensive error handling.
    
    Args:
        prompt: The question or prompt to send to the LLM
        model: The model identifier to use
        temperature: The temperature parameter for generation
        
    Returns:
        Dictionary containing the answer or error information
    """
    # Input validation
    if not prompt or not prompt.strip():
        logger.warning("Empty prompt received")
        return {
            "success": False,
            "error": "Empty prompt provided",
            "answer": "I need a question to respond to."
        }
    
    if not isinstance(temperature, (float, int)) or temperature < 0 or temperature > 1:
        logger.warning(f"Invalid temperature value: {temperature}, using default 0.7")
        temperature = 0.7
        
    # Sanitize prompt
    prompt = prompt.strip()
    
    try:
        logger.info(f"Sending prompt to Gemini model: {model}")
        # Initialize the model
        generative_model = genai.GenerativeModel(model)
        
        # Start chat and send message
        chat = generative_model.start_chat()
        response = chat.send_message(prompt)
        
        logger.info("Successfully received response from Gemini API")
        return {
            "success": True,
            "answer": response.text,
            "model": model
        }
    except genai.types.BlockedPromptException as e:
        logger.warning(f"Blocked prompt: {str(e)}")
        return {
            "success": False,
            "error": "Your request was blocked due to content safety restrictions",
            "answer": "I'm unable to respond to this query due to content safety policies."
        }
    except Exception as e:
        logger.error(f"Error getting answer from LLM: {str(e)}")
        return {
            "success": False, 
            "error": str(e),
            "answer": "I encountered an error processing your request. Please try again later."
        }