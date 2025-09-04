"""
Settings page
Manage API keys and provider configuration
"""

import streamlit as st
from utils.config import (
    load_api_key, save_api_key, CONFIG_FILE, get_current_provider,
    set_current_provider, SUPPORTED_PROVIDERS, load_tavily_api_key, save_tavily_api_key,
    get_cost_effective_models_setting, set_cost_effective_models_setting
)
from utils.providers import validate_api_key, get_provider_info, list_available_models
from pathlib import Path

# Ensure internal Streamlit assets load from root, not under /settings/
st.markdown('<base href="/">', unsafe_allow_html=True)

# Page header
st.markdown("# ⚙️ Settings")
st.markdown("Manage your Autodidact configuration")

# Back button
if st.button("← Back to Home", key="back_to_home"):
    st.switch_page("pages/home.py")

st.markdown("---")

# AI Provider section
st.markdown("## 🤖 AI Provider Configuration")

current_provider = get_current_provider()
provider_info = get_provider_info(current_provider)

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Current Provider")
    st.info(f"**{provider_info.get('name', current_provider.title())}**")
    st.markdown(provider_info.get('description', ''))
    
    # Provider selection
    new_provider = st.selectbox(
        "Switch Provider:",
        options=SUPPORTED_PROVIDERS,
        index=SUPPORTED_PROVIDERS.index(current_provider),
        format_func=lambda x: get_provider_info(x).get("name", x.title()),
        help="Select your preferred AI provider"
    )
    
    if new_provider != current_provider:
        if st.button("🔄 Switch Provider", type="secondary"):
            set_current_provider(new_provider)
            st.session_state.api_key = None  # Clear current API key
            st.success(f"Switched to {get_provider_info(new_provider).get('name', new_provider)}")
            st.rerun()

with col2:
    st.markdown("### Available Models")
    try:
        models = list_available_models(current_provider)
        for task, model in models.items():
            st.code(f"{task}: {model}")
    except Exception as e:
        st.warning(f"Could not load models: {e}")

# Model preferences section (only show for OpenRouter)
if current_provider == "openrouter":
    st.markdown("---")
    st.markdown("### 💰 Model Preferences")
    
    cost_effective_enabled = get_cost_effective_models_setting()
    
    new_cost_effective = st.toggle(
        "Use Cost-Effective Models",
        value=cost_effective_enabled,
        help="Switch to more affordable models when available (e.g., DeepSeek instead of Claude 4.1 for chat)"
    )
    
    if new_cost_effective != cost_effective_enabled:
        set_cost_effective_models_setting(new_cost_effective)
        if new_cost_effective:
            st.success("✅ Switched to cost-effective models! Chat will now use DeepSeek instead of Claude 4.1.")
        else:
            st.success("✅ Switched to premium models! Chat will use Claude 4.1.")
        st.rerun()
    
    # Show cost comparison
    if current_provider == "openrouter":
        with st.expander("💡 Cost Comparison"):
            if cost_effective_enabled:
                st.markdown("""
                **Current Configuration (Cost-Effective):**
                - Chat: `deepseek/deepseek-chat-v3.1` (~$0.001-0.003 per request)
                - Deep Research: `perplexity/sonar-deep-research` (~$0.01-0.05 per request)
                
                **Premium Configuration:**
                - Chat: `anthropic/claude-opus-4.1` (~$0.05-0.20 per request)
                - Deep Research: `perplexity/sonar-deep-research` (~$0.01-0.05 per request)
                """)
            else:
                st.markdown("""
                **Current Configuration (Premium):**
                - Chat: `anthropic/claude-opus-4.1` (~$0.05-0.20 per request)
                - Deep Research: `perplexity/sonar-deep-research` (~$0.01-0.05 per request)
                
                **Cost-Effective Configuration:**
                - Chat: `deepseek/deepseek-chat-v3.1` (~$0.001-0.003 per request)
                - Deep Research: `perplexity/sonar-deep-research` (~$0.01-0.05 per request)
                """)
            
            st.info("💡 **Tip**: DeepSeek v3.1 offers excellent performance at a fraction of the cost of Claude 4.1, making it ideal for learning and experimentation.")

st.markdown("---")

# API Key section
st.markdown(f"## 🔑 {provider_info.get('name', current_provider.title())} API Key")

# Check current API key status
current_key = st.session_state.get('api_key') or load_api_key(current_provider)

