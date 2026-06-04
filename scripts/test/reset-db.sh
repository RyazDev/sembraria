#!/bin/bash
# ====================================================================
#  SEMBRARIA — Reset DB (Linux/Mac/WSL)
# ====================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

bash "$SCRIPT_DIR/setup-db.sh"
