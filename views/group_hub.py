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
        for i in range(0, len(my_groups), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(my_groups):
                    grp = my_groups[i+j]
                    with cols[j]:
                        st.markdown(f"""
                        <div class="custom-card">
                            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                                <h4 style="margin:0; color:white; font-size: 1.3rem;">{grp['name']}</h4>
                                <span style="background:rgba(127, 90, 240, 0.2); color:#7F5AF0; padding:4px 8px; border-radius:12px; font-size:12px; font-weight:bold;">🔥 0 Day Streak</span>
                            </div>
                            <p style="color:#a0aec0; margin-top:10px; font-size: 0.9rem;">👤 {grp['members']} members</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.button("View Details", key=f"view_grp_{grp['id']}", use_container_width=True)
