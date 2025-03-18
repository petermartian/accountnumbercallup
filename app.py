import streamlit as st
import pandas as pd
import numpy as np


# --- Nigerian Tax and Deduction Rules (Based on Image Analysis - Simplified) ---
# **IMPORTANT:** These are based on a snapshot and might not be fully accurate or up-to-date.
# Refer to official FIRS guidelines for precise calculations.
PERSONAL_ALLOWANCE = 200000  # Assuming a value based on common structures
TAX_RATES = {
    300000: 0.07,
    300000: 0.11,  # Next 300,000
    500000: 0.15,  # Next 500,000
    500000: 0.19,  # Next 500,000
    1600000: 0.21, # Next 1,600,000
    None: 0.24,     # Above 3,200,000
}
PENSION_RATE_EMPLOYEE = 0.08  # Assuming standard rate if applicable
NHF_RATE = 0.025  # Assuming standard rate if applicable
NHIS_RATE = 0.05   # Assuming a hypothetical rate for NHIS

def calculate_paye(annual_income):
    taxable_income = max(0, annual_income - PERSONAL_ALLOWANCE)
    tax_payable = 0
    bracket_start = 0
    for limit, rate in TAX_RATES.items():
        bracket_end = limit if limit is not None else float('inf')
        taxable_in_bracket = max(0, min(taxable_income, bracket_end) - bracket_start)
        tax_payable += taxable_in_bracket * rate
        bracket_start = bracket_end
        if taxable_income <= bracket_end:
            break
    return tax_payable / 12  # Monthly PAYE

def calculate_salary(basic_salary, housing_allowance, transport_allowance, other_allowances=0, include_pension=False, include_nhf=False, include_nhis=False):
    gross_salary = basic_salary + housing_allowance + transport_allowance + other_allowances
    annual_basic_salary = basic_salary * 12

    paye = calculate_paye(annual_basic_salary)

    total_deductions = paye
    pension_employee = 0
    if include_pension:
        pension_employee = gross_salary * PENSION_RATE_EMPLOYEE
        total_deductions += pension_employee

    nhf = 0
    if include_nhf:
        nhf = gross_salary * NHF_RATE
        total_deductions += nhf

    nhis = 0
    if include_nhis:
        nhis = gross_salary * NHIS_RATE
        total_deductions += nhis

    net_salary = gross_salary - total_deductions

    return gross_salary, paye, pension_employee, nhf, nhis, total_deductions, net_salary

def main():
    st.title("Nigerian Salary Calculator")

    tab1, tab2, tab3 = st.tabs(["Employee Info", "Salary Input", "Calculation Result"])

    with st.sidebar:
        st.header("Optional Deductions")
        include_pension = st.checkbox("Include Pension (8%)", value=False)
        include_nhf = st.checkbox("Include NHF (2.5%)", value=False)
        include_nhis = st.checkbox("Include NHIS (5%)", value=False)

    with tab1:
        st.header("Employee Information")
        employee_name = st.text_input("Employee Name")
        st.session_state['employee_name'] = employee_name

    with tab2:
        st.header("Enter Your Salary Details (Monthly in NGN)")
        basic_salary = st.number_input("Basic Salary", min_value=0, value=375000, step=1000)
        housing_allowance = st.number_input("Housing Allowance", min_value=0, value=187500, step=1000)
        transport_allowance = st.number_input("Transport Allowance", min_value=0, value=187500, step=1000)
        other_allowances = st.number_input("Other Allowances", min_value=0, value=0, step=1000)

        if st.button("Calculate"):
            gross_salary, paye, pension_employee, nhf, nhis, total_deductions, net_salary = calculate_salary(
                basic_salary, housing_allowance, transport_allowance, other_allowances, include_pension, include_nhf, include_nhis
            )
            st.session_state['results'] = {
                'basic_salary': basic_salary,
                'housing_allowance': housing_allowance,
                'transport_allowance': transport_allowance,
                'other_allowances': other_allowances,
                'gross_salary': gross_salary,
                'paye': paye,
                'pension_employee': pension_employee,
                'nhf': nhf,
                'nhis': nhis,
                'total_deductions': total_deductions,
                'net_salary': net_salary,
            }

    with tab3:
        st.header("Your Result")
        if 'results' in st.session_state and 'employee_name' in st.session_state:
            results = st.session_state['results']
            employee_name = st.session_state['employee_name']
            st.subheader(f"Salary Breakdown for: {employee_name}")
            st.subheader("Monthly Breakdown (NGN)")
            st.write(f"**Basic Salary:** {results['basic_salary']:,}")
            st.write(f"**Housing Allowance:** {results['housing_allowance']:,}")
            st.write(f"**Transport Allowance:** {results['transport_allowance']:,}")
            st.write(f"**Other Allowances:** {results['other_allowances']:,}")
            st.write(f"**Total Pay:** {results['gross_salary']:,}")
            st.write("--- Deductions ---")
            st.write(f"**PAYE Tax:** {results['paye']:,.2f}")
            if results['pension_employee'] > 0:
                st.write(f"**Pension Contribution (8%):** {results['pension_employee']:,.2f}")
            if results['nhf'] > 0:
                st.write(f"**NHF Contribution (2.5%):** {results['nhf']:,.2f}")
            if results['nhis'] > 0:
                st.write(f"**NHIS Contribution (5%):** {results['nhis']:,.2f}")
            st.write(f"**Total Deductions:** {results['total_deductions']:,.2f}")
            st.write(f"**Take-Home Pay:** {results['net_salary']:,.2f}")

            st.subheader("Yearly Breakdown (NGN)")
            st.write(f"**Basic Salary:** {results['basic_salary'] * 12:_,}")
            st.write(f"**Housing Allowance:** {results['housing_allowance'] * 12:_,}")
            st.write(f"**Transport Allowance:** {results['transport_allowance'] * 12:_,}")
            st.write(f"**Other Allowances:** {results['other_allowances'] * 12:_,}")
            st.write(f"**Total Pay:** {results['gross_salary'] * 12:_,}")
            st.write(f"**PAYE Tax:** {results['paye'] * 12:_,.2f}")
            total_yearly_deductions = results['total_deductions'] * 12
            st.write(f"**Total Deductions:** {total_yearly_deductions:_,.2f}")
            st.write(f"**Take-Home Pay:** {results['net_salary'] * 12:_,.2f}")

            chargeable_income = (results['gross_salary'] * 12 - PERSONAL_ALLOWANCE) / 12
            st.write(f"**Chargeable Income (Monthly - Approx.):** {chargeable_income:_,.2f}")
            effective_tax_rate = (results['paye'] * 12) / (results['gross_salary'] * 12) * 100 if (results['gross_salary'] * 12) > 0 else 0
            st.write(f"**Effective Tax Rate:** {effective_tax_rate:.2f}%")

        else:
            st.info("Enter employee and salary details in the respective tabs and click 'Calculate'.")

if __name__ == "__main__":
    main()
