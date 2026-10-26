#!/usr/bin/env bash
set -e

# Source ROS 2 Humble environment
if [ -f "/opt/ros/humble/setup.bash" ]; then
    source "/opt/ros/humble/setup.bash"
fi

# Source workspace install overlay if built
if [ -f "/home/ventek/ventek_ws/install/setup.bash" ]; then
    source "/home/ventek/ventek_ws/install/setup.bash"
fi

# Ensure PYTHONPATH includes project root and src
export PYTHONPATH="/home/ventek/ventek_ws/ventek_project:${PYTHONPATH}"

# If Web GUI is requested (useful on macOS / Apple Silicon for no-config browser display)
if [ "${ENABLE_VNC:-0}" = "1" ]; then
    echo "[VENTEK Docker] Starting headless Xvfb display and noVNC on port 6080..."
    export DISPLAY=:1
    
    # Clean up stale locks if container was restarted
    rm -f /tmp/.X1-lock /tmp/.X11-unix/X1

    # Start virtual X server (1920x1080 24-bit color)
    Xvfb :1 -screen 0 1920x1080x24 +extension GLX +render -noreset &
    sleep 1

    # Start lightweight window manager
    fluxbox &
    sleep 1

    # Start VNC server (listening on localhost:5900)
    x11vnc -display :1 -nopw -forever -shared -bg -quiet

    # Start websockify/noVNC bridge on port 6080
    websockify --web=/usr/share/novnc 6080 localhost:5900 &
    
    echo "[VENTEK Docker] Web VNC running! Open in Safari/Chrome on Mac: http://localhost:6080/vnc.html?autoconnect=true"
fi

# Execute user command or default shell
exec "$@"
