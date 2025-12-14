# Dexsplitter

This repo contains splits and splitters for speedrunning the game Ambidextro.

## LiveSplit autosplitter

A LiveSplit autosplitter for Ambidextro and splits for running the Any% category can be found in the `LiveSplit` folder.

You can download the splits for the Any% category [here](https://github.com/FeldrinH/Dexsplitter/blob/main/LiveSplit/Ambidextro%20-%20Any%25.lss) (click the download button in the top right corner). The autosplitter will be automatically downloaded when opening the splits in LiveSplit. You can enable it by opening the 'Edit Splits' window and clicking the button labeled 'Activate'.

The autosplitter has the following features:

* Automatically splits at the end of a level (before the level transition, if there is one).
* Automatically starts run when speedrun timer starts ticking.
* Automatically resets run when (re)starting level 0.

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