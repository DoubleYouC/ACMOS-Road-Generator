# ACMOS-Road-Generator
This tool adds the roads using the png files in the "roads" directory to overlay onto the terrain LOD for Skyrim Special Edition.

Requires Python 3 with Pillow. I use version 3.8 to compile to ensure compatibility with Windows 7, but it can be compiled and used with the latest version.

Also requires texconv.exe from DirectXTex: https://github.com/microsoft/DirectXTex. It should be placed in subfolder called texconv, or modify code to point to your custom path.

## CLI arguments
The follwing CLI arguments are available.

| Parameter                  | Description                                                                  | Example                                                          |
|----------------------------|------------------------------------------------------------------------------|------------------------------------------------------------------|
| -zip                       | Zips the output. If not using this or `-autorun`, you will be prompted.      | `-zip`                                                           |
| -l                         | LOD Path. Relative paths are supported.                                      | `-l:"C:\Path to LOD\xLODGen Output"` or `-l:"./xLODGen Output"`  |
| -o                         | Output Path. Relative paths are supported.                                   | `-o:"C:\Skyrim Modding\ACMOS Output"` or `-o:"./ACMOS Output"`   |
| -t                         | Roads Type                                                                   | `-t:"Roads"` or `-t:"Paths Only"`                                |
| -autorun                   | Automatically clicks the "Generate" button for you.                          | `-autorun`                                                       |
| -clear-output-on-generate  | ***Deletes*** the folder selected as Output Path, upon starting generation.  | `-clear-output-on-generate`                                      |

CC BY-NC-SA
