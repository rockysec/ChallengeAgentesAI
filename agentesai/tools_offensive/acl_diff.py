"""
Herramienta ofensiva: Comparación de ACLs - Anónimo vs Admin LDAP
"""

import logging
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)

def tool_acl_diff(admin_username: str = None, admin_password: str = None, base_dn: str = None, max_results: int = 100) -> Dict[str, Any]:
    """
    Compara lo que ve un bind anónimo vs un bind autenticado admin para detectar diferencias en ACLs.
    
    Esta herramienta realiza dos análisis LDAP paralelos:
    1. Bind anónimo (-x) para ver permisos mínimos
    2. Bind autenticado como admin para ver permisos máximos
    
    Compara los resultados para detectar:
    - Diferencias en objetos visibles
    - Diferencias en atributos accesibles
    - Vulnerabilidades de control de acceso
    - Información sensible expuesta anónimamente
    - Posibles escalaciones de privilegios
    
    Args:
        admin_username (str, optional): Usuario admin para autenticación
        admin_password (str, optional): Contraseña del usuario admin
        base_dn (str, optional): DN base para la búsqueda
        max_results (int, optional): Número máximo de resultados por búsqueda
        
    Returns:
        Dict[str, Any]: Resultado de la comparación ACL con análisis de seguridad
        
    Raises:
        No lanza excepciones, todas las excepciones son capturadas y retornadas
        como parte del diccionario de resultado.
        
    Example:
        >>> resultado = tool_acl_diff("admin", "password123")
        >>> if not resultado["error"]:
        ...     print(f"Diferencias detectadas: {resultado['resultado']['diferencias_detectadas']}")
    """
    try:
        console.print(Panel("🔴 Iniciando comparación de ACLs - Anónimo vs Admin LDAP", style="red"))
        
        # Importar el conector LDAP
        from ..tools_base.ldap_connector import LDAPConnector
        
        # Verificar credenciales admin
        if not admin_username or not admin_password:
            return {
                "error": True,
                "mensaje": "Se requieren credenciales de admin para la comparación ACL",
                "herramienta": "tool_acl_diff",
                "tipo": "error_credenciales"
            }
        
        # Test 1: Bind anónimo
        console.print(Panel("🔓 Test 1: Bind Anónimo (permisos mínimos)", style="blue"))
        resultado_anonimo = _test_bind_anonimo(admin_username, admin_password, base_dn, max_results)
        
        # Test 2: Bind admin
        console.print(Panel("👑 Test 2: Bind Admin (permisos máximos)", style="blue"))
        resultado_admin = _test_bind_admin(admin_username, admin_password, base_dn, max_results)
        
        # Test 3: Análisis de diferencias
        console.print(Panel("⚖️ Test 3: Análisis de Diferencias ACL", style="blue"))
        resultado_diferencias = _analizar_diferencias_acl(resultado_anonimo, resultado_admin)
        
        # Test 4: Detección de vulnerabilidades
        console.print(Panel("⚠️ Test 4: Detección de Vulnerabilidades ACL", style="yellow"))
        resultado_vulnerabilidades = _detectar_vulnerabilidades_acl(resultado_anonimo, resultado_admin, resultado_diferencias)
        
        # Análisis de seguridad
        analisis_seguridad = _analizar_seguridad_acl(
            resultado_anonimo, resultado_admin, resultado_diferencias, resultado_vulnerabilidades
        )
        
        # Resultado final
        resultado_completo = {
            "tests": {
                "bind_anonimo": resultado_anonimo,
                "bind_admin": resultado_admin,
                "analisis_diferencias": resultado_diferencias,
                "deteccion_vulnerabilidades": resultado_vulnerabilidades
            },
            "analisis_seguridad": analisis_seguridad,
            "metadata": {
                "herramienta": "tool_acl_diff",
                "tipo": "comparacion_acls",
                "categoria": "reconocimiento_ofensivo",
                "riesgo": "medio",  # Comparación de permisos ACL
                "timestamp": "ahora",  # TODO: usar datetime real
                "admin_usuario": admin_username,
                "base_dn": base_dn or "configuracion_sistema"
            }
        }
        
        console.print(Panel("✅ Comparación de ACLs completada exitosamente", style="green"))
        
        return {
            "error": False,
            "resultado": resultado_completo,
            "herramienta": "tool_acl_diff",
            "tipo": "comparacion_acls"
        }
        
    except Exception as e:
        logger.error(f"Error en tool_acl_diff: {e}")
        return {
            "error": True,
            "mensaje": f"Error ejecutando comparación de ACLs: {str(e)}",
            "herramienta": "tool_acl_diff",
            "tipo": "error_ejecucion"
        }

