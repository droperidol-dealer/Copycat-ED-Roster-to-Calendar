import pandas as pd
import streamlit as st

st.set_page_config(page_title="Roster Converter", page_icon="📅")
st.title("📅 ED Roster to Google Calendar")

uploaded_file = st.file_uploader("Upload Roster (Excel)", type=["xlsx"])

if uploaded_file:
    # Based on your image: Dates are Row 6 (index 5), Names are Col D (index 3)
    df = pd.read_excel(uploaded_file, header=3)
    name_col = df.columns[3]
    date_cols = df.columns[4:]
    
    staff_names = df[name_col].dropna().unique()
    target_name = st.selectbox("Select your name:", staff_names)
    
    if target_name:
        user_row = df[df[name_col] == target_name]
        events = []
        
        for date_col in date_cols:
            shift_code = user_row[date_col].values[0]
            if pd.notna(shift_code) and str(shift_code).strip().upper() != 'X':
                events.append({
                    "Subject": f"Shift: {shift_code}",
                    "Start Date": date_col,
                    "All Day Event": "True"
                })
        
        if events:
            output_df = pd.DataFrame(events)
            st.dataframe(output_df)
            csv = output_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "roster.csv", "text/csv")
