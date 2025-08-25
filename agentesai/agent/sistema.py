"""
Sistema Principal - Coordina todos los agentes y maneja el flujo de trabajo
"""

import logging
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from .coordinador import AgenteCoordinador
from .ejecutor import AgenteEjecutor
from .generador import AgenteGenerador
from .registry import RegistryTools
from .ofensivo import AgenteOfensivo

console = Console()
logger = logging.getLogger(__name__)

class SistemaAgentes:
    """Sistema principal que coordina todos los agentes"""
    
    def __init__(self):
        self.coordinador = AgenteCoordinador()
        self.ejecutor = AgenteEjecutor()
        self.generador = AgenteGenerador()
        self.registry = RegistryTools()
        self.ofensivo = AgenteOfensivo()
        
        # Estado del sistema
        self.estado = "inicializado"
        self.consultas_procesadas = 0
        
        console.print(Panel("🚀 Sistema de Agentes AI inicializado", style="green"))
    
    def procesar_consulta(self, consulta: str) -> Dict[str, Any]:
        """
        Procesa una consulta completa usando el flujo completo de agentes.
        
        Esta es la función principal del sistema que orquesta todo el proceso
        de respuesta a consultas. Implementa el flujo completo:
        1. Análisis de la consulta por el coordinador
        2. Decisión de usar herramienta existente o generar nueva
        3. Ejecución o generación según corresponda
        4. Registro de resultados para auditoría
        
        Args:
            consulta (str): La consulta del usuario (ej: "¿quién soy?", "¿cuáles son todos los grupos?")
            
        Returns:
            Dict[str, Any]: Resultado del procesamiento con la siguiente estructura:
                - error (bool): True si hubo error, False si fue exitosa
                - tipo (str): Tipo de resultado ("herramienta_existente", "herramienta_generada", "error_generacion")
                - herramienta (str): Nombre de la herramienta utilizada
                - resultado: Resultado de la ejecución o generación
                - decision: Información de la decisión tomada por el coordinador
                - mensaje (str): Descripción del error (solo si error=True)
                
        Raises:
            No lanza excepciones, todas las excepciones son capturadas y retornadas
            como parte del diccionario de resultado.
            
        Note:
            Esta función mantiene el estado del sistema y contadores de consultas
            procesadas para monitoreo y debugging.
            
        Example:
            >>> sistema = SistemaAgentes()
            >>> resultado = sistema.procesar_consulta("¿quién soy?")
            >>> if not resultado["error"]:
            ...     print(f"Resultado: {resultado['resultado']}")
        """
        try:
            # Actualizar estado del sistema
            self.estado = "procesando"
            self.consultas_procesadas += 1
            
            console.print(Panel(f"🎯 Procesando consulta #{self.consultas_procesadas}: {consulta}", style="blue"))
            
            # Paso 1: El coordinador analiza la consulta y toma una decisión
            # Puede decidir usar una herramienta existente o generar una nueva
            decision = self.coordinador.analizar_consulta(consulta)
            
            # Paso 2: Ejecutar la decisión tomada
            if decision["accion"] == "ejecutar":
                # Verificar si es una herramienta ofensiva
                if decision["herramienta"] == "tool_rootdse_info":
                    resultado = self.ejecutar_herramienta_ofensiva("tool_rootdse_info")
                elif decision["herramienta"] == "tool_anonymous_enum":
                    resultado = self.ejecutar_herramienta_ofensiva("tool_anonymous_enum")
                elif decision["herramienta"] == "tool_starttls_test":
                    resultado = self.ejecutar_herramienta_ofensiva("tool_starttls_test")
                else:
                    # La consulta puede ser respondida con herramientas existentes
                    resultado = self._ejecutar_herramienta_existente(decision)
            else:
                # La consulta requiere generar una nueva herramienta
                resultado = self._generar_y_ejecutar_herramienta(decision)
            
            # Paso 3: Registrar la consulta y su resultado para auditoría
            self.coordinador.registrar_consulta(consulta, str(resultado))
            
            # Actualizar estado del sistema
            self.estado = "listo"
            return resultado
            
        except Exception as e:
            # Capturar cualquier error no esperado durante el procesamiento
            logger.error(f"Error procesando consulta: {e}")
            self.estado = "error"
            
            return {
                "error": True,
                "mensaje": f"Error procesando consulta: {str(e)}",
                "consulta": consulta
            }
    
    def _ejecutar_herramienta_existente(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta una herramienta existente
        """
        nombre_herramienta = decision["herramienta"]
        
        console.print(Panel(f"⚡ Ejecutando herramienta existente: {nombre_herramienta}", style="yellow"))
        
        # Ejecutar la herramienta
        resultado = self.ejecutor.ejecutar_herramienta(nombre_herramienta)
        
        # Registrar uso en registry
        if not resultado.get("error"):
            self.registry.incrementar_uso(nombre_herramienta)
        
        return {
            "tipo": "herramienta_existente",
            "herramienta": nombre_herramienta,
            "resultado": resultado,
            "decision": decision
        }
    
    def _generar_y_ejecutar_herramienta(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera una nueva herramienta y la ejecuta
        """
        consulta = decision["consulta"]
        tipo = decision["tipo_herramienta"]
        
        console.print(Panel(f"🤖 Generando nueva herramienta para: {consulta}", style="blue"))
        
        # Generar nueva herramienta
        resultado_generacion = self.generador.generar_herramienta(consulta, tipo)
        
        if resultado_generacion.get("error"):
            return {
                "tipo": "error_generacion",
                "error": True,
                "mensaje": resultado_generacion["mensaje"],
                "decision": decision
            }
        
        # Agregar al ejecutor
        nombre_herramienta = resultado_generacion["nombre"]
        funcion_generada = resultado_generacion["funcion"]
        
        self.ejecutor.agregar_herramienta_generada(nombre_herramienta, funcion_generada)
        
        # Registrar en registry
        metadata = {
            "tipo": tipo,
            "consulta_original": consulta,
            "codigo_generado": resultado_generacion["codigo"],
            "fecha_generacion": "ahora"  # TODO: usar datetime real
        }
        
        self.registry.registrar_herramienta(nombre_herramienta, metadata)
        
        # Registrar en coordinador
        self.coordinador.registrar_herramienta(nombre_herramienta)
        
        # Ejecutar la nueva herramienta
        resultado_ejecucion = self.ejecutor.ejecutar_herramienta(nombre_herramienta)
        
        return {
            "tipo": "herramienta_generada",
            "herramienta": nombre_herramienta,
            "resultado_generacion": resultado_generacion,
            "resultado_ejecucion": resultado_ejecucion,
            "decision": decision
        }
    
    def reset_sistema(self) -> Dict[str, Any]:
        """
        Resetea el sistema a su estado original
        """
        try:
            console.print(Panel("🔄 Reseteando sistema completo...", style="blue"))
            
            # Reset del ejecutor
            herramientas_removidas = self.ejecutor.reset_herramientas_generadas()
            
            # Reset del registry
            self.registry.reset_completo()
            
            # Reset del coordinador
            self.coordinador.herramientas_disponibles.clear()
            self.coordinador.historial_consultas.clear()
            
            # Reset del estado del sistema
            self.estado = "inicializado"
            self.consultas_procesadas = 0
            
            console.print(Panel("✅ Sistema reseteado completamente", style="green"))
            
            return {
                "error": False,
                "mensaje": "Sistema reseteado",
                "herramientas_removidas": herramientas_removidas
            }
            
        except Exception as e:
            logger.error(f"Error reseteando sistema: {e}")
            return {
                "error": True,
                "mensaje": f"Error en reset: {str(e)}"
            }
    
    def mostrar_estado_completo(self):
        """
        Muestra el estado completo del sistema
        """
        console.print(Panel("📊 Estado Completo del Sistema", style="bold blue"))
        
        # Estado general
        console.print(Panel(f"🔄 Estado: {self.estado}", style="cyan"))
        console.print(Panel(f"📈 Consultas procesadas: {self.consultas_procesadas}", style="cyan"))
        
        # Estado del coordinador
        console.print(Panel("🧠 Agente Coordinador", style="bold green"))
        stats_coordinador = self.coordinador.obtener_estadisticas()
        console.print(f"   Herramientas disponibles: {stats_coordinador['herramientas_disponibles']}")
        console.print(f"   Consultas procesadas: {stats_coordinador['consultas_procesadas']}")
        
        # Estado del ejecutor
        console.print(Panel("⚡ Agente Ejecutor", style="bold yellow"))
        self.ejecutor.mostrar_estado()
        
        # Estado del agente ofensivo
        console.print(Panel("🔴 Agente Ofensivo", style="bold red"))
        self.ofensivo.mostrar_estado()
        
        # Estado del registry
        console.print(Panel("📚 Registry de Tools", style="bold magenta"))
        self.registry.mostrar_estado()
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas completas del sistema
        """
        return {
            "estado": self.estado,
            "consultas_procesadas": self.consultas_procesadas,
            "coordinador": self.coordinador.obtener_estadisticas(),
            "ejecutor": self.ejecutor.listar_herramientas(),
            "ofensivo": self.ofensivo.obtener_estadisticas(),
            "registry": self.registry.obtener_estadisticas()
        }
    
    def ejecutar_herramienta_ofensiva(self, nombre: str, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta una herramienta ofensiva específica.
        
        Args:
            nombre (str): Nombre de la herramienta ofensiva
            **kwargs: Parámetros adicionales para la herramienta
            
        Returns:
            Dict[str, Any]: Resultado de la ejecución de la herramienta ofensiva
        """
        try:
            console.print(Panel(f"🔴 Ejecutando herramienta ofensiva: {nombre}", style="red"))
            
            resultado = self.ofensivo.ejecutar_herramienta_ofensiva(nombre, **kwargs)
            
            # Mostrar resultado formateado para herramientas específicas
            if nombre == "tool_starttls_test" and not resultado.get("error"):
                try:
                    from .tools_offensive.starttls_test import mostrar_resultado_starttls
                    mostrar_resultado_starttls(resultado)
                except ImportError:
                    console.print("⚠️ No se pudo importar la función de visualización")
            elif nombre == "tool_rootdse_info" and not resultado.get("error"):
                try:
                    from .tools_offensive.rootdse_info import mostrar_resultado_rootdse
                    mostrar_resultado_rootdse(resultado)
                except ImportError:
                    console.print("⚠️ No se pudo importar la función de visualización")
            elif nombre == "tool_anonymous_enum" and not resultado.get("error"):
                try:
                    from .tools_offensive.anonymous_enum import mostrar_resultado_enum
                    mostrar_resultado_enum(resultado)
                except ImportError:
                    console.print("⚠️ No se pudo importar la función de visualización")
            
            # Registrar la operación ofensiva
            self.coordinador.registrar_consulta(f"herramienta_ofensiva:{nombre}", str(resultado))
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error ejecutando herramienta ofensiva {nombre}: {e}")
            return {
                "error": True,
                "mensaje": f"Error ejecutando herramienta ofensiva {nombre}: {str(e)}",
                "herramienta": nombre
            }
    
    def modo_interactivo(self):
        """
        Activa el modo interactivo del sistema
        """
        console.print(Panel("🎮 Modo Interactivo Activado", style="bold green"))
        console.print("Escribe 'salir' para terminar, 'estado' para ver estado, 'reset' para resetear")
        
        while True:
            try:
                consulta = Prompt.ask("\n🤖 Tu consulta")
                
                if consulta.lower() in ['salir', 'exit', 'quit']:
                    console.print("👋 ¡Hasta luego!")
                    break
                elif consulta.lower() in ['estado', 'status']:
                    self.mostrar_estado_completo()
                elif consulta.lower() in ['reset', 'reseteo']:
                    self.reset_sistema()
                else:
                    resultado = self.procesar_consulta(consulta)
                    console.print(Panel(f"📝 Resultado: {resultado}", style="green"))
                    
            except KeyboardInterrupt:
                console.print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                console.print(Panel(f"❌ Error: {e}", style="red")) 