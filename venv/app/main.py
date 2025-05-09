from fastapi import FastAPI, HTTPException, Depends, Request, status, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional
import logging
import time

from app.llm import get_answer
from app.chat import add_to_history, get_history, connect_db, disconnect_db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app with enhanced documentation
app = FastAPI(
    title="Chatbot API",
    description="""
    # Chatbot API Documentation
    
    This API allows users to interact with a chatbot backed by Gemini's LLM and maintains
    a history of conversations in a PostgreSQL database.
    
    ## Features
    
    * Ask questions and receive AI-generated answers
    * View history of previous conversations
    * Health check endpoint
    
    ## Authentication
    
    No authentication is currently required for this API.
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "chatbot",
            "description": "Operations related to chatbot interactions",
        },
        {
            "name": "history",
            "description": "Operations related to chat history",
        },
        {
            "name": "health",
            "description": "Operations related to API health",
        },
    ],
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request and response models with validation
class Question(BaseModel):
    question: str = Field(
        ..., 
        min_length=1, 
        max_length=500,
        description="The question to ask the chatbot"
    )
    
    @validator('question')
    def question_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()
    
    class Config:
        # Using json_schema_extra instead of schema_extra for Pydantic v2 compatibility
        json_schema_extra = {
            "example": {
                "question": "What is artificial intelligence?"
            }
        }

class QuestionResponse(BaseModel):
    question: str = Field(..., description="The original question asked")
    answer: str = Field(..., description="The chatbot's response")
    success: bool = Field(..., description="Whether the request was successful")
    error: Optional[str] = Field(None, description="Error message if the request failed")
    
    class Config:
        # Using json_schema_extra instead of schema_extra for Pydantic v2 compatibility
        json_schema_extra = {
            "example": {
                "question": "What is artificial intelligence?",
                "answer": "Artificial Intelligence (AI) refers to systems or machines that mimic human intelligence to perform tasks and can iteratively improve themselves based on the information they collect.",
                "success": True,
                "error": None
            }
        }

class HistoryEntry(BaseModel):
    id: int = Field(..., description="Unique identifier for the history entry")
    question: str = Field(..., description="The question that was asked")
    answer: str = Field(..., description="The answer that was provided")
    timestamp: str = Field(..., description="When the interaction occurred")
    
    class Config:
        # Using json_schema_extra instead of schema_extra for Pydantic v2 compatibility
        json_schema_extra = {
            "example": {
                "id": 1,
                "question": "What is artificial intelligence?",
                "answer": "Artificial Intelligence (AI) refers to systems or machines that mimic human intelligence to perform tasks.",
                "timestamp": "2025-05-09T12:34:56"
            }
        }

# Middleware for request timing and logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Request {request.method} {request.url.path} completed in {process_time:.3f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request {request.method} {request.url.path} failed in {process_time:.3f}s: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

# Exception handler for general exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    """
    Initialize application services on startup.
    Connects to the database and performs any necessary setup.
    """
    logger.info("Starting up the application")
    db_connected = await connect_db()
    if not db_connected:
        logger.critical("Failed to connect to database, application may not function correctly")

@app.on_event("shutdown")
async def shutdown():
    """
    Clean up application resources on shutdown.
    Disconnects from the database and performs any necessary cleanup.
    """
    logger.info("Shutting down the application")
    await disconnect_db()

# Health check endpoint
@app.get(
    "/health", 
    status_code=status.HTTP_200_OK,
    tags=["health"],
    summary="Check API health",
    description="Returns the health status of the API",
    response_description="Health status information"
)
async def health_check():
    """
    Endpoint to check if the API is running correctly.
    
    Returns:
        dict: A dictionary containing the health status of the API
    """
    return {"status": "healthy"}

# Ask endpoint with improved error handling and documentation
@app.post(
    "/ask", 
    response_model=QuestionResponse,
    tags=["chatbot"],
    summary="Ask a question to the chatbot",
    description="Send a question to the chatbot and receive an AI-generated answer. The question-answer pair will be stored in the chat history.",
    response_description="The chatbot's answer to the question along with status information",
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successful response with answer",
            "content": {
                "application/json": {
                    "example": {
                        "question": "What is artificial intelligence?",
                        "answer": "Artificial Intelligence (AI) refers to systems or machines that mimic human intelligence to perform tasks.",
                        "success": True,
                        "error": None
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "question"],
                                "msg": "ensure this value has at least 1 characters",
                                "type": "value_error.any_str.min_length"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to process your question"
                    }
                }
            }
        }
    }
)
async def ask_question(item: Question):
    """
    Ask a question to the chatbot.
    
    The question is sent to the LLM, which generates an answer.
    Both the question and answer are stored in the chat history.
    
    Args:
        item: The question to ask, as a Question object
        
    Returns:
        QuestionResponse: The answer from the chatbot along with status information
        
    Raises:
        HTTPException: If there's an error processing the question
    """
    logger.info(f"Received question: {item.question}")
    
    try:
        # Get answer from LLM
        llm_response = get_answer(item.question)
        
        if not llm_response["success"]:
            logger.warning(f"LLM error: {llm_response.get('error', 'Unknown error')}")
            
        # Prepare response
        answer = llm_response["answer"]
        
        # Add to history (don't wait for result to respond to user)
        history_added = await add_to_history(item.question, answer)
        if not history_added:
            logger.warning("Failed to add question-answer pair to history")
            
        return {
            "question": item.question,
            "answer": answer,
            "success": llm_response["success"],
            "error": llm_response.get("error")
        }
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process your question"
        )

# Get history endpoint with error handling and documentation - FIXED VERSION
@app.get(
    "/history", 
    status_code=status.HTTP_200_OK,
    tags=["history"],
    summary="Get chat history",
    description="Retrieve the history of previous chat interactions, ordered by most recent first.",
    response_description="List of previous chat interactions",
    responses={
        200: {
            "description": "Successful retrieval of chat history",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 2,
                            "question": "How does machine learning work?",
                            "answer": "Machine learning is a subset of artificial intelligence...",
                            "timestamp": "2025-05-09T14:30:45"
                        },
                        {
                            "id": 1,
                            "question": "What is artificial intelligence?",
                            "answer": "Artificial Intelligence (AI) refers to systems...",
                            "timestamp": "2025-05-09T12:34:56"
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Invalid parameters",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Limit must be between 1 and 1000"
                    }
                }
            }
        },
        500: {
            "description": "Server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to retrieve chat history"
                    }
                }
            }
        }
    }
)
async def get_chat_history(
    limit: int = Query(
        100, 
        description="Maximum number of history entries to return",
        ge=1,
        le=1000
    )
):
    """
    Retrieve chat history.
    
    Returns a list of previous question-answer pairs, ordered by most recent first.
    
    Args:
        limit: Maximum number of history entries to return (default: 100)
        
    Returns:
        List[HistoryEntry]: List of chat history entries
        
    Raises:
        HTTPException: If there's an error retrieving the history or if parameters are invalid
    """
    try:
        history = await get_history(limit)
        logger.info(f"Retrieved {len(history)} history entries")
        return history
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )

# Optional: Add custom documentation URLs
@app.get("/api-docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI documentation"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/api-redoc", include_in_schema=False)
async def custom_redoc_html():
    """Custom ReDoc documentation"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )