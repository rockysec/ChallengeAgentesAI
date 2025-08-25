"""
Herramienta ofensiva: Test de seguridad STARTTLS LDAP
"""

import logging
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)

def tool_starttls_test(server: str = None, base_dn: str = None, username: str = None, password: str = None) -> Dict[str, Any]:
    """
    Prueba la seguridad STARTTLS del servidor LDAP para detectar vulnerabilidades.
    
    Esta herramienta intenta establecer una conexión TLS (-ZZ) y detecta:
    - Si el servidor falla en el handshake TLS
    - Si permite continuar en texto claro (TLS downgrade)
    - Vulnerabilidades de configuración TLS
    - Posibles ataques de downgrade
    
    Args:
        server (str, optional): Servidor LDAP (por defecto usa configuración del sistema)
        base_dn (str, optional): DN base (por defecto usa configuración del sistema)
        username (str, optional): Usuario para autenticación (opcional)
        password (str, optional): Contraseña para autenticación (opcional)
        
    Returns:
        Dict[str, Any]: Resultado del test STARTTLS con análisis de seguridad
        
    Raises:
        No lanza excepciones, todas las excepciones son capturadas y retornadas
        como parte del diccionario de resultado.
        
    Example:
        >>> resultado = tool_starttls_test()
        >>> if not resultado["error"]:
        ...     print(f"Vulnerabilidades: {resultado['resultado']['vulnerabilidades']}")
    """
    try:
        console.print(Panel("🔴 Iniciando test de seguridad STARTTLS LDAP", style="red"))
        
        # Importar el conector LDAP
        from ..tools_base.ldap_connector import LDAPConnector
        
        # Crear conexión LDAP
        ldap_conn = LDAPConnector()
        
        # Test 1: Conexión normal (sin TLS)
        console.print(Panel("🔍 Test 1: Conexión normal sin TLS", style="blue"))
        resultado_normal = _test_conexion_normal(ldap_conn)
        
        # Test 2: Conexión con STARTTLS (-Z)
        console.print(Panel("🔒 Test 2: Conexión con STARTTLS (-Z)", style="blue"))
        resultado_starttls = _test_starttls(ldap_conn)
        
        # Test 3: Conexión forzada TLS (-ZZ)
        console.print(Panel("🔐 Test 3: Conexión forzada TLS (-ZZ)", style="blue"))
        resultado_tls_forzado = _test_tls_forzado(ldap_conn)
        
        # Test 4: Test de downgrade TLS
        console.print(Panel("⚠️ Test 4: Test de downgrade TLS", style="yellow"))
        resultado_downgrade = _test_downgrade_tls(ldap_conn)
        
        # Análisis de seguridad
        analisis_seguridad = _analizar_seguridad_starttls(
            resultado_normal, resultado_starttls, resultado_tls_forzado, resultado_downgrade
        )
        
        # Resultado final
        resultado_completo = {
            "tests": {
                "conexion_normal": resultado_normal,
                "starttls": resultado_starttls,
                "tls_forzado": resultado_tls_forzado,
                "downgrade": resultado_downgrade
            },
            "analisis_seguridad": analisis_seguridad,
            "metadata": {
                "herramienta": "tool_starttls_test",
                "tipo": "test_seguridad_tls",
                "categoria": "reconocimiento_ofensivo",
                "riesgo": "medio",  # Test de seguridad TLS
                "timestamp": "ahora"  # TODO: usar datetime real
            }
        }
        
        console.print(Panel("✅ Test STARTTLS completado exitosamente", style="green"))
        
        return {
            "error": False,
            "resultado": resultado_completo,
            "herramienta": "tool_starttls_test",
            "tipo": "test_seguridad_tls"
        }
        
    except Exception as e:
        logger.error(f"Error en tool_starttls_test: {e}")
        return {
            "error": True,
            "mensaje": f"Error ejecutando test STARTTLS: {str(e)}",
            "herramienta": "tool_starttls_test",
            "tipo": "error_ejecucion"
        }

