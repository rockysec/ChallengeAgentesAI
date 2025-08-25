#!/bin/bash

# 🚀 Script de Instalación Automática - Sistema de Agentes AI
# Compatible con: macOS, Ubuntu, Debian, CentOS, RHEL

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para detectar el sistema operativo
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$NAME
            VER=$VERSION_ID
        else
            OS=$(uname -s)
            VER=$(uname -r)
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
        VER=$(sw_vers -productVersion)
    else
        OS="Unknown"
        VER="Unknown"
    fi
    
    print_status "Sistema operativo detectado: $OS $VER"
}

# Función para verificar Python
check_python() {
    print_status "Verificando Python..."
    
    if command -v python3.11 &> /dev/null; then
        PYTHON_VERSION=$(python3.11 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION encontrado"
        PYTHON_CMD="python3.11"
    elif command -v python3.10 &> /dev/null; then
        PYTHON_VERSION=$(python3.10 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION encontrado"
        PYTHON_CMD="python3.10"
    elif command -v python3.9 &> /dev/null; then
        PYTHON_VERSION=$(python3.9 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION encontrado"
        PYTHON_CMD="python3.9"
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION encontrado"
        PYTHON_CMD="python3"
    else
        print_error "Python 3.8+ no encontrado. Instalando..."
        install_python
    fi
}

# Función para instalar Python
install_python() {
    print_status "Instalando Python..."
    
    if [[ "$OS" == "macOS" ]]; then
        if ! command -v brew &> /dev/null; then
            print_status "Instalando Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python@3.11
        PYTHON_CMD="python3.11"
        
    elif [[ "$OS" == "Ubuntu" ]] || [[ "$OS" == "Debian" ]]; then
        sudo apt update
        sudo apt install -y python3.11 python3.11-venv python3.11-pip python3-pip
        PYTHON_CMD="python3.11"
        
    elif [[ "$OS" == "CentOS Linux" ]] || [[ "$OS" == "Red Hat Enterprise Linux" ]]; then
        if [[ "$VER" == "7" ]]; then
            sudo yum install -y python3.11 python3.11-pip python3.11-devel
        else
            sudo dnf install -y python3.11 python3.11-pip python3.11-devel
        fi
        PYTHON_CMD="python3.11"
        
    else
        print_error "Sistema operativo no soportado para instalación automática de Python"
        print_status "Por favor, instala Python 3.8+ manualmente"
        exit 1
    fi
    
    print_success "Python instalado correctamente"
}

# Función para verificar Poetry
check_poetry() {
    print_status "Verificando Poetry..."
    
    if command -v poetry &> /dev/null; then
        POETRY_VERSION=$(poetry --version)
        print_success "Poetry encontrado: $POETRY_VERSION"
    else
        print_status "Poetry no encontrado. Instalando..."
        install_poetry
    fi
}

# Función para instalar Poetry
install_poetry() {
    print_status "Instalando Poetry..."
    
    # Instalar Poetry
    curl -sSL https://install.python-poetry.org | $PYTHON_CMD -
    
    # Agregar al PATH
    if [[ "$OS" == "macOS" ]]; then
        echo 'export PATH="/Users/$USER/.local/bin:$PATH"' >> ~/.zshrc
        export PATH="/Users/$USER/.local/bin:$PATH"
    else
        echo 'export PATH="/home/$USER/.local/bin:$PATH"' >> ~/.bashrc
        export PATH="/home/$USER/.local/bin:$PATH"
    fi
    
    # Verificar instalación
    if command -v poetry &> /dev/null; then
        print_success "Poetry instalado correctamente"
    else
        print_error "Error al instalar Poetry"
        exit 1
    fi
}

# Función para verificar Git
check_git() {
    print_status "Verificando Git..."
    
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_success "Git encontrado: $GIT_VERSION"
    else
        print_error "Git no encontrado. Por favor, instálalo manualmente:"
        if [[ "$OS" == "macOS" ]]; then
            print_status "brew install git"
        elif [[ "$OS" == "Ubuntu" ]] || [[ "$OS" == "Debian" ]]; then
            print_status "sudo apt install git"
        elif [[ "$OS" == "CentOS Linux" ]] || [[ "$OS" == "Red Hat Enterprise Linux" ]]; then
            print_status "sudo yum install git"
        fi
        exit 1
    fi
}

# Función para clonar repositorio
clone_repo() {
    print_status "Clonando repositorio..."
    
    if [ -d "offsec_challenge" ]; then
        print_warning "Directorio offsec_challenge ya existe"
        read -p "¿Deseas continuar con el directorio existente? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Por favor, elimina el directorio existente y ejecuta el script nuevamente"
            exit 1
        fi
    else
        git clone https://github.com/tu-usuario/offsec_challenge.git
    fi
    
    cd offsec_challenge/AgentesAI
    
    if [ ! -f "pyproject.toml" ]; then
        print_error "No se encontró pyproject.toml. Verifica que el repositorio se clonó correctamente"
        exit 1
    fi
    
    print_success "Repositorio clonado correctamente"
}

# Función para instalar dependencias
install_dependencies() {
    print_status "Instalando dependencias..."
    
    # Configurar Poetry para usar la versión de Python correcta
    poetry env use $PYTHON_CMD
    
    # Instalar dependencias
    poetry install
    
    print_success "Dependencias instaladas correctamente"
}

# Función para configurar variables de entorno
setup_env() {
    print_status "Configurando variables de entorno..."
    
    if [ -f ".env.example" ]; then
        if [ ! -f ".env" ]; then
            cp .env.example .env
            print_success "Archivo .env creado desde .env.example"
            print_warning "IMPORTANTE: Edita .env y configura tu GEMINI_API_KEY"
        else
            print_warning "Archivo .env ya existe"
        fi
    else
        print_warning "Archivo .env.example no encontrado"
    fi
}

# Función para verificar instalación
verify_installation() {
    print_status "Verificando instalación..."
    
    # Verificar que el módulo se puede importar
    if poetry run python -c "from agentesai.agent.sistema import SistemaAgentes; print('✅ Módulo importado correctamente')" 2>/dev/null; then
        print_success "Módulo importado correctamente"
    else
        print_error "Error al importar módulo"
        exit 1
    fi
    
    # Verificar tests
    print_status "Ejecutando tests de verificación..."
    if poetry run pytest tests/ -q --tb=no 2>/dev/null; then
        print_success "Tests ejecutados correctamente"
    else
        print_warning "Algunos tests fallaron, pero la instalación básica está completa"
    fi
    
    print_success "Instalación verificada correctamente"
}

# Función para mostrar próximos pasos
show_next_steps() {
    echo
    echo -e "${GREEN}🎉 ¡Instalación completada exitosamente!${NC}"
    echo
    echo -e "${BLUE}📋 Próximos pasos:${NC}"
    echo "1. Configura tu API key de Gemini en el archivo .env"
    echo "2. Ejecuta tu primera consulta:"
    echo "   poetry run python -m agentesai.cli '¿quién soy?'"
    echo "3. Explora más funcionalidades:"
    echo "   poetry run python demo_completo.py"
    echo
    echo -e "${BLUE}📚 Documentación:${NC}"
    echo "- README.md: Guía de uso principal"
    echo "- INSTALACION.md: Guía de instalación detallada"
    echo
    echo -e "${BLUE}🆘 Soporte:${NC}"
    echo "- Revisa la sección de solución de problemas en INSTALACION.md"
    echo "- Abre un issue en el repositorio si encuentras problemas"
}

# Función principal
main() {
    echo -e "${BLUE}🚀 Script de Instalación Automática - Sistema de Agentes AI${NC}"
    echo "================================================================"
    echo
    
    # Detectar sistema operativo
    detect_os
    
    # Verificar requisitos
    check_python
    check_poetry
    check_git
    
    # Instalar aplicación
    clone_repo
    install_dependencies
    setup_env
    
    # Verificar instalación
    verify_installation
    
    # Mostrar próximos pasos
    show_next_steps
}

# Ejecutar función principal
main "$@" 