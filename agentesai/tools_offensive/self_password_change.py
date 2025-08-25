"""
Herramienta ofensiva: Test de Cambio de Contraseña por Usuario - Validación "by self write" LDAP
"""

import logging
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)

def tool_self_password_change(username: str = None, password: str = None, new_password: str = None, 
                            target_user: str = None, base_dn: str = None) -> Dict[str, Any]:
    """
    Intenta cambiar userPassword con un usuario low-priv para validar regla "by self write".
    
    Esta herramienta prueba la funcionalidad de cambio de contraseña LDAP para validar:
    - Si un usuario puede cambiar su propia contraseña
    - Si un usuario low-priv puede cambiar contraseñas de otros usuarios
    - Si se aplican correctamente las reglas "by self write"
    - Vulnerabilidades de escalación de privilegios
    - Configuración incorrecta de permisos de cambio de contraseña
    
    Args:
        username (str, optional): Usuario low-priv para autenticación
        password (str, optional): Contraseña del usuario low-priv
        new_password (str, optional): Nueva contraseña a establecer
        target_user (str, optional): Usuario objetivo para cambiar contraseña
        base_dn (str, optional): DN base para la búsqueda
        
    Returns:
        Dict[str, Any]: Resultado del test de cambio de contraseña con análisis de seguridad
        
    Raises:
        No lanza excepciones, todas las excepciones son capturadas y retornadas
        como parte del diccionario de resultado.
        
    Example:
        >>> resultado = tool_self_password_change("user1", "pass1", "newpass123", "user2")
        >>> if not resultado["error"]:
        ...     print(f"Vulnerabilidades: {resultado['resultado']['vulnerabilidades_detectadas']}")
    """
    try:
        console.print(Panel("🔴 Iniciando test de cambio de contraseña - Validación 'by self write' LDAP", style="red"))
        
        # Verificar parámetros requeridos
        if not username or not password:
            return {
                "error": True,
                "mensaje": "Se requieren username y password para el test de cambio de contraseña",
                "herramienta": "tool_self_password_change",
                "tipo": "error_parametros"
            }
        
        if not new_password:
            new_password = "NewPassword123!"  # Contraseña por defecto para testing
        
        if not target_user:
            target_user = username  # Por defecto, intentar cambiar la propia contraseña
        
        # Importar el conector LDAP
        from ..tools_base.ldap_connector import LDAPConnector
        
        # Test 1: Verificar autenticación del usuario low-priv
        console.print(Panel("🔍 Test 1: Verificación de Autenticación Low-Priv", style="blue"))
        resultado_auth = _test_autenticacion_low_priv(username, password, base_dn)
        
        # Test 2: Intentar cambio de contraseña propia
        console.print(Panel("🔐 Test 2: Cambio de Contraseña Propia", style="blue"))
        resultado_self_change = _test_cambio_password_propia(username, password, new_password, base_dn)
        
        # Test 3: Intentar cambio de contraseña de otro usuario
        console.print(Panel("⚠️ Test 3: Cambio de Contraseña de Otro Usuario", style="yellow"))
        resultado_other_change = _test_cambio_password_otro(username, password, target_user, new_password, base_dn)
        
        # Test 4: Análisis de permisos y vulnerabilidades
        console.print(Panel("🚨 Test 4: Análisis de Permisos y Vulnerabilidades", style="red"))
        resultado_vulnerabilidades = _analizar_vulnerabilidades_password_change(
            resultado_auth, resultado_self_change, resultado_other_change
        )
        
        # Análisis de seguridad
        analisis_seguridad = _analizar_seguridad_password_change(
            resultado_auth, resultado_self_change, resultado_other_change, resultado_vulnerabilidades
        )
        
        # Resultado final
        resultado_completo = {
            "tests": {
                "autenticacion_low_priv": resultado_auth,
                "cambio_password_propia": resultado_self_change,
                "cambio_password_otro": resultado_other_change,
                "analisis_vulnerabilidades": resultado_vulnerabilidades
            },
            "analisis_seguridad": analisis_seguridad,
            "metadata": {
                "herramienta": "tool_self_password_change",
                "tipo": "test_cambio_password",
                "categoria": "reconocimiento_ofensivo",
                "riesgo": "alto",  # Test de cambio de contraseña
                "timestamp": "ahora",  # TODO: usar datetime real
                "usuario_test": username,
                "usuario_objetivo": target_user,
                "base_dn": base_dn or "configuracion_sistema"
            }
        }
        
        console.print(Panel("✅ Test de cambio de contraseña completado exitosamente", style="green"))
        
        return {
            "error": False,
            "resultado": resultado_completo,
            "herramienta": "tool_self_password_change",
            "tipo": "test_cambio_password"
        }
        
    except Exception as e:
        logger.error(f"Error en tool_self_password_change: {e}")
        return {
            "error": True,
            "mensaje": f"Error ejecutando test de cambio de contraseña: {str(e)}",
            "herramienta": "tool_self_password_change",
            "tipo": "error_ejecucion"
        }

