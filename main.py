import streamlit as st

# Title of the app
st.title("My First Streamlit App")

# Input box
name = st.text_input("Enter your name")

# Button
if st.button("Greet Me"):
    st.success(f"Hello, {name}! Welcome to Streamlit 🎉")

# Display a simple table
st.subheader("Sample Data")
data = {"Name": ["Alice", "Bob", "Charlie"], "Age": [25, 30, 22]}
st.table(data)
