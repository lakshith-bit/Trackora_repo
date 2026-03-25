import streamlit as st
import db

def render():
    st.markdown("<h2 style='margin-bottom: 25px;'>Practice Hub 🎸</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="custom-card" style="border-top: 4px solid #2CB67D;">
            <h3 style="margin-top:0;">⏱️ Practice Session</h3>
        </div>
        """, unsafe_allow_html=True)
        
        task = db.get_or_create_daily_task(st.session_state['user_id'])
        st.info(f"**Today's Mission:** {task['task_desc']}", icon="🎯")
        
        dur_inp = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=15)
        
        if 'timer_running' not in st.session_state:
            st.session_state.timer_running = False
            st.session_state.timer_duration = 0
            
        if not st.session_state.timer_running:
            if st.button("▶️ Start Practice Timer", type="primary", use_container_width=True):
                st.session_state.timer_running = True
                st.session_state.timer_duration = dur_inp
                
                # Automatically complete task and log streak immediately for hackathon demo purposes
                db.update_streak(st.session_state['user_id'], dur_inp)
                db.complete_daily_task(st.session_state['user_id'])
                db.update_profile_points(st.session_state['user_id'], 2)  # Bonus XP for starting session
                db.complete_all_group_tasks_for_user(st.session_state['user_id']) # Mark their part in ALL groups!
                st.rerun()
        else:
            import streamlit.components.v1 as components
            st.success("Session Active! Focus on your music.")
            
            components.html(f"""
            <div id="clock" style="font-family: Arial, sans-serif; font-size: 4rem; color: #2CB67D; text-align: center; font-weight: bold; background: #1E2028; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);"></div>
            <script>
            var time = {st.session_state.timer_duration * 60};
            var clock = document.getElementById("clock");
            var timer = setInterval(function() {{
                var m = Math.floor(time / 60);
                var s = time % 60;
                clock.innerHTML = (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
                time--;
                if (time < 0) {{
                    clearInterval(timer);
                    clock.innerHTML = "Done! 🎉";
                }}
            }}, 1000);
            </script>
            """, height=130)
            
            if st.button("⏹️ End Session", use_container_width=True):
                st.session_state.timer_running = False
                st.snow()
                st.rerun()
    with col2:
        st.markdown("""
        <div class="custom-card" style="border-top: 4px solid #7F5AF0;">
            <h3 style="margin-top:0;">🎥 Upload Work</h3>
        </div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Recording", type=["mp4", "mov", "mp3", "wav"])
        if uploaded_file is not None:
            if st.button("📤 Share to Community Feed", use_container_width=True):
                with st.spinner("Uploading and processing your music..."):
                    import os
                    if not os.path.exists("uploads"):
                        os.makedirs("uploads")
                    
                    file_path = f"uploads/{st.session_state['user_id']}_{uploaded_file.name}"
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                        
                    from datetime import datetime
                    db.run_query("INSERT INTO practices (user_id, duration_minutes, created_at, upvotes, file_path) VALUES (?, ?, ?, 0, ?)", (st.session_state['user_id'], 15, datetime.now(), file_path), fetch=False)
                    db.update_profile_points(st.session_state['user_id'], 5) # 5 XP for sharing
                    st.success("Successfully shared your session to the community feed!")
                    st.balloons()
                    st.rerun()

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top: 40px; margin-bottom: 30px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 20px;'>📂 My Upload Gallery</h3>", unsafe_allow_html=True)
    
    my_recs = db.run_query("SELECT * FROM practices WHERE user_id = ? AND file_path IS NOT NULL ORDER BY created_at DESC", (st.session_state['user_id'],))
    
    if not my_recs:
        st.info("You haven't uploaded any media yet.")
    else:
        for i in range(0, len(my_recs), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(my_recs):
                    rec = my_recs[i+j]
                    with cols[j]:
                        st.markdown(f"""
                        <div class="custom-card" style="padding: 15px; margin-bottom: 10px; text-align: center; border-top: 3px solid #686de0;">
                            <p style="color:#e056fd; font-weight:bold; font-size:1.1rem; margin:0;">{rec['duration_minutes']} min Session</p>
                            <p style="color:#a0aec0; font-size:12px; margin:5px 0;">❤️ {rec['upvotes']} upvotes</p>
                        </div>
                        """, unsafe_allow_html=True)
                        try:
                            if rec['file_path'].lower().endswith(('.mp4', '.mov')):
                                st.video(rec['file_path'])
                            elif rec['file_path'].lower().endswith(('.mp3', '.wav')):
                                st.audio(rec['file_path'])
                        except Exception:
                            st.error("Media processing error")
