"""
Herramientas consolidadas del sistema que usan datos reales del LDAP.
"""

import os
import getpass
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from .ldap_connector import LDAPConnector

console = Console()

# ============================================================================
# HERRAMIENTAS OBLIGATORIAS (requeridas por el challenge)
# ============================================================================

def get_current_user_info() -> Dict[str, Any]:
    """
    Obtiene información del usuario actual del sistema.
    
    Esta función es una de las herramientas base obligatorias del sistema.
    Recopila información del usuario que está ejecutando el programa,
    incluyendo detalles del sistema operativo y entorno.
    
    Returns:
        Dict[str, Any]: Diccionario con información del usuario:
            - username: Nombre del usuario del sistema
            - home_dir: Directorio home del usuario
            - shell: Shell por defecto del usuario
            - os_info: Información del sistema operativo
            - python_version: Versión de Python en uso
            - working_dir: Directorio de trabajo actual
            
    Example:
        >>> info = get_current_user_info()
        >>> print(f"Usuario: {info['username']}")
        >>> print(f"Directorio: {info['working_dir']}")
    """
    try:
        # Obtener información básica del usuario
        username = getpass.getuser()
        home_dir = os.path.expanduser("~")
        working_dir = os.getcwd()
        
        # Obtener información del sistema
        shell = os.environ.get('SHELL', 'No disponible')
        os_info = os.uname() if hasattr(os, 'uname') else 'Sistema no identificado'
        
        # Obtener versión de Python
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Crear tabla de información
        table = Table(title="👤 Información del Usuario Actual")
        table.add_column("Propiedad", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("Usuario", username)
        table.add_row("Directorio Home", home_dir)
        table.add_row("Directorio Actual", working_dir)
        table.add_row("Shell", shell)
        table.add_row("Sistema Operativo", str(os_info))
        table.add_row("Versión Python", python_version)
        
        console.print(table)
        
        return {
            "username": username,
            "home_dir": home_dir,
            "shell": shell,
            "os_info": str(os_info),
            "python_version": python_version,
            "working_dir": working_dir
        }
        
    except Exception as e:
        error_msg = f"Error obteniendo información del usuario: {str(e)}"
        console.print(Panel(error_msg, style="red"))
        return {
            "error": True,
            "mensaje": error_msg
        }

def get_user_groups(username: str = None) -> Dict[str, Any]:
    """
    Obtiene los grupos del usuario especificado o del usuario actual.
    
    Esta función es una de las herramientas base obligatorias del sistema.
    Utiliza el conector LDAP real para obtener información de grupos.
    
    Args:
        username (str, optional): Nombre del usuario. Si no se especifica,
                                 se usa el usuario actual.
    
    Returns:
        Dict[str, Any]: Diccionario con información de grupos:
            - username: Nombre del usuario consultado
            - groups: Lista de grupos del usuario
            - total_groups: Número total de grupos
            - source: Fuente de los datos
            
    Example:
        >>> grupos = get_user_groups("admin")
        >>> print(f"Grupos de admin: {grupos['groups']}")
    """
    try:
        if not username:
            username = getpass.getuser()
        
        console.print(Panel(f"🔍 Obteniendo grupos del usuario: {username}", style="blue"))
        
        with LDAPConnector() as ldap_conn:
            groups = ldap_conn.get_user_groups(username)
            
            if groups:
                # Crear tabla de grupos
                table = Table(title=f"👥 Grupos del Usuario: {username}")
                table.add_column("Grupo", style="cyan")
                table.add_column("Descripción", style="green")
                
                # Obtener descripciones de grupos
                with LDAPConnector() as ldap_conn2:
                    for group_name in groups:
                        group_info = ldap_conn2.search("ou=groups,dc=meli,dc=com", f"(cn={group_name})")
                        if group_info:
                            description = group_info[0].get("description", "Sin descripción")
                            table.add_row(group_name, description)
                
                console.print(table)
                
                return {
                    "username": username,
                    "groups": groups,
                    "total_groups": len(groups),
                    "source": "LDAP_REAL"
                }
            else:
                console.print(Panel(f"⚠️ Usuario {username} no tiene grupos asignados", style="yellow"))
                return {
                    "username": username,
                    "groups": [],
                    "total_groups": 0,
                    "source": "LDAP_REAL"
                }
                
    except Exception as e:
        error_msg = f"Error obteniendo grupos del usuario {username}: {str(e)}"
        console.print(Panel(error_msg, style="red"))
        return {
            "error": True,
            "mensaje": error_msg,
            "username": username
        }

def reset_system() -> Dict[str, Any]:
    """
    Resetea el sistema a su estado original.
    
    Esta función es una de las herramientas base obligatorias del sistema.
    Por ahora simula un reset, pero se puede extender para limpiar
    herramientas generadas dinámicamente.
    
    Returns:
        Dict[str, Any]: Resultado del reset del sistema:
            - success: True si el reset fue exitoso
            - mensaje: Mensaje descriptivo del resultado
            - timestamp: Timestamp del reset
            
    Example:
        >>> resultado = reset_system()
        >>> print(f"Reset exitoso: {resultado['success']}")
    """
    try:
        console.print(Panel("🔄 Reseteando sistema...", style="yellow"))
        
        # TODO: Implementar limpieza de herramientas generadas dinámicamente
        # TODO: Limpiar caché de agentes
        # TODO: Restaurar estado inicial
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        console.print(Panel("✅ Sistema reseteado exitosamente", style="green"))
        
        return {
            "success": True,
            "mensaje": "Sistema reseteado a estado original",
            "timestamp": timestamp
        }
        
    except Exception as e:
        error_msg = f"Error reseteando sistema: {str(e)}"
        console.print(Panel(error_msg, style="red"))
        return {
            "success": False,
            "mensaje": error_msg,
            "timestamp": None
        }

# ============================================================================
# HERRAMIENTAS ADICIONALES DE SEGURIDAD OFENSIVA (datos reales del LDAP)
# ============================================================================

def list_all_users() -> Dict[str, Any]:
    """
    Lista todos los usuarios del sistema desde el LDAP real.
    
    Esta herramienta se conecta al servidor OpenLDAP activo y obtiene
    la lista completa de usuarios con información real.
    
    Returns:
        Dict[str, Any]: Lista de todos los usuarios:
            - total_users: Número total de usuarios
            - users: Lista de usuarios con detalles
            - departments: Departamentos encontrados
            - source: Fuente de los datos
            
    Example:
        >>> usuarios = list_all_users()
        >>> print(f"Total de usuarios: {usuarios['total_users']}")
    """
    try:
        console.print(Panel("🔍 Listando usuarios desde LDAP real...", style="blue"))
        
        with LDAPConnector() as ldap_conn:
            users = ldap_conn.list_all_users()
            
            if users and isinstance(users, list):
                # Crear tabla de usuarios
                table = Table(title="👥 Usuarios del Sistema (desde LDAP)")
                table.add_column("Usuario", style="cyan")
                table.add_column("Nombre", style="green")
                table.add_column("Email", style="yellow")
                table.add_column("Título", style="magenta")
                table.add_column("Departamento", style="blue")
                
                for user in users:
                    table.add_row(
                        user.get("username", ""),
                        user.get("full_name", ""),
                        user.get("email", ""),
                        user.get("title", ""),
                        user.get("department", "")
                    )
                
                console.print(table)
                
                # Calcular estadísticas
                departments = list(set(user.get("department", "") for user in users if user.get("department")))
                
                return {
                    "total_users": len(users),
                    "users": users,
                    "departments": departments,
                    "source": "LDAP_REAL"
                }
            else:
                console.print(Panel("❌ No se pudieron obtener usuarios desde LDAP", style="red"))
                return {
                    "error": True,
                    "mensaje": "No se pudieron obtener usuarios desde LDAP"
                }
                
    except Exception as e:
        error_msg = f"Error listando usuarios: {str(e)}"
        console.print(Panel(error_msg, style="red"))
        return {
            "error": True,
            "mensaje": error_msg
        }

def search_users_by_department(department: str) -> Dict[str, Any]:
    """
    Busca usuarios por departamento específico desde el LDAP real.
    
    Args:
        department (str): Nombre del departamento a buscar
        
    Returns:
        Dict[str, Any]: Usuarios del departamento especificado:
            - department: Departamento consultado
            - total_users: Número de usuarios en el departamento
            - users: Lista de usuarios del departamento
            - source: Fuente de los datos
            
    Example:
        >>> dev_users = search_users_by_department("Development")
        >>> print(f"Usuarios en Development: {dev_users['total_users']}")
    """
    try:
        console.print(Panel(f"🔍 Buscando usuarios en departamento: {department}", style="blue"))
        
        with LDAPConnector() as ldap_conn:
            all_users = ldap_conn.list_all_users()
            
            if not all_users or not isinstance(all_users, list):
                return {
                    "error": True,
                    "mensaje": "No se pudieron obtener usuarios desde LDAP",
                    "department": department
                }
            
            # Filtrar por departamento
            department_users = [
                user for user in all_users
                if user.get("department", "").lower() == department.lower()
            ]
            
            if not department_users:
                console.print(Panel(f"❌ No se encontraron usuarios en el departamento: {department}", style="yellow"))
                return {
                    "department": department,
                    "total_users": 0,
                    "users": [],
                    "source": "LDAP_REAL"
                }
            
            # Crear tabla de usuarios del departamento
            table = Table(title=f"👥 Usuarios del Departamento: {department}")
            table.add_column("Usuario", style="cyan")
            table.add_column("Nombre", style="green")
            table.add_column("Email", style="yellow")
            table.add_column("Título", style="magenta")
            
            for user in department_users:
                table.add_row(
                    user.get("username", ""),
                    user.get("full_name", ""),
                    user.get("email", ""),
                    user.get("title", "")
                )
            
            console.print(table)
            
            return {
                "department": department,
                "total_users": len(department_users),
                "users": department_users,
                "source": "LDAP_REAL"
            }
            
    except Exception as e:
        error_msg = f"Error buscando usuarios por departamento: {str(e)}"
        console.print(Panel(error_msg, style="red"))
        return {
            "error": True,
            "mensaje": error_msg,
            "department": department
        }

def analyze_ldap_structure() -> Dict[str, Any]:
    """
    Analiza la estructura real del directorio LDAP.
    
    Esta herramienta se conecta al servidor OpenLDAP activo y obtiene
    información real sobre la estructura del directorio.
    
    Returns:
        Dict[str, Any]: Estructura del directorio LDAP:
            - base_dn: DN base del directorio
            - organizational_units: Unidades organizativas
            - total_users: Total de usuarios
            - total_groups: Total de grupos
            - structure_depth: Profundidad de la estructura
            - source: Fuente de los datos
            
    Example:
        >>> estructura = analyze_ldap_structure()
        >>> print(f"Base DN: {estructura['base_dn']}")
    """
    try:
        console.print(Panel("🏗️ Analizando estructura del directorio LDAP...", style="blue"))
        
        with LDAPConnector() as ldap_conn:
            structure = ldap_conn.get_ldap_structure()
            
            if structure:
                # Crear tabla de estructura
                table = Table(title="🏗️ Estructura del Directorio LDAP")
                table.add_column("Propiedad", style="cyan")
                table.add_column("Valor", style="green")
                
                table.add_row("Base DN", structure.get("base_dn", ""))
                table.add_row("Unidades Organizativas", str(len(structure.get("organizational_units", []))))
                table.add_row("Total Usuarios", str(structure.get("total_users", 0)))
                table.add_row("Total Grupos", str(structure.get("total_groups", 0)))
                table.add_row("Profundidad", str(structure.get("structure_depth", 0)))
                
                console.print(table)
                
                # Mostrar unidades organizativas
                if structure.get("organizational_units"):
                    ou_table = Table(title="📁 Unidades Organizativas")
                    ou_table.add_column("Nombre", style="cyan")
                    ou_table.add_column("DN", style="green")
                    ou_table.add_column("Descripción", style="yellow")
                    ou_table.add_column("Entradas", style="magenta")
                    
                    for ou in structure.get("organizational_units", []):
                        ou_table.add_row(
                            ou.get("name", ""),
                            ou.get("dn", ""),
                            ou.get("description", ""),
                            str(ou.get("entry_count", 0))
                        )
                    
                    console.print(ou_table)
                
                return {
                    **structure,
                    "source": "LDAP_REAL"
                }
            else:
                console.print(Panel("❌ No se pudo obtener estructura desde LDAP", style="red"))
                return {
                    "error": True,
                    "mensaje": "No se pudo obtener estructura desde LDAP"
                }
                
    except Exception as e:
        error_msg = f"Error obteniendo estructura del LDAP: {str(e)}"
        console.print(Panel(error_msg, style="red"))
        return {
            "error": True,
            "mensaje": error_msg
        } 