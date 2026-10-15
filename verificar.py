import numpy as np
from modelo import encuesta,calcular,DEFAULT
b=encuesta(); t,k=calcular(b,DEFAULT)
assert len(t)==48
assert (t.Ventas<=DEFAULT['capacidad']).all()
assert (t.Ventas<=t.Demanda).all()
assert (t.loc[t.Mes<DEFAULT['lanzamiento'],'Ventas']==0).all()
assert np.isclose(t['Flujo neto'].sum(),t.EBITDA.sum()-DEFAULT['inversion'])
assert np.isclose(k['van'],-DEFAULT['inversion']+sum(t.EBITDA/(1+DEFAULT['descuento'])**(t.Mes/12)))
p=DEFAULT.copy();p['capacidad']=0
z,_=calcular(b,p);assert z.Ventas.sum()==0
p=DEFAULT.copy();p['conversion']=0
z,_=calcular(b,p);assert z.Demanda.sum()==0
print('Modelo: demanda, capacidad, caja, VAN y escenarios extremos correctos.')
