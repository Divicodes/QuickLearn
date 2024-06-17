import streamlit as st
from generator import generate_video


# Creating a tab interface for navigation
tab1, tab2 = st.tabs(["Home", "Settings"])

# Content for the 'Home' tab
with tab1:
    st.header("EUERK.Ai 💡")
    topic = st.text_input("What topic do you want to learn", key="topic")
    if st.button("Explain"):
        if topic:
            # Get explanation and video URL
            interests = st.session_state["user_info"]
            explanation, video_url = generate_video(topic, interests, debug_mode=True)
            # Save to session state
            st.session_state["explanation"] = explanation
            st.session_state["video_url"] = video_url
        else:
            st.warning("Please enter a topic to explain.")

    if "video_url" in st.session_state:
        st.subheader("Video Explanation")
        st.video(st.session_state["video_url"])

    if "explanation" in st.session_state:
        st.subheader("Explanation")
        st.write(st.session_state["explanation"])


# Content for the 'Settings' tab
with tab2:
    st.header("Settings")
    user_info = st.text_area("What are your interests", key="user_info")
