"""
Herramientas base del sistema consolidadas.
"""

# Herramientas obligatorias (requeridas por el challenge)
from .tools import (
    get_current_user_info,
    get_user_groups,
    reset_system
)

# Herramientas adicionales de seguridad ofensiva (datos reales del LDAP)
from .tools import (
    list_all_users,
    search_users_by_department,
    analyze_ldap_structure
)

# Conector LDAP para integración real
from .ldap_connector import LDAPConnector

__all__ = [
    # Herramientas obligatorias
    'get_current_user_info',
    'get_user_groups',
    'reset_system',

    # Herramientas de seguridad ofensiva
    'list_all_users',
    'search_users_by_department',
    'analyze_ldap_structure',

    # Conector LDAP
    'LDAPConnector'
] 