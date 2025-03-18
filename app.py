import streamlit as st
import pandas as pd
import numpy as np
import openpyxl as xl
import smtplib
from email.mime.text import MIMEText


def load_account_details(file_path):
    """Loads account details from an Excel file into a Pandas DataFrame."""
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        st.error(f"Error: File not found at {file_path}")
        return None

def get_currencies_for_account(df, account_name):
    """Returns a list of currencies associated with a given account name."""
    if df is None or account_name == "":
        return [""]
    return [""] + list(df[df['ACCOUNT NAME'] == account_name]['CURRENCIES'].unique())

def get_account_details(df, account_name=None, currency=None):
    """Retrieves account details based on account name and/or currency."""
    if df is None:
        return None

    query = []
    if account_name and 'ACCOUNT NAME' in df.columns:
        query.append(f"`ACCOUNT NAME` == '{account_name}'")
    if currency and 'CURRENCIES' in df.columns:
        query.append(f"`CURRENCIES` == '{currency}'")

    if not query:
        st.warning("Please select an Account Name and Currency.")
        return None

    query_string = " and ".join(query)
    try:
        filtered_df = df.query(query_string)
        if not filtered_df.empty:
            return filtered_df.iloc[0].to_dict()  # Return the first matching row as a dictionary
        else:
            st.warning("No matching account details found.")
            return None
    except pd.core.computation.ops.UndefinedVariableError as e:
        st.error(f"Error: Column '{e.variable}' not found in the Excel file.")
        return None
    except Exception as e:
        st.error(f"An error occurred during data retrieval: {e}")
        return None

def format_account_details(details):
    """Formats the retrieved account details for communication."""
    if details:
        formatted_text = "Account Details:\n"
        for key, value in details.items():
            formatted_text += f"- {key}: {value}\n"
        return formatted_text
    return "No account details to display."

def send_email(recipient_email, subject, body, sender_email, sender_password):
    """Sends an email with the provided details."""
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        st.success(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        st.error(f"Error sending email: {e}")

def main():
    st.title("Automated Account Details Retrieval")

    st.sidebar.header("Configuration")
    excel_file_path = st.sidebar.file_uploader("Upload Excel File (account concession sheet.xlsx)", type=["xlsx", "xls"])

    if excel_file_path is not None:
        df = load_account_details(excel_file_path)

        if df is not None:
            st.sidebar.header("Filter Options")
            account_names = [""] + list(df['ACCOUNT NAME'].unique()) if 'ACCOUNT NAME' in df.columns else ["No ACCOUNT NAME Column"]
            selected_account_name = st.sidebar.selectbox("Select Account Name", account_names)

            available_currencies = get_currencies_for_account(df, selected_account_name)
            selected_currency = st.sidebar.selectbox("Select Currency", available_currencies)

            st.sidebar.header("Email Options")
            send_email_option = st.sidebar.checkbox("Send Account Number via Email")
            recipient_email = st.sidebar.text_input("Recipient Email")
            sender_email = st.sidebar.text_input("Your Email Address")
            sender_password = st.sidebar.text_input("Your Email Password", type="password")

            if st.button("Retrieve Account Details"):
                details = get_account_details(df, selected_account_name, selected_currency)
                formatted_details = format_account_details(details)
                st.subheader("Retrieved Account Details:")
                st.code(formatted_details, language="text")

                if details and send_email_option and recipient_email and sender_email and sender_password:
                    account_number = details.get('ACCOUNT NUMBER', 'N/A')
                    email_subject = f"Account Details for {selected_account_name} ({selected_currency})"
                    email_body = f"Please find the account number below:\n\nAccount Name: {selected_account_name}\nAccount Number: {account_number}\nCurrency: {selected_currency}\n\nBank: {details.get('BANK', 'N/A')}"
                    send_email(recipient_email, email_subject, email_body, sender_email, sender_password)
                elif send_email_option and not (recipient_email and sender_email and sender_password):
                    st.warning("Please provide recipient email, your email address, and password to send an email.")

    else:
        st.info("Please upload the Excel file named 'account concession sheet.xlsx' containing account details.")

if __name__ == "__main__":
    main()