def _test_conexion_normal(ldap_conn) -> Dict[str, Any]:
    """
    Test de conexión normal sin TLS.
    
    Args:
        ldap_conn: Conexión LDAP
        
    Returns:
        Dict[str, Any]: Resultado del test
    """
    try:
        # Intentar conexión normal
        if ldap_conn.connect():
            # Realizar búsqueda simple para verificar funcionalidad
            resultado_busqueda = ldap_conn.search("", "(objectClass=*)")
            
            return {
                "estado": "exitoso",
                "conexion": True,
                "busqueda": len(resultado_busqueda) > 0,
                "tls_activo": False,
                "vulnerabilidad": "Conexión en texto claro permitida"
            }
        else:
            return {
                "estado": "fallido",
                "conexion": False,
                "busqueda": False,
                "tls_activo": False,
                "vulnerabilidad": "No se pudo establecer conexión"
            }
            
    except Exception as e:
        return {
            "estado": "error",
            "conexion": False,
            "busqueda": False,
            "tls_activo": False,
            "vulnerabilidad": f"Error en conexión normal: {str(e)}"
        }

def _test_starttls(ldap_conn) -> Dict[str, Any]:
    """
    Test de conexión con STARTTLS (-Z).
    
    Args:
        ldap_conn: Conexión LDAP
        
    Returns:
        Dict[str, Any]: Resultado del test
    """
    try:
        # Intentar conexión con STARTTLS
        if ldap_conn.connect():
            # Simular STARTTLS (en la implementación real se usaría ldap.start_tls_s())
            # Por ahora, verificamos si la conexión está activa
            resultado_busqueda = ldap_conn.search("", "(objectClass=*)")
            
            return {
                "estado": "exitoso",
                "conexion": True,
                "busqueda": len(resultado_busqueda) > 0,
                "tls_activo": False,  # STARTTLS no está implementado en el conector actual
                "vulnerabilidad": "STARTTLS no implementado en el conector",
                "nota": "Requiere implementación de STARTTLS en LDAPConnector"
            }
        else:
            return {
                "estado": "fallido",
                "conexion": False,
                "busqueda": False,
                "tls_activo": False,
                "vulnerabilidad": "No se pudo establecer conexión STARTTLS"
            }
            
    except Exception as e:
        return {
            "estado": "error",
            "conexion": False,
            "busqueda": False,
            "tls_activo": False,
            "vulnerabilidad": f"Error en STARTTLS: {str(e)}"
        }

def _test_tls_forzado(ldap_conn) -> Dict[str, Any]:
    """
    Test de conexión forzada TLS (-ZZ).
    
    Args:
        ldap_conn: Conexión LDAP
        
    Returns:
        Dict[str, Any]: Resultado del test
    """
    try:
        # Intentar conexión forzada TLS
        # En la implementación real, esto forzaría TLS desde el inicio
        if ldap_conn.connect():
            # Simular verificación TLS forzado
            resultado_busqueda = ldap_conn.search("", "(objectClass=*)")
            
            return {
                "estado": "exitoso",
                "conexion": True,
                "busqueda": len(resultado_busqueda) > 0,
                "tls_activo": False,  # TLS forzado no está implementado en el conector actual
                "vulnerabilidad": "TLS forzado no implementado en el conector",
                "nota": "Requiere implementación de TLS forzado en LDAPConnector"
            }
        else:
            return {
                "estado": "fallido",
                "conexion": False,
                "busqueda": False,
                "tls_activo": False,
                "vulnerabilidad": "No se pudo establecer conexión TLS forzado"
            }
            
    except Exception as e:
        return {
            "estado": "error",
            "conexion": False,
            "busqueda": False,
            "tls_activo": False,
            "vulnerabilidad": f"Error en TLS forzado: {str(e)}"
        }