def _test_bind_anonimo(admin_username: str, admin_password: str, base_dn: str, max_results: int) -> Dict[str, Any]:
    """
    Test de bind anónimo para ver permisos mínimos.
    
    Args:
        admin_username (str): Usuario admin (no usado en bind anónimo)
        admin_password (str): Contraseña admin (no usado en bind anónimo)
        base_dn (str): DN base para la búsqueda
        max_results (int): Número máximo de resultados
        
    Returns:
        Dict[str, Any]: Resultado del test de bind anónimo
    """
    try:
        # Crear conexión LDAP para bind anónimo
        ldap_conn = _crear_conexion_ldap()
        
        # Intentar bind anónimo
        if ldap_conn.connect():
            # Realizar búsquedas anónimas
            resultado_busqueda = _realizar_busquedas_anonimas(ldap_conn, base_dn, max_results)
            
            return {
                "estado": "exitoso",
                "tipo_bind": "anonimo",
                "usuario": "anonymous",
                "conexion": True,
                "resultados_busqueda": resultado_busqueda,
                "total_objetos": _contar_total_objetos(resultado_busqueda),
                "permisos": _evaluar_permisos_anonimos(resultado_busqueda),
                "metodo_autenticacion": "anonymous_bind",
                "vulnerabilidad": "Bind anónimo permitido"
            }
        else:
            return {
                "estado": "fallido",
                "tipo_bind": "anonimo",
                "usuario": "anonymous",
                "conexion": False,
                "resultados_busqueda": {},
                "total_objetos": 0,
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
            "resultados_busqueda": {},
            "total_objetos": 0,
            "permisos": "error",
            "metodo_autenticacion": "anonymous_bind",
            "vulnerabilidad": f"Error en bind anónimo: {str(e)}"
        }

def _test_bind_admin(admin_username: str, admin_password: str, base_dn: str, max_results: int) -> Dict[str, Any]:
    """
    Test de bind admin para ver permisos máximos.
    
    Args:
        admin_username (str): Usuario admin para autenticación
        admin_password (str): Contraseña del usuario admin
        base_dn (str): DN base para la búsqueda
        max_results (int): Número máximo de resultados
        
    Returns:
        Dict[str, Any]: Resultado del test de bind admin
    """
    try:
        # Crear conexión LDAP para bind admin
        ldap_conn = _crear_conexion_ldap()
        
        # Intentar bind admin
        if ldap_conn.connect(username=admin_username, password=admin_password):
            # Realizar búsquedas como admin
            resultado_busqueda = _realizar_busquedas_admin(ldap_conn, base_dn, max_results)
            
            return {
                "estado": "exitoso",
                "tipo_bind": "admin",
                "usuario": admin_username,
                "conexion": True,
                "resultados_busqueda": resultado_busqueda,
                "total_objetos": _contar_total_objetos(resultado_busqueda),
                "permisos": _evaluar_permisos_admin(resultado_busqueda),
                "metodo_autenticacion": "simple_bind",
                "vulnerabilidad": "Bind admin exitoso"
            }
        else:
            return {
                "estado": "fallido",
                "tipo_bind": "admin",
                "usuario": admin_username,
                "conexion": False,
                "resultados_busqueda": {},
                "total_objetos": 0,
                "permisos": "sin_acceso",
                "metodo_autenticacion": "simple_bind",
                "vulnerabilidad": "Credenciales admin inválidas o acceso denegado"
            }
            
    except Exception as e:
        return {
            "estado": "error",
            "tipo_bind": "admin",
            "usuario": admin_username,
            "conexion": False,
            "resultados_busqueda": {},
            "total_objetos": 0,
            "permisos": "error",
            "metodo_autenticacion": "simple_bind",
            "vulnerabilidad": f"Error en bind admin: {str(e)}"
        }

