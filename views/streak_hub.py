import streamlit as st
import db

def render():
    st.markdown("<h2 style='margin-bottom: 25px;'>Streak Hub 🔥</h2>", unsafe_allow_html=True)
    
    user = db.get_user_by_id(st.session_state['user_id'])
    
    # Daily Task Section
    task = db.get_or_create_daily_task(st.session_state['user_id'])
    st.markdown("""
<div class="custom-card" style="border-left: 5px solid #e056fd; margin-bottom: 25px;">
    <h3 style="margin-top:0;">🎯 Today's Mission</h3>
</div>
""", unsafe_allow_html=True)
    
    cols_task = st.columns([3, 1])
    with cols_task[0]:
        st.info(task['task_desc'])
    with cols_task[1]:
        if not task['completed']:
            if st.button("Complete Mission ✓", use_container_width=True):
                db.complete_daily_task(st.session_state['user_id'])
                st.balloons()
                st.success("+1 Streak Day!")
                st.rerun()
        else:
            st.success("Mission Accomplished! ✅")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
<div class="custom-card" style="border-top: 4px solid #2CB67D; height: 100%;">
    <h3 style="margin-top:0;">Individual Streak</h3>
""", unsafe_allow_html=True)
        st.markdown(f"<p class='big-number' style='text-align:center;'>{user['current_streak']}</p>", unsafe_allow_html=True)
        st.progress(min(user['current_streak']/30.0, 1.0))
        st.markdown(f"<p style='text-align:center; color:#a0aec0; font-size:12px;'>Next Milestone: 30 Days</p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color:rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        st.metric("Highest Streak", f"{user['highest_streak']} Days")
        this_week = min(user['current_streak'], 7)
        st.metric("This Week", f"{this_week}/7 Days")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
<div class="custom-card" style="border-top: 4px solid #e67e22; height: 100%;">
    <h3 style="margin-top:0; color:white;">Group Streak</h3>
""", unsafe_allow_html=True)
        st.markdown(f"<p class='big-number' style='text-align:center; background: -webkit-linear-gradient(135deg, #e67e22 0%, #d35400 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>0</p>", unsafe_allow_html=True)
        st.progress(0)
        st.markdown(f"<p style='text-align:center; color:#a0aec0; font-size:12px;'>Join a group to start a streak</p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color:rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        st.metric("Highest Group Streak", "0 Days")
        st.markdown("<p style='color:#e74c3c; font-size:13px; font-weight:bold; margin-top:20px;'>⚠️ Last broken by: N/A</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<h3 style='margin-top:30px;'>Weekly Streak History</h3>", unsafe_allow_html=True)
    st.markdown("""
<div class="custom-card">
    <p style="color:#a0aec0; font-style:italic;">Visual history of your consistency.</p>
    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
        <span>Week 1 (Current)</span>
        <span style="color:#2CB67D;">7/7</span>
    </div>
    <div style="background:#2D3748; height:10px; border-radius:5px; width:100%; margin-bottom:20px;"><div style="background:#2CB67D; width:100%; height:100%; border-radius:5px;"></div></div>
    
    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
        <span>Week 2</span>
        <span style="color:#e67e22;">5/7</span>
    </div>
    <div style="background:#2D3748; height:10px; border-radius:5px; width:100%;"><div style="background:linear-gradient(90deg, #e67e22 0%, #d35400 100%); width:71%; height:100%; border-radius:5px;"></div></div>
</div>
""", unsafe_allow_html=True)