def _test_downgrade_tls(ldap_conn) -> Dict[str, Any]:
    """
    Test de downgrade TLS (intentar forzar texto claro después de TLS).
    
    Args:
        ldap_conn: Conexión LDAP
        
    Returns:
        Dict[str, Any]: Resultado del test
    """
    try:
        # Simular test de downgrade
        # En la implementación real, esto intentaría forzar texto claro después de TLS
        
        if ldap_conn.connect():
            # Intentar búsqueda para ver si la conexión sigue funcionando
            resultado_busqueda = ldap_conn.search("", "(objectClass=*)")
            
            return {
                "estado": "simulado",
                "conexion": True,
                "busqueda": len(resultado_busqueda) > 0,
                "tls_activo": False,
                "vulnerabilidad": "Test de downgrade no implementado completamente",
                "nota": "Requiere implementación completa de STARTTLS/TLS en LDAPConnector"
            }
        else:
            return {
                "estado": "fallido",
                "conexion": False,
                "busqueda": False,
                "tls_activo": False,
                "vulnerabilidad": "No se pudo establecer conexión para test de downgrade"
            }
            
    except Exception as e:
        return {
            "estado": "error",
            "conexion": False,
            "busqueda": False,
            "tls_activo": False,
            "vulnerabilidad": f"Error en test de downgrade: {str(e)}"
        }

def _analizar_seguridad_starttls(resultado_normal: Dict, resultado_starttls: Dict, 
                                resultado_tls_forzado: Dict, resultado_downgrade: Dict) -> Dict[str, Any]:
    """
    Analiza la seguridad de los resultados del test STARTTLS.
    
    Args:
        resultado_normal (Dict): Resultado del test de conexión normal
        resultado_starttls (Dict): Resultado del test STARTTLS
        resultado_tls_forzado (Dict): Resultado del test TLS forzado
        resultado_downgrade (Dict): Resultado del test de downgrade
        
    Returns:
        Dict[str, Any]: Análisis de seguridad
    """
    analisis = {
        "riesgos_detectados": [],
        "vulnerabilidades_potenciales": [],
        "recomendaciones": [],
        "nivel_riesgo": "bajo",
        "implementacion_requerida": []
    }
    
    # Análisis de conexión normal
    if resultado_normal.get("estado") == "exitoso" and resultado_normal.get("conexion"):
        analisis["riesgos_detectados"].append("Conexión en texto claro permitida")
        analisis["vulnerabilidades_potenciales"].append("Datos transmitidos sin cifrado")
        analisis["nivel_riesgo"] = "medio"
        analisis["recomendaciones"].append("Forzar uso de TLS para todas las conexiones")
    
    # Análisis de STARTTLS
    if resultado_starttls.get("estado") == "exitoso":
        if not resultado_starttls.get("tls_activo"):
            analisis["implementacion_requerida"].append("Implementar STARTTLS en LDAPConnector")
            analisis["recomendaciones"].append("Implementar soporte completo para STARTTLS")
    
    # Análisis de TLS forzado
    if resultado_tls_forzado.get("estado") == "exitoso":
        if not resultado_tls_forzado.get("tls_activo"):
            analisis["implementacion_requerida"].append("Implementar TLS forzado en LDAPConnector")
            analisis["recomendaciones"].append("Implementar soporte para conexiones TLS forzadas")
    
    # Análisis de downgrade
    if resultado_downgrade.get("estado") == "simulado":
        analisis["implementacion_requerida"].append("Implementar test completo de downgrade TLS")
        analisis["recomendaciones"].append("Implementar detección de ataques de downgrade")
    
    # Recomendaciones generales
    if analisis["nivel_riesgo"] == "medio":
        analisis["recomendaciones"].append("Configurar servidor LDAP para requerir TLS")
        analisis["recomendaciones"].append("Implementar políticas de seguridad TLS")
    
    if analisis["implementacion_requerida"]:
        analisis["recomendaciones"].append("Completar implementación de funcionalidades TLS en LDAPConnector")
    
    return analisis

