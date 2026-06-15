# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\pygame\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\pygame\\sounds', 'sounds'), ('C:\\pygame\\arena_sound_settings.json', '.'), ('C:\\pygame\\CHANGELOG_2_0_0.txt', '.'), ('C:\\pygame\\gski.png', '.'), ('C:\\pygame\\gunwoo.jpg', '.'), ('C:\\pygame\\jaemin.jpg', '.'), ('C:\\pygame\\jungwoo.png', '.'), ('C:\\pygame\\minjae.jpg', '.'), ('C:\\pygame\\suin.jpg', '.'), ('C:\\pygame\\sunghyun.png', '.'), ('C:\\pygame\\sungmin.jpg', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Arena_Battle_2_0_0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