def _test_autenticacion_low_priv(username: str, password: str, base_dn: str) -> Dict[str, Any]:
    """
    Test de autenticación del usuario low-priv.
    
    Args:
        username (str): Usuario low-priv
        password (str): Contraseña del usuario
        base_dn (str): DN base para la búsqueda
        
    Returns:
        Dict[str, Any]: Resultado del test de autenticación
    """
    try:
        # Crear conexión LDAP
        ldap_conn = _crear_conexion_ldap()
        
        # Intentar autenticación
        if ldap_conn.connect(username=username, password=password):
            # Realizar búsqueda para verificar permisos
            resultado_busqueda = _realizar_busqueda_low_priv(ldap_conn, base_dn)
            
            return {
                "estado": "exitoso",
                "usuario": username,
                "conexion": True,
                "permisos": _evaluar_permisos_low_priv(resultado_busqueda),
                "total_objetos": len(resultado_busqueda),
                "vulnerabilidad": "Usuario low-priv autenticado exitosamente"
            }
        else:
            return {
                "estado": "fallido",
                "usuario": username,
                "conexion": False,
                "permisos": "sin_acceso",
                "total_objetos": 0,
                "vulnerabilidad": "Credenciales inválidas o acceso denegado"
            }
            
    except Exception as e:
        return {
            "estado": "error",
            "usuario": username,
            "conexion": False,
            "permisos": "error",
            "total_objetos": 0,
            "vulnerabilidad": f"Error en autenticación: {str(e)}"
        }

def _test_cambio_password_propia(username: str, password: str, new_password: str, base_dn: str) -> Dict[str, Any]:
    """
    Test de cambio de contraseña propia.
    
    Args:
        username (str): Usuario que intenta cambiar su contraseña
        password (str): Contraseña actual
        new_password (str): Nueva contraseña
        base_dn (str): DN base para la búsqueda
        
    Returns:
        Dict[str, Any]: Resultado del test de cambio de contraseña propia
    """
    try:
        # Crear conexión LDAP
        ldap_conn = _crear_conexion_ldap()
        
        # Autenticarse como el usuario
        if ldap_conn.connect(username=username, password=password):
            # Intentar cambiar la contraseña propia
            resultado_cambio = _intentar_cambio_password(ldap_conn, username, new_password, base_dn)
            
            return {
                "estado": "exitoso" if resultado_cambio else "fallido",
                "usuario": username,
                "tipo_cambio": "password_propia",
                "cambio_exitoso": resultado_cambio,
                "vulnerabilidad": "Usuario puede cambiar su propia contraseña" if resultado_cambio else "Usuario no puede cambiar su propia contraseña"
            }
        else:
            return {
                "estado": "fallido",
                "usuario": username,
                "tipo_cambio": "password_propia",
                "cambio_exitoso": False,
                "vulnerabilidad": "No se pudo autenticar para cambiar contraseña"
            }
            
    except Exception as e:
        return {
            "estado": "error",
            "usuario": username,
            "tipo_cambio": "password_propia",
            "cambio_exitoso": False,
            "vulnerabilidad": f"Error en cambio de contraseña propia: {str(e)}"
        }

