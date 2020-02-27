# -*- mode: python -*-

block_cipher = None

def get_resources():
    data_files = []
    for file_name in os.listdir('resources'):
        data_files.append((os.path.join('resources', file_name), 'resources'))
    return data_files

a = Analysis(['uber-lyft.py'],
             pathex=['C:\\Users\\teresa\\uber-Lyft'],
             binaries=[],
             datas=get_resources(),
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
          name='uber-lyft',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='logo.ico')
