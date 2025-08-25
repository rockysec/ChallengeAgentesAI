"""
Herramienta ofensiva: Enumeración anónima LDAP
"""

import logging
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)

def tool_anonymous_enum(base_dn: str = None, max_results: int = 100) -> Dict[str, Any]:
    """
    Realiza enumeración anónima del directorio LDAP para extraer información sensible.
    
    Esta herramienta realiza un bind anónimo (-x) al servidor LDAP y enumera objetos
    y atributos clave que pueden revelar información valiosa para análisis de seguridad:
    
    - uid: Identificadores de usuario
    - cn: Nombres comunes
    - memberOf: Membresías en grupos
    - userPassword: Contraseñas (si están expuestas)
    - shadow*: Atributos de sombra (shadowLastChange, shadowMin, etc.)
    - objectClass: Tipos de objetos
    - description: Descripciones de objetos
    
    Args:
        base_dn (str, optional): DN base para la búsqueda (por defecto usa configuración del sistema)
        max_results (int, optional): Número máximo de resultados a retornar (por defecto 100)
        
    Returns:
        Dict[str, Any]: Resultado de la enumeración anónima con metadatos de seguridad
        
    Raises:
        No lanza excepciones, todas las excepciones son capturadas y retornadas
        como parte del diccionario de resultado.
        
    Example:
        >>> resultado = tool_anonymous_enum()
        >>> if not resultado["error"]:
        ...     print(f"Usuarios encontrados: {len(resultado['resultado']['usuarios'])}")
    """
    try:
        console.print(Panel("🔴 Iniciando enumeración anónima LDAP", style="red"))
        
        # Importar el conector LDAP
        from ..tools_base.ldap_connector import LDAPConnector
        
        # Crear conexión LDAP
        ldap_conn = LDAPConnector()
        
        # Intentar conexión anónima
        console.print(Panel("🔓 Intentando bind anónimo...", style="yellow"))
        
        if not ldap_conn.connect():
            return {
                "error": True,
                "mensaje": "No se pudo conectar al servidor LDAP",
                "herramienta": "tool_anonymous_enum",
                "tipo": "error_conexion"
            }
        
        try:
            # Verificar si el bind anónimo está permitido
            console.print(Panel("🔍 Verificando permisos de bind anónimo...", style="blue"))
            
            # Realizar búsqueda de prueba para verificar permisos
            resultado_prueba = ldap_conn.search("", "(objectClass=*)")
            
            if not resultado_prueba:
                return {
                    "error": True,
                    "mensaje": "Bind anónimo no permitido o sin resultados",
                    "herramienta": "tool_anonymous_enum",
                    "tipo": "error_permisos"
                }
            
            console.print(Panel("✅ Bind anónimo exitoso - Iniciando enumeración", style="green"))
            
            # Realizar enumeración completa
            resultado_enum = _realizar_enumeracion_completa(ldap_conn, base_dn, max_results)
            
            # Análisis de seguridad de los resultados
            analisis_seguridad = _analizar_seguridad_enum(resultado_enum)
            
            # Resultado final
            resultado_completo = {
                "enumeracion": resultado_enum,
                "analisis_seguridad": analisis_seguridad,
                "metadata": {
                    "herramienta": "tool_anonymous_enum",
                    "tipo": "enumeracion_anonima",
                    "categoria": "reconocimiento_ofensivo",
                    "riesgo": "medio",  # Enumeración anónima puede revelar información sensible
                    "timestamp": "ahora",  # TODO: usar datetime real
                    "base_dn": base_dn or "configuracion_sistema",
                    "max_results": max_results
                }
            }
            
            console.print(Panel("✅ Enumeración anónima completada exitosamente", style="green"))
            
            return {
                "error": False,
                "resultado": resultado_completo,
                "herramienta": "tool_anonymous_enum",
                "tipo": "enumeracion_anonima"
            }
            
        finally:
            # Siempre desconectar
            ldap_conn.disconnect()
            
    except Exception as e:
        logger.error(f"Error en tool_anonymous_enum: {e}")
        return {
            "error": True,
            "mensaje": f"Error ejecutando enumeración anónima: {str(e)}",
            "herramienta": "tool_anonymous_enum",
            "tipo": "error_ejecucion"
        }

