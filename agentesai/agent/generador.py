"""
Agente Generador - Crea nuevas herramientas dinámicamente usando IA
"""

import logging
import os
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

console = Console()
logger = logging.getLogger(__name__)

class AgenteGenerador:
    """Agente que genera nuevas herramientas usando IA"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.herramientas_generadas = []
        self.templates_disponibles = {
            "ldap_query": self._template_ldap_query,
            "generic_query": self._template_generic_query
        }
    
    def generar_herramienta(self, consulta: str, tipo: str) -> Dict[str, Any]:
        """
        Genera una nueva herramienta dinámicamente usando IA (Gemini).
        
        Esta función es el corazón del sistema de auto-expansión. Toma una consulta
        del usuario y genera código Python funcional que puede responder a esa consulta.
        El proceso incluye generación de código con IA, creación de funciones dinámicas
        y asignación de nombres únicos.
        
        Args:
            consulta (str): La consulta del usuario que requiere una nueva herramienta
            tipo (str): Tipo de herramienta a generar ("ldap_query", "generic_query", etc.)
            
        Returns:
            Dict[str, Any]: Resultado de la generación con la siguiente estructura:
                - error (bool): True si hubo error, False si fue exitosa
                - nombre (str): Nombre único generado para la herramienta
                - funcion (callable): Función Python ejecutable generada
                - codigo (str): Código fuente generado por la IA
                - tipo (str): Tipo de herramienta generada
                - consulta_original (str): La consulta que originó la generación
                - mensaje (str): Descripción del error (solo si error=True)
                
        Raises:
            No lanza excepciones, todas las excepciones son capturadas y retornadas
            como parte del diccionario de resultado.
            
        Note:
            Si la API de Gemini falla, se usa un sistema de fallback con templates
            predefinidos para asegurar que siempre se genere algo funcional.
            
        Example:
            >>> resultado = generador.generar_herramienta("¿cuáles son todos los grupos?", "ldap_query")
            >>> if not resultado["error"]:
            ...     print(f"Nueva herramienta: {resultado['nombre']}")
        """
        # Verificar que la API key esté configurada
        if not self.api_key:
            return {
                "error": True,
                "mensaje": "API key de Gemini no configurada"
            }
        
        try:
            console.print(Panel(f"🤖 Generando nueva herramienta para: {consulta}", style="blue"))
            
            # Paso 1: Generar código Python usando la API de Gemini
            codigo_generado = self._generar_codigo_con_ia(consulta, tipo)
            
            if not codigo_generado:
                return {
                    "error": True,
                    "mensaje": "No se pudo generar código para la consulta"
                }
            
            # Paso 2: Crear una función Python ejecutable a partir del código
            funcion_generada = self._crear_funcion_dinamica(codigo_generado, consulta)
            
            if funcion_generada:
                # Paso 3: Generar un nombre único para la nueva herramienta
                nombre_herramienta = self._generar_nombre_herramienta(consulta)
                
                return {
                    "error": False,
                    "nombre": nombre_herramienta,
                    "funcion": funcion_generada,
                    "codigo": codigo_generado,
                    "tipo": tipo,
                    "consulta_original": consulta
                }
            else:
                return {
                    "error": True,
                    "mensaje": "Error creando función dinámica"
                }
                
        except Exception as e:
            # Capturar cualquier error durante el proceso de generación
            logger.error(f"Error generando herramienta: {e}")
            return {
                "error": True,
                "mensaje": f"Error en generación: {str(e)}"
            }
    
    def _generar_codigo_con_ia(self, consulta: str, tipo: str) -> Optional[str]:
        """
        Genera código usando la API de Gemini
        """
        try:
            import google.generativeai as genai
            
            # Configurar Gemini
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Prompt para generar herramienta
            prompt = self._crear_prompt_generacion(consulta, tipo)
            
            response = model.generate_content(prompt)
            
            # Extraer código del response
            codigo = self._extraer_codigo_python(response.text)
            
            if codigo:
                console.print(Panel("✅ Código generado exitosamente", style="green"))
                console.print(Panel(f"```python\n{codigo}\n```", style="green"))
                return codigo
            else:
                console.print(Panel("❌ No se pudo extraer código válido", style="red"))
                return None
                
        except Exception as e:
            logger.error(f"Error con Gemini API: {e}")
            # Fallback: usar template básico
            return self._usar_template_fallback(consulta, tipo)
    
    def _crear_prompt_generacion(self, consulta: str, tipo: str) -> str:
        """
        Crea el prompt para la generación de código
        """
        base_prompt = f"""
        Necesito que generes una función de Python para responder a esta consulta: "{consulta}"
        
        Tipo de herramienta: {tipo}
        
        Requisitos:
        1. La función debe ser simple y funcional
        2. Debe retornar un string con la respuesta
        3. Si es una consulta LDAP, usa la conexión LDAP real
        4. La función debe tener un nombre descriptivo
        5. Incluye manejo básico de errores
        
        Genera SOLO el código Python, sin explicaciones adicionales.
        """
        
        if tipo == "ldap_query":
            base_prompt += """
            ====== GUÍA COMPLETA PARA HERRAMIENTAS LDAP ======
            
            IMPORTAR SIEMPRE:
            from agentesai.tools_base.ldap_connector import LDAPConnector
            
            ====== FUNCIONES DISPONIBLES EN LDAPConnector ======
            
            1. CONEXIÓN Y DESCONEXIÓN:
               - ldap_conn.connect() -> bool (True si exitoso)
               - ldap_conn.disconnect() -> bool
            
            2. BÚSQUEDAS GENERALES:
               - ldap_conn.search(base_dn, filter_str) -> list
               - base_dn típico: "dc=meli,dc=com"
               - filtros comunes: "(objectClass=*)", "(objectClass=person)", "(objectClass=groupOfNames)"
            
            3. FUNCIONES ESPECÍFICAS (RECOMENDADAS):
               - ldap_conn.list_all_users() -> list[dict] (usuarios con atributos completos)
               - ldap_conn.list_all_groups() -> list[dict] (grupos con atributos completos)
               - ldap_conn.get_user_info(username) -> dict o None
               - ldap_conn.get_user_groups(username) -> list o None
            
            4. ATRIBUTOS DISPONIBLES EN USUARIOS:
               - username, full_name, email, title, department, status, last_login
            
            5. ATRIBUTOS DISPONIBLES EN GRUPOS:
               - cn (nombre), description, member, memberUid
            
            ====== PATRONES RECOMENDADOS ======
            
            A) CONSULTAS DE USUARIOS POR DEPARTAMENTO:
               def obtener_usuarios_departamento_X():
                   ldap_conn = LDAPConnector()
                   if ldap_conn.connect():
                       try:
                           all_users = ldap_conn.list_all_users()
                           usuarios_dept = [
                               user for user in all_users
                               if user.get("department", "").lower() == "nombre_departamento"
                           ]
                           return f"Usuarios en {nombre_departamento}: {len(usuarios_dept)} encontrados"
                       finally:
                           ldap_conn.disconnect()
                   else:
                       return "Error: No se pudo conectar al LDAP"
            
            B) CONSULTAS DE GRUPOS:
               def obtener_grupos_info():
                   ldap_conn = LDAPConnector()
                   if ldap_conn.connect():
                       try:
                           all_groups = ldap_conn.list_all_groups()
                           return f"Total grupos: {len(all_groups)}"
                       finally:
                           ldap_conn.disconnect()
                   else:
                       return "Error: No se pudo conectar al LDAP"
            
            C) CONSULTAS ESPECÍFICAS:
               def buscar_usuario_especifico():
                   ldap_conn = LDAPConnector()
                   if ldap_conn.connect():
                       try:
                           # Usar search para consultas específicas
                           resultado = ldap_conn.search("dc=meli,dc=com", "(cn=nombre_usuario)")
                           return f"Resultado: {len(resultado)} entradas encontradas"
                       finally:
                           ldap_conn.disconnect()
                   else:
                       return "Error: No se pudo conectar al LDAP"
            
            D) INFORMACIÓN DE USUARIO ESPECÍFICO:
               def obtener_info_usuario_admin():
                   ldap_conn = LDAPConnector()
                   if ldap_conn.connect():
                       try:
                           # Usar get_user_info para usuario específico
                           user_info = ldap_conn.get_user_info("admin")
                           if user_info:
                               return f"Usuario admin: {user_info.get('full_name', 'N/A')} - {user_info.get('email', 'N/A')}"
                           else:
                               return "Usuario admin no encontrado"
                       finally:
                           ldap_conn.disconnect()
                   else:
                       return "Error: No se pudo conectar al LDAP"
            
            ====== REGLAS IMPORTANTES ======
            
            1. SIEMPRE usar try/finally para desconectar
            2. SIEMPRE verificar connect() antes de operaciones
            3. Para usuarios por departamento: usar list_all_users() + filtro
            4. Para grupos: usar list_all_groups()
            5. Para búsquedas específicas: usar search() con filtros apropiados
            6. NO usar filtros LDAP directos para atributos personalizados
            7. La función debe ser específica para la consulta y NO requerir parámetros
            
            ====== EJEMPLOS DE FILTROS LDAP VÁLIDOS ======
            
            - "(objectClass=person)" -> todos los usuarios
            - "(objectClass=groupOfNames)" -> todos los grupos
            - "(cn=admin)" -> usuario específico por nombre
            - "(uid=john.doe)" -> usuario por UID
            - "(&(objectClass=person)(cn=*))" -> usuarios con nombre que empiece con cualquier letra
            
            ====== ESTRUCTURA DE RETORNO ======
            
            Retorna siempre un string descriptivo con la información solicitada.
            Incluye manejo de errores y mensajes claros.
            """
        
        return base_prompt
    
    def _extraer_codigo_python(self, texto: str) -> Optional[str]:
        """
        Extrae código Python del texto generado por la IA
        """
        # Buscar bloques de código Python
        import re
        
        # Patrón para bloques de código
        patrones = [
            r'```python\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'def\s+\w+\s*\(.*?\):.*?(?=\n\S|\Z)',
        ]
        
        for patron in patrones:
            matches = re.findall(patron, texto, re.DOTALL)
            if matches:
                return matches[0].strip()
        
        return None
    
    def _crear_funcion_dinamica(self, codigo: str, consulta: str):
        """
        Crea una función dinámica a partir del código generado
        """
        try:
            # Crear un namespace local para la función
            local_namespace = {}
            
            # Ejecutar el código en el namespace
            exec(codigo, globals(), local_namespace)
            
            # Buscar la función definida
            for nombre, valor in local_namespace.items():
                if callable(valor) and nombre.startswith('get_'):
                    return valor
            
            # Si no se encuentra, crear una función wrapper
            def funcion_wrapper():
                try:
                    # Crear un módulo temporal con el código
                    import types
                    import sys
                    
                    # Crear un módulo temporal
                    temp_module = types.ModuleType('temp_module')
                    
                    # Agregar LDAPConnector al módulo temporal
                    from agentesai.tools_base.ldap_connector import LDAPConnector
                    temp_module.LDAPConnector = LDAPConnector
                    
                    # Ejecutar el código en el módulo temporal
                    exec(codigo, temp_module.__dict__)
                    
                    # Buscar y ejecutar la función definida
                    for nombre, valor in temp_module.__dict__.items():
                        if callable(valor) and nombre.startswith(('obtener_', 'get_', 'count_', 'list_', 'contar_')):
                            try:
                                resultado = valor()
                                return resultado
                            except Exception as e:
                                return f"Error ejecutando función {nombre}: {str(e)}"
                    
                    return f"Herramienta generada para: {consulta}"
                except Exception as e:
                    return f"Error ejecutando herramienta: {str(e)}"
            
            return funcion_wrapper
            
        except Exception as e:
            logger.error(f"Error creando función dinámica: {e}")
            return None
    
    def _generar_nombre_herramienta(self, consulta: str) -> str:
        """
        Genera un nombre único para la herramienta
        """
        import hashlib
        
        # Crear hash de la consulta para nombre único
        hash_consulta = hashlib.md5(consulta.encode()).hexdigest()[:8]
        
        # Generar nombre descriptivo
        palabras = consulta.lower().split()[:3]
        nombre_base = "_".join(palabras)
        
        return f"get_{nombre_base}_{hash_consulta}"
    
    def _usar_template_fallback(self, consulta: str, tipo: str) -> str:
        """
        Usa un template básico si falla la generación con IA
        """
        if tipo == "ldap_query":
            return f'''
def get_ldap_query_fallback():
    """Herramienta fallback para consulta LDAP usando conexión real"""
    try:
        from agentesai.tools_base.ldap_connector import LDAPConnector
        
        ldap_conn = LDAPConnector()
        if ldap_conn.connect():
            try:
                # Búsqueda básica como fallback
                resultado = ldap_conn.search("dc=meli,dc=com", "(objectClass=*)")
                return f"Consulta LDAP real completada: {len(resultado)} entradas encontradas para: {consulta}"
            finally:
                ldap_conn.disconnect()
        else:
            return f"Error: No se pudo conectar al LDAP para: {consulta}"
    except Exception as e:
        return f"Error en fallback LDAP: {{str(e)}} para: {consulta}"
'''
        else:
            return f'''
def get_generic_query_fallback():
    """Herramienta fallback genérica"""
    return f"Respuesta genérica para: {consulta}"
'''
    
    def _template_ldap_query(self, consulta: str) -> str:
        """Template para consultas LDAP"""
        return f'''
def get_ldap_query():
    """Consulta LDAP generada dinámicamente"""
    return f"Resultado LDAP para: {consulta}"
'''
    
    def _template_generic_query(self, consulta: str) -> str:
        """Template para consultas genéricas"""
        return f'''
def get_generic_query():
    """Consulta genérica generada dinámicamente"""
    return f"Respuesta para: {consulta}"
''' 