"""
Herramienta ofensiva: Comparación Simple vs SASL Bind LDAP
"""

import logging
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)

def tool_simple_vs_sasl_bind(server: str = None, base_dn: str = None, username: str = None, password: str = None) -> Dict[str, Any]:
    """
    Compara resultados de ldapwhoami con y sin -x para detectar fallbacks inseguros.
    
    Esta herramienta realiza dos pruebas de autenticación LDAP:
    1. Bind simple (ldapwhoami normal)
    2. Bind anónimo (ldapwhoami -x)
    
    Compara los resultados para detectar:
    - Fallbacks inseguros de SASL a simple bind
    - Intentos de SASL/GSSAPI no deseados
    - Diferencias en permisos entre métodos de autenticación
    - Vulnerabilidades de downgrade de autenticación
    
    Args:
        server (str, optional): Servidor LDAP (por defecto usa configuración del sistema)
        base_dn (str, optional): DN base (por defecto usa configuración del sistema)
        username (str, optional): Usuario para autenticación (opcional)
        password (str, optional): Contraseña para autenticación (opcional)
        
    Returns:
        Dict[str, Any]: Resultado de la comparación con análisis de seguridad
        
    Raises:
        No lanza excepciones, todas las excepciones son capturadas y retornadas
        como parte del diccionario de resultado.
        
    Example:
        >>> resultado = tool_simple_vs_sasl_bind()
        >>> if not resultado["error"]:
        ...     print(f"Fallbacks detectados: {resultado['resultado']['fallbacks_detectados']}")
    """
    try:
        console.print(Panel("🔴 Iniciando comparación Simple vs SASL Bind LDAP", style="red"))
        
        # Importar el conector LDAP
        from ..tools_base.ldap_connector import LDAPConnector
        
        # Crear conexión LDAP
        ldap_conn = LDAPConnector()
        
        # Test 1: Bind simple (ldapwhoami normal)
        console.print(Panel("🔍 Test 1: Bind Simple (ldapwhoami normal)", style="blue"))
        resultado_simple = _test_bind_simple(ldap_conn, username, password)
        
        # Test 2: Bind anónimo (ldapwhoami -x)
        console.print(Panel("🔓 Test 2: Bind Anónimo (ldapwhoami -x)", style="blue"))
        resultado_anonimo = _test_bind_anonimo(ldap_conn)
        
        # Test 3: Comparación de permisos
        console.print(Panel("⚖️ Test 3: Comparación de Permisos", style="blue"))
        resultado_comparacion = _comparar_permisos(resultado_simple, resultado_anonimo)
        
        # Test 4: Detección de fallbacks
        console.print(Panel("⚠️ Test 4: Detección de Fallbacks", style="yellow"))
        resultado_fallbacks = _detectar_fallbacks(resultado_simple, resultado_anonimo)
        
        # Análisis de seguridad
        analisis_seguridad = _analizar_seguridad_bind(
            resultado_simple, resultado_anonimo, resultado_comparacion, resultado_fallbacks
        )
        
        # Resultado final
        resultado_completo = {
            "tests": {
                "bind_simple": resultado_simple,
                "bind_anonimo": resultado_anonimo,
                "comparacion_permisos": resultado_comparacion,
                "deteccion_fallbacks": resultado_fallbacks
            },
            "analisis_seguridad": analisis_seguridad,
            "metadata": {
                "herramienta": "tool_simple_vs_sasl_bind",
                "tipo": "comparacion_autenticacion",
                "categoria": "reconocimiento_ofensivo",
                "riesgo": "medio",  # Comparación de métodos de autenticación
                "timestamp": "ahora"  # TODO: usar datetime real
            }
        }
        
        console.print(Panel("✅ Comparación Simple vs SASL Bind completada exitosamente", style="green"))
        
        return {
            "error": False,
            "resultado": resultado_completo,
            "herramienta": "tool_simple_vs_sasl_bind",
            "tipo": "comparacion_autenticacion"
        }
        
    except Exception as e:
        logger.error(f"Error en tool_simple_vs_sasl_bind: {e}")
        return {
            "error": True,
            "mensaje": f"Error ejecutando comparación Simple vs SASL Bind: {str(e)}",
            "herramienta": "tool_simple_vs_sasl_bind",
            "tipo": "error_ejecucion"
        }

