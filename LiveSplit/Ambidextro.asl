// Copyright (c) 2025 Juhan Oskar Hennoste (FeldrinH)
// Licensed under MIT License (https://spdx.org/licenses/MIT.html)

// NB: The location of this file in the repository must not change. This location is linked to from https://github.com/LiveSplit/LiveSplit.AutoSplitters.

state("Ambidextro")
{
    // Internal time of speedrun timer. Updates every frame while in game. Zero while in menus. 
    double speedrunTime : 0x04FF5AA0, 0x2B0, 0x150, 0x18, 0x68, 0x28, 0x158;

    // Updates at end of level. Has next level index during level transition.
    long level : 0x04FF5AA0, 0x288, 0x0, 0x68, 0x28, 0x140;
    
    // Updates at start of level. Has previous level index during level transition.
    long levelLoaded : 0x04FF5AA0, 0x288, 0x0, 0x68, 0x28, 0x158;

    // TODO: level and levelLoaded are broken for TAS, probably because of the patching that TAS does.
}

startup
{
    // refreshRate = 2;
}

gameTime
{
    // Note: We use this conversion instead of FromSeconds so that we can match the rounding behavior of the in-game timer.
    return TimeSpan.FromMilliseconds((long)(current.speedrunTime * 1000.0));
}

isLoading
{
    return true;
}

start
{
    return current.speedrunTime > 0.0;
}

reset
{
    // TODO: Do we need an extra check to avoid resetting when returning to main menu?
    // Currently this is prevented by the fact that level number is preserved when returning to main menu, but should we rely on this?
    return current.level == 0 && current.speedrunTime == 0.0;
}

split
{
    if (current.speedrunTime < 0.1)
    {
        // Avoid splitting immediately at start of run.
        return;
    }
    // TODO: Does final level need special handling?
    return current.level != old.level;
}