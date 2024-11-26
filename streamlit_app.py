from sqlalchemy import create_engine
import streamlit as st
import pandas as pd
import datetime
import main
import os
from dotenv import load_dotenv

load_dotenv()

#Codespaces
# SUPABASE_USER = os.environ.get('SUPABASE_USER')
# SUPABASE_PASSWORD = os.environ.get('SUPABASE_PASSWORD')

#Streamlit Serverless
SUPABASE_USER = st.secrets['SUPABASE_USER']
SUPABASE_PASSWORD = st.secrets['SUPABASE_PASSWORD']

SUPABASE_CONNECTION = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD}@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

# Title of the app
st.title("Ciso SVM Prototype")

# Section 1: Input
st.header("Input Section")

if "output" not in st.session_state:
  st.session_state.output = {}

if "feedback" not in st.session_state:
  st.session_state.feedback = ""

def save_to_supabase(df, table_name):
  try:
    engine = create_engine(SUPABASE_CONNECTION)
    df.to_sql(table_name, engine, if_exists='append', index=False)
    return "Data saved successfully to Supabase!"
  except Exception as e:
    return f"An error occurred: {e}"

topic_option = [
  "E-Money",
  "Kartu Kredit"
]
selected_topic = st.multiselect("Choose topic (mandatory)*:", topic_option)

regulation_option = [
  "Peraturan Anggota Dewan Gubernur No.24:7:PADG:2022",
  # "Peraturan Bank Indonesia No.23:6:PBI:2021",
  "Peraturan Bank Indonesia No.2 tahun 2024",
  "Peraturan Bank Indonesia No.3 tahun 2023",
  "Peraturan Bank Indonesia No.18:40:PBI:2016",
  "Peraturan Bank Indonesia No.19:8:PBI:2017",
  "Peraturan Bank Indonesia No.23:7:PBI:2021",
  "Peraturan Bank Indonesia No.23:11:PBI:2021",
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
    if len(df_output) != 0:
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
      st.session_state.output[topic][regulation] = df_edited

if st.session_state.output != {}:
  st.header("Describe your feedback")

  # We're adding tickets via an `st.form` and some input widgets. If widgets are used
  # in a form, the app will only rerun once the submit button is pressed.
  with st.form("add_ticket_form"):
    st.session_state.feedback = st.text_area("Please mark any missing correct pasal here")
    submitted = st.form_submit_button("Submit")

  if submitted:
    with st.spinner("Submitting feedback..."):
      # Make a dataframe for the new ticket and append it to the dataframe in session
      # state.\
      time_submitted = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
      data = [st.session_state.feedback]
      df_issue = pd.DataFrame(data, columns=["feedback"])

      result = save_to_supabase(df_issue, "ciso_prediction_feedback")  # Replace with your table name
      for topic in st.session_state.output:
        for regulation in st.session_state.output[topic]:
          df_output = st.session_state.output[topic][regulation]
          result = save_to_supabase(df_output, "ciso_prediction_result")  # Replace with your table name

      # Show a little success message.
      st.success("Feedback submitted!")