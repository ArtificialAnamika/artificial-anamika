#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# ✨ ARTIFICIAL ANAMIKA — 1-LINE NATIVE TERMUX INSTALLER & PROVISIONER
# ==============================================================================

set -e

GREEN="\033[1;32m"
CYAN="\033[1;36m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

echo -e "${CYAN}"
echo "   _              __  __ _ _         "
echo "  /_\  _ _  __ _ |  \/  (_) |____ _  "
echo " / _ \| ' \/ _` || |\/| | | / / _` | "
echo "/_/ \_\_||_\__,_||_|  |_|_|_\_\__,_| "
echo -e "${RESET}"
echo -e "${GREEN}⚡ Starting 1-Line Native Installation for Artificial Anamika...${RESET}\n"

# Step 1: Detect Environment
if [ -z "$PREFIX" ]; then
    INSTALL_DIR="$HOME/.anamika/app"
    BIN_DIR="/usr/local/bin"
else
    INSTALL_DIR="$PREFIX/opt/artificial-anamika"
    BIN_DIR="$PREFIX/bin"
    
    echo -e "${YELLOW}📦 [1/4] Updating Termux packages & installing dependencies...${RESET}"
    pkg update -y -o Dpkg::Options::="--force-confnew" || true
    pkg install -y python git termux-api jq curl -o Dpkg::Options::="--force-confnew"
fi

# Step 2: Clone or Update Repository
echo -e "${YELLOW}📥 [2/4] Fetching latest Artificial Anamika codebase...${RESET}"
mkdir -p "$(dirname "$INSTALL_DIR")"

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating existing installation..."
    cd "$INSTALL_DIR"
    git fetch origin
    git reset --hard origin/main
else
    rm -rf "$INSTALL_DIR"
    git clone https://github.com/ArtificialAnamika/artificial-anamika.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Step 3: Create executable runner
echo -e "${YELLOW}🔗 [3/4] Creating system binary link ($BIN_DIR/anamika)...${RESET}"
mkdir -p "$BIN_DIR"
chmod +x "$INSTALL_DIR/main.py"

cat << 'EOF' > "$BIN_DIR/anamika"
#!/data/data/com.termux/files/usr/bin/bash
exec python3 "${PREFIX:-/usr}/opt/artificial-anamika/main.py" "$@"
EOF

# For standard linux / fallback path
if [ -z "$PREFIX" ]; then
cat << EOF > "$BIN_DIR/anamika"
#!/usr/bin/env bash
exec python3 "$INSTALL_DIR/main.py" "\$@"
EOF
fi

chmod +x "$BIN_DIR/anamika"

# Step 4: Final verification & launch config wizard
echo -e "\n${GREEN}✅ Installation Complete!${RESET}"
echo -e "${CYAN}------------------------------------------------------------${RESET}"
echo -e "💡 To start chat:       ${YELLOW}anamika${RESET}"
echo -e "💡 To configure:        ${YELLOW}anamika config${RESET}"
echo -e "💡 To check doctor:     ${YELLOW}anamika doctor${RESET}"
echo -e "💡 To run Telegram bot: ${YELLOW}anamika telegram${RESET}"
echo -e "💡 To list tools:       ${YELLOW}anamika tools${RESET}"
echo -e "${CYAN}------------------------------------------------------------${RESET}\n"

# Launch setup wizard immediately if interactive
if [ -t 0 ]; then
    echo -e "${GREEN}🚀 Launching Interactive Setup Wizard...${RESET}\n"
    python3 "$INSTALL_DIR/main.py" config
fi
