@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
##  A Clear Map of Skyrim and Other Worlds  ##
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
###############  by DoubleYou  ###############
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

----------------------------------------------
%%%%%%%%%%%%%%%  Description  %%%%%%%%%%%%%%%%
----------------------------------------------

A Clear Map of Skyrim and Other Worlds enhances the map to make it more useful so you can't get lost. It modifies the map's weather to allow it to be more visible and responsive to the time of day. Missing maps to other worlds in the game have also been added, including the most confusing locations of Blackreach, the Forgotten Vale, and the Soul Cairn, as well as Skuldafn and Sovngarde for kicks and giggles. Furthermore, it includes custom rules to be used with DynDOLOD, which allows it to have missing elements added to the map that previously could not be seen. The results are impressive, to say the least.

----------------------------------------------
%%%%%%%%%%%%%%%%%  Summary  %%%%%%%%%%%%%%%%%%
----------------------------------------------

A Clear Map of Skyrim and Other Worlds enhances the map to make it more useful so you can't get lost. And it looks AMAZING!

TL;DR

* Roads
* Support for other land mods including Beyond Reach, Bruma, Falskaar, Midwood Isle, Vominheim, and Wyrmstooth.
* It modifies the map's weather to enhance visibility and responsiveness to the time of day. 
* It fixes z-fighting between terrain and water.
* Map markers too close? You can actually select the right one now! 
* Missing maps to other worlds in the game have also been added, including the most confusing locations of Blackreach, the Forgotten Vale, and the Soul Cairn, as well as Skuldafn and Sovngarde for kicks and giggles.
* Custom rules to be used with DynDOLOD, which allows it to have missing elements added to the map that previously could not be seen. The results are impressive, to say the least.

----------------------------------------------
%%%%%%%%  Unlocks Missing World Maps  %%%%%%%%
----------------------------------------------

Let's be honest. How many times have you visited the Soul Cairn? Blackreach? The Forgotten Vale? Not nearly enough times, at least for most of us, not to get turned around and not be able to tell where we've been or where we're going. Just think. If only we had a map!

The following worlds are currently added to the map that otherwise would be missing:

﻿* Blackreach
﻿* The Forgotten Vale
﻿* The Soul Cairn
* Skuldafn
﻿* Sovngarde

I recommend supplementing these maps with the amazing Atlas Map Markers mod.

----------------------------------------------
%%%%%%%%%%%%  Map Weather Tweaks  %%%%%%%%%%%%
----------------------------------------------

So... it's the dead of night. You just crawled out of a draugr crypt with all your precious treasures. You want to go home.

You open your map, and ugh! You can't see! The moon may be shining bright, but your map looks as dark as Alduin's hide! Why does the map always have to be experiencing bad weather?

The following weather tweaks have been applied to improve visibility of the map:

* Fog has been removed from the map.
* Weather has been completely remodeled to provide greater visibility and realism.
* Optionally removes clouds from the map.

----------------------------------------------
%%%%%%%%%%%%%  Map Camera Fixes  %%%%%%%%%%%%%
----------------------------------------------

Ever visit Mount Kilkreath? Talk with Meridia? Get taken up into the clouds? Isn't that an amazing way to view Skyrim?

