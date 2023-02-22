[home page](https://alex7li.github.io/DataStories/) | [prev: final project wireframe](https://alex7li.github.io/DataStories/final-project-wireframe) 

# Final Project

# Summary of the work

## Features Implemented since part 2

Some of the user features were very simple to implement.
- Make the text refering to a question mark refer to an information icon.
- Separate out pupil and newbie category
- Remove colors from the treemap
- Add discussion on limitations due to practice on other platforms.

Some features took a bit more time.

- Modify the rating vs n submissions to have an x-axis of number of correct submissions, and smooth out the lines.

This was just a matter of running the script and counting the correct things. To smooth the lines, I applied scipy's savgol filter function to the values of the graph.

- Add subtitles to remove text from the website

I tried to minimize the amount of text that was surrounding the graph and put more inside of them. There is a lot of important context that needs to stay outside, but i got rid of a few paragraphs.

- Modify some of the background to have more of a coding feel

I added a picture of some code to the background. I found real code from a programming competition for realism, but I had to look around for a while in order to find some code that was badly written enough that, when you look at it, you immediately want to give up and not think about it instead of trying to understand the meaning. Actually, it wasn't that hard, many people write really unreadable code in CP.

- Split the linear model into all rating categories.

I did this, but the coefficients became pretty random. Maybe there were too many variables? I wasn't impressed by it, so will not include in the project.

- Take the last chart and either make a grid of correlation between variables instead of the existing chart, or change the title to be more clear

I tried making a grid of correlation values here. However, I don't know if it's that good since it's a bit confusing and there isn't that much information, it is fine to explain in text. I think I will stick with the existing chart.

<div class="flourish-embed flourish-heatmap" data-src="visualisation/12829168"><script src="https://public.flourish.studio/resources/embed.js"></script></div>

## Audience

The target audience is people who are interested in improving their skills at competitive programming and practicing in the future.

Three personas:

1) Prospective interest, someone who has practiced for job interviews and is curious about entering programming contests.

2) Starting competitors, someone who has started to practice programming contests and wants to know how to improve.

3) Stuck competitors, who have been practicing for a while but have not seen development recently. They want to know what they can do in order to continue to improve.

For the first persona, the context statistics at the start of the page are meant to be helpful. They can see how the popularity of contests compares to the popularity of interview websites, and they will see that there is a lot of overlap in the topic areas. This is the persona that will get the most out of the treemap diagram.

The second persona is really going to be interested in some of the later analysis.

The third persona will want to see where they are and if they are really falling behind or just imagining it. To help with that, I added a line explaining how to find yourself on the graph, so they can measure their progress. This persona will also be interested in the analysis of easy vs hard problems. To help account for the differences in the first and second persona and make results feel at least a little bit more applicable, I separated the users into groups distinguished by their current rating.


## Final project website

[Final Project Website](https://carnegiemellon.shorthandstories.com/competitive-programming-talent-vs-tenacity/index.html)
