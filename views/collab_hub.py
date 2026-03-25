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
    
    users = db.run_query("SELECT * FROM users WHERE id != ?", (st.session_state['user_id'],))
    
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
                        st.markdown(f"""
                        <div class="custom-card" style="text-align:center; padding-top:30px; border-top: 4px solid #e056fd;">
                            <div style="background:linear-gradient(135deg, #e056fd 0%, #686de0 100%); width:60px; height:60px; border-radius:50%; margin:0 auto 15px auto; display:flex; align-items:center; justify-content:center; font-size:24px; font-weight:bold; color:white;">
                                {u['username'][0].upper()}
                            </div>
                            <h4 style="margin:0; font-size:1.2rem; color:white;">{u['username']}</h4>
                            <p style="color:#a0aec0; font-size:13px; margin:5px 0;">📍 {u['region']}</p>
                            <div style="margin: 15px 0; display:flex; justify-content:center; gap:5px; flex-wrap:wrap;">
                                <span style="background:rgba(255,255,255,0.1); padding:4px 10px; border-radius:12px; font-size:11px; color:#cbd5e1;">{u['instrument']}</span>
                                <span style="background:rgba(255,255,255,0.1); padding:4px 10px; border-radius:12px; font-size:11px; color:#cbd5e1;">{u['genre']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Send Request", key=f"req_{u['id']}", use_container_width=True):
                            st.success(f"Request sent to {u['username']}!")
                        
    st.markdown("<hr style='border-color:rgba(255,255,255,0.1); margin-top:40px; margin-bottom:30px;'>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4>📤 Sent Requests</h4>", unsafe_allow_html=True)
        st.info("No pending requests.", icon="📩")
    with c2:
        st.markdown("<h4>📥 Received Requests</h4>", unsafe_allow_html=True)
        st.info("No new requests.", icon="📬")
