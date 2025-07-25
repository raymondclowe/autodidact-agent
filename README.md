# Autodidact - AI-Powered Learning Assistant

Note: I have a bunch of kinks I need to iron out with this project (I'll do them over the next few days), but the main structure is mostly done

Here is a quick video overview of the project: 
https://github.com/baibhavbista/autodidact-agent


Autodidact is an AI-powered personalized learning assistant that creates custom study plans, provides interactive tutoring sessions, and tracks your learning progress.

## Features

- 🔍 **Deep Research**: AI investigates your topic and creates comprehensive study plans
- 📊 **Knowledge Graphs**: Visual representation of concepts and their prerequisites
- 👨‍🏫 **AI Tutoring**: Personalized 30-minute learning sessions with an AI tutor
- 📈 **Progress Tracking**: Monitor your mastery of each concept over time
- 🔄 **Session Recovery**: Resume interrupted learning sessions

## Installation


### Option 1: Docker (Recommended)

The easiest way to run Autodidact is using Docker:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/autodidact.git
cd autodidact
```

2. Build the Docker image locally (since it is not published on Docker Hub):
```bash
docker build -t autodidact-agent .
```

3. Run with Docker Compose:
```bash
docker compose up
```

The application will be available at http://localhost:8501

**Note**: Your data (database, configuration, projects) will be persisted in a Docker volume called `autodidact_data`, so it will be preserved across container restarts.

### Option 2: Local Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/autodidact.git
cd autodidact
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

**Alternative**: Use the wrapper script for additional features like debug mode:
```bash
python run.py
```

## Setup

On first run, you'll need to choose an AI provider and provide your API key. The app supports:

- **OpenRouter**: Access to multiple models (Claude, Gemini, Perplexity) with deep research via Perplexity Sonar
- **OpenAI**: Full features including deep research with web search

The app will guide you through the setup process and store your configuration securely at `~/.autodidact/.env.json`.

## Database Schema

The application uses SQLite with the following schema:

- **project**: Learning projects with topics and metadata
- **node**: Knowledge graph nodes (concepts to learn)
- **edge**: Relationships between concepts
- **learning_objective**: Specific objectives for each concept
- **session**: Learning sessions linking projects and nodes
- **transcript**: Conversation history for each session

### Database Migration

If you're upgrading from an earlier version, run the migration script:

```bash
python backend/migrate_db.py
```

This will update your database schema to include the new session tracking features.

## AI Provider Options

Autodidact supports multiple AI providers to give you flexibility in model choice and cost. You can configure multiple providers and switch between them seamlessly.

### Provider Comparison

| Feature | OpenRouter | OpenAI |
|---------|------------|---------|
| **Deep Research** | ✅ Perplexity Sonar Deep Research | ✅ o4-mini-deep-research |
| **Web Search** | ✅ Built-in via Perplexity | ✅ Built-in |
| **Chat Models** | Claude 3.5 Sonnet/Haiku, Gemini | GPT-4o-mini |
| **Cost Range** | $0.001-0.05 per request | $0.50-2.00 (research), $0.02-0.05 (chat) |
| **Best For** | Model diversity, cost optimization, access to latest models | OpenAI-specific features and workflows |

### OpenRouter Provider
- **Features**: Access to Claude, Gemini, Perplexity and other top models with deep research capabilities
- **Models**:
  - `perplexity/sonar-deep-research` for comprehensive research with web search
  - `anthropic/claude-3.5-haiku` for fast, cost-effective conversations
  - Many other models available (Gemini, GPT variants, etc.)
- **Setup**: Get API key from [OpenRouter](https://openrouter.ai/keys)
- **API Key Format**: Starts with `sk-or-`
- **Best for**: Users who want model diversity, potentially lower costs, or prefer Claude/Gemini/Perplexity

### OpenAI Provider
- **Features**: Full deep research with web search capabilities
- **Models**: 
  - `o4-mini-deep-research-2025-06-26` for comprehensive research
  - `gpt-4o-mini` for interactive tutoring sessions
- **Setup**: Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
- **API Key Format**: Starts with `sk-`
- **Best for**: Users who need OpenAI-specific features and models

### Provider Setup Examples

#### Initial Setup (New Users)
When you first run Autodidact, you'll see a provider selection dialog:

1. **Choose OpenRouter** for model diversity, cost optimization, and access to the latest models
2. **Choose OpenAI** for OpenAI-specific features and workflows
3. Enter your API key when prompted
4. The app validates your key and saves the configuration

#### Adding Multiple Providers
You can configure multiple providers and switch between them:

```bash
# Your config will be stored at ~/.autodidact/.env.json
{
  "provider": "openrouter",
  "openrouter_api_key": "sk-or-your-openrouter-key",
  "openai_api_key": "sk-your-openai-key"
}
```

#### Switching Providers
You can change providers anytime through the Settings page:
1. Go to **Settings** in the sidebar
2. Select your preferred provider
3. Configure API keys for any new providers
4. Changes take effect immediately

### Programming Examples

The provider system is designed to work seamlessly in code:

#### Basic Usage
```python
from utils.providers import create_client, get_model_for_task

# Works with your currently configured provider
client = create_client()
model = get_model_for_task("chat")

# Make API calls (same interface regardless of provider)
response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Explain quantum physics"}]
)
```

#### Provider-Specific Operations
```python
from utils.providers import create_client, get_model_for_task, get_provider_info
from utils.config import get_current_provider, set_current_provider

