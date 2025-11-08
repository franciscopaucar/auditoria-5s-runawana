import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Auditoría 5S - Bralunne", page_icon="✅", layout="wide")

st.title("Auditoría 5S - Bralunne")
col0, col1, col2 = st.columns([1, 2, 2])
with col0:
    fecha = st.date_input("Fecha")
with col1:
    responsable_1 = st.text_input("Responsable 1", "")
with col2:
    responsable_2 = st.text_input("Responsable 2", "")

st.markdown("---")

preguntas_5s = [
    {"Área": "PISO", "Pregunta": "¿El piso se encuentra limpio (está libre de manchas visibles, polvo o residuos)?"},
    {"Área": "PISO", "Pregunta": "¿Los hilos, insumos o materiales no se almacenan directamente sobre el piso?"},
    {"Área": "PISO", "Pregunta": "¿Las estaciones de costura y corte permiten paso fluido sin obstáculos en el piso?"},
    {"Área": "PISO", "Pregunta": "¿El contenedor de desechos está en una zona fija y accesible sin generar desorden?"},
    {"Área": "PAREDES", "Pregunta": "¿Las paredes se encuentran sin manchas visibles, grietas, telarañas ni residuos adheridos?"},
    {"Área": "PAREDES", "Pregunta": "¿Existe señalización visible (ej. baño, salida, extintor, normas básicas)?"},
    {"Área": "PAREDES", "Pregunta": "¿Hay un extintor instalado, visible, accesible y en su ubicación correcta (identificado)?"},
    {"Área": "PAREDES", "Pregunta": "¿Se realiza verificación manual de inventario?"},
    {"Área": "PAREDES", "Pregunta": "¿Los tomacorrientes están operativos (verificado con prueba de conexión)?"},
    {"Área": "PAREDES", "Pregunta": "¿Se encuentran en pared los instructivos visibles sobre los procesos?"},
    {"Área": "TECHO", "Pregunta": "¿El techo se encuentra limpio (sin manchas, humedad visible ni telarañas)?"},
    {"Área": "TECHO", "Pregunta": "¿La iluminación instalada es funcional y sin focos, lámparas quemadas)?"},
    {"Área": "OBJETOS", "Pregunta": "¿Cada cajón está etiquetado con el nombre del insumo o herramienta que debe contener?"},
    {"Área": "OBJETOS", "Pregunta": "¿Las herramientas están almacenadas en bandejas o compartimentos designados?"},
    {"Área": "OBJETOS", "Pregunta": "¿Los moldes están estandarizados y almacenados correctamente?"},
    {"Área": "OBJETOS", "Pregunta": "¿Los hilos están organizados por color o referencia?"},
    {"Área": "OBJETOS", "Pregunta": "¿Cada máquina de coser está limpia?"},
    {"Área": "OBJETOS", "Pregunta": "¿Los objetos en los cajones están organizados con separadores?"},
    {"Área": "OBJETOS", "Pregunta": "¿Las estaciones de trabajo tienen guías visibles?"},
    {"Área": "OBJETOS", "Pregunta": "¿Se usa señalética para indicar ubicación de herramientas e insumos?"},
    {"Área": "OBJETOS", "Pregunta": "¿Las herramientas se devuelven a su lugar asignado tras uso?"},
    {"Área": "OBJETOS", "Pregunta": "¿Los colaboradores colocan los insumos nuevamente en su sitio?"},
    {"Área": "OBJETOS", "Pregunta": "¿Hay delimitación con cinta adhesiva en cajones o áreas de almacenamiento?"}
]

st.subheader("Formulario de auditoría")
with st.form("form_auditoria"):
    respuestas = []
    for area in sorted(set([p["Área"] for p in preguntas_5s])):
        st.markdown(f"### Área: **{area}**")
        for i, item in enumerate([p for p in preguntas_5s if p["Área"] == area], start=1):
            colA, colB = st.columns([2, 3])
            with colA:
                resp = st.radio(
                    label=f"{i}. {item['Pregunta']}",
                    options=["SI", "NO", "NA"],
                    horizontal=True,
                    key=f"{area}_{i}"
                )
            with colB:
                obs = st.text_input("Observación (opcional)", "", key=f"obs_{area}_{i}")
            respuestas.append({
                "Área": item["Área"],
                "Pregunta": item["Pregunta"],
                "Respuesta": resp,
                "Observación": obs
            })
        st.markdown("---")
    submitted = st.form_submit_button("Calcular Porcentajes y Mostrar Resultados")

