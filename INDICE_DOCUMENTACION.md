# 📚 Índice de Documentación - Sistema de Agentes AI

## 🚀 Documentación Principal

### **1. [README_AGENTES.md](README_AGENTES.md) - Documentación Completa**
- **Descripción**: Documentación principal del sistema con explicación completa de la arquitectura
- **Contenido**:
  - Descripción general del sistema
  - Arquitectura y componentes principales
  - Diagrama de flujo del sistema
  - Flujo detallado de procesamiento
  - Herramientas base disponibles
  - Configuración y uso
  - Características clave
  - Estructura de archivos
  - Casos de uso
  - Mantenimiento del sistema

### **2. [DIAGRAMA_FLUJO.md](DIAGRAMA_FLUJO.md) - Diagramas Visuales**
- **Descripción**: Diagramas detallados y flujos visuales del sistema
- **Contenido**:
  - Vista general del sistema
  - Flujo de procesamiento detallado
  - Puntos de decisión clave
  - Herramientas base disponibles
  - Flujo de datos y persistencia

## 🏗️ Arquitectura del Sistema

### **Componentes Principales**

| Agente | Archivo | Responsabilidad | Estado |
|--------|---------|-----------------|---------|
| 🔄 **SistemaAgentes** | `agentesai/agent/sistema.py` | Orquestador principal | ✅ Implementado |
| 🧠 **AgenteCoordinador** | `agentesai/agent/coordinador.py` | Cerebro del sistema | ✅ Implementado |
| ⚡ **AgenteEjecutor** | `agentesai/agent/ejecutor.py` | Motor de ejecución | ✅ Implementado |
| 🤖 **AgenteGenerador** | `agentesai/agent/generador.py` | Creador de herramientas | ✅ Implementado |
| 📚 **RegistryTools** | `agentesai/agent/registry.py` | Sistema de registro | ✅ Implementado |

## 📁 Estructura de Archivos

```
AgentesAI/
├── 📚 README_AGENTES.md           # Documentación principal
├── 🔄 DIAGRAMA_FLUJO.md           # Diagramas visuales
├── 📋 INDICE_DOCUMENTACION.md     # Este archivo índice
├── agentesai/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── sistema.py             # 🔄 SistemaAgentes
│   │   ├── coordinador.py         # 🧠 AgenteCoordinador
│   │   ├── ejecutor.py            # ⚡ AgenteEjecutor
│   │   ├── generador.py           # 🤖 AgenteGenerador
│   │   └── registry.py            # 📚 RegistryTools
│   ├── tools_base/                # Herramientas base del sistema
│   ├── tools_generated/           # Herramientas generadas dinámicamente
│   └── cli.py                     # Interfaz de línea de comandos
├── tests/                         # Pruebas unitarias e integración
├── requirements.txt               # Dependencias del proyecto
└── pyproject.toml                # Configuración de Poetry
```

## 🔄 Flujo de Trabajo del Sistema

### **Flujo Principal**
1. **Usuario envía consulta** → `SistemaAgentes`
2. **Análisis de consulta** → `AgenteCoordinador`
3. **Decisión de ruteo** → Herramienta existente o nueva
4. **Ejecución o generación** → `AgenteEjecutor` o `AgenteGenerador`
5. **Registro y persistencia** → `RegistryTools`
6. **Resultado al usuario** → Respuesta procesada

### **Tipos de Flujo**
- **🔄 Flujo Simple**: Consulta → Herramienta existente → Resultado
- **🤖 Flujo Complejo**: Consulta → Generación IA → Nueva herramienta → Ejecución → Resultado

## 🛠️ Herramientas Disponibles

### **Herramientas Base (Obligatorias)**
- `get_current_user_info` - Información del usuario actual
- `get_user_groups` - Grupos del usuario
- `reset_system` - Reseteo del sistema

