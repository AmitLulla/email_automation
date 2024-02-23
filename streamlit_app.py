import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time


def send_emails(df, email_subject, email_template, email_ids, userId, userPass):
    js_code = """
        window.addEventListener('load', function() {
            // Page is fully loaded, proceed with scraping
            window.loaded = true;
        });
        """
    # Initialize Chrome WebDriver
    options = Options()
    options.headless = True
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    try:
        # Use webdriver_manager to ensure ChromeDriver is up-to-date
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        

        driver.get("https://mail.google.com")
    
        driver.execute_script(js_code)
         # Enter email
        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "identifierId"))
        )
        email_field.send_keys(userId)
        email_field.send_keys(Keys.RETURN)
    
        # Wait for password field
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='Passwd']"))
        )
        password_field.send_keys(userPass)
        password_field.send_keys(Keys.RETURN)
        # Wait for user to log in and handle 2FA
    
        wait_time = 0
        while wait_time < 300:  # 180 seconds = 3 minutes
            current_url = driver.current_url
            if current_url.startswith("https://mail.google.com/mail/u/0/"):
                print("True in URL")
                driver.execute_script(js_code)
                break
            else:
                time.sleep(10)  # Wait for 10 seconds
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
            compose_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//div[text()='Compose']"))
            )
            compose_button.click()
            time.sleep(2)  # Wait for compose window to open
    
            to_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@aria-label='To recipients']"))
            )
            to_field.send_keys(email)
    
            subject_field = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@name='subjectbox']"))
            )
            subject_field.send_keys(subject)
    
            body_field = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@aria-label='Message Body']"))
            )
            body_field.send_keys(body)
    
            # Send the email using "Ctrl+Enter" shortcut
            body_field.send_keys(Keys.CONTROL, Keys.ENTER)
            time.sleep(2)  # Wait for email to be sent
    
        # Close the browser window
        driver.quit()
    except Exception as e:
        st.error(f"Error occurred: {e}")
        st.stop()



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
