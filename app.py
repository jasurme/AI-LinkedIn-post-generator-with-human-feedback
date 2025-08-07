import streamlit as st
import uuid
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os
import time

# Page configuration
st.set_page_config(
    page_title="AI LinkedIn Post Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #0077B5;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .post-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 2rem;
        border-left: 5px solid #0077B5;
        margin: 1rem 0;
    }
    
    .feedback-container {
        background: #fff3cd;
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    
    .success-container {
        background: #d1edff;
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 4px solid #0077B5;
        margin: 1rem 0;
    }
    
    .feedback-item {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #0077B5 0%, #005885 100%);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 5px 15px rgba(0,119,181,0.4);
        transform: translateY(-2px);
    }
    
    @media (max-width: 768px) {
        /* Only hide the quick topics section on mobile, not feedback */
        .quick-topics-mobile-hide {
            display: none !important;
        }
    }
    
    @media (min-width: 769px) {
        .main-content {
            display: flex;
            gap: 2rem;
        }
    }
    
    .copy-area {
        border: 2px dashed #0077B5 !important;
        border-radius: 10px !important;
        background-color: #f0f8ff !important;
    }
</style>
""", unsafe_allow_html=True)

class LinkedInPostGenerator:
    def __init__(self):
        if not st.secrets.get("OPENAI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            st.error("⚠️ OpenAI API key not found! Please add it to your Streamlit secrets.")
            st.stop()
        
        api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=api_key)
        
        # Initialize session state
        if 'generated_posts' not in st.session_state:
            st.session_state.generated_posts = []
        if 'all_feedbacks' not in st.session_state:
            st.session_state.all_feedbacks = []
        if 'current_post' not in st.session_state:
            st.session_state.current_post = ""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        if 'iteration_count' not in st.session_state:
            st.session_state.iteration_count = 0
    
    def generate_post(self, topic: str, all_feedback: List[str] = None) -> str:
        """Generate LinkedIn post with accumulated feedback"""
        if all_feedback is None:
            all_feedback = []
        
        feedback_text = "\n".join(all_feedback) if all_feedback else "No previous feedback"
        
        prompt = f"""
        LinkedIn topic: {topic}
        Previous human feedback: {feedback_text}
        
        Generate a professional, engaging LinkedIn post based on the given topic.
        Consider ALL previous human feedback to refine and improve the response.
        
        Make it:
        - Professional yet conversational
        - Include relevant hashtags
        - Have a clear call-to-action
        - Be engaging and valuable to the LinkedIn audience
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are an expert LinkedIn content writer with 10+ years of experience creating viral, engaging posts that drive meaningful professional conversations."),
            HumanMessage(content=prompt)
        ])
        
        return response.content
    
    def render_sidebar(self):
        """Render sidebar with instructions and tips"""
        with st.sidebar:
            st.markdown("### 💡 Feedback Tips")
            st.markdown("""
            **Good feedback examples:**
            - "Make it more conversational"
            - "Add more industry-specific examples"
            - "Include a stronger call-to-action"
            - "Make it shorter and punchier"
            - "Add more emotional appeal"
            """)
            
            st.markdown("### 📊 Session Stats")
            st.metric("Posts Generated", len(st.session_state.generated_posts))
            st.metric("Feedback Given", len(st.session_state.all_feedbacks))
            st.metric("Current Iteration", st.session_state.iteration_count)
            
            if st.button("🔄 Reset Session", key="reset"):
                for key in ['generated_posts', 'all_feedbacks', 'current_post', 'iteration_count']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    def render_main_interface(self):
        """Render main application interface"""
        st.markdown('<h1 class="main-header">🚀 AI LinkedIn Post Generator</h1>', unsafe_allow_html=True)
        
        # Topic input section
        st.markdown("### 📝 What would you like to write about?")
        
        # Only show quick topics if no post has been generated yet
        if not st.session_state.current_post:
            # Desktop layout: Show quick topics on main area
            topic_col, quick_topics_col = st.columns([3, 1])
            
            with topic_col:
                # Check for quick topic selection
                if 'quick_topic' in st.session_state:
                    topic = st.text_area(
                        "Enter your LinkedIn topic or idea:",
                        value=st.session_state.quick_topic,
                        height=100,
                        help="Describe what you want your LinkedIn post to be about. Be as specific as possible!"
                    )
                    del st.session_state.quick_topic  # Clear after use
                else:
                    topic = st.text_area(
                        "Enter your LinkedIn topic or idea:",
                        placeholder="e.g., The importance of continuous learning in tech careers...",
                        height=100,
                        help="Describe what you want your LinkedIn post to be about. Be as specific as possible!"
                    )
            
            # Quick topics only on desktop and only when no post generated
            with quick_topics_col:
                st.markdown('<div class="quick-topics-mobile-hide">', unsafe_allow_html=True)
                st.markdown("### 🎯 Quick Topics")
                if st.button("💼 Career Growth", key="career"):
                    st.session_state.quick_topic = "Career growth strategies for young professionals in tech"
                    st.rerun()
                if st.button("🤝 Networking", key="networking"):
                    st.session_state.quick_topic = "The power of authentic networking in building meaningful professional relationships"
                    st.rerun()
                if st.button("🧠 Learning", key="learning"):
                    st.session_state.quick_topic = "Why continuous learning is essential in today's fast-changing workplace"
                    st.rerun()
                if st.button("🚀 Innovation", key="innovation"):
                    st.session_state.quick_topic = "How to foster innovation and creativity in remote work environments"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # When post exists, show only topic input (full width)
            # Check for quick topic selection
            if 'quick_topic' in st.session_state:
                topic = st.text_area(
                    "Enter your LinkedIn topic or idea:",
                    value=st.session_state.quick_topic,
                    height=100,
                    help="Describe what you want your LinkedIn post to be about. Be as specific as possible!"
                )
                del st.session_state.quick_topic  # Clear after use
            else:
                topic = st.text_area(
                    "Enter your LinkedIn topic or idea:",
                    placeholder="e.g., The importance of continuous learning in tech careers...",
                    height=100,
                    help="Describe what you want your LinkedIn post to be about. Be as specific as possible!"
                )
        
        # Generate initial post
        if st.button("✨ Generate Post", type="primary", disabled=not topic):
            if topic.strip():
                with st.spinner("🤖 AI is crafting your LinkedIn post..."):
                    try:
                        post = self.generate_post(topic, st.session_state.all_feedbacks)
                        st.session_state.current_post = post
                        st.session_state.generated_posts.append({
                            'iteration': st.session_state.iteration_count + 1,
                            'post': post,
                            'topic': topic
                        })
                        st.session_state.iteration_count += 1
                        st.success("✅ Post generated successfully!")
                        time.sleep(0.5)  # Brief pause for UX
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error generating post: {str(e)}")
            else:
                st.warning("⚠️ Please enter a topic first!")
        
        # Layout: Always show both sections, CSS handles responsive behavior  
        if st.session_state.current_post:
            # Desktop: two columns, Mobile: stacked (handled by CSS)
            post_col, feedback_col = st.columns([1, 1])
            
            with post_col:
                self.render_current_post()
                self.render_post_history()
            
            with feedback_col:
                self.render_feedback_section()
    
    def render_current_post(self):
        """Render the current generated post"""
        st.markdown("### 📄 Your Generated Post")
        st.markdown(f'<div class="post-container">{st.session_state.current_post}</div>', unsafe_allow_html=True)
        
        # Copy functionality
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Simple copy button with feedback
            if st.button("📋 Copy Post", key=f"copy_btn_{st.session_state.iteration_count}"):
                # Show success message
                st.success("✅ Copied! Text is ready to paste")
                
                # Display text in copyable format
                st.text_area(
                    "Select all (Ctrl+A) and copy (Ctrl+C):",
                    value=st.session_state.current_post,
                    height=100,
                    key=f"copy_text_{st.session_state.iteration_count}"
                )
        
        with col2:
            st.metric("Character Count", len(st.session_state.current_post))
    
    def render_feedback_section(self):
        """Render feedback input and processing section"""
        st.markdown("### 💬 Provide Feedback to Improve")
        
        # Show current feedback count
        if st.session_state.all_feedbacks:
            st.info(f"📊 You've provided {len(st.session_state.all_feedbacks)} feedback(s) so far. Each one helps improve the next iteration!")
        
        # Only text area for feedback - no quick feedback buttons
        feedback = st.text_area(
            "What would you like to improve?",
            placeholder="e.g., Make it more engaging, add specific examples, shorten the length, include more hashtags...",
            height=120,
            help="Be specific about what you'd like to change. The AI will consider all your previous feedback too!"
        )
        
        # Process feedback
        if st.button("🔄 Regenerate with Feedback", type="primary", disabled=not feedback):
            if feedback.strip():
                with st.spinner("🧠 AI is incorporating your feedback..."):
                    try:
                        # Add feedback to accumulated list
                        st.session_state.all_feedbacks.append(feedback.strip())
                        
                        # Get current topic from last generation
                        current_topic = st.session_state.generated_posts[-1]['topic'] if st.session_state.generated_posts else "LinkedIn post"
                        
                        # Generate new post with all feedback
                        new_post = self.generate_post(current_topic, st.session_state.all_feedbacks)
                        st.session_state.current_post = new_post
                        st.session_state.generated_posts.append({
                            'iteration': st.session_state.iteration_count + 1,
                            'post': new_post,
                            'topic': current_topic,
                            'feedback': feedback.strip()
                        })
                        st.session_state.iteration_count += 1
                        
                        st.success(f"✅ Post updated! (Iteration #{st.session_state.iteration_count})")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error processing feedback: {str(e)}")
            else:
                st.warning("⚠️ Please provide feedback first!")
        
        # Show accumulated feedback
        if st.session_state.all_feedbacks:
            st.markdown("### 📝 All Your Feedback")
            for i, fb in enumerate(st.session_state.all_feedbacks, 1):
                st.markdown(f'<div class="feedback-item"><strong>Feedback {i}:</strong> {fb}</div>', unsafe_allow_html=True)
    
    def render_post_history(self):
        """Render post generation history"""
        if len(st.session_state.generated_posts) > 1:
            st.markdown("### 📚 Post Evolution History")
            
            # Show evolution in expandable sections
            for i, post_data in enumerate(reversed(st.session_state.generated_posts)):
                with st.expander(f"📄 Version {post_data['iteration']} {('(Current)' if i == 0 else '')}"):
                    if 'feedback' in post_data:
                        st.markdown(f"**💬 Feedback applied:** {post_data['feedback']}")
                    st.markdown(f"**📝 Post:**")
                    st.markdown(post_data['post'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Character Count", len(post_data['post']))
                    with col2:
                        if st.button(f"🔄 Revert to Version {post_data['iteration']}", key=f"revert_{post_data['iteration']}"):
                            st.session_state.current_post = post_data['post']
                            st.rerun()
    
    def run(self):
        """Run the complete Streamlit application"""
        self.render_sidebar()
        self.render_main_interface()

# Initialize and run the app
if __name__ == "__main__":
    app = LinkedInPostGenerator()
    app.run()
