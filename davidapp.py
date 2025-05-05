import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# --- SIP Simulation Function ---
def sip_simulation(monthly_investment, annual_return_rate, years):
    total_invested = monthly_investment * 12 * years
    future_value = 0
    monthly_rate = annual_return_rate / 12 / 100
    months = years * 12
    for i in range(1, months + 1):
        future_value += monthly_investment * (1 + monthly_rate) ** (months - i + 1)
    return total_invested, future_value

# --- Tax Benefit Calculation (Simplified) ---
def tax_benefits(investment_amount):
    sec_80c_limit = 150000
    eligible = min(investment_amount, sec_80c_limit)
    tax_saved = eligible * 0.3  # Assuming 30% tax slab
    return eligible, tax_saved

# --- Post-Retirement Income Models ---
def post_retirement_income_models(total_corpus, annuity_rate, swp_amount):
    annual_annuity = total_corpus * annuity_rate / 100
    years_swp = total_corpus / (swp_amount * 12)
    return annual_annuity, years_swp

# --- Title ---
st.title("📈 Optimal Retirement Planner & SIP Simulation")
st.markdown("Plan your retirement, estimate tax savings, and simulate income models in one place.")

# --- Sidebar: User Inputs ---
st.sidebar.header("Enter Your Details")
age = st.sidebar.number_input("Current Age", min_value=18, max_value=60, value=30)
retirement_age = st.sidebar.number_input("Retirement Age", min_value=50, max_value=70, value=60)
monthly_investment = st.sidebar.number_input("Monthly Investment (₹)", min_value=500, value=5000)
estimated_return_equity = st.sidebar.slider("Equity Return Rate (p.a.)", 5.0, 15.0, 12.0)
estimated_return_traditional = st.sidebar.slider("Traditional Return Rate (p.a.)", 4.0, 9.0, 7.0)

# --- Retirement Calculation ---
months = (retirement_age - age) * 12
total_investment = monthly_investment * months
future_value_equity = monthly_investment * (((1 + estimated_return_equity/100/12) ** months - 1) / (estimated_return_equity/100/12))
future_value_traditional = monthly_investment * (((1 + estimated_return_traditional/100/12) ** months - 1) / (estimated_return_traditional/100/12))

st.subheader("💼 Retirement Portfolio Summary")
st.write(f"**Total Investment:** ₹{total_investment:,.0f}")
st.write(f"**Future Value (Equity-Based):** ₹{future_value_equity:,.0f}")
st.write(f"**Future Value (Traditional):** ₹{future_value_traditional:,.0f}")

# --- Growth Over Time Graph ---
if st.checkbox("📊 Show Year-by-Year Growth"):
    years = list(range(age, retirement_age + 1))
    equity_growth = [monthly_investment * (((1 + estimated_return_equity/100/12) ** (i*12) - 1) / (estimated_return_equity/100/12)) for i in range(len(years))]
    traditional_growth = [monthly_investment * (((1 + estimated_return_traditional/100/12) ** (i*12) - 1) / (estimated_return_traditional/100/12)) for i in range(len(years))]
    df_growth = pd.DataFrame({"Year": years, "Equity-Based": equity_growth, "Traditional": traditional_growth})
    st.line_chart(df_growth.set_index("Year"))
else:
    df_growth = pd.DataFrame()

# --- Investment Option Comparison ---
st.subheader("🔄 Comparison of Investment Options")
data = {
    "Option": ["Equity Mutual Fund", "Public Provident Fund (PPF)", "Employees Provident Fund (EPF)", "National Pension Scheme (NPS)"],
    "Expected Returns (p.a.)": [12, 7.1, 8.1, 9],
    "Risk Level": ["High", "Low", "Low", "Moderate"],
    "Liquidity": ["High (after 1 year)", "Low", "Low", "Moderate"]
}
df_comparison = pd.DataFrame(data)
st.dataframe(df_comparison)

# --- SIP Simulation ---
st.subheader("🔮 SIP-Based Investment Simulation")
monthly = st.number_input("SIP Monthly Investment (₹)", 1000, 100000, 5000, key="sip")
rate = st.number_input("Expected Annual Return (%)", 1.0, 20.0, 12.0, key="sip_rate")
years = st.slider("Investment Duration (Years)", 1, 40, 20, key="sip_years")

if st.button("🧮 Calculate SIP Growth"):
    invested, value = sip_simulation(monthly, rate, years)
    st.success(f"Total Invested: ₹{invested:,.0f}, Future Value: ₹{value:,.0f}")
    st.bar_chart(pd.DataFrame({"Future Value": [value], "Invested": [invested]}))

# --- Tax Benefit Estimation ---
st.subheader("💰 Tax Benefit Estimation")
investment = st.number_input("Annual Investment for Tax Saving (₹)", 0, 500000, 100000)
eligible, saved = tax_benefits(investment)
if investment:
    st.info(f"Eligible under Sec 80C: ₹{eligible:,.0f}\nPotential Tax Saved: ₹{saved:,.0f}")

# --- Post-Retirement Income Simulation ---
st.subheader("🏦 Post-Retirement Income Simulation")
corpus = st.number_input("Total Corpus at Retirement (₹)", 100000, 100000000, 1000000)
annuity_rate = st.slider("Annuity Rate (%)", 1, 10, 6)
swp_amount = st.number_input("SWP Monthly Amount (₹)", 1000, 100000, 10000)

if st.button("📈 Simulate Income Models"):
    annuity, swp_years = post_retirement_income_models(corpus, annuity_rate, swp_amount)
    st.success(f"Annual Annuity Income: ₹{annuity:,.0f}\nSWP Duration: {swp_years:.1f} years")

# --- Excel Export ---
if st.button("📥 Download Excel Summary"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame({
            "Summary": ["Total Investment", "Equity FV", "Traditional FV"],
            "Amount": [total_investment, future_value_equity, future_value_traditional]
        }).to_excel(writer, sheet_name='Summary', index=False)
        if not df_growth.empty:
            df_growth.to_excel(writer, sheet_name='Growth Over Time', index=False)
        df_comparison.to_excel(writer, sheet_name='Option Comparison', index=False)
    st.download_button("📤 Click to Download Excel File", data=output.getvalue(), file_name="retirement_summary.xlsx")