def _test_bind_simple(ldap_conn, username: str = None, password: str = None) -> Dict[str, Any]:
    """
    Test de bind simple (ldapwhoami normal).
    
    Args:
        ldap_conn: Conexión LDAP
        username (str, optional): Usuario para autenticación
        password (str, optional): Contraseña para autenticación
        
    Returns:
        Dict[str, Any]: Resultado del test de bind simple
    """
    try:
        # Intentar bind simple
        if username and password:
            # Bind con credenciales específicas
            if ldap_conn.connect(username=username, password=password):
                resultado_busqueda = ldap_conn.search("", "(objectClass=*)")
                return {
                    "estado": "exitoso",
                    "tipo_bind": "simple_con_credenciales",
                    "usuario": username,
                    "conexion": True,
                    "busqueda": len(resultado_busqueda) > 0,
                    "permisos": _evaluar_permisos(resultado_busqueda),
                    "metodo_autenticacion": "simple_bind",
                    "vulnerabilidad": "Bind con credenciales específicas"
                }
            else:
                return {
                    "estado": "fallido",
                    "tipo_bind": "simple_con_credenciales",
                    "usuario": username,
                    "conexion": False,
                    "busqueda": False,
                    "permisos": "sin_acceso",
                    "metodo_autenticacion": "simple_bind",
                    "vulnerabilidad": "Credenciales inválidas o acceso denegado"
                }
        else:
            # Bind simple sin credenciales (intenta SASL/GSSAPI)
            if ldap_conn.connect():
                resultado_busqueda = ldap_conn.search("", "(objectClass=*)")
                return {
                    "estado": "exitoso",
                    "tipo_bind": "simple_sin_credenciales",
                    "usuario": "sistema",
                    "conexion": True,
                    "busqueda": len(resultado_busqueda) > 0,
                    "permisos": _evaluar_permisos(resultado_busqueda),
                    "metodo_autenticacion": "sasl_gssapi",
                    "vulnerabilidad": "Bind SASL/GSSAPI automático"
                }
            else:
                return {
                    "estado": "fallido",
                    "tipo_bind": "simple_sin_credenciales",
                    "usuario": "sistema",
                    "conexion": False,
                    "busqueda": False,
                    "permisos": "sin_acceso",
                    "metodo_autenticacion": "sasl_gssapi",
                    "vulnerabilidad": "SASL/GSSAPI falló"
                }
                
    except Exception as e:
        return {
            "estado": "error",
            "tipo_bind": "simple",
            "usuario": username or "sistema",
            "conexion": False,
            "busqueda": False,
            "permisos": "error",
            "metodo_autenticacion": "desconocido",
            "vulnerabilidad": f"Error en bind simple: {str(e)}"
        }

def _test_bind_anonimo(ldap_conn) -> Dict[str, Any]:
    """
    Test de bind anónimo (ldapwhoami -x).
    
    Args:
        ldap_conn: Conexión LDAP
        
    Returns:
        Dict[str, Any]: Resultado del test de bind anónimo
    """
    try:
        # Intentar bind anónimo
        if ldap_conn.connect():
            # Realizar búsqueda anónima
            resultado_busqueda = ldap_conn.search("", "(objectClass=*)")
            
            return {
                "estado": "exitoso",
                "tipo_bind": "anonimo",
                "usuario": "anonymous",
                "conexion": True,
                "busqueda": len(resultado_busqueda) > 0,
                "permisos": _evaluar_permisos(resultado_busqueda),
                "metodo_autenticacion": "anonymous_bind",
                "vulnerabilidad": "Bind anónimo permitido"
            }
        else:
            return {
                "estado": "fallido",
                "tipo_bind": "anonimo",
                "usuario": "anonymous",
                "conexion": False,
                "busqueda": False,
                "permisos": "sin_acceso",
                "metodo_autenticacion": "anonymous_bind",
                "vulnerabilidad": "Bind anónimo denegado"
            }
            
    except Exception as e:
        return {
            "estado": "error",
            "tipo_bind": "anonimo",
            "usuario": "anonymous",
            "conexion": False,
            "busqueda": False,
            "permisos": "error",
            "metodo_autenticacion": "anonymous_bind",
            "vulnerabilidad": f"Error en bind anónimo: {str(e)}"
        }

