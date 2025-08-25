"""
Tests unitarios para las herramientas base consolidadas del sistema.
"""

import pytest
from unittest.mock import Mock, patch
from agentesai.tools_base.tools import (
    get_current_user_info,
    get_user_groups,
    reset_system,
    list_all_users,
    search_users_by_department,
    analyze_ldap_structure
)


class TestToolsBase:
    """Tests unitarios para las herramientas base consolidadas."""
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_get_current_user_info_structure(self):
        """Test: get_current_user_info retorna estructura correcta."""
        resultado = get_current_user_info()
        
        # Verificar campos requeridos
        required_fields = ["username", "home_dir", "shell", "working_dir", "python_version"]
        for field in required_fields:
            assert field in resultado, f"Campo '{field}' debe estar presente"
        
        # Verificar tipos de datos
        assert isinstance(resultado["username"], str)
        assert isinstance(resultado["home_dir"], str)
        assert isinstance(resultado["working_dir"], str)
        assert isinstance(resultado["python_version"], str)
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_get_current_user_info_username_not_empty(self):
        """Test: username no debe estar vacío."""
        resultado = get_current_user_info()
        assert len(resultado["username"]) > 0, "Username no debe estar vacío"
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_get_current_user_info_home_dir_exists(self):
        """Test: home_dir debe ser un directorio válido."""
        import os
        resultado = get_current_user_info()
        assert os.path.exists(resultado["home_dir"]), "Home directory debe existir"
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_get_user_groups_default_user(self):
        """Test: get_user_groups sin parámetros usa usuario actual."""
        resultado = get_user_groups()
        
        assert "username" in resultado
        assert "groups" in resultado
        assert "total_groups" in resultado
        assert isinstance(resultado["groups"], list)
        assert resultado["total_groups"] >= 0
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_get_user_groups_specific_user(self):
        """Test: get_user_groups con usuario específico."""
        resultado = get_user_groups("admin")
        
        assert resultado["username"] == "admin"
        assert "groups" in resultado
        assert "total_groups" in resultado
        assert isinstance(resultado["groups"], list)
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_get_user_groups_structure(self):
        """Test: get_user_groups retorna estructura correcta."""
        resultado = get_user_groups("admin")
        
        required_fields = ["username", "groups", "total_groups", "source"]
        for field in required_fields:
            assert field in resultado, f"Campo '{field}' debe estar presente"
        
        # Verificar lógica de grupos
        assert resultado["total_groups"] == len(resultado["groups"])
        assert resultado["source"] == "LDAP_REAL"
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_reset_system_structure(self):
        """Test: reset_system retorna estructura correcta."""
        resultado = reset_system()
        
        assert "mensaje" in resultado
        assert "Sistema reseteado" in resultado["mensaje"]
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_list_all_users_structure(self):
        """Test: list_all_users retorna estructura correcta."""
        resultado = list_all_users()
        
        required_fields = ["total_users", "users", "departments", "source"]
        for field in required_fields:
            assert field in resultado, f"Campo '{field}' debe estar presente"
        
        assert isinstance(resultado["total_users"], int)
        assert isinstance(resultado["users"], list)
        assert isinstance(resultado["departments"], list)
        assert resultado["source"] == "LDAP_REAL"
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_list_all_users_has_users(self):
        """Test: list_all_users debe tener usuarios."""
        resultado = list_all_users()
        
        assert resultado["total_users"] > 0, "Debe haber al menos un usuario"
        assert len(resultado["users"]) > 0, "Lista de usuarios no debe estar vacía"
        
        # Verificar estructura de cada usuario
        for user in resultado["users"]:
            user_fields = ["username", "full_name", "email", "title", "department", "status"]
            for field in user_fields:
                assert field in user, f"Usuario debe tener campo '{field}'"
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_search_users_by_department_structure(self):
        """Test: search_users_by_department retorna estructura correcta."""
        resultado = search_users_by_department("Development")
        
        required_fields = ["department", "total_users", "users", "source"]
        for field in required_fields:
            assert field in resultado, f"Campo '{field}' debe estar presente"
        
        assert resultado["department"] == "Development"
        assert isinstance(resultado["total_users"], int)
        assert isinstance(resultado["users"], list)
        assert resultado["source"] == "LDAP_REAL"
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_search_users_by_department_invalid(self):
        """Test: search_users_by_department con departamento inexistente."""
        resultado = search_users_by_department("DepartamentoInexistente")
        
        assert resultado["department"] == "DepartamentoInexistente"
        assert resultado["total_users"] == 0
        assert len(resultado["users"]) == 0
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_analyze_ldap_structure_structure(self):
        """Test: analyze_ldap_structure retorna estructura correcta."""
        resultado = analyze_ldap_structure()
        
        required_fields = ["base_dn", "organizational_units", "total_users", "total_groups", "structure_depth"]
        for field in required_fields:
            assert field in resultado, f"Campo '{field}' debe estar presente"
        
        assert resultado["base_dn"] == "dc=meli,dc=com"
        assert resultado["structure_depth"] == 3
        assert len(resultado["organizational_units"]) > 0
        assert resultado["total_users"] > 0
        assert resultado["total_groups"] > 0
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_analyze_ldap_structure_ou_structure(self):
        """Test: estructura de unidades organizativas."""
        resultado = analyze_ldap_structure()
        
        for ou in resultado["organizational_units"]:
            required_ou_fields = ["dn", "name", "description", "entry_count"]
            for field in required_ou_fields:
                assert field in ou, f"Campo '{field}' debe estar presente en OU"
            
            assert isinstance(ou["entry_count"], int)
            assert ou["entry_count"] >= 0
    
    @pytest.mark.unit
    @pytest.mark.tools
    def test_analyze_ldap_structure_data_consistency(self):
        """Test: consistencia de datos en la estructura LDAP."""
        resultado = analyze_ldap_structure()
        
        # Verificar que el total de usuarios coincide con la suma de entradas en OUs
        total_entries = sum(ou["entry_count"] for ou in resultado["organizational_units"])
        assert total_entries >= resultado["total_users"], "Total de entradas debe ser >= total de usuarios"
        
        # Verificar que la base DN es correcta
        assert resultado["base_dn"] == "dc=meli,dc=com"
        
        # Verificar que hay al menos 3 unidades organizativas
        assert len(resultado["organizational_units"]) >= 3, "Debe haber al menos 3 OUs"