def calcular_resumen(df):
    resumen = df.groupby("Área")["Respuesta"].value_counts().unstack(fill_value=0)
    for col in ["SI", "NO", "NA"]:
        if col not in resumen.columns:
            resumen[col] = 0
    resumen["% OK"] = (resumen["SI"] / (resumen["SI"] + resumen["NO"])) * 100
    resumen["% OK"] = resumen["% OK"].fillna(0)
    total_si = resumen["SI"].sum()
    total_no = resumen["NO"].sum()
    total_na = resumen["NA"].sum()
    total_ok = (total_si / (total_si + total_no) * 100) if (total_si + total_no) > 0 else 0
    total_row = pd.DataFrame({"NA": [total_na], "NO": [total_no], "SI": [total_si], "% OK": [total_ok]}, index=["TOTAL EVALUACIÓN"])
    return pd.concat([resumen[["NA", "NO", "SI", "% OK"]], total_row])

def resumen_coloreado(df):
    base = df[df["Respuesta"] != "NA"].groupby("Área")["Respuesta"].value_counts().unstack(fill_value=0)
    for col in ["SI", "NO"]:
        if col not in base.columns:
            base[col] = 0
    base["Revisados"] = base["SI"] + base["NO"]
    na = df[df["Respuesta"] == "NA"].groupby("Área").size()
    base["NA"] = na
    base["NA"] = base["NA"].fillna(0).astype(int)
    base["%"] = (base["SI"] / base["Revisados"] * 100).fillna(0).round(2)
    base = base.reset_index()
    base = base[["Área", "Revisados", "SI", "NO", "NA", "%"]]
    total = {
        "Área": "TOTAL EVALUACIÓN",
        "Revisados": int(base["Revisados"].sum()),
        "SI": int(base["SI"].sum()),
        "NO": int(base["NO"].sum()),
        "NA": int(base["NA"].sum()),
        "%": round((base["SI"].sum() / (base["SI"].sum() + base["NO"].sum()) * 100) if (base["SI"].sum() + base["NO"].sum()) > 0 else 0, 2)
    }
    base.loc[len(base)] = total
    return base

def color_porcentaje(val):
    if val >= 85: return "background-color: rgba(0, 128, 0, .25); font-weight:bold;"
    elif val >= 70: return "background-color: rgba(255, 215, 0, .35); font-weight:bold;"
    else: return "background-color: rgba(255, 0, 0, .25); font-weight:bold;"

def grafico_linea(series_ok):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axhspan(85, 100, facecolor='green', alpha=0.15)
    ax.axhspan(70, 85, facecolor='yellow', alpha=0.15)
    ax.axhspan(0, 70, facecolor='red', alpha=0.12)
    ax.plot(series_ok.index, series_ok.values, marker='o', linewidth=2)
    for i, v in enumerate(series_ok.values):
        ax.text(i, v + 2, f"{v:.0f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_ylabel("% Cumplimiento")
    ax.set_title("Resumen auditoría por área")
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)

def grafico_radar(series_ok):
    categorias = list(series_ok.index)
    valores = list(series_ok.values)
    valores += valores[:1]
    angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angulos += angulos[:1]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill_between(angulos, 0, 0.7*np.ones_like(angulos), color='red', alpha=0.08)
    ax.fill_between(angulos, 0.7, 0.85, color='yellow', alpha=0.08)
    ax.fill_between(angulos, 0.85, 1.0, color='green', alpha=0.08)
    ax.plot(angulos, np.array(valores)/100.0, linewidth=2)
    ax.fill(angulos, np.array(valores)/100.0, alpha=0.25)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
    ax.set_title('Diagrama de Araña - %OK por área', fontsize=13, fontweight='bold')
    st.pyplot(fig)

if submitted:
    df = pd.DataFrame(respuestas)
    st.subheader("Tabla de respuestas")
    st.dataframe(df, use_container_width=True)

    st.markdown("### Resumen por área (% OK excluye NA)")
    resumen = calcular_resumen(df)
    st.dataframe(resumen.round(2), use_container_width=True)

    st.markdown("### Gráficos")
    colg1, colg2 = st.columns(2, vertical_alignment="center")
    series_ok = resumen.loc[resumen.index != "TOTAL EVALUACIÓN", "% OK"].round(2)
    with colg1:
        grafico_linea(series_ok)
    with colg2:
        if len(series_ok) >= 3:
            grafico_radar(series_ok)
        else:
            st.info("El diagrama de araña requiere al menos 3 áreas con datos.")

    st.markdown("### Resumen final (con colores por %)")
    tabla_final = resumen_coloreado(df)
    styled = tabla_final.style.apply(
        lambda s: [color_porcentaje(v) if s.name == "%" else "" for v in s],
        axis=0
    )
    st.dataframe(styled, use_container_width=True)

    st.markdown("### Descargas")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar respuestas (CSV)", data=csv, file_name="respuestas_auditoria_5s.csv", mime="text/csv")

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Respuestas")
        resumen.round(2).to_excel(writer, sheet_name="Resumen_por_area")
        tabla_final.to_excel(writer, index=False, sheet_name="Resumen_final")
    st.download_button(
        "⬇️ Descargar reporte (Excel)",
        data=output.getvalue(),
        file_name="reporte_auditoria_5s.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Completa el formulario y presiona **Calcular Porcentajes y Mostrar Resultados**.")
