# QA Chatbot API

A Python-based chatbot API designed for question answering, leveraging natural language processing to provide accurate responses to user queries.

## Overview

This project implements a question-answering chatbot API that processes user input and generates relevant answers. The system is built with modern Python frameworks and includes testing capabilities for quality assurance.

## Features

- Natural language question processing
- Intelligent answer generation
- API endpoints for chat interaction
- LLM (Large Language Model) integration
- Comprehensive test suite
- Swagger UI for API documentation and testing

## Project Structure

```
qa-chatbot-api/
├── app/
│   ├── __pycache__/
│   ├── chat.py          # Core chat functionality
│   ├── llm.py           # Language model integration
│   └── main.py          # Main application entry point
├── include/             # Additional resources
├── lib/                 # Library dependencies
├── scripts/             # Utility scripts
├── test/
│   ├── __pycache__/
│   ├── .pytest_cache/
│   └── test_chat.py     # Test cases for chat functionality
├── venv/                # Virtual environment (not tracked in git)
├── .env                 # Environment variables (not tracked in git)
├── list.py              # Utility functions
├── pyenv.cfg            # Python environment configuration
├── requirements.txt     # Project dependencies
└── README.md            # This file
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Git
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mounishreddy027/qa-chatbot-api.git
   cd qa-chatbot-api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   - **Windows PowerShell:**
     ```powershell
     venv\Scripts\activate
     ```
   
   - **Windows Command Prompt:**
     ```cmd
     venv\Scripts\activate.bat
     ```
   
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Environment configuration**
   
   Create a `.env` file in the root directory:
   ```bash
   # Windows PowerShell
   New-Item -Path ".env" -ItemType "file"
   
   # Windows Command Prompt
   type nul > .env
   
   # macOS/Linux
   touch .env
   ```
   
   Add the following environment variables to the file:
   ```
   API_KEY=your_api_key_here
   PORT=8000
   DEBUG=True
   # Add other required environment variables
   ```

### Running the Application

1. **Start the API server**
   ```bash
   python app/main.py
   ```

2. **Access the API**
   - The API will be available at: http://localhost:8000 (or the port specified in your .env)
   - You can test it using curl, Postman, or any API client
   - Swagger UI is available at: http://localhost:8000/docs

### API Endpoints

#### Using Swagger UI

The API includes Swagger UI documentation that allows you to explore and test all available endpoints directly from your browser:

1. Start the server as described above
2. Open your browser and navigate to http://localhost:8000/docs
3. You'll see all available endpoints with their descriptions, parameters, and response models

#### Key Endpoints

1. **Health Check**
   - **Endpoint**: `/health`
   - **Method**: GET
   - **Description**: Check if the API is running
   - **Via Swagger UI**: Click on the endpoint, then click "Try it out" followed by "Execute"

2. **Ask Question**
   - **Endpoint**: `/ask`
   - **Method**: POST
   - **Description**: Send a question to get an answer from the chatbot
   - **Via Swagger UI**: 
     - Click on the `/ask` endpoint
     - Click "Try it out"
     - Enter your question in the request body:
       ```json
       {
         "question": "What is artificial intelligence?"
       }
       ```
     - Click "Execute"

3. **Get Chat History**
   - **Endpoint**: `/history`
   - **Method**: GET
   - **Description**: Retrieve chat history
   - **Parameters**: 
     - `limit` (optional): Number of recent conversations to retrieve
   - **Via Swagger UI**: Click on the endpoint, adjust any parameters, then click "Try it out" followed by "Execute"

4. **Delete Chat History**
   - **Endpoint**: `/history/{id}`
   - **Method**: DELETE
   - **Description**: Delete a specific chat history entry
   - **Parameters**:
     - `id`: ID of the chat history entry to delete
   - **Via Swagger UI**:
     - Click on the endpoint
     - Enter the ID in the parameter field
     - Click "Try it out" followed by "Execute"

### Testing

Run the test suite to ensure everything is working properly:
```bash
pytest
```

For more specific tests:
```bash
pytest test/test_chat.py
```

## Development Workflow

1. **Update your local repository**
   ```bash
   git pull origin main
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature-name
   ```

3. **Make your changes and commit them**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

4. **Push to GitHub**
   ```bash
   git push origin feature-name
   ```

5. **Create a pull request** on GitHub to merge your changes

## Deployment

### Local Deployment
Follow the setup instructions above.

### Server Deployment
1. Clone the repository on your server
2. Follow the setup instructions
3. Configure a production web server (like Nginx or Apache) to proxy requests to the application
4. Set up a process manager (like Supervisord or systemd) to keep the application running

## API Authentication

For protected endpoints, you'll need to include an API key in your requests:

- **Via Swagger UI**: Some endpoints may require authentication. Look for the "Authorize" button at the top of the Swagger UI page.
- **Via HTTP request**: Include your API key in the header: `X-API-Key: your_api_key_here`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

[MIT License](LICENSE)

## Contact

Mounish Reddy - [GitHub Profile](https://github.com/mounishreddy027)

Project Link: [https://github.com/mounishreddy027/qa-chatbot-api](https://github.com/mounishreddy027/qa-chatbot-api)
