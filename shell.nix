{ pkgs ? import <nixpkgs> {} }:

(pkgs.buildFHSEnv {
  name = "python-fhs-env";
  targetPkgs = pkgs: with pkgs; [
    # --- Решение ваших ошибок ---
    stdenv.cc.cc.lib    # Исправляет libstdc++.so.6
    xorg.libxcb         # Исправляет libxcb.so.1
    glib                # Исправляет libgthread-2.0.so.0

    # --- Часто требуются следом (советую добавить сразу) ---
    libGL               # Для графики (OpenCV)
    libz                # Для сжатия (Pillow/Pandas)
    fontconfig          # Для отрисовки текста
    dbus                # Для системных уведомлений/интерфейсов
    
    # --- Python ---
    python3
    python3Packages.pip
  ];
  runScript = "bash";
}).env
