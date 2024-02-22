import streamlit as st
from email_automation import send_emails
import pandas as pd

def main():
    st.title("Email Automation")

    uploaded_file = st.file_uploader("Upload File", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('xlsx'):
                xls = pd.ExcelFile(uploaded_file)
                sheet_names = xls.sheet_names
                selected_sheet = st.selectbox("Select a worksheet:", sheet_names)
                df = pd.read_excel(xls, sheet_name=selected_sheet)
            else:
                df = pd.read_csv(uploaded_file)
            email_ids = st.text_input("Map Email Ids")
            email_subject = st.text_input("Email Subject")
            email_template = st.text_area("Email Template")
            headers = [f"{{{header}}}" for header in df.columns.tolist()]
            st.write("File Binders:")
            st.write(headers)
            if not email_template:
                st.warning("Please provide an email template.")
                
            if st.button("Send Emails"):
                send_emails(df, email_subject, email_template, email_ids)
                st.success("Emails sent successfully!")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please upload a file first.")

if __name__ == "__main__":
    main()