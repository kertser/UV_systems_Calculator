# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['C:/Users/kerts/Desktop/Calculator/calculator.py'],
             pathex=['C:\\Users\\kerts\\Desktop\\Calculator'],
             binaries=[],
             datas=[('C:/Users/kerts/Desktop/Calculator/Calculator_v11a5.ui', '.'), ('C:/Users/kerts/Desktop/Calculator/KillData.xlsx', '.'), ('C:/Users/kerts/Desktop/Calculator/logo_long.jpg', '.'), ('C:/Users/kerts/Desktop/Calculator/UV Systems.xlsx', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='calculator',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='C:\\Users\\kerts\\Desktop\\Calculator\\Calculator.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='calculator')
