# -*- mode: python -*-

block_cipher = None


a = Analysis(['SMTPTool.py'],
             pathex=['C:\\Users\\ishan_shinde\\Desktop\\personalrepo-master-00dcab3ce9b5a377d323bd2ab6a8282862dcfa2f\\SMTPTool'],
             binaries=[],
             datas=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SMTPTool',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
