# Chat-with-Documents Chatbot  

A comprehensive AI chatbot application with in-memory storage, file upload capabilities, voice features, and authentication integration. 

## Features List

### Core Functionality
- **Document Chat Interface**: Generic chatbot that allows users to chat with uploaded documents
- **In-Memory Storage**: Session-based document storage with conversation context
- **Authentication Integration**: Connects to existing UserAndAuthSystem via SSO
- **Real-time Communication**: WebSocket-based chat interface

### File Processing
- **Drag & Drop Upload**: Support for multiple file types up to 50MB each
- **Document Processing**: 
  - Text files (.txt)
  - PDF documents (.pdf) with OCR fallback for image-based PDFs
  - Word documents (.doc, .docx)
  - Rich Text Format (.rtf)
  - Images (.jpg, .jpeg, .png, .bmp) with OCR
- **Full Document Integration**: Complete document content is processed and added to the bot's knowledge base
- **OCR Download**: Download processed OCR PDFs after completion

### Voice Features
- **Speech-to-Text**: Whisper API integration for voice input
- **Text-to-Speech**: Multiple voice options using OpenAI TTS
- **Hold-to-Record**: Simple voice recording interface

### Storage System
- **Session-Based Storage**: Documents stored in memory per user session
- **Document Limit**: Maintains up to 5 most recent documents per user
- **No Persistence**: Data cleared on server restart or user logout
- **Real-time Processing**: Background OCR processing with progress tracking

### Export & Sharing
- **PDF Export**: Save chat history as PDF
- **Print Function**: Print conversation history
- **Client-Side Logs**: Conversation logs managed in browser session

## Installation

### Prerequisites
- Python 3.8+
- Flask application server
- OpenAI API key
- Access to UserAndAuthSystem for SSO authentication

### Environment Setup

Create a `.env` file with your configuration variables:
```  
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
AUTH_SERVICE_URL=your_auth_system_url
```

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the Flask application:
```bash
python app.py
```

3. The application will be available at `http://localhost:5000`

### Heroku Deployment

The application is configured for Heroku deployment with:
- Procfile for web process
- Requirements.txt for Python dependencies
- Environment variables configured in Heroku dashboard

## Project Structure

```
basic-chatbot/
├── app.py                 # Main Flask application
├── sso_client_utils.py    # SSO authentication utilities
├── public/
│   ├── index.html         # Frontend template
│   ├── js/
│   │   └── app.js         # Frontend JavaScript
│   └── styles/
│       └── main.css       # Styling
├── uploads/               # Temporary file uploads
├── downloads/             # Processed OCR files
├── requirements.txt       # Python dependencies
└── README.md
```

## Installation

To get started with the chatbot, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/basic-chatbot.git
   ```

2. Navigate to the project directory:
   ```
   cd basic-chatbot
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the chatbot, execute the following command:

```
python app.py
```

This will start the Flask application and you can begin interacting with the chatbot.

## Features

- **Document Interaction**: Upload and chat with various document types
- **Intelligent Responses**: AI-powered responses using OpenAI's GPT models
- **OCR Processing**: Automatic OCR for image-based PDFs with download capability
- **Progress Tracking**: Real-time progress updates for file processing
- **SSO Integration**: Seamless authentication through existing user system

## Memory Management

- Documents are stored in server memory during user sessions
- Maximum of 5 documents per user to manage memory usage
- Documents are automatically cleared when users logout
- No persistent storage - suitable for temporary document analysis

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.   