Ever wish you could just tilt up and down, rotate a full turn, do backflips in mid-air? (Ok, that last one's a joke).

Ever want to fast travel to the Thieve's Guild's secret entrance, but fat click on the main city of Riften instead? And then after getting to Riften, you try to fast travel to Markarth, but the city of Markarth is just like a centimeter too far away for you to reach its map marker?

Enough questions!

The following map camera fixes are utilized:

* Zooming out and in has been increased to more appropriate levels.
* You can now rotate the camera a full turn (360 degrees). You must hold right-click and turn to rotate.
* Pitch can be adjusted a full 90 degrees. You must hold right-click and tilt up and down to adjust.
* Map boundaries have been expanded, removing the problem of not being able to reach from one side of the map to the other.
* Map markers are slightly less magnetic, meaning if you have two map markers that are close together, it is much easier to select the correct one.
* Z-fighting between terrain and water and other objects has been largely eliminated.

----------------------------------------------
%%%%%%%%%%%%%%%%%%  Roads  %%%%%%%%%%%%%%%%%%%
----------------------------------------------
﻿
Roads are added to the Terrain LOD textures via included ACMOS Road Generator tool. Now you don't need to exploit the game by jumping up the mountains with your horse just to figure out how to get to where you're going!

----------------------------------------------
%%%%%%%%%%%%%%  DynDOLOD Rules  %%%%%%%%%%%%%%
----------------------------------------------

"Have you seen that Shrine of Azura? I'd sacrifice my firstborn to see it!"

DynDOLOD rules are included to generate high quality Map LOD as a fake object LOD 32 level BTO. Basically, this means that all the objects it adds or takes away from the map will be impact the map only, and not actually affect the performance of the game. This feature requires using the latest DynDOLOD 3 alpha and setting Level32=1 in \Edit Scripts\DynDOLOD\DynDOLOD_SSE.ini.

This is really one of my favorite features of this mod, and ultimately what started it all in the first place. However, I understand many users have difficulty using these advanced tools, so this step is optional, but is nevertheless highly recommended, and required to get the intricate details as displayed on these pictures.

----------------------------------------------
%%%%%%%%  Installation Instructions  %%%%%%%%%
----------------------------------------------

1. Install the FOMOD installer like any other mod using your favorite mod manager.
   Warning: Do NOT install the "With DynDOLOD LOD32" option if you are not going to use DynDOLOD 3! This will cause significant issues with LODS otherwise!
2. Follow the Recommended xLODGen Instructions, Road Generation Instructions, and DynDOLOD 3 Instructions for best results.

----------------------------------------------
%%%%%  Recommended xLODGen Instructions  %%%%%
----------------------------------------------

For most users, this process will take about a half hour to an hour. Seasons of Skyrim users can expect it to take 5x that amount, since it generates 5x the amount of files.

1. If you run Synthesis, make sure you run it first.
2. If you are using xLODGen Resource - SSE Terrain Tamriel mod, make sure it is enabled.
3. If you are using Cathedral Landscapes, make sure you install the LODGEN Textures for v3 file. This file tweaks the lod files to make better looking terrain lod output as generated from xLODGen, and it may be disabled following xLODGen generation.
4. If you haven't sorted your load order yet, do so now.
5. If using Seasons of Skyrim, launch the game to the main menu so it can generate its configuration files and exit.
6. Run xLODGen and select all worldspaces.
7. Ensure that ONLY the Terrain LOD box is ticked in the right pane if all you want to generate is Terrain LOD. If you want to use the other features, that is your perogative.
8. If you are using Seasons of Skyrim, ensure that the Seasons box is ticked and all seasons are ticked in the dropdown.
9. Use whatever settings you normally use for LOD4, LOD8, and LOD16.
10. Recommended settings for LOD32 (the map):
   X Build Meshes      Quality 0     Max Vertices 32767     Optimize Unseen 550
   X Build Diffuse     Size 2048     Format BC7 Max         □ MipMap
                       Brightness, Contrast, and Gamma settings may vary with your landscape textures, but typically should be left alone.
					   Cathedral Landscapes users may find increasing gamma to 1.25 to be beneficial.
   X Build Normal      Size 2048     Format BC7 Max         □ MipMap     □ Raise steepness
   X Bake normal-maps  Vertex Color Intensity 1.00          Default size: Diffuse 128 Normal 128
11. Click [Generate] to run the process, which make take a between 20 minutes and 3 hours, depending on the PC and whether or not you are using Seasons of Skyrim.
12. Once the "LOD generation complete" message has appeared, close xLODGen
13. If using the LODGEN Textures for v3 file from Cathedral Landscapes, it may be disabled now.
14. Proceed to Road Generation Instructions prior to installing the xLODGen output.

----------------------------------------------
%%%%%%%  Road Generation Instructions  %%%%%%%
----------------------------------------------

For most users, this process should take less than 5 minutes. It could take longer dependent on mods/hardware. If it appears to be not responding, leave it be, as it most likely is still working.

1. Extract the ACMOS Road Generator tool anywhere and run.
2. Browse to where you generated your xLODGen Output.
   a. If not using xLODGen, browse to the game Data folder, and as long as the terrain LOD files are loose, it will work. If they are not loose, you will need to extract them first. The required files are in the path textures\terrain
3. By default, the Output Path is set to the same folder, and it will overwrite the files. If desired, you can specify an alternate output path.
4. Click Generate.
5. Wait until it says "All Done!" and then close.
6. Install the output if you haven't already done so.
7. Profit.

----------------------------------------------
%%%%%%%%%%  DynDOLOD 3 Instructions  %%%%%%%%%%%
----------------------------------------------

1. Navigate to the \Edit Scripts\DynDOLOD\DynDOLOD_SSE.ini file in your DynDOLOD install and set Expert=1 and Level32=1.
2. Sort with LOOT.
3. Launch DynDOLOD.
4. Ensure that all worldspaces are ticked.
5. If using Candles and FXGlow, tick them now.
6. Click on any of the presets (Low/Medium/High). This step is required to load my custom rules!
7. Modify the tree rule by double clicking it. Under the LOD Level 32 dropdown, select Billboard6.
8. Modify the \ rule by double clicking it. Under the LOD Level 32 dropdown, select Level0.
9. Ensure that Object LOD is ticked.
10. If you want trees to show on the map, you must untick Tree LOD and tick Ultra instead.
11. It is recommended to generate Dynamic LOD to prevent stuck object LOD bugs in game. Plus it makes everything prettier.
12. It is recommended to tick Occlusion data to generate the proper data to prevent terrain LOD holes in-game.
13. If using Seasons of Skyrim, ensure that all the seasons are enabled, including Default.
14. Tweak the other settings to your liking.
15. Click OK and wait for maybe a half hour, but this is highly dependent upon your settings/hardware/mods/etc. Seasons of Skyrim users may want to leave it run overnight.
11. If generation is successful, select the Save & Zip & Exit option to zip up the output into an easily installable zip file that can be installed like any other mod using your mod manager.
12. Install the output
13. Sort with LOOT.
14. Profit.

----------------------------------------------
%%%%%%%%%%%  Compatibility Notes  %%%%%%%%%%%%
----------------------------------------------

* The plugin MUST be loaded at or very near the bottom of your load order. Don't worry. It will not overwrite any of your fancy mod-added armors or spells. It edits the base Worldspace records, so it actually is compatible with basically everything, but just about every mod that edits something in a worldspace can effectively overwrite my map changes.
* Terrain LOD as generated by xLODGen﻿ (highly recommended) or as otherwise used by the game must be in loose file form for road generation (see road generation instructions).
* Incompatible with other map mods modifying the same things this mod does, obviously.