def _crear_conexion_ldap():
    """
    Crea una nueva conexión LDAP.
    
    Returns:
        LDAPConnector: Instancia del conector LDAP
    """
    from ..tools_base.ldap_connector import LDAPConnector
    return LDAPConnector()

def _realizar_busquedas_anonimas(ldap_conn, base_dn: str, max_results: int) -> Dict[str, Any]:
    """
    Realiza búsquedas anónimas para evaluar permisos mínimos.
    
    Args:
        ldap_conn: Conexión LDAP
        base_dn (str): DN base para la búsqueda
        max_results (int): Número máximo de resultados
        
    Returns:
        Dict[str, Any]: Resultados de las búsquedas anónimas
    """
    if not base_dn:
        base_dn = "dc=meli,dc=com"  # TODO: obtener de configuración
    
    resultados = {}
    
    try:
        # Búsqueda de usuarios
        usuarios = ldap_conn.search(base_dn, "(objectClass=person)")
        if usuarios and len(usuarios) > max_results:
            usuarios = usuarios[:max_results]
        resultados["usuarios"] = usuarios or []
        
        # Búsqueda de grupos
        grupos = ldap_conn.search(base_dn, "(objectClass=groupOfNames)")
        if grupos and len(grupos) > max_results:
            grupos = grupos[:max_results]
        resultados["grupos"] = grupos or []
        
        # Búsqueda de objetos del sistema
        objetos_sistema = ldap_conn.search(base_dn, "(objectClass=*)")
        if objetos_sistema and len(objetos_sistema) > max_results:
            objetos_sistema = objetos_sistema[:max_results]
        resultados["objetos_sistema"] = objetos_sistema or []
        
        # Búsqueda de atributos sensibles
        atributos_sensibles = ldap_conn.search(base_dn, "(|(userPassword=*)(shadowLastChange=*)(pwdLastSet=*))")
        if atributos_sensibles and len(atributos_sensibles) > max_results:
            atributos_sensibles = atributos_sensibles[:max_results]
        resultados["atributos_sensibles"] = atributos_sensibles or []
        
    except Exception as e:
        logger.error(f"Error en búsquedas anónimas: {e}")
        resultados = {
            "usuarios": [],
            "grupos": [],
            "objetos_sistema": [],
            "atributos_sensibles": []
        }
    
    return resultados