def _realizar_enumeracion_completa(ldap_conn, base_dn: str, max_results: int) -> Dict[str, Any]:
    """
    Realiza la enumeración completa del directorio LDAP.
    
    Args:
        ldap_conn: Conexión LDAP activa
        base_dn (str): DN base para la búsqueda
        max_results (int): Número máximo de resultados
        
    Returns:
        Dict[str, Any]: Resultados de la enumeración organizados por categoría
    """
    # Usar base_dn del sistema si no se especifica
    if not base_dn:
        base_dn = "dc=meli,dc=com"  # TODO: obtener de configuración
    
    console.print(Panel(f"🔍 Enumerando desde: {base_dn}", style="blue"))
    
    # Búsqueda de usuarios
    console.print(Panel("👥 Enumerando usuarios...", style="cyan"))
    usuarios = _enumerar_usuarios(ldap_conn, base_dn, max_results)
    
    # Búsqueda de grupos
    console.print(Panel("👥 Enumerando grupos...", style="cyan"))
    grupos = _enumerar_grupos(ldap_conn, base_dn, max_results)
    
    # Búsqueda de objetos del sistema
    console.print(Panel("⚙️ Enumerando objetos del sistema...", style="cyan"))
    objetos_sistema = _enumerar_objetos_sistema(ldap_conn, base_dn, max_results)
    
    # Búsqueda de atributos sensibles
    console.print(Panel("🔐 Buscando atributos sensibles...", style="red"))
    atributos_sensibles = _buscar_atributos_sensibles(ldap_conn, base_dn, max_results)
    
    return {
        "usuarios": usuarios,
        "grupos": grupos,
        "objetos_sistema": objetos_sistema,
        "atributos_sensibles": atributos_sensibles,
        "resumen": {
            "total_usuarios": len(usuarios),
            "total_grupos": len(grupos),
            "total_objetos_sistema": len(objetos_sistema),
            "total_atributos_sensibles": len(atributos_sensibles)
        }
    }

def _enumerar_usuarios(ldap_conn, base_dn: str, max_results: int) -> List[Dict]:
    """
    Enumera usuarios del directorio LDAP.
    
    Args:
        ldap_conn: Conexión LDAP activa
        base_dn (str): DN base para la búsqueda
        max_results (int): Número máximo de resultados
        
    Returns:
        List[Dict]: Lista de usuarios encontrados
    """
    try:
        # Búsqueda de usuarios (person)
        filtro_usuarios = "(objectClass=person)"
        usuarios = ldap_conn.search(base_dn, filtro_usuarios)
        
        # Procesar y limpiar resultados
        usuarios_procesados = []
        for usuario in usuarios:
            usuario_limpio = _limpiar_entrada_ldap(usuario)
            if usuario_limpio:
                usuarios_procesados.append(usuario_limpio)
        
        # Limitar resultados si es necesario
        if max_results and len(usuarios_procesados) > max_results:
            usuarios_procesados = usuarios_procesados[:max_results]
        
        return usuarios_procesados
        
    except Exception as e:
        logger.error(f"Error enumerando usuarios: {e}")
        return []

def _enumerar_grupos(ldap_conn, base_dn: str, max_results: int) -> List[Dict]:
    """
    Enumera grupos del directorio LDAP.
    
    Args:
        ldap_conn: Conexión LDAP activa
        base_dn (str): DN base para la búsqueda
        max_results (int): Número máximo de resultados
        
    Returns:
        List[Dict]: Lista de grupos encontrados
    """
    try:
        # Búsqueda de grupos
        filtro_grupos = "(objectClass=groupOfNames)"
        grupos = ldap_conn.search(base_dn, filtro_grupos)
        
        # Procesar y limpiar resultados
        grupos_procesados = []
        for grupo in grupos:
            grupo_limpio = _limpiar_entrada_ldap(grupo)
            if grupo_limpio:
                grupos_procesados.append(grupo_limpio)
        
        # Limitar resultados si es necesario
        if max_results and len(grupos_procesados) > max_results:
            grupos_procesados = grupos_procesados[:max_results]
        
        return grupos_procesados
        
    except Exception as e:
        logger.error(f"Error enumerando grupos: {e}")
        return []

def _enumerar_objetos_sistema(ldap_conn, base_dn: str, max_results: int) -> List[Dict]:
    """
    Enumera objetos del sistema LDAP.
    
    Args:
        ldap_conn: Conexión LDAP activa
        base_dn (str): DN base para la búsqueda
        max_results (int): Número máximo de resultados
        
    Returns:
        List[Dict]: Lista de objetos del sistema encontrados
    """
    try:
        # Búsqueda de objetos del sistema
        filtro_sistema = "(objectClass=*)"
        objetos = ldap_conn.search(base_dn, filtro_sistema)
        
        # Filtrar solo objetos del sistema (no usuarios ni grupos)
        objetos_sistema = []
        for obj in objetos:
            obj_limpio = _limpiar_entrada_ldap(obj)
            if obj_limpio and _es_objeto_sistema(obj_limpio):
                objetos_sistema.append(obj_limpio)
        
        # Limitar resultados si es necesario
        if max_results and len(objetos_sistema) > max_results:
            objetos_sistema = objetos_sistema[:max_results]
        
        return objetos_sistema
        
    except Exception as e:
        logger.error(f"Error enumerando objetos del sistema: {e}")
        return []

