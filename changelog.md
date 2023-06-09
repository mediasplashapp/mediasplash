# MediaSplash changelog

## version 1.3.0
### features
- Last-watched track and it's position are remembered automatically.
- when a chapter starts, It will now be announced by the screen reader if available.
- the window title is now updated with the currently playing chapter title as well as the title of the playing file.

### changes:
- Maximum volume is now 200%

### fixes:
- Jump to dialog now works correctly.

## Version 1.2.0
### Changes
- Moves to the mpv library for media handling instead of vlc, This also removes the requirement of having an external program installed with this.
### Fixes
- Fixed changing subtitles wouldn't change it visually.
- Fixes Auto subtitle loading would not load some subtitles if they had 2 or more extensions.
### Features
- You can now select audio devices, They save at program exit.

## Version 1.1.0:
### features
- The program can now check for updates, it can be done from the help menu in the menu bar.
- added the ability to quickly go to a media position, press CTRL + J while focused on the media control to activate the go to dialog. As an example, typing 5.30 will instantly move the media track position to 5 minutes and 30 seconds.
## bug fixes:
- Fixed a keyboard issue that caused the video and subtitle to not be visable on the screen.
- Fixes a bug with subtitles if the media  had no default value videos wouldn't function.
