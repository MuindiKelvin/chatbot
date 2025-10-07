import streamlit as st
import requests
from datetime import datetime
import json
import re

# Page configuration
st.set_page_config(
    page_title="AI Search Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for Claude-like interface with full responsiveness
st.markdown("""
<style>
    /* Base styles */
    .main {
        background: #f8f9fa;
        padding: 1rem;
    }
    
    /* Responsive container */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        .block-container {
            padding: 1rem 0.5rem !important;
        }
    }
    
    /* Chat message styling with better differentiation */
    .stChatMessage {
        border-radius: 12px;
        padding: 18px;
        margin: 12px 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        border: 1px solid #e5e7eb;
        transition: all 0.2s;
    }
    
    /* User messages - distinct blue theme */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-left: 4px solid #4f46e5;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .stChatMessage[data-testid="user-message"] * {
        color: white !important;
    }
    
    /* Assistant messages - clean white with accent */
    .stChatMessage[data-testid="assistant-message"] {
        background: white;
        color: #1f2937 !important;
        border-left: 4px solid #10b981;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    .stChatMessage[data-testid="assistant-message"] * {
        color: #1f2937 !important;
    }
    
    /* Mobile responsiveness for chat messages */
    @media (max-width: 768px) {
        .stChatMessage {
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
        }
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        padding: 12px 16px;
        font-size: 15px;
        transition: all 0.2s;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4f46e5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }
    
    @media (max-width: 768px) {
        .stTextInput > div > div > input {
            font-size: 14px;
            padding: 10px 12px;
        }
    }
    
    /* Header styles */
    h1 {
        color: #1f2937;
        font-weight: 600;
        margin-bottom: 8px;
        font-size: 2.5rem;
    }
    
    @media (max-width: 768px) {
        h1 {
            font-size: 1.8rem;
        }
    }
    
    @media (max-width: 480px) {
        h1 {
            font-size: 1.5rem;
        }
    }
    
    .subtitle {
        color: #6b7280;
        font-size: 16px;
        margin-bottom: 30px;
    }
    
    @media (max-width: 768px) {
        .subtitle {
            font-size: 14px;
            margin-bottom: 20px;
        }
    }
    
    /* Badge styles */
    .search-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        display: inline-block;
        margin: 8px 4px 0 0;
        font-weight: 500;
    }
    
    .image-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        display: inline-block;
        margin: 8px 4px 0 0;
        font-weight: 500;
    }
    
    .ai-badge {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        display: inline-block;
        margin: 8px 4px 0 0;
        font-weight: 500;
    }
    
    @media (max-width: 480px) {
        .search-badge, .image-badge, .ai-badge {
            padding: 4px 10px;
            font-size: 0.75em;
        }
    }
    
    /* Result card styling */
    .result-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 16px;
        margin: 12px 0;
        transition: all 0.2s;
    }
    
    .result-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #4f46e5;
        transform: translateY(-2px);
    }
    
    @media (max-width: 768px) {
        .result-card {
            padding: 12px;
            margin: 8px 0;
        }
    }
    
    .result-title {
        color: #1f2937;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 8px;
        line-height: 1.4;
    }
    
    .result-snippet {
        color: #4b5563;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 8px;
    }
    
    .result-link {
        color: #4f46e5;
        font-size: 13px;
        text-decoration: none;
        word-break: break-all;
    }
    
    @media (max-width: 768px) {
        .result-title {
            font-size: 15px;
        }
        .result-snippet {
            font-size: 13px;
        }
        .result-link {
            font-size: 12px;
        }
    }
    
    /* Image grid - fully responsive */
    .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 12px;
        margin: 16px 0;
    }
    
    @media (max-width: 1024px) {
        .image-grid {
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
        }
    }
    
    @media (max-width: 768px) {
        .image-grid {
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 8px;
        }
    }
    
    @media (max-width: 480px) {
        .image-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 6px;
        }
    }
    
    .image-item {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
        transition: all 0.2s;
        background: white;
    }
    
    .image-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .image-item img {
        width: 100%;
        height: 150px;
        object-fit: cover;
    }
    
    @media (max-width: 768px) {
        .image-item img {
            height: 120px;
        }
    }
    
    @media (max-width: 480px) {
        .image-item img {
            height: 100px;
        }
    }
    
    /* Quick button styling */
    .quick-btn {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px;
        transition: all 0.2s;
        cursor: pointer;
    }
    
    .quick-btn:hover {
        border-color: #4f46e5;
        background: #f0f4ff;
    }
    
    @media (max-width: 768px) {
        .quick-btn {
            padding: 10px 12px;
            font-size: 14px;
        }
    }
    
    /* Stats card */
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 16px;
        margin: 10px 0;
    }
    
    @media (max-width: 768px) {
        .stats-card {
            padding: 12px;
        }
    }
    
    /* Sidebar responsiveness */
    @media (max-width: 768px) {
        .css-1d391kg {
            padding: 1rem 0.5rem;
        }
    }
    
    /* Button responsiveness */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    
    @media (max-width: 480px) {
        .stButton > button {
            padding: 0.4rem 0.8rem;
            font-size: 14px;
        }
    }
    
    /* Radio buttons */
    .stRadio > div {
        gap: 0.5rem;
    }
    
    @media (max-width: 768px) {
        .stRadio > div {
            flex-direction: column;
        }
    }
    
    /* Metrics responsive */
    .stMetric {
        background: white;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    @media (max-width: 768px) {
        .stMetric {
            padding: 8px;
        }
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #6b7280;
        font-size: 14px;
        padding: 20px 0;
        margin-top: 40px;
        border-top: 1px solid #e5e7eb;
    }
    
    .footer a {
        color: #4f46e5;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .footer a:hover {
        color: #764ba2;
        text-decoration: underline;
    }
    
    @media (max-width: 768px) {
        .footer {
            font-size: 12px;
            padding: 15px 0;
        }
    }
    
    /* Chat input container */
    .stChatInputContainer {
        padding: 1rem 0;
    }
    
    @media (max-width: 768px) {
        .stChatInputContainer {
            padding: 0.5rem 0;
        }
    }
    
    /* Column responsiveness */
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "search_mode" not in st.session_state:
    st.session_state.search_mode = "smart"  # smart, web, images, ai

# API Configuration
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "")
SERPAPI_URL = "https://serpapi.com/search"

def detect_query_type(query):
    """Intelligently detect what type of search to perform"""
    query_lower = query.lower()
    
    # Image search indicators
    image_keywords = ['image', 'picture', 'photo', 'show me', 'visual', 'look like', 'appearance']
    if any(keyword in query_lower for keyword in image_keywords):
        return "images"
    
    # AI mode indicators (complex queries, analysis, comparisons)
    ai_keywords = ['explain', 'how does', 'why', 'compare', 'difference', 'analyze', 'what is', 'who is']
    if any(query_lower.startswith(keyword) for keyword in ai_keywords):
        return "ai"
    
    # Default to web search
    return "web"

def search_serpapi(query, search_type="web"):
    """Unified SerpAPI search function"""
    if not SERPAPI_KEY:
        return None, "Please configure SERPAPI_KEY in Streamlit secrets"
    
    params = {
        "api_key": SERPAPI_KEY,
        "q": query,
        "gl": "us",
        "hl": "en"
    }
    
    # Configure based on search type
    if search_type == "images":
        params["engine"] = "google_images"
        params["num"] = 12
    elif search_type == "ai":
        params["engine"] = "google"
        params["num"] = 8
        params["google_domain"] = "google.com"
    else:  # web
        params["engine"] = "google"
        params["num"] = 6
    
    try:
        response = requests.get(SERPAPI_URL, params=params, timeout=15)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Search error: {str(e)}"

def synthesize_ai_response(query, results):
    """Synthesize a comprehensive AI response from search results"""
    if not results:
        return "I couldn't find enough information to answer your question."
    
    # Extract relevant information
    organic_results = results.get("organic_results", [])
    answer_box = results.get("answer_box", {})
    knowledge_graph = results.get("knowledge_graph", {})
    
    response = ""
    
    # Start with direct answer if available
    if answer_box:
        if "answer" in answer_box:
            response += f"**Direct Answer:** {answer_box['answer']}\n\n"
        elif "snippet" in answer_box:
            response += f"**Quick Summary:** {answer_box['snippet']}\n\n"
    
    # Add knowledge graph info
    if knowledge_graph:
        title = knowledge_graph.get("title", "")
        description = knowledge_graph.get("description", "")
        if title and description:
            response += f"**About {title}:** {description}\n\n"
    
    # Synthesize from top results
    if organic_results:
        response += "**Detailed Information:**\n\n"
        
        # Collect snippets
        snippets = []
        for result in organic_results[:5]:
            snippet = result.get("snippet", "")
            if snippet and len(snippet) > 50:
                snippets.append(snippet)
        
        if snippets:
            # Create a comprehensive answer
            response += " ".join(snippets[:3])
            response += "\n\n"
    
    # Add source references
    response += "**Sources:**\n"
    for idx, result in enumerate(organic_results[:3], 1):
        title = result.get("title", "")
        link = result.get("link", "")
        if title and link:
            response += f"{idx}. [{title}]({link})\n"
    
    return response

def format_web_results(results):
    """Format web search results with rich cards"""
    if not results:
        return "No results found."
    
    organic_results = results.get("organic_results", [])
    if not organic_results:
        return "No results found."
    
    # Search metadata
    search_info = results.get("search_information", {})
    total_results = search_info.get("total_results", "N/A")
    
    formatted = f"**Found approximately {total_results:,} results**\n\n"
    
    # Answer box
    if "answer_box" in results:
        answer_box = results["answer_box"]
        if "answer" in answer_box:
            formatted += f"📌 **Quick Answer:** {answer_box['answer']}\n\n"
        elif "snippet" in answer_box:
            formatted += f"📌 **Featured Snippet:** {answer_box['snippet']}\n\n"
    
    # Top results as cards
    formatted += "**Top Results:**\n\n"
    for idx, item in enumerate(organic_results[:5], 1):
        title = item.get("title", "No title")
        snippet = item.get("snippet", "No description available")
        link = item.get("link", "")
        
        formatted += f"<div class='result-card'>"
        formatted += f"<div class='result-title'>{idx}. {title}</div>"
        formatted += f"<div class='result-snippet'>{snippet}</div>"
        formatted += f"<a href='{link}' target='_blank' class='result-link'>🔗 {link}</a>"
        formatted += f"</div>\n\n"
    
    return formatted

def format_image_results(results):
    """Format image search results in a grid"""
    if not results:
        return "No images found."
    
    images = results.get("images_results", [])
    if not images:
        return "No images found."
    
    formatted = f"**Found {len(images)} images**\n\n"
    
    # Create image grid using HTML
    formatted += "<div class='image-grid'>"
    for idx, img in enumerate(images[:12], 1):
        thumbnail = img.get("thumbnail", "")
        title = img.get("title", "Image")
        link = img.get("link", "")
        source = img.get("source", "")
        
        if thumbnail:
            formatted += f"""
            <div class='image-item'>
                <a href='{link}' target='_blank'>
                    <img src='{thumbnail}' alt='{title}'/>
                </a>
                <div style='padding: 8px; font-size: 12px; color: #6b7280;'>{source}</div>
            </div>
            """
    
    formatted += "</div>"
    
    return formatted

def generate_response(user_query, mode="smart"):
    """Generate intelligent response based on query and mode"""
    # Handle greetings
    greetings = ["hi", "hello", "hey", "greetings", "hi there"]
    if user_query.lower().strip() in greetings:
        return "Hello! I'm your AI Search Assistant. I can help you find information, images, and provide detailed answers using Google's search capabilities. What would you like to know?", None, "greeting"
    
    # Detect search type
    if mode == "smart":
        search_type = detect_query_type(user_query)
    else:
        search_type = mode
    
    # Perform search
    with st.spinner(f"🔍 Searching ({search_type} mode)..."):
        results, error = search_serpapi(user_query, search_type)
    
    if error:
        return f"I encountered an error while searching: {error}", None, search_type
    
    # Track search
    st.session_state.search_history.append({
        "query": user_query,
        "type": search_type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Format response based on search type
    if search_type == "ai":
        response = synthesize_ai_response(user_query, results)
    elif search_type == "images":
        response = format_image_results(results)
    else:
        response = format_web_results(results)
    
    return response, results, search_type

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🤖 AI Search Assistant")
    st.markdown("<p class='subtitle'>Intelligent search powered by Google AI, Web Search, and Image Search</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings & Stats")
    
    # Search mode selector
    st.subheader("Search Mode")
    st.session_state.search_mode = st.radio(
        "Select Mode",
        ["smart", "web", "images", "ai"],
        format_func=lambda x: {
            "smart": "🧠 Smart (Auto-detect)",
            "web": "🌐 Web Search",
            "images": "🖼️ Image Search",
            "ai": "🤖 AI Mode (Detailed)"
        }[x],
        help="Smart mode automatically detects the best search type for your query",
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # API Status
    st.subheader("API Status")
    if SERPAPI_KEY:
        st.success("✅ SerpAPI Connected")
    else:
        st.error("❌ API Key Missing")
        st.info("Add SERPAPI_KEY to Streamlit secrets")
    
    st.divider()
    
    # Statistics
    st.subheader("Statistics")
    
    total_searches = len(st.session_state.search_history)
    st.markdown(f"""
    <div class='stats-card'>
        <div style='font-size: 28px; font-weight: bold;'>{total_searches}</div>
        <div style='font-size: 14px; opacity: 0.9;'>Total Searches</div>
    </div>
    """, unsafe_allow_html=True)
    
    if total_searches > 0:
        # Search type breakdown
        search_types = {}
        for search in st.session_state.search_history:
            stype = search.get("type", "web")
            search_types[stype] = search_types.get(stype, 0) + 1
        
        st.markdown("**Search Breakdown:**")
        for stype, count in search_types.items():
            st.metric(stype.capitalize(), count)
    
    st.divider()
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.search_history = []
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)
        
        # Show search badges
        if message.get("search_type"):
            stype = message["search_type"]
            if stype == "ai":
                st.markdown("<span class='ai-badge'>🤖 AI Mode</span>", unsafe_allow_html=True)
            elif stype == "images":
                st.markdown("<span class='image-badge'>🖼️ Image Search</span>", unsafe_allow_html=True)
            elif stype == "web":
                st.markdown("<span class='search-badge'>🌐 Web Search</span>", unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask me anything... I can search the web, find images, or provide detailed AI-powered answers"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        response, search_results, search_type = generate_response(prompt, st.session_state.search_mode)
        st.markdown(response, unsafe_allow_html=True)
        
        # Add badge
        if search_type == "ai":
            st.markdown("<span class='ai-badge'>🤖 AI Mode</span>", unsafe_allow_html=True)
        elif search_type == "images":
            st.markdown("<span class='image-badge'>🖼️ Image Search</span>", unsafe_allow_html=True)
        elif search_type == "web":
            st.markdown("<span class='search-badge'>🌐 Web Search</span>", unsafe_allow_html=True)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "search_type": search_type if search_type != "greeting" else None
        })

# Quick suggestions
if not st.session_state.messages:
    st.markdown("### 💡 Try these examples:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🌐 Web Search**")
        if st.button("Latest AI developments", use_container_width=True, key="btn1"):
            query = "Latest AI developments"
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Generate response immediately
            response, search_results, search_type = generate_response(query, st.session_state.search_mode)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "search_type": search_type if search_type != "greeting" else None
            })
            st.rerun()
            
        if st.button("Python best practices 2024", use_container_width=True, key="btn2"):
            query = "Python best practices 2024"
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Generate response immediately
            response, search_results, search_type = generate_response(query, st.session_state.search_mode)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "search_type": search_type if search_type != "greeting" else None
            })
            st.rerun()
    
    with col2:
        st.markdown("**🖼️ Image Search**")
        if st.button("Show me auroras", use_container_width=True, key="btn3"):
            query = "Show me auroras"
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Generate response immediately
            response, search_results, search_type = generate_response(query, st.session_state.search_mode)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "search_type": search_type if search_type != "greeting" else None
            })
            st.rerun()
            
        if st.button("Modern office designs", use_container_width=True, key="btn4"):
            query = "Modern office designs"
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Generate response immediately
            response, search_results, search_type = generate_response(query, st.session_state.search_mode)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "search_type": search_type if search_type != "greeting" else None
            })
            st.rerun()
    
    with col3:
        st.markdown("**🤖 AI Mode**")
        if st.button("Explain quantum computing", use_container_width=True, key="btn5"):
            query = "Explain quantum computing"
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Generate response immediately
            response, search_results, search_type = generate_response(query, st.session_state.search_mode)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "search_type": search_type if search_type != "greeting" else None
            })
            st.rerun()
            
        if st.button("Compare renewable energy", use_container_width=True, key="btn6"):
            query = "Compare renewable energy sources"
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Generate response immediately
            response, search_results, search_type = generate_response(query, st.session_state.search_mode)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "search_type": search_type if search_type != "greeting" else None
            })
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div class='footer'>
    <p>Powered by <strong>SerpAPI</strong> + <strong>Google Search</strong> | Built with <strong>Streamlit</strong> | AI-Enhanced Responses</p>
    <p style='margin-top: 10px;'>
        Developed by <a href='https://muindikelvin.github.io' target='_blank'>Kelvin Muindi</a> 
        | <a href='https://github.com/muindikelvin' target='_blank'>GitHub</a>
    </p>
</div>
""", unsafe_allow_html=True)