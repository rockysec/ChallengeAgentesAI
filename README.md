# 🤖 Sistema de Agentes AI con Auto-Expansión y LDAP

Sistema multi-agente inteligente que puede generar herramientas dinámicamente usando Gemini AI y conectarse a servidores LDAP reales para obtener datos en tiempo real.

## 📚 **Documentación del Sistema**

Para entender completamente la arquitectura y funcionamiento del sistema, consulta la documentación detallada:

- **[📋 Documentación Completa](README_AGENTES.md)** - Explicación completa de la arquitectura y componentes
- **[🔄 Diagramas de Flujo](DIAGRAMA_FLUJO.md)** - Visualizaciones detalladas del sistema
- **[📚 Índice de Documentación](INDICE_DOCUMENTACION.md)** - Navegación organizada de toda la documentación

## 🏗️ **Arquitectura del Sistema**

### **Componentes Principales**

El sistema está compuesto por 5 agentes especializados que trabajan en conjunto:

| Agente | Responsabilidad | Archivo | Estado |
|--------|-----------------|---------|---------|
| 🔄 **SistemaAgentes** | Orquestador principal | `agentesai/agent/sistema.py` | ✅ Implementado |
| 🧠 **AgenteCoordinador** | Cerebro del sistema | `agentesai/agent/coordinador.py` | ✅ Implementado |
| ⚡ **AgenteEjecutor** | Motor de ejecución | `agentesai/agent/ejecutor.py` | ✅ Implementado |
| 🤖 **AgenteGenerador** | Creador de herramientas | `agentesai/agent/generador.py` | ✅ Implementado |
| 🔴 **AgenteOfensivo** | Análisis de seguridad ofensiva | `agentesai/agent/ofensivo.py` | ✅ Implementado |
| 📚 **RegistryTools** | Sistema de registro | `agentesai/agent/registry.py` | ✅ Implementado |

### **Flujo de Trabajo del Sistema**

```
Usuario → SistemaAgentes → AgenteCoordinador → [Decisión]
                                    ↓
                            [Herramienta Existente] → AgenteEjecutor → Resultado
                                    ↓
                            [Nueva Herramienta] → AgenteGenerador → AgenteEjecutor → Resultado
                                    ↓
                            RegistryTools ← Registro y Metadatos
```

### **Características Clave**

- **🔄 Auto-expansión**: Genera nuevas herramientas automáticamente
- **💾 Persistencia**: Guarda herramientas generadas para reutilización
- **🛡️ Fallbacks**: Templates predefinidos si la IA falla
- **📊 Auditoría**: Registro completo de consultas y herramientas
- **🧩 Modularidad**: Arquitectura limpia y extensible
- **📈 Escalabilidad**: Fácil agregar nuevos tipos de agentes

## 🛠️ **Herramientas Disponibles**

### **Herramientas LDAP Base**
- `get_current_user_info` - Información del usuario actual
- `get_user_groups` - Grupos del usuario
- `reset_system` - Reseteo del sistema

### **Herramientas LDAP Adicionales**
- `list_all_users` - Lista todos los usuarios del LDAP
- `search_users_by_department` - Búsqueda de usuarios por departamento
- `analyze_ldap_structure` - Análisis de la estructura LDAP

### **🔴 Herramientas Ofensivas (Análisis de Seguridad)**
- `tool_rootdse_info` - Análisis RootDSE para namingContexts, extensiones y controles soportados
- `tool_anonymous_enum` - Enumeración anónima para usuarios, grupos y atributos sensibles
- `tool_starttls_test` - Test de seguridad STARTTLS, detecta fallos en handshake y downgrades TLS
- `tool_simple_vs_sasl_bind` - Compara resultados de ldapwhoami con y sin -x para detectar fallbacks inseguros
- `tool_acl_diff` - Compara lo que ve un bind anónimo vs un bind autenticado admin para detectar diferencias en ACLs
- `tool_self_password_change` - Intenta cambiar userPassword con un usuario low-priv para validar regla "by self write"
- `tool_ldap_nmap_nse` - Ejecuta nmap -p389 --script ldap-rootdse,ldap-search para fingerprint adicional (acepta target desde CLI)

## 🚀 **Instalación y Configuración Paso a Paso**

### 📋 **Requisitos Previos**

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.8+** (recomendado 3.11+)
- **Git** para clonar el repositorio
- **API Key de Gemini** (Google AI Studio)
- **Servidor OpenLDAP** (opcional, para funcionalidad completa)

### 🔧 **Paso 1: Clonar el Repositorio**

```bash
# Clonar el repositorio
git clone https://github.com/rockysec/ChallengeAgentesAI.git

# Entrar al directorio del proyecto
cd ChallengeAgentesAI
```

