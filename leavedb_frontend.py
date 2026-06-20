import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Leave Management", layout="wide")

# ---------------- PREMIUM CSS ----------------
st.markdown("""
<style>
.kpi {
    padding: 20px;
    border-radius: 12px;
    color: white;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
}
.kpi-total { background: #007bff; }
.kpi-pending { background: #ffc107; color:black; }
.kpi-approved { background: #28a745; }
.kpi-rejected { background: #dc3545; }

.approve-btn button {
    background-color: #28a745 !important;
    color: white !important;
}
.reject-btn button {
    background-color: #dc3545 !important;
    color: white !important;
}

.badge {
    padding: 5px 10px;
    border-radius: 8px;
    color: white;
    font-weight: bold;
}
.pending { background-color: #ffc107; color:black; }
.approved { background-color: #28a745; }
.rejected { background-color: #dc3545; }

.card {
    padding: 15px;
    border-radius: 10px;
    background: #f8f9fa;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- REGISTER ----------------
if choice == "Register":
    st.title("Register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["employee", "manager"])

    if st.button("Register"):
        res = requests.post(f"{API}/register", json={
            "username": username,
            "password": password,
            "role": role
        })
        st.success(res.text)

# ---------------- LOGIN ----------------
elif choice == "Login":

    if not st.session_state.user:
        st.title("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            res = requests.post(f"{API}/login", json={
                "username": username,
                "password": password
            })

            if res.status_code == 200:
                st.session_state.user = res.json()
                st.rerun()
            else:
                st.error("Invalid login")

    else:
        user = st.session_state.user

        st.sidebar.success(f"{user['username']} ({user['role']})")

        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.rerun()

        # ---------------- FETCH DATA ----------------
        res = requests.get(f"{API}/leaves")

        if res.status_code == 200:
            try:
                data = res.json()
            except:
                data = []
        else:
            data = []

        df = pd.DataFrame(data)

        # ---------------- EMPLOYEE ----------------
        if user["role"] == "employee":
            st.title("🧑 Employee Dashboard")

            st.subheader("Apply Leave")

            reason = st.text_area("Reason")
            col1, col2 = st.columns(2)
            start = col1.date_input("Start Date")
            end = col2.date_input("End Date")

            if st.button("Apply Leave"):
                requests.post(f"{API}/leave", json={
                    "employee_name": user["username"],
                    "reason": reason,
                    "start_date": str(start),
                    "end_date": str(end)
                })
                st.success("Leave applied")
                st.rerun()

            st.subheader("My Leaves")

            if not df.empty:
                my_df = df[df["employee_name"] == user["username"]]

                for _, row in my_df.iterrows():
                    st.markdown(f"""
                    <div class="card">
                    <b>ID:</b> {row['id']} <br>
                    <b>Reason:</b> {row['reason']} <br>
                    <b>Dates:</b> {row['start_date']} → {row['end_date']} <br>
                    <b>Status:</b> <span class="badge {row['status'].lower()}">{row['status']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No records")

        # ---------------- MANAGER ----------------
        else:
            st.title("🧑‍💼 Manager Dashboard")

            if not df.empty:

                # KPI
                total = len(df)
                pending = len(df[df["status"] == "Pending"])
                approved = len(df[df["status"] == "Approved"])
                rejected = len(df[df["status"] == "Rejected"])

                k1, k2, k3, k4 = st.columns(4)

                k1.markdown(f'<div class="kpi kpi-total">Total<br>{total}</div>', unsafe_allow_html=True)
                k2.markdown(f'<div class="kpi kpi-pending">Pending<br>{pending}</div>', unsafe_allow_html=True)
                k3.markdown(f'<div class="kpi kpi-approved">Approved<br>{approved}</div>', unsafe_allow_html=True)
                k4.markdown(f'<div class="kpi kpi-rejected">Rejected<br>{rejected}</div>', unsafe_allow_html=True)

                st.divider()

                # FILTER
                employees = df["employee_name"].unique()
                selected = st.selectbox("Filter by Employee", ["All"] + list(employees))

                if selected != "All":
                    df = df[df["employee_name"] == selected]

                # TABLE
                for _, row in df.iterrows():
                    cols = st.columns([1,2,2,3,2,4])

                    cols[0].write(row["id"])
                    cols[1].write(row["employee_name"])
                    cols[2].write(row["reason"])
                    cols[3].write(f"{row['start_date']} → {row['end_date']}")

                    status_html = f'<span class="badge {row["status"].lower()}">{row["status"]}</span>'
                    cols[4].markdown(status_html, unsafe_allow_html=True)

                    if row["status"] == "Pending":
                        with cols[5]:
                            c1, c2 = st.columns(2)

                            # ✅ UPDATED BUTTONS HERE
                            with c1:
                                st.markdown('<div class="approve-btn">', unsafe_allow_html=True)
                                if st.button("Approve", key=f"approve_{row['id']}"):
                                    requests.put(
                                        f"{API}/leave/{row['id']}",
                                        params={"status": "Approved"}
                                    )
                                    st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)

                            with c2:
                                st.markdown('<div class="reject-btn">', unsafe_allow_html=True)
                                if st.button("Reject", key=f"reject_{row['id']}"):
                                    requests.put(
                                        f"{API}/leave/{row['id']}",
                                        params={"status": "Rejected"}
                                    )
                                    st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)

                    else:
                        cols[5].write("✔ Done")

                # CHARTS
                st.subheader("📊 Analytics")

                col1, col2 = st.columns(2)

                with col1:
                    fig1 = px.pie(df, names="status", title="Status Distribution")
                    st.plotly_chart(fig1, use_container_width=True)

                with col2:
                    fig2 = px.bar(df, x="employee_name", title="Leaves per Employee")
                    st.plotly_chart(fig2, use_container_width=True)

            else:
                st.info("No records found")