if current_key:
    # API key is configured
    st.success("✅ API Key is configured")
    
    # Show masked key
    masked_key = current_key[:7] + "..." + current_key[-4:]
    st.code(masked_key)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Update API Key", use_container_width=True):
            st.session_state.show_update_key = True
    
    with col2:
        if st.button("🗑️ Remove API Key", type="secondary", use_container_width=True):
            if CONFIG_FILE.exists():
                # Just remove the current provider's key, not the whole file
                from utils.config import load_config, save_config
                config = load_config()
                key_name = f"{current_provider}_api_key"
                if key_name in config:
                    del config[key_name]
                    save_config(config)
            st.session_state.api_key = None
            st.success("API key removed successfully!")
            st.rerun()
    
    # Update key form
    if st.session_state.get('show_update_key', False):
        with st.form("update_api_key"):
            st.markdown("### Update API Key")
            new_key = st.text_input(
                "New API Key:",
                type="password",
                placeholder=provider_info.get('api_key_prefix', 'sk-') + "...",
                help=f"Enter your new {provider_info.get('name', current_provider)} API key"
            )
            
            if st.form_submit_button("Save New Key", type="primary"):
                prefix = provider_info.get('api_key_prefix', 'sk-')
                if new_key and new_key.startswith(prefix):
                    with st.spinner("Validating API key..."):
                        if validate_api_key(new_key, current_provider):
                            # Save it
                            save_api_key(new_key, current_provider)
                            st.session_state.api_key = new_key
                            st.session_state.show_update_key = False
                            st.success("✅ API key updated successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Invalid API key for {provider_info.get('name', current_provider)}")
                else:
                    st.error(f"Please enter a valid {provider_info.get('name', current_provider)} API key (should start with '{prefix}')")
