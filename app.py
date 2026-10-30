import os
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

from services.resume_parser import extract_text_from_pdf_stream, analyze_resume_profile
from services.post_generator import generate_post, refine_post, POST_STYLES
from services.linkedin_service import publish_linkedin_post, verify_linkedin_token
from services.whatsapp_service import send_whatsapp_preview
from services.storage_service import save_profile, load_profile, add_post_to_history, load_history

# ==========================================
# Page Configuration & Mobile-Friendly CSS
# ==========================================
st.set_page_config(
    page_title="LinkedIn AutoBrand AI",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Mobile CSS for smooth mobile experience
st.markdown("""
<style>
    /* Responsive container tweaks */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    /* Touch friendly big buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.2rem;
        font-size: 1.05rem;
        font-weight: 600;
        margin-top: 0.3rem;
        margin-bottom: 0.3rem;
    }
    /* LinkedIn Post Card Preview */
    .linkedin-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 14px;
        padding: 16px;
        color: #1e1e1e;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.5;
        white-space: pre-wrap;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .linkedin-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 10px;
    }
    .badge {
        background-color: #0077b5;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "current_draft" not in st.session_state:
    st.session_state.current_draft = ""
if "profile_data" not in st.session_state:
    st.session_state.profile_data = load_profile()

# ==========================================
# Sidebar: Settings & API Credentials
# ==========================================
with st.sidebar:
    st.title("⚙️ API Configuration")
    st.caption("Aap ye keys yahan bhi dal sakte hain ya `.env` file me.")

    st.subheader("1. Google Gemini AI")
    gemini_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")

    st.subheader("2. LinkedIn API")
    linkedin_token = st.text_input("Access Token", value=os.getenv("LINKEDIN_ACCESS_TOKEN", ""), type="password")
    linkedin_urn = st.text_input("Person URN (e.g. urn:li:person:XXXX)", value=os.getenv("LINKEDIN_PERSON_URN", ""))

    if st.button("🔍 Test LinkedIn Connection"):
        with st.spinner("Checking token..."):
            res = verify_linkedin_token(linkedin_token)
            if res.get("valid"):
                st.success(f"Connected as: {res.get('name')}")
            else:
                st.error(f"Failed: {res.get('error')}")

    st.subheader("3. WhatsApp (Twilio)")
    twilio_sid = st.text_input("Twilio Account SID", value=os.getenv("TWILIO_ACCOUNT_SID", ""))
    twilio_token = st.text_input("Twilio Auth Token", value=os.getenv("TWILIO_AUTH_TOKEN", ""), type="password")
    twilio_from = st.text_input("Twilio WhatsApp Number", value=os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886"))
    user_phone = st.text_input("Your WhatsApp Number", value=os.getenv("USER_WHATSAPP_NUMBER", "whatsapp:+91"), help="Include country code, e.g. whatsapp:+919876543210")

# ==========================================
# Header
# ==========================================
st.title("💼 AutoBrand LinkedIn Bot")
st.caption("AI-Powered Resume to Daily LinkedIn Posts with WhatsApp Review & Approval")

# ==========================================
# Main Tabs (Mobile-Friendly Navigation)
# ==========================================
tab_post, tab_resume, tab_whatsapp, tab_history = st.tabs([
    "✍️ Create & Refine",
    "📄 Resume Profile",
    "📱 WhatsApp Review",
    "📜 History"
])

# -----------------------------------------------------------------------------
# TAB 1: CREATE, REFINE & POST
# -----------------------------------------------------------------------------
with tab_post:
    profile = st.session_state.profile_data
    if not profile:
        st.info("💡 Sabse pehle **'Resume Profile'** tab me jakar apna resume (PDF) upload karein!")
    else:
        st.markdown("### 🎯 Content Options")
        col1, col2 = st.columns(2)
        with col1:
            selected_style = st.selectbox("Style / Format", POST_STYLES, index=0)
        with col2:
            include_code = st.checkbox("Include Code Snippet", value=False)

        custom_topic = st.text_input("Specific Topic / Skill (Optional)", placeholder="e.g. Python AsyncIO, React Hooks, System Design...")

        if st.button("✨ Generate Fresh Post with AI", type="primary"):
            with st.spinner("AI aapke resume ke basis par post likh raha hai..."):
                try:
                    post = generate_post(
                        profile_analysis=profile["analysis"],
                        topic_focus=custom_topic if custom_topic.strip() else None,
                        style=selected_style,
                        include_code=include_code,
                        api_key=gemini_key
                    )
                    st.session_state.current_draft = post
                    st.success("Naya post draft taiyar hai!")
                except Exception as e:
                    st.error(f"Error: {e}")

        # Post Display & Editing
        if st.session_state.current_draft:
            st.markdown("---")
            st.markdown("### 👁️ Live LinkedIn Preview")
            
            # Simulated LinkedIn Card
            st.markdown(f"""
            <div class="linkedin-card">
                <div class="linkedin-header">
                    <div>
                        <strong>Your Name</strong> <span class="badge">Preview</span><br>
                        <small style="color: #666;">Just now • 🌐 Public</small>
                    </div>
                </div>
                {st.session_state.current_draft}
            </div>
            """, unsafe_allow_html=True)

            # Editable Text Area
            edited_text = st.text_area("📝 Edit Text Manually (agar khud koi word badalna ho):", 
                                       value=st.session_state.current_draft, 
                                       height=220)
            st.session_state.current_draft = edited_text

            # ==============================================================
            # User Feedback / AI Modification (Code / Image / Tone changes)
            # ==============================================================
            with st.expander("🛠️ AI se post me changes karwayein (Refine with AI)", expanded=False):
                st.caption("Aap yahan bata sakte hain ki post me kya change chahiye, jaise: 'Python code snippet add karo', 'Tone thoda funny karo', 'Isse short karo', etc.")
                feedback_prompt = st.text_input("Aapko kya change chahiye?", placeholder="e.g. Add 5 lines of Python code, make it more beginner friendly")
                if st.button("🔄 Apply Changes to Post"):
                    if not feedback_prompt.strip():
                        st.warning("Pehle changes likhein!")
                    else:
                        with st.spinner("AI changes apply kar raha hai..."):
                            try:
                                updated = refine_post(st.session_state.current_draft, feedback_prompt, api_key=gemini_key)
                                st.session_state.current_draft = updated
                                st.success("Post successfully update ho gaya!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating post: {e}")

            st.markdown("---")
            
            # Action Buttons
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if st.button("📱 Send to WhatsApp", help="Aapke phone par preview bhejega"):
                    with st.spinner("WhatsApp par message bheja ja raha hai..."):
                        res = send_whatsapp_preview(
                            post_text=st.session_state.current_draft,
                            account_sid=twilio_sid,
                            auth_token=twilio_token,
                            from_whatsapp=twilio_from,
                            to_whatsapp=user_phone
                        )
                        if res.get("success"):
                            st.success("✅ WhatsApp par preview bhej diya gaya!")
                        else:
                            st.error(f"WhatsApp Error: {res.get('error')}")

            with btn_col2:
                if st.button("🚀 Post Now to LinkedIn", type="primary"):
                    with st.spinner("LinkedIn par publish ho raha hai..."):
                        res = publish_linkedin_post(
                            post_text=st.session_state.current_draft,
                            token=linkedin_token,
                            urn=linkedin_urn
                        )
                        if res.get("success"):
                            st.balloons()
                            st.success("🎉 LinkedIn par successfully post ho gaya!")
                            add_post_to_history(st.session_state.current_draft, "PUBLISHED", res.get("post_id", ""))
                        else:
                            st.error(f"LinkedIn Error: {res.get('error')}")

# -----------------------------------------------------------------------------
# TAB 2: RESUME PROFILE
# -----------------------------------------------------------------------------
with tab_resume:
    st.subheader("📄 Upload Resume (PDF)")
    st.caption("Aapka resume extract karke AI aapke skills aur domains ka analysis save karega.")

    uploaded_file = st.file_uploader("Apna Resume yahan drop karein (PDF)", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("⚡ Extract & Save Profile", type="primary"):
            with st.spinner("PDF read aur AI analysis ho raha hai..."):
                try:
                    raw_text = extract_text_from_pdf_stream(uploaded_file)
                    profile_res = analyze_resume_profile(raw_text, api_key=gemini_key)
                    
                    # Save to local storage
                    save_profile(profile_res)
                    st.session_state.profile_data = profile_res
                    st.success("✅ Resume analysis complete aur save ho gaya!")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Display Saved Profile
    if st.session_state.profile_data:
        st.markdown("---")
        st.markdown("### 🧠 Saved Skills & Content Pillars")
        st.markdown(st.session_state.profile_data.get("analysis", "No analysis found."))
        
        if st.button("🗑️ Clear / Reset Saved Profile"):
            from services.storage_service import PROFILE_FILE
            if os.path.exists(PROFILE_FILE):
                os.remove(PROFILE_FILE)
            st.session_state.profile_data = None
            st.info("Profile reset kar di gayi hai.")
            st.rerun()

# -----------------------------------------------------------------------------
# TAB 3: WHATSAPP REVIEW & CLOUD SETUP
# -----------------------------------------------------------------------------
with tab_whatsapp:
    st.subheader("📱 WhatsApp Approval & Automation")
    st.markdown("""
    Aap chahein toh **GitHub Actions** ya **Local Schedule** ke zariye har din ek fix time par automated flow chala sakte hain:
    
    1. **Scheduled Run:** Rozana subah bot aapke resume ke skills se ek fresh post banayega.
    2. **WhatsApp Preview:** Bot turant aapke WhatsApp number par draft bhejega.
    3. **Mobile Approval:** Aap apne phone se WhatsApp message check karke Streamlit dashboard me 1-click se **Approve (Post)** ya **AI Changes** kar sakte hain!
    """)
    
    st.markdown("---")
    st.markdown("### 🧪 Test WhatsApp Connection")
    test_msg = st.text_input("Test message", value="Hello! Twilio WhatsApp bot connection working perfectly 🚀")
    if st.button("Send Test WhatsApp"):
        with st.spinner("Sending test ping..."):
            res = send_whatsapp_preview(
                post_text=test_msg,
                account_sid=twilio_sid,
                auth_token=twilio_token,
                from_whatsapp=twilio_from,
                to_whatsapp=user_phone
            )
            if res.get("success"):
                st.success("✅ Test message aapke WhatsApp par bhej diya gaya!")
            else:
                st.error(f"Failed: {res.get('error')}")

# -----------------------------------------------------------------------------
# TAB 4: HISTORY
# -----------------------------------------------------------------------------
with tab_history:
    st.subheader("📜 Recent Post History")
    history = load_history()
    if not history:
        st.info("Abhi tak koi post history nahi hai.")
    else:
        for idx, item in enumerate(history):
            with st.expander(f"📌 {item.get('timestamp')} - {item.get('status')}"):
                st.text(item.get("content"))
                if item.get("post_id"):
                    st.caption(f"LinkedIn ID: {item.get('post_id')}")
