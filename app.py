import streamlit as st
import uuid
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

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
</style>
        # Custom CSS for better styling and mobile responsiveness
        st.markdown("""
        <style>
        /* Hide quick topics on mobile */
        @media (max-width: 768px) {
            .stColumn:nth-child(2) {
                display: none !important;
            }
        }
        
        /* Copy area styling */
        .copy-area {
            border: 2px dashed #0077B5 !important;
            border-radius: 10px !important;
            background-color: #f0f8ff !important;
        }
        
        /* Mobile responsive layout */
        @media (max-width: 768px) {
            .main-content {
                flex-direction: column;
            }
        }
        
        /* Desktop layout */
        @media (min-width: 769px) {
            .main-content {
                display: flex;
                gap: 2rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)

class LinkedInPostGenerator:
    def __init__(self):
        if not os.getenv("OPENAI_API_KEY"):
            st.error("⚠️ OpenAI API key not found! Please add it to your .env file or Streamlit secrets.")
            st.stop()
        
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        
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
            
            # Quick topics on mobile (hide on desktop)
            if st.session_state.get('is_mobile', False):
                st.markdown("### 🎯 Quick Topics")
                if st.button("💼 Career Growth", key="career_mobile"):
                    st.session_state.quick_topic = "Career growth strategies for young professionals in tech"
                if st.button("🤝 Networking", key="networking_mobile"):
                    st.session_state.quick_topic = "The power of authentic networking in building meaningful professional relationships"
                if st.button("🧠 Learning", key="learning_mobile"):
                    st.session_state.quick_topic = "Why continuous learning is essential in today's fast-changing workplace"
                if st.button("🚀 Innovation", key="innovation_mobile"):
                    st.session_state.quick_topic = "How to foster innovation and creativity in remote work environments"
            
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
        
        # Detect mobile (simple check based on viewport)
        if 'is_mobile' not in st.session_state:
            st.session_state.is_mobile = False
        
        # Topic input section
        st.markdown("### 📝 What would you like to write about?")
        
        # Desktop layout: Show quick topics on main area
        # Mobile layout: Hide quick topics from main area (moved to sidebar)
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
        
        # Quick topics only on desktop
        with quick_topics_col:
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
        
        # Layout: Desktop (post on right, feedback on left) vs Mobile (stacked)
        if st.session_state.current_post:
            # Desktop layout - two columns
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
        
        # Copy functionality using streamlit-clipboard (fallback to text_area)
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Create a text area that's easy to copy from
            st.text_area(
                "👆 Select all and copy (Ctrl+C / Cmd+C):",
                value=st.session_state.current_post,
                height=100,
                key=f"copy_area_{st.session_state.iteration_count}",
                help="Click in the box above, press Ctrl+A (or Cmd+A) to select all, then Ctrl+C (or Cmd+C) to copy!"
            )
        
        with col2:
            st.metric("Character Count", len(st.session_state.current_post))
    
    def render_feedback_section(self):
        """Render feedback input and processing section"""
        st.markdown("### 💬 Provide Feedback to Improve")
        
        # Show current feedback count
        if st.session_state.all_feedbacks:
            st.info(f"📊 You've provided {len(st.session_state.all_feedbacks)} feedback(s) so far. Each one helps improve the next iteration!")
        
        feedback_col1, feedback_col2 = st.columns([3, 1])
        
        with feedback_col1:
            feedback = st.text_area(
                "What would you like to improve?",
                placeholder="e.g., Make it more engaging, add specific examples, shorten the length, include more hashtags...",
                height=120,
                help="Be specific about what you'd like to change. The AI will consider all your previous feedback too!"
            )
        
        with feedback_col2:
            st.markdown("### 🎨 Quick Feedback")
            if st.button("🎯 More engaging", key="engaging"):
                feedback = "Make the post more engaging and captivating for the LinkedIn audience"
            if st.button("📏 Make shorter", key="shorter"):
                feedback = "Make the post shorter and more concise while keeping the key message"
            if st.button("💼 More professional", key="professional"):
                feedback = "Make the tone more professional and business-appropriate"
            if st.button("#️⃣ Add hashtags", key="hashtags"):
                feedback = "Add more relevant hashtags to increase visibility"
        
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
