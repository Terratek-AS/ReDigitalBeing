from pathlib import Path
import shutil

src = Path("RoomZero/app/static")
out = Path("out")

if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True, exist_ok=True)

for p in src.iterdir():
    target = out / p.name
    if p.is_dir():
        shutil.copytree(p, target)
    else:
        shutil.copy2(p, target)

required = [
    "index.html",
    "app.js",
    "config.js",
    "manifest.json",
    "styles.css",
    "service-worker.js",
]

for name in required:
    path = out / name
    print(f"{name} {'OK' if path.exists() else 'MISSING'}")
