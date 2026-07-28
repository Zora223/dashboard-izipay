import pandas as pd

print("="*70)
print("DIAGNOSTICO YAPE - VER TODAS LAS FILAS")
print("="*70)

df = pd.read_excel("yape.xlsx", header=None)
print(f"\nTotal filas: {len(df)}")
print(f"\nCONTENIDO COMPLETO:\n")
print(df.to_string())