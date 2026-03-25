import streamlit as st
import db
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

def render():
    st.markdown("<h2 style='margin-bottom: 25px;'>Performance Hub 📊</h2>", unsafe_allow_html=True)
    
    user = db.get_user_by_id(st.session_state['user_id'])
    
    total_hours = float(user.get('total_hours') or 0)
    highest_streak = int(user.get('highest_streak') or 0)
    current_streak = int(user.get('current_streak') or 0)

    practices = db.run_query("SELECT duration_minutes, created_at, upvotes FROM practices WHERE user_id = ?", (st.session_state['user_id'],))
    
    total_upvotes = sum((p.get('upvotes') or 0) for p in practices) if practices else 0
    
    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Hours", f"{round(total_hours, 1)}h")
    with c2:
        st.metric("Highest Streak", f"{highest_streak} Days")
    with c3:
        st.metric("Total Upvotes", f"{total_upvotes}")
    with c4:
        consis = min(100, int((current_streak / max(1, 30)) * 100))
        st.metric("Consistency (30 Days)", f"{consis}%")
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Process charts dynamically
    today_dt = pd.Timestamp.now()
    months = [(today_dt - pd.DateOffset(months=i)).strftime('%b') for i in range(5, -1, -1)]
    hrs = [0] * len(months)
    
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    vals = [0] * 7
    
    dates = pd.date_range(end=datetime.today(), periods=14)
    eng = [0] * 14
    
    if practices:
        df = pd.DataFrame(practices)
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        df = df.dropna(subset=['created_at'])
        
        df['month'] = df['created_at'].dt.strftime('%b')
        df['day'] = df['created_at'].dt.strftime('%a')
        df['date'] = df['created_at'].dt.date
        
        # Monthly Hours
        monthly_df = df.groupby('month')['duration_minutes'].sum() / 60.0
        hrs = [monthly_df.get(m, 0.0) for m in months]
        
        # Weekly Duration (Minutes) Instead of just "days"
        weekly_df = df[df['created_at'] >= pd.Timestamp.now() - pd.Timedelta(days=7)]
        weekly_group = weekly_df.groupby('day')['duration_minutes'].sum()
        vals = [weekly_group.get(d, 0) for d in days]
        
        # Engagement
        eng_df = df.groupby('date')['duration_minutes'].sum()
        eng = [eng_df.get(d.date(), 0) for d in dates]

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
        df_weekly = pd.DataFrame({"Day": days, "Minutes": vals})
        fig_week = px.bar(df_weekly, x="Day", y="Minutes", title="Weekly Practice Minutes",
                          color_discrete_sequence=['#2CB67D'])
        fig_week.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            font_color="white",
            title_font_size=16
        )
        st.plotly_chart(fig_week, use_container_width=True)
        
    with c_chart2:
        df_line = pd.DataFrame({"Date": dates, "Engagement (Mins)": eng})
        fig_line = px.line(df_line, x="Date", y="Engagement (Mins)", title="Engagement Over Time", 
                           color_discrete_sequence=['#e056fd'])
        fig_line.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            font_color="white",
            title_font_size=16
        )
        st.plotly_chart(fig_line, use_container_width=True)
