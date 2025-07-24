# OpenRouter Provider Support

This document explains how to use the new OpenRouter provider support in Autodidact.

## Overview

Autodidact now supports multiple AI providers:

- **OpenRouter**: Access to Claude, Gemini, Perplexity and other top models with deep research
- **OpenAI**: Full deep research capabilities with web search

## Setup

### 1. Choose Your Provider

When you first run Autodidact, you'll see a provider selection dialog. You can choose between:

- **OpenRouter**: Best for diverse model options, cost optimization, and access to latest models
- **OpenAI**: Best for OpenAI-specific features and workflows

### 2. Get an API Key

#### For OpenAI:
1. Visit https://platform.openai.com/api-keys
2. Create a new API key (starts with `sk-`)
3. Copy the key

#### For OpenRouter:
1. Visit https://openrouter.ai/keys
2. Create a new API key (starts with `sk-or-`)
3. Copy the key

### 3. Configure in Autodidact

1. Paste your API key in the setup dialog
2. The app will validate the key
3. Your configuration is saved locally and securely

## Features by Provider

### OpenAI Features
- ✅ Deep Research with web search
- ✅ GPT-4o-mini for conversations
- ✅ o4-mini-deep-research for comprehensive research
- ✅ Background job processing

### OpenRouter Features
- ✅ Deep Research with Perplexity Sonar
- ✅ Claude 3.5 Sonnet/Haiku models
- ✅ Access to Gemini, GPT, and other models
- ✅ Competitive pricing
- ✅ Web search capabilities via Perplexity
- ✅ Background job processing

## Switching Providers

You can switch providers anytime:

1. Go to Settings
2. Select a different provider from the dropdown
3. Configure the API key for that provider
4. Start using the new provider immediately

## Model Configuration

Each provider has predefined model configurations:

### OpenAI Models
- Chat: `gpt-4o-mini`
- Deep Research: `o4-mini-deep-research-2025-06-26`

### OpenRouter Models
- Deep Research: `perplexity/sonar-deep-research`
- Chat: `anthropic/claude-3.5-haiku`

## Cost Comparison

### OpenAI Pricing (approximate)
- Topic clarification: $0.01-0.02
- Deep research: $0.50-2.00 per topic
- Tutoring sessions: $0.02-0.05 per 30-minute session

### OpenRouter Pricing (approximate)
- Varies by model chosen
- Perplexity Sonar Deep Research: ~$0.01-0.05 per research query
- Claude Haiku: ~$0.001 per request
- Claude Sonnet: ~$0.01-0.05 per request
- Generally more cost-effective for most interactions

## Technical Details

### Backward Compatibility
- Existing OpenAI setups continue to work without changes
- Legacy `openai_api_key` configuration is automatically migrated
- Default provider remains OpenAI

### Provider Abstraction
- Unified API client interface
- Automatic fallback for unsupported features
- Provider-specific error handling

### Configuration Storage
All provider configurations are stored in `~/.autodidact/.env.json`:

```json
{
  "provider": "openrouter",
  "openai_api_key": "sk-...",
  "openrouter_api_key": "sk-or-..."
}
```

## Troubleshooting

### Common Issues

1. **"Provider configuration error"**
   - Check that you have an API key configured for the selected provider
   - Try switching to a different provider with a valid API key

2. **"API key validation failed"**
   - Verify your API key is correct and active
   - Check that the key has the right prefix (`sk-` for OpenAI, `sk-or-` for OpenRouter)

3. **"Deep research not available"**
   - This should no longer occur - OpenRouter now supports deep research via Perplexity Sonar
   - If you see this message, check that you're using the latest version

### Getting Help

1. Check the Settings page for provider status
2. Try the API key validation in Settings
3. Check the console logs for detailed error messages
4. Open an issue on GitHub if problems persist

## Migration Guide

### From OpenAI-only to Multi-provider

Your existing setup will continue to work. To add OpenRouter support:

1. Go to Settings
2. Switch provider to OpenRouter
3. Add your OpenRouter API key
4. Test with a simple topic and enjoy access to Perplexity Sonar deep research

You can switch back to OpenAI anytime without losing your configuration.