# Check current provider capabilities
current = get_current_provider()
info = get_provider_info(current)

if info.get("supports_deep_research"):
    # Use deep research model
    model = get_model_for_task("deep_research")
    print(f"Using {model} for comprehensive research")
else:
    # Fall back to chat model for research-style queries
    model = get_model_for_task("chat")
    print(f"Using {model} for research (no deep research available)")

# Switch providers programmatically
set_current_provider("openrouter")  # Switch to OpenRouter 
set_current_provider("openai")      # Switch to OpenAI
```

#### Multi-Provider Workflows
```python
from utils.providers import create_client
from utils.config import set_current_provider

# Use OpenRouter for research phase (Perplexity Sonar Deep Research)
set_current_provider("openrouter")
research_client = create_client()
research_response = research_client.chat.completions.create(
    model="perplexity/sonar-deep-research",
    messages=[{"role": "user", "content": "Research latest developments in AI"}]
)

# Switch to OpenAI for alternative approach
set_current_provider("openai") 
openai_client = create_client()
openai_response = openai_client.chat.completions.create(
    model="o4-mini-deep-research-2025-06-26",
    messages=[{"role": "user", "content": "Research latest developments in AI"}]
)
```

### Usage Recommendations

#### For Beginners
- **Start with OpenRouter** if you want access to multiple top models and cost-effective deep research
- **Start with OpenAI** if you prefer OpenAI-specific models and workflows

#### For Cost Optimization
- **Research Phase**: Use OpenRouter for comprehensive research with Perplexity Sonar
- **Learning Phase**: Continue with OpenRouter for interactive tutoring sessions with Claude
- **Monitor usage** in your provider dashboards to track costs

#### For Model Experimentation
- Configure both providers to access different model families
- **OpenRouter**: Access to Claude, Gemini, Perplexity Sonar, and many other models
- **OpenAI**: Access to latest GPT models and o4 deep research

### Troubleshooting

#### Common Issues
1. **API Key Invalid**: Ensure key format matches provider (sk- vs sk-or-)
2. **Provider Switch Failed**: Check that API keys are configured for target provider
3. **Model Not Available**: Some models may not be available in your region

#### Getting Help
- Check your API key format matches the provider requirements
- Verify your account has credits/billing set up with the provider
- See the [OpenRouter Guide](OPENROUTER_GUIDE.md) for detailed OpenRouter setup

You can configure multiple providers and switch between them anytime in Settings.

## Quick Start Guide

### New Users - Choose Your Provider

1. **For model diversity and cost optimization**: Choose **OpenRouter**
   ```bash
   # Get API key from https://openrouter.ai/keys  
   # Format: sk-or-...
   ```

2. **For OpenAI-specific features**: Choose **OpenAI**
   ```bash
   # Get API key from https://platform.openai.com/api-keys
   # Format: sk-...
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Follow the setup wizard** to configure your chosen provider

### Existing Users - Add More Providers

1. Go to **Settings** in the sidebar
2. Click **"Configure Additional Provider"**
3. Enter API key for new provider
4. Switch between providers anytime

## Usage

1. **Start a New Project**: Enter a topic you want to learn
2. **Review the Plan**: Examine the generated knowledge graph and report
3. **Begin Learning**: Start tutoring sessions for available topics
4. **Track Progress**: Monitor your mastery levels across concepts

### Debug Mode

Autodidact supports debug mode for troubleshooting and development. There are two ways to enable it:

#### Method 1: Using the wrapper script (Recommended)
```bash
python run.py --debug
```

#### Method 2: Using environment variable
```bash
AUTODIDACT_DEBUG=true streamlit run app.py
```

When debug mode is enabled, you'll see:
- 🐛 A red debug banner at the top of the app
- Enhanced logging to `~/.autodidact/debug-YYYYMMDD-HHMMSS.log`
- Detailed error information and system state

**Note**: The original `streamlit run app.py --debug` command won't work because Streamlit doesn't recognize the `--debug` flag. Use one of the methods above instead.

## Project Structure

```
autodidact/
├── app.py                 # Main Streamlit application
├── backend/
│   ├── db.py             # Database operations
│   ├── jobs.py           # AI job processing
│   ├── graph.py          # LangGraph tutor implementation
│   ├── deep_research.py  # Deep research module
│   └── migrate_db.py     # Database migration script
├── components/
│   └── graph_viz.py      # Graph visualization
├── utils/
│   ├── config.py         # Configuration management
│   ├── providers.py      # AI provider abstraction layer
│   └── deep_research.py  # Deep research utilities
├── OPENROUTER_GUIDE.md   # Detailed OpenRouter setup guide
└── requirements.txt      # Python dependencies
```

## Development

To contribute or modify Autodidact:

1. Follow the installation steps above
2. Make your changes
3. Test thoroughly with various topics
4. Submit a pull request

## Requirements

- Python 3.8+
- API key from a supported provider:
  - **OpenAI**: For full deep research capabilities ([Get API Key](https://platform.openai.com/api-keys))
  - **OpenRouter**: For access to multiple AI models ([Get API Key](https://openrouter.ai/keys))

## Documentation

- **[OpenRouter Setup Guide](OPENROUTER_GUIDE.md)**: Detailed setup instructions for OpenRouter
- **[Architecture Guide](ARCHITECTURE.md)**: Technical details about the provider system

## License

MIT License - see LICENSE file for details