### 🐍 **Paso 2: Instalar Python y Poetry**

#### **En macOS (usando Homebrew):**
```bash
# Instalar Python si no lo tienes
brew install python@3.11

# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Agregar Poetry al PATH (agregar a ~/.zshrc o ~/.bash_profile)
export PATH="/Users/$USER/.local/bin:$PATH"
```

#### **En Ubuntu/Debian:**
```bash
# Instalar Python y pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Agregar Poetry al PATH
export PATH="/home/$USER/.local/bin:$PATH"
```

#### **En Windows:**
```bash
# Instalar Python desde python.org
# Instalar Poetry usando PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Agregar Poetry al PATH del sistema
```

### 🔑 **Paso 3: Configurar Variables de Entorno**

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar el archivo .env con tus credenciales
nano .env  # o usar tu editor preferido
```

**Contenido del archivo `.env`:**
```bash
# Gemini API Configuration
GEMINI_API_KEY=tu_api_key_aqui

# LDAP Configuration (opcional, para funcionalidad completa)
LDAP_SERVER=ldap://localhost:389
LDAP_BASE_DN=dc=meli,dc=com
LDAP_ADMIN_DN=cn=admin,dc=meli,dc=com
LDAP_ADMIN_PASSWORD=tu_password_ldap

# Application Configuration
LOG_LEVEL=INFO
DEBUG=false
```

**⚠️ IMPORTANTE:** Obtén tu API key de Gemini en [Google AI Studio](https://makersuite.google.com/app/apikey)

### 📦 **Paso 4: Instalar Dependencias**

#### **Opción A: Usando Poetry (Recomendado)**
```bash
# Instalar dependencias usando Poetry
poetry install
```

#### **Opción B: Usando pip (Alternativa)**
```bash
# Instalar dependencias principales
pip install -r requirements.txt

# O instalar todas las dependencias (incluyendo desarrollo)
pip install -r requirements-dev.txt
```

### 🚀 **Paso 5: Verificar la Instalación**

```bash
# Verificar que Python puede importar el módulo
poetry run python -c "from agentesai.agent.sistema import SistemaAgentes; print('✅ Instalación exitosa!')"

# Ejecutar tests para verificar funcionalidad
poetry run pytest tests/ -v
```

### 🎯 **Paso 6: Ejecutar la Aplicación**

#### **Comandos Directos:**
```bash
# Consulta básica
poetry run python -m agentesai.cli "¿quién soy?"

# Listar usuarios del LDAP
poetry run python -m agentesai.cli "listar usuarios"

# Buscar por departamento
poetry run python -m agentesai.cli "usuarios del departamento Development"
```

### 🛠️ **Paso 7: Solución de Problemas Comunes**

#### **Error: "poetry: command not found"**
```bash
# Agregar Poetry al PATH
export PATH="/Users/$USER/.local/bin:$PATH"

# O reinstalar Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

#### **Error: "ModuleNotFoundError: No module named 'agentesai'"**
```bash
# Verificar que estás en el directorio correcto
pwd  # Debe mostrar: .../offsec_challenge/AgentesAI

# Reinstalar dependencias
poetry install --force
```

#### **Error: "API key de Gemini no configurada"**
```bash
# Verificar archivo .env
cat .env

# Asegurarte de que GEMINI_API_KEY esté configurado
export GEMINI_API_KEY="tu_api_key_aqui"
```

#### **Error: "Connection refused" en LDAP**
```bash
# Verificar que el servidor LDAP esté corriendo
# O comentar la configuración LDAP en .env si no lo necesitas
```

### 📚 **Paso 8: Primeros Pasos con la Aplicación**

1. **Ejecuta una consulta simple:**
   ```bash
   poetry run python -m agentesai.cli "¿quién soy?"
   ```

2. **Explora las herramientas base:**
   ```bash
   poetry run python -m agentesai.cli "listar usuarios"
   poetry run python -m agentesai.cli "mostrar estructura LDAP"
   ```

3. **Prueba la auto-expansión:**
   ```bash
   poetry run python -m agentesai.cli "¿cuántos grupos hay en total?"
   ```

### 🎉 **¡Listo! Tu aplicación está funcionando**

## 🎯 **Uso Rápido**

### **Comandos (Herramientas Existentes):**

```bash
# Información del usuario actual
poetry run python -m agentesai.cli "¿quién soy?"

# Grupos del usuario
poetry run python -m agentesai.cli "qué grupos tengo"

# Listar todos los usuarios
poetry run python -m agentesai.cli "listar usuarios"

# Analizar estructura LDAP con herramienta autogenerada
poetry run python -m agentesai.cli "mostrar estructura LDAP"
```

