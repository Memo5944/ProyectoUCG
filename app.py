import streamlit as st
import pandas as pd
import libreria_funciones as lf

st.title("Proyecto final UCG")

st.sidebar.title("Parámetros")

st.sidebar.image("Python_logo.png")

uploaded_files = st.file_uploader(
    "Upload data", accept_multiple_files=True, type="csv"
)
for uploaded_file in uploaded_files:
    df = pd.read_csv(uploaded_file)
    st.write(df)

monto = st.number_input("Ingrese el monto:", min_value = 0 , max_value = 10000, value=1000)
interes = st.number_input("Ingrese el interes:",min_value = 0.0 , max_value = 1.0, value=0.10)
anios = st.number_input("Ingrese el número de años del prestamo:",value=1)
numero_pagos = st.number_input("Ingrese el número pagos anuales:" , value = 12)

cuota = lf.cuota_prestamo(monto, interes,anios,numero_pagos)
st.write("Su cuota mensual es: ",cuota)
