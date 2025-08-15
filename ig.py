import streamlit as st
import sqlite3
import pandas as pd
import datetime
import plotly.express as px

conn = sqlite3.connect("finflow_users.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,       
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users_setup (
        user_id INTEGER PRIMARY KEY,
        age INTEGER,
        occupation TEXT NOT NULL,
        bank_balance REAL       
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS  savings (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        asset_name TEXT NOT NULL,
        total_worth REAL NOT NULL,
        monthly_savings REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS emergency_fund (
        user_id INTEGER NOT NULL,
        monthly_savings REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

def is_username_taken(username):
    result = cursor.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    return result is not None


def home():
    st.title("FinFlow 💰📊")
    st.subheader("Your Personal Expense Tracker 🚀")

    st.subheader(" Take control of your finances with FinFlow! 💪")

    st.markdown("#### Features:")
    st.write("- 📅 Track daily expenses effortlessly")
    st.write("- 📈 Visualize spending patterns with intuitive graphs")
    st.write("- 💳 Categorize expenses for better insights")
    st.write("- 📉 Set budget goals and stay on track")
    st.write("- 📑 Generate detailed expense reports")

    st.markdown("## Why FinFlow?")
    st.write("- 💡 Easy-to-use interface")
    st.write("- ⏱ Save time with quick expense entry")
    st.write("- 📈 Gain financial insights for smarter decisions")

    st.subheader(" Get Started Today! 🚀")
    
def signup_page():
    st.title("FinFlow 💰 - Signup")
    st.subheader("Create a New Account 📝🔐")

    username = st.text_input("Enter Username:")
    password = st.text_input("Enter Password:", type="password", key="signup_password")

    if st.button("Signup"):
        if not is_username_taken(username):
            cursor.execute("INSERT INTO users (username,  password) VALUES (?, ?)", (username,  password))
            conn.commit()
            st.success("Account created successfully! You can now log in.")
            st.balloons()
        else:
            st.error("Username or email is already taken. Please choose another.")

def login_page():
    st.title("FinFlow 💰 - Login")
    st.subheader("Log into Your Account 🔐")

    username = st.text_input("Enter Username :")
    password = st.text_input("Enter Password:", type="password", key="login_password")

    if st.button("Login"):
        user_id = authenticate_user(username , password)
        if user_id:
            st.success(f"Login successful! Welcome, {username} (User ID: {user_id}).")
            st.balloons()
            return user_id
        else:
            st.error("Invalid username or password. Please try again.")
            return None

def authenticate_user(username, password):
    result = cursor.execute("SELECT id FROM users WHERE (username=? ) AND password=?", (username,  password)).fetchone()
    return result[0] if result else None


def user_setup_page():
    st.title("FinFlow 💰 - User Setup")
    st.subheader("Set Up Your Profile 🛠️")
    age = st.number_input("Enter Your Age:", min_value=0)
    occupation = st.text_input("Enter Your Occupation:")
    bank_balance = st.number_input("Enter Your Initial Bank Balance (₹):", min_value=0.0)

    if st.button("Save"):
        # Save user setup details in the database
        cursor.execute("INSERT INTO users_setup ( age, occupation, bank_balance) VALUES ( ?, ?, ?)",
                       ( age, occupation, bank_balance))
        conn.commit()
        st.success("User setup completed successfully!")

def add_expense_page():
    st.title("FinFlow 💰📊 - Add Expense")
    st.subheader("Track Your Expenses 📉")

    product_name = st.text_input("Product Name:")
    amount = st.number_input("Amount (₹):", min_value=0.0)
    # Use datetime.date.today() as the default value for date
    date = st.date_input("Expense Date:", value=datetime.date.today())
    notes = st.text_area("Notes:")

    if st.button("Add Expense"):
        # You may want to associate the expense with a user.
        # For simplicity, let's assume user_id is 1 (replace it with the actual user_id logic)
        user_id = 1
        cursor.execute("INSERT INTO expenses (user_id, product_name, amount, date, notes) VALUES (?, ?, ?, ?, ?)",
                       (user_id, product_name, amount, date, notes))
        conn.commit()
        st.success("Expense added successfully! 🎉")

def show_expenses_page():
    st.title("FinFlow 💰📊 - Show Expenses")
    st.subheader("Your Expense List 📜")

    user_id = 1  # Assume user_id is 1 for simplicity

    # Fetch all expenses associated with the user
    expenses_data = cursor.execute("SELECT * FROM expenses WHERE user_id=?", (user_id,)).fetchall()

    if expenses_data:
        # Display expenses in a tabular format
        expenses_df = pd.DataFrame(expenses_data, columns=["Expense ID", "User ID", "Product Name", "Amount", "Date", "Notes"])
        st.dataframe(expenses_df)

        # Allow user to remove an expense
        expense_id_to_remove = st.number_input("Enter Expense ID to Remove:", min_value=1, max_value=expenses_df["Expense ID"].max())

        if st.button("Remove Expense"):
            # Remove the selected expense
            cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id_to_remove,))
            conn.commit()
            st.success("Expense removed successfully! 🗑️")
    else:
        st.info("No expenses found.")

def show_graphs_page():
    st.title("FinFlow 💰📊 - Show Graphs")
    st.subheader("Expense Statistics 📊")

    user_id = 1  

    expenses_data = cursor.execute("SELECT * FROM expenses WHERE user_id=?", (user_id,)).fetchall()

    if expenses_data:
        expenses_df = pd.DataFrame(expenses_data, columns=["Expense ID", "User ID", "Product Name", "Amount", "Date", "Notes"])

        product_expenses = expenses_df.groupby("Product Name")["Amount"].sum().reset_index()

        st.subheader("Bar Graph - Total Expense vs Product Name")
        fig_bar = px.bar(product_expenses, x="Product Name", y="Amount", title="Total Expense vs Product Name")
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("Circular Graph - Total Expense Distribution")
        fig_pie = px.pie(product_expenses, values="Amount", names="Product Name", title="Total Expense Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)

        # Calculate total expenses
        total_expenses_result = cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (user_id,)).fetchone()
        total_expenses = total_expenses_result[0] if total_expenses_result is not None and total_expenses_result[0] is not None else 0

        benchmark_value = 2000  

        comparison_data = {
            'Category': ['User Expenses', 'Benchmark'],
            'Amount': [total_expenses, benchmark_value]
        }
        comparison_df = pd.DataFrame(comparison_data)

    
        st.subheader("Bar Graph - User Expenses vs avg student expense")
        fig_bar_comparison = px.bar(comparison_df, x='Category', y='Amount', title="User Expenses vs avg student expense")
        st.plotly_chart(fig_bar_comparison, use_container_width=True)


        if total_expenses > benchmark_value:
            st.warning("Your expenses are higher than other students. Spend cautiously!")
        elif total_expenses < benchmark_value:
            st.success("Great job! Your expenses are lower than the other students. Keep it up!")

    else:
        st.warning("No expense found to plot graphs. Add expenses to see the statistics.") 
               

def show_savings_page():
    st.title("FinFlow 💰📊 - Savings")
    st.subheader("Plan Your Savings 💵")

    user_id = 1  


    existing_savings_data = cursor.execute("SELECT * FROM savings WHERE user_id=?", (user_id,)).fetchall()

    if existing_savings_data:
        existing_savings_df = pd.DataFrame(existing_savings_data, columns=["Savings ID", "User ID", "Asset Name", "Total Worth", "Monthly Savings"])
        st.subheader("Existing Savings:")
        st.dataframe(existing_savings_df)

    # Allow user to input new savings details
    st.subheader("Add New Savings:")
    asset_name = st.text_input("Asset Name:")
    total_worth = st.number_input("Total Worth of the Asset (₹):", min_value=0.0)
    monthly_savings = st.number_input("Monthly Savings (₹):", min_value=0.0)

    if st.button("Add Savings"):

        existing_asset = cursor.execute("SELECT * FROM savings WHERE user_id=? AND asset_name=?", (user_id, asset_name)).fetchone()

        if existing_asset:
            st.warning("Asset with the same name already exists. Please use a different name.")
        else:
            cursor.execute("INSERT INTO savings (user_id, asset_name, total_worth, monthly_savings) VALUES (?, ?, ?, ?)",
                           (user_id, asset_name, total_worth, monthly_savings))
            conn.commit()
            st.success("Savings added successfully! 🎉")
            st.balloons()

    
            months_required = int(total_worth / monthly_savings) if monthly_savings > 0 else None
            if months_required is not None:
                st.info(f"You will reach the total worth in approximately {months_required} months.")


    st.subheader("Remove Savings:")
    asset_name_to_remove = st.text_input("Asset Name to Remove:")

    if st.button("Remove Savings"):
        existing_asset_to_remove = cursor.execute("SELECT * FROM savings WHERE user_id=? AND asset_name=?", (user_id, asset_name_to_remove)).fetchone()

        if existing_asset_to_remove:
            cursor.execute("DELETE FROM savings WHERE user_id=? AND asset_name=?", (user_id, asset_name_to_remove))
            conn.commit()
            st.success("Savings removed successfully! 🚀")
        else:
            st.warning("No savings found with the given asset name.")

def emergency_fund():
    st.title("FinFlow 💰📊 - Emergency Fund")
    st.subheader("Secure Your Emergency Needs 🚑")
    user_id = 1 

    existing_emergency_fund_data = cursor.execute("SELECT * FROM emergency_fund WHERE user_id=?", (user_id,)).fetchone()

    if existing_emergency_fund_data:
        existing_emergency_fund_df = pd.DataFrame(
            {
                "Emergency Fund ID": [existing_emergency_fund_data[0]],
                "Monthly Savings": [existing_emergency_fund_data[1]],
            }
        )
        st.subheader("Existing Emergency Fund:")
        st.dataframe(existing_emergency_fund_df)

        if st.button("Remove Emergency Fund"):
            cursor.execute("DELETE FROM emergency_fund WHERE user_id=?", (user_id,))
            conn.commit()
            st.success("Emergency Fund removed successfully! 🚀")
    else:
        st.info("No existing emergency fund found.")

    st.subheader("Set Up Emergency Fund:")
    st.write("Monthly Savings for Emergency Fund 📅")
    default_min_amount = 500
    default_max_amount = 2000 
    monthly_savings_range = st.slider("Select Monthly Savings Amount (₹):",
                                      min_value=default_min_amount, max_value=default_max_amount,
                                      value=default_min_amount, step=50)

    if st.button("Set Up Emergency Fund"):
        existing_emergency_fund = cursor.execute("SELECT * FROM emergency_fund WHERE user_id=?", (user_id,)).fetchone()

        if existing_emergency_fund:
            cursor.execute("UPDATE emergency_fund SET monthly_savings=? WHERE user_id=?",
                           (monthly_savings_range, user_id))
        else:
            cursor.execute("INSERT INTO emergency_fund (user_id, monthly_savings) VALUES (?, ?)",
                           (user_id, monthly_savings_range))

        conn.commit()
        st.success("Emergency Fund set up successfully! 🎉")
    




def currency_converter_page():
    st.title("Currency Converter 🌐💱")

    amount = st.number_input("Enter Amount:")

    from_currency = st.selectbox("Select From Currency:", ["INR", "USD"])
    to_currency = st.selectbox("Select To Currency:", ["INR", "USD"])

    # Conversion factors
    inr_to_usd_factor = 0.012
    usd_to_inr_factor = 83.12

    if from_currency == "INR" and to_currency == "USD":
        result = amount * inr_to_usd_factor
    elif from_currency == "USD" and to_currency == "INR":
        result = amount * usd_to_inr_factor
    else:
        result = amount 

    st.subheader("Conversion Result:")
    st.write(f"{amount} {from_currency} is equal to {result:.2f} {to_currency}")

def total_expenses_page():
    st.title("FinFlow 💰📊 - Total Expenses")
    st.subheader("Calculate Your Total Expenses 📉")

    bank_balance = st.number_input("Enter Your Bank Balance (₹):", min_value=0.0)

    user_id = 1 

    total_expenses_result = cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (user_id,)).fetchone()
    total_expenses = total_expenses_result[0] if total_expenses_result is not None and total_expenses_result[0] is not None else 0


    total_savings_result = cursor.execute("SELECT SUM(monthly_savings) FROM savings WHERE user_id=?", (user_id,)).fetchone()
    total_savings = total_savings_result[0] if total_savings_result is not None and total_savings_result[0] is not None else 0

 
    total_emergency_fund_result = cursor.execute("SELECT SUM(monthly_savings) FROM emergency_fund WHERE user_id=?", (user_id,)).fetchone()
    total_emergency_fund = total_emergency_fund_result[0] if total_emergency_fund_result is not None and total_emergency_fund_result[0] is not None else 0

    available_balance = bank_balance - total_expenses - total_savings - total_emergency_fund

    st.subheader("Total Expenses Summary:")
    total_expenses_df = pd.DataFrame({
        "Category": ["Expenses", "Savings", "Emergency Fund", "Available Balance"],
        "Amount (₹)": [total_expenses, total_savings, total_emergency_fund, available_balance]
    })
    st.table(total_expenses_df)


def main():
    st.sidebar.title("FinFlow 💰📊 Menu")
    menu_options = ["Home", "Sign Up", "Log In", "User Setup", "Add Expense", "Show Expenses", "Show Graphs", "Savings", "Emergency Fund", "Total Expenses","Currency Converter" ]

    choice = st.sidebar.radio("Select an option", menu_options)

    if choice == "Home":
     home()
          

    elif choice == "Sign Up":
         signup_page()

    elif choice == "Log In":
        login_page()

    elif choice == "User Setup":
        user_setup_page()

    elif choice == "Add Expense":
        add_expense_page()

    elif choice == "Show Expenses":
        show_expenses_page()

    elif choice == "Show Graphs":
        show_graphs_page()

    elif choice == "Savings":
        show_savings_page()
    elif choice == "Emergency Fund":
        emergency_fund()

    elif choice =="Total Expenses":
        total_expenses_page()    
    elif choice =="Currency Converter":
        currency_converter_page() 
if __name__ == "__main__":
    main()