### **Auto-Expansión (Generación Dinámica de Herramientas):**

```bash
# Buscar por departamento con herramienta autogenerada
poetry run python -m agentesai.cli "usuarios del departamento Development"

# Lista de usuarios que comiencen con una letra con herramienta autogenerada
poetry run python -m agentesai.cli "Dame la lista de usuarios con nombres que comiencen por la letra J"

# Generar herramienta para análisis de departamentos
poetry run python -m agentesai.cli "¿cuál es el departamento con más usuarios?"

# Generar herramienta para ordenar usuarios
poetry run python -m agentesai.cli "mostrar usuarios ordenados alfabeticamente"

### **🔴 Herramientas Ofensivas (Análisis de Seguridad):**
```
```bash
# Análisis RootDSE del servidor LDAP
poetry run python -m agentesai.cli "rootdse info"
poetry run python -m agentesai.cli "análisis rootdse"
poetry run python -m agentesai.cli "información servidor ldap"

# Enumeración anónima del directorio
poetry run python -m agentesai.cli "enumeración anónima"
poetry run python -m agentesai.cli "bind anónimo"
poetry run python -m agentesai.cli "enumerar usuarios y grupos"

# Start TLS test
poetry run python -m agentesai.cli "starttls test"
poetry run python -m agentesai.cli "test seguridad tls"
poetry run python -m agentesai.cli "downgrade tls"

# Simple vs SASL Bind
poetry run python -m agentesai.cli "simple vs sasl bind"
poetry run python -m agentesai.cli "ldapwhoami"
poetry run python -m agentesai.cli "comparar autenticacion"
poetry run python -m agentesai.cli "fallback bind"

# ACL Diff
poetry run python -m agentesai.cli "acl diff"
poetry run python -m agentesai.cli "comparar acls"
poetry run python -m agentesai.cli "anonimo vs admin"
poetry run python -m agentesai.cli "control acceso"
poetry run python -m agentesai.cli "escalacion privilegios"

# Self Password Change
poetry run python -m agentesai.cli "self password change"
poetry run python -m agentesai.cli "cambiar contraseña"
poetry run python -m agentesai.cli "by self write"
poetry run python -m agentesai.cli "escalacion privilegios"
poetry run python -m agentesai.cli "low priv"

### **Fingerprint NSE con Target Específico:**

# Con IP específica
poetry run python -m agentesai.cli "nmap nse 192.168.1.100"
poetry run python -m agentesai.cli "fingerprint nmap 10.0.0.50"
poetry run python -m agentesai.cli "ldap nmap nse 172.16.1.10"

# Con hostname
poetry run python -m agentesai.cli "nmap nse ldap.example.com"
poetry run python -m agentesai.cli "fingerprint nmap dc01.local"
poetry run python -m agentesai.cli "nse scripts server.domain.com"

# Con puerto específico
poetry run python -m agentesai.cli "nmap nse 192.168.1.100 puerto 636"
poetry run python -m agentesai.cli "fingerprint nmap ldap.example.com 389"

# Con scripts específicos
poetry run python -m agentesai.cli "nmap nse 192.168.1.100 ldap-rootdse"
poetry run python -m agentesai.cli "fingerprint nmap 10.0.0.50 ldap-search"
poetry run python -m agentesai.cli "nse scripts server.com ldap-brute"

# Con modo verbose
poetry run python -m agentesai.cli "nmap nse 192.168.1.100 verbose"
poetry run python -m agentesai.cli "fingerprint nmap ldap.example.com detallado"

# Con timeout personalizado
poetry run python -m agentesai.cli "nmap nse 192.168.1.100 timeout 60"
poetry run python -m agentesai.cli "fingerprint nmap 10.0.0.50 timeout 120"
```

## 🔄 **Sistema de Reset**

### **Comandos de Reset Disponibles:**

El sistema detecta automáticamente cuando quieres hacer reset y ofrece múltiples formas de hacerlo:

```bash
# Formas de texto (detectadas automáticamente)
poetry run python -m agentesai.cli "reset del sistema"
poetry run python -m agentesai.cli "reset"
poetry run python -m agentesai.cli "limpiar sistema"
poetry run python -m agentesai.cli "limpiar herramientas"

# Forma con flag (tradicional)
poetry run python -m agentesai.cli --reset

# Usando Makefile
make reset
```

### **¿Qué hace el Reset?**

- 🗑️ **Elimina todas las herramientas generadas** dinámicamente
- 📚 **Limpia el registry** completamente
- 🔄 **Resetea el estado** del sistema a inicial
- 🧹 **Elimina archivos temporales** y caches
- ✅ **Mantiene solo las herramientas base** del sistema

