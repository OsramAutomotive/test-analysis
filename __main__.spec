# -*- mode: python -*-

block_cipher = None

added_files = [
         ( 'styles/*.qss', 'styles' ),
         ( 'images/*.png', 'images' ),
         ( '!output/templates/data.xsl', '!output/templates'),
         ( '!output/templates/styles.css', '!output/templates')
         ]

a = Analysis(['__main__.py'],
             pathex=['C:\\Users\\bruno\\programming-projects\\Test Data Analysis', 'C:\\Python35\\Lib\\site-packages\\PyQt5\\Qt\\bin'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='__main__',
          debug=False,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='__main__')
