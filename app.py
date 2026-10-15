from pathlib import Path
import json
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from modelo import encuesta, calcular, DEFAULT, SECTORES

st.set_page_config(page_title='AeroEntrega | Diseño de Máquinas',page_icon='🚁',layout='wide')
st.markdown('''<style>.stApp{background:#f6f8fc} h1,h2,h3{color:#102c50} div[data-testid="stMetric"]{background:white;padding:18px;border-radius:12px;border:1px solid #dce5ef}</style>''',unsafe_allow_html=True)
st.title('AeroEntrega · del mercado al diseño')
st.caption('Laboratorio de Diseño de Máquinas · drones de reparto · horizonte de 48 meses · USD')
st.warning('CASO FICTICIO. Encuesta sintética y supuestos didácticos; no representa demanda real ni una autorización de vuelo.')
if 'base' not in st.session_state: st.session_state.base=encuesta()
p=DEFAULT.copy()
with st.sidebar:
    st.header('Simulador de negocio')
    escenario=st.selectbox('Escenario',['Base','Conservador','Optimista'])
    p['empresas']=st.number_input('Empresas en mercado objetivo',1,100000,1500)
    p['conversion']=st.slider('Conversión de intención a compra',0.,1.,.6,.05)
    p['precio']=st.number_input('Precio por dron (USD)',100,50000,6000,100)
    p['variable']=st.number_input('Costo variable por dron (USD)',0,50000,3400,100)
    p['fijo']=st.number_input('Costos fijos mensuales (USD)',0,100000,9000,500)
    p['inversion']=st.number_input('Inversión inicial total (USD)',0,5000000,180000,10000)
    p['activo']=st.number_input('Activos depreciables incluidos (USD)',0,p['inversion'],min(120000,p['inversion']),1000)
    p['capacidad']=st.number_input('Capacidad de fabricación (drones/mes)',0,1000,25)
    p['inflacion']=st.slider('Crecimiento anual de costos',0.,.3,.03,.01)
    p['precio_var']=st.slider('Variación anual del precio',-.3,.3,-.02,.01)
    p['descuento']=st.slider('Tasa de descuento anual',0.,.5,.12,.01)
    st.subheader('Ciclo de vida: meses')
    p['lanzamiento']=st.slider('Salida al mercado',2,12,7)
    p['madurez']=st.slider('Inicio de maduración',p['lanzamiento']+1,28,22)
    p['saturacion']=st.slider('Inicio de saturación',p['madurez']+1,38,32)
    p['declive']=st.slider('Inicio de declive',p['saturacion']+1,47,39)
    p['cola']=st.slider('Ventas relativas al final',0.,1.,.25,.05)
    if escenario=='Conservador': p['conversion']*=.7; p['variable']*=1.15
    if escenario=='Optimista': p['conversion']=min(1,p['conversion']*1.25); p['variable']*=.9
