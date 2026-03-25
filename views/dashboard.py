import streamlit as st

def render():
    st.markdown('<h1 style="margin-top: 0; color: white;">Welcome to Trackora</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #a0aec0; margin-bottom: 30px; font-size: 1.1rem;">Choose a hub to get started</p>', unsafe_allow_html=True)
    
    # Render Cards horizontally in a grid format using Streamlit columns
    card_html = """
<div class="custom-card {color}" style="display: flex; justify-content: space-between; align-items: center; padding: 25px; margin-bottom: 10px;">
    <div>
        <h3 style="margin:0; color:white; font-size: 1.5rem;">{icon} {title}</h3>
        <p style="margin:5px 0 0 0; color:rgba(255,255,255,0.8); font-size: 1rem;">{desc}</p>
    </div>
</div>
"""
    
    def hub_card(col, page, color, icon, title, desc):
        with col:
            st.markdown(card_html.format(color=color, icon=icon, title=title, desc=desc), unsafe_allow_html=True)
            if st.button(f"Go to {title} →", key=f"btn_dash_{page}", use_container_width=True):
                st.session_state.page = page
                st.rerun()
            
    col1, col2 = st.columns(2)
    hub_card(col1, "group_hub", "bg-purple", "👥", "Group Hub", "Create or join accountability groups")
    hub_card(col2, "practice_hub", "bg-green", "🎸", "Practice Hub", "Schedule sessions and go live")
    
    col3, col4 = st.columns(2)
    hub_card(col3, "streak_hub", "bg-orange", "🔥", "Streak Hub", "Track your musical consistency")
    hub_card(col4, "collab_hub", "bg-pink", "🤝", "Collab Hub", "Find partners for your next project")
    
    # 5th card spans full or center
    col5, _ = st.columns([1, 1])
    hub_card(col5, "performance_page", "bg-blue", "📊", "Performance Hub", "View analytics and insights")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3>🌐 Community Activity</h3>", unsafe_allow_html=True)
    import db
    recent_practices = db.run_query("""
        SELECT p.duration_minutes, p.created_at, u.username, u.instrument 
        FROM practices p 
        JOIN users u ON p.user_id = u.id 
        ORDER BY p.created_at DESC LIMIT 5
    """)
    if not recent_practices:
        st.info("No activity yet. Be the first to practice!")
    else:
        for p in recent_practices:
            st.markdown(f"""
<div style="background-color:rgba(255,255,255,0.05); padding:12px 15px; border-radius:8px; margin-bottom:10px; display:flex; align-items:center; gap:15px; border-left: 3px solid #7F5AF0; transition: transform 0.2s;">
    <span style="font-size:24px;">🔥</span>
    <div>
        <span style="color:white; font-weight:bold; font-size:1.1rem;">{p['username']}</span> 
        <span style="color:#cbd5e1;">practiced <span style="color:#e056fd; font-weight:bold;">{p['instrument']}</span> for {p['duration_minutes']} minutes.</span>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Motivation Card Bottom
    st.markdown("""
<div class="custom-card" style="text-align: center; padding: 30px; background-color: rgba(30, 32, 40, 0.7); border-radius: 12px; border-left: 5px solid #7F5AF0;">
    <p style="font-size: 1.2rem; font-style: italic; color: #cbd5e1; margin:0;">"Without music, life would be a mistake." <br><br>— Friedrich Nietzsche</p>
</div>
""", unsafe_allow_html=True)
