[home page](https://alex7li.github.io/DataStories/) | [prev: final project wireframe](https://alex7li.github.io/DataStories/final-project-wireframe) 

# Final Project

# Summary of the work

## Features Implemented since part 2 from interviews

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

## Features implemented based on grader feedback of part 2

First, I tried to add a story of a contestant named Andrew. However, something about trying to follow a user through the analysis just felt strange to me in this context. Every time I wrote the name andrew, it just felt like I was introducing an artificial person and trying to force an unnatrual story. It felt more natural to write a story that followed the journey of [the reader].

Next, I added context for readers unfamiliar with comp programming by providing an example rating and a graph of the rating distribution. This along with a paragraph about percentiles makes it more clear what a rating of 2100 is, and everyone knows what we are talking about. It does take up a bunch of space, but the problem is fun so I think it's worth it. In fact, the graph is not my own but the color scheme is consistent and it works well so there is no reason to redesign it.

Finally, I checked the sources for all the images and put citations in the bottom (other than the free images from shorthand, which includes the neccessary citation.)

## Bonus feature: Don't crash on mobile

When giving some user interviews, I learned that my site crashes on mobile. Why? Because the flourish charts are massive.

So, I subsampled the data to be 1000 points per grouping. I think the resulting charts don't look as good, but it does not crash on my phone and loads a bit faster, so it's a worthy tradeoff, since I plan to add the site to a blog article later.

## Audience

The target audience is people who are interested in improving their skills at competitive programming and practicing in the future.

Three personas:

1) Prospective interest, someone who has practiced for job interviews and is curious about entering programming contests.

2) Starting competitors, someone who has started to practice programming contests and wants to know how to improve.

3) Stuck competitors, who have been practicing for a while but have not seen development recently. They want to know what they can do in order to continue to improve.

For the first persona, the context statistics at the start of the page are meant to be helpful. They can see how the popularity of contests compares to the popularity of interview websites, and they will see that there is a lot of overlap in the topic areas. This is the persona that will get the most out of the treemap diagram.

The second persona is really going to be interested in some of the later analysis. They might wonder how much effort it takes in total to get very good, so I tried to estimate it.

The third persona will want to see where they are and if they are really falling behind or just imagining it. To help with that, I added a line explaining how to find yourself on the graph, so they can measure their progress. This persona will also be interested in the analysis of easy vs hard problems. To help account for the differences in the first and second persona and make results feel at least a little bit more applicable, I separated the users into groups distinguished by their current rating.



## Final project website

[Final Project Website](https://carnegiemellon.shorthandstories.com/competitive-programming-talent-vs-tenacity/index.html)

### Script

Competitive programming is the logical extreme of a programming interview, where contestants need to solve super hard problems in extremely short timeframes. Millions of people have tried it, and tens of thousands show up to the biggest competitions.

There's a large span of problem topics, and to measure your skill there is a rating system like in chess, with 2000 being extremely impressive. As you practice more, you will improve: there is no clear indicator that there exists a level at which you cannot get any better, so long as you keep pouring more time into it.

But it's not just about the number of problems solved: it's also about the diffculty of those problems. We tried to predict the rating growth from the number of easy problems and the number of hard problems solved. A 2 variable linear model revelealed that solving a hard problem improves your rating by 1, but solving more easy problems is a negative predictor of success.

This holds true for both beginners and experts in our datasets: solving problems that are easy for you does not actually seem to make you get better.

So to conclude, now is a great time to get started in competitions, and you can always improve so long as you keep challenging yourself.
