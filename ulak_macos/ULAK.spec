# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ulak.py'],
    pathex=[],
    binaries=[],
    datas=[('ulaklo.png', '.')],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'cryptography', 'cryptography.hazmat.primitives.ciphers', 'cryptography.hazmat.backends', 'requests', 'bs4'],
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
    [],
    exclude_binaries=True,
    name='ULAK',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['ulaklo.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ULAK',
)
app = BUNDLE(
    coll,
    name='ULAK.app',
    icon='ulaklo.icns',
    bundle_identifier='net.algsoft.ulak',
)