def _buscar_atributos_sensibles(ldap_conn, base_dn: str, max_results: int) -> List[Dict]:
    """
    Busca atributos sensibles en el directorio LDAP.
    
    Args:
        ldap_conn: Conexión LDAP activa
        base_dn (str): DN base para la búsqueda
        max_results (int): Número máximo de resultados
        
    Returns:
        List[Dict]: Lista de entradas con atributos sensibles
    """
    try:
        # Atributos sensibles a buscar
        atributos_sensibles = [
            "userPassword", "shadowLastChange", "shadowMin", "shadowMax",
            "shadowWarning", "shadowInactive", "shadowExpire", "shadowFlag",
            "pwdLastSet", "pwdExpireDate", "pwdCanChange", "pwdMustChange"
        ]
        
        # Búsqueda de objetos con atributos sensibles
        filtro_sensibles = "(|(userPassword=*)(shadowLastChange=*)(pwdLastSet=*))"
        objetos_sensibles = ldap_conn.search(base_dn, filtro_sensibles)
        
        # Procesar y limpiar resultados
        sensibles_procesados = []
        for obj in objetos_sensibles:
            obj_limpio = _limpiar_entrada_ldap(obj)
            if obj_limpio and _tiene_atributos_sensibles(obj_limpio):
                sensibles_procesados.append(obj_limpio)
        
        # Limitar resultados si es necesario
        if max_results and len(sensibles_procesados) > max_results:
            sensibles_procesados = sensibles_procesados[:max_results]
        
        return sensibles_procesados
        
    except Exception as e:
        logger.error(f"Error buscando atributos sensibles: {e}")
        return []

def _limpiar_entrada_ldap(entrada: Dict) -> Dict:
    """
    Limpia y normaliza una entrada LDAP.
    
    Args:
        entrada (Dict): Entrada LDAP cruda
        
    Returns:
        Dict: Entrada limpia y normalizada
    """
    entrada_limpia = {}
    
    for atributo, valores in entrada.items():
        if atributo.lower() not in ['dn', 'distinguishedname']:
            # Normalizar nombres de atributos
            atributo_normalizado = atributo.lower()
            
            # Convertir valores a string si es necesario
            if isinstance(valores, list):
                valores_procesados = [str(v) for v in valores]
            else:
                valores_procesados = [str(valores)]
            
            entrada_limpia[atributo_normalizado] = valores_procesados
    
    return entrada_limpia

def _es_objeto_sistema(objeto: Dict) -> bool:
    """
    Determina si un objeto es del sistema (no usuario ni grupo).
    
    Args:
        objeto (Dict): Objeto LDAP procesado
        
    Returns:
        bool: True si es objeto del sistema
    """
    object_classes = objeto.get('objectclass', [])
    
    # Objetos que NO son del sistema
    no_sistema = ['person', 'organizationalperson', 'inetorgperson', 'groupofnames', 'posixgroup']
    
    # Si tiene alguna clase que NO es del sistema, no es objeto del sistema
    for clase in object_classes:
        if clase.lower() in no_sistema:
            return False
    
    return True

def _tiene_atributos_sensibles(objeto: Dict) -> bool:
    """
    Verifica si un objeto tiene atributos sensibles.
    
    Args:
        objeto (Dict): Objeto LDAP procesado
        
    Returns:
        bool: True si tiene atributos sensibles
    """
    atributos_sensibles = [
        'userpassword', 'shadowlastchange', 'shadowmin', 'shadowmax',
        'shadowwarning', 'shadowinactive', 'shadowexpire', 'shadowflag',
        'pwdlastset', 'pwdexpiredate', 'pwdcanchange', 'pwdmustchange'
    ]
    
    for atributo in atributos_sensibles:
        if atributo in objeto:
            return True
    
    return False

