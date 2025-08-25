"""
Agente Ofensivo - Especializado en análisis de seguridad ofensiva y herramientas LDAP
"""

import logging
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)

class AgenteOfensivo:
    """
    Agente especializado en análisis de seguridad ofensiva y herramientas LDAP.
    
    Este agente proporciona herramientas avanzadas para análisis de seguridad,
    enumeración de directorios LDAP, y técnicas de reconocimiento ofensivo.
    
    Atributos:
        herramientas_ofensivas (dict): Diccionario de herramientas ofensivas disponibles
        historial_operaciones (list): Lista de operaciones realizadas para auditoría
        
    Métodos principales:
        - ejecutar_herramienta_ofensiva(): Ejecuta una herramienta ofensiva específica
        - listar_herramientas(): Lista todas las herramientas ofensivas disponibles
        - obtener_estadisticas(): Obtiene estadísticas del agente ofensivo
        - registrar_operacion(): Registra una operación para auditoría
    """
    
    def __init__(self):
        self.herramientas_ofensivas = {}
        self.historial_operaciones = []
        self._inicializar_herramientas_ofensivas()
        
    def _inicializar_herramientas_ofensivas(self):
        """Inicializa las herramientas ofensivas del sistema"""
        from ..tools_offensive import (
            tool_rootdse_info,
            tool_anonymous_enum,
            # Futuras herramientas ofensivas se agregarán aquí
        )
        
        self.herramientas_ofensivas = {
            "tool_rootdse_info": tool_rootdse_info,
            "tool_anonymous_enum": tool_anonymous_enum,
        }
        
        console.print(Panel(f"🔴 {len(self.herramientas_ofensivas)} herramientas ofensivas inicializadas", style="red"))
    
    def ejecutar_herramienta_ofensiva(self, nombre: str, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta una herramienta ofensiva específica.
        
        Args:
            nombre (str): Nombre de la herramienta ofensiva a ejecutar
            **kwargs: Parámetros adicionales para la herramienta
            
        Returns:
            Dict[str, Any]: Resultado de la ejecución con metadatos de seguridad
        """
        if nombre not in self.herramientas_ofensivas:
            return {
                "error": True,
                "mensaje": f"Herramienta ofensiva '{nombre}' no encontrada",
                "herramientas_disponibles": list(self.herramientas_ofensivas.keys())
            }
        
        try:
            console.print(Panel(f"🔴 Ejecutando herramienta ofensiva: {nombre}", style="red"))
            
            # Ejecutar la herramienta ofensiva
            resultado = self.herramientas_ofensivas[nombre](**kwargs)
            
            # Registrar la operación para auditoría
            self.registrar_operacion(nombre, kwargs, resultado)
            
            return {
                "error": False,
                "herramienta": nombre,
                "resultado": resultado,
                "tipo": "ofensiva",
                "timestamp": "ahora",  # TODO: usar datetime real
                "parametros": kwargs
            }
            
        except Exception as e:
            logger.error(f"Error ejecutando herramienta ofensiva {nombre}: {e}")
            return {
                "error": True,
                "mensaje": f"Error ejecutando {nombre}: {str(e)}",
                "herramienta": nombre
            }
    
    def agregar_herramienta_ofensiva(self, nombre: str, funcion):
        """
        Agrega una nueva herramienta ofensiva al agente.
        
        Args:
            nombre (str): Nombre de la herramienta
            funcion: Función ejecutable de la herramienta
        """
        self.herramientas_ofensivas[nombre] = funcion
        console.print(Panel(f"🔴 Nueva herramienta ofensiva agregada: {nombre}", style="red"))
        
        return True
    
    def listar_herramientas(self) -> Dict[str, Any]:
        """
        Lista todas las herramientas ofensivas disponibles.
        
        Returns:
            Dict[str, Any]: Información de las herramientas ofensivas
        """
        return {
            "total": len(self.herramientas_ofensivas),
            "herramientas": list(self.herramientas_ofensivas.keys()),
            "categorias": {
                "ldap_analysis": ["tool_rootdse_info"],
                "enumeration": ["tool_anonymous_enum"],
                # Futuras categorías se agregarán aquí
            }
        }
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del agente ofensivo.
        
        Returns:
            Dict[str, Any]: Estadísticas del agente
        """
        return {
            "herramientas_disponibles": len(self.herramientas_ofensivas),
            "operaciones_realizadas": len(self.historial_operaciones),
            "ultima_operacion": self.historial_operaciones[-1] if self.historial_operaciones else None
        }
    
    def registrar_operacion(self, herramienta: str, parametros: Dict, resultado: Any):
        """
        Registra una operación ofensiva para auditoría.
        
        Args:
            herramienta (str): Nombre de la herramienta utilizada
            parametros (Dict): Parámetros de la operación
            resultado (Any): Resultado de la operación
        """
        operacion = {
            "herramienta": herramienta,
            "parametros": parametros,
            "resultado": str(resultado),
            "timestamp": "ahora",  # TODO: usar datetime real
            "tipo": "ofensiva"
        }
        
        self.historial_operaciones.append(operacion)
        
        # Log de seguridad
        logger.warning(f"Operación ofensiva registrada: {herramienta} con parámetros {parametros}")
    
    def mostrar_estado(self):
        """
        Muestra el estado actual del agente ofensivo.
        """
        estadisticas = self.obtener_estadisticas()
        
        table = Table(title="Estado del Agente Ofensivo")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="red")
        
        table.add_row("Herramientas disponibles", str(estadisticas['herramientas_disponibles']))
        table.add_row("Operaciones realizadas", str(estadisticas['operaciones_realizadas']))
        
        if estadisticas['ultima_operacion']:
            table.add_row("Última operación", estadisticas['ultima_operacion']['herramienta'])
        
        console.print(table)
    
    def obtener_historial_operaciones(self, limite: int = 10) -> list:
        """
        Obtiene el historial de operaciones ofensivas.
        
        Args:
            limite (int): Número máximo de operaciones a retornar
            
        Returns:
            list: Lista de operaciones recientes
        """
        return self.historial_operaciones[-limite:] if self.historial_operaciones else []
    
    def limpiar_historial(self):
        """
        Limpia el historial de operaciones ofensivas.
        """
        operaciones_limpiadas = len(self.historial_operaciones)
        self.historial_operaciones.clear()
        
        console.print(Panel(f"🧹 Historial limpiado: {operaciones_limpiadas} operaciones removidas", style="yellow"))
        
        return operaciones_limpiadas 