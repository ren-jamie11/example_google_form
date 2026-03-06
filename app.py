import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# ── Google Sheets setup ────────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_sheet():
    """Authenticate and return the target worksheet."""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open(st.secrets["sheet"]["name"]).sheet1
    return sheet


def ensure_header(sheet):
    """Add header row if the sheet is empty."""
    if sheet.row_count == 0 or sheet.cell(1, 1).value != "Name":
        sheet.insert_row(["Name", "Age", "Timestamp"], index=1)


def append_row(sheet, name: str, age: int):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([name, age, timestamp])


def load_as_dataframe(sheet) -> pd.DataFrame:
    records = sheet.get_all_records()
    return pd.DataFrame(records)


# ── UI ─────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="User Info Form", page_icon="📋")
st.title("📋 User Info Form")

with st.form("user_form"):
    name = st.text_input("Enter name")
    age  = st.number_input("Enter age", min_value=0, max_value=130, step=1)
    submitted = st.form_submit_button("Submit")

if submitted:
    if not name.strip():
        st.error("Please enter a name.")
    else:
        try:
            sheet = get_sheet()
            ensure_header(sheet)
            append_row(sheet, name.strip(), int(age))
            st.success(f"✅ Saved: **{name}**, age **{age}**")
        except Exception as e:
            st.error(f"Failed to save: {e}")

# ── Optional: preview stored data ─────────────────────────────────────────────
st.divider()
if st.button("🔍 Preview stored data"):
    try:
        sheet = get_sheet()
        df = load_as_dataframe(sheet)
        if df.empty:
            st.info("No submissions yet.")
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load data: {e}")