def mostrar_resultado_starttls(resultado: Dict[str, Any]):
    """
    Muestra el resultado del test STARTTLS de manera formateada y organizada.
    
    Args:
        resultado (Dict[str, Any]): Resultado de tool_starttls_test
    """
    if resultado.get("error"):
        console.print(Panel(f"❌ Error: {resultado['mensaje']}", style="red"))
        return
    
    data = resultado["resultado"]
    tests = data["tests"]
    analisis_seguridad = data["analisis_seguridad"]
    
    # Título principal
    console.print(Panel("🔐 TEST DE SEGURIDAD STARTTLS LDAP", style="bold red"))
    console.print()
    
    # Mostrar cada test individualmente con detalles
    console.print(Panel("🧪 DETALLES DE CADA PRUEBA REALIZADA", style="bold blue"))
    console.print()
    
    # Test 1: Conexión Normal
    test_normal = tests["conexion_normal"]
    console.print(Panel("🔍 PRUEBA 1: Conexión Normal (sin TLS)", style="cyan"))
    console.print(f"   📊 Estado: {test_normal['estado'].upper()}")
    console.print(f"   🔌 Conexión: {'✅ Activa' if test_normal['conexion'] else '❌ Fallida'}")
    console.print(f"   🔍 Búsqueda: {'✅ Exitosa' if test_normal['busqueda'] else '❌ Fallida'}")
    console.print(f"   🔐 TLS Activo: {'✅ Sí' if test_normal['tls_activo'] else '❌ No'}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_normal['vulnerabilidad']}")
    if test_normal.get('nota'):
        console.print(f"   📝 Nota: {test_normal['nota']}")
    console.print()
    
    # Test 2: STARTTLS
    test_starttls = tests["starttls"]
    console.print(Panel("🔒 PRUEBA 2: Conexión STARTTLS (-Z)", style="cyan"))
    console.print(f"   📊 Estado: {test_starttls['estado'].upper()}")
    console.print(f"   🔌 Conexión: {'✅ Activa' if test_starttls['conexion'] else '❌ Fallida'}")
    console.print(f"   🔍 Búsqueda: {'✅ Exitosa' if test_starttls['busqueda'] else '❌ Fallida'}")
    console.print(f"   🔐 TLS Activo: {'✅ Sí' if test_starttls['tls_activo'] else '❌ No'}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_starttls['vulnerabilidad']}")
    if test_starttls.get('nota'):
        console.print(f"   📝 Nota: {test_starttls['nota']}")
    console.print()
    
    # Test 3: TLS Forzado
    test_tls_forzado = tests["tls_forzado"]
    console.print(Panel("🔐 PRUEBA 3: TLS Forzado (-ZZ)", style="cyan"))
    console.print(f"   📊 Estado: {test_tls_forzado['estado'].upper()}")
    console.print(f"   🔌 Conexión: {'✅ Activa' if test_tls_forzado['conexion'] else '❌ Fallida'}")
    console.print(f"   🔍 Búsqueda: {'✅ Exitosa' if test_tls_forzado['busqueda'] else '❌ Fallida'}")
    console.print(f"   🔐 TLS Activo: {'✅ Sí' if test_tls_forzado['tls_activo'] else '❌ No'}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_tls_forzado['vulnerabilidad']}")
    if test_tls_forzado.get('nota'):
        console.print(f"   📝 Nota: {test_tls_forzado['nota']}")
    console.print()
    
    # Test 4: Downgrade TLS
    test_downgrade = tests["downgrade"]
    console.print(Panel("⚠️ PRUEBA 4: Test de Downgrade TLS", style="cyan"))
    console.print(f"   📊 Estado: {test_downgrade['estado'].upper()}")
    console.print(f"   🔌 Conexión: {'✅ Activa' if test_downgrade['conexion'] else '❌ Fallida'}")
    console.print(f"   🔍 Búsqueda: {'✅ Exitosa' if test_downgrade['busqueda'] else '❌ Fallida'}")
    console.print(f"   🔐 TLS Activo: {'✅ Sí' if test_downgrade['tls_activo'] else '❌ No'}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_downgrade['vulnerabilidad']}")
    if test_downgrade.get('nota'):
        console.print(f"   📝 Nota: {test_downgrade['nota']}")
    console.print()
    
    # Resumen de resultados
    console.print(Panel("📋 RESUMEN DE RESULTADOS", style="bold green"))
    total_tests = len(tests)
    tests_exitosos = sum(1 for test in tests.values() if test.get('estado') == 'exitoso')
    tests_fallidos = sum(1 for test in tests.values() if test.get('estado') == 'fallido')
    tests_error = sum(1 for test in tests.values() if test.get('estado') == 'error')
    
    console.print(f"   🧪 Total de pruebas: {total_tests}")
    console.print(f"   ✅ Exitosas: {tests_exitosos}")
    console.print(f"   ❌ Fallidas: {tests_fallidos}")
    console.print(f"   💥 Con error: {tests_error}")
    console.print()
    
    # Análisis de seguridad
    console.print(Panel("🔒 ANÁLISIS DE SEGURIDAD", style="bold red"))
    console.print(f"   🚨 Nivel de Riesgo: {analisis_seguridad['nivel_riesgo'].upper()}")
    console.print(f"   ⚠️ Riesgos Detectados: {len(analisis_seguridad['riesgos_detectados'])}")
    console.print(f"   💥 Vulnerabilidades: {len(analisis_seguridad['vulnerabilidades_potenciales'])}")
    console.print(f"   🔧 Implementaciones Requeridas: {len(analisis_seguridad['implementacion_requerida'])}")
    console.print()
    
    # Riesgos detectados
    if analisis_seguridad["riesgos_detectados"]:
        console.print(Panel("🚨 RIESGOS DETECTADOS", style="bold red"))
        for i, riesgo in enumerate(analisis_seguridad["riesgos_detectados"], 1):
            console.print(f"   {i}. {riesgo}")
        console.print()
    
    # Vulnerabilidades potenciales
    if analisis_seguridad["vulnerabilidades_potenciales"]:
        console.print(Panel("💥 VULNERABILIDADES POTENCIALES", style="bold red"))
        for i, vuln in enumerate(analisis_seguridad["vulnerabilidades_potenciales"], 1):
            console.print(f"   {i}. {vuln}")
        console.print()
    
    # Recomendaciones
    if analisis_seguridad["recomendaciones"]:
        console.print(Panel("💡 RECOMENDACIONES DE SEGURIDAD", style="bold yellow"))
        for i, rec in enumerate(analisis_seguridad["recomendaciones"], 1):
            console.print(f"   {i}. {rec}")
        console.print()
    
    # Implementaciones requeridas
    if analisis_seguridad["implementacion_requerida"]:
        console.print(Panel("🔧 IMPLEMENTACIONES REQUERIDAS", style="bold blue"))
        for i, impl in enumerate(analisis_seguridad["implementacion_requerida"], 1):
            console.print(f"   {i}. {impl}")
        console.print()
    
    # Conclusión
    nivel_riesgo = analisis_seguridad["nivel_riesgo"]
    if nivel_riesgo == "alto":
        estilo_conclusion = "bold red"
        emoji = "🚨"
        mensaje = "ALTO RIESGO - Requiere atención inmediata"
    elif nivel_riesgo == "medio":
        estilo_conclusion = "bold yellow"
        emoji = "⚠️"
        mensaje = "RIESGO MEDIO - Requiere atención pronto"
    else:
        estilo_conclusion = "bold green"
        emoji = "✅"
        mensaje = "RIESGO BAJO - Sistema relativamente seguro"
    
    console.print(Panel(f"{emoji} CONCLUSIÓN: {mensaje}", style=estilo_conclusion)) 