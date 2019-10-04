# SteamUploader for RenPy

This tool is meant to make it easier for devs to upload their RenPy games
and their DLCs into Steam (using SteamPipe, Steam's own tool). It is designed
to run as a RenPy game within RenPy Launcher.

I have tested this on Windows and OSX, but not Linux.

HOW TO USE:

1. Clone this repo and place it alongside your other RenPy games
2. Using RenPy Launcher, run SteamUploader as if it's a RenPy game
3. The UI should provide hints on the next steps:

    - Step 1: If you haven't done so, build your game using RenPy Launcher's
      'Build Distributions' with '...for Markets' option selected
    - Step 2: If you have any DLCs, put it into a folder alongside your build zip file
    (the build file name should end with '-market.zip'), and append the DLC folder
    name with '-dlc'
    - Step 3: Get your App ID and Depot ID(s) from Steam and enter them into
    SteamUploader and press Upload
    - Step 4: On your first time running, you should get a request for Steam Guard code.
    Check your email and enter that code
    - Step 5: It should be done! Check Steam to see if your upload was successful.
