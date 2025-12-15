# Dexsplitter

This repo contains splits and splitters for speedrunning the game Ambidextro.

## LiveSplit autosplitter

A LiveSplit autosplitter for Ambidextro can be found in the `LiveSplit` folder. This autosplitter is registered with LiveSplit, so it is installed automatically when you select Ambidextro as the game for your splits and click 'Activate'.

You can download splits for the Any% category on [speedrun.com](https://www.speedrun.com/Ambidextro/resources/55lo9).

The autosplitter has the following features:

* Reads in-game speedrun timer for the most accurate time (make sure that LiveSplit is set to use game time).
* Automatically splits at the end of a level (before the level transition, if there is one).
* Automatically starts run when speedrun timer starts ticking.
* Automatically resets run when (re)starting level 0.

Note that the autosplitter is tested with Ambidextro 1.2.3 on Windows. Other versions of the game may work and support can be added on demand if they don't. Other operating systems do not work and support is currently not planned.

## Video splitter

A Python script to extract split times from a speedrun video can be found in the `videosplitter` folder.

### Installation

1. Install Python 3 if you don't have it already.
1. Download this repo and open the `videosplitter` folder.
2. Install dependencies with `pip install -r requirements.txt` or equivalent.

### Usage

```
$ python videosplitter.py speedrun_video.mp4
```
