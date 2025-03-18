import streamlit as st
import pandas as pd
import numpy as np


def load_account_details(file_path):
    """Loads account details from an Excel file into a Pandas DataFrame."""
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        st.error(f"Error: File not found at {file_path}")
        return None

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
        st.warning("Please select an Account Name or Currency.")
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

def main():
    st.title("Automated Account Details Retrieval")

    st.sidebar.header("Configuration")
    excel_file_path = st.sidebar.file_uploader("Upload Excel File (account concession sheet.xlsx)", type=["xlsx", "xls"])

    if excel_file_path is not None:
        df = load_account_details(excel_file_path)

        if df is not None:
            st.sidebar.header("Filter Options")
            account_names = [""] + list(df['ACCOUNT NAME'].unique()) if 'ACCOUNT NAME' in df.columns else ["No ACCOUNT NAME Column"]
            currencies = [""] + list(df['CURRENCIES'].unique()) if 'CURRENCIES' in df.columns else ["No CURRENCIES Column"]

            account_name = st.sidebar.selectbox("Select Account Name", account_names)
            currency = st.sidebar.selectbox("Select Currency", currencies)

            if st.button("Retrieve Account Details"):
                details = get_account_details(df, account_name, currency)
                formatted_details = format_account_details(details)
                st.subheader("Retrieved Account Details:")
                st.code(formatted_details, language="text")
    else:
        st.info("Please upload the Excel file named 'account concession sheet.xlsx' containing account details.")

if __name__ == "__main__":
    main()
