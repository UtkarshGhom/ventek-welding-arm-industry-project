# Multi-architecture Dockerfile for VENTEK Autonomous Robotic Welding
# Supports Apple Silicon (MacBook M2, M3, M4 - arm64) and standard x86_64 PCs (amd64)

FROM osrf/ros:humble-desktop

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 1. Install prerequisites and configure Gazebo Harmonic repository
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    lsb-release \
    ca-certificates \
    && mkdir -p /usr/share/keyrings \
    && curl -fsSL https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" > /etc/apt/sources.list.d/gazebo-stable.list \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Gazebo Harmonic, ROS 2 bridges, controllers, and development utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    gz-harmonic \
    ros-humble-ros-gzharmonic \
    ros-humble-ros-gzharmonic-sim \
    ros-humble-ros-gzharmonic-bridge \
    ros-humble-ros-gzharmonic-image \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-controller-manager \
    ros-humble-joint-trajectory-controller \
    ros-humble-joint-state-broadcaster \
    ros-humble-xacro \
    ros-humble-rviz2 \
    ros-humble-cv-bridge \
    python3-colcon-common-extensions \
    python3-pip \
    python3-pytest \
    python3-pytest-cov \
    python3-opencv \
    python3-yaml \
    git \
    sudo \
    nano \
    net-tools \
    # Web VNC packages (enables zero-config 3D GUI in browser on macOS)
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    libgl1-mesa-dri \
    libgl1-mesa-glx \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Python dependencies for data contracts & CAD/mesh checks
RUN pip3 install --no-cache-dir \
    jsonschema \
    trimesh \
    numpy

# 4. Create non-root developer user with matching host UID/GID
ARG USERNAME=ventek
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/bash \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# 5. Set up workspace directory and entrypoint
WORKDIR /home/ventek/ventek_ws

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER $USERNAME

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
