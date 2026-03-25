import streamlit as st
import db

def render():
    st.markdown("<h2 style='margin-bottom: 25px;'>Group Hub 👥</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Create Group", use_container_width=True):
            st.session_state['show_create_group'] = not st.session_state.get('show_create_group', False)
    with col2:
        if st.button("🔍 Join Group", use_container_width=True):
            st.session_state['show_join_group'] = not st.session_state.get('show_join_group', False)
            
    if st.session_state.get('show_create_group', False):
        with st.form("create_group"):
            g_name = st.text_input("Group Name")
            if st.form_submit_button("Create") and g_name:
                if db.create_group(g_name, st.session_state['user_id']):
                    st.success("Group created!")
                    st.session_state['show_create_group'] = False
                    st.rerun()
                else:
                    st.error("Name taken or error.")
                    
    if st.session_state.get('show_join_group', False):
        with st.form("join_group"):
            all_groups = db.run_query("SELECT * FROM groups")
            g_sel = st.selectbox("Select Group", [g['name'] for g in all_groups] if all_groups else ["No groups yet"])
            if st.form_submit_button("Join") and all_groups:
                g_id = next(g['id'] for g in all_groups if g['name'] == g_sel)
                if db.join_group(g_id, st.session_state['user_id']):
                    st.success("Joined!")
                    st.session_state['show_join_group'] = False
                    st.rerun()
                else:
                    st.error("Already joined or error.")
                    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown("<h3>Your Groups</h3>", unsafe_allow_html=True)
    
    my_groups = db.run_query('''
        SELECT g.id, g.name, COUNT(gm.user_id) as members
        FROM groups g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE g.id IN (SELECT group_id FROM group_members WHERE user_id = ?)
        GROUP BY g.id
    ''', (st.session_state['user_id'],))
    
    if not my_groups:
        st.info("You haven't joined any groups yet.")
    else:
        for grp in my_groups:
            g_task = db.get_or_create_group_task(grp['id'])
            comp_status = db.get_group_completion_status(grp['id'])
            
            # Check if current user completed
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            user_completed_query = db.run_query("SELECT * FROM group_task_completions WHERE group_id = ? AND user_id = ? AND task_date = ?", (grp['id'], st.session_state['user_id'], today))
            user_has_done = len(user_completed_query) > 0
            
            st.markdown(f"""
            <div class="custom-card" style="margin-bottom: 20px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <h4 style="margin:0; color:white; font-size: 1.4rem;">{grp['name']} <span style="color:#a0aec0; font-size: 0.9rem;">(👤 {grp['members']} members)</span></h4>
                    <span style="background:rgba(127, 90, 240, 0.2); color:#7F5AF0; padding:4px 10px; border-radius:12px; font-size:13px; font-weight:bold;">🔥 {'Active' if comp_status['all_done'] else 'Pending'} Streak</span>
                </div>
                <div style="margin-top: 15px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 8px; border-left: 4px solid #f6ad55;">
                    <h5 style="margin:0 0 10px 0; color:#fbd38d;">🤝 Group Mission:</h5>
                    <p style="margin:0; color:#e2e8f0;">{g_task['task_desc']}</p>
                    <p style="margin:10px 0 0 0; font-size:12px; color:#a0aec0;">Progress: {comp_status['completed']} / {comp_status['total_members']} members completed</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if not comp_status['all_done']:
                if not user_has_done:
                    st.warning("⚠️ You haven't practiced today! Complete a session in the Practice Hub to fulfill your part for the group.")
                else:
                    st.info("✅ You completely your part by practicing today! Waiting for others... ⏳")
            else:
                st.success("🌟 Group Mission Accomplished! The group streak continues!")
