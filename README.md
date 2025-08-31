# LangChain Google Generative AI Project

A Python project demonstrating the integration of LangChain with Google's Generative AI (Gemini) models for AI-powered text generation and conversation.

## 🚀 Features

- **Secure API Key Management**: Environment-based configuration using `.env` files
- **Google Gemini Integration**: Leverages Google's latest Gemini-1.5-flash model
- **LangChain Framework**: Built with LangChain for robust AI application development
- **Jupyter Notebook Support**: Interactive development environment
- **Error Handling**: Comprehensive validation and error management

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)

### Python Dependencies
See `requirements.txt` for the complete list. Key packages include:
- `langchain` - Core LangChain framework
- `langchain-google-genai` - Google Generative AI integration
- `python-dotenv` - Environment variable management
- `jupyter` - Notebook environment

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd Langchain
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv langchain_env

# Activate virtual environment
# On macOS/Linux:
source langchain_env/bin/activate
# On Windows:
# langchain_env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
1. Create a `.env` file in the project root:
```bash
cp .env.example .env  # If you have an example file
# OR create manually:
touch .env
```

2. Add your Google API key to the `.env` file:
```env
# Environment variables for Langchain project
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_actual_google_api_key_here
```

## 🔑 Getting Your Google API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key to your `.env` file
5. Ensure the Generative AI API is enabled in your Google Cloud Console

## 📁 Project Structure

```
Langchain/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env                     # Environment variables (not in git)
├── .gitignore              # Git ignore rules
├── app.ipynb               # Main Jupyter notebook
├── langchain_env/          # Virtual environment
└── ...
```

## 🚀 Usage

### Running the Jupyter Notebook

1. **Start Jupyter Notebook**:
```bash
jupyter notebook
```

2. **Open `app.ipynb`** in your browser

3. **Run the cells** to see the AI in action!

### Basic Code Example

```python
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Initialize the model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Generate a response
response = llm.invoke("Tell me a joke about Python programming!")
print(response.content)
```

## 🔧 Configuration Options

### Model Parameters
- **model**: Choose from available Gemini models (e.g., "gemini-1.5-flash", "gemini-1.5-pro")
- **temperature**: Controls randomness (0.0 = deterministic, 1.0 = very random)
- **max_tokens**: Maximum number of tokens in the response

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Your Google Generative AI API key | Yes |

## 🛡️ Security Best Practices

- ✅ **Never commit API keys** to version control
- ✅ **Use environment variables** for sensitive data
- ✅ **Add `.env` to `.gitignore`**
- ✅ **Regularly rotate API keys**
- ✅ **Monitor API usage** in Google Cloud Console

## 🐛 Troubleshooting

### Common Issues

#### 1. "API key not valid" Error
- Verify your API key is correct in the `.env` file
- Ensure the Generative AI API is enabled in Google Cloud Console
- Check if your API key has the necessary permissions

#### 2. "GOOGLE_API_KEY environment variable is not set"
- Confirm the `.env` file exists in the project root
- Check that the variable name is exactly `GOOGLE_API_KEY`
- Restart your Jupyter kernel after modifying `.env`

#### 3. Import Errors
- Ensure your virtual environment is activated
- Run `pip install -r requirements.txt` to install dependencies
- Verify you're using the correct Python interpreter

#### 4. Jupyter Kernel Issues
- Restart the kernel: Kernel → Restart
- Ensure the notebook is using the `langchain_env` kernel
- Check kernel list: `jupyter kernelspec list`

## 📚 Additional Resources

- [LangChain Documentation](https://docs.langchain.com/)
- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Python-dotenv Documentation](https://github.com/theskumar/python-dotenv)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the [LangChain documentation](https://docs.langchain.com/)
3. Create an issue in this repository
4. Check Google AI documentation for API-related questions

---

**Happy Coding! 🎉**
