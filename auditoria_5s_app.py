import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO


# Cargar CSS personalizado
with open("styles.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.set_page_config(page_title="Auditoría 5S - RUNAWANA", page_icon="✅", layout="wide")

# Título + Logo a la derecha
col_title, col_logo = st.columns([6, 1])

with col_title:
    st.title("Auditoría 5S - RUNAWANA")

with col_logo:
    st.image("logo_runawana.png", width=120)  # Asegúrate de que el archivo exista

# Columnas normales
fecha = st.date_input("Fecha")
auditor_1 = st.text_input("Auditoría realizada por", "")


st.markdown("---")

preguntas_5s = [
    {"Área": "BODEGA/CALIDAD", "Pregunta": "¿El piso de Bodega/Calidad se mantiene limpio y libre de polvo, restos de tela o empaques?"},
    {"Área": "BODEGA/CALIDAD", "Pregunta": "¿Los estantes están etiquetados con el tipo o modelo de producto que contienen?"},
    {"Área": "BODEGA/CALIDAD", "Pregunta": "¿Las herramientas y materiales se encuentran organizadas e identificadas?"},
    {"Área": "BODEGA/CALIDAD", "Pregunta": "¿Todas las luces del área funcionan correctamente y proporcionan buena iluminación?"},
    {"Área": "BODEGA/CALIDAD", "Pregunta": "¿Existe señalización visible que identifique el área de Control de calidad y Bodega?"},

    {"Área": "PASILLO", "Pregunta": "¿El piso del pasillo se mantiene limpio, libre de restos de tela, hilos?"},
    {"Área": "PASILLO", "Pregunta": "¿El pasillo se mantiene despejado, sin materiales que obstaculicen el tránsito o acceso a las áreas?"},
    {"Área": "PASILLO", "Pregunta": "¿La mesa de trabajo de corte mantiene únicamente los materiales necesarios y ordenados?"},
    {"Área": "PASILLO", "Pregunta": "¿Las telas se encuentran dobladas y almacenadas en estanterías, evitando colocarlas directamente en el piso?"},
    {"Área": "PASILLO", "Pregunta": "¿La zona donde se almacenan los moldes para el proceso de corte cuenta con señalización clara y visible?"},
    {"Área": "PASILLO", "Pregunta": "¿La máquina de corte cuenta con una correcta gestión de cables para garantizar un uso seguro y ordenado?"},
    {"Área": "PASILLO", "Pregunta": "¿Existe un extintor y botiquín ubicados en zonas accesibles y correctamente señalizados?"},
    {"Área": "PASILLO", "Pregunta": "¿Todas las luces del área funcionan correctamente y permiten buena visibilidad para el trabajo?"},
    {"Área": "PASILLO", "Pregunta": "¿Existe señaléticas visibles que identifique claramente las áreas o puestos de trabajo?"},
    {"Área": "PASILLO", "Pregunta": "¿Las ventanas se encuentran en buen estado y permiten el ingreso adecuado de luz natural al área de trabajo?"},
    {"Área": "PASILLO", "Pregunta": "¿Las instalaciones eléctricas se encuentran en buen estado, protegidas y sin cables expuestos?"},

    {"Área": "CONFECCIÓN", "Pregunta": "¿Los insumos o materiales se encuentran almacenados en contenedores identificados?"},
    {"Área": "CONFECCIÓN", "Pregunta": "¿Las estaciones de trabajo están limpias y sin acumulación de materiales innecesarios al finalizar la jornada laboral?"},
    {"Área": "CONFECCIÓN", "Pregunta": "¿La estantería de hilos está correctamente organizada por colores y cuenta con señalización visible?"},
    {"Área": "CONFECCIÓN", "Pregunta": "¿Las paredes del área se encuentran libres de objetos innecesarios?"},
    {"Área": "CONFECCIÓN", "Pregunta": "¿Todas las luces del área funcionan correctamente y proporcionan buena iluminación?"},
    {"Área": "CONFECCIÓN", "Pregunta": "¿Existe señaléticas visibles que identifique claramente las áreas o puestos de trabajo?"},

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
                obs = st.text_input("Observación", "", key=f"obs_{area}_{i}")
            respuestas.append({
                "Área": item["Área"],
                "Pregunta": item["Pregunta"],
                "Respuesta": resp,
                "Observación": obs
            })
        st.markdown("---")
    submitted = st.form_submit_button("Calcular resultados")

def calcular_resumen(df):
    resumen = df.groupby("Área")["Respuesta"].value_counts().unstack(fill_value=0)
    for col in ["SI", "NO", "NA"]:
        if col not in resumen.columns:
            resumen[col] = 0
    resumen["%"] = (resumen["SI"] / (resumen["SI"] + resumen["NO"])) * 100
    resumen["%"] = resumen["%"].fillna(0)
    total_si = resumen["SI"].sum()
    total_no = resumen["NO"].sum()
    total_na = resumen["NA"].sum()
    total_ok = (total_si / (total_si + total_no) * 100) if (total_si + total_no) > 0 else 0
    total_row = pd.DataFrame({"NA": [total_na], "NO": [total_no], "SI": [total_si], "%": [total_ok]}, index=["TOTAL"])
    return pd.concat([resumen[["NA", "NO", "SI", "%"]], total_row])

def resumen_coloreado(df):
    base = df[df["Respuesta"] != "NA"].groupby("Área")["Respuesta"].value_counts().unstack(fill_value=0)
    for col in ["SI", "NO"]:
        if col not in base.columns:
            base[col] = 0
    base["Items Revisados"] = base["SI"] + base["NO"]
    na = df[df["Respuesta"] == "NA"].groupby("Área").size()
    base["NA"] = na
    base["NA"] = base["NA"].fillna(0).astype(int)
    base["%"] = (base["SI"] / base["Items Revisados"] * 100).fillna(0).round(2)
    base = base.reset_index()
    base = base[["Área", "Items Revisados", "SI", "NO", "NA", "%"]]
    total = {
        "Área": "TOTAL",
        "Items Revisados": int(base["Items Revisados"].sum()),
        "SI": int(base["SI"].sum()),
        "NO": int(base["NO"].sum()),
        "NA": int(base["NA"].sum()),
        "%": round((base["SI"].sum() / (base["SI"].sum() + base["NO"].sum()) * 100) if (base["SI"].sum() + base["NO"].sum()) > 0 else 0, 2)
    }
    base.loc[len(base)] = total
    return base


# Color de porcentaje de la tabla de resumen
def color_porcentaje(val):
    if val >= 80: return "background-color: rgba(110, 252, 71, 1); font-weight:bold;"
    elif val >= 60: return "background-color: rgba(255, 242, 0, 1); font-weight:bold;"
    else: return "background-color: rgba(234, 40, 40, 1); font-weight:bold;"



def grafico_linea(series_ok):
    fig, ax = plt.subplots(figsize=(8, 4))

    # Colores fuertes (no pastel) con 80% transparencia
    verde_claro    = (0/255, 200/255, 0/255, 0.8)
    amarillo_claro = (255/255, 230/255, 0/255, 0.8)
    rojo_claro     = (255/255, 0/255, 0/255, 0.8)

    # Bandas
    ax.axhspan(80, 100, facecolor=verde_claro)
    ax.axhspan(60, 80, facecolor=amarillo_claro)
    ax.axhspan(0, 60, facecolor=rojo_claro)

    # Línea principal
    ax.plot(series_ok.index, series_ok.values, marker='o', linewidth=2, color="#001B4D")

    # Etiquetas numéricas en la línea
    for i, v in enumerate(series_ok.values):
        ax.text(i, v + 2, f"{v:.2f}%", ha='center', va='bottom',
                fontsize=9, fontweight='bold', color="#001B4D")

    # ======= CAMBIOS SOLICITADOS =======
    ax.set_ylim(-5, 110)                                     # Extiende eje Y
    ax.set_yticks(range(0, 101, 10))                         # Mostrar solo 0–100
    ax.set_yticklabels([f"{y}%" for y in range(0, 101, 10)]) # Mostrar % limpio

    ax.set_ylabel("Cumplimiento", fontweight='bold')
    ax.set_title("Cumplimiento de Condiciones por Área", fontsize=12, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)

    st.pyplot(fig)





def grafico_radar(series_ok):

    # ✅ Tamaño corregido
    fig, ax = plt.subplots(figsize=(4, 2), subplot_kw=dict(polar=True))

    categorias = list(series_ok.index)    # PISO - PAREDES - OBJETOS
    valores = np.array(series_ok.values, dtype=float) / 100.0

    # Cerrar figura
    valores = np.concatenate((valores, [valores[0]]))
    angulos = np.linspace(0, 2 * np.pi, len(categorias) + 1)

    # Fondos por zona
    ax.fill_between(angulos, 0.8, 1.0, color=(0/255, 180/255, 0/255), alpha=0.7)   # Verde ≥ 80
    ax.fill_between(angulos, 0.6, 0.8, color=(255/255, 210/255, 0/255), alpha=0.7) # Amarillo ≥ 60
    ax.fill_between(angulos, 0.0, 0.6, color=(255/255, 0/255, 0/255), alpha=0.7)   # Rojo < 60

    # Línea y relleno
    ax.plot(angulos, valores, color="black", linewidth=0.8)
    ax.fill(angulos, valores, color="black", alpha=0.20)

    # ✅ ETIQUETAS AFUERA (OBJETOS sale bien)
    for angulo, categoria in zip(angulos[:-1], categorias):
        ax.text(angulo, 1.6, categoria, fontsize=4, fontweight='bold',
                ha='center', va='center')

    # Escala radial
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=3)
    ax.set_rlabel_position(75) 
    ax.tick_params(axis='y', pad=100)

    ax.set_title("Gráfico de Radar por Área", fontsize=6, fontweight='bold', pad=5)
    


    angulos_mostrar = [45, 90, 135, 180, 225, 270, 315]
    etiquetas = [f"{a}°" for a in angulos_mostrar]

    ax.set_xticks(np.deg2rad(angulos_mostrar))
    ax.set_xticklabels(etiquetas, fontsize=4)
  


    ax.spines['polar'].set_linewidth(0.5)   # grosor
    ax.set_rlim(0, 1.14)  
    
    st.pyplot(fig, use_container_width=False)



    
if submitted:
    df = pd.DataFrame(respuestas)

    st.subheader("Resumen de respuestas")
    st.dataframe(df, use_container_width=True)

    #st.markdown("### Resumen por área")
    resumen = calcular_resumen(df)
    #st.dataframe(resumen.round(2), use_container_width=True)

    st.markdown("### Gráficos")
    colg1, colg2 = st.columns(2)
    series_ok = resumen.loc[resumen.index != "TOTAL", "%"]

    with colg1:
        grafico_linea(series_ok)

    with colg2:
        if len(series_ok) >= 3:
            grafico_radar(series_ok)
        else:
            st.info("El diagrama requiere al menos 3 áreas con datos.")

    # ========= GENERAR TABLA FINAL (NECESARIA PARA LA TABLA NUEVA) =========
    tabla_final = resumen_coloreado(df)

    # ========= NUEVA TABLA: RESUMEN GENERAL =========
    st.markdown("### Resumen General de la Auditoría")

    total_items = tabla_final.loc[tabla_final["Área"] == "TOTAL", "Items Revisados"].values[0]
    cumplimiento_promedio = tabla_final.loc[tabla_final["Área"] == "TOTAL", "%"].values[0]

    areas = tabla_final.iloc[:-1]
    max_c = areas["%"].max()
    areas_mayor = ", ".join(areas[areas["%"] == max_c]["Área"].tolist()) + f" ({max_c}%)"

    areas_crit = areas[areas["%"] < 60]["Área"].tolist()
    areas_criticas_texto = ", ".join(areas_crit) if len(areas_crit) > 0 else "Ninguna"

    resumen_general = pd.DataFrame({
        "Total Ítems Revisados": [int(total_items)],
        "Cumplimiento Promedio (%)": [round(float(cumplimiento_promedio), 2)],
        "Área(s) con Mayor Cumplimiento": [areas_mayor],
        "Área(s) Críticas": [areas_criticas_texto]
    })

    st.dataframe(resumen_general, use_container_width=True)

    # ========= TABLA FINAL (COLOREADA) =========
    st.markdown("### Cumplimiento por Área")
    styled = tabla_final.style.apply(
        lambda s: [color_porcentaje(v) if s.name == "%" else "" for v in s],
        axis=0
    )
    st.dataframe(styled, use_container_width=True)

    # ========= DESCARGAS =========
    st.markdown("### Descargas")

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Respuestas")
        resumen.round(2).to_excel(writer, sheet_name="Resumen_por_area")
        tabla_final.to_excel(writer, index=False, sheet_name="Resumen_final")
        resumen_general.to_excel(writer, index=False, sheet_name="Resumen_general")

    st.download_button(
        "⬇️ Descargar reporte (Excel)",
        data=output.getvalue(),
        file_name="reporte_auditoria_5s.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Para mostrar los resultados, por favor da click al botón **Calcular**.")