def _realizar_busquedas_admin(ldap_conn, base_dn: str, max_results: int) -> Dict[str, Any]:
    """
    Realiza búsquedas como admin para evaluar permisos máximos.
    
    Args:
        ldap_conn: Conexión LDAP
        base_dn (str): DN base para la búsqueda
        max_results (int): Número máximo de resultados
        
    Returns:
        Dict[str, Any]: Resultados de las búsquedas como admin
    """
    if not base_dn:
        base_dn = "dc=meli,dc=com"  # TODO: obtener de configuración
    
    resultados = {}
    
    try:
        # Búsqueda de usuarios (admin debería ver más)
        usuarios = ldap_conn.search(base_dn, "(objectClass=person)")
        if usuarios and len(usuarios) > max_results:
            usuarios = usuarios[:max_results]
        resultados["usuarios"] = usuarios or []
        
        # Búsqueda de grupos (admin debería ver más)
        grupos = ldap_conn.search(base_dn, "(objectClass=groupOfNames)")
        if grupos and len(grupos) > max_results:
            grupos = grupos[:max_results]
        resultados["grupos"] = grupos or []
        
        # Búsqueda de objetos del sistema (admin debería ver más)
        objetos_sistema = ldap_conn.search(base_dn, "(objectClass=*)")
        if objetos_sistema and len(objetos_sistema) > max_results:
            objetos_sistema = objetos_sistema[:max_results]
        resultados["objetos_sistema"] = objetos_sistema or []
        
        # Búsqueda de atributos sensibles (admin debería ver más)
        atributos_sensibles = ldap_conn.search(base_dn, "(|(userPassword=*)(shadowLastChange=*)(pwdLastSet=*))")
        if atributos_sensibles and len(atributos_sensibles) > max_results:
            atributos_sensibles = atributos_sensibles[:max_results]
        resultados["atributos_sensibles"] = atributos_sensibles or []
        
        # Búsquedas adicionales solo para admin
        configuracion = ldap_conn.search(base_dn, "(objectClass=olcGlobal)")
        if configuracion and len(configuracion) > max_results:
            configuracion = configuracion[:max_results]
        resultados["configuracion"] = configuracion or []
        
    except Exception as e:
        logger.error(f"Error en búsquedas admin: {e}")
        resultados = {
            "usuarios": [],
            "grupos": [],
            "objetos_sistema": [],
            "atributos_sensibles": [],
            "configuracion": []
        }
    
    return resultados

def _contar_total_objetos(resultados_busqueda: Dict[str, Any]) -> int:
    """
    Cuenta el total de objetos en los resultados de búsqueda.
    
    Args:
        resultados_busqueda (Dict[str, Any]): Resultados de búsqueda
        
    Returns:
        int: Total de objetos encontrados
    """
    total = 0
    for categoria, objetos in resultados_busqueda.items():
        if isinstance(objetos, list):
            total += len(objetos)
    return total

def _evaluar_permisos_anonimos(resultados_busqueda: Dict[str, Any]) -> str:
    """
    Evalúa los permisos del bind anónimo basándose en los resultados.
    
    Args:
        resultados_busqueda (Dict[str, Any]): Resultados de búsqueda anónima
        
    Returns:
        str: Nivel de permisos evaluado
    """
    total_objetos = _contar_total_objetos(resultados_busqueda)
    
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

def _evaluar_permisos_admin(resultados_busqueda: Dict[str, Any]) -> str:
    """
    Evalúa los permisos del bind admin basándose en los resultados.
    
    Args:
        resultados_busqueda (Dict[str, Any]): Resultados de búsqueda admin
        
    Returns:
        str: Nivel de permisos evaluado
    """
    total_objetos = _contar_total_objetos(resultados_busqueda)
    
    if total_objetos == 0:
        return "sin_acceso"
    elif total_objetos <= 50:
        return "acceso_limitado"
    elif total_objetos <= 200:
        return "acceso_moderado"
    elif total_objetos <= 500:
        return "acceso_amplio"
    else:
        return "acceso_completo"

