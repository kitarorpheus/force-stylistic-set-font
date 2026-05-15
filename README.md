# Force Stylistic Set Font

A browser-based tool that forces OpenType stylistic alternates into font glyphs.

## Features

- Apply stylistic sets permanently
- Browser-only processing
- No server upload

## Demo

https://teal-kheer-8466ef.netlify.app/

## Tech

- Pyodide
- fontTools

## Limitations

- Ligature substitutions are not supported
- Some fonts may not contain GSUB tables
- cmap compatibility differs between applications
- Font merging may break width consistency
- Mainly tested on Windows environments and some fonts
 
## License

This tool does not modify the original font license.

Please follow the license terms of the original font.
