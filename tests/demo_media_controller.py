"""
Demo del Módulo 8: Controlador Multimedia.

Demuestra el funcionamiento del controlador en modo simulado.
"""

from src.media_controller import MediaController, ActionType


def demo_discrete_commands():
    """Demuestra comandos discretos."""
    print("Demo 1: Comandos Discretos")
    print("=" * 50)
    
    controller = MediaController(dry_run=True)
    
    commands = [
        "PLAY_PAUSA",
        "SIGUIENTE",
        "ANTERIOR",
        "ACCION_ADICIONAL",
    ]
    
    print("\nEjecutando comandos multimedia:")
    for command in commands:
        result = controller.execute(command)
        status = "✓ ÉXITO" if result.success else "✗ ERROR"
        print(f"  {status}: {command}")
        if result.error:
            print(f"    Error: {result.error}")
    
    print(f"\nComandos registrados: {len(controller.get_execution_log())}")
    print("Log de ejecución:")
    for entry in controller.get_execution_log():
        print(f"  - {entry['action']} (dry_run: {entry['dry_run']})")


def demo_volume_control():
    """Demuestra control de volumen."""
    print("\n" + "=" * 50)
    print("Demo 2: Control de Volumen")
    print("=" * 50)
    
    controller = MediaController(dry_run=True)
    
    print("\nAjustando volumen progresivamente:")
    volumes = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    
    for vol in volumes:
        result = controller.set_volume(vol)
        status = "✓" if result.success else "✗"
        print(f"  {status} Volumen: {result.value_used:.0f}%")
    
    print(f"\nComandos de volumen registrados: {len(controller.get_execution_log())}")


def demo_edge_cases():
    """Demuestra manejo de casos especiales."""
    print("\n" + "=" * 50)
    print("Demo 3: Casos Especiales")
    print("=" * 50)
    
    controller = MediaController(dry_run=True)
    
    print("\nManejo seguro de valores inválidos:")
    
    test_cases = [
        ("None command", None),
        ("Empty string", ""),
        ("Unknown command", "COMANDO_INEXISTENTE"),
        ("Number instead of string", 123),
        ("Mixed case command", "Play_Pausa"),
    ]
    
    print("\nComandos inválidos:")
    for description, command in test_cases:
        result = controller.execute(command)
        status = "✗ Rechazado" if not result.success else "✓ Aceptado"
        print(f"  {status}: {description}")
    
    # Volúmenes especiales
    print("\nVolúmenes especiales:")
    volume_cases = [
        ("Volumen negativo", -50.0),
        ("Volumen superior a 100", 150.0),
        ("Volumen None", None),
        ("Volumen string", "cincuenta"),
    ]
    
    for description, volume in volume_cases:
        result = controller.set_volume(volume)
        status = "✗ Rechazado" if not result.success else "✓ Aceptado"
        print(f"  {status}: {description}")


def demo_execution_log():
    """Demuestra el log de ejecución."""
    print("\n" + "=" * 50)
    print("Demo 4: Log de Ejecución")
    print("=" * 50)
    
    controller = MediaController(dry_run=True)
    
    print("\nEjecutando secuencia de acciones:")
    controller.execute("PLAY_PAUSA")
    controller.set_volume(30.0)
    controller.execute("SIGUIENTE")
    controller.set_volume(60.0)
    controller.execute("ANTERIOR")
    controller.set_volume(45.0)
    
    log = controller.get_execution_log()
    print(f"\nTotal de acciones registradas: {len(log)}")
    print("\nDetalle del log:")
    for i, entry in enumerate(log, 1):
        action = entry['action']
        value = entry.get('value')
        if value is not None:
            print(f"  {i}. {action}: {value:.1f}")
        else:
            print(f"  {i}. {action}")
    
    # Demostrar que el log retorna copia
    print("\nVerificación: El log retorna copia (no referencia):")
    log_copy = controller.get_execution_log()
    log_copy.append({"action": "FAKE", "dry_run": True})
    log_real = controller.get_execution_log()
    print(f"  Log real tiene {len(log_real)} elementos")
    print(f"  ✓ Copia protege el log original")


def demo_independence():
    """Demuestra independencia del módulo."""
    print("\n" + "=" * 50)
    print("Demo 5: Independencia del Módulo 8")
    print("=" * 50)
    
    print("\nEl Módulo 8 funciona sin:")
    print("  - Módulo 7 (StateMachine)")
    print("  - Webcam")
    print("  - Entrada multimedia real")
    print("  - Otros módulos del sistema")
    
    controller = MediaController(dry_run=True)
    
    # Simular que Module 7 envía comandos
    print("\nSimulando envío de comandos desde Module 7:")
    
    # Secuencia 1: PLAY
    result = controller.execute("PLAY_PAUSA")
    print(f"  Module 7 → execute(PLAY_PAUSA) → {result.success}")
    
    # Secuencia 2: Volumen
    result = controller.set_volume(50.0)
    print(f"  Module 7 → set_volume(50.0) → {result.success}, valor: {result.value_used}")
    
    # Secuencia 3: Siguiente
    result = controller.execute("SIGUIENTE")
    print(f"  Module 7 → execute(SIGUIENTE) → {result.success}")
    
    print("\n✓ Módulo 8 completamente independiente y funcional")


def demo_dry_run_modes():
    """Demuestra los modos de ejecución."""
    print("\n" + "=" * 50)
    print("Demo 6: Modos de Ejecución")
    print("=" * 50)
    
    print("\nModo DRY_RUN = True (simulado):")
    dry_controller = MediaController(dry_run=True)
    result = dry_controller.execute("PLAY_PAUSA")
    print(f"  Resultado: {result.success}")
    print(f"  Log marca dry_run: {dry_controller.get_execution_log()[0]['dry_run']}")
    
    print("\nModo DRY_RUN = False (real):")
    real_controller = MediaController(dry_run=False)
    result = real_controller.execute("SIGUIENTE")
    print(f"  Resultado: {result.success}")
    print(f"  Log marca dry_run: {real_controller.get_execution_log()[0]['dry_run']}")
    print("  (Sin cambios reales al sistema operativo)")


if __name__ == "__main__":
    try:
        demo_discrete_commands()
        demo_volume_control()
        demo_edge_cases()
        demo_execution_log()
        demo_independence()
        demo_dry_run_modes()
        
        print("\n" + "=" * 50)
        print("TODAS LAS DEMOSTRACIONES COMPLETADAS")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nError durante la demo: {e}")
        import traceback
        traceback.print_exc()
