"""
Agente Coordinador - Maneja el enrutamiento y la toma de decisiones
"""

import logging
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel

console = Console()
logger = logging.getLogger(__name__)

class AgenteCoordinador:
    """
    Agente que coordina entre el ejecutor y el generador.
    
    El AgenteCoordinador es el cerebro del sistema de agentes. Su responsabilidad
    principal es analizar las consultas de los usuarios y decidir qué agente debe
    manejarlas. Puede decidir entre:
    
    1. Usar herramientas existentes (enviar al AgenteEjecutor)
    2. Generar nuevas herramientas (enviar al AgenteGenerador)
    
    Atributos:
        herramientas_disponibles (set): Conjunto de nombres de herramientas disponibles
        historial_consultas (list): Lista de consultas procesadas para auditoría
        
    Métodos principales:
        - analizar_consulta(): Analiza una consulta y toma una decisión
        - registrar_herramienta(): Registra una nueva herramienta disponible
        - registrar_consulta(): Registra una consulta procesada
        - obtener_estadisticas(): Obtiene estadísticas del coordinador
        
    Example:
        >>> coordinador = AgenteCoordinador()
        >>> decision = coordinador.analizar_consulta("¿quién soy?")
        >>> print(decision["accion"])  # "ejecutar"
        >>> print(decision["agente"])  # "ejecutor"
    """
    
    def __init__(self):
        self.herramientas_disponibles = set()
        self.historial_consultas = []
        
    def analizar_consulta(self, consulta: str) -> Dict[str, Any]:
        """
        Analiza la consulta del usuario y decide qué agente debe manejarla.
        
        Esta función es el cerebro del sistema de coordinación. Analiza el texto de la consulta
        y determina si puede ser respondida con herramientas existentes o si necesita
        generar una nueva herramienta.
        
        Args:
            consulta (str): La consulta del usuario (ej: "¿quién soy?", "¿qué grupos tengo?")
            
        Returns:
            Dict[str, Any]: Diccionario con la decisión tomada:
                - accion: "ejecutar" o "generar"
                - agente: "ejecutor" o "generador"
                - herramienta: nombre de la herramienta (si accion="ejecutar")
                - tipo_herramienta: tipo de herramienta a generar (si accion="generar")
                - consulta: la consulta original
        """
        console.print(Panel(f"🧠 Analizando consulta: {consulta}", style="blue"))
        
        # Lógica de análisis basada en patrones de texto
        # TODO: En el futuro, esto se puede mejorar usando IA para análisis semántico
        if self._puede_responder_directamente(consulta):
            return {
                "accion": "ejecutar",
                "agente": "ejecutor",
                "herramienta": self._identificar_herramienta(consulta),
                "consulta": consulta
            }
        else:
            return {
                "accion": "generar",
                "agente": "generador",
                "consulta": consulta,
                "tipo_herramienta": self._determinar_tipo_herramienta(consulta)
            }
    
    def _puede_responder_directamente(self, consulta: str) -> bool:
        """
        Determina si la consulta puede ser respondida con herramientas existentes.
        
        Esta función implementa un sistema de reconocimiento de patrones para identificar
        consultas que el sistema ya sabe manejar. Utiliza una lista predefinida de
        patrones de texto para hacer la comparación.
        
        Args:
            consulta (str): La consulta del usuario en texto plano
            
        Returns:
            bool: True si la consulta puede ser respondida directamente, False si necesita
                  generación de nueva herramienta
                  
        Note:
            Los patrones incluyen variaciones en español e inglés para mayor flexibilidad.
            En el futuro, esto se puede mejorar con NLP o embeddings semánticos.
        """
        consulta_lower = consulta.lower()
        
        # Lista de patrones de consultas que el sistema ya sabe manejar
        # Cada patrón representa una funcionalidad implementada
        patrones_conocidos = [
            # Herramientas obligatorias
            "quién soy", "quien soy", "who am i",        # get_current_user_info
            "qué grupos tengo", "que grupos tengo", "what groups",  # get_user_groups
            "reset", "reseteo", "reiniciar",             # reset_system
            
            # Herramientas adicionales de seguridad ofensiva
            "listar usuarios", "lista usuarios", "todos los usuarios", "list users", "all users",  # list_all_users
            "buscar usuarios", "usuarios por departamento", "search users", "users by department",  # search_users_by_department
            "estructura ldap", "estructura del directorio", "ldap structure", "directory structure",  # analyze_ldap_structure
            
            # Herramientas ofensivas
            "rootdse", "root dse", "rootdse info", "root dse info",  # tool_rootdse_info
            "análisis rootdse", "analisis rootdse", "rootdse analysis",  # tool_rootdse_info
            "información servidor", "server info", "ldap info", "ldap server info",  # tool_rootdse_info
            
            # Enumeración anónima
            "enumeración anónima", "enumeracion anonima", "anonymous enum",  # tool_anonymous_enum
            "bind anónimo", "bind anonimo", "anonymous bind",  # tool_anonymous_enum
            "usuarios anónimos", "usuarios anonimos", "anonymous users",  # tool_anonymous_enum
            "enumerar usuarios", "enumerar grupos", "list users groups",  # tool_anonymous_enum
            
            # Test STARTTLS
            "starttls", "start tls", "tls test", "test tls",  # tool_starttls_test
            "test seguridad", "seguridad tls", "tls security",  # tool_starttls_test
            "downgrade tls", "tls downgrade", "handshake tls"  # tool_starttls_test
        ]
        
        # Verifica si alguno de los patrones está presente en la consulta
        return any(patron in consulta_lower for patron in patrones_conocidos)
    
    def _identificar_herramienta(self, consulta: str) -> Optional[str]:
        """
        Identifica qué herramienta usar para la consulta.
        
        Esta función mapea consultas de texto a herramientas específicas disponibles
        en el sistema. Incluye tanto herramientas obligatorias como adicionales.
        
        Args:
            consulta (str): La consulta del usuario
            
        Returns:
            Optional[str]: Nombre de la herramienta a usar, o None si no encuentra match
        """
        consulta_lower = consulta.lower()
        
        # Herramientas obligatorias
        if any(palabra in consulta_lower for palabra in ["quién soy", "quien soy", "who am i"]):
            return "get_current_user_info"
        elif any(palabra in consulta_lower for palabra in ["qué grupos", "que grupos", "what groups"]):
            return "get_user_groups"
        elif any(palabra in consulta_lower for palabra in ["reset", "reseteo", "reiniciar"]):
            return "reset_system"
        
        # Herramientas adicionales de seguridad ofensiva
        elif any(palabra in consulta_lower for palabra in ["listar usuarios", "lista usuarios", "todos los usuarios", "list users", "all users"]):
            return "list_all_users"
        elif any(palabra in consulta_lower for palabra in ["buscar usuarios", "usuarios por departamento", "search users", "users by department"]):
            return "search_users_by_department"
        elif any(palabra in consulta_lower for palabra in ["estructura ldap", "estructura del directorio", "ldap structure", "directory structure"]):
            return "analyze_ldap_structure"
        
        # Herramientas ofensivas
        elif any(palabra in consulta_lower for palabra in ["rootdse", "root dse", "rootdse info", "root dse info", "análisis rootdse", "analisis rootdse", "rootdse analysis", "información servidor", "server info", "ldap info", "ldap server info"]):
            return "tool_rootdse_info"
        elif any(palabra in consulta_lower for palabra in ["enumeración anónima", "enumeracion anonima", "anonymous enum", "bind anónimo", "bind anonimo", "anonymous bind", "usuarios anónimos", "usuarios anonimos", "anonymous users", "enumerar usuarios", "enumerar grupos", "list users groups"]):
            return "tool_anonymous_enum"
        elif any(palabra in consulta_lower for palabra in ["starttls", "start tls", "tls test", "test tls", "test seguridad", "seguridad tls", "tls security", "downgrade tls", "tls downgrade", "handshake tls"]):
            return "tool_starttls_test"
        
        return None
    
    def _determinar_tipo_herramienta(self, consulta: str) -> str:
        """Determina qué tipo de herramienta generar"""
        consulta_lower = consulta.lower()
        
        if any(palabra in consulta_lower for palabra in ["grupos", "groups"]):
            return "ldap_query"
        elif any(palabra in consulta_lower for palabra in ["usuarios", "users"]):
            return "ldap_query"
        elif any(palabra in consulta_lower for palabra in ["departamento", "department"]):
            return "ldap_query"
        
        return "generic_query"
    
    def registrar_herramienta(self, nombre: str):
        """Registra una nueva herramienta disponible"""
        self.herramientas_disponibles.add(nombre)
        console.print(Panel(f"✅ Nueva herramienta registrada: {nombre}", style="green"))
    
    def registrar_consulta(self, consulta: str, resultado: str):
        """Registra una consulta y su resultado"""
        self.historial_consultas.append({
            "consulta": consulta,
            "resultado": resultado,
            "timestamp": "ahora"  # TODO: usar datetime real
        })
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema"""
        return {
            "herramientas_disponibles": len(self.herramientas_disponibles),
            "consultas_procesadas": len(self.historial_consultas),
            "herramientas": list(self.herramientas_disponibles)
        } 