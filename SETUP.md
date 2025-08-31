# 🤖 AI Social Media Chatbot Setup Guide

## Prerequisites

1. Python 3.8 or higher
2. pip (Python package installer)
3. API Keys:
   - Google API Key (for Gemini)

## Setup Instructions

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root with:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## Running the Chatbot

1. **Start the chatbot**
   ```bash
   python social_media_chatbot.py
   ```

2. **Available commands**
   - `generate post [platform] [niche] [audience]`: Generate a complete post
   - `suggest posts [platform/niche]`: Get post suggestions
   - `search posts [query]`: Search similar posts
   - `chat`: Have a conversation about social media strategy
   - `clear`: Clear conversation history
   - `help`: Show help message
   - `exit`: End conversation

## Features

1. **Post Generation**
   - Topics and titles (using Gemini)
   - Content creation (using Gemini)
   - Hashtag optimization (using Gemini)
   - Platform-specific formatting

2. **Content Management**
   - Saves posts as JSON and TXT files
   - Organized file structure
   - Search and retrieval capabilities

3. **Smart Conversation**
   - Context-aware responses
   - Social media expertise
   - Strategy suggestions

## File Structure

```
project/
├── social_media_chatbot.py  # Main chatbot code
├── requirements.txt         # Python dependencies
├── .env                    # API keys (create this)
└── posts/                  # Generated posts (created automatically)
    ├── platform_niche_date.json
    └── platform_niche_date.txt
```

## Troubleshooting

1. **ImportError: No module found**
   - Ensure you've activated the virtual environment
   - Run `pip install -r requirements.txt` again

2. **API Key Errors**
   - Check if `.env` file exists
   - Verify API key is correct
   - Ensure no spaces around API key in `.env`

3. **Generation Errors**
   - Check internet connection
   - Verify API keys are valid
   - Check API quotas/limits

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages
3. Contact support team

## Updates

The chatbot uses:
- Gemini for content generation
- LangChain for conversation management
- Modern Python best practices

Keep dependencies updated for best performance!