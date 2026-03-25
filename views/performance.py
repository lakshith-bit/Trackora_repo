import streamlit as st
import db
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

def render():
    st.markdown("<h2 style='margin-bottom: 25px;'>Performance Hub 📊</h2>", unsafe_allow_html=True)
    
    user = db.get_user_by_id(st.session_state['user_id'])
    
    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Hours", f"{round(user['total_hours'], 1)}h", "+2.5h this week")
    with c2:
        st.metric("Practice Days", f"{user['highest_streak'] + 4} Days", "Top 10%")
    with c3:
        st.metric("Total Upvotes", "112", "On 🔥")
    with c4:
        consis = min(100, int((user['current_streak']/30)*100)) + 20
        st.metric("Consistency", f"{consis}%", "+5% MoM")
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Mock data for charts
    months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar']
    hrs = [12, 15, 10, 22, 18, user['total_hours'] + 5]
    
    df_monthly = pd.DataFrame({"Month": months, "Hours": hrs})
    fig_monthly = px.bar(df_monthly, x="Month", y="Hours", title="Monthly Practice Hours",
                         color_discrete_sequence=['#7F5AF0'])
    fig_monthly.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", 
        paper_bgcolor="rgba(0,0,0,0)", 
        font_color="white",
        title_font_size=20,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    c_chart1, c_chart2 = st.columns(2)
    
    with c_chart1:
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        vals = [1, 1, 0, 1, 1, 1, 1]
        df_weekly = pd.DataFrame({"Day": days, "Practiced": vals})
        fig_week = px.bar(df_weekly, x="Day", y="Practiced", title="Weekly Practice Days",
                          color_discrete_sequence=['#2CB67D'])
        fig_week.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            font_color="white",
            title_font_size=16
        )
        st.plotly_chart(fig_week, use_container_width=True)
        
    with c_chart2:
        dates = pd.date_range(end=datetime.today(), periods=14)
        eng = [random.randint(10, 50) for _ in range(14)]
        df_line = pd.DataFrame({"Date": dates, "Engagement": eng})
        fig_line = px.line(df_line, x="Date", y="Engagement", title="Engagement Over Time", 
                           color_discrete_sequence=['#e056fd'])
        fig_line.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            font_color="white",
            title_font_size=16
        )
        st.plotly_chart(fig_line, use_container_width=True)
