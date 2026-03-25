import streamlit as st
import sqlite3
import db
from passlib.hash import pbkdf2_sha256

# ---------------- PASSWORD UTILS ----------------
def hash_password(password):
    return pbkdf2_sha256.hash(password)

def verify_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)

# ---------------- LOGOUT ----------------
def logout_user():
    st.session_state.user_id = None
    st.session_state.username = ""
    st.session_state.page = "dashboard"
    st.rerun()

# ---------------- AUTH PAGE ----------------
def show_auth_page():
    st.markdown('<h1 style="text-align: center; color: #e2e8f0;">Trackora 🎵</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #a0aec0;">Your Social Music Habit Tracker</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        # ---------------- LOGIN ----------------
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)

                if submitted:
                    username = username.strip()
                    user = db.get_user_by_username(username)

                    if user and verify_password(password, user['password_hash']):
                        st.session_state.user_id = user['id']
                        st.session_state.username = user['username']
                        st.session_state.page = "dashboard"
                        st.success("Login successful")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

        # ---------------- SIGNUP ----------------
        with tab2:
            with st.form("signup_form"):
                new_user = st.text_input("Username")
                new_pass = st.text_input("Password", type="password")
                instrument = st.selectbox("Primary Instrument", ["Piano", "Guitar", "Violin", "Drums", "Vocals", "Other"])
                region = st.text_input("Region", placeholder="e.g. Asia")
                genre = st.selectbox("Favorite Genre", ["Classical", "Rock", "Jazz", "Pop", "Electronic", "Other"])
                language = st.selectbox("Preferred Language", ["English", "Spanish", "French", "Other"])

                submitted = st.form_submit_button("Sign Up", use_container_width=True)

                if submitted:
                    new_user = new_user.strip()

                    if len(new_user) < 3:
                        st.error("Username must be at least 3 characters.")
                        return

                    if len(new_pass) < 3:
                        st.error("Password must be at least 3 characters.")
                        return

                    try:
                        db.create_user(
                            new_user,
                            hash_password(new_pass),
                            instrument,
                            region,
                            genre,
                            language
                        )
                        st.success("Account created! Please switch to Login.")

                    except sqlite3.IntegrityError:
                        st.error("Username already exists!")

                    except Exception as e:
                        st.error(f"Error: {e}")