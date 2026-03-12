"""Shared sample documents for tests."""

SAMPLE_XLIFF = """<?xml version="1.0" encoding="UTF-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file source-language="en" target-language="zh" datatype="plaintext" original="test.txt">
    <body>
      <trans-unit id="1">
        <source>Hello World</source>
        <target>你好世界</target>
      </trans-unit>
      <trans-unit id="2">
        <source>This is a <g id="1">test</g> message.</source>
        <target></target>
      </trans-unit>
    </body>
  </file>
</xliff>"""

SAMPLE_TMX = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">
  <header creationtool="TestTool" creationtoolversion="1.0"
          datatype="plaintext" segtype="sentence"
          adminlang="en" srclang="en" o-tmf="test"/>
  <body>
    <tu>
      <tuv xml:lang="en">
        <seg>Hello World</seg>
      </tuv>
      <tuv xml:lang="zh">
        <seg>你好世界</seg>
      </tuv>
    </tu>
  </body>
</tmx>"""

SDL_XLIFF = """<?xml version="1.0" encoding="utf-8"?>
<xliff xmlns:sdl="http://sdl.com/FileTypes/SdlXliff/1.0" xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2" sdl:version="1.0">
  <file original="test.xlf" datatype="x-sdlfilterframework2" source-language="en-US" target-language="zh-HK">
    <header>
      <sdl:seg-defs>
        <sdl:seg id="1" conf="Draft" origin="source"/>
      </sdl:seg-defs>
    </header>
    <body>
      <trans-unit id="1">
        <source>Hello World</source>
        <seg-source>
          <mrk mid="0" mtype="seg">Hello World</mrk>
        </seg-source>
        <target>
          <mrk mid="0" mtype="seg">你好世界</mrk>
        </target>
      </trans-unit>
      <trans-unit id="2">
        <source>Welcome to the application</source>
        <seg-source>
          <mrk mid="0" mtype="seg">Welcome to the application</mrk>
        </seg-source>
        <target>
          <mrk mid="0" mtype="seg">歡迎使用應用程式</mrk>
        </target>
      </trans-unit>
    </body>
  </file>
</xliff>"""
