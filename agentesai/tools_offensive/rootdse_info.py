"""
Herramienta ofensiva: Análisis RootDSE LDAP
"""

import logging
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)

def tool_rootdse_info(server: str = None, base_dn: str = None, username: str = None, password: str = None) -> Dict[str, Any]:
    """
    Consulta RootDSE para obtener información crítica del servidor LDAP.
    
    Esta herramienta realiza una consulta anónima al RootDSE (Root Directory Service Entry)
    para extraer información valiosa para reconocimiento y análisis de seguridad:
    
    - namingContexts: Contextos de nombres disponibles
    - supportedExtension: Extensiones soportadas
    - supportedControl: Controles soportados
    - supportedSASLMechanisms: Mecanismos SASL soportados
    - supportedLDAPVersion: Versiones de LDAP soportadas
    - vendorName: Información del proveedor
    - vendorVersion: Versión del proveedor
    
    Args:
        server (str, optional): Servidor LDAP (por defecto usa configuración del sistema)
        base_dn (str, optional): DN base (por defecto usa configuración del sistema)
        username (str, optional): Usuario para autenticación (opcional)
        password (str, optional): Contraseña para autenticación (opcional)
        
    Returns:
        Dict[str, Any]: Información detallada del RootDSE con metadatos de seguridad
        
    Raises:
        No lanza excepciones, todas las excepciones son capturadas y retornadas
        como parte del diccionario de resultado.
        
    Example:
        >>> resultado = tool_rootdse_info()
        >>> if not resultado["error"]:
        ...     print(f"Naming Contexts: {resultado['resultado']['namingContexts']}")
    """
    try:
        console.print(Panel("🔴 Iniciando análisis RootDSE LDAP", style="red"))
        
        # Importar el conector LDAP
        from ..tools_base.ldap_connector import LDAPConnector
        
        # Crear conexión LDAP
        ldap_conn = LDAPConnector()
        
        # Conectar al servidor
        if not ldap_conn.connect():
            return {
                "error": True,
                "mensaje": "No se pudo conectar al servidor LDAP",
                "herramienta": "tool_rootdse_info",
                "tipo": "error_conexion"
            }
        
        try:
            # Consultar RootDSE (DN vacío o ".")
            console.print(Panel("🔍 Consultando RootDSE...", style="blue"))
            
            # Realizar búsqueda en RootDSE
            resultado_busqueda = ldap_conn.search("", "(objectClass=*)")
            
            if not resultado_busqueda:
                return {
                    "error": True,
                    "mensaje": "No se pudo obtener información del RootDSE",
                    "herramienta": "tool_rootdse_info",
                    "tipo": "error_busqueda"
                }
            
            # Procesar resultados del RootDSE
            rootdse_info = _procesar_rootdse(resultado_busqueda)
            
            # Análisis de seguridad
            analisis_seguridad = _analizar_seguridad_rootdse(rootdse_info)
            
            # Resultado final
            resultado_completo = {
                "rootdse_info": rootdse_info,
                "analisis_seguridad": analisis_seguridad,
                "metadata": {
                    "herramienta": "tool_rootdse_info",
                    "tipo": "analisis_ldap",
                    "categoria": "reconocimiento",
                    "riesgo": "bajo",  # Consulta anónima estándar
                    "timestamp": "ahora"  # TODO: usar datetime real
                }
            }
            
            console.print(Panel("✅ Análisis RootDSE completado exitosamente", style="green"))
            
            return {
                "error": False,
                "resultado": resultado_completo,
                "herramienta": "tool_rootdse_info",
                "tipo": "analisis_ldap"
            }
            
        finally:
            # Siempre desconectar
            ldap_conn.disconnect()
            
    except Exception as e:
        logger.error(f"Error en tool_rootdse_info: {e}")
        return {
            "error": True,
            "mensaje": f"Error ejecutando análisis RootDSE: {str(e)}",
            "herramienta": "tool_rootdse_info",
            "tipo": "error_ejecucion"
        }

def _procesar_rootdse(resultado_busqueda: List[Dict]) -> Dict[str, Any]:
    """
    Procesa los resultados del RootDSE para extraer información relevante.
    
    Args:
        resultado_busqueda (List[Dict]): Resultados de la búsqueda RootDSE
        
    Returns:
        Dict[str, Any]: Información procesada del RootDSE
    """
    rootdse_data = {}
    
    # Procesar cada entrada del RootDSE
    for entrada in resultado_busqueda:
        for atributo, valores in entrada.items():
            if atributo.lower() not in ['dn', 'distinguishedname']:
                # Normalizar nombres de atributos
                atributo_normalizado = atributo.lower()
                
                # Convertir valores a string si es necesario
                if isinstance(valores, list):
                    valores_procesados = [str(v) for v in valores]
                else:
                    valores_procesados = [str(valores)]
                
                rootdse_data[atributo_normalizado] = valores_procesados
    
    # Atributos críticos para análisis de seguridad
    atributos_criticos = {
        'namingcontexts': rootdse_data.get('namingcontexts', []),
        'supportedextension': rootdse_data.get('supportedextension', []),
        'supportedcontrol': rootdse_data.get('supportedcontrol', []),
        'supportedsaslmechanisms': rootdse_data.get('supportedsaslmechanisms', []),
        'supportedldapversion': rootdse_data.get('supportedldapversion', []),
        'vendorname': rootdse_data.get('vendorname', []),
        'vendorversion': rootdse_data.get('vendorversion', []),
        'subschemasubentry': rootdse_data.get('subschemasubentry', []),
        'altserver': rootdse_data.get('altserver', []),
        'supportedfeatures': rootdse_data.get('supportedfeatures', []),
        'supportedldapversion': rootdse_data.get('supportedldapversion', []),
        'supportedldapversion': rootdse_data.get('supportedldapversion', [])
    }
    
    return {
        "atributos_completos": rootdse_data,
        "atributos_criticos": atributos_criticos,
        "total_atributos": len(rootdse_data)
    }