### **Cuándo usar Reset:**

- **Después de pruebas** para limpiar herramientas generadas
- **Para liberar memoria** del sistema
- **Antes de demos** para tener un estado limpio
- **Para debugging** cuando hay problemas con herramientas generadas

## 🔧 **Configuración y Mantenimiento**

### **Variables de Entorno:**

```bash
# Gemini API Configuration
GEMINI_API_KEY=tu_api_key_aqui

# LDAP Configuration
LDAP_SERVER=ldap://localhost:389
LDAP_BASE_DN=dc=meli,dc=com
LDAP_ADMIN_DN=cn=admin,dc=meli,dc=com
LDAP_ADMIN_PASSWORD=tu_password_ldap

# Application Configuration
LOG_LEVEL=INFO
DEBUG=false
```

### **Comandos de Mantenimiento:**

```bash
# Ver estado completo del sistema
poetry run python -c "
from agentesai.agent.sistema import SistemaAgentes
sistema = SistemaAgentes()
sistema.mostrar_estado_completo()
"

# Reset del sistema
poetry run python -c "
from agentesai.agent.sistema import SistemaAgentes
sistema = SistemaAgentes()
sistema.reset_sistema()
"

# Obtener estadísticas
poetry run python -c "
from agentesai.agent.sistema import SistemaAgentes
sistema = SistemaAgentes()
stats = sistema.obtener_estadisticas()
print(stats)
"
```

## 🧪 **Pruebas y Validación**

### **Ejecutar Tests:**

```bash
# Con Poetry
poetry run pytest tests/ -v

# Con pip
python -m pytest tests/ -v

# Tests específicos
poetry run pytest tests/unit/test_coordinador.py -v
poetry run pytest tests/unit/test_ejecutor.py -v
poetry run pytest tests/unit/test_generador.py -v
poetry run pytest tests/unit/test_sistema_agentes.py -v
```

### **Verificar Funcionalidad:**

```bash
# Test de conexión LDAP
poetry run python -c "
from agentesai.tools_base.ldap_connector import LDAPConnector
conn = LDAPConnector()
print('LDAP disponible:', conn.connect())
"

# Test de generación de herramientas
poetry run python -c "
from agentesai.agent.generador import AgenteGenerador
gen = AgenteGenerador()
print('Generador disponible:', gen.api_key is not None)
"
```

## 📁 **Estructura del Proyecto**

```
AgentesAI/
├── 📚 README.md                    # Este archivo (documentación unificada)
├── 📋 README_AGENTES.md            # Documentación detallada de agentes
├── 🔄 DIAGRAMA_FLUJO.md            # Diagramas visuales del sistema
├── 📋 INDICE_DOCUMENTACION.md      # Índice de toda la documentación
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
├── pyproject.toml                # Configuración de Poetry
└── Makefile                      # Comandos de construcción
```

## 🚀 **Casos de Uso**

### **1. Consulta Simple (Herramienta Existente)**
```
Usuario: "¿quién soy?"
Sistema: Usa get_current_user_info → Resultado inmediato
```

### **2. Consulta Compleja (Nueva Herramienta)**
```
Usuario: "¿cuáles son todos los usuarios del departamento de IT?"
Sistema: Genera nueva herramienta LDAP → Ejecuta → Registra
```

### **3. Reseteo del Sistema**
```
Usuario: "reset"
Sistema: Limpia herramientas generadas → Restaura estado inicial
```

## 🔗 **Enlaces Útiles**

### **Documentación Detallada:**
- [📋 Documentación Completa](README_AGENTES.md) - Explicación completa de la arquitectura
- [🔄 Diagramas de Flujo](DIAGRAMA_FLUJO.md) - Visualizaciones detalladas
- [📚 Índice de Documentación](INDICE_DOCUMENTACION.md) - Navegación organizada

### **Configuración:**
- [requirements.txt](requirements.txt) - Dependencias del proyecto
- [pyproject.toml](pyproject.toml) - Configuración de Poetry
- [Makefile](Makefile) - Comandos de construcción

### **Pruebas:**
- [pytest.ini](pytest.ini) - Configuración de pruebas
- [tests/](tests/) - Suite de pruebas completa

---

## 📝 **Notas de Desarrollo**

- El sistema está diseñado para ser robusto y manejar errores graciosamente
- Todas las excepciones son capturadas y retornadas como parte del resultado
- El sistema mantiene estado persistente entre sesiones
- Las herramientas generadas se pueden reutilizar en futuras consultas
- El sistema es extensible para nuevos tipos de agentes y funcionalidades

---

*Documentación unificada para el Sistema de Agentes AI - Challenge OffSec*
