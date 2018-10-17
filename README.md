# Zane's CFB Analytics Projects

This repo contains several python notebooks and other files that I'm using in college football analytics projects.

## Current Project: Adjusted Per-Drive Metrics
For decades, the most common statistics used to judge the quality of individual offenses and defenses were yards/game and points/game. While these numbers are fairly adequate surrogate metrics in most cases, in today's world of radically differing paces of play, they often fall short of properly grading any given offensive or defensive performance. As the length of a football game is determined by a game clock rather than by a set number of chances, faster-paced and passing-based offenses benefit unfairly in per-game stats relative to slower-paced or running-based offenses.

So how, then, should we define the quality of an offense? The goal of an offense is to score as many points as possible every time they have the ball (and the reverse for a defense). This translates to points-per-drive. But, as the legendary Phyllis from Mulga once pointed out, some teams "ain't played nobody" and as a result have inflated statistics. Further, some teams are much stronger on one side of the ball than the other, as has been the case at my alma mater Baylor for about the last decade. A team with a dreadful offensive unit often leaves its defense defending short fields, drastically affecting its ability to achieve its goal of preventing points. The chart below shows just how drastically field position affects expected points per drive among FBS teams.

![image caption](https://raw.githubusercontent.com/zaneddennis/CFB-Analytics/master/AveragePPD/bestfit.png)

To control for these factors, I took every drive from FBS vs FBS games this season (excluding those ending a half or game) and compared the points scored to the regression line of the graph to compute the Points Relative to Expectation. For example, a drive beginning at the offense's own 20 yard line (i.e. a start distance of 80 yards) would have an expected value of about 1.8 points. If the offense then scores a touchdown (7 points), they are awarded 5.2 PRE. A made FG would give 1.2 PRE, and no points would be -1.8 PRE.

Teams' initial offensive and defensive adjusted points per drive (aOPPD and aDPPD) are computed by taking the average PRE of all of that unit's possessions (a positive rating is good for offenses and bad for defenses). Then, each drive's PRE is used to compute an opponent-adjusted PRE for both the offense the the defense by subtracting the relevant opponent's rating from the base PRE. The base offensive and defensive ratings are recalculated based on the opponent-adjusted PREs. This process is repeated until the changes in team ratings are negligible (a similar formula to Sports-Reference's Simple Rating System).

What I hope to accomplish with this stat is a metric with the robustness of "advanced" stats while still being as understandable and approachable for the average fan as a typical box score stat. This isn't a machine-learning powered predictor of future performance; it's a simple measure of how well an offense or defense has done its job so far.
