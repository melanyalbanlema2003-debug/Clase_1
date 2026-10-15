"""Modelo docente: datos sintéticos, demanda de compra y flujo sin impuestos."""
import numpy as np
import pandas as pd

SECTORES = ['Comercio electrónico', 'Farmacias', 'Alimentos', 'Logística', 'Agroindustria']

def encuesta(n=120, seed=42):
    r = np.random.default_rng(seed)
    return pd.DataFrame({
        'empresa': [f'Empresa simulada {i+1:03}' for i in range(n)],
        'sector': r.choice(SECTORES, n),
        'entregas_dia': r.integers(10, 201, n),
        'distancia_km': r.integers(2, 31, n),
        'carga_kg': r.choice([1,2,3,5,8], n),
        'autonomia_min': r.choice([20,30,40,60], n),
        'intencion': r.choice(['Sí','Tal vez','No'], n, p=[.48,.32,.20]),
        'unidades': r.integers(1,6,n),
        'presupuesto_usd': r.choice([3000,4000,5000,6000,8000,10000], n),
        'prioridad': r.choice(['Autonomía','Seguridad','Precio','Carga útil','Mantenimiento'],n),
        'barrera': r.choice(['Costo','Regulación','Seguridad','Infraestructura','Aceptación'],n),
    })

def calcular(df, p):
    # Se filtra disposición de pago e intención; no se confunden entregas con drones.
    peso = df.intencion.map({'Sí':p['conversion'], 'Tal vez':p['conversion']*.3, 'No':0})
    potencial = p['empresas'] * float((df.unidades*peso*(df.presupuesto_usd >= p['precio'])).mean())
    meses = np.arange(1,49)
    # Pesos de ventas normalizados, NO parque instalado. Cuatro años comprimidos para docencia.
    nodos = [1,p['lanzamiento'],p['madurez'],p['declive'],48]
    niveles = [0,.12,1,1,p['cola']]
    curva = np.interp(meses,nodos,niveles)
    curva[meses < p['lanzamiento']] = 0
    deseada = potencial * curva / curva.sum() if curva.sum() else np.zeros(48)
    demanda = np.floor(np.cumsum(deseada)+1e-9).astype(int)
    demanda = np.diff(np.r_[0, demanda])
    ventas = np.minimum(demanda,p['capacidad']).astype(int)
    precio = p['precio']*(1+p['precio_var'])**((meses-1)//12)
    costo = p['variable']*(1+p['inflacion'])**((meses-1)//12)
    fijo = p['fijo']*(1+p['inflacion'])**((meses-1)//12)
    ingresos=ventas*precio
    variable=ventas*costo
    ebitda=ingresos-variable-fijo
    depreciacion=np.full(48,p['activo']/48)
    utilidad=ebitda-depreciacion
    flujo=ebitda.copy()
    flujo[0]-=p['inversion']
    acumulado=np.cumsum(flujo)
    tasa=(1+p['descuento'])**(1/12)-1
    # Inversión en t=0; operaciones al final de cada mes.
    van=-p['inversion']+sum(ebitda/(1+tasa)**meses)
    recuperacion=np.flatnonzero(acumulado>=0)
    etapa=np.select([meses<p['lanzamiento'],meses<p['madurez'],meses<p['saturacion'],meses<p['declive']],['Desarrollo','Introducción / crecimiento','Maduración','Saturación'],default='Declive')
    tabla=pd.DataFrame({'Mes':meses,'Año':(meses-1)//12+1,'Etapa':etapa,'Demanda':demanda,'Ventas':ventas,'Demanda no atendida':demanda-ventas,'Precio':precio,'Ingresos':ingresos,'Costo variable':variable,'Costo fijo':fijo,'EBITDA':ebitda,'Depreciación':depreciacion,'Utilidad operativa':utilidad,'Flujo neto':flujo,'Caja acumulada':acumulado})
    return tabla, {'potencial':potencial,'van':van,'payback':int(recuperacion[0]+1) if len(recuperacion) else None}

DEFAULT = dict(empresas=1500,conversion=.6,precio=6000,variable=3400,fijo=9000,inversion=180000,activo=120000,capacidad=25,inflacion=.03,precio_var=-.02,descuento=.12,lanzamiento=7,madurez=22,saturacion=32,declive=39,cola=.25)
