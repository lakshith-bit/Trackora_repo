import streamlit as st
import os
import db
import auth
import math

# ✅ MOVE IMPORTS HERE (CRITICAL FIX)
from views import dashboard, group_hub, practice_hub, streak_hub, collab_hub, performance, leaderboard_hub, feed_hub

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Trackora 🎵", page_icon="🎵", layout="wide")

# ------------------ DB INIT ------------------
db.init_db()

# ------------------ LOAD CSS ------------------
def load_css():
    if os.path.exists('assets/style.css'):
        with open('assets/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# ------------------ SESSION STATE INIT ------------------
st.session_state.setdefault("user_id", None)
st.session_state.setdefault("username", "")
st.session_state.setdefault("page", "dashboard")

# ------------------ NAVBAR ------------------
def render_navbar():
    col1, col2 = st.columns([10, 2])
    with col1:
        st.markdown(f"""
            <div style="
                display:flex;
                align-items:center;
                padding:10px 20px;
                background:#1E2028;
                border-radius:10px;
                margin-bottom:20px;">
                <h2 style="margin:0; color:white;">🎵 Trackora</h2>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        user_id = st.session_state.get('user_id')
        if user_id:
            user = db.get_user_by_id(user_id)
            if user:
                with st.popover("👤 Profile", use_container_width=True):
                    st.markdown("### User Profile")
                    
                    # Compute XP
                    total_hours = user.get('total_hours') or 0
                    profile_points = user.get('profile_points') or 0
                    current_streak = user.get('current_streak') or 0
                    
                    try:
                        xp = int((total_hours * 100) + (profile_points * 50) + (current_streak * 25))
                    except:
                        xp = 0
                        
                    level = int(math.sqrt(max(0, xp))) // 10 + 1
                    next_level_xp = ((level * 10) ** 2)
                    prev_level_xp = (((level - 1) * 10) ** 2)
                    progress = (xp - prev_level_xp) / max(1, next_level_xp - prev_level_xp)
                    
                    st.markdown(f"**Level {level} Musician** ✨")
                    st.progress(min(progress, 1.0))
                    st.write(f"*{xp} / {next_level_xp} XP*")
                    
                    st.divider()
                    st.write(f"**Name:** {user.get('name', 'N/A')}")
                    st.write(f"**Email:** {user.get('email', 'N/A')}")
                    st.write(f"**Age:** {user.get('age', 'N/A')}")
                    st.write(f"**Instrument:** {user.get('instrument', 'N/A')}")
                    st.write(f"**Genre:** {user.get('genre', 'N/A')}")
                    st.write(f"**Experience:** {user.get('experience', 'N/A')}")
                    st.write(f"**Teacher:** {user.get('teacher', 'N/A')}")
                    st.write(f"**Public:** {'Yes' if user.get('is_public') else 'No'}")
                    
                    if level >= 5:
                        st.divider()
                        st.success("🏆 Maestro Badge Acquired! (Level 5+)")

# ------------------ SIDEBAR ------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🔥 Streaks")

        user = None
        if st.session_state.user_id:
            user = db.get_user_by_id(st.session_state.user_id)

        current_streak = user['current_streak'] if user else 0

        st.markdown(f"""
        <div style="padding:15px; background:#1E2028; border-radius:12px; text-align:center; margin-bottom:10px;">
            <p style="margin:0; color:#cbd5e1;">Individual Streak</p>
            <h2>{current_streak}</h2>
            <p style="margin:0; color:#94a3b8;">Days</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="padding:15px; background:#1E2028; border-radius:12px; text-align:center;">
            <p style="margin:0; color:#cbd5e1;">Group Streak</p>
            <h2 style="color:#e67e22;">0</h2>
            <p style="margin:0; color:#94a3b8;">Days</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("## 📌 Navigation")

        pages = {
            "Dashboard 🏠": "dashboard",
            "Feed Hub 📸": "feed_hub",
            "Group Hub 👥": "group_hub",
            "Practice Hub 🎸": "practice_hub",
            "Streak Hub 🔥": "streak_hub",
            "Collab Hub 🤝": "collab_hub",
            "Performance Hub 📊": "performance_page",
            "Leaderboard 🏆": "leaderboard_hub"
        }

        for name, key in pages.items():
            if st.button(name, key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()  # ✅ controlled rerun

        if st.button("Logout", key="logout_btn", use_container_width=True):
            auth.logout_user()

# ------------------ MAIN APP ------------------
def main():

    # ✅ STRONG LOGIN CHECK
    if "user_id" not in st.session_state or st.session_state.user_id is None:
        auth.show_auth_page()
        return

    render_navbar()
    render_sidebar()

    page = st.session_state.page

    try:
        if page == 'dashboard':
            dashboard.render()

        elif page == 'group_hub':
            group_hub.render()

        elif page == 'practice_hub':
            practice_hub.render()

        elif page == 'streak_hub':
            streak_hub.render()

        elif page == 'collab_hub':
            collab_hub.render()

        elif page == 'performance_page':
            performance.render()
            
        elif page == 'leaderboard_hub':
            leaderboard_hub.render()
            
        elif page == 'feed_hub':
            feed_hub.render()

        else:
            dashboard.render()

    except Exception as e:
        st.error(f"Error loading page: {e}")

# ------------------ RUN ------------------
if __name__ == "__main__":
    main()