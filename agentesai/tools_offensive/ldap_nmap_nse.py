"""
Herramienta ofensiva: Fingerprint LDAP usando Nmap NSE Scripts
"""

import logging
import subprocess
import re
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)

def tool_ldap_nmap_nse(target: str = None, port: int = 389, scripts: str = None, 
                       timeout: int = 30, verbose: bool = False) -> Dict[str, Any]:
    """
    Ejecuta nmap -p389 --script ldap-rootdse,ldap-search para fingerprint adicional de LDAP.
    
    Esta herramienta utiliza scripts de NSE de Nmap para realizar:
    - Fingerprint del servidor LDAP
    - Análisis de RootDSE usando NSE
    - Búsquedas LDAP con scripts especializados
    - Detección de información del servidor
    - Análisis de configuración y versiones
    
    Args:
        target (str, optional): Objetivo LDAP (IP o hostname)
        port (int, optional): Puerto LDAP (por defecto 389)
        scripts (str, optional): Scripts NSE específicos a ejecutar
        timeout (int, optional): Timeout en segundos para la ejecución
        verbose (bool, optional): Modo verbose para más detalles
        
    Returns:
        Dict[str, Any]: Resultado del fingerprint NSE con análisis de seguridad
        
    Raises:
        No lanza excepciones, todas las excepciones son capturadas y retornadas
        como parte del diccionario de resultado.
        
    Example:
        >>> resultado = tool_ldap_nmap_nse("192.168.1.100")
        >>> if not resultado["error"]:
        ...     print(f"Fingerprint: {resultado['resultado']['fingerprint']}")
    """
    try:
        console.print(Panel("🔴 Iniciando fingerprint LDAP usando Nmap NSE Scripts", style="red"))
        
        # Verificar parámetros requeridos
        if not target:
            # Intentar obtener target desde configuración del sistema o usar localhost por defecto
            target = _obtener_target_por_defecto()
            if not target:
                return {
                    "error": True,
                    "mensaje": "Se requiere un objetivo (target) para el fingerprint NSE. Use: 'nmap nse 192.168.1.100' o configure un target por defecto",
                    "herramienta": "tool_ldap_nmap_nse",
                    "tipo": "error_parametros"
                }
        
        # Scripts por defecto si no se especifican
        if not scripts:
            scripts = "ldap-rootdse,ldap-search"
        
        # Test 1: Verificar disponibilidad de nmap
        console.print(Panel("🔍 Test 1: Verificación de Disponibilidad de Nmap", style="blue"))
        resultado_nmap_check = _verificar_disponibilidad_nmap()
        
        # Test 2: Verificar conectividad al objetivo
        console.print(Panel("🌐 Test 2: Verificación de Conectividad", style="blue"))
        resultado_conectividad = _verificar_conectividad(target, port)
        
        # Test 3: Ejecutar scripts NSE
        console.print(Panel("🔐 Test 3: Ejecución de Scripts NSE", style="blue"))
        resultado_nse = _ejecutar_scripts_nse(target, port, scripts, timeout, verbose)
        
        # Test 4: Análisis de resultados NSE
        console.print(Panel("📊 Test 4: Análisis de Resultados NSE", style="blue"))
        resultado_analisis = _analizar_resultados_nse(resultado_nse)
        
        # Análisis de seguridad
        analisis_seguridad = _analizar_seguridad_nse(
            resultado_nmap_check, resultado_conectividad, resultado_nse, resultado_analisis
        )
        
        # Resultado final
        resultado_completo = {
            "tests": {
                "verificacion_nmap": resultado_nmap_check,
                "verificacion_conectividad": resultado_conectividad,
                "ejecucion_nse": resultado_nse,
                "analisis_resultados": resultado_analisis
            },
            "analisis_seguridad": analisis_seguridad,
            "metadata": {
                "herramienta": "tool_ldap_nmap_nse",
                "tipo": "fingerprint_nse",
                "categoria": "reconocimiento_ofensivo",
                "riesgo": "bajo",  # Fingerprint pasivo
                "timestamp": "ahora",  # TODO: usar datetime real
                "target": target,
                "port": port,
                "scripts": scripts,
                "timeout": timeout
            }
        }
        
        console.print(Panel("✅ Fingerprint NSE completado exitosamente", style="green"))
        
        return {
            "error": False,
            "resultado": resultado_completo,
            "herramienta": "tool_ldap_nmap_nse",
            "tipo": "fingerprint_nse"
        }
        
    except Exception as e:
        logger.error(f"Error en tool_ldap_nmap_nse: {e}")
        return {
            "error": True,
            "mensaje": f"Error ejecutando fingerprint NSE: {str(e)}",
            "herramienta": "tool_ldap_nmap_nse",
            "tipo": "error_ejecucion"
        }

