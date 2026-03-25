import streamlit as st
import db
import math

def render():
    st.markdown("<h2 style='margin-bottom: 25px;'>Leaderboard 🏆</h2>", unsafe_allow_html=True)
    
    users = db.run_query("SELECT * FROM users")
    
    if not users:
        st.info("Not enough data to display leaderboard.")
        return
        
    for u in users:
        total_hours = u.get('total_hours', 0)
        profile_points = u.get('profile_points', 0)
        current_streak = u.get('current_streak', 0)
        u['xp'] = int((total_hours * 100) + (profile_points * 50) + (current_streak * 25))
        u['level'] = int(math.sqrt(max(0, u['xp']))) // 10 + 1

    t1, t2 = st.tabs(["🔥 Top Streaks", "🌟 Highest XP"])
    
    with t1:
        st.markdown("### Top Streaks")
        top_streaks = sorted(users, key=lambda x: x['highest_streak'], reverse=True)[:10]
        for idx, u in enumerate(top_streaks):
            st.markdown(f"""
<div class="custom-card" style="display:flex; justify-content:space-between; align-items:center; padding: 15px;">
    <div style="display:flex; align-items:center; gap: 15px;">
        <h2 style="margin:0; min-width:30px; color:#a0aec0;">#{idx+1}</h2>
        <div>
            <h4 style="margin:0;">{u['username']} <span style="font-size:12px; color:#7F5AF0;">(Lvl {u['level']})</span></h4>
            <p style="margin:0; color:#a0aec0; font-size:12px;">{u['instrument']}</p>
        </div>
    </div>
    <h3 style="margin:0; color:#e67e22;">{u['highest_streak']} Days</h3>
</div>
""", unsafe_allow_html=True)
            
    with t2:
        st.markdown("### Highest XP (Most Dedicated)")
        top_xp = sorted(users, key=lambda x: x['xp'], reverse=True)[:10]
        for idx, u in enumerate(top_xp):
            st.markdown(f"""
<div class="custom-card" style="display:flex; justify-content:space-between; align-items:center; padding: 15px;">
    <div style="display:flex; align-items:center; gap: 15px;">
        <h2 style="margin:0; min-width:30px; color:#a0aec0;">#{idx+1}</h2>
        <div>
            <h4 style="margin:0;">{u['username']} <span style="font-size:12px; color:#7F5AF0;">(Lvl {u['level']})</span></h4>
            <p style="margin:0; color:#a0aec0; font-size:12px;">{u['instrument']}</p>
        </div>
    </div>
    <h3 style="margin:0; color:#2CB67D;">{u['xp']} XP</h3>
</div>
""", unsafe_allow_html=True)
