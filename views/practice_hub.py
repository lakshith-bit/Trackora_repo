import streamlit as st
import db

def render():
    st.markdown("<h2 style='margin-bottom: 25px;'>Practice Hub 🎸</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="custom-card" style="border-top: 4px solid #2CB67D;">
            <h3 style="margin-top:0;">📅 Schedule Practice</h3>
        </div>
        """, unsafe_allow_html=True)
        time_inp = st.time_input("Time")
        dur_inp = st.number_input("Duration (minutes)", min_value=5, max_value=300, value=30)
        st.info("Camera tracking will ensure your posture and activity.", icon="📷")
        
        if st.button("▶️ Start Practice Timer", type="primary", use_container_width=True):
            st.success("Timer started! Practice hard.")
            db.update_streak(st.session_state['user_id'], dur_inp)
            st.snow()
            
    with col2:
        st.markdown("""
        <div class="custom-card" style="border-top: 4px solid #7F5AF0;">
            <h3 style="margin-top:0;">🎥 Upload & Live</h3>
        </div>
        """, unsafe_allow_html=True)
        st.file_uploader("Upload Recording", type=["mp4", "mov", "mp3", "wav"])
        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns(2)
        cols[0].button("▶ Join Live", use_container_width=True)
        cols[1].button("➕ Create Live", use_container_width=True)
        
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top: 30px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 20px;'>Recent Recordings</h3>", unsafe_allow_html=True)
    
    recordings = [
        {"name": "Alice", "inst": "Piano", "time": "2 hours ago", "upvotes": 14},
        {"name": "Bob", "inst": "Guitar", "time": "5 hours ago", "upvotes": 8},
        {"name": "Charlie", "inst": "Violin", "time": "1 day ago", "upvotes": 24},
        {"name": "Diana", "inst": "Vocals", "time": "2 days ago", "upvotes": 42}
    ]
    
    for i in range(0, len(recordings), 2):
        row_cols = st.columns(2)
        for j in range(2):
            if i + j < len(recordings):
                rec = recordings[i+j]
                with row_cols[j]:
                    st.markdown(f"""
                    <div class="custom-card" style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <p style="margin:0; font-weight:bold; font-size: 1.1rem;">{rec['name']}</p>
                            <p style="margin:0; font-size:12px; color:#a0aec0;">{rec['inst']} • {rec['time']}</p>
                        </div>
                        <div style="text-align:center; background:rgba(44, 182, 125, 0.1); border: 1px solid rgba(44, 182, 125, 0.3); border-radius:8px; padding:5px 12px; color:#2CB67D; font-weight:bold;">
                            ⇧ {rec['upvotes']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
