# -*- coding: utf-8 -*-
r"""
encolar_wan.py — Manda el workflow Wan 2.2 I2V (API) a ComfyUI y trae los frames PNG resultantes.

Requisitos:
  1. ComfyUI corriendo:  E:\ComfyUI_portable\run_portable_8188.bat
  2. La foto en el input de ComfyUI:  C:\Users\Urano\Documents\ComfyUI\input\cordillera_graziani.jpg
Uso:
  python encolar_wan.py                 (seed y prompt del JSON)
  python encolar_wan.py --seed 123      (otra semilla)
  python encolar_wan.py --prompt "..."  (otro prompt positivo)
Salida: 04 COMFYUI CORDILLERA\salida\cordillera_tilt_<seed>.mp4
"""
import json, sys, time, uuid, shutil, os, urllib.request, urllib.error

HOST = "http://127.0.0.1:8188"
AQUI = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(AQUI, "wan22_i2v_cordillera_api.json")
OUT_COMFY = r"E:\ComfyUI_portable\output"
SALIDA = os.path.join(AQUI, "salida")

args = sys.argv[1:]
seed = int(args[args.index("--seed") + 1]) if "--seed" in args else None
prompt_txt = args[args.index("--prompt") + 1] if "--prompt" in args else None

wf = json.load(open(WF, encoding="utf-8"))
if seed is not None:
    wf["13"]["inputs"]["noise_seed"] = seed
else:
    seed = wf["13"]["inputs"]["noise_seed"]
if prompt_txt:
    wf["9"]["inputs"]["text"] = prompt_txt

def api(path, data=None):
    req = urllib.request.Request(HOST + path, data=json.dumps(data).encode() if data else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

try:
    api("/system_stats")
except Exception as e:
    print("ComfyUI no responde en", HOST, "->", e); print("Abrí E:\\ComfyUI_portable\\run_portable_8188.bat y volvé a correr."); sys.exit(1)

client = str(uuid.uuid4())
try:
    res = api("/prompt", {"prompt": wf, "client_id": client})
except urllib.error.HTTPError as e:
    print("ComfyUI rechazó el workflow:"); print(e.read().decode()[:3000]); sys.exit(1)
pid = res["prompt_id"]
print("Encolado", pid, "seed", seed, "- generando 81 frames 1280x720 (varios minutos)...")

t0 = time.time()
while True:
    time.sleep(5)
    hist = api(f"/history/{pid}")
    if pid in hist:
        h = hist[pid]
        st = h.get("status", {})
        if st.get("status_str") == "error":
            print("ERROR en la ejecución:"); print(json.dumps(st.get("messages", []), indent=1, ensure_ascii=False)[:3000]); sys.exit(1)
        if st.get("completed") or h.get("outputs"):
            break
    print(f"  ... {time.time()-t0:5.0f}s", end="\r")

archivos = []
for node, out in h["outputs"].items():
    for k, v in out.items():
        if isinstance(v, list):
            for it in v:
                if isinstance(it, dict) and "filename" in it:
                    archivos.append(os.path.join(OUT_COMFY, it.get("subfolder", ""), it["filename"]))
if not archivos:
    print("Terminó pero no encontré archivos de salida en el historial:", h["outputs"]); sys.exit(1)
dst_dir = os.path.join(SALIDA, f"frames_{seed}")
os.makedirs(dst_dir, exist_ok=True)
for i, a in enumerate(sorted(archivos)):
    shutil.copy2(a, os.path.join(dst_dir, f"f_{i:04d}{os.path.splitext(a)[1]}"))
print(f"\nListo en {time.time()-t0:.0f}s: {len(archivos)} frames ->", dst_dir)
print("Siguiente paso:  python extraer_frames.py", dst_dir)
