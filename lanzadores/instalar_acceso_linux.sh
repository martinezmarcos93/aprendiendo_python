#!/usr/bin/env sh
# Crea el acceso directo de TortuScript en el menú de aplicaciones de Linux (solo para tu usuario).
# Uso:  sh lanzadores/instalar_acceso_linux.sh
AQUI="$(cd "$(dirname "$0")/.." && pwd)"
DESTINO="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$DESTINO" || exit 1
cat > "$DESTINO/tortuscript.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=TortuScript
Comment=Aprendé a programar en español
Exec=sh "$AQUI/lanzadores/iniciar_tortuscript.sh"
Icon=$AQUI/web/static/img/tortuscript.svg
Terminal=false
Categories=Education;Development;
EOF
chmod +x "$AQUI/lanzadores/iniciar_tortuscript.sh"
echo "Listo: buscá «TortuScript» en el menú de aplicaciones."