pmodelo=p.copy()
tabla,k=calcular(st.session_state.base,pmodelo)
# Etiquetas independientes de los nodos de ventas.
m=tabla.Mes
tabla['Etapa']=np.select([m<p['lanzamiento'],m<p['madurez'],m<p['saturacion'],m<p['declive']],['Desarrollo','Introducción / crecimiento','Maduración','Saturación'],default='Declive')
cols=st.columns(4)
for col,label,value in zip(cols,['Drones vendidos · 4 años','Ingresos · USD','VAN · USD','Recuperación simple'],[f'{tabla.Ventas.sum():,}',f'{tabla.Ingresos.sum():,.0f}',f'{k["van"]:,.0f}',f'Mes {k["payback"]}' if k['payback'] else 'No recupera en 48 meses']): col.metric(label,value)
tabs=st.tabs(['1 · Encuesta','2 · Mercado','3 · Demanda y ciclo','4 · Costos y ganancias','5 · Sensibilidad','6 · Diseño y clase'])
with tabs[0]:
    st.subheader('Encuesta empresarial ficticia')
    st.write('Producto: compra de un dron de reparto, con capacitación inicial. Seleccione una empresa hipotética y complete el formulario; sus respuestas se incorporan al análisis.')
    with st.form('encuesta'):
        a,b=st.columns(2)
        sector=a.selectbox('1. Sector de la empresa',SECTORES)
        entregas=a.number_input('2. Entregas diarias',1,10000,50)
        distancia=a.number_input('3. Radio de servicio requerido (km)',1,500,10)
        carga=a.number_input('4. Carga útil requerida (kg)',.1,100.,3.)
        autonomia=a.number_input('5. Autonomía mínima (min)',1,300,30)
        intencion=b.selectbox('6. ¿Compraría drones de reparto?',['Sí','Tal vez','No'])
        unidades=b.number_input('7. Unidades que adquiriría en cuatro años',1,1000,2)
        presupuesto=b.number_input('8. Presupuesto máximo por dron (USD)',0,100000,6000)
        prioridad=b.selectbox('9. Principal criterio de compra',['Autonomía','Seguridad','Precio','Carga útil','Mantenimiento'])
        barrera=b.selectbox('10. Principal barrera',['Costo','Regulación','Seguridad','Infraestructura','Aceptación'])
        if st.form_submit_button('Añadir respuesta ficticia'):
            fila=dict(empresa=f'Respuesta de clase {len(st.session_state.base)+1}',sector=sector,entregas_dia=entregas,distancia_km=distancia,carga_kg=carga,autonomia_min=autonomia,intencion=intencion,unidades=unidades,presupuesto_usd=presupuesto,prioridad=prioridad,barrera=barrera)
            st.session_state.base=pd.concat([st.session_state.base,pd.DataFrame([fila])],ignore_index=True)
            st.rerun()
    st.info('Respuestas de clase conservadas solo durante esta sesión. Descargue el CSV para guardarlas.')
    if st.button('Restablecer las 120 empresas simuladas'): st.session_state.base=encuesta(); st.rerun()
    st.dataframe(st.session_state.base,hide_index=True)
    st.download_button('Descargar encuesta CSV',st.session_state.base.to_csv(index=False).encode('utf-8-sig'),'encuesta_ficticia.csv','text/csv')
with tabs[1]:
    df=st.session_state.base
    a,b=st.columns(2)
    a.plotly_chart(px.histogram(df,x='sector',color='intencion',barmode='group',title='Intención por sector'),width='stretch')
    b.plotly_chart(px.histogram(df,x='presupuesto_usd',title='Presupuesto máximo por dron'),width='stretch')
    st.dataframe(df.groupby('sector').agg(empresas=('empresa','count'),entregas_dia=('entregas_dia','mean'),carga_kg=('carga_kg','median'),autonomia_min=('autonomia_min','median'),presupuesto=('presupuesto_usd','median')),width='stretch')
    st.write(f'Potencial estimado del horizonte: {k["potencial"]:,.1f} drones, antes de capacidad. Es una extrapolación docente de una muestra sintética.')
with tabs[2]:
    st.plotly_chart(px.line(tabla,x='Mes',y=['Demanda','Ventas'],title='Demanda de compra y ventas limitadas por fabricación'),width='stretch')
    st.dataframe(tabla.groupby(['Año','Etapa'],sort=False)[['Demanda','Ventas','Demanda no atendida']].sum().reset_index(),hide_index=True)
    anual=tabla.groupby('Año')[['Demanda','Ventas','Demanda no atendida','Ingresos','Costo variable','Costo fijo','EBITDA','Utilidad operativa','Flujo neto']].sum()
    st.subheader('Proyección a cuatro años'); st.dataframe(anual.style.format('{:,.0f}'))
    st.caption('La curva corresponde a ventas mensuales, no a adopción acumulada. El ciclo completo se comprime a cuatro años para el ejercicio; las unidades no atendidas se pierden, sin cartera pendiente ni reemplazos.')
with tabs[3]:
    st.plotly_chart(px.line(tabla,x='Mes',y=['Ingresos','Costo variable','Costo fijo','Utilidad operativa'],title='Resultados mensuales · USD'),width='stretch')
    caja=pd.concat([pd.DataFrame({'Mes':[0],'Caja acumulada':[-p['inversion']]}),tabla[['Mes','Caja acumulada']]])
    st.plotly_chart(px.line(caja,x='Mes',y='Caja acumulada',title='Caja acumulada, incluida inversión inicial'),width='stretch')
    margen=p['precio']-p['variable']
    st.write(f'Margen unitario inicial: USD {margen:,.0f}.')
    st.write(f'Punto de equilibrio operativo inicial: {int(np.ceil(p["fijo"]/margen))} drones/mes.' if margen>0 else 'Sin punto de equilibrio: margen unitario no positivo.')
    st.metric('Utilidad operativa total (sin impuestos)',f'USD {tabla["Utilidad operativa"].sum():,.0f}')
    st.dataframe(tabla,hide_index=True)
    st.download_button('Descargar resultados mensuales',tabla.to_csv(index=False).encode('utf-8-sig'),'resultados_48_meses.csv','text/csv')
    st.download_button('Descargar supuestos',json.dumps(p,indent=2,ensure_ascii=False),'supuestos.json','application/json')