else:
    # No API key configured
    st.warning("⚠️ No API Key configured")
    st.markdown(f"""
    To use Autodidact with {provider_info.get('name', current_provider)}, you need an API key. This allows the app to:
    - Generate clarifying questions
    - Conduct research on topics  
    - Power the AI tutor conversations
    """)
    
    # API key input
    api_key = st.text_input(
        f"Enter your {provider_info.get('name', current_provider)} API key:",
        type="password",
        placeholder=provider_info.get('api_key_prefix', 'sk-') + "...",
        help="Your API key will be stored in ~/.autodidact/.env.json"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save API Key", type="primary", use_container_width=True, disabled=not api_key):
            prefix = provider_info.get('api_key_prefix', 'sk-')
            if api_key and api_key.startswith(prefix):
                with st.spinner("Validating API key..."):
                    if validate_api_key(api_key, current_provider):
                        # Save it
                        save_api_key(api_key, current_provider)
                        st.session_state.api_key = api_key
                        st.success("✅ API key saved successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Invalid API key for {provider_info.get('name', current_provider)}")
            else:
                st.error(f"Please enter a valid {provider_info.get('name', current_provider)} API key (should start with '{prefix}')")
    
    with col2:
        st.link_button(
            "🔗 Get API Key",
            provider_info.get('signup_url', '#'),
            help=f"Create an API key on {provider_info.get('name', current_provider)}'s website",
            use_container_width=True
        )
    
    with col3:
        st.link_button(
            "📖 Pricing Info",
            provider_info.get('pricing_url', '#'),
            help=f"View {provider_info.get('name', current_provider)}'s pricing details",
            use_container_width=True
        )

st.markdown("---")

# Tavily API Key section (for image search and research features)
st.markdown("## 🔍 Tavily API Key (Optional)")
st.markdown("Tavily powers image search and enhanced research features. This is optional - the app works without it.")

# Check current Tavily API key status
current_tavily_key = load_tavily_api_key()

if current_tavily_key:
    # Tavily API key is configured
    st.success("✅ Tavily API Key is configured")
    
    # Show masked key
    masked_key = current_tavily_key[:7] + "..." + current_tavily_key[-4:]
    st.code(masked_key)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Update Tavily Key", use_container_width=True):
            st.session_state.show_update_tavily_key = True
    
    with col2:
        if st.button("🗑️ Remove Tavily Key", type="secondary", use_container_width=True):
            from utils.config import load_config, save_config
            config = load_config()
            if "tavily_api_key" in config:
                del config["tavily_api_key"]
                save_config(config)
            st.success("Tavily API key removed successfully!")
            st.rerun()
    
    # Update key form
    if st.session_state.get('show_update_tavily_key', False):
        with st.form("update_tavily_api_key"):
            st.markdown("### Update Tavily API Key")
            new_tavily_key = st.text_input(
                "New Tavily API Key:",
                type="password",
                placeholder="tvly-...",
                help="Enter your new Tavily API key"
            )
            
            if st.form_submit_button("Save New Tavily Key", type="primary"):
                if new_tavily_key and new_tavily_key.startswith('tvly-'):
                    save_tavily_api_key(new_tavily_key)
                    st.session_state.show_update_tavily_key = False
                    st.success("✅ Tavily API key updated successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a valid Tavily API key (should start with 'tvly-')")
else:
    # No Tavily API key configured
    st.info("ℹ️ No Tavily API Key configured")
    st.markdown("""
    Tavily enhances Autodidact with:
    - 🖼️ Educational image search for visual learning
    - 🔍 Enhanced research capabilities
    - 📊 Better content discovery
    
    **This is optional** - the core tutoring features work without it.
    """)
    
    # Tavily API key input
    tavily_api_key = st.text_input(
        "Enter your Tavily API key (optional):",
        type="password",
        placeholder="tvly-...",
        help="Your Tavily API key will be stored securely in ~/.autodidact/.env.json"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Tavily Key", type="secondary", use_container_width=True, disabled=not tavily_api_key):
            if tavily_api_key and tavily_api_key.startswith('tvly-'):
                save_tavily_api_key(tavily_api_key)
                st.success("✅ Tavily API key saved successfully!")
                st.rerun()
            else:
                st.error("Please enter a valid Tavily API key (should start with 'tvly-')")
    
    with col2:
        st.link_button(
            "🔗 Get Tavily Key",
            "https://tavily.com",
            help="Create a Tavily API key on their website",
            use_container_width=True
        )
    
    with col3:
        st.link_button(
            "📖 Tavily Pricing",
            "https://tavily.com/pricing",
            help="View Tavily's pricing details",
            use_container_width=True
        )

st.markdown("---")

# Storage location section
st.markdown("---")
st.markdown("## 📁 Data Storage")

config_dir = Path.home() / ".autodidact"
st.info(f"**Configuration directory:** `{config_dir}`")

if config_dir.exists():
    # Calculate directory size
    total_size = sum(f.stat().st_size for f in config_dir.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    
    st.markdown(f"**Total size:** {size_mb:.1f} MB")
    
    # Show subdirectories
    with st.expander("View storage details"):
        st.markdown("**Directory structure:**")
        st.code(f"""
{config_dir}/
├── .env.json          # API key storage
├── autodidact.db      # Project database
└── projects/          # Project files
    └── [project-id]/
        ├── report.md
        ├── graph.json
        └── deep_research_response.json
        """)

# About section
st.markdown("---")
st.markdown("## ℹ️ About Autodidact")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Version
    **v0.1** - Topic Mode
    
    ### Features
    - 🔍 Deep Research on any topic
    - 📊 Visual knowledge graphs
    - 👨‍🏫 AI-powered tutoring
    - 📈 Progress tracking
    """)

with col2:
    st.markdown("""
    ### Privacy
    - ✅ Runs entirely locally
    - ✅ Data never leaves your computer
    - ✅ API key stored securely
    - ✅ Open source
    """)

# Help section
st.markdown("---")
st.markdown("## 🆘 Need Help?")

with st.expander("Frequently Asked Questions"):
    st.markdown(f"""
    **Q: How much does it cost to use Autodidact?**
    
    A: Autodidact itself is free. You only pay for API usage to your chosen provider:
    - **OpenAI**: $0.01-0.02 for topic clarification, $0.50-2.00 for deep research, $0.02-0.05 per tutoring session
    - **OpenRouter**: Varies by model, typically $0.001-0.05 per request depending on the model chosen
    
    **Q: Where is my data stored?**
    
    A: All data is stored locally in `~/.autodidact/` on your computer. Nothing is sent to any servers except your API calls to your chosen provider.
    
    **Q: What's the difference between providers?**
    
    A: 
    - **OpenAI**: Access to GPT models and deep research capabilities with web search
    - **OpenRouter**: Access to multiple AI models (Claude, Gemini, etc.) but no deep research mode
    
    **Q: Can I switch between providers?**
    
    A: Yes! You can configure API keys for multiple providers and switch between them in Settings.
    
    **Q: How do I report bugs or request features?**
    
    A: Please visit our GitHub repository to open issues or contribute to the project.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.9rem;'>
    Made with ❤️ for autodidacts everywhere
</div>
""", unsafe_allow_html=True)