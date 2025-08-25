# 🔄 Diagrama de Flujo Detallado del Sistema de Agentes AI

## 📊 Vista General del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           🚀 SISTEMA DE AGENTES AI                            │
│                              Challenge OffSec                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            🔄 SistemaAgentes                                   │
│                              (sistema.py)                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ • Recibe consultas del usuario                                        │   │
│  │ • Coordina flujo de trabajo                                           │   │
│  │ • Maneja estado global                                                │   │
│  │ • Interfaz interactiva                                                │   │
│  │ • Contadores de consultas                                             │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          🧠 AgenteCoordinador                                  │
│                            (coordinador.py)                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ • Analiza consultas con patrones de texto                              │   │
│  │ • Toma decisiones de ruteo inteligente                                 │   │
│  │ • Mantiene registro de herramientas disponibles                        │   │
│  │ • Rutea consultas al agente apropiado                                  │   │
│  │ • Reconocimiento de consultas conocidas                               │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
                    ┌─────────────────────────────────────────────────┐
                    │              🎯 DECISIÓN                        │
                    │                                               │
                    │  ¿Puede responder con herramienta existente?  │
                    │                                               │
                    │  Patrones conocidos:                          │
                    │  • "quién soy" → get_current_user_info        │
                    │  • "qué grupos" → get_user_groups             │
                    │  • "reset" → reset_system                     │
                    │  • "usuarios" → list_all_users                │
                    │  • "departamento" → search_users_by_department│
                    │  • "estructura" → analyze_ldap_structure      │
                    └─────────────────────────────────────────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
                    ▼                                       ▼
        ┌─────────────────────────┐         ┌─────────────────────────┐
        │    ⚡ AgenteEjecutor    │         │   🤖 AgenteGenerador    │
        │      (ejecutor.py)      │         │    (generador.py)       │
        │                         │         │                         │
        │  ┌─────────────────┐   │         │  ┌─────────────────┐   │
        │  │ • Tools Base    │   │         │  │ • Gemini API    │   │
        │  │ • Tools Gen.    │   │         │  │ • Código Python │   │
        │  │ • Ejecución     │   │         │  │ • Funciones     │   │
        │  │ • Manejo Errores│   │         │  │ • Fallbacks     │   │
        │  │ • Estadísticas  │   │         │  │ • Templates     │   │
        │  └─────────────────┘   │         │  └─────────────────┘   │
        └─────────────────────────┘         └─────────────────────────┘
                    │                                       │
                    └─────────────────┬─────────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────────────────────────────┐
        │                        📚 RegistryTools                                │
        │                          (registry.py)                                 │
        │  ┌─────────────────────────────────────────────────────────────────┐   │
        │  │ • Registra herramientas generadas                               │   │
        │  │ • Mantiene metadatos y historial                                │   │
        │  │ • Persistencia en disco (JSON)                                  │   │
        │  │ • Estadísticas del sistema                                       │   │
        │  │ • Auditoría completa de operaciones                             │   │
        │  └─────────────────────────────────────────────────────────────────┘   │
        └─────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Flujo de Procesamiento Detallado

### **Flujo 1: Herramienta Existente**
```
Usuario: "¿quién soy?"
    │
    ▼
┌─────────────────┐
│ SistemaAgentes  │ → procesar_consulta("¿quién soy?")
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ AgenteCoordinador│ → analizar_consulta("¿quién soy?")
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Patrón detectado│ → "quién soy" ∈ patrones_conocidos
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Decisión:       │ → {"accion": "ejecutar", "herramienta": "get_current_user_info"}
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ AgenteEjecutor  │ → ejecutar_herramienta("get_current_user_info")
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Resultado       │ → {"error": false, "resultado": "Usuario: admin..."}
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ RegistryTools   │ → incrementar_uso("get_current_user_info")
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Usuario         │ ← Resultado retornado
└─────────────────┘
```

