import streamlit as st
import db
from datetime import datetime

def time_ago(dt_str):
    try:
        past = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f')
    except:
        try:
            past = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except:
            return dt_str # fallback
    
    diff = datetime.now() - past
    s = diff.total_seconds()
    if s < 60:
        return "Just now"
    elif s < 3600:
        return f"{int(s//60)}m"
    elif s < 86400:
        return f"{int(s//3600)}h"
    else:
        return f"{int(s//86400)}d"

def render():
    st.markdown("<h2 style='margin-bottom: 25px; text-align: center;'>Community Feed 📸</h2>", unsafe_allow_html=True)
    
    recordings = db.run_query("""
        SELECT p.id, p.duration_minutes, p.created_at, p.upvotes, p.file_path, p.user_id, u.username, u.instrument, u.highest_streak 
        FROM practices p 
        JOIN users u ON p.user_id = u.id 
        WHERE p.file_path IS NOT NULL
        ORDER BY p.created_at DESC LIMIT 50
    """)
    
    if not recordings:
        st.info("No activity in the community yet. Head over to the Practice Hub to post the first session!")
        return

    # Center the Instagram feed
    col_spacer1, col_main, col_spacer2 = st.columns([1, 2, 1])
    
    with col_main:
        for rec in recordings:
            ago = time_ago(rec['created_at'])
            
            # Header Container
            header_html = f"""
<div style="background-color: #1a1c23; border: 1px solid rgba(255,255,255,0.05); border-radius: 12px 12px 0 0; box-shadow: 0 4px 12px rgba(0,0,0,0.4); margin-top:20px; padding: 15px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05);">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div style="background: linear-gradient(135deg, #e056fd 0%, #686de0 100%); width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; color: white;">
            {rec['username'][0].upper()}
        </div>
        <div>
            <h4 style="margin: 0; font-size: 1.1rem; color: white;">{rec['username']}</h4>
            <p style="margin: 0; font-size: 12px; color: #a0aec0;">🔥 {rec['highest_streak']} Day Streak</p>
        </div>
    </div>
    <span style="color: #cbd5e1; font-size: 0.9rem;">{ago}</span>
</div>
"""
            st.markdown(header_html, unsafe_allow_html=True)
            
            # Play Media
            try:
                if rec['file_path'].lower().endswith(('.mp4', '.mov')):
                    st.video(rec['file_path'])
                elif rec['file_path'].lower().endswith(('.mp3', '.wav')):
                    st.audio(rec['file_path'])
            except Exception as e:
                st.info("Media processing error")
            
            footer_html = f"""
<div style="background-color: #1a1c23; border: 1px solid rgba(255,255,255,0.05); border-radius: 0 0 12px 12px; padding: 15px; border-top: none; margin-bottom: 5px;">
    <small style="color: #a0aec0;">Liked by <b>{rec['upvotes']} musicians</b></small>
</div>
"""
            st.markdown(footer_html, unsafe_allow_html=True)
            
            # Post Footer Actions
            f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
            with f_col1:
                # Upvote Button mapped nicely underneath
                if st.button(f"❤️ Like", key=f"up_{rec['id']}", use_container_width=True):
                    db.run_query("UPDATE practices SET upvotes = upvotes + 1 WHERE id = ?", (rec['id'],), fetch=False)
                    db.update_profile_points(rec['user_id'], 1)
                    st.rerun()
            with f_col2:
                # Disabled Comment button to look like IG
                st.button("💬 Comment", key=f"com_{rec['id']}", disabled=True, use_container_width=True)
                
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-bottom: 30px; margin-top: 20px;'>", unsafe_allow_html=True)