def _obtener_target_por_defecto() -> str:
    """
    Obtiene el target por defecto desde configuración del sistema o usa localhost.
    
    Returns:
        str: Target por defecto o None si no se puede determinar
    """
    try:
        # Intentar obtener desde configuración del sistema
        # Por ahora, usar localhost como fallback
        target_por_defecto = "localhost"
        
        console.print(f"   ⚠️ No se especificó target, usando por defecto: {target_por_defecto}")
        console.print("   💡 Para especificar un target: 'nmap nse 192.168.1.100' o 'fingerprint nmap ldap.example.com'")
        
        return target_por_defecto
        
    except Exception as e:
        logger.error(f"Error obteniendo target por defecto: {e}")
        return None

def _verificar_disponibilidad_nmap() -> Dict[str, Any]:
    """
    Verifica si nmap está disponible en el sistema.
    
    Returns:
        Dict[str, Any]: Resultado de la verificación de nmap
    """
    try:
        # Intentar ejecutar nmap --version
        resultado = subprocess.run(
            ["nmap", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if resultado.returncode == 0:
            # Extraer versión de nmap
            version_match = re.search(r'Nmap version (\d+\.\d+)', resultado.stdout)
            version = version_match.group(1) if version_match else "desconocida"
            
            return {
                "estado": "exitoso",
                "nmap_disponible": True,
                "version": version,
                "comando": "nmap --version",
                "vulnerabilidad": "Nmap disponible para fingerprint"
            }
        else:
            return {
                "estado": "fallido",
                "nmap_disponible": False,
                "version": "no disponible",
                "comando": "nmap --version",
                "vulnerabilidad": "Nmap no disponible o no ejecutable"
            }
            
    except FileNotFoundError:
        return {
            "estado": "fallido",
            "nmap_disponible": False,
            "version": "no instalado",
            "comando": "nmap --version",
            "vulnerabilidad": "Nmap no está instalado en el sistema"
        }
    except subprocess.TimeoutExpired:
        return {
            "estado": "error",
            "nmap_disponible": False,
            "version": "timeout",
            "comando": "nmap --version",
            "vulnerabilidad": "Timeout al verificar nmap"
        }
    except Exception as e:
        return {
            "estado": "error",
            "nmap_disponible": False,
            "version": "error",
            "comando": "nmap --version",
            "vulnerabilidad": f"Error verificando nmap: {str(e)}"
        }

def _verificar_conectividad(target: str, port: int) -> Dict[str, Any]:
    """
    Verifica la conectividad básica al objetivo LDAP.
    
    Args:
        target (str): Objetivo LDAP
        port (int): Puerto LDAP
        
    Returns:
        Dict[str, Any]: Resultado de la verificación de conectividad
    """
    try:
        # Usar nmap para verificar conectividad básica
        comando = ["nmap", "-p", str(port), "--open", target]
        
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if resultado.returncode == 0:
            # Analizar salida para verificar si el puerto está abierto
            if f"{port}/tcp" in resultado.stdout and "open" in resultado.stdout:
                return {
                    "estado": "exitoso",
                    "target": target,
                    "port": port,
                    "conectividad": True,
                    "puerto_abierto": True,
                    "comando": " ".join(comando),
                    "vulnerabilidad": "Puerto LDAP accesible para fingerprint"
                }
            else:
                return {
                    "estado": "fallido",
                    "target": target,
                    "port": port,
                    "conectividad": False,
                    "puerto_abierto": False,
                    "comando": " ".join(comando),
                    "vulnerabilidad": "Puerto LDAP no accesible"
                }
        else:
            return {
                "estado": "fallido",
                "target": target,
                "port": port,
                "conectividad": False,
                "puerto_abierto": False,
                "comando": " ".join(comando),
                "vulnerabilidad": f"Error en verificación de conectividad: {resultado.stderr}"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "estado": "error",
            "target": target,
            "port": port,
            "conectividad": False,
            "puerto_abierto": False,
            "comando": "nmap -p {port} --open {target}",
            "vulnerabilidad": "Timeout en verificación de conectividad"
        }
    except Exception as e:
        return {
            "estado": "error",
            "target": target,
            "port": port,
            "conectividad": False,
            "puerto_abierto": False,
            "comando": "nmap -p {port} --open {target}",
            "vulnerabilidad": f"Error en verificación de conectividad: {str(e)}"
        }

def _ejecutar_scripts_nse(target: str, port: int, scripts: str, timeout: int, verbose: bool) -> Dict[str, Any]:
    """
    Ejecuta los scripts NSE especificados contra el objetivo LDAP.
    
    Args:
        target (str): Objetivo LDAP
        port (int): Puerto LDAP
        scripts (str): Scripts NSE a ejecutar
        timeout (int): Timeout en segundos
        verbose (bool): Modo verbose
        
    Returns:
        Dict[str, Any]: Resultado de la ejecución de scripts NSE
    """
    try:
        # Construir comando nmap con scripts NSE
        comando = [
            "nmap", 
            "-p", str(port), 
            "--script", scripts,
            "--script-timeout", str(timeout),
            target
        ]
        
        if verbose:
            comando.append("-v")
        
        console.print(f"   🔍 Ejecutando: {' '.join(comando)}")
        
        # Ejecutar nmap con scripts NSE
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=timeout + 10  # Agregar margen de seguridad
        )
        
        if resultado.returncode == 0:
            return {
                "estado": "exitoso",
                "target": target,
                "port": port,
                "scripts": scripts,
                "comando": " ".join(comando),
                "stdout": resultado.stdout,
                "stderr": resultado.stderr,
                "returncode": resultado.returncode,
                "vulnerabilidad": "Scripts NSE ejecutados exitosamente"
            }
        else:
            return {
                "estado": "fallido",
                "target": target,
                "port": port,
                "scripts": scripts,
                "comando": " ".join(comando),
                "stdout": resultado.stdout,
                "stderr": resultado.stderr,
                "returncode": resultado.returncode,
                "vulnerabilidad": f"Scripts NSE fallaron con código {resultado.returncode}"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "estado": "error",
            "target": target,
            "port": port,
            "scripts": scripts,
            "comando": f"nmap -p {port} --script {scripts} {target}",
            "stdout": "",
            "stderr": "Timeout en ejecución de scripts NSE",
            "returncode": -1,
            "vulnerabilidad": "Timeout en ejecución de scripts NSE"
        }
    except Exception as e:
        return {
            "estado": "error",
            "target": target,
            "port": port,
            "scripts": scripts,
            "comando": f"nmap -p {port} --script {scripts} {target}",
            "stdout": "",
            "stderr": f"Error en ejecución: {str(e)}",
            "returncode": -1,
            "vulnerabilidad": f"Error ejecutando scripts NSE: {str(e)}"
        }

def _analizar_resultados_nse(resultado_nse: Dict) -> Dict[str, Any]:
    """
    Analiza los resultados de la ejecución de scripts NSE.
    
    Args:
        resultado_nse (Dict): Resultado de la ejecución de scripts NSE
        
    Returns:
        Dict[str, Any]: Análisis de los resultados NSE
    """
    try:
        if resultado_nse.get("estado") != "exitoso":
            return {
                "estado": "error",
                "analisis_completado": False,
                "informacion_detectada": [],
                "vulnerabilidades_nse": [],
                "servidor_info": {},
                "descripcion": "No se pudieron analizar resultados NSE"
            }
        
        stdout = resultado_nse.get("stdout", "")
        stderr = resultado_nse.get("stderr", "")
        
        # Extraer información del servidor LDAP
        servidor_info = _extraer_info_servidor(stdout)
        
        # Extraer información de RootDSE
        rootdse_info = _extraer_info_rootdse(stdout)
        
        # Extraer información de búsquedas
        busqueda_info = _extraer_info_busqueda(stdout)
        
        # Detectar vulnerabilidades específicas
        vulnerabilidades = _detectar_vulnerabilidades_nse(stdout, stderr)
        
        # Consolidar información detectada
        informacion_detectada = []
        if servidor_info:
            informacion_detectada.append("Información del servidor LDAP")
        if rootdse_info:
            informacion_detectada.append("Información RootDSE")
        if busqueda_info:
            informacion_detectada.append("Información de búsquedas")
        
        return {
            "estado": "completado",
            "analisis_completado": True,
            "informacion_detectada": informacion_detectada,
            "vulnerabilidades_nse": vulnerabilidades,
            "servidor_info": servidor_info,
            "rootdse_info": rootdse_info,
            "busqueda_info": busqueda_info,
            "descripcion": f"Análisis completado: {len(informacion_detectada)} tipos de información detectados"
        }
        
    except Exception as e:
        return {
            "estado": "error",
            "analisis_completado": False,
            "informacion_detectada": [],
            "vulnerabilidades_nse": [],
            "servidor_info": {},
            "descripcion": f"Error analizando resultados NSE: {str(e)}"
        }

def _extraer_info_servidor(stdout: str) -> Dict[str, Any]:
    """
    Extrae información del servidor LDAP desde la salida de nmap.
    
    Args:
        stdout (str): Salida estándar de nmap
        
    Returns:
        Dict[str, Any]: Información del servidor extraída
    """
    info = {}
    
    try:
        # Buscar información de puerto abierto
        puerto_match = re.search(r'(\d+)/tcp\s+(\w+)', stdout)
        if puerto_match:
            info["puerto"] = puerto_match.group(1)
            info["estado"] = puerto_match.group(2)
        
        # Buscar información de servicio
        servicio_match = re.search(r'(\d+)/tcp\s+\w+\s+(\w+)', stdout)
        if servicio_match:
            info["servicio"] = servicio_match.group(2)
        
        # Buscar información de versión si está disponible
        version_match = re.search(r'(\d+\.\d+\.\d+)', stdout)
        if version_match:
            info["version"] = version_match.group(1)
        
        # Buscar información de hostname
        hostname_match = re.search(r'Host is up', stdout)
        if hostname_match:
            info["host_up"] = True
        
    except Exception as e:
        logger.error(f"Error extrayendo información del servidor: {e}")
    
    return info

def _extraer_info_rootdse(stdout: str) -> Dict[str, Any]:
    """
    Extrae información de RootDSE desde la salida de nmap.
    
    Args:
        stdout (str): Salida estándar de nmap
        
    Returns:
        Dict[str, Any]: Información RootDSE extraída
    """
    info = {}
    
    try:
        # Buscar información de namingContexts
        naming_contexts = re.findall(r'namingContexts:\s*(.+)', stdout)
        if naming_contexts:
            info["namingContexts"] = naming_contexts
        
        # Buscar información de supportedSASLMechanisms
        sasl_mechanisms = re.findall(r'supportedSASLMechanisms:\s*(.+)', stdout)
        if sasl_mechanisms:
            info["supportedSASLMechanisms"] = sasl_mechanisms
        
        # Buscar información de supportedControls
        supported_controls = re.findall(r'supportedControls:\s*(.+)', stdout)
        if supported_controls:
            info["supportedControls"] = supported_controls
        
        # Buscar información de supportedExtensions
        supported_extensions = re.findall(r'supportedExtensions:\s*(.+)', stdout)
        if supported_extensions:
            info["supportedExtensions"] = supported_extensions
        
        # Buscar información de vendorName
        vendor_name = re.search(r'vendorName:\s*(.+)', stdout)
        if vendor_name:
            info["vendorName"] = vendor_name.group(1)
        
        # Buscar información de vendorVersion
        vendor_version = re.search(r'vendorVersion:\s*(.+)', stdout)
        if vendor_version:
            info["vendorVersion"] = vendor_version.group(1)
        
    except Exception as e:
        logger.error(f"Error extrayendo información RootDSE: {e}")
    
    return info

def _extraer_info_busqueda(stdout: str) -> Dict[str, Any]:
    """
    Extrae información de búsquedas LDAP desde la salida de nmap.
    
    Args:
        stdout (str): Salida estándar de nmap
        
    Returns:
        Dict[str, Any]: Información de búsquedas extraída
    """
    info = {}
    
    try:
        # Buscar información de resultados de búsqueda
        resultados_busqueda = re.findall(r'(\w+):\s*(.+)', stdout)
        if resultados_busqueda:
            info["atributos_encontrados"] = dict(resultados_busqueda)
        
        # Buscar información de DN encontrados
        dns_encontrados = re.findall(r'dn:\s*(.+)', stdout)
        if dns_encontrados:
            info["dns_encontrados"] = dns_encontrados
        
        # Buscar información de objectClass
        object_classes = re.findall(r'objectClass:\s*(.+)', stdout)
        if object_classes:
            info["objectClasses"] = object_classes
        
        # Buscar información de usuarios
        usuarios = re.findall(r'uid:\s*(.+)', stdout)
        if usuarios:
            info["usuarios"] = usuarios
        
        # Buscar información de grupos
        grupos = re.findall(r'cn:\s*(.+)', stdout)
        if grupos:
            info["grupos"] = grupos
        
    except Exception as e:
        logger.error(f"Error extrayendo información de búsquedas: {e}")
    
    return info

def _detectar_vulnerabilidades_nse(stdout: str, stderr: str) -> List[str]:
    """
    Detecta vulnerabilidades específicas desde la salida de scripts NSE.
    
    Args:
        stdout (str): Salida estándar de nmap
        stderr (str): Salida de error de nmap
        
    Returns:
        List[str]: Lista de vulnerabilidades detectadas
    """
    vulnerabilidades = []
    
    try:
        # Detectar información sensible expuesta
        if "userPassword:" in stdout:
            vulnerabilidades.append("Contraseñas de usuario expuestas en búsquedas")
        
        if "shadowLastChange:" in stdout:
            vulnerabilidades.append("Información de shadow password expuesta")
        
        if "pwdLastSet:" in stdout:
            vulnerabilidades.append("Información de política de contraseñas expuesta")
        
        # Detectar información de configuración expuesta
        if "olcRootDN:" in stdout:
            vulnerabilidades.append("DN raíz de configuración expuesto")
        
        if "olcSuffix:" in stdout:
            vulnerabilidades.append("Sufijos de configuración expuestos")
        
        # Detectar información de usuarios y grupos
        if len(re.findall(r'uid:\s*(.+)', stdout)) > 10:
            vulnerabilidades.append("Gran cantidad de usuarios enumerados")
        
        if len(re.findall(r'cn:\s*(.+)', stdout)) > 10:
            vulnerabilidades.append("Gran cantidad de grupos enumerados")
        
        # Detectar errores de autenticación
        if "Invalid credentials" in stderr:
            vulnerabilidades.append("Credenciales inválidas detectadas")
        
        if "Connection refused" in stderr:
            vulnerabilidades.append("Conexión LDAP rechazada")
        
        # Detectar información de versión
        if "vendorVersion:" in stdout:
            version_match = re.search(r'vendorVersion:\s*(.+)', stdout)
            if version_match:
                version = version_match.group(1)
                if "2.4" in version or "2.3" in version:
                    vulnerabilidades.append(f"Versión LDAP potencialmente vulnerable: {version}")
        
    except Exception as e:
        logger.error(f"Error detectando vulnerabilidades NSE: {e}")
    
    return vulnerabilidades

def _analizar_seguridad_nse(resultado_nmap_check: Dict, resultado_conectividad: Dict, 
                           resultado_nse: Dict, resultado_analisis: Dict) -> Dict[str, Any]:
    """
    Analiza la seguridad general de los resultados NSE.
    
    Args:
        resultado_nmap_check (Dict): Resultado de verificación de nmap
        resultado_conectividad (Dict): Resultado de verificación de conectividad
        resultado_nse (Dict): Resultado de ejecución de scripts NSE
        resultado_analisis (Dict): Resultado del análisis de resultados
        
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
    
    # Análisis de disponibilidad de nmap
    if not resultado_nmap_check.get("nmap_disponible"):
        analisis["riesgos_detectados"].append("Nmap no disponible para fingerprint")
        analisis["recomendaciones"].append("Instalar nmap para análisis de seguridad completo")
    
    # Análisis de conectividad
    if resultado_conectividad.get("puerto_abierto"):
        analisis["configuracion_actual"] = f"Puerto LDAP {resultado_conectividad['port']} accesible"
        analisis["riesgos_detectados"].append("Puerto LDAP accesible para fingerprint externo")
        analisis["recomendaciones"].append("Considerar restricción de acceso al puerto LDAP")
    else:
        analisis["configuracion_actual"] = f"Puerto LDAP {resultado_conectividad['port']} no accesible"
    
    # Análisis de scripts NSE
    if resultado_nse.get("estado") == "exitoso":
        analisis["configuracion_actual"] += ", Scripts NSE ejecutados exitosamente"
        
        # Analizar vulnerabilidades detectadas
        vulnerabilidades_nse = resultado_analisis.get("vulnerabilidades_nse", [])
        if vulnerabilidades_nse:
            analisis["vulnerabilidades_potenciales"].extend(vulnerabilidades_nse)
            analisis["nivel_riesgo"] = "medio"
            analisis["recomendaciones"].append("Investigar vulnerabilidades detectadas por NSE")
        
        # Analizar información expuesta
        info_detectada = resultado_analisis.get("informacion_detectada", [])
        if len(info_detectada) > 2:
            analisis["riesgos_detectados"].append("Gran cantidad de información expuesta")
            analisis["recomendaciones"].append("Revisar configuración de permisos LDAP")
    
    # Análisis de información específica
    rootdse_info = resultado_analisis.get("rootdse_info", {})
    if rootdse_info.get("vendorVersion"):
        analisis["configuracion_actual"] += f", Versión: {rootdse_info['vendorVersion']}"
    
    if rootdse_info.get("namingContexts"):
        analisis["configuracion_actual"] += f", Contextos: {len(rootdse_info['namingContexts'])}"
    
    # Recomendaciones generales
    if analisis["nivel_riesgo"] == "medio":
        analisis["recomendaciones"].append("Implementar logging de acceso LDAP")
        analisis["recomendaciones"].append("Revisar configuración de permisos")
    elif analisis["nivel_riesgo"] == "bajo":
        analisis["recomendaciones"].append("Mantener monitoreo de acceso LDAP")
    
    analisis["recomendaciones"].append("Implementar detección de anomalías")
    analisis["recomendaciones"].append("Revisar regularmente logs de acceso")
    analisis["recomendaciones"].append("Considerar implementación de WAF o IPS")
    
    return analisis

def mostrar_resultado_ldap_nmap_nse(resultado: Dict[str, Any]):
    """
    Muestra el resultado del fingerprint NSE de manera formateada.
    
    Args:
        resultado (Dict[str, Any]): Resultado de tool_ldap_nmap_nse
    """
    if resultado.get("error"):
        console.print(Panel(f"❌ Error: {resultado['mensaje']}", style="red"))
        return
    
    data = resultado["resultado"]
    tests = data["tests"]
    analisis_seguridad = data["analisis_seguridad"]
    
    # Título principal
    console.print(Panel("🔍 FINGERPRINT LDAP USANDO NMAP NSE SCRIPTS", style="bold red"))
    console.print()
    
    # Mostrar cada test individualmente con detalles
    console.print(Panel("🧪 DETALLES DE CADA PRUEBA REALIZADA", style="bold blue"))
    console.print()
    
    # Test 1: Verificación de Disponibilidad de Nmap
    test_nmap = tests["verificacion_nmap"]
    console.print(Panel("🔍 PRUEBA 1: Verificación de Disponibilidad de Nmap", style="cyan"))
    console.print(f"   📊 Estado: {test_nmap['estado'].upper()}")
    console.print(f"   🔧 Nmap Disponible: {'✅ Sí' if test_nmap['nmap_disponible'] else '❌ No'}")
    console.print(f"   📋 Versión: {test_nmap['version']}")
    console.print(f"   💻 Comando: {test_nmap['comando']}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_nmap['vulnerabilidad']}")
    console.print()
    
    # Test 2: Verificación de Conectividad
    test_conectividad = tests["verificacion_conectividad"]
    console.print(Panel("🌐 PRUEBA 2: Verificación de Conectividad", style="cyan"))
    console.print(f"   📊 Estado: {test_conectividad['estado'].upper()}")
    console.print(f"   🎯 Target: {test_conectividad['target']}")
    console.print(f"   🔌 Puerto: {test_conectividad['port']}")
    console.print(f"   🌐 Conectividad: {'✅ Activa' if test_conectividad['conectividad'] else '❌ Fallida'}")
    console.print(f"   🔓 Puerto Abierto: {'✅ Sí' if test_conectividad['puerto_abierto'] else '❌ No'}")
    console.print(f"   💻 Comando: {test_conectividad['comando']}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_conectividad['vulnerabilidad']}")
    console.print()
    
    # Test 3: Ejecución de Scripts NSE
    test_nse = tests["ejecucion_nse"]
    console.print(Panel("🔐 PRUEBA 3: Ejecución de Scripts NSE", style="cyan"))
    console.print(f"   📊 Estado: {test_nse['estado'].upper()}")
    console.print(f"   🎯 Target: {test_nse['target']}")
    console.print(f"   🔌 Puerto: {test_nse['port']}")
    console.print(f"   📜 Scripts: {test_nse['scripts']}")
    console.print(f"   💻 Comando: {test_nse['comando']}")
    console.print(f"   📊 Return Code: {test_nse['returncode']}")
    console.print(f"   ⚠️ Vulnerabilidad: {test_nse['vulnerabilidad']}")
    console.print()
    
    # Test 4: Análisis de Resultados NSE
    test_analisis = tests["analisis_resultados"]
    console.print(Panel("📊 PRUEBA 4: Análisis de Resultados NSE", style="cyan"))
    console.print(f"   📊 Estado: {test_analisis['estado'].upper()}")
    console.print(f"   🔍 Análisis Completado: {'✅ Sí' if test_analisis['analisis_completado'] else '❌ No'}")
    console.print(f"   📋 Información Detectada: {len(test_analisis['informacion_detectada'])} tipos")
    console.print(f"   🚨 Vulnerabilidades: {len(test_analisis['vulnerabilidades_nse'])}")
    console.print(f"   📝 Descripción: {test_analisis['descripcion']}")
    
    if test_analisis.get("informacion_detectada"):
        console.print("   📋 Tipos de información:")
        for info in test_analisis["informacion_detectada"]:
            console.print(f"      - {info}")
    
    if test_analisis.get("vulnerabilidades_nse"):
        console.print("   🚨 Vulnerabilidades específicas:")
        for vuln in test_analisis["vulnerabilidades_nse"]:
            console.print(f"      - {vuln}")
    
    # Mostrar información del servidor si está disponible
    if test_analisis.get("servidor_info"):
        servidor_info = test_analisis["servidor_info"]
        console.print("   🔍 Información del servidor:")
        for key, value in servidor_info.items():
            console.print(f"      {key}: {value}")
    
    # Mostrar información RootDSE si está disponible
    if test_analisis.get("rootdse_info"):
        rootdse_info = test_analisis["rootdse_info"]
        console.print("   🔐 Información RootDSE:")
        for key, value in rootdse_info.items():
            if isinstance(value, list):
                console.print(f"      {key}: {len(value)} elementos")
            else:
                console.print(f"      {key}: {value}")
    
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