### **Flujo 2: Nueva Herramienta**
```
Usuario: "¿cuáles son todos los usuarios del departamento de IT?"
    │
    ▼
┌─────────────────┐
│ SistemaAgentes  │ → procesar_consulta(consulta_compleja)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ AgenteCoordinador│ → analizar_consulta(consulta_compleja)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Patrón NO       │ → consulta ∉ patrones_conocidos
│ detectado       │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Decisión:       │ → {"accion": "generar", "tipo_herramienta": "ldap_query"}
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ AgenteGenerador │ → generar_herramienta(consulta, "ldap_query")
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Gemini API      │ → Genera código Python para consulta LDAP
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Función         │ → Crea función dinámica ejecutable
│ Dinámica        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ RegistryTools   │ → registrar_herramienta(nombre, metadata)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ AgenteEjecutor  │ → agregar_herramienta_generada(nombre, funcion)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Ejecución       │ → ejecutar_herramienta(nombre_generada)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Resultado       │ → {"error": false, "resultado": "Usuarios IT: 15 encontrados"}
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Usuario         │ ← Resultado retornado
└─────────────────┘
```

## 🎯 Puntos de Decisión Clave

### **1. Análisis de Consulta**
```
┌─────────────────────────────────────────────────────────────────┐
│                    🧠 PUNTO DE DECISIÓN 1                      │
│                    Análisis de Consulta                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │ ¿Patrón conocido?   │
                    └─────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
            ┌─────────────┐         ┌─────────────┐
            │    SÍ       │         │     NO      │
            └─────────────┘         └─────────────┘
                    │                       │
                    ▼                       ▼
            ┌─────────────┐         ┌─────────────┐
            │ Ejecutar    │         │ Generar     │
            │ Herramienta │         │ Nueva       │
            │ Existente   │         │ Herramienta │
            └─────────────┘         └─────────────┘
```

### **2. Tipo de Herramienta a Generar**
```
┌─────────────────────────────────────────────────────────────────┐
│                    🤖 PUNTO DE DECISIÓN 2                      │
│                    Tipo de Herramienta                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │ ¿Qué tipo generar?  │
                    └─────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
            ┌─────────────┐         ┌─────────────┐
            │ LDAP Query  │         │ Generic     │
            │             │         │ Query       │
            └─────────────┘         └─────────────┘
                    │                       │
                    ▼                       ▼
            ┌─────────────┐         ┌─────────────┐
            │ • Conexión  │         │ • Respuesta │
            │   LDAP      │         │   Genérica  │
            │ • Búsquedas │         │ • Templates │
            │ • Filtros   │         │   Básicos   │
            └─────────────┘         └─────────────┘
```

## 🔧 Herramientas Base Disponibles

### **Categorías de Herramientas**

```
┌─────────────────────────────────────────────────────────────────┐
│                    🛠️ HERRAMIENTAS BASE                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
        ┌─────────────────────┐    ┌─────────────────────┐
        │   OBLIGATORIAS      │    │    ADICIONALES      │
        │   (Challenge)       │    │  (Seguridad Of.)    │
        └─────────────────────┘    └─────────────────────┘
                    │                       │
                    ▼                       ▼
        ┌─────────────────────┐    ┌─────────────────────┐
        │ • get_current_user_ │    │ • list_all_users    │
        │   info              │    │ • search_users_by_  │
        │ • get_user_groups   │    │   department        │
        │ • reset_system      │    │ • analyze_ldap_     │
        │                     │    │   structure         │
        └─────────────────────┘    └─────────────────────┘
```

## 📊 Flujo de Datos y Persistencia

### **Persistencia de Datos**
```
┌─────────────────────────────────────────────────────────────────┐
│                    💾 PERSISTENCIA DE DATOS                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
        ┌─────────────────────┐    ┌─────────────────────┐
        │   RegistryTools     │    │   Archivos Disco     │
        │   (Memoria)         │    │                     │
        └─────────────────────┘    └─────────────────────┘
                    │                       │
                    ▼                       ▼
        ┌─────────────────────┐    ┌─────────────────────┐
        │ • Herramientas      │    │ • tools_registry.json│
        │   registradas       │    │ • Historial completo │
        │ • Metadatos         │    │ • Estadísticas      │
        │ • Contadores        │    │ • Timestamps        │
        └─────────────────────┘    └─────────────────────┘
```

---

*Diagrama de flujo detallado para el Sistema de Agentes AI - Challenge OffSec* 