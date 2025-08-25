"""
Tests unitarios para el agente coordinador.
"""

import pytest
from unittest.mock import Mock, patch
from agentesai.agent.coordinador import AgenteCoordinador


class TestAgenteCoordinador:
    """Tests unitarios para el agente coordinador."""
    
    @pytest.fixture
    def coordinador(self):
        """Instancia del agente coordinador para testing."""
        return AgenteCoordinador()
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_coordinador_initialization(self, coordinador):
        """Test: inicialización del agente coordinador."""
        assert coordinador.herramientas_disponibles is not None
        assert coordinador.historial_consultas is not None
        assert len(coordinador.herramientas_disponibles) >= 0
        assert len(coordinador.historial_consultas) == 0
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_analizar_consulta_herramienta_existente(self, coordinador):
        """Test: análisis de consulta que puede ser respondida directamente."""
        consulta = "¿quién soy?"
        
        resultado = coordinador.analizar_consulta(consulta)
        
        assert resultado["accion"] == "ejecutar"
        assert resultado["agente"] == "ejecutor"
        assert resultado["herramienta"] == "get_current_user_info"
        assert resultado["consulta"] == consulta
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_analizar_consulta_necesita_generar(self, coordinador):
        """Test: análisis de consulta que necesita generación de herramienta."""
        consulta = "¿cuál es el nombre de todos los grupos?"
        
        resultado = coordinador.analizar_consulta(consulta)
        
        assert resultado["accion"] == "generar"
        assert resultado["agente"] == "generador"
        assert resultado["consulta"] == consulta
        assert "tipo_herramienta" in resultado
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_analizar_consulta_case_insensitive(self, coordinador):
        """Test: análisis de consulta insensible a mayúsculas/minúsculas."""
        consultas = ["¿QUIÉN SOY?", "quien soy", "WHO AM I", "Who Am I"]
        
        for consulta in consultas:
            resultado = coordinador.analizar_consulta(consulta)
            assert resultado["accion"] == "ejecutar"
            assert resultado["herramienta"] == "get_current_user_info"
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_identificar_herramienta_quien_soy(self, coordinador):
        """Test: identificación de herramienta para '¿quién soy?'."""
        herramienta = coordinador._identificar_herramienta("¿quién soy?")
        assert herramienta == "get_current_user_info"
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_identificar_herramienta_grupos(self, coordinador):
        """Test: identificación de herramienta para consultas de grupos."""
        herramienta = coordinador._identificar_herramienta("qué grupos tengo")
        assert herramienta == "get_user_groups"
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_identificar_herramienta_reset(self, coordinador):
        """Test: identificación de herramienta para reset."""
        herramienta = coordinador._identificar_herramienta("reset del sistema")
        assert herramienta == "reset_system"
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_identificar_herramienta_listar_usuarios(self, coordinador):
        """Test: identificación de herramienta para listar usuarios."""
        herramienta = coordinador._identificar_herramienta("listar usuarios")
        assert herramienta == "list_all_users"
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_identificar_herramienta_buscar_departamento(self, coordinador):
        """Test: identificación de herramienta para buscar por departamento."""
        herramienta = coordinador._identificar_herramienta("usuarios por departamento")
        assert herramienta == "search_users_by_department"
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_identificar_herramienta_estructura_ldap(self, coordinador):
        """Test: identificación de herramienta para estructura LDAP."""
        herramienta = coordinador._identificar_herramienta("estructura ldap")
        assert herramienta == "analyze_ldap_structure"
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_identificar_herramienta_no_encontrada(self, coordinador):
        """Test: identificación de herramienta no encontrada."""
        herramienta = coordinador._identificar_herramienta("consulta desconocida")
        assert herramienta is None
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_determinar_tipo_herramienta_grupos(self, coordinador):
        """Test: determinación de tipo de herramienta para grupos."""
        tipo = coordinador._determinar_tipo_herramienta("¿cuántos grupos hay?")
        assert tipo == "ldap_query"
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_determinar_tipo_herramienta_usuarios(self, coordinador):
        """Test: determinación de tipo de herramienta para usuarios."""
        tipo = coordinador._determinar_tipo_herramienta("¿cuántos usuarios hay?")
        assert tipo == "ldap_query"
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_determinar_tipo_herramienta_departamento(self, coordinador):
        """Test: determinación de tipo de herramienta para departamentos."""
        tipo = coordinador._determinar_tipo_herramienta("usuarios del departamento IT")
        assert tipo == "ldap_query"
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_determinar_tipo_herramienta_generico(self, coordinador):
        """Test: determinación de tipo de herramienta genérico."""
        tipo = coordinador._determinar_tipo_herramienta("consulta general")
        assert tipo == "generic_query"
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_registrar_herramienta(self, coordinador):
        """Test: registro de nueva herramienta."""
        herramienta_nueva = "nueva_herramienta"
        coordinador.registrar_herramienta(herramienta_nueva)
        
        assert herramienta_nueva in coordinador.herramientas_disponibles
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_registrar_consulta(self, coordinador):
        """Test: registro de consulta en historial."""
        consulta = "¿quién soy?"
        resultado = "Usuario: test_user"
        
        coordinador.registrar_consulta(consulta, resultado)
        
        assert len(coordinador.historial_consultas) == 1
        assert coordinador.historial_consultas[0]["consulta"] == consulta
        assert coordinador.historial_consultas[0]["resultado"] == resultado
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_obtener_estadisticas(self, coordinador):
        """Test: obtención de estadísticas del coordinador."""
        # Registrar algunas consultas
        coordinador.registrar_consulta("consulta1", "resultado1")
        coordinador.registrar_consulta("consulta2", "resultado2")
        
        estadisticas = coordinador.obtener_estadisticas()
        
        assert estadisticas["consultas_procesadas"] == 2
        assert estadisticas["herramientas_disponibles"] >= 0
    
    @pytest.mark.unit
    @pytest.mark.agent
    def test_multiple_registrations(self, coordinador):
        """Test: múltiples registros de herramientas y consultas."""
        # Registrar múltiples herramientas
        herramientas = ["tool1", "tool2", "tool3"]
        for tool in herramientas:
            coordinador.registrar_herramienta(tool)
        
        # Registrar múltiples consultas
        consultas = ["consulta1", "consulta2", "consulta3"]
        for i, consulta in enumerate(consultas):
            coordinador.registrar_consulta(consulta, f"resultado{i}")
        
        # Verificar que todo se registró correctamente
        assert len(coordinador.herramientas_disponibles) >= len(herramientas)
        assert len(coordinador.historial_consultas) == len(consultas)
        
        # Verificar estadísticas
        estadisticas = coordinador.obtener_estadisticas()
        assert estadisticas["consultas_procesadas"] == len(consultas) 