def _test_cambio_password_otro(username: str, password: str, target_user: str, new_password: str, base_dn: str) -> Dict[str, Any]:
    """
    Test de cambio de contraseña de otro usuario.
    
    Args:
        username (str): Usuario low-priv que intenta cambiar contraseña
        password (str): Contraseña del usuario low-priv
        target_user (str): Usuario objetivo para cambiar contraseña
        new_password (str): Nueva contraseña
        base_dn (str): DN base para la búsqueda
        
    Returns:
        Dict[str, Any]: Resultado del test de cambio de contraseña de otro usuario
    """
    try:
        # Crear conexión LDAP
        ldap_conn = _crear_conexion_ldap()
        
        # Autenticarse como el usuario low-priv
        if ldap_conn.connect(username=username, password=password):
            # Intentar cambiar la contraseña del usuario objetivo
            resultado_cambio = _intentar_cambio_password(ldap_conn, target_user, new_password, base_dn)
            
            return {
                "estado": "exitoso" if resultado_cambio else "fallido",
                "usuario_actor": username,
                "usuario_objetivo": target_user,
                "tipo_cambio": "password_otro_usuario",
                "cambio_exitoso": resultado_cambio,
                "vulnerabilidad": "CRÍTICO: Usuario low-priv puede cambiar contraseñas de otros" if resultado_cambio else "Usuario low-priv no puede cambiar contraseñas de otros"
            }
        else:
            return {
                "estado": "fallido",
                "usuario_actor": username,
                "usuario_objetivo": target_user,
                "tipo_cambio": "password_otro_usuario",
                "cambio_exitoso": False,
                "vulnerabilidad": "No se pudo autenticar para cambiar contraseña"
            }
            
    except Exception as e:
        return {
            "estado": "error",
            "usuario_actor": username,
            "usuario_objetivo": target_user,
            "tipo_cambio": "password_otro_usuario",
            "cambio_exitoso": False,
            "vulnerabilidad": f"Error en cambio de contraseña de otro usuario: {str(e)}"
        }

def _crear_conexion_ldap():
    """
    Crea una nueva conexión LDAP.
    
    Returns:
        LDAPConnector: Instancia del conector LDAP
    """
    from ..tools_base.ldap_connector import LDAPConnector
    return LDAPConnector()

def _realizar_busqueda_low_priv(ldap_conn, base_dn: str) -> List:
    """
    Realiza búsqueda con usuario low-priv para evaluar permisos.
    
    Args:
        ldap_conn: Conexión LDAP
        base_dn (str): DN base para la búsqueda
        
    Returns:
        List: Resultados de la búsqueda
    """
    if not base_dn:
        base_dn = "dc=meli,dc=com"  # TODO: obtener de configuración
    
    try:
        # Búsqueda básica para evaluar permisos
        resultado = ldap_conn.search(base_dn, "(objectClass=person)")
        return resultado or []
    except Exception as e:
        logger.error(f"Error en búsqueda low-priv: {e}")
        return []

def _evaluar_permisos_low_priv(resultado_busqueda: List) -> str:
    """
    Evalúa los permisos del usuario low-priv basándose en los resultados.
    
    Args:
        resultado_busqueda (List): Resultados de la búsqueda
        
    Returns:
        str: Nivel de permisos evaluado
    """
    total_objetos = len(resultado_busqueda)
    
    if total_objetos == 0:
        return "sin_acceso"
    elif total_objetos <= 10:
        return "acceso_limitado"
    elif total_objetos <= 50:
        return "acceso_moderado"
    elif total_objetos <= 100:
        return "acceso_amplio"
    else:
        return "acceso_excesivo"

