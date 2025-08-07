#!/usr/bin/env python3
"""
Script de diagnóstico para Ollama
Detecta y muestra todos los modelos disponibles
"""

import requests
import json
import sys

def diagnosticar_ollama():
    print("🔍 DIAGNÓSTICO DE OLLAMA")
    print("=" * 50)
    
    # Verificar conexión
    try:
        print("📡 Verificando conexión a Ollama...")
        response = requests.get('http://localhost:11434/api/tags', timeout=10)
        print(f"✅ Estado de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ollama está funcionando correctamente")
            print(f"📊 Respuesta completa: {json.dumps(data, indent=2)}")
            
            modelos = data.get('models', [])
            print(f"\n🤖 MODELOS DETECTADOS: {len(modelos)}")
            print("-" * 30)
            
            if modelos:
                for i, modelo in enumerate(modelos, 1):
                    nombre = modelo.get('name', 'Sin nombre')
                    tamano = modelo.get('size', 0)
                    modificado = modelo.get('modified_at', 'Desconocido')
                    
                    # Convertir tamaño
                    if tamano > 1024**3:  # GB
                        tamano_str = f"{tamano / (1024**3):.1f} GB"
                    elif tamano > 1024**2:  # MB
                        tamano_str = f"{tamano / (1024**2):.1f} MB"
                    else:
                        tamano_str = f"{tamano} bytes"
                    
                    print(f"{i}. {nombre}")
                    print(f"   📏 Tamaño: {tamano_str}")
                    print(f"   📅 Modificado: {modificado}")
                    print(f"   🔧 Detalles: {modelo.get('details', {})}")
                    print()
            else:
                print("❌ No se encontraron modelos")
                
        else:
            print(f"❌ Error de conexión: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a Ollama en puerto 11434")
        print("💡 Verifica que Ollama esté ejecutándose:")
        print("   - Windows: Busca 'Ollama' en el menú inicio")
        print("   - Terminal: ollama serve")
        
    except requests.exceptions.Timeout:
        print("⏱️ Timeout conectando a Ollama")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    # Verificar proceso
    print("\n🔍 VERIFICANDO PROCESO...")
    try:
        import subprocess
        import platform
        
        sistema = platform.system().lower()
        
        if sistema == 'windows':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq ollama.exe'], 
                                  capture_output=True, text=True)
            if 'ollama.exe' in result.stdout:
                print("✅ Proceso ollama.exe está ejecutándose")
            else:
                print("❌ Proceso ollama.exe NO está ejecutándose")
                print("💡 Inicia Ollama manualmente")
        else:
            result = subprocess.run(['pgrep', '-f', 'ollama'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Proceso ollama está ejecutándose")
            else:
                print("❌ Proceso ollama NO está ejecutándose")
    except Exception as e:
        print(f"❌ Error verificando proceso: {e}")

if __name__ == "__main__":
    diagnosticar_ollama()