with tabs[4]:
    filas=[]
    for precio_factor in [.8,.9,1.,1.1,1.2]:
        for conversion_factor in [.6,.8,1.,1.2,1.4]:
            q=pmodelo.copy();q['precio']*=precio_factor;q['conversion']=min(1,q['conversion']*conversion_factor)
            _,r=calcular(st.session_state.base,q)
            filas.append({'Precio relativo':precio_factor,'Conversión relativa':conversion_factor,'VAN':r['van']})
    sens=pd.DataFrame(filas)
    st.plotly_chart(px.density_heatmap(sens,x='Precio relativo',y='Conversión relativa',z='VAN',histfunc='avg',text_auto='.0f',color_continuous_scale='RdYlGn',title='VAN ante precio y conversión'),width='stretch')
    st.caption('La disposición de pago se vuelve a filtrar en cada precio; subir precio puede reducir compradores. Escenarios deterministas, sin probabilidades ni intervalos de confianza.')
    st.dataframe(sens,hide_index=True)
with tabs[5]:
    st.subheader('Del requerimiento al concepto mecánico')
    requisitos=pd.DataFrame([
        ['Carga útil','Percentil 75 de encuesta',f'{df.carga_kg.quantile(.75):.1f} kg','Estructura, tren de aterrizaje, mecanismo de sujeción'],
        ['Radio de servicio','Percentil 75',f'{df.distancia_km.quantile(.75):.1f} km','Energía de ida, retorno y reserva'],
        ['Autonomía','Percentil 75',f'{df.autonomia_min.quantile(.75):.1f} min','Batería, motores y masa total'],
        ['Seguridad','Necesidad del sistema','Validar','Retención de carga, redundancia y aterrizaje'],
        ['Fabricación','Capacidad del escenario',f'{p["capacidad"]} unidades/mes','Proceso, tolerancias, ensamble y mantenimiento']
    ],columns=['Requisito','Criterio docente','Objetivo preliminar','Decisión de diseño'])
    st.dataframe(requisitos,hide_index=True)
    st.markdown('''**Taller sugerido**
1. Defina el problema, usuarios, variables y restricciones.
2. Justifique el mercado objetivo y critique la extrapolación de la encuesta.
3. Construya tres conceptos: multirrotor, ala fija y VTOL; compare carga, autonomía y costo.
4. Proponga una matriz de decisión y un presupuesto de masa; no dimensione motores solo con la encuesta.
5. Ajuste precio, capacidad e inversión para evaluar viabilidad; explique por qué rentabilidad no garantiza viabilidad técnica.
6. Explique cuándo conviene rediseñar o retirar el producto y presente sus tablas de cuatro años.''')
    with st.expander('Fórmulas y límites del modelo',expanded=True):
        st.markdown('''Potencial = empresas objetivo × promedio(unidades × peso de intención × indicador de presupuesto ≥ precio).

Peso: Sí = conversión; Tal vez = 0,3 × conversión; No = 0. Los pesos son supuestos editables en el código, no resultados estadísticos.

Demanda mensual = potencial distribuido con curva lineal por tramos, redondeada por diferencias acumuladas. Ventas = mínimo(demanda, capacidad).

Ingresos = ventas × precio. EBITDA = ingresos − costos variables − costos fijos. Utilidad operativa = EBITDA − depreciación lineal.

Inversión total en t=0; flujo operativo al final del mes. El CSV incluye inversión en la fila del mes 1 solo para sumar flujos. VAN = −inversión + suma(EBITDA mensual descontado). Recuperación simple sin descuento.

Sin impuestos, deuda, capital de trabajo, valor residual, mantenimiento posterior a venta ni reinversión. No se calcula TIR. Activos depreciables son parte de la inversión y no se suman otra vez. Cuatro años es una hipótesis docente, no una vida útil demostrada. Los requisitos técnicos son objetivos preliminares, no un diseño validado.''')
