import pdfplumber

print("="*70)
print("🔍 DIAGNÓSTICO DETALLADO DEL PDF - CAJA 1")
print("="*70)

with pdfplumber.open("caja1.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"\n{'='*70}")
        print(f"📄 PÁGINA {i+1}")
        print(f"{'='*70}")
        
        tablas = page.extract_tables()
        print(f"Tablas encontradas: {len(tablas)}")
        
        for j, tabla in enumerate(tablas):
            print(f"\n--- Tabla {j+1} ({len(tabla)} filas) ---")
            for k, fila in enumerate(tabla):
                print(f"  Fila {k}: {fila}")
                if k > 15:  # Solo primeras 15 filas por tabla
                    print(f"  ... ({len(tabla) - 15} filas más)")
                    break

print("\n" + "="*70)
print("✅ DIAGNÓSTICO COMPLETADO")
print("="*70)