### **Herramientas Adicionales (Seguridad Ofensiva)**
- `list_all_users` - Lista todos los usuarios del LDAP
- `search_users_by_department` - Búsqueda de usuarios por departamento
- `analyze_ldap_structure` - Análisis de la estructura LDAP

## 🎯 Casos de Uso Documentados

### **1. Consulta Simple**
- **Entrada**: "¿quién soy?"
- **Flujo**: Herramienta existente
- **Resultado**: Información del usuario actual

### **2. Consulta Compleja**
- **Entrada**: "¿cuáles son todos los usuarios del departamento de IT?"
- **Flujo**: Generación de nueva herramienta
- **Resultado**: Herramienta LDAP personalizada

### **3. Reseteo del Sistema**
- **Entrada**: "reset"
- **Flujo**: Limpieza y restauración
- **Resultado**: Sistema en estado inicial

## 🔧 Configuración y Uso

### **Requisitos del Sistema**
- Python 3.8+
- API Key de Gemini (configurada en variables de entorno)
- Conexión LDAP configurada

### **Uso Básico**
```python
from agentesai.agent.sistema import SistemaAgentes

# Crear sistema
sistema = SistemaAgentes()

# Procesar consulta
resultado = sistema.procesar_consulta("¿quién soy?")

# Modo interactivo
sistema.modo_interactivo()
```

### **Comandos de Mantenimiento**
```python
# Ver estado completo
sistema.mostrar_estado_completo()

# Reset del sistema
sistema.reset_sistema()

# Estadísticas
stats = sistema.obtener_estadisticas()
```

## 📊 Características del Sistema

### **🔄 Auto-expansión**
- Genera nuevas herramientas automáticamente
- Aprende de consultas previas
- Mantiene inventario de funcionalidades

### **💾 Persistencia**
- Guarda herramientas generadas
- Historial completo de operaciones
- Metadatos de auditoría

### **🛡️ Robustez**
- Manejo de errores gracioso
- Fallbacks automáticos
- Templates predefinidos

### **📈 Escalabilidad**
- Arquitectura modular
- Fácil extensión
- Nuevos tipos de agentes

## 🧪 Pruebas y Validación

### **Pruebas Unitarias**
- `tests/unit/test_coordinador.py` - Pruebas del coordinador
- `tests/unit/test_ejecutor.py` - Pruebas del ejecutor
- `tests/unit/test_generador.py` - Pruebas del generador
- `tests/unit/test_sistema_agentes.py` - Pruebas del sistema principal

### **Pruebas de Integración**
- `tests/integration/` - Pruebas de flujo completo
- Validación de interacciones entre agentes
- Pruebas de persistencia de datos

## 📝 Notas de Desarrollo

### **Estado Actual**
- ✅ Sistema base implementado
- ✅ Agentes principales funcionales
- ✅ Herramientas LDAP integradas
- ✅ Sistema de registro persistente
- ✅ Generación de herramientas con IA

### **Próximos Pasos**
- 🔄 Mejoras en análisis semántico
- 🔄 Nuevos tipos de herramientas
- 🔄 Interfaz web opcional
- 🔄 Métricas avanzadas

## 🔗 Enlaces Útiles

### **Documentación**
- [README Principal](README_AGENTES.md) - Documentación completa
- [Diagramas de Flujo](DIAGRAMA_FLUJO.md) - Visualizaciones detalladas
- [Código Fuente](../agentesai/) - Implementación del sistema

### **Configuración**
- [requirements.txt](requirements.txt) - Dependencias del proyecto
- [pyproject.toml](pyproject.toml) - Configuración de Poetry
- [Makefile](Makefile) - Comandos de construcción

### **Pruebas**
- [pytest.ini](pytest.ini) - Configuración de pruebas
- [tests/](tests/) - Suite de pruebas completa

---

## 📞 Soporte y Contacto

Para preguntas sobre la implementación o arquitectura del sistema, consulta la documentación principal o revisa el código fuente en los archivos correspondientes.

---

*Índice de documentación para el Sistema de Agentes AI - Challenge OffSec* 