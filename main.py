from nlp_id.stopword import StopWord
from nlp_id.lemmatizer import Lemmatizer
from joblib import dump, load
import pandas as pd
import re

RAW_FILE_PATH = '/content/drive/My Drive/Cisometric/Raw/'
SVM_FILE_PATH = '/content/drive/My Drive/Cisometric/SVM/'

def clean_pasal(df_input):
  stopword = StopWord()
  lemmatizer = Lemmatizer()
  clean_data = []

  for index, row in df_input.iterrows():
    text = row['pasal_text']

    clean_text = re.sub(r'pasal\s+\d+[.|\s+]\d+|pasal\s+\d+' , '', text.lower()) # remove pasal
    clean_text = re.sub(r'ayat\s+\(\d+\)|\(\d+\)' , '', clean_text) # remove ayat
    clean_text = re.sub(r'huruf\s+\w|angka\s+\d|\n\w\.' , '', clean_text) # remove huruf & angka
    clean_text = re.sub(r'[^\d\w\s]' , '', clean_text)
    clean_text = stopword.remove_stopword(clean_text)
    clean_text = lemmatizer.lemmatize(clean_text)

    clean_data.append(clean_text)

  return clean_data

def get_svm_model():
  model = load(f'{SVM_FILE_PATH}Model/svm_model.joblib')

  return model

def get_tfidf_model():
  model = load(f'{SVM_FILE_PATH}Model/tfidf_model.joblib')

  return model

def get_pasal(regulation_name):
  df_pasal = pd.read_csv(f'{RAW_FILE_PATH}{regulation_name}.csv')

  return df_pasal

def predict_pasal(regulation_name):
  df_pasal = get_pasal(regulation_name)
  clean_data = clean_pasal(df_pasal)

  vectorizer = get_tfidf_model()
  features = vectorizer.transform(clean_data)

  model = get_svm_model()
  predictions = model.predict(features)

  df_pasal['regulation_name'] = regulation_name
  df_pasal['prediction'] = predictions

  return df_pasal

def get_prediction(regulation_name):
  df_prediction = predict_pasal(regulation_name)
  df_prediction = df_prediction[df_prediction['prediction'] == 1]

  result = f'Total Prediction for {regulation_name.upper()}: {len(df_prediction)}\n\n'
  for index, row in df_prediction.iterrows():
    result += str(row['pasal'])+'\n\n'

  return result

def parse_name(item):
  no_index = item.find('No')
  regulator_name = item[:no_index]
  regulator_name = re.sub(r'[^A-Z]', '', regulator_name)
  regulation_name = regulator_name + item[no_index-1:]
  regulation_name = re.sub(r'[^\w]', '_', regulation_name.lower())

  return regulation_name