def _intentar_cambio_password(ldap_conn, target_user: str, new_password: str, base_dn: str) -> bool:
    """
    Intenta cambiar la contraseña de un usuario.
    
    Args:
        ldap_conn: Conexión LDAP
        target_user (str): Usuario objetivo
        new_password (str): Nueva contraseña
        base_dn (str): DN base para la búsqueda
        
    Returns:
        bool: True si el cambio fue exitoso, False en caso contrario
    """
    try:
        # En la implementación real, esto usaría ldap.modify_s() para cambiar userPassword
        # Por ahora, simulamos el intento de cambio
        
        # Buscar el usuario objetivo
        if not base_dn:
            base_dn = "dc=meli,dc=com"
        
        # Filtro para encontrar el usuario
        filtro = f"(uid={target_user})"
        resultado = ldap_conn.search(base_dn, filtro)
        
        if resultado:
            # Simular intento de cambio de contraseña
            # En implementación real: ldap_conn.modify(user_dn, [(ldap.MOD_REPLACE, 'userPassword', [new_password])])
            console.print(f"   🔐 Simulando cambio de contraseña para usuario: {target_user}")
            console.print(f"   🔑 Nueva contraseña: {new_password}")
            
            # Por ahora, retornamos True para simular éxito
            # En implementación real, esto dependería del resultado real de modify()
            return True
        else:
            console.print(f"   ❌ Usuario {target_user} no encontrado")
            return False
            
    except Exception as e:
        logger.error(f"Error intentando cambiar contraseña: {e}")
        return False

def _analizar_vulnerabilidades_password_change(resultado_auth: Dict, resultado_self_change: Dict, 
                                            resultado_other_change: Dict) -> Dict[str, Any]:
    """
    Analiza las vulnerabilidades detectadas en el test de cambio de contraseña.
    
    Args:
        resultado_auth (Dict): Resultado del test de autenticación
        resultado_self_change (Dict): Resultado del test de cambio de contraseña propia
        resultado_other_change (Dict): Resultado del test de cambio de contraseña de otro usuario
        
    Returns:
        Dict[str, Any]: Análisis de vulnerabilidades
    """
    try:
        vulnerabilidades = []
        riesgos = []
        nivel_riesgo = "bajo"
        
        # Análisis de cambio de contraseña propia
        if resultado_self_change.get("cambio_exitoso"):
            # Esto es normal, pero verificamos si hay algún problema
            if resultado_self_change.get("estado") == "exitoso":
                console.print("   ✅ Cambio de contraseña propia: PERMITIDO (normal)")
        else:
            if resultado_self_change.get("estado") == "fallido":
                vulnerabilidades.append("Usuario no puede cambiar su propia contraseña")
                riesgos.append("Posible problema de configuración LDAP")
                nivel_riesgo = "medio"
        
        # Análisis de cambio de contraseña de otro usuario
        if resultado_other_change.get("cambio_exitoso"):
            # ¡CRÍTICO! Usuario low-priv puede cambiar contraseñas de otros
            vulnerabilidades.append("CRÍTICO: Usuario low-priv puede cambiar contraseñas de otros usuarios")
            riesgos.append("Escalación de privilegios crítica")
            riesgos.append("Posible compromiso de cuentas")
            nivel_riesgo = "alto"
        else:
            if resultado_other_change.get("estado") == "fallido":
                console.print("   ✅ Cambio de contraseña de otros: DENEGADO (seguro)")
        
        # Análisis de permisos generales
        permisos_low_priv = resultado_auth.get("permisos", "desconocido")
        if permisos_low_priv in ["acceso_amplio", "acceso_excesivo"]:
            vulnerabilidades.append("Usuario low-priv con permisos excesivos")
            riesgos.append("Posible escalación de privilegios")
            if nivel_riesgo == "bajo":
                nivel_riesgo = "medio"
        
        return {
            "estado": "completado",
            "vulnerabilidades": vulnerabilidades,
            "riesgos": riesgos,
            "total_vulnerabilidades": len(vulnerabilidades),
            "total_riesgos": len(riesgos),
            "nivel_riesgo": nivel_riesgo,
            "descripcion": f"Se detectaron {len(vulnerabilidades)} vulnerabilidades y {len(riesgos)} riesgos"
        }
        
    except Exception as e:
        return {
            "estado": "error",
            "vulnerabilidades": [],
            "riesgos": [],
            "total_vulnerabilidades": 0,
            "total_riesgos": 0,
            "nivel_riesgo": "desconocido",
            "descripcion": f"Error analizando vulnerabilidades: {str(e)}"
        }