def _analizar_diferencias_acl(resultado_anonimo: Dict, resultado_admin: Dict) -> Dict[str, Any]:
    """
    Analiza las diferencias entre los permisos anónimos y admin.
    
    Args:
        resultado_anonimo (Dict): Resultado del test de bind anónimo
        resultado_admin (Dict): Resultado del test de bind admin
        
    Returns:
        Dict[str, Any]: Análisis de diferencias ACL
    """
    try:
        # Extraer información básica
        permisos_anonimo = resultado_anonimo.get("permisos", "desconocido")
        permisos_admin = resultado_admin.get("permisos", "desconocido")
        total_anonimo = resultado_anonimo.get("total_objetos", 0)
        total_admin = resultado_admin.get("total_objetos", 0)
        
        # Calcular diferencias
        diferencia_objetos = total_admin - total_objetos
        diferencia_porcentual = (diferencia_objetos / total_admin * 100) if total_admin > 0 else 0
        
        # Análisis de categorías específicas
        diferencias_categoria = _analizar_diferencias_por_categoria(
            resultado_anonimo.get("resultados_busqueda", {}),
            resultado_admin.get("resultados_busqueda", {})
        )
        
        # Evaluar nivel de riesgo
        if total_anonimo > 0 and total_anonimo >= total_admin * 0.8:
            riesgo = "alto"
            descripcion = "Bind anónimo tiene acceso casi igual al admin (CRÍTICO)"
        elif total_anonimo > 0 and total_anonimo >= total_admin * 0.5:
            riesgo = "medio"
            descripcion = "Bind anónimo tiene acceso significativo"
        elif total_anonimo > 0 and total_anonimo < total_admin * 0.5:
            riesgo = "bajo"
            descripcion = "Bind anónimo tiene acceso limitado"
        else:
            riesgo = "bajo"
            descripcion = "Bind anónimo sin acceso (seguro)"
        
        return {
            "estado": "completado",
            "permisos_anonimo": permisos_anonimo,
            "permisos_admin": permisos_admin,
            "total_anonimo": total_anonimo,
            "total_admin": total_admin,
            "diferencia_objetos": diferencia_objetos,
            "diferencia_porcentual": round(diferencia_porcentual, 2),
            "diferencias_categoria": diferencias_categoria,
            "riesgo": riesgo,
            "descripcion": descripcion,
            "vulnerabilidad": _identificar_vulnerabilidad_acl(permisos_anonimo, permisos_admin, total_anonimo, total_admin)
        }
        
    except Exception as e:
        return {
            "estado": "error",
            "permisos_anonimo": "error",
            "permisos_admin": "error",
            "total_anonimo": 0,
            "total_admin": 0,
            "diferencia_objetos": 0,
            "diferencia_porcentual": 0,
            "diferencias_categoria": {},
            "riesgo": "desconocido",
            "descripcion": f"Error analizando diferencias: {str(e)}",
            "vulnerabilidad": "Error en análisis"
        }

def _analizar_diferencias_por_categoria(resultados_anonimo: Dict, resultados_admin: Dict) -> Dict[str, Any]:
    """
    Analiza las diferencias por categoría específica.
    
    Args:
        resultados_anonimo (Dict): Resultados anónimos por categoría
        resultados_admin (Dict): Resultados admin por categoría
        
    Returns:
        Dict[str, Any]: Diferencias por categoría
    """
    diferencias = {}
    
    categorias = ["usuarios", "grupos", "objetos_sistema", "atributos_sensibles"]
    
    for categoria in categorias:
        anonimo = resultados_anonimo.get(categoria, [])
        admin = resultados_admin.get(categoria, [])
        
        if isinstance(anonimo, list) and isinstance(admin, list):
            total_anonimo = len(anonimo)
            total_admin = len(admin)
            diferencia = total_admin - total_anonimo
            
            diferencias[categoria] = {
                "anonimo": total_anonimo,
                "admin": total_admin,
                "diferencia": diferencia,
                "porcentaje": round((total_anonimo / total_admin * 100) if total_admin > 0 else 0, 2)
            }
    
    return diferencias

def _identificar_vulnerabilidad_acl(permisos_anonimo: str, permisos_admin: str, total_anonimo: int, total_admin: int) -> str:
    """
    Identifica vulnerabilidades basándose en la comparación de permisos ACL.
    
    Args:
        permisos_anonimo (str): Permisos del bind anónimo
        permisos_admin (str): Permisos del bind admin
        total_anonimo (int): Total de objetos vistos por anónimo
        total_admin (int): Total de objetos vistos por admin
        
    Returns:
        str: Vulnerabilidad identificada
    """
    if total_anonimo == 0:
        return "Configuración segura - sin acceso anónimo"
    elif total_anonimo >= total_admin * 0.8:
        return "CRÍTICO: Bind anónimo con acceso casi igual al admin"
    elif total_anonimo >= total_admin * 0.5:
        return "ALTO: Bind anónimo con acceso significativo"
    elif total_anonimo >= total_admin * 0.2:
        return "MEDIO: Bind anónimo con acceso moderado"
    else:
        return "BAJO: Bind anónimo con acceso limitado"