def _evaluar_permisos(resultado_busqueda: List) -> str:
    """
    Evalúa los permisos basándose en los resultados de búsqueda.
    
    Args:
        resultado_busqueda (List): Resultados de la búsqueda LDAP
        
    Returns:
        str: Nivel de permisos evaluado
    """
    if not resultado_busqueda:
        return "sin_resultados"
    
    total_entradas = len(resultado_busqueda)
    
    if total_entradas > 100:
        return "acceso_completo"
    elif total_entradas > 50:
        return "acceso_amplio"
    elif total_entradas > 10:
        return "acceso_moderado"
    elif total_entradas > 0:
        return "acceso_limitado"
    else:
        return "sin_acceso"

def _comparar_permisos(resultado_simple: Dict, resultado_anonimo: Dict) -> Dict[str, Any]:
    """
    Compara los permisos entre bind simple y anónimo.
    
    Args:
        resultado_simple (Dict): Resultado del test de bind simple
        resultado_anonimo (Dict): Resultado del test de bind anónimo
        
    Returns:
        Dict[str, Any]: Comparación de permisos
    """
    try:
        # Extraer permisos
        permisos_simple = resultado_simple.get("permisos", "desconocido")
        permisos_anonimo = resultado_anonimo.get("permisos", "desconocido")
        
        # Comparar niveles de acceso
        niveles = {
            "sin_acceso": 0,
            "sin_resultados": 1,
            "acceso_limitado": 2,
            "acceso_moderado": 3,
            "acceso_amplio": 4,
            "acceso_completo": 5
        }
        
        nivel_simple = niveles.get(permisos_simple, 0)
        nivel_anonimo = niveles.get(permisos_anonimo, 0)
        
        # Análisis de la comparación
        if nivel_simple > nivel_anonimo:
            diferencia = "simple_superior"
            riesgo = "medio"
            descripcion = "Bind simple tiene más permisos que anónimo"
        elif nivel_anonimo > nivel_simple:
            diferencia = "anonimo_superior"
            riesgo = "alto"
            descripcion = "Bind anónimo tiene más permisos que simple (CRÍTICO)"
        else:
            diferencia = "iguales"
            riesgo = "bajo"
            descripcion = "Ambos métodos tienen permisos similares"
        
        return {
            "estado": "completado",
            "permisos_simple": permisos_simple,
            "permisos_anonimo": permisos_anonimo,
            "nivel_simple": nivel_simple,
            "nivel_anonimo": nivel_anonimo,
            "diferencia": diferencia,
            "riesgo": riesgo,
            "descripcion": descripcion,
            "vulnerabilidad": _identificar_vulnerabilidad_permisos(permisos_simple, permisos_anonimo)
        }
        
    except Exception as e:
        return {
            "estado": "error",
            "permisos_simple": "error",
            "permisos_anonimo": "error",
            "nivel_simple": 0,
            "nivel_anonimo": 0,
            "diferencia": "error",
            "riesgo": "desconocido",
            "descripcion": f"Error comparando permisos: {str(e)}",
            "vulnerabilidad": "Error en comparación"
        }

def _identificar_vulnerabilidad_permisos(permisos_simple: str, permisos_anonimo: str) -> str:
    """
    Identifica vulnerabilidades basándose en la comparación de permisos.
    
    Args:
        permisos_simple (str): Permisos del bind simple
        permisos_anonimo (str): Permisos del bind anónimo
        
    Returns:
        str: Vulnerabilidad identificada
    """
    if permisos_anonimo in ["acceso_amplio", "acceso_completo"]:
        return "Bind anónimo con acceso excesivo"
    elif permisos_simple == "sin_acceso" and permisos_anonimo in ["acceso_limitado", "acceso_moderado"]:
        return "Bind anónimo con más permisos que autenticado"
    elif permisos_simple == "acceso_completo" and permisos_anonimo == "sin_acceso":
        return "Configuración segura - solo autenticados tienen acceso"
    else:
        return "Configuración estándar"