def _analizar_seguridad_enum(resultado_enum: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analiza la seguridad de los resultados de la enumeración.
    
    Args:
        resultado_enum (Dict[str, Any]): Resultados de la enumeración
        
    Returns:
        Dict[str, Any]: Análisis de seguridad
    """
    analisis = {
        "riesgos_detectados": [],
        "vulnerabilidades_potenciales": [],
        "recomendaciones": [],
        "nivel_riesgo": "bajo"
    }
    
    resumen = resultado_enum.get("resumen", {})
    atributos_sensibles = resultado_enum.get("atributos_sensibles", [])
    
    # Análisis de usuarios
    total_usuarios = resumen.get("total_usuarios", 0)
    if total_usuarios > 0:
        analisis["riesgos_detectados"].append(f"Usuarios enumerados: {total_usuarios}")
        analisis["recomendaciones"].append("Revisar permisos de acceso anónimo a usuarios")
    
    # Análisis de grupos
    total_grupos = resumen.get("total_grupos", 0)
    if total_grupos > 0:
        analisis["riesgos_detectados"].append(f"Grupos enumerados: {total_grupos}")
        analisis["recomendaciones"].append("Revisar permisos de acceso anónimo a grupos")
    
    # Análisis de atributos sensibles
    total_sensibles = resumen.get("total_atributos_sensibles", 0)
    if total_sensibles > 0:
        analisis["riesgos_detectados"].append(f"Atributos sensibles expuestos: {total_sensibles}")
        analisis["vulnerabilidades_potenciales"].append("Información sensible accesible anónimamente")
        analisis["nivel_riesgo"] = "alto"
        analisis["recomendaciones"].append("Restringir acceso anónimo a atributos sensibles")
        analisis["recomendaciones"].append("Implementar control de acceso basado en roles")
    
    # Análisis de objetos del sistema
    total_objetos = resumen.get("total_objetos_sistema", 0)
    if total_objetos > 0:
        analisis["riesgos_detectados"].append(f"Objetos del sistema enumerados: {total_objetos}")
        analisis["recomendaciones"].append("Revisar permisos de acceso anónimo a objetos del sistema")
    
    # Recomendaciones generales
    if total_usuarios > 0 or total_grupos > 0:
        analisis["recomendaciones"].append("Considerar deshabilitar bind anónimo si no es necesario")
        analisis["recomendaciones"].append("Implementar autenticación obligatoria para consultas")
    
    return analisis

def mostrar_resultado_enum(resultado: Dict[str, Any]):
    """
    Muestra el resultado de la enumeración anónima de manera formateada.
    
    Args:
        resultado (Dict[str, Any]): Resultado de tool_anonymous_enum
    """
    if resultado.get("error"):
        console.print(Panel(f"❌ Error: {resultado['mensaje']}", style="red"))
        return
    
    data = resultado["resultado"]
    enumeracion = data["enumeracion"]
    analisis_seguridad = data["analisis_seguridad"]
    
    # Mostrar resumen de la enumeración
    console.print(Panel("📊 Resumen de Enumeración Anónima", style="bold blue"))
    
    resumen = enumeracion["resumen"]
    table_resumen = Table(title="Resumen de Enumeración")
    table_resumen.add_column("Categoría", style="cyan")
    table_resumen.add_column("Cantidad", style="green")
    
    table_resumen.add_row("Usuarios", str(resumen['total_usuarios']))
    table_resumen.add_row("Grupos", str(resumen['total_grupos']))
    table_resumen.add_row("Objetos del Sistema", str(resumen['total_objetos_sistema']))
    table_resumen.add_row("Atributos Sensibles", str(resumen['total_atributos_sensibles']))
    
    console.print(table_resumen)
    
    # Mostrar análisis de seguridad
    console.print(Panel("🔒 Análisis de Seguridad", style="bold red"))
    
    table_seguridad = Table(title="Análisis de Seguridad")
    table_seguridad.add_column("Categoría", style="cyan")
    table_seguridad.add_column("Detalles", style="yellow")
    
    table_seguridad.add_row("Nivel de Riesgo", analisis_seguridad["nivel_riesgo"].upper())
    table_seguridad.add_row("Riesgos Detectados", str(len(analisis_seguridad["riesgos_detectados"])))
    table_seguridad.add_row("Vulnerabilidades", str(len(analisis_seguridad["vulnerabilidades_potenciales"])))
    
    console.print(table_seguridad)
    
    # Mostrar recomendaciones
    if analisis_seguridad["recomendaciones"]:
        console.print(Panel("💡 Recomendaciones de Seguridad", style="bold yellow"))
        for i, rec in enumerate(analisis_seguridad["recomendaciones"], 1):
            console.print(f"{i}. {rec}")
    
    # Mostrar detalles de atributos sensibles si los hay
    if resumen['total_atributos_sensibles'] > 0:
        console.print(Panel("⚠️ Atributos Sensibles Detectados", style="bold red"))
        atributos_sensibles = enumeracion["atributos_sensibles"]
        
        for i, obj in enumerate(atributos_sensibles[:5], 1):  # Mostrar solo los primeros 5
            console.print(f"{i}. {obj.get('dn', 'N/A')}")
            for attr, valores in obj.items():
                if attr in ['userpassword', 'shadowlastchange', 'pwdlastset']:
                    console.print(f"   {attr}: {'*' * len(str(valores))}")  # Ocultar valores sensibles
        
        if resumen['total_atributos_sensibles'] > 5:
            console.print(f"   ... y {resumen['total_atributos_sensibles'] - 5} más") 