class TestToolsIntegration:
    """Tests de integración entre herramientas."""
    
    @pytest.mark.integration
    @pytest.mark.tools
    def test_user_info_and_groups_consistency(self):
        """Test: consistencia entre información de usuario y grupos."""
        user_info = get_current_user_info()
        user_groups = get_user_groups()
        
        # Verificar que ambos se refieren al mismo usuario
        assert user_info["username"] == user_groups["username"]
    
    @pytest.mark.integration
    @pytest.mark.tools
    def test_all_users_and_departments_consistency(self):
        """Test: consistencia entre listado de usuarios y departamentos."""
        all_users = list_all_users()
        
        # Verificar que todos los departamentos mencionados existen
        for user in all_users["users"]:
            dept_result = search_users_by_department(user["department"])
            assert dept_result["total_users"] > 0, f"Departamento {user['department']} debe tener usuarios"
    
    @pytest.mark.integration
    @pytest.mark.tools
    def test_ldap_structure_and_users_consistency(self):
        """Test: consistencia entre estructura LDAP y usuarios."""
        ldap_structure = analyze_ldap_structure()
        all_users = list_all_users()
        
        # Verificar que el total de usuarios coincide
        assert ldap_structure["total_users"] == all_users["total_users"], "Total de usuarios debe coincidir"
        
        # Verificar que todos los departamentos están en la estructura
        for dept in all_users["departments"]:
            # Buscar si el departamento está en alguna OU o es un departamento válido
            dept_found = False
            for ou in ldap_structure["organizational_units"]:
                if dept.lower() in ou["name"].lower() or dept.lower() in ou["description"].lower():
                    dept_found = True
                    break
            
            # Algunos departamentos pueden no estar mapeados exactamente
            if not dept_found:
                # Verificar si es un departamento estándar
                standard_depts = ["IT", "Development", "Management", "Finance", "Quality Assurance", "General"]
                if dept in standard_depts:
                    dept_found = True
            
            assert dept_found, f"Departamento {dept} debe estar en estructura LDAP o ser estándar" 