def _detectar_fallbacks(resultado_simple: Dict, resultado_anonimo: Dict) -> Dict[str, Any]:
    """
    Detecta fallbacks inseguros entre métodos de autenticación.
    
    Args:
        resultado_simple (Dict): Resultado del test de bind simple
        resultado_anonimo (Dict): Resultado del test de bind anónimo
        
    Returns:
        Dict[str, Any]: Resultado de la detección de fallbacks
    """
    try:
        fallbacks_detectados = []
        vulnerabilidades = []
        
        # Detectar fallback de SASL a simple bind
        if (resultado_simple.get("metodo_autenticacion") == "sasl_gssapi" and 
            resultado_simple.get("estado") == "exitoso"):
            fallbacks_detectados.append("SASL/GSSAPI a simple bind")
            vulnerabilidades.append("Posible downgrade de autenticación")
        
        # Detectar bind anónimo con permisos excesivos
        if (resultado_anonimo.get("estado") == "exitoso" and 
            resultado_anonimo.get("permisos") in ["acceso_amplio", "acceso_completo"]):
            fallbacks_detectados.append("Bind anónimo con permisos excesivos")
            vulnerabilidades.append("Acceso anónimo no restringido")
        
        # Detectar diferencias significativas en permisos
        if (resultado_simple.get("estado") == "exitoso" and 
            resultado_anonimo.get("estado") == "exitoso"):
            permisos_simple = resultado_simple.get("permisos", "desconocido")
            permisos_anonimo = resultado_anonimo.get("permisos", "desconocido")
            
            if permisos_anonimo in ["acceso_amplio", "acceso_completo"]:
                fallbacks_detectados.append("Bind anónimo con acceso amplio")
                vulnerabilidades.append("Configuración de permisos insegura")
        
        return {
            "estado": "completado",
            "fallbacks_detectados": fallbacks_detectados,
            "vulnerabilidades": vulnerabilidades,
            "total_fallbacks": len(fallbacks_detectados),
            "total_vulnerabilidades": len(vulnerabilidades),
            "riesgo": "alto" if fallbacks_detectados else "bajo",
            "descripcion": f"Se detectaron {len(fallbacks_detectados)} fallbacks y {len(vulnerabilidades)} vulnerabilidades"
        }
        
    except Exception as e:
        return {
            "estado": "error",
            "fallbacks_detectados": [],
            "vulnerabilidades": [],
            "total_fallbacks": 0,
            "total_vulnerabilidades": 0,
            "riesgo": "desconocido",
            "descripcion": f"Error detectando fallbacks: {str(e)}"
        }

