import streamlit as st
import anvil.server
anvil.server.connect("server_EXGPO337E7MCHKSGUVRWEJS3-564IOCBNIE22XVLU") #aceit
from anvil.tables import app_tables

def post():
  row = app_tables.questions.get (unique_key='something')
  row['Structured Interview'] = ['something', 'ish']


if st.button("Click Me"):
    post()
