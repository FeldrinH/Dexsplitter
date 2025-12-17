// Copyright (c) 2025 Juhan Oskar Hennoste (FeldrinH)
// Licensed under MIT License (https://spdx.org/licenses/MIT.html)

// NB: The location of this file in the repository must not change. This location is linked to from https://github.com/LiveSplit/LiveSplit.AutoSplitters.

state("Ambidextro")
{
    // Internal time of speedrun timer. Updates every frame while in game. Zero while in menus. 
    double speedrunTime : 0x04FF5AA0, 0x2B0, 0x150, 0x18, 0x68, 0x28, 0x158;

    // True if playing in story mode. False if playing individual levels.
    bool inStoryMode : 0x04FF5AA0, 0x2B0, 0x150, 0x18, 0x68, 0x28, 0x170;

    // True if game has been completed. Set to true at end of final level.
    bool gameEnded : 0x04FF5AA0, 0x2B0, 0x150, 0x18, 0x68, 0x28, 0x188;

    // Updates at end of level. Has next level index during level transition.
    long level : 0x04FF5AA0, 0x288, 0x0, 0x68, 0x28, 0x140;
    
    // Updates at start of level. Has previous level index during level transition.
    // long levelLoaded : 0x04FF5AA0, 0x288, 0x0, 0x68, 0x28, 0x158;

    // TODO: level and levelLoaded are broken for TAS, probably because of the patching that TAS does.
}

startup
{
    // Based on https://github.com/ItsMaximum/autosplitters/blob/master/rb1improved.asl
    if (timer.CurrentTimingMethod != TimingMethod.GameTime)
    {
        DialogResult timingPromptResult = MessageBox.Show(
            "This game uses the in-game timer (Game Time) as the main timing method.\n" +
            "Would you like to switch the timing method to Game Time?",
            "LiveSplit | Ambidextro",
            MessageBoxButtons.YesNo, MessageBoxIcon.Question
        );
        if (timingPromptResult == DialogResult.Yes)
        {
            timer.CurrentTimingMethod = TimingMethod.GameTime;
        }
    }
}

gameTime
{
    if (!current.inStoryMode)
    {
        // Timer can sometimes start ticking unexpectedly outside story mode. Default to zero to avoid issues.
        return TimeSpan.Zero;
    }
    // Note: We use this conversion instead of FromSeconds so that we can match the rounding behavior of the in-game timer.
    return TimeSpan.FromMilliseconds((long)(current.speedrunTime * 1000.0));
}

isLoading
{
    return true;
}

start
{
    // Start is triggered after time has gone from zero to positive. This ensures that start is triggered after reset.
    return current.inStoryMode && current.level == 0 && old.speedrunTime > 0.0 && current.speedrunTime > 0.0 && current.speedrunTime <= 0.5;
}

reset
{
    // Reset is triggered when time goes from zero to positive. This ensures that reset is not triggered in main menu where time is zero by default.
    return current.inStoryMode && current.level == 0 && old.speedrunTime == 0.0 && current.speedrunTime > 0.0 && current.speedrunTime <= 0.5;
}

split
{
    if (!current.inStoryMode || current.speedrunTime <= 0.2)
    {
        // Avoid splitting when playing outside story mode and when run has just started.
        return;
    }
    return current.level != old.level || (current.level == 101 && current.gameEnded && !old.gameEnded);
}