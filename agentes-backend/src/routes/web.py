from flask import Blueprint, request, jsonify
import requests
import json
from datetime import datetime
import urllib.parse
import re
from bs4 import BeautifulSoup

web_bp = Blueprint('web', __name__)

@web_bp.route('/web/buscar', methods=['POST'])
def buscar_web():
    """Búsqueda web real para agentes"""
    try:
        data = request.get_json()
        consulta = data.get('consulta')
        num_resultados = data.get('num_resultados', 5)
        
        if not consulta:
            return jsonify({'error': 'Consulta requerida'}), 400
        
        # Realizar búsqueda con DuckDuckGo
        resultados = buscar_duckduckgo(consulta, num_resultados)
        
        return jsonify({
            'consulta': consulta,
            'resultados': resultados,
            'total': len(resultados),
            'timestamp': datetime.utcnow().isoformat(),
            'fuente': 'DuckDuckGo'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_bp.route('/web/extraer-contenido', methods=['POST'])
def extraer_contenido_web():
    """Extraer contenido de una URL específica"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL requerida'}), 400
        
        # Extraer contenido de la página
        contenido = extraer_contenido_pagina(url)
        
        return jsonify({
            'url': url,
            'contenido': contenido,
            'longitud': len(contenido) if contenido else 0,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_bp.route('/web/noticias', methods=['POST'])
def buscar_noticias():
    """Buscar noticias recientes"""
    try:
        data = request.get_json()
        tema = data.get('tema')
        
        if not tema:
            return jsonify({'error': 'Tema requerido'}), 400
        
        # Buscar noticias con términos específicos
        consulta_noticias = f"{tema} noticias recientes"
        resultados = buscar_duckduckgo(consulta_noticias, 10)
        
        # Filtrar resultados que parezcan noticias
        noticias = []
        for resultado in resultados:
            if es_noticia(resultado):
                noticias.append(resultado)
        
        return jsonify({
            'tema': tema,
            'noticias': noticias,
            'total': len(noticias),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_bp.route('/web/wikipedia', methods=['POST'])
def buscar_wikipedia():
    """Buscar información en Wikipedia"""
    try:
        data = request.get_json()
        termino = data.get('termino')
        idioma = data.get('idioma', 'es')
        
        if not termino:
            return jsonify({'error': 'Término requerido'}), 400
        
        # Buscar en Wikipedia
        info_wikipedia = obtener_info_wikipedia(termino, idioma)
        
        return jsonify({
            'termino': termino,
            'idioma': idioma,
            'informacion': info_wikipedia,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_bp.route('/web/clima', methods=['POST'])
def obtener_clima():
    """Obtener información del clima"""
    try:
        data = request.get_json()
        ciudad = data.get('ciudad')
        
        if not ciudad:
            return jsonify({'error': 'Ciudad requerida'}), 400
        
        # Buscar información del clima
        info_clima = buscar_clima(ciudad)
        
        return jsonify({
            'ciudad': ciudad,
            'clima': info_clima,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def buscar_duckduckgo(consulta, num_resultados=5):
    """Realizar búsqueda en DuckDuckGo"""
    try:
        query_encoded = urllib.parse.quote(consulta)
        search_url = f"https://duckduckgo.com/html/?q={query_encoded}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            resultados = []
            
            # Buscar resultados
            result_links = soup.find_all('a', class_='result__a')
            
            for i, link in enumerate(result_links[:num_resultados]):
                try:
                    titulo = link.get_text().strip()
                    url = link.get('href', '')
                    
                    # Buscar descripción
                    descripcion = ""
                    parent = link.find_parent('div', class_='result__body')
                    if parent:
                        snippet = parent.find('a', class_='result__snippet')
                        if snippet:
                            descripcion = snippet.get_text().strip()
                    
                    if titulo and url:
                        resultados.append({
                            'posicion': i + 1,
                            'titulo': titulo,
                            'url': url,
                            'descripcion': descripcion
                        })
                except Exception as e:
                    continue
            
            return resultados
        
        return []
    
    except Exception as e:
        print(f"Error en búsqueda DuckDuckGo: {e}")
        return []

def extraer_contenido_pagina(url):
    """Extraer contenido de texto de una página web"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Eliminar scripts y estilos
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extraer texto
            texto = soup.get_text()
            
            # Limpiar texto
            lineas = (line.strip() for line in texto.splitlines())
            chunks = (phrase.strip() for line in lineas for phrase in line.split("  "))
            texto_limpio = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limitar longitud
            return texto_limpio[:5000] if len(texto_limpio) > 5000 else texto_limpio
        
        return None
    
    except Exception as e:
        print(f"Error extrayendo contenido: {e}")
        return None

def es_noticia(resultado):
    """Determinar si un resultado parece ser una noticia"""
    try:
        titulo = resultado.get('titulo', '').lower()
        url = resultado.get('url', '').lower()
        descripcion = resultado.get('descripcion', '').lower()
        
        # Palabras clave que indican noticias
        palabras_noticias = [
            'noticia', 'news', 'actualidad', 'hoy', 'ayer', 'reciente',
            'último', 'breaking', 'urgente', 'reporta', 'informa'
        ]
        
        # Dominios de noticias conocidos
        dominios_noticias = [
            'elpais.com', 'elmundo.es', 'abc.es', 'lavanguardia.com',
            'rtve.es', 'antena3.com', 'telecinco.es', 'bbc.com',
            'cnn.com', 'reuters.com', 'ap.org'
        ]
        
        # Verificar palabras clave
        texto_completo = f"{titulo} {descripcion}"
        for palabra in palabras_noticias:
            if palabra in texto_completo:
                return True
        
        # Verificar dominios
        for dominio in dominios_noticias:
            if dominio in url:
                return True
        
        return False
    
    except Exception:
        return False

def obtener_info_wikipedia(termino, idioma='es'):
    """Obtener información de Wikipedia"""
    try:
        # API de Wikipedia
        api_url = f"https://{idioma}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(termino)}"
        
        headers = {
            'User-Agent': 'AgentesIA/1.0 (https://github.com/Jonathan-camara/agentes-ia-v6.0)'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'titulo': data.get('title', ''),
                'resumen': data.get('extract', ''),
                'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                'imagen': data.get('thumbnail', {}).get('source', '') if data.get('thumbnail') else None
            }
        
        return None
    
    except Exception as e:
        print(f"Error obteniendo info Wikipedia: {e}")
        return None

def buscar_clima(ciudad):
    """Buscar información del clima"""
    try:
        # Buscar clima usando DuckDuckGo
        consulta_clima = f"clima {ciudad} temperatura"
        resultados = buscar_duckduckgo(consulta_clima, 3)
        
        # Intentar extraer información del clima del primer resultado
        if resultados:
            primer_resultado = resultados[0]
            contenido = extraer_contenido_pagina(primer_resultado['url'])
            
            if contenido:
                return {
                    'fuente': primer_resultado['titulo'],
                    'url': primer_resultado['url'],
                    'informacion': contenido[:500],  # Primeros 500 caracteres
                    'descripcion': primer_resultado['descripcion']
                }
        
        return {
            'mensaje': f'No se pudo obtener información del clima para {ciudad}',
            'sugerencia': 'Intenta con una ciudad más específica'
        }
    
    except Exception as e:
        print(f"Error buscando clima: {e}")
        return None

