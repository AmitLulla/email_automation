import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import chromedriver_autoinstaller
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
from pyppeteer import launch


async def send_emails(df, email_subject, email_template, email_ids, userId, userPass):
    # Initialize Pyppeteer browser
    browser = await launch(headless=False, args=['--disable-dev-shm-usage', '--no-sandbox', '--enable-chrome-browser-cloud-management'])
    page = await browser.newPage()
    await page.goto("https://mail.google.com")

    # Enter email
    await page.waitForSelector("#identifierId")
    await page.type("#identifierId", userId)
    await page.keyboard.press('Enter')

    # Wait for password field
    await page.waitForXPath("//input[@name='password']")
    await page.type("input[name='password']", userPass)
    await page.keyboard.press('Enter')

    # Wait for user to log in and handle 2FA
    wait_time = 0
    while wait_time < 300:  # 180 seconds = 3 minutes
        current_url = page.url
        if current_url.startswith("https://mail.google.com/mail/u/0/"):
            print("True in URL")
            break
        else:
            await asyncio.sleep(10)  # Wait for 10 seconds
            wait_time += 10

    if wait_time >= 180 and not current_url.startswith("https://mail.google.com/mail/u/0/"):
        print("Error: Timed out waiting for user to log in.")

    # Read data from the file and send emails
    for index, row in df.iterrows():
        # Initialize an empty dictionary to store column names and values
        kwargs = {}
        
        # Iterate over each column dynamically
        for column_name, value in row.items():
            # Add column name and value to the kwargs dictionary
            kwargs[column_name] = value
        
        # Compose email dynamically
        subject = email_subject.format(**kwargs)
        body = email_template.format(**kwargs)
        email = email_ids.format(**kwargs)

        # Open compose window
        # Compose the email
        await page.waitForXPath("//div[text()='Compose']")
        await page.click("//div[text()='Compose']")
        await asyncio.sleep(2)  # Wait for compose window to open

        await page.waitForSelector("input[aria-label='To recipients']")
        await page.type("input[aria-label='To recipients']", email)

        await page.waitForSelector("input[name='subjectbox']")
        await page.type("input[name='subjectbox']", subject)

        await page.waitForSelector("div[aria-label='Message Body']")
        await page.type("div[aria-label='Message Body']", body)

        # Send the email using "Ctrl+Enter" shortcut
        await page.keyboard.down('Control')
        await page.keyboard.press('Enter')
        await page.keyboard.up('Control')
        await asyncio.sleep(2)  # Wait for email to be sent

    # Close the browser window
    await browser.close()



def main():
    st.title("Email Automation")
    col1, col2 = st.columns(2)
    with col1:
        userId = st.text_input("Enter Gmail ID:")
    with col2:        
        userPass = st.text_input("Enter Gmail Password:", type = "password")

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
                email_list = st.text_input("Enter Receipetients")
                email_template = st.text_area("Email Template")
                headers = [f"{{{header}}}" for header in df.columns.tolist()]
                st.write("File Binders:")
                st.write(headers)
                
                if not email_template:
                    st.warning("Please provide an email template.")
                    
                if st.button("Send Emails"):
                    # To run the async function in a synchronous environment
                    asyncio.get_event_loop().run_until_complete(send_emails(df, email_subject, email_template, email_ids, userId, userPass))
                    st.success("Emails sent successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please upload a file first.")
    else:
        st.warning("Please enter your login credentials first.")

if __name__ == "__main__":
    main()