def _analizar_seguridad_bind(resultado_simple: Dict, resultado_anonimo: Dict, 
                            resultado_comparacion: Dict, resultado_fallbacks: Dict) -> Dict[str, Any]:
    """
    Analiza la seguridad de los resultados de bind.
    
    Args:
        resultado_simple (Dict): Resultado del test de bind simple
        resultado_anonimo (Dict): Resultado del test de bind anónimo
        resultado_comparacion (Dict): Resultado de la comparación de permisos
        resultado_fallbacks (Dict): Resultado de la detección de fallbacks
        
    Returns:
        Dict[str, Any]: Análisis de seguridad
    """
    analisis = {
        "riesgos_detectados": [],
        "vulnerabilidades_potenciales": [],
        "recomendaciones": [],
        "nivel_riesgo": "bajo",
        "configuracion_actual": "desconocida"
    }
    
    # Análisis de bind simple
    if resultado_simple.get("estado") == "exitoso":
        metodo_simple = resultado_simple.get("metodo_autenticacion", "desconocido")
        if metodo_simple == "sasl_gssapi":
            analisis["configuracion_actual"] = "SASL/GSSAPI habilitado"
            analisis["recomendaciones"].append("Verificar configuración de SASL/GSSAPI")
        elif metodo_simple == "simple_bind":
            analisis["configuracion_actual"] = "Simple bind habilitado"
            analisis["recomendaciones"].append("Considerar deshabilitar simple bind si no es necesario")
    
    # Análisis de bind anónimo
    if resultado_anonimo.get("estado") == "exitoso":
        permisos_anonimo = resultado_anonimo.get("permisos", "desconocido")
        if permisos_anonimo in ["acceso_amplio", "acceso_completo"]:
            analisis["riesgos_detectados"].append("Bind anónimo con acceso excesivo")
            analisis["vulnerabilidades_potenciales"].append("Información sensible accesible anónimamente")
            analisis["nivel_riesgo"] = "alto"
            analisis["recomendaciones"].append("Restringir permisos del bind anónimo")
        elif permisos_anonimo in ["acceso_limitado", "acceso_moderado"]:
            analisis["riesgos_detectados"].append("Bind anónimo con acceso moderado")
            analisis["nivel_riesgo"] = "medio"
            analisis["recomendaciones"].append("Revisar si el acceso anónimo es necesario")
    
    # Análisis de comparación de permisos
    if resultado_comparacion.get("riesgo") == "alto":
        analisis["riesgos_detectados"].append("Diferencia crítica en permisos")
        analisis["vulnerabilidades_potenciales"].append("Bind anónimo más privilegiado que autenticado")
        analisis["nivel_riesgo"] = "alto"
        analisis["recomendaciones"].append("Revisar configuración de permisos LDAP")
    
    # Análisis de fallbacks
    if resultado_fallbacks.get("total_fallbacks") > 0:
        analisis["riesgos_detectados"].extend(resultado_fallbacks.get("fallbacks_detectados", []))
        analisis["vulnerabilidades_potenciales"].extend(resultado_fallbacks.get("vulnerabilidades", []))
        analisis["nivel_riesgo"] = "alto"
        analisis["recomendaciones"].append("Investigar y corregir fallbacks detectados")
    
    # Recomendaciones generales
    if analisis["nivel_riesgo"] == "alto":
        analisis["recomendaciones"].append("Revisar configuración de seguridad LDAP inmediatamente")
        analisis["recomendaciones"].append("Implementar políticas de autenticación estrictas")
    elif analisis["nivel_riesgo"] == "medio":
        analisis["recomendaciones"].append("Revisar configuración de permisos LDAP")
        analisis["recomendaciones"].append("Considerar restricciones adicionales")
    
    analisis["recomendaciones"].append("Implementar logging de autenticación LDAP")
    analisis["recomendaciones"].append("Revisar regularmente permisos de usuarios y grupos")
    
    return analisis