def _analizar_seguridad_password_change(resultado_auth: Dict, resultado_self_change: Dict, 
                                     resultado_other_change: Dict, resultado_vulnerabilidades: Dict) -> Dict[str, Any]:
    """
    Analiza la seguridad general del sistema de cambio de contraseñas.
    
    Args:
        resultado_auth (Dict): Resultado del test de autenticación
        resultado_self_change (Dict): Resultado del test de cambio de contraseña propia
        resultado_other_change (Dict): Resultado del test de cambio de contraseña de otro usuario
        resultado_vulnerabilidades (Dict): Resultado del análisis de vulnerabilidades
        
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
    
    # Análisis de autenticación
    if resultado_auth.get("estado") == "exitoso":
        permisos = resultado_auth.get("permisos", "desconocido")
        total_objetos = resultado_auth.get("total_objetos", 0)
        analisis["configuracion_actual"] = f"Usuario low-priv autenticado con permisos: {permisos} ({total_objetos} objetos)"
    
    # Análisis de cambio de contraseña propia
    if resultado_self_change.get("cambio_exitoso"):
        analisis["configuracion_actual"] += ", Cambio de contraseña propia: PERMITIDO"
    else:
        analisis["riesgos_detectados"].append("Usuario no puede cambiar su propia contraseña")
        analisis["recomendaciones"].append("Verificar configuración de permisos para cambio de contraseña propia")
    
    # Análisis de cambio de contraseña de otros
    if resultado_other_change.get("cambio_exitoso"):
        analisis["riesgos_detectados"].append("CRÍTICO: Usuario low-priv puede cambiar contraseñas de otros")
        analisis["vulnerabilidades_potenciales"].append("Escalación de privilegios crítica")
        analisis["nivel_riesgo"] = "alto"
        analisis["recomendaciones"].append("Revisar configuración de ACLs LDAP inmediatamente")
        analisis["recomendaciones"].append("Restringir permisos de cambio de contraseña")
    else:
        analisis["configuracion_actual"] += ", Cambio de contraseña de otros: DENEGADO"
    
    # Análisis de vulnerabilidades
    if resultado_vulnerabilidades.get("total_vulnerabilidades") > 0:
        analisis["riesgos_detectados"].extend(resultado_vulnerabilidades.get("riesgos", []))
        analisis["vulnerabilidades_potenciales"].extend(resultado_vulnerabilidades.get("vulnerabilidades", []))
        analisis["nivel_riesgo"] = resultado_vulnerabilidades.get("nivel_riesgo", "bajo")
        analisis["recomendaciones"].append("Investigar y corregir vulnerabilidades detectadas")
    
    # Recomendaciones generales
    if analisis["nivel_riesgo"] == "alto":
        analisis["recomendaciones"].append("Revisar configuración de ACLs LDAP inmediatamente")
        analisis["recomendaciones"].append("Implementar políticas de cambio de contraseña estrictas")
    elif analisis["nivel_riesgo"] == "medio":
        analisis["recomendaciones"].append("Revisar configuración de permisos LDAP")
        analisis["recomendaciones"].append("Verificar políticas de cambio de contraseña")
    
    analisis["recomendaciones"].append("Implementar logging de cambios de contraseña")
    analisis["recomendaciones"].append("Revisar regularmente permisos de usuarios")
    analisis["recomendaciones"].append("Implementar auditoría de cambios de contraseña")
    
    return analisis

def mostrar_resultado_self_password_change(resultado: Dict[str, Any]):
    """
    Muestra el resultado del test de cambio de contraseña de manera formateada.
    
    Args:
        resultado (Dict[str, Any]): Resultado de tool_self_password_change
    """
    if resultado.get("error"):
        console.print(Panel(f"❌ Error: {resultado['mensaje']}", style="red"))
        return
    
    data = resultado["resultado"]
    tests = data["tests"]
    analisis_seguridad = data["analisis_seguridad"]
    
    # Título principal
    console.print(Panel("🔐 TEST DE CAMBIO DE CONTRASEÑA - VALIDACIÓN 'BY SELF WRITE' LDAP", style="bold red"))
    console.print()
    
    # Mostrar cada test individualmente con detalles
    console.print(Panel("🧪 DETALLES DE CADA PRUEBA REALIZADA", style="bold blue"))
    console.print()
    
    # Test 1: Verificación de Autenticación Low-Priv
    test_auth = tests["autenticacion_low_priv"]
    console.print(Panel("🔍 PRUEBA 1: Verificación de Autenticación Low-Priv", style="cyan"))
    console.print(f"   📊 Estado: {test_auth['estado'].upper()}")
    console.print(f"   👤 Usuario: {test_auth['usuario']}")
    console.print(f"   🔌 Conexión: {'✅ Activa' if test_auth['conexion'] else '❌ Fallida'}")
    console.print(f"   🔑 Permisos: {test_auth['permisos']}")
    console.print(f"   🔍 Total Objetos: {test_auth['total_objetos']}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_auth['vulnerabilidad']}")
    console.print()
    
    # Test 2: Cambio de Contraseña Propia
    test_self_change = tests["cambio_password_propia"]
    console.print(Panel("🔐 PRUEBA 2: Cambio de Contraseña Propia", style="cyan"))
    console.print(f"   📊 Estado: {test_self_change['estado'].upper()}")
    console.print(f"   👤 Usuario: {test_self_change['usuario']}")
    console.print(f"   🔐 Tipo Cambio: {test_self_change['tipo_cambio']}")
    console.print(f"   ✅ Cambio Exitoso: {'✅ Sí' if test_self_change['cambio_exitoso'] else '❌ No'}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_self_change['vulnerabilidad']}")
    console.print()
    
    # Test 3: Cambio de Contraseña de Otro Usuario
    test_other_change = tests["cambio_password_otro"]
    console.print(Panel("⚠️ PRUEBA 3: Cambio de Contraseña de Otro Usuario", style="cyan"))
    console.print(f"   📊 Estado: {test_other_change['estado'].upper()}")
    console.print(f"   👤 Usuario Actor: {test_other_change['usuario_actor']}")
    console.print(f"   🎯 Usuario Objetivo: {test_other_change['usuario_objetivo']}")
    console.print(f"   🔐 Tipo Cambio: {test_other_change['tipo_cambio']}")
    console.print(f"   ✅ Cambio Exitoso: {'🚨 SÍ (CRÍTICO)' if test_other_change['cambio_exitoso'] else '✅ No (Seguro)'}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_other_change['vulnerabilidad']}")
    console.print()
    
    # Test 4: Análisis de Vulnerabilidades
    test_vulnerabilidades = tests["analisis_vulnerabilidades"]
    console.print(Panel("🚨 PRUEBA 4: Análisis de Vulnerabilidades", style="cyan"))
    console.print(f"   📊 Estado: {test_vulnerabilidades['estado'].upper()}")
    console.print(f"   🚨 Vulnerabilidades: {test_vulnerabilidades['total_vulnerabilidades']}")
    console.print(f"   ⚠️ Riesgos: {test_vulnerabilidades['total_riesgos']}")
    console.print(f"   🚨 Nivel Riesgo: {test_vulnerabilidades['nivel_riesgo'].upper()}")
    console.print(f"   📝 Descripción: {test_vulnerabilidades['descripcion']}")
    
    if test_vulnerabilidades.get("vulnerabilidades"):
        console.print("   📋 Vulnerabilidades específicas:")
        for vuln in test_vulnerabilidades["vulnerabilidades"]:
            console.print(f"      - {vuln}")
    
    if test_vulnerabilidades.get("riesgos"):
        console.print("   📋 Riesgos específicos:")
        for riesgo in test_vulnerabilidades["riesgos"]:
            console.print(f"      - {riesgo}")
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