def _analizar_seguridad_rootdse(rootdse_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analiza la información del RootDSE desde una perspectiva de seguridad.
    
    Args:
        rootdse_info (Dict[str, Any]): Información procesada del RootDSE
        
    Returns:
        Dict[str, Any]: Análisis de seguridad del RootDSE
    """
    analisis = {
        "riesgos_detectados": [],
        "vulnerabilidades_potenciales": [],
        "recomendaciones": [],
        "nivel_riesgo": "bajo"
    }
    
    atributos_criticos = rootdse_info.get("atributos_criticos", {})
    
    # Análisis de naming contexts
    naming_contexts = atributos_criticos.get('namingcontexts', [])
    if len(naming_contexts) > 1:
        analisis["riesgos_detectados"].append("Múltiples contextos de nombres detectados")
        analisis["recomendaciones"].append("Revisar permisos de acceso a cada contexto")
    
    # Análisis de extensiones soportadas
    supported_extensions = atributos_criticos.get('supportedextension', [])
    if supported_extensions:
        analisis["riesgos_detectados"].append(f"Extensiones LDAP habilitadas: {len(supported_extensions)}")
        analisis["recomendaciones"].append("Revisar si todas las extensiones son necesarias")
    
    # Análisis de controles soportados
    supported_controls = atributos_criticos.get('supportedcontrol', [])
    if supported_controls:
        analisis["riesgos_detectados"].append(f"Controles LDAP habilitados: {len(supported_controls)}")
        analisis["recomendaciones"].append("Verificar controles de seguridad críticos")
    
    # Análisis de mecanismos SASL
    sasl_mechanisms = atributos_criticos.get('supportedsaslmechanisms', [])
    if 'PLAIN' in sasl_mechanisms or 'LOGIN' in sasl_mechanisms:
        analisis["riesgos_detectados"].append("Mecanismos SASL débiles detectados (PLAIN/LOGIN)")
        analisis["vulnerabilidades_potenciales"].append("Autenticación en texto plano")
        analisis["nivel_riesgo"] = "medio"
        analisis["recomendaciones"].append("Deshabilitar mecanismos SASL débiles")
    
    # Análisis de versiones soportadas
    ldap_versions = atributos_criticos.get('supportedldapversion', [])
    if '2' in ldap_versions:
        analisis["riesgos_detectados"].append("LDAP v2 soportado (obsoleto e inseguro)")
        analisis["vulnerabilidades_potenciales"].append("LDAP v2 sin autenticación")
        analisis["nivel_riesgo"] = "alto"
        analisis["recomendaciones"].append("Deshabilitar soporte para LDAP v2")
    
    # Análisis de servidores alternativos
    alt_servers = atributos_criticos.get('altserver', [])
    if alt_servers:
        analisis["riesgos_detectados"].append(f"Servidores alternativos detectados: {len(alt_servers)}")
        analisis["recomendaciones"].append("Verificar configuración de servidores alternativos")
    
    # Información del proveedor
    vendor_name = atributos_criticos.get('vendorname', [])
    vendor_version = atributos_criticos.get('vendorversion', [])
    if vendor_name and vendor_version:
        analisis["riesgos_detectados"].append(f"Proveedor: {vendor_name[0]} {vendor_version[0]}")
        analisis["recomendaciones"].append("Verificar si hay vulnerabilidades conocidas para esta versión")
    
    return analisis

def mostrar_resultado_rootdse(resultado: Dict[str, Any]):
    """
    Muestra el resultado del análisis RootDSE de manera formateada.
    
    Args:
        resultado (Dict[str, Any]): Resultado de tool_rootdse_info
    """
    if resultado.get("error"):
        console.print(Panel(f"❌ Error: {resultado['mensaje']}", style="red"))
        return
    
    data = resultado["resultado"]
    rootdse_info = data["rootdse_info"]
    analisis_seguridad = data["analisis_seguridad"]
    
    # Mostrar información del RootDSE
    console.print(Panel("📊 Información RootDSE", style="bold blue"))
    
    # Tabla de atributos críticos
    table_criticos = Table(title="Atributos Críticos")
    table_criticos.add_column("Atributo", style="cyan")
    table_criticos.add_column("Valor", style="green")
    
    for atributo, valores in rootdse_info["atributos_criticos"].items():
        if valores:
            table_criticos.add_row(atributo, ", ".join(valores))
    
    console.print(table_criticos)
    
    # Mostrar análisis de seguridad
    console.print(Panel("🔒 Análisis de Seguridad", style="bold red"))
    
    table_seguridad = Table(title="Análisis de Seguridad")
    table_seguridad.add_column("Categoría", style="cyan")
    table_criticos.add_column("Detalles", style="yellow")
    
    table_seguridad.add_row("Nivel de Riesgo", analisis_seguridad["nivel_riesgo"].upper())
    table_seguridad.add_row("Riesgos Detectados", str(len(analisis_seguridad["riesgos_detectados"])))
    table_seguridad.add_row("Vulnerabilidades", str(len(analisis_seguridad["vulnerabilidades_potenciales"])))
    
    console.print(table_seguridad)
    
    # Mostrar recomendaciones
    if analisis_seguridad["recomendaciones"]:
        console.print(Panel("💡 Recomendaciones de Seguridad", style="bold yellow"))
        for i, rec in enumerate(analisis_seguridad["recomendaciones"], 1):
            console.print(f"{i}. {rec}") 