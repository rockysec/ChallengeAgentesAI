"""
Registry de Tools - Sistema de registro y gestión de herramientas
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)

class RegistryTools:
    """Sistema de registro y gestión de herramientas"""
    
    def __init__(self, archivo_registro: str = "tools_registry.json"):
        self.archivo_registro = archivo_registro
        self.herramientas_registradas = {}
        self.historial_herramientas = []
        self.cargar_registro()
    
    def cargar_registro(self):
        """Carga el registro desde archivo"""
        try:
            if os.path.exists(self.archivo_registro):
                with open(self.archivo_registro, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    self.herramientas_registradas = datos.get('herramientas', {})
                    self.historial_herramientas = datos.get('historial', [])
                
                console.print(Panel(f"📚 Registry cargado: {len(self.herramientas_registradas)} herramientas", style="green"))
            else:
                console.print(Panel("📚 Creando nuevo registry de herramientas", style="blue"))
                
        except Exception as e:
            logger.error(f"Error cargando registry: {e}")
            console.print(Panel(f"❌ Error cargando registry: {e}", style="red"))
    
    def guardar_registro(self):
        """Guarda el registro en archivo"""
        try:
            datos = {
                'herramientas': self.herramientas_registradas,
                'historial': self.historial_herramientas,
                'ultima_actualizacion': datetime.now().isoformat()
            }
            
            with open(self.archivo_registro, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            console.print(Panel("💾 Registry guardado exitosamente", style="green"))
            
        except Exception as e:
            logger.error(f"Error guardando registry: {e}")
            console.print(Panel(f"❌ Error guardando registry: {e}", style="red"))
    
    def registrar_herramienta(self, nombre: str, metadata: Dict[str, Any]) -> bool:
        """
        Registra una nueva herramienta en el registry del sistema.
        
        Esta función es fundamental para el sistema de auto-expansión. Cada vez que
        se genera una nueva herramienta, debe ser registrada aquí para mantener
        un inventario completo de todas las funcionalidades disponibles.
        
        Args:
            nombre (str): Nombre único de la herramienta (ej: "get_user_groups_abc123")
            metadata (Dict[str, Any]): Metadatos de la herramienta que incluyen:
                - tipo: Tipo de herramienta ("ldap_query", "generic_query", etc.)
                - consulta_original: La consulta que originó la herramienta
                - codigo_generado: Código fuente de la herramienta
                - fecha_generacion: Cuándo fue generada
                
        Returns:
            bool: True si el registro fue exitoso, False si hubo error
            
        Raises:
            No lanza excepciones, todas las excepciones son capturadas y retornadas
            como False.
            
        Note:
            La función agrega automáticamente metadatos adicionales como:
            - fecha_registro: Timestamp del registro
            - estado: Siempre "activa" para nuevas herramientas
            - uso_count: Contador de uso inicializado en 0
            
            También actualiza el historial y guarda el registry en disco.
            
        Example:
            >>> metadata = {
            ...     "tipo": "ldap_query",
            ...     "consulta_original": "¿cuáles son todos los grupos?",
            ...     "codigo_generado": "def get_groups(): return 'grupos...'"
            ... }
            >>> success = registry.registrar_herramienta("get_groups_abc123", metadata)
        """
        try:
            # Agregar metadatos adicionales automáticamente
            metadata_completa = {
                **metadata,  # Metadatos originales
                'fecha_registro': datetime.now().isoformat(),  # Timestamp del registro
                'estado': 'activa',  # Estado inicial siempre activo
                'uso_count': 0  # Contador de uso inicializado
            }
            
            # Registrar en el diccionario principal de herramientas
            self.herramientas_registradas[nombre] = metadata_completa
            
            # Registrar en el historial para auditoría
            self.historial_herramientas.append({
                'accion': 'registro',
                'herramienta': nombre,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata
            })
            
            console.print(Panel(f"✅ Herramienta registrada: {nombre}", style="green"))
            
            # Persistir cambios en disco automáticamente
            self.guardar_registro()
            
            return True
            
        except Exception as e:
            # Log del error para debugging
            logger.error(f"Error registrando herramienta {nombre}: {e}")
            return False
    
    def desregistrar_herramienta(self, nombre: str) -> bool:
        """
        Desregistra una herramienta del registry
        """
        if nombre in self.herramientas_registradas:
            # Marcar como inactiva
            self.herramientas_registradas[nombre]['estado'] = 'inactiva'
            self.herramientas_registradas[nombre]['fecha_desregistro'] = datetime.now().isoformat()
            
            # Registrar en historial
            self.historial_herramientas.append({
                'accion': 'desregistro',
                'herramienta': nombre,
                'timestamp': datetime.now().isoformat()
            })
            
            console.print(Panel(f"🗑️ Herramienta desregistrada: {nombre}", style="yellow"))
            
            # Guardar automáticamente
            self.guardar_registro()
            
            return True
        
        return False
    
    def obtener_herramienta(self, nombre: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de una herramienta específica
        """
        return self.herramientas_registradas.get(nombre)
    
    def listar_herramientas(self, filtro_estado: str = None) -> Dict[str, Any]:
        """
        Lista todas las herramientas con filtros opcionales
        """
        if filtro_estado:
            herramientas_filtradas = {
                nombre: datos for nombre, datos in self.herramientas_registradas.items()
                if datos.get('estado') == filtro_estado
            }
        else:
            herramientas_filtradas = self.herramientas_registradas
        
        return {
            'total': len(herramientas_filtradas),
            'herramientas': herramientas_filtradas,
            'filtro_aplicado': filtro_estado
        }
    
    def incrementar_uso(self, nombre: str):
        """
        Incrementa el contador de uso de una herramienta
        """
        if nombre in self.herramientas_registradas:
            self.herramientas_registradas[nombre]['uso_count'] += 1
            self.herramientas_registradas[nombre]['ultimo_uso'] = datetime.now().isoformat()
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del registry
        """
        herramientas_activas = sum(1 for h in self.herramientas_registradas.values() if h.get('estado') == 'activa')
        herramientas_inactivas = sum(1 for h in self.herramientas_registradas.values() if h.get('estado') == 'inactiva')
        
        total_uso = sum(h.get('uso_count', 0) for h in self.herramientas_registradas.values())
        
        return {
            'total_herramientas': len(self.herramientas_registradas),
            'activas': herramientas_activas,
            'inactivas': herramientas_inactivas,
            'total_uso': total_uso,
            'promedio_uso': total_uso / len(self.herramientas_registradas) if self.herramientas_registradas else 0
        }
    
    def mostrar_estado(self):
        """
        Muestra el estado actual del registry
        """
        estadisticas = self.obtener_estadisticas()
        
        table = Table(title="Estado del Registry de Tools")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="magenta")
        
        table.add_row("Total de herramientas", str(estadisticas['total_herramientas']))
        table.add_row("Herramientas activas", str(estadisticas['activas']))
        table.add_row("Herramientas inactivas", str(estadisticas['inactivas']))
        table.add_row("Total de uso", str(estadisticas['total_uso']))
        table.add_row("Promedio de uso", f"{estadisticas['promedio_uso']:.2f}")
        
        console.print(table)
    
    def reset_completo(self):
        """
        Resetea completamente el registry
        """
        self.herramientas_registradas = {}
        self.historial_herramientas = []
        
        # Eliminar archivo de registro
        if os.path.exists(self.archivo_registro):
            os.remove(self.archivo_registro)
        
        console.print(Panel("🔄 Registry reseteado completamente", style="blue"))
    
    def exportar_registry(self, archivo_destino: str = None) -> str:
        """
        Exporta el registry a un archivo
        """
        if not archivo_destino:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_destino = f"registry_export_{timestamp}.json"
        
        try:
            datos_exportacion = {
                'herramientas': self.herramientas_registradas,
                'historial': self.historial_herramientas,
                'estadisticas': self.obtener_estadisticas(),
                'fecha_exportacion': datetime.now().isoformat()
            }
            
            with open(archivo_destino, 'w', encoding='utf-8') as f:
                json.dump(datos_exportacion, f, indent=2, ensure_ascii=False)
            
            console.print(Panel(f"📤 Registry exportado a: {archivo_destino}", style="green"))
            return archivo_destino
            
        except Exception as e:
            logger.error(f"Error exportando registry: {e}")
            console.print(Panel(f"❌ Error exportando: {e}", style="red"))
            return "" 