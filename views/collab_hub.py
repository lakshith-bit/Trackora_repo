import streamlit as st
import db

def render():
    st.markdown("<h2 style='margin-bottom: 25px;'>Collab Hub 🤝</h2>", unsafe_allow_html=True)
    
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_q = st.text_input("Search musicians...", placeholder="Name, instrument or genre", label_visibility="collapsed")
    with col_filter:
        filt = st.selectbox("Filter By", ["All", "Guitar", "Piano", "Vocals", "Drums", "Violin", "Other"], label_visibility="collapsed")
        
    st.markdown("<h3 style='margin-top:20px; color:#cbd5e1;'>Discover Partners</h3>", unsafe_allow_html=True)
    
    users = db.run_query("SELECT * FROM users WHERE is_public = 1 AND id != ?", (st.session_state['user_id'],))
    
    if filt != "All":
        users = [u for u in users if u['instrument'] == filt]
        
    if search_q:
        users = [u for u in users if search_q.lower() in u['username'].lower() or search_q.lower() in str(u['instrument']).lower()]

    if not users:
        st.info("No musicians found matching your criteria.")
    else:
        for i in range(0, len(users), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(users):
                    u = users[i+j]
                    with cols[j]:
                        import math
                        th = u.get('total_hours') or 0
                        pp = u.get('profile_points') or 0
                        cs = u.get('current_streak') or 0
                        xp = int((th * 100) + (pp * 50) + (cs * 25))
                        level = int(math.sqrt(max(0, xp))) // 10 + 1
                        
                        st.markdown(f"""
<div class="custom-card" style="text-align:center; padding-top:30px; border-top: 4px solid #e056fd; transition: transform 0.2s;">
    <div style="background:linear-gradient(135deg, #e056fd 0%, #686de0 100%); width:60px; height:60px; border-radius:50%; margin:0 auto 15px auto; display:flex; align-items:center; justify-content:center; font-size:24px; font-weight:bold; color:white; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
        {u['username'][0].upper()}
    </div>
    <h4 style="margin:0; font-size:1.2rem; color:white;">{u['username']} <span style="font-size:0.9rem; color:#a289f7;">(Lvl {level})</span></h4>
    <p style="color:#cbd5e1; font-size:13px; margin:5px 0;">📍 {u['region']} &nbsp;|&nbsp; 🔥 {u.get('highest_streak') or 0} Days</p>
    <div style="margin: 15px 0; display:flex; justify-content:center; gap:5px; flex-wrap:wrap;">
        <span style="background:rgba(224, 86, 253, 0.1); border: 1px solid rgba(224, 86, 253, 0.3); padding:4px 10px; border-radius:12px; font-size:11px; color:#e056fd; font-weight:bold;">{u['instrument']}</span>
        <span style="background:rgba(255,255,255,0.1); padding:4px 10px; border-radius:12px; font-size:11px; color:#cbd5e1;">{u['genre']}</span>
        <span style="background:rgba(255,255,255,0.1); padding:4px 10px; border-radius:12px; font-size:11px; color:#cbd5e1;">{u['experience']}</span>
    </div>
</div>
""", unsafe_allow_html=True)
                        if st.button("Send Request", key=f"req_{u['id']}", use_container_width=True):
                            existing = db.run_query("SELECT id FROM collab_requests WHERE sender_id = ? AND receiver_id = ?", (st.session_state['user_id'], u['id']))
                            if existing:
                                st.warning("Request already sent!")
                            else:
                                from datetime import datetime
                                db.run_query("INSERT INTO collab_requests (sender_id, receiver_id, status, created_at) VALUES (?, ?, ?, ?)", (st.session_state['user_id'], u['id'], 'pending', datetime.now()), fetch=False)
                                db.update_profile_points(st.session_state['user_id'], 1)  # Sender gets 1 point
                                db.update_profile_points(u['id'], 2)  # Highly requested musicians get points
                                st.success(f"Request sent to {u['username']}! (+1 pt)")
                                st.rerun()
                        
    st.markdown("<hr style='border-color:rgba(255,255,255,0.1); margin-top:40px; margin-bottom:30px;'>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4>📤 Sent Requests</h4>", unsafe_allow_html=True)
        sent_reqs = db.run_query("SELECT cr.*, u.username as receiver_name FROM collab_requests cr JOIN users u ON cr.receiver_id = u.id WHERE cr.sender_id = ?", (st.session_state['user_id'],))
        if not sent_reqs:
            st.info("No sent requests.", icon="📩")
        else:
            for req in sent_reqs:
                st.write(f"To: **{req['receiver_name']}** - Status: *{req['status']}*")

    with c2:
        st.markdown("<h4>📥 Received Requests</h4>", unsafe_allow_html=True)
        received_reqs = db.run_query("SELECT cr.*, u.username as sender_name FROM collab_requests cr JOIN users u ON cr.sender_id = u.id WHERE cr.receiver_id = ?", (st.session_state['user_id'],))
        if not received_reqs:
            st.info("No new requests.", icon="📬")
        else:
            for req in received_reqs:
                col_info, col_act = st.columns([3, 1])
                with col_info:
                    st.write(f"From: **{req['sender_name']}** - [{req['status']}]")
                with col_act:
                    if req['status'] == 'pending':
                        if st.button("Accept Invitation", key=f"acc_{req['id']}", use_container_width=True):
                            db.run_query("UPDATE collab_requests SET status = 'accepted' WHERE id = ?", (req['id'],), fetch=False)
                            db.update_profile_points(st.session_state['user_id'], 3) # Extra reward for matching
                            st.toast("Collaboration Accepted! 🎉", icon="🔥")
                            st.balloons()
                            st.rerun()
