#!/usr/bin/env python3
"""
CLI principal para el sistema de agentes AI
"""

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

console = Console()

@click.command()
@click.argument('query', required=False)
@click.option('--reset', is_flag=True, help='Reset del sistema a estado original')
def main(query, reset):
    """Sistema de Agentes AI Auto-Adaptativos para Offensive Security"""
    
    # Cargar variables de entorno
    load_dotenv()

    if reset:
        console.print(Panel("🔄 Reseteando sistema...", style="blue"))
        
        try:
            # Importar y usar el sistema de agentes
            from agentesai.agent.sistema import SistemaAgentes
            
            # Crear instancia del sistema
            sistema = SistemaAgentes()
            
            # Ejecutar reset completo
            resultado_reset = sistema.reset_sistema()
            
            if resultado_reset.get("error"):
                console.print(Panel(f"❌ Error en reset: {resultado_reset.get('mensaje', 'Error desconocido')}", style="red"))
            else:
                console.print(Panel("✅ Sistema reseteado exitosamente", style="green"))
                
                # Mostrar información del reset
                herramientas_removidas = resultado_reset.get("herramientas_removidas", [])
                if herramientas_removidas:
                    console.print(Panel(f"🗑️ Herramientas removidas: {len(herramientas_removidas)}", style="yellow"))
                    for herramienta in herramientas_removidas:
                        console.print(f"   - {herramienta}")
                
        except Exception as e:
            console.print(Panel(f"❌ Error durante el reset: {str(e)}", style="red"))
        
        return

    if not query:
        console.print(Panel("🤖 Bienvenido al Sistema de Agentes AI\n\nUso: python -m agentesai.cli 'tu consulta'\n\nEjemplos:\n- python -m agentesai.cli '¿quién soy?'\n- python -m agentesai.cli 'listar usuarios'\n- python -m agentesai.cli 'estructura ldap'\n- python -m agentesai.cli 'reset del sistema'", style="green"))
        return
    
    # Detectar si el usuario quiere hacer reset del sistema
    if query.lower().strip() in ["reset", "reset del sistema", "reset sistema", "limpiar sistema", "limpiar herramientas"]:
        console.print(Panel("🔄 Detectado comando de reset del sistema...", style="blue"))
        
        try:
            # Importar y usar el sistema de agentes
            from agentesai.agent.sistema import SistemaAgentes
            
            # Crear instancia del sistema
            sistema = SistemaAgentes()
            
            # Ejecutar reset completo
            resultado_reset = sistema.reset_sistema()
            
            if resultado_reset.get("error"):
                console.print(Panel(f"❌ Error en reset: {resultado_reset.get('mensaje', 'Error desconocido')}", style="red"))
            else:
                console.print(Panel("✅ Sistema reseteado exitosamente", style="green"))
                
                # Mostrar información del reset
                herramientas_removidas = resultado_reset.get("herramientas_removidas", [])
                if herramientas_removidas:
                    console.print(Panel(f"🗑️ Herramientas removidas: {len(herramientas_removidas)}", style="yellow"))
                    for herramienta in herramientas_removidas:
                        console.print(f"   - {herramienta}")
                else:
                    console.print(Panel("🧹 No había herramientas generadas para limpiar", style="cyan"))
                
        except Exception as e:
            console.print(Panel(f"❌ Error durante el reset: {str(e)}", style="red"))
        
        return

    console.print(Panel(f"🎯 Procesando consulta: {query}", style="yellow"))
    
    try:
        # Importar y usar el sistema de agentes
        from agentesai.agent.sistema import SistemaAgentes
        
        # Crear instancia del sistema
        sistema = SistemaAgentes()
        
        # Procesar la consulta
        resultado = sistema.procesar_consulta(query)
        
        # Mostrar resultado de manera organizada
        if resultado.get("error"):
            console.print(Panel(f"❌ Error: {resultado.get('mensaje', 'Error desconocido')}", style="red"))
        else:
            # Mostrar resultado según el tipo
            tipo = resultado.get("tipo", "desconocido")
            
            if tipo == "herramienta_generada":
                # Resultado de herramienta generada
                console.print(Panel("🎉 Herramienta Generada Exitosamente", style="bold green"))
                
                # Mostrar información de la herramienta
                herramienta = resultado.get("herramienta", "N/A")
                console.print(Panel(f"🔧 Nombre: {herramienta}", style="cyan"))
                
                # Mostrar resultado de ejecución
                if "resultado_ejecucion" in resultado:
                    ejecucion = resultado["resultado_ejecucion"]
                    if isinstance(ejecucion, dict):
                        if ejecucion.get("error"):
                            console.print(Panel(f"❌ Error en ejecución: {ejecucion.get('mensaje', 'Error desconocido')}", style="red"))
                        else:
                            resultado_final = ejecucion.get("resultado", "Sin resultado")
                            console.print(Panel(f"📊 Resultado: {resultado_final}", style="bold blue"))
                    else:
                        console.print(Panel(f"📊 Resultado: {ejecucion}", style="bold blue"))
                
                # Mostrar código generado (opcional)
                if "resultado_generacion" in resultado:
                    codigo = resultado["resultado_generacion"].get("codigo", "")
                    if codigo:
                        console.print(Panel("💻 Código Generado", style="yellow"))
                        console.print(Panel(codigo, style="dim"))
                
            elif tipo == "herramienta_existente":
                # Resultado de herramienta existente
                ejecucion = resultado.get("resultado", {})
                if isinstance(ejecucion, dict):
                    if ejecucion.get("error"):
                        console.print(Panel(f"❌ Error: {ejecucion.get('mensaje', 'Error desconocido')}", style="red"))
                    else:
                        resultado_final = ejecucion.get("resultado", "Sin resultado")
                        console.print(Panel(f"📊 Resultado: {resultado_final}", style="bold blue"))
                else:
                    console.print(Panel(f"📊 Resultado: {ejecucion}", style="bold blue"))
            
            elif tipo == "herramienta_ofensiva":
                # Resultado de herramienta ofensiva - ya se mostró formateado en el sistema
                console.print(Panel("✅ Herramienta ofensiva ejecutada exitosamente", style="bold green"))
                console.print("📊 El resultado formateado ya se mostró arriba")
                    
            else:
                # Resultado genérico
                console.print(Panel(f"📊 Resultado: {resultado}", style="green"))
            
    except Exception as e:
        console.print(Panel(f"❌ Error procesando consulta: {str(e)}", style="red"))

if __name__ == "__main__":
    main() 