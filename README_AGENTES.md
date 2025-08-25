# 🚀 Sistema de Agentes AI - Documentación de Arquitectura

## 📋 Descripción General

El Sistema de Agentes AI es una arquitectura modular e inteligente que coordina múltiples agentes especializados para procesar consultas de usuarios de manera autoadaptativa. El sistema puede generar nuevas herramientas dinámicamente usando IA y mantener un registro completo de todas las operaciones.

## 🏗️ Arquitectura del Sistema

### **Componentes Principales**

#### 1. **🔄 SistemaAgentes** - `agentesai/agent/sistema.py`
- **Responsabilidad**: Orquestador principal del sistema
- **Funciones**:
  - Recibe consultas del usuario
  - Coordina la interacción entre todos los agentes
  - Maneja el estado global del sistema
  - Proporciona interfaz interactiva
  - Mantiene contadores de consultas procesadas

#### 2. **🧠 AgenteCoordinador** - `agentesai/agent/coordinador.py`
- **Responsabilidad**: Cerebro del sistema que toma decisiones inteligentes
- **Funciones**:
  - Analiza consultas usando patrones de texto
  - Decide si usar herramientas existentes o generar nuevas
  - Mantiene registro de herramientas disponibles
  - Rutea consultas al agente apropiado
  - Implementa reconocimiento de patrones para consultas conocidas

#### 3. **⚡ AgenteEjecutor** - `agentesai/agent/ejecutor.py`
- **Responsabilidad**: Motor de ejecución de herramientas
- **Funciones**:
  - Ejecuta herramientas base predefinidas
  - Integra herramientas generadas dinámicamente
  - Maneja errores de ejecución
  - Proporciona estadísticas de herramientas
  - Gestiona ciclo de vida de herramientas generadas

#### 4. **🤖 AgenteGenerador** - `agentesai/agent/generador.py`
- **Responsabilidad**: Creador de nuevas herramientas usando IA
- **Funciones**:
  - Crea código Python funcional usando Gemini API
  - Genera funciones dinámicas ejecutables
  - Maneja fallbacks si la IA falla
  - Crea herramientas específicas para consultas LDAP
  - Implementa templates predefinidos como respaldo

#### 5. **📚 RegistryTools** - `agentesai/agent/registry.py`
- **Responsabilidad**: Sistema de registro y gestión de herramientas
- **Funciones**:
  - Registra herramientas generadas
  - Mantiene historial de uso y metadatos
  - Persiste información en disco (JSON)
  - Proporciona estadísticas del sistema
  - Maneja auditoría completa de operaciones

## 🔄 Diagrama de Flujo del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    🚀 SISTEMA DE AGENTES AI                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    🔄 SistemaAgentes                           │
│                    (sistema.py)                                │
│  • Recibe consultas del usuario                               │
│  • Coordina flujo de trabajo                                  │
│  • Maneja estado global                                       │
│  • Interfaz interactiva                                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    🧠 AgenteCoordinador                        │
│                   (coordinador.py)                             │
│  • Analiza consultas                                          │
│  • Toma decisiones de ruteo                                   │
│  • Patrones de reconocimiento                                 │
│  • Ruteo inteligente                                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │    DECISIÓN         │
                    │                     │
                    │ ¿Herramienta        │
                    │ existente?          │
                    └─────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
        ┌─────────────────────┐    ┌─────────────────────┐
        │ ⚡ AgenteEjecutor   │    │ 🤖 AgenteGenerador │
        │   (ejecutor.py)     │    │  (generador.py)     │
        │                     │    │                     │
        │ • Ejecuta tools     │    │ • Genera código IA  │
        │ • Tools base        │    │ • Crea funciones    │
        │ • Tools generadas   │    │ • Fallbacks         │
        │ • Manejo de errores │    │ • Templates LDAP    │
        └─────────────────────┘    └─────────────────────┘
                    │                       │
                    └───────────┬───────────┘
                                │
                                ▼
        ┌─────────────────────────────────────────────────────────┐
        │                    📚 RegistryTools                     │
        │                  (registry.py)                         │
        │  • Registra herramientas                               │
        │  • Mantiene metadatos                                  │
        │  • Historial de uso                                    │
        │  • Persistencia en disco                               │
        │  • Auditoría completa                                  │
        └─────────────────────────────────────────────────────────┘
