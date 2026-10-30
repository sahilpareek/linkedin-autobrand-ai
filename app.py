import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from services.resume_parser import extract_text_from_pdf_stream, analyze_resume_profile
from services.post_generator import (
    generate_morning_ui_post,
    generate_afternoon_frontend_post,
    generate_evening_ai_post,
    generate_weekend_interactive_post,
    refine_post
)
from services.image_card_service import generate_svg_banner
from services.linkedin_service import publish_linkedin_post, verify_linkedin_token
from services.whatsapp_service import send_whatsapp_preview
from services.storage_service import save_profile, load_profile, add_post_to_history, load_history

# ==========================================
# Page Config & Mobile-First Styling
# ==========================================
st.set_page_config(
    page_title="AutoBrand 3x LinkedIn AI",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2.5rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.2rem;
        font-size: 1.05rem;
        font-weight: 600;
        margin-top: 0.3rem;
        margin-bottom: 0.3rem;
    }
    .slot-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
    }
    .linkedin-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 14px;
        padding: 16px;
        color: #1e1e1e;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        line-height: 1.5;
        white-space: pre-wrap;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .banner-preview-box {
        border-radius: 16px;
        overflow: hidden;
        margin-top: 10px;
        margin-bottom: 15px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    }
</style>
""", unsafe_allow_html=True)

# Session State
if "current_draft" not in st.session_state:
    st.session_state.current_draft = ""
if "current_topic" not in st.session_state:
    st.session_state.current_topic = ""
if "current_category" not in st.session_state:
    st.session_state.current_category = "ui_ux"
if "current_svg" not in st.session_state:
    st.session_state.current_svg = ""
if "profile_data" not in st.session_state:
    st.session_state.profile_data = load_profile()

# ==========================================
# Sidebar: Credentials & Schedule Info
# ==========================================
with st.sidebar:
    st.title("⚙️ Bot Configuration")
    
    st.subheader("1. Gemini API Key")
    gemini_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")

    st.subheader("2. LinkedIn API")
    linkedin_token = st.text_input("Access Token", value=os.getenv("LINKEDIN_ACCESS_TOKEN", ""), type="password")
    linkedin_urn = st.text_input("Person URN", value=os.getenv("LINKEDIN_PERSON_URN", ""))

    if st.button("🔍 Check LinkedIn Status"):
        res = verify_linkedin_token(linkedin_token)
        if res.get("valid"):
            st.success(f"Connected: {res.get('name')}")
        else:
            st.error(f"Error: {res.get('error')}")

    st.subheader("3. WhatsApp (Twilio)")
    twilio_sid = st.text_input("Twilio Account SID", value=os.getenv("TWILIO_ACCOUNT_SID", ""))
    twilio_token = st.text_input("Twilio Auth Token", value=os.getenv("TWILIO_AUTH_TOKEN", ""), type="password")
    twilio_from = st.text_input("Twilio WhatsApp From", value=os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886"))
    user_phone = st.text_input("Your WhatsApp Number", value=os.getenv("USER_WHATSAPP_NUMBER", "whatsapp:+91"))

# ==========================================
# Main Header
# ==========================================
st.title("🚀 LinkedIn 3x Daily AutoBrand")
st.caption("UI/UX Tricks • Frontend Hacks • AI News • Weekend Polls (Simple English & Viral Reach)")

tab_slots, tab_resume, tab_whatsapp, tab_history = st.tabs([
    "✨ Generate Post",
    "📄 Resume Profile",
    "📱 WhatsApp Review",
    "📜 History"
])

# -----------------------------------------------------------------------------
# TAB 1: 3 DAILY SLOTS & CONTENT GENERATOR
# -----------------------------------------------------------------------------
with tab_slots:
    st.markdown("### 🕒 Select Daily Traffic Slot")
    
    slot_option = st.radio(
        "Aap konsi post generate karna chahte hain?",
        [
            "🌅 1. Morning (09:00 AM IST) - UI/UX & Design Short Tricks (Figma, XD, Mobile)",
            "☀️ 2. Afternoon (01:00 PM IST) - Frontend Short Tricks (CSS, JS, React)",
            "🌙 3. Evening (07:00 PM IST) - Trending AI News & Tool Breakdown",
            "🎉 4. Weekend Special - Interactive Poll / Quiz / A vs B Challenge"
        ],
        index=0
    )

    custom_topic = st.text_input(
        "Custom Topic / Focus (Optional):", 
        placeholder="e.g. Figma auto-layout, CSS clamp trick, OpenAI model release..."
    )

    profile = st.session_state.profile_data
    profile_summary = profile.get("analysis", "") if profile else ""

    if st.button("⚡ Generate High-Traffic Post & Visual Banner", type="primary"):
        with st.spinner("AI simple English me viral post aur visual graphic bana raha hai..."):
            try:
                if "Morning" in slot_option:
                    result = generate_morning_ui_post(profile_summary, custom_topic, api_key=gemini_key)
                    cat = "ui_ux"
                elif "Afternoon" in slot_option:
                    result = generate_afternoon_frontend_post(profile_summary, custom_topic, api_key=gemini_key)
                    cat = "frontend"
                elif "Evening" in slot_option:
                    result = generate_evening_ai_post(profile_summary, custom_topic, api_key=gemini_key)
                    cat = "ai_news"
                else:
                    result = generate_weekend_interactive_post("poll", api_key=gemini_key)
                    cat = "weekend"

                st.session_state.current_draft = result["content"]
                st.session_state.current_topic = result["topic"]
                st.session_state.current_category = cat

                # Generate matching visual graphic
                svg = generate_svg_banner(
                    title=result["topic"],
                    category=cat,
                    author="@LinkedInCreator"
                )
                st.session_state.current_svg = svg
                st.success("✅ Post & Graphic Card ready ho gaya!")

            except Exception as e:
                st.error(f"Generation error: {e}")

    # Display & Edit Section
    if st.session_state.current_draft:
        st.markdown("---")
        st.markdown(f"### 🖼️ Visual Graphic Banner ({st.session_state.current_category.upper()})")
        st.caption("Ye image post ke sath attach karne ke liye auto-design hui hai (1080x1080):")
        
        # Render SVG directly
        st.markdown(f'<div class="banner-preview-box">{st.session_state.current_svg}</div>', unsafe_allow_html=True)
        st.download_button(
            label="📥 Download Banner Image (SVG)",
            data=st.session_state.current_svg,
            file_name=f"linkedin_{st.session_state.current_category}_banner.svg",
            mime="image/svg+xml"
        )

        st.markdown("### 👁️ Post Preview & Hashtags (Simple English)")
        st.markdown(f"""
        <div class="linkedin-card">
            <strong>Your Profile</strong> • <small>Public 🌐</small><br><br>
            {st.session_state.current_draft}
        </div>
        """, unsafe_allow_html=True)

        # Editable Box
        edited_text = st.text_area("📝 Edit Text Manually:", value=st.session_state.current_draft, height=220)
        st.session_state.current_draft = edited_text

        # AI Modification / Refinement Section
        with st.expander("🛠️ AI se Post ya Code me Changes Karwayein", expanded=False):
            st.caption("Aap koi bhi change maang sakte hain (e.g. 'Figma shortcut add karo', 'React code snippet daalo', 'English aur easy karo'):")
            feedback = st.text_input("Aapko kya change chahiye?", placeholder="e.g. Add 4 lines of clean CSS code, make it shorter")
            if st.button("🔄 Apply Changes to Draft"):
                if feedback.strip():
                    with st.spinner("Changes apply ho rahe hain..."):
                        updated = refine_post(st.session_state.current_draft, feedback, api_key=gemini_key)
                        st.session_state.current_draft = updated
                        st.success("Post updated successfully!")
                        st.rerun()

        st.markdown("---")
        col_wa, col_post = st.columns(2)
        with col_wa:
            if st.button("📱 Send to WhatsApp Preview"):
                with st.spinner("WhatsApp par bheja ja raha hai..."):
                    res = send_whatsapp_preview(
                        post_text=st.session_state.current_draft,
                        account_sid=twilio_sid,
                        auth_token=twilio_token,
                        from_whatsapp=twilio_from,
                        to_whatsapp=user_phone
                    )
                    if res.get("success"):
                        st.success("✅ WhatsApp par preview chala gaya!")
                    else:
                        st.error(f"WhatsApp Error: {res.get('error')}")

        with col_post:
            if st.button("🚀 Post Now to LinkedIn", type="primary"):
                with st.spinner("Publishing to LinkedIn..."):
                    res = publish_linkedin_post(
                        post_text=st.session_state.current_draft,
                        token=linkedin_token,
                        urn=linkedin_urn
                    )
                    if res.get("success"):
                        st.balloons()
                        st.success("🎉 Post successfully uploaded to LinkedIn!")
                        add_post_to_history(st.session_state.current_draft, "PUBLISHED", res.get("post_id", ""))
                    else:
                        st.error(f"LinkedIn Error: {res.get('error')}")

# -----------------------------------------------------------------------------
# TAB 2: RESUME PROFILE
# -----------------------------------------------------------------------------
with tab_resume:
    st.subheader("📄 Upload Resume (PDF)")
    st.caption("Aapka resume extract karke AI aapke skills ke related topics save karega.")
    
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    if uploaded_file is not None:
        if st.button("⚡ Parse & Save Profile", type="primary"):
            with st.spinner("Extracting resume skills with Gemini..."):
                try:
                    text = extract_text_from_pdf_stream(uploaded_file)
                    p_res = analyze_resume_profile(text, api_key=gemini_key)
                    save_profile(p_res)
                    st.session_state.profile_data = p_res
                    st.success("✅ Resume skills saved successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.profile_data:
        st.markdown("---")
        st.markdown("### 🧠 Saved Skills & Domains")
        st.markdown(st.session_state.profile_data.get("analysis", ""))

# -----------------------------------------------------------------------------
# TAB 3: WHATSAPP REVIEW & TIMING INFO
# -----------------------------------------------------------------------------
with tab_whatsapp:
    st.subheader("📱 High-Traffic Timings & Automated Review")
    st.markdown("""
    Bot in **3 peak traffic times** par automatically operate karega:
    
    | Slot | Time (IST) | Content Type | Strategy |
    | :--- | :--- | :--- | :--- |
    | **🌅 Morning** | 08:30 - 09:30 AM | UI/UX & Design Short Tricks (Figma/XD/Mobile) | High save & share rate |
    | **☀️ Afternoon** | 01:00 - 02:00 PM | Frontend Code Hacks (CSS, JS, React) | Tech community shares |
    | **🌙 Evening** | 06:30 - 07:30 PM | Trending AI News & Tool Breakdown | Viral reach & debates |
    | **🎉 Weekend** | Sat & Sun | Interactive Polls, Quizzes & A vs B | 5x more comments |
    
    Har post me:
    - **Very simple English** (No hard words).
    - **10 to 15 targeted hashtags**.
    - **Auto-generated visual banner image**.
    """)

# -----------------------------------------------------------------------------
# TAB 4: HISTORY
# -----------------------------------------------------------------------------
with tab_history:
    st.subheader("📜 Recent Posts History")
    hist = load_history()
    if not hist:
        st.info("No posts published yet.")
    else:
        for item in hist:
            with st.expander(f"📌 {item.get('timestamp')} - {item.get('status')}"):
                st.text(item.get("content"))
