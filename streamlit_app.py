import streamlit as st
import pandas as pd
import datetime
import os
import main

OUTPUT_FILE_PATH = main.OUTPUT_FILE_PATH

# Title of the app
st.title("Ciso SVM Prototype")

# Section 1: Input
st.header("Input Section")

if "output" not in st.session_state:
  st.session_state.output = {}

topic_option = [
  "E-Money",
  "Kartu Kredit"
]
selected_topic = st.multiselect("Choose topic (mandatory)*:", topic_option)

regulation_option = [
  "Peraturan Anggota Dewan Gubernur No.24:7:PADG:2022",
  "Peraturan Bank Indonesia No.23:7:PBI:2021"
  ]
selected_regulation = st.multiselect("Choose one or more for specific regulation (default is all):", regulation_option)

trigger = st.button("Predict")

# Section 2: Output
st.header("Output Section")
if trigger:  # Output is displayed only when the button is clicked
  st.session_state.output = {}
  if selected_topic:
    for topic in selected_topic:
      topic_name = topic.lower().replace(' ', '_')
      st.session_state.output[topic_name] = {}

      if not selected_regulation:
        selected_regulation = regulation_option # Default is to pick all

      for regulation in selected_regulation:
        regulation_name = main.parse_name(regulation)
        df_prediction = main.get_prediction(topic_name, regulation_name)
        df_prediction["feedback"] = None

        st.session_state.output[topic_name][regulation_name] = df_prediction
  else:
    st.write("Please choose topic.")
else:
  st.write("Click the button to see the output.")

for topic in st.session_state.output:
  st.write(topic.upper())
  for regulation in st.session_state.output[topic]:

    df_output = st.session_state.output[topic][regulation]
    st.write(f"Total Prediction for {regulation.upper()}: `{len(df_output)}`")
    df_edited = st.data_editor(
      df_output,
      use_container_width=True,
      hide_index=True,
      column_config={
        "feedback": st.column_config.SelectboxColumn(
          "feedback",
          help="Feedback for the prediction",
          options=["Correct", "Wrong"],
          required=False,
        ),
      },
      disabled=["topic_name", "regulation_name", "pasal", "pasal_text"],
    )
    csv = df_edited.to_csv(f"{OUTPUT_FILE_PATH}Prediction/{topic}_{regulation}_output.csv", index=False)

if st.session_state.output != {}:
  st.header("Describe your feedback")

  # We're adding tickets via an `st.form` and some input widgets. If widgets are used
  # in a form, the app will only rerun once the submit button is pressed.
  with st.form("add_ticket_form"):
    issue = st.text_area("Please mark any missing correct pasal here")
    submitted = st.form_submit_button("Submit")

  if submitted:
    # Make a dataframe for the new ticket and append it to the dataframe in session
    # state.\
    time_submitted = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    with open(f'{OUTPUT_FILE_PATH}Feedback/feedback_{time_submitted}.txt', 'w') as f:
      f.write(issue)

    # Show a little success message.
    st.write("Feedback submitted!")