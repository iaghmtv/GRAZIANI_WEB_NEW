#!/usr/bin/env bash
# Espera a que termine el render de Video Inducción Técnica (no se toca) y renderiza las botellas finales por GPU.
D="E:/GRACIANI/WEB GRAZIANI/06 BLENDER PRODUCTOS WEB"
BL="/c/Program Files/Blender Foundation/Blender 5.1/blender.exe"
BF="E:/GRACIANI/Botellas Finales"
while tasklist //FI "PID eq 53364" 2>/dev/null | grep -qi blender; do sleep 20; done
echo "$(date +%H:%M:%S) GPU libre: $(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader)"
COMUN="modo=web res=100 samples=256 device=GPU base_brillo=0 flags=1 frontal=20 fuerza_color=1.5"
"$BL" -b "$BF/Graziani Botellas_FondosNuevosColores_Camara 90 mm_Amargos Nuevas Etiqueta verde EXP tapa shortclaude 1.blend" \
  -P "$D/productos_web.py" -- $COMUN productos=todos "renombrar=agua500>ecoagua500" salida="$D/render_final_junio" > "$D/final_junio.log" 2>&1
echo "$(date +%H:%M:%S) junio: $(grep -c '^OK' "$D/final_junio.log") renders"
"$BL" -b "$BF/Graziani Botellas_FondosNuevosColores_Camara 90 mm.blend" \
  -P "$D/productos_web.py" -- $COMUN productos=agua500 salida="$D/render_final_abril" > "$D/final_abril.log" 2>&1
echo "$(date +%H:%M:%S) abril: $(grep -c '^OK' "$D/final_abril.log") renders"
grep -hE "Error|Traceback" "$D/final_junio.log" "$D/final_abril.log" | head -5