def _detectar_vulnerabilidades_acl(resultado_anonimo: Dict, resultado_admin: Dict, 
                                 resultado_diferencias: Dict) -> Dict[str, Any]:
    """
    Detecta vulnerabilidades específicas en la configuración ACL.
    
    Args:
        resultado_anonimo (Dict): Resultado del test de bind anónimo
        resultado_admin (Dict): Resultado del test de bind admin
        resultado_diferencias (Dict): Resultado del análisis de diferencias
        
    Returns:
        Dict[str, Any]: Resultado de la detección de vulnerabilidades
    """
    try:
        vulnerabilidades = []
        riesgos = []
        
        # Verificar si ambos binds fueron exitosos
        if (resultado_anonimo.get("estado") == "exitoso" and 
            resultado_admin.get("estado") == "exitoso"):
            
            # Análisis de diferencias de objetos
            diferencia_porcentual = resultado_diferencias.get("diferencia_porcentual", 0)
            if diferencia_porcentual < 20:
                vulnerabilidades.append("Bind anónimo con acceso casi igual al admin")
                riesgos.append("Posible escalación de privilegios")
            
            # Análisis de atributos sensibles
            atributos_anonimo = resultado_anonimo.get("resultados_busqueda", {}).get("atributos_sensibles", [])
            if len(atributos_anonimo) > 0:
                vulnerabilidades.append("Atributos sensibles accesibles anónimamente")
                riesgos.append("Información sensible expuesta")
            
            # Análisis de configuración
            config_admin = resultado_admin.get("resultados_busqueda", {}).get("configuracion", [])
            config_anonimo = resultado_anonimo.get("resultados_busqueda", {}).get("configuracion", [])
            if len(config_anonimo) > 0:
                vulnerabilidades.append("Configuración del sistema accesible anónimamente")
                riesgos.append("Información de configuración expuesta")
        
        # Análisis de permisos excesivos
        permisos_anonimo = resultado_anonimo.get("permisos", "desconocido")
        if permisos_anonimo in ["acceso_amplio", "acceso_excesivo"]:
            vulnerabilidades.append("Bind anónimo con permisos excesivos")
            riesgos.append("Acceso anónimo no restringido")
        
        return {
            "estado": "completado",
            "vulnerabilidades": vulnerabilidades,
            "riesgos": riesgos,
            "total_vulnerabilidades": len(vulnerabilidades),
            "total_riesgos": len(riesgos),
            "riesgo": "alto" if vulnerabilidades else "bajo",
            "descripcion": f"Se detectaron {len(vulnerabilidades)} vulnerabilidades y {len(riesgos)} riesgos"
        }
        
    except Exception as e:
        return {
            "estado": "error",
            "vulnerabilidades": [],
            "riesgos": [],
            "total_vulnerabilidades": 0,
            "total_riesgos": 0,
            "riesgo": "desconocido",
            "descripcion": f"Error detectando vulnerabilidades: {str(e)}"
        }

