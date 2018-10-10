# Zane's CFB Analytics Projects

This repo contains several python notebooks and other files that I'm using in college football analytics projects.

## Current Project: Adjusted Per-Drive Metrics
My current project aims to construct new metrics to more accurately measure offensive and defensive efficiency by adjusting points-per-drive stats for both field position and opponent using an SRS-style method. So far, I've calculated a regression line/equation showing the expected PPD for an average offense against an average defense. It works out to approximately: expected points = -0.05(drive start distance) + 5.4.

![image caption](https://raw.githubusercontent.com/zaneddennis/CFB-Analytics/master/AveragePPD/bestfit.png)

My next steps will be to use this equation to calculate how far above/below expectation every given drive is, then use an algorithm similar to Simple Rating System to normalize by opponent. The result will be an adjusted PPD for every team's offense and defense.

