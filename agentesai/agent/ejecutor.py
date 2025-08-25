"""
Agente Ejecutor - Maneja y ejecuta las herramientas existentes
"""

import logging
from typing import Dict, Any, Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)

class AgenteEjecutor:
    """Agente que ejecuta las herramientas disponibles"""
    
    def __init__(self):
        self.herramientas = {}
        self.herramientas_base = {}
        self.herramientas_generadas = {}
        self._inicializar_herramientas_base()
    
    def _inicializar_herramientas_base(self):
        """Inicializa las herramientas base y adicionales del sistema"""
        from ..tools_base import (
            get_current_user_info, 
            get_user_groups, 
            reset_system,
            list_all_users,
            search_users_by_department,
            analyze_ldap_structure
        )
        
        self.herramientas_base = {
            # Herramientas obligatorias (requeridas por el challenge)
            "get_current_user_info": get_current_user_info,
            "get_user_groups": get_user_groups,
            "reset_system": reset_system,
            
            # Herramientas adicionales de seguridad ofensiva (datos reales del LDAP)
            "list_all_users": list_all_users,
            "search_users_by_department": search_users_by_department,
            "analyze_ldap_structure": analyze_ldap_structure
        }
        
        # Registrar en herramientas generales
        self.herramientas.update(self.herramientas_base)
        
        console.print(Panel(f"🔧 {len(self.herramientas_base)} herramientas base inicializadas con datos LDAP reales", style="green"))
    
    def ejecutar_herramienta(self, nombre: str, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta una herramienta específica por su nombre.
        
        Esta función es el núcleo del agente ejecutor. Busca la herramienta solicitada
        en el registro de herramientas disponibles y la ejecuta con los parámetros
        proporcionados. Maneja tanto herramientas base como generadas dinámicamente.
        
        Args:
            nombre (str): Nombre de la herramienta a ejecutar
            **kwargs: Parámetros adicionales que se pasarán a la herramienta
            
        Returns:
            Dict[str, Any]: Resultado de la ejecución con la siguiente estructura:
                - error (bool): True si hubo error, False si fue exitosa
                - herramienta (str): Nombre de la herramienta ejecutada
                - resultado: Valor retornado por la herramienta (si no hay error)
                - tipo (str): "base" o "generada" según el origen de la herramienta
                - mensaje (str): Descripción del error (solo si error=True)
                - herramientas_disponibles (list): Lista de herramientas disponibles (solo si error=True)
                
        Raises:
            No lanza excepciones, todas las excepciones son capturadas y retornadas
            como parte del diccionario de resultado.
            
        Example:
            >>> resultado = ejecutor.ejecutar_herramienta("get_current_user_info")
            >>> if not resultado["error"]:
            ...     print(f"Usuario: {resultado['resultado']}")
        """
        # Verificar si la herramienta existe
        if nombre not in self.herramientas:
            return {
                "error": True,
                "mensaje": f"Herramienta '{nombre}' no encontrada",
                "herramientas_disponibles": list(self.herramientas.keys())
            }
        
        try:
            console.print(Panel(f"⚡ Ejecutando herramienta: {nombre}", style="yellow"))
            
            # Ejecutar la herramienta con los parámetros proporcionados
            # La herramienta puede ser una función base o generada dinámicamente
            resultado = self.herramientas[nombre](**kwargs)
            
            # Determinar el tipo de herramienta para el registro
            tipo_herramienta = "base" if nombre in self.herramientas_base else "generada"
            
            return {
                "error": False,
                "herramienta": nombre,
                "resultado": resultado,
                "tipo": tipo_herramienta
            }
            
        except Exception as e:
            # Capturar cualquier error durante la ejecución
            logger.error(f"Error ejecutando herramienta {nombre}: {e}")
            return {
                "error": True,
                "mensaje": f"Error ejecutando {nombre}: {str(e)}",
                "herramienta": nombre
            }
    
    def agregar_herramienta_generada(self, nombre: str, funcion: Callable):
        """
        Agrega una nueva herramienta generada dinámicamente
        """
        self.herramientas_generadas[nombre] = funcion
        self.herramientas[nombre] = funcion
        
        console.print(Panel(f"🆕 Herramienta generada agregada: {nombre}", style="green"))
        
        return True
    
    def remover_herramienta_generada(self, nombre: str) -> bool:
        """
        Remueve una herramienta generada
        """
        if nombre in self.herramientas_generadas:
            del self.herramientas_generadas[nombre]
            del self.herramientas[nombre]
            
            console.print(Panel(f"🗑️ Herramienta removida: {nombre}", style="red"))
            return True
        
        return False
    
    def reset_herramientas_generadas(self):
        """
        Resetea todas las herramientas generadas al estado original
        """
        herramientas_removidas = list(self.herramientas_generadas.keys())
        
        for nombre in herramientas_removidas:
            self.remover_herramienta_generada(nombre)
        
        console.print(Panel(f"🔄 Reset completado. {len(herramientas_removidas)} herramientas removidas", style="blue"))
        
        return len(herramientas_removidas)
    
    def listar_herramientas(self) -> Dict[str, Any]:
        """
        Lista todas las herramientas disponibles
        """
        return {
            "base": list(self.herramientas_base.keys()),
            "generadas": list(self.herramientas_generadas.keys()),
            "total": len(self.herramientas),
            "base_count": len(self.herramientas_base),
            "generadas_count": len(self.herramientas_generadas)
        }
    
    def mostrar_estado(self):
        """
        Muestra el estado actual del agente ejecutor
        """
        estado = self.listar_herramientas()
        
        table = Table(title="Estado del Agente Ejecutor")
        table.add_column("Categoría", style="cyan")
        table.add_column("Cantidad", style="magenta")
        table.add_column("Herramientas", style="green")
        
        table.add_row("Base", str(estado["base_count"]), ", ".join(estado["base"]))
        table.add_row("Generadas", str(estado["generadas_count"]), ", ".join(estado["generadas"]))
        table.add_row("Total", str(estado["total"]), "")
        
        console.print(table) 