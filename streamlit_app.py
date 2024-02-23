from pyppeteer import launch
import pandas as pd
import streamlit as st
import time

def send_emails(df, email_subject, email_template, email_ids, userId, userPass):
    browser = launch(headless=False, args=['--disable-dev-shm-usage', '--no-sandbox', '--enable-chrome-browser-cloud-management'])
    page = browser.newPage()
    page.goto("https://mail.google.com")

    # Enter email
    page.waitForSelector("#identifierId")
    page.type("#identifierId", userId)
    page.keyboard.press('Enter')

    # Wait for password field
    page.waitForXPath("//input[@name='password']")
    page.type("input[name='password']", userPass)
    page.keyboard.press('Enter')

    # Wait for user to log in and handle 2FA
    wait_time = 0
    while wait_time < 300:  # 180 seconds = 3 minutes
        current_url = page.url
        if current_url.startswith("https://mail.google.com/mail/u/0/"):
            print("True in URL")
            break
        else:
            time.sleep(10)  # Wait for 10 seconds
            wait_time += 10

    if wait_time >= 180 and not current_url.startswith("https://mail.google.com/mail/u/0/"):
        print("Error: Timed out waiting for user to log in.")

    # Read data from the file and send emails
    for index, row in df.iterrows():
        kwargs = {}
        for column_name, value in row.items():
            kwargs[column_name] = value

        subject = email_subject.format(**kwargs)
        body = email_template.format(**kwargs)
        email = email_ids.format(**kwargs)

        page.waitForXPath("//div[text()='Compose']")
        page.click("//div[text()='Compose']")
        time.sleep(2)

        page.waitForSelector("input[aria-label='To recipients']")
        page.type("input[aria-label='To recipients']", email)

        page.waitForSelector("input[name='subjectbox']")
        page.type("input[name='subjectbox']", subject)

        page.waitForSelector("div[aria-label='Message Body']")
        page.type("div[aria-label='Message Body']", body)

        # Send the email using "Ctrl+Enter" shortcut
        page.keyboard.down('Control')
        page.keyboard.press('Enter')
        page.keyboard.up('Control')
        time.sleep(2)

    browser.close()

def main():
    st.title("Email Automation")
    col1, col2 = st.columns(2)
    with col1:
        userId = st.text_input("Enter Gmail ID:")
    with col2:        
        userPass = st.text_input("Enter Gmail Password:", type="password")

    if userPass and userId:
        uploaded_file = st.file_uploader("Upload File", type=["xlsx", "csv"])
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('xlsx'):
                    xls = pd.ExcelFile(uploaded_file)
                    sheet_names = xls.sheet_names
                    selected_sheet = st.selectbox("Select a worksheet:", sheet_names)
                    df = pd.read_excel(xls, sheet_name=selected_sheet)
                else:
                    df = pd.read_csv(uploaded_file)
                
                email_subject = st.text_input("Email Subject")
                email_list = st.text_input("Enter Recipients")
                email_template = st.text_area("Email Template")
                headers = [f"{{{header}}}" for header in df.columns.tolist()]
                st.write("File Binders:")
                st.write(headers)
                
                if not email_template:
                    st.warning("Please provide an email template.")
                    
                if st.button("Send Emails"):
                    send_emails(df, email_subject, email_template, email_list, userId, userPass)
                    st.success("Emails sent successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please upload a file first.")
    else:
        st.warning("Please enter your login credentials first.")

if __name__ == "__main__":
    main()
