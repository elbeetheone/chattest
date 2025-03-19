import streamlit as st
import anvil.server
anvil.server.connect("server_EXGPO337E7MCHKSGUVRWEJS3-564IOCBNIE22XVLU") #aceit
from anvil.tables import app_tables

def click_me():
    row = app_tables.questions.get(unique_key='something')
    row['Structured Interview'] = ['testing some isj']


if st.button("Click Me"):
    click_me()
