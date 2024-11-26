import streamlit as st
import main

# Title of the app
st.title("Ciso SVM Prototype")

# Section 1: Input
st.header("Input Section")

topic_option = [
  "E-Money",
  "Kartu Kredit"
]
selected_topic = st.selectbox("Choose an option:", topic_option)

regulation_option = [
  "Peraturan Anggota Dewan Gubernur No.24:7:PADG:2022",
  "Peraturan Bank Indonesia No.23:7:PBI:2021"
  ]
selected_regulation = st.multiselect("Choose one or more options:", regulation_option)

trigger = st.button("Show Output")

# Section 2: Output
st.header("Output Section")
if trigger:  # Output is displayed only when the button is clicked
  if selected_topic and selected_regulation:
    for option in selected_regulation:
      regulation_name = main.parse_name(option)
      st.write(main.get_prediction(regulation_name))
  else:
    st.write("Please choose at both field.")
else:
  st.write("Click the button to see the output.")