def mostrar_resultado_simple_vs_sasl(resultado: Dict[str, Any]):
    """
    Muestra el resultado de la comparación Simple vs SASL Bind de manera formateada.
    
    Args:
        resultado (Dict[str, Any]): Resultado de tool_simple_vs_sasl_bind
    """
    if resultado.get("error"):
        console.print(Panel(f"❌ Error: {resultado['mensaje']}", style="red"))
        return
    
    data = resultado["resultado"]
    tests = data["tests"]
    analisis_seguridad = data["analisis_seguridad"]
    
    # Título principal
    console.print(Panel("🔐 COMPARACIÓN SIMPLE vs SASL BIND LDAP", style="bold red"))
    console.print()
    
    # Mostrar cada test individualmente con detalles
    console.print(Panel("🧪 DETALLES DE CADA PRUEBA REALIZADA", style="bold blue"))
    console.print()
    
    # Test 1: Bind Simple
    test_simple = tests["bind_simple"]
    console.print(Panel("🔍 PRUEBA 1: Bind Simple (ldapwhoami normal)", style="cyan"))
    console.print(f"   📊 Estado: {test_simple['estado'].upper()}")
    console.print(f"   🔐 Tipo Bind: {test_simple['tipo_bind']}")
    console.print(f"   👤 Usuario: {test_simple['usuario']}")
    console.print(f"   🔌 Conexión: {'✅ Activa' if test_simple['conexion'] else '❌ Fallida'}")
    console.print(f"   🔍 Búsqueda: {'✅ Exitosa' if test_simple['busqueda'] else '❌ Fallida'}")
    console.print(f"   🔑 Permisos: {test_simple['permisos']}")
    console.print(f"   🔒 Método: {test_simple['metodo_autenticacion']}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_simple['vulnerabilidad']}")
    console.print()
    
    # Test 2: Bind Anónimo
    test_anonimo = tests["bind_anonimo"]
    console.print(Panel("🔓 PRUEBA 2: Bind Anónimo (ldapwhoami -x)", style="cyan"))
    console.print(f"   📊 Estado: {test_anonimo['estado'].upper()}")
    console.print(f"   🔐 Tipo Bind: {test_anonimo['tipo_bind']}")
    console.print(f"   👤 Usuario: {test_anonimo['usuario']}")
    console.print(f"   🔌 Conexión: {'✅ Activa' if test_anonimo['conexion'] else '❌ Fallida'}")
    console.print(f"   🔍 Búsqueda: {'✅ Exitosa' if test_anonimo['busqueda'] else '❌ Fallida'}")
    console.print(f"   🔑 Permisos: {test_anonimo['permisos']}")
    console.print(f"   🔒 Método: {test_anonimo['metodo_autenticacion']}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_anonimo['vulnerabilidad']}")
    console.print()
    
    # Test 3: Comparación de Permisos
    test_comparacion = tests["comparacion_permisos"]
    console.print(Panel("⚖️ PRUEBA 3: Comparación de Permisos", style="cyan"))
    console.print(f"   📊 Estado: {test_comparacion['estado'].upper()}")
    console.print(f"   🔑 Permisos Simple: {test_comparacion['permisos_simple']}")
    console.print(f"   🔑 Permisos Anónimo: {test_comparacion['permisos_anonimo']}")
    console.print(f"   📊 Diferencia: {test_comparacion['diferencia']}")
    console.print(f"   🚨 Riesgo: {test_comparacion['riesgo'].upper()}")
    console.print(f"   📝 Descripción: {test_comparacion['descripcion']}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_comparacion['vulnerabilidad']}")
    console.print()
    
    # Test 4: Detección de Fallbacks
    test_fallbacks = tests["deteccion_fallbacks"]
    console.print(Panel("⚠️ PRUEBA 4: Detección de Fallbacks", style="cyan"))
    console.print(f"   📊 Estado: {test_fallbacks['estado'].upper()}")
    console.print(f"   🚨 Fallbacks Detectados: {test_fallbacks['total_fallbacks']}")
    console.print(f"   💥 Vulnerabilidades: {test_fallbacks['total_vulnerabilidades']}")
    console.print(f"   🚨 Riesgo: {test_fallbacks['riesgo'].upper()}")
    console.print(f"   📝 Descripción: {test_fallbacks['descripcion']}")
    
    if test_fallbacks.get("fallbacks_detectados"):
        console.print("   📋 Fallbacks específicos:")
        for fallback in test_fallbacks["fallbacks_detectados"]:
            console.print(f"      - {fallback}")
    
    if test_fallbacks.get("vulnerabilidades"):
        console.print("   📋 Vulnerabilidades específicas:")
        for vuln in test_fallbacks["vulnerabilidades"]:
            console.print(f"      - {vuln}")
    console.print()
    
    # Resumen de resultados
    console.print(Panel("📋 RESUMEN DE RESULTADOS", style="bold green"))
    total_tests = len(tests)
    tests_exitosos = sum(1 for test in tests.values() if test.get('estado') == 'exitoso' or test.get('estado') == 'completado')
    tests_fallidos = sum(1 for test in tests.values() if test.get('estado') == 'fallido')
    tests_error = sum(1 for test in tests.values() if test.get('estado') == 'error')
    
    console.print(f"   🧪 Total de pruebas: {total_tests}")
    console.print(f"   ✅ Exitosas/Completadas: {tests_exitosos}")
    console.print(f"   ❌ Fallidas: {tests_fallidos}")
    console.print(f"   💥 Con error: {tests_error}")
    console.print()
    
    # Análisis de seguridad
    console.print(Panel("🔒 ANÁLISIS DE SEGURIDAD", style="bold red"))
    console.print(f"   🚨 Nivel de Riesgo: {analisis_seguridad['nivel_riesgo'].upper()}")
    console.print(f"   ⚠️ Riesgos Detectados: {len(analisis_seguridad['riesgos_detectados'])}")
    console.print(f"   💥 Vulnerabilidades: {len(analisis_seguridad['vulnerabilidades_potenciales'])}")
    console.print(f"   🔧 Configuración Actual: {analisis_seguridad['configuracion_actual']}")
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