# AeroEntrega — Laboratorio de Diseño de Máquinas

Todos los datos empresariales son FICTICIOS. Aplicación local para docencia.

## Probar en PyCharm
1. Descomprima el ZIP y abra la carpeta drones_clase como proyecto.
2. Seleccione un intérprete Python 3.11 o 3.12 y cree un entorno virtual.
3. En la terminal de PyCharm, ubicada en esta carpeta:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

4. Abra http://localhost:8501 si no se abre automáticamente.
5. Detenga con Ctrl+C en la terminal.

Para una configuración Run de PyCharm: Module name = streamlit; Parameters = run app.py; Working directory = carpeta drones_clase. No ejecutar app.py directamente con el botón normal de Python.

## Archivos
- app.py: interfaz, encuesta de diez preguntas, gráficos, exportaciones, sensibilidad y taller.
- modelo.py: generador reproducible de 120 empresas y modelo económico.
- datos_ficticios.csv: base inicial reproducible, semilla 42.
- requirements.txt: dependencias.
- verificar.py: verificaciones de coherencia del modelo, ejecutar con python verificar.py.

## Uso docente
Las respuestas nuevas solo viven en la sesión. Descargue el CSV antes de cerrar. Esta versión no es una plataforma pública multiusuario ni incorpora una base persistente. Ajuste supuestos en el lateral; todos los gráficos se recalculan. La demanda mide drones adquiridos en cuatro años, no cantidad de paquetes entregados. Los montos son USD nominales.

Las etapas se comprimen en 48 meses: desarrollo, introducción/crecimiento, maduración, saturación y declive. La inversión ocurre al inicio, no es una etapa de ventas. Las ventas crecen linealmente hasta maduración, forman una meseta hasta el comienzo del declive y luego disminuyen. Esta forma y sus fechas son supuestos, no un ajuste empírico. La introducción y el crecimiento se muestran juntos.

Modelo sin impuestos ni financiación: distingue EBITDA, utilidad operativa y flujo. Depreciación de activos a 48 meses sin valor residual. El mes 1 del CSV incluye inversión inicial por conveniencia de agregación; VAN descuenta solo operaciones al final de cada mes y registra inversión en t=0. Ver fórmulas y límites completos en la pestaña 6.

Fuente de API de interfaz consultada: https://docs.streamlit.io/develop/api-reference (Streamlit). Las dependencias deben descargarse de Internet al instalar. No se necesita cuenta, credenciales ni servicios de pago.