```

## 🔄 Flujo Detallado de Procesamiento

### **1. Recepción de Consulta**
```
Usuario → SistemaAgentes.procesar_consulta(consulta)
```

### **2. Análisis y Decisión**
```
SistemaAgentes → AgenteCoordinador.analizar_consulta(consulta)
                ↓
        [Análisis de patrones de texto]
                ↓
        [Decisión de ruteo]
```

### **3. Ejecución o Generación**

#### **Opción A: Herramienta Existente**
```
AgenteCoordinador → AgenteEjecutor.ejecutar_herramienta(nombre)
                ↓
        [Ejecución de herramienta base o generada]
                ↓
        [Resultado retornado al usuario]
```

#### **Opción B: Nueva Herramienta**
```
AgenteCoordinador → AgenteGenerador.generar_herramienta(consulta, tipo)
                ↓
        [Generación de código con IA Gemini]
                ↓
        [Creación de función dinámica]
                ↓
        [Registro en RegistryTools]
                ↓
        [Agregado a AgenteEjecutor]
                ↓
        [Ejecución de nueva herramienta]
                ↓
        [Resultado retornado al usuario]
```

### **4. Registro y Persistencia**
```
RegistryTools.registrar_herramienta(nombre, metadata)
                ↓
        [Guardado en disco automático]
                ↓
        [Actualización de estadísticas]
```

## 🛠️ Herramientas Base Disponibles

### **Herramientas Obligatorias (Challenge)**
- `get_current_user_info` - Información del usuario actual
- `get_user_groups` - Grupos del usuario
- `reset_system` - Reseteo del sistema

### **Herramientas Adicionales de Seguridad Ofensiva**
- `list_all_users` - Lista todos los usuarios del LDAP
- `search_users_by_department` - Búsqueda de usuarios por departamento
- `analyze_ldap_structure` - Análisis de la estructura LDAP

## 🔧 Configuración y Uso

### **Requisitos**
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

### **Estadísticas del Sistema**
```python
# Ver estado completo
sistema.mostrar_estado_completo()

# Obtener estadísticas
stats = sistema.obtener_estadisticas()
```

## 🎯 Características Clave

- **🔄 Auto-expansión**: Genera nuevas herramientas automáticamente
- **💾 Persistencia**: Guarda herramientas generadas para reutilización
- **🛡️ Fallbacks**: Templates predefinidos si la IA falla
- **📊 Auditoría**: Registro completo de consultas y herramientas
- **🧩 Modularidad**: Arquitectura limpia y extensible
- **📈 Escalabilidad**: Fácil agregar nuevos tipos de agentes

## 🔍 Estructura de Archivos

```
agentesai/
├── agent/
│   ├── __init__.py
│   ├── sistema.py          # 🔄 SistemaAgentes
│   ├── coordinador.py      # 🧠 AgenteCoordinador
│   ├── ejecutor.py         # ⚡ AgenteEjecutor
│   ├── generador.py        # 🤖 AgenteGenerador
│   └── registry.py         # 📚 RegistryTools
├── tools_base/             # Herramientas base del sistema
├── tools_generated/        # Herramientas generadas dinámicamente
└── cli.py                  # Interfaz de línea de comandos
```

## 🚀 Casos de Uso

### **Consulta Simple (Herramienta Existente)**
```
Usuario: "¿quién soy?"
Sistema: Usa get_current_user_info → Resultado inmediato
```

### **Consulta Compleja (Nueva Herramienta)**
```
Usuario: "¿cuáles son todos los usuarios del departamento de IT?"
Sistema: Genera nueva herramienta LDAP → Ejecuta → Registra
```

### **Reseteo del Sistema**
```
Usuario: "reset"
Sistema: Limpia herramientas generadas → Restaura estado inicial
```

## 🔧 Mantenimiento

### **Reset del Sistema**
```python
sistema.reset_sistema()
```

### **Exportar Registry**
```python
sistema.registry.exportar_registry("backup.json")
```

### **Ver Estado**
```python
sistema.mostrar_estado_completo()
```

---

## 📝 Notas de Desarrollo

- El sistema está diseñado para ser robusto y manejar errores graciosamente
- Todas las excepciones son capturadas y retornadas como parte del resultado
- El sistema mantiene estado persistente entre sesiones
- Las herramientas generadas se pueden reutilizar en futuras consultas
- El sistema es extensible para nuevos tipos de agentes y funcionalidades

---

*Documentación generada para el Sistema de Agentes AI - Challenge OffSec* 