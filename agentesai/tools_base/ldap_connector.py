"""
Conector LDAP real para el servidor OpenLDAP activo.
"""

import os
import ldap
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class LDAPConnector:
    """
    Conector real para servidor LDAP activo.
    
    Esta clase se conecta al servidor OpenLDAP real en localhost:389
    y proporciona métodos para consultar datos reales del directorio.
    
    Atributos:
        server_url (str): URL del servidor LDAP
        base_dn (str): DN base del directorio
        admin_dn (str): DN del administrador
        admin_password (str): Contraseña del administrador
        connection (object): Conexión LDAP activa
        
    Métodos principales:
        - connect(): Establece conexión con el servidor LDAP
        - disconnect(): Cierra la conexión LDAP
        - search(): Realiza búsquedas en el directorio
        - get_user_info(): Obtiene información de un usuario específico
        - get_user_groups(): Obtiene grupos de un usuario
        - list_all_users(): Lista todos los usuarios
        - list_all_groups(): Lista todos los grupos
    """
    
    def __init__(self, server_url: str = None, base_dn: str = None):
        """
        Inicializa el conector LDAP real.
        
        Args:
            server_url (str, optional): URL del servidor LDAP. Si no se especifica,
                                      se toma de las variables de entorno.
            base_dn (str, optional): DN base del directorio. Si no se especifica,
                                   se toma de las variables de entorno.
        """
        self.server_url = server_url or os.getenv("LDAP_SERVER", "ldap://localhost:389")
        self.base_dn = base_dn or os.getenv("LDAP_BASE_DN", "dc=meli,dc=com")
        self.admin_dn = os.getenv("LDAP_ADMIN_DN", "CN=admin,DC=meli,DC=com")
        self.admin_password = os.getenv("LDAP_ADMIN_PASSWORD", "itachi")
        self.connection = None
        self.is_connected = False
        
        console.print(Panel(f"🔗 Conector LDAP REAL inicializado para: {self.server_url}", style="blue"))
    
    def connect(self) -> bool:
        """
        Establece conexión real con el servidor LDAP.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            console.print(Panel(f"🔌 Conectando a servidor LDAP REAL: {self.server_url}", style="yellow"))
            
            # Configurar LDAP
            ldap.set_option(ldap.OPT_NETWORK_TIMEOUT, 10)
            ldap.set_option(ldap.OPT_REFERRALS, 0)
            
            # Crear conexión
            self.connection = ldap.initialize(self.server_url)
            self.connection.set_option(ldap.OPT_REFERRALS, 0)
            
            # Autenticar como admin
            self.connection.simple_bind_s(self.admin_dn, self.admin_password)
            
            self.is_connected = True
            console.print(Panel("✅ Conexión LDAP REAL establecida exitosamente", style="green"))
            
            return True
            
        except Exception as e:
            console.print(Panel(f"❌ Error conectando a LDAP REAL: {str(e)}", style="red"))
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """
        Cierra la conexión con el servidor LDAP.
        
        Returns:
            bool: True si la desconexión fue exitosa, False en caso contrario
        """
        try:
            if self.is_connected and self.connection:
                console.print(Panel("🔌 Desconectando del servidor LDAP...", style="yellow"))
                self.connection.unbind_s()
                self.is_connected = False
                console.print(Panel("✅ Desconexión LDAP exitosa", style="green"))
                return True
            return True
        except Exception as e:
            console.print(Panel(f"❌ Error desconectando de LDAP: {str(e)}", style="red"))
            return False
    
    def search(self, base_dn: str, filter_str: str, attributes: List[str] = None) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda en el directorio LDAP.
        
        Args:
            base_dn (str): DN base para la búsqueda
            filter_str (str): Filtro LDAP
            attributes (List[str], optional): Atributos a retornar
            
        Returns:
            List[Dict[str, Any]]: Lista de resultados de la búsqueda
        """
        if not self.is_connected:
            console.print(Panel("❌ No hay conexión LDAP activa", style="red"))
            return []
        
        try:
            if attributes is None:
                attributes = ['*']
            
            # Realizar búsqueda
            result = self.connection.search_s(
                base_dn,
                ldap.SCOPE_SUBTREE,
                filter_str,
                attributes
            )
            
            # Procesar resultados
            processed_results = []
            for dn, attrs in result:
                if dn:  # Ignorar entradas de control
                    processed_entry = {'dn': dn}
                    for attr, values in attrs.items():
                        if isinstance(values, list) and len(values) == 1:
                            processed_entry[attr] = values[0].decode('utf-8') if isinstance(values[0], bytes) else values[0]
                        else:
                            processed_entry[attr] = [v.decode('utf-8') if isinstance(v, bytes) else v for v in values]
                    processed_results.append(processed_entry)
            
            return processed_results
            
        except Exception as e:
            console.print(Panel(f"❌ Error en búsqueda LDAP: {str(e)}", style="red"))
            return []
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información completa de un usuario específico.
        
        Args:
            username (str): Nombre de usuario a consultar
            
        Returns:
            Optional[Dict[str, Any]]: Información del usuario o None si no se encuentra
        """
        try:
            filter_str = f"(uid={username})"
            results = self.search("ou=users,dc=meli,dc=com", filter_str)
            
            if results:
                user_info = results[0]
                return {
                    "username": user_info.get("uid", username),
                    "full_name": user_info.get("displayName", ""),
                    "email": user_info.get("mail", ""),
                    "title": user_info.get("title", ""),
                    "department": self._get_user_department(user_info),
                    "status": "active",  # Asumimos activo si existe en LDAP
                    "last_login": "N/A",  # No disponible en LDAP básico
                    "home_directory": user_info.get("homeDirectory", ""),
                    "shell": user_info.get("loginShell", ""),
                    "uid_number": user_info.get("uidNumber", ""),
                    "gid_number": user_info.get("gidNumber", "")
                }
            return None
            
        except Exception as e:
            console.print(Panel(f"❌ Error obteniendo información del usuario {username}: {str(e)}", style="red"))
            return None
    
    def get_user_groups(self, username: str) -> List[str]:
        """
        Obtiene los grupos de un usuario específico.
        
        Args:
            username (str): Nombre de usuario
            
        Returns:
            List[str]: Lista de nombres de grupos
        """
        try:
            groups = []
            
            # Buscar en todos los grupos
            group_results = self.search("ou=groups,dc=meli,dc=com", "(objectClass=groupOfNames)")
            
            for group in group_results:
                members = group.get("member", [])
                if isinstance(members, str):
                    members = [members]
                
                # Verificar si el usuario es miembro
                user_dn = f"cn={username},ou=users,dc=meli,dc=com"
                if user_dn in members:
                    groups.append(group.get("cn", ""))
            
            return groups
            
        except Exception as e:
            console.print(Panel(f"❌ Error obteniendo grupos del usuario {username}: {str(e)}", style="red"))
            return []
    
    def list_all_users(self) -> List[Dict[str, Any]]:
        """
        Lista todos los usuarios del directorio.
        
        Returns:
            List[Dict[str, Any]]: Lista de todos los usuarios
        """
        try:
            results = self.search("ou=users,dc=meli,dc=com", "(objectClass=inetOrgPerson)")
            users = []
            
            for user in results:
                user_info = {
                    "username": user.get("uid", ""),
                    "full_name": user.get("displayName", ""),
                    "email": user.get("mail", ""),
                    "title": user.get("title", ""),
                    "department": self._get_user_department(user),
                    "status": "active",
                    "last_login": "N/A"
                }
                users.append(user_info)
            
            return users
            
        except Exception as e:
            console.print(Panel(f"❌ Error listando usuarios: {str(e)}", style="red"))
            return []
    
    def list_all_groups(self) -> List[Dict[str, Any]]:
        """
        Lista todos los grupos del directorio.
        
        Returns:
            List[Dict[str, Any]]: Lista de todos los grupos
        """
        try:
            results = self.search("ou=groups,dc=meli,dc=com", "(objectClass=groupOfNames)")
            groups = []
            
            for group in results:
                group_info = {
                    "name": group.get("cn", ""),
                    "description": group.get("description", ""),
                    "members": group.get("member", []),
                    "member_count": len(group.get("member", []))
                }
                groups.append(group_info)
            
            return groups
            
        except Exception as e:
            console.print(Panel(f"❌ Error listando grupos: {str(e)}", style="red"))
            return []
    
    def _get_user_department(self, user_info: Dict[str, Any]) -> str:
        """
        Determina el departamento de un usuario basado en sus grupos.
        
        Args:
            user_info (Dict[str, Any]): Información del usuario
            
        Returns:
            str: Departamento del usuario
        """
        try:
            username = user_info.get("uid", "")
            if not username:
                return "Unknown"
            
            # Mapeo de grupos a departamentos
            group_dept_mapping = {
                "admins": "IT",
                "developers": "Development",
                "managers": "Management",
                "hr": "Human Resources",
                "finance": "Finance",
                "qa": "Quality Assurance",
                "it": "IT"
            }
            
            user_groups = self.get_user_groups(username)
            
            # Buscar el primer grupo que tenga mapeo de departamento
            for group in user_groups:
                if group in group_dept_mapping:
                    return group_dept_mapping[group]
            
            return "General"
            
        except Exception:
            return "Unknown"
    
    def get_ldap_structure(self) -> Dict[str, Any]:
        """
        Obtiene la estructura completa del directorio LDAP.
        
        Returns:
            Dict[str, Any]: Estructura del directorio
        """
        try:
            # Obtener unidades organizativas
            ou_results = self.search(self.base_dn, "(objectClass=organizationalUnit)")
            
            # Obtener usuarios y grupos
            users = self.list_all_users()
            groups = self.list_all_groups()
            
            structure = {
                "base_dn": self.base_dn,
                "organizational_units": [],
                "total_users": len(users),
                "total_groups": len(groups),
                "structure_depth": 3
            }
            
            # Procesar unidades organizativas
            for ou in ou_results:
                if "ou" in ou:
                    ou_name = ou.get("ou", "")
                    if ou_name:
                        structure["organizational_units"].append({
                            "name": ou_name,
                            "dn": ou.get("dn", ""),
                            "description": f"Unidad organizativa: {ou_name}",
                            "entry_count": len(users) if ou_name == "users" else len(groups) if ou_name == "groups" else 0
                        })
            
            return structure
            
        except Exception as e:
            console.print(Panel(f"❌ Error obteniendo estructura LDAP: {str(e)}", style="red"))
            return {}
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect() 