def _analizar_seguridad_acl(resultado_anonimo: Dict, resultado_admin: Dict, 
                           resultado_diferencias: Dict, resultado_vulnerabilidades: Dict) -> Dict[str, Any]:
    """
    Analiza la seguridad de la configuración ACL.
    
    Args:
        resultado_anonimo (Dict): Resultado del test de bind anónimo
        resultado_admin (Dict): Resultado del test de bind admin
        resultado_diferencias (Dict): Resultado del análisis de diferencias
        resultado_vulnerabilidades (Dict): Resultado de la detección de vulnerabilidades
        
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
    
    # Análisis de bind anónimo
    if resultado_anonimo.get("estado") == "exitoso":
        permisos_anonimo = resultado_anonimo.get("permisos", "desconocido")
        total_anonimo = resultado_anonimo.get("total_objetos", 0)
        
        if permisos_anonimo in ["acceso_amplio", "acceso_excesivo"]:
            analisis["riesgos_detectados"].append("Bind anónimo con permisos excesivos")
            analisis["vulnerabilidades_potenciales"].append("Información sensible accesible anónimamente")
            analisis["nivel_riesgo"] = "alto"
            analisis["recomendaciones"].append("Restringir permisos del bind anónimo")
        elif permisos_anonimo in ["acceso_moderado"]:
            analisis["riesgos_detectados"].append("Bind anónimo con permisos moderados")
            analisis["nivel_riesgo"] = "medio"
            analisis["recomendaciones"].append("Revisar si el acceso anónimo es necesario")
        
        if total_anonimo > 0:
            analisis["configuracion_actual"] = f"Bind anónimo con acceso a {total_anonimo} objetos"
    
    # Análisis de bind admin
    if resultado_admin.get("estado") == "exitoso":
        permisos_admin = resultado_admin.get("permisos", "desconocido")
        total_admin = resultado_admin.get("total_objetos", 0)
        
        if permisos_admin == "acceso_completo":
            analisis["configuracion_actual"] += f", Admin con acceso completo a {total_admin} objetos"
        else:
            analisis["recomendaciones"].append("Verificar permisos del usuario admin")
    
    # Análisis de diferencias
    if resultado_diferencias.get("riesgo") == "alto":
        analisis["riesgos_detectados"].append("Diferencia crítica en permisos ACL")
        analisis["vulnerabilidades_potenciales"].append("Bind anónimo con acceso excesivo")
        analisis["nivel_riesgo"] = "alto"
        analisis["recomendaciones"].append("Revisar configuración de ACLs LDAP")
    
    # Análisis de vulnerabilidades
    if resultado_vulnerabilidades.get("total_vulnerabilidades") > 0:
        analisis["riesgos_detectados"].extend(resultado_vulnerabilidades.get("riesgos", []))
        analisis["vulnerabilidades_potenciales"].extend(resultado_vulnerabilidades.get("vulnerabilidades", []))
        analisis["nivel_riesgo"] = "alto"
        analisis["recomendaciones"].append("Investigar y corregir vulnerabilidades detectadas")
    
    # Recomendaciones generales
    if analisis["nivel_riesgo"] == "alto":
        analisis["recomendaciones"].append("Revisar configuración de ACLs LDAP inmediatamente")
        analisis["recomendaciones"].append("Implementar políticas de acceso estrictas")
    elif analisis["nivel_riesgo"] == "medio":
        analisis["recomendaciones"].append("Revisar configuración de permisos LDAP")
        analisis["recomendaciones"].append("Considerar restricciones adicionales")
    
    analisis["recomendaciones"].append("Implementar logging de acceso LDAP")
    analisis["recomendaciones"].append("Revisar regularmente permisos de usuarios y grupos")
    analisis["recomendaciones"].append("Considerar deshabilitar bind anónimo si no es necesario")
    
    return analisis

def mostrar_resultado_acl_diff(resultado: Dict[str, Any]):
    """
    Muestra el resultado de la comparación ACL de manera formateada.
    
    Args:
        resultado (Dict[str, Any]): Resultado de tool_acl_diff
    """
    if resultado.get("error"):
        console.print(Panel(f"❌ Error: {resultado['mensaje']}", style="red"))
        return
    
    data = resultado["resultado"]
    tests = data["tests"]
    analisis_seguridad = data["analisis_seguridad"]
    
    # Título principal
    console.print(Panel("🔐 COMPARACIÓN DE ACLs - ANÓNIMO vs ADMIN LDAP", style="bold red"))
    console.print()
    
    # Mostrar cada test individualmente con detalles
    console.print(Panel("🧪 DETALLES DE CADA PRUEBA REALIZADA", style="bold blue"))
    console.print()
    
    # Test 1: Bind Anónimo
    test_anonimo = tests["bind_anonimo"]
    console.print(Panel("🔓 PRUEBA 1: Bind Anónimo (permisos mínimos)", style="cyan"))
    console.print(f"   📊 Estado: {test_anonimo['estado'].upper()}")
    console.print(f"   🔐 Tipo Bind: {test_anonimo['tipo_bind']}")
    console.print(f"   👤 Usuario: {test_anonimo['usuario']}")
    console.print(f"   🔌 Conexión: {'✅ Activa' if test_anonimo['conexion'] else '❌ Fallida'}")
    console.print(f"   🔍 Total Objetos: {test_anonimo['total_objetos']}")
    console.print(f"   🔑 Permisos: {test_anonimo['permisos']}")
    console.print(f"   🔒 Método: {test_anonimo['metodo_autenticacion']}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_anonimo['vulnerabilidad']}")
    console.print()
    
    # Test 2: Bind Admin
    test_admin = tests["bind_admin"]
    console.print(Panel("👑 PRUEBA 2: Bind Admin (permisos máximos)", style="cyan"))
    console.print(f"   📊 Estado: {test_admin['estado'].upper()}")
    console.print(f"   🔐 Tipo Bind: {test_admin['tipo_bind']}")
    console.print(f"   👤 Usuario: {test_admin['usuario']}")
    console.print(f"   🔌 Conexión: {'✅ Activa' if test_admin['conexion'] else '❌ Fallida'}")
    console.print(f"   🔍 Total Objetos: {test_admin['total_objetos']}")
    console.print(f"   🔑 Permisos: {test_admin['permisos']}")
    console.print(f"   🔒 Método: {test_admin['metodo_autenticacion']}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_admin['vulnerabilidad']}")
    console.print()
    
    # Test 3: Análisis de Diferencias
    test_diferencias = tests["analisis_diferencias"]
    console.print(Panel("⚖️ PRUEBA 3: Análisis de Diferencias ACL", style="cyan"))
    console.print(f"   📊 Estado: {test_diferencias['estado'].upper()}")
    console.print(f"   🔑 Permisos Anónimo: {test_diferencias['permisos_anonimo']}")
    console.print(f"   🔑 Permisos Admin: {test_diferencias['permisos_admin']}")
    console.print(f"   📊 Total Anónimo: {test_diferencias['total_anonimo']}")
    console.print(f"   📊 Total Admin: {test_diferencias['total_admin']}")
    console.print(f"   📊 Diferencia: {test_diferencias['diferencia_objetos']} objetos")
    console.print(f"   📊 Diferencia %: {test_diferencias['diferencia_porcentual']}%")
    console.print(f"   🚨 Riesgo: {test_diferencias['riesgo'].upper()}")
    console.print(f"   📝 Descripción: {test_diferencias['descripcion']}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_diferencias['vulnerabilidad']}")
    console.print()
    
    # Mostrar diferencias por categoría
    if test_diferencias.get("diferencias_categoria"):
        console.print(Panel("📋 DIFERENCIAS POR CATEGORÍA", style="bold yellow"))
        for categoria, info in test_diferencias["diferencias_categoria"].items():
            console.print(f"   🔍 {categoria.title()}:")
            console.print(f"      Anónimo: {info['anonimo']} | Admin: {info['admin']} | Diferencia: {info['diferencia']} | %: {info['porcentaje']}%")
        console.print()
    
    # Test 4: Detección de Vulnerabilidades
    test_vulnerabilidades = tests["deteccion_vulnerabilidades"]
    console.print(Panel("⚠️ PRUEBA 4: Detección de Vulnerabilidades ACL", style="cyan"))
    console.print(f"   📊 Estado: {test_vulnerabilidades['estado'].upper()}")
    console.print(f"   🚨 Vulnerabilidades: {test_vulnerabilidades['total_vulnerabilidades']}")
    console.print(f"   ⚠️ Riesgos: {test_vulnerabilidades['total_riesgos']}")
    console.print(f"   🚨 Riesgo: {test_vulnerabilidades['riesgo'].upper()}")
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