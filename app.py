import pandas as pd
import streamlit as st

st.set_page_config(page_title="ED Roster Converter", page_icon="📅", layout="wide")

st.title("📅 ED Roster to Calendar")
st.info("Since every hospital roster is slightly different, let's make sure we're reading yours correctly.")

uploaded_file = st.file_uploader("Upload Roster (Excel)", type=["xlsx"])

if uploaded_file:
    # Load the sheet without a header first to see everything
    df_raw = pd.read_excel(uploaded_file, header=None)
    
    st.write("### 1. Identify your Roster Layout")
    st.write("Take a look at the table below. Which **Row Number** contains the dates (1, 2, 3...)?")
    st.dataframe(df_raw.head(15)) # Show first 15 rows for reference

    # User inputs for the layout
    col1, col2 = st.columns(2)
    with col1:
        date_row_num = st.number_input("Enter the Row Number for Dates:", min_value=1, value=6)
    with col2:
        name_col_num = st.number_input("Enter the Column Letter/Number for Names (A=1, B=2, C=3, D=4):", min_value=1, value=4)

    # Re-process with the user's settings
    # Subtract 1 because computers start counting at 0
    header_idx = int(date_row_num) - 1
    name_col_idx = int(name_col_num) - 1

    if st.button("Extract My Shifts"):
        # Reload with proper header
        df = pd.read_excel(uploaded_file, header=header_idx)
        
        # Identify name column and date columns
        try:
            name_col = df.columns[name_col_idx]
            date_cols = df.columns[name_col_idx + 1:]
            
            # Clean up names (remove empty ones)
            staff_names = df[name_col].dropna().unique()
            target_name = st.selectbox("Select your name:", staff_names)
            
            if target_name:
                user_row = df[df[name_col] == target_name]
                events = []
                
                for date_col in date_cols:
                    shift_code = user_row[date_col].values[0]
                    # Only grab actual shift codes (skip X, empty, or nan)
                    if pd.notna(shift_code) and str(shift_code).strip().upper() not in ['X', 'OFF', '']:
                        events.append({
                            "Subject": f"Shift: {shift_code}",
                            "Start Date": date_col,
                            "All Day Event": "True"
                        })
                
                if events:
                    output_df = pd.DataFrame(events)
                    st.success(f"Successfully found {len(events)} shifts for {target_name}!")
                    st.dataframe(output_df)
                    
                    csv = output_df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Corrected CSV", csv, f"{target_name}_roster.csv", "text/csv")
                else:
                    st.warning("No shifts found for that name. Check if the Row/Column numbers are correct.")
        except Exception as e:
            st.error(f"Error: {e}. Please double-check the Row and Column numbers above.")
