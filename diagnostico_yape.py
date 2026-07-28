import pandas as pd
import json

print('='*60)
print('LEYENDO yape.xlsx DIRECTO')
print('='*60)
df = pd.read_excel('yape.xlsx')
print(f'Filas: {len(df)}')
print(f'Columnas: {list(df.columns)}')
print('\nPrimeras 3 filas:')
print(df.head(3))
print(f'\nTipos:\n{df.dtypes}')

print('\n' + '='*60)
print('REVISANDO historial.json')
print('='*60)
try:
    with open('historial.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'Ventas: {len(data.get(\"ventas\", []))}')
    print(f'Izipay: {len(data.get(\"izipay\", []))}')
    print(f'Yape:   {len(data.get(\"yape\", []))}')
    if len(data.get('yape', [])) > 0:
        print('\nPrimera transaccion Yape guardada:')
        print(data['yape'][0])
except Exception as e:
    print(f'Error: {e}')
