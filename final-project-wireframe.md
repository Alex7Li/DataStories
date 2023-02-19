[home page](https://alex7li.github.io/DataStories/)
[prev](https://alex7li.github.io/DataStories/final-project-outline) 


[home page](https://alex7li.github.io/DataStories/)
[prev](https://alex7li.github.io/DataStories/final-project-outline)
[next](https://alex7li.github.io/DataStories/final-project-final)

# Final Project Wireframe

## Introduction Wireframes

I began with the introduction, since the data for those charts was quite easy to process, and I could get them with a few google searches. I think there is a pretty smooth introduction even for people who are more unfamiliar with competitive programming.

<div class="flourish-embed flourish-chart" data-src="visualisation/12778058"><script src="https://public.flourish.studio/resources/embed.js"></script></div>

We start with giving context along with something most people are familiar with: techinical interviews.

<div class="flourish-embed flourish-hierarchy" data-src="visualisation/12778073"><script src="https://public.flourish.studio/resources/embed.js"></script></div>

Then we dive into topics! This treemap is a lot easier to look at than the purplce circle in the project outline.

<div class="flourish-embed flourish-chart" data-src="visualisation/12777760"><script src="https://public.flourish.studio/resources/embed.js"></script></div>

And we finish off with a diagram showing growth. It's interesting to note that growth of the number of users on a platform, which I was originally planning to show is a wa~ay more exponential line than the metric of number of competitiors, but I decided that this metric is more important. I don't need to wow the viewer with a quickly increasing curve, anyways.

## Data analysis Wireframes

Next, I started the hard work of trying to do data analysis. The thing that makes this part challenging is that my data is not formatted in a way that is possible to visualize naively: I have thousands of csv files, representing the submission history and rating changes for individual users. But I need to do a meta-analysis to get valuable insights. In order to do this, I had to write a bunch of python code (it's ~600 lines already to process the data). And because the dataset is quite large, it takes about 20 minutes just to read everything in RAM, and another 30 for analysis.

<div class="flourish-embed flourish-chart" data-src="visualisation/12779798"><script src="https://public.flourish.studio/resources/embed.js"></script></div>

The first chart was not to hard to get from the data, I simply counted the number of submissions and current rating of each user. Though, I wish it was the number of solved problems instead of the number of submissions now, I don't want to re-run everything. One big challege with this chart was getting the percentage intervals to work. Originally, I wanted to use tableau, which does have the percentage feature. However, you need to do a different chart for each line, or at most 2 lines for one chart with dual-axis. There were some tutorials that showed how to do unlimited lines on one chart, but they didn't work for me so I think there was some issue with the web version of tableau. (The desktop version doesn't work for me as I have linux.)

I still wanted more, though. To break down the time series data I had into more managable units of information, I tried to break events into time periods of change. For every year of data on a specific user, if that user was active in that year, I collect statistics about what happened in that year for that user: the number of submissions that they've made, the rating that they started and ended at, the number of problems that they've solved, the number of problems that they've submitted but not solved, and their average time to solve the first problem. For the last one, I needed to spend few days to create a whole new dataset, but it wasn't too bad because I had existing infrastructure from the first dataset. The time to solve the first problem is notable since this is the time to solve the easy problem that everyone can tell the answer to at a glance, and thus it's more of a metric of coding speed than the final result, which also has information about the 'solving speed'.

> The lazy chart would be to show the submission history for a single user. But [this is already on the frontpage of every profile](https://codeforces.com/profile/ecnerwala), and people are familiar with them. In fact, people are so familiar with this graph and it's color scheme that usually, rather than saying "I want to be a <span style="color:purple;">candidate master</span>", they say "I want to be purple". Or instead of "<span style="color:blue;">expert</span>", they say "blue". Funnily enough, many even say
"<span style="color:black;">n</span><span style="color:red;">utella</span>" instead of legendary grandmaster. As you might expect, there is only one reasonable choice for the color scheme in many of the following charts!

For the next chart, I wanted to try and get some idea of individual user differences. I made a quite confusing chart which plotted statistics for certain users over time. For this chart, I just selected a few users who displayed high activity level over a period of several years. For each of these users, I accumulated statisitics on the average number of correct vs incorrect problems they had that year, as well as their median first solve time in all contests that year. I was hoping to see if one of those variables influenced how fast they grow.

<div class="flourish-embed flourish-scatter" data-src="visualisation/12778453"><script src="https://public.flourish.studio/resources/embed.js"></script></div>

Unfortunately, I didn't get any insights out of these user stories. Perhaps staring at more data in simpler charts will be more insightful than trying to get information from just a few users! Especially in a setting as noisy as this one.

And indeed, I was much happier with the charts that just plot rating change against a single variable. I made these and thought that they were nice.

<div class="flourish-embed flourish-scatter" data-src="visualisation/12680245"><script src="https://public.flourish.studio/resources/embed.js"></script></div>
<div class="flourish-embed flourish-scatter" data-src="visualisation/12716075"><script src="https://public.flourish.studio/resources/embed.js"></script></div>

These charts do have a lot to unpack in them, to be sure. However, by keeping the format consistent between them, it's not hard to get the second one after you get the first one.

I saw correlation in both, and I wasn't able to say which one was more impactful. It looked like the data was less spread out for the hard problems, though, and I wasn't sure if it was just the graph or not. I decided to write another script to get the r value because flourish wouldn't do it for me. The results script proved that the hard problems were more correlated with succcess than the easy problems. (r^2=.3 vs r^2=.4)

But then, easy problems are easier to solve. So even if 10 easy problems only give as much benefit as 1 hard problem, maybe it's still beneficial to solve a bunch of easy problems. I used a 2-variable linear model to compare the benefits, and this gave the most interesting result and valuable insight of the entire experiment: easy problems are not only less effective than hard problems, but they correlate negatively for success after taking hard ones into account. This alone makes the effort for this project worthwhile, since it allows a lot of people to save a lot of time they might waste on easy problems otherwise. Also it has some interesting implications for things outside of competitive programming if this pattern holds...
To generalize further than I stastically should, taking classes that are easy for you and learning things you already know is not better than doing nothing, despite the notion that you are just 'improving your fundamentals'.

Because these statistics are so important to the story, and because my audience is pretty good techinically, I include them as callouts in the final story. I know it's strange to have correlation coefficients and linear function coefficients as a data visualization but this is the thing that tells a compelling story.

## Storyboards

Introduction: By including imagery of real competitions, we give unfamiliar people an idea of what the sport looks like.

Anaysis: Idk let's just use random 'analysis' images

Call to action: First it's a picture of text reinforcing the message, then we transition into the 'victory' image from I think the winners of last year's ICPC world finals. Maybe the reader will feel like they will be able to get there. Probablly not, statistically speaking.

[View the website preview!](https://preview.shorthand.com/ePD6rBoLNtleDV6i)


## User Research

There is only one target persona: someone who is currently doing competitive programming, and who wants to get better.

Though, to make sure the audience can be more broad, the introduction exists.

Questions to ask in the interview:

After reading the storyboard, do you feel that anything is missing?

What chart was the hardest to comprehend? Why?

Did you agree with the conclusions of the storyboard?

Looking through the storyboard, did any section seem to not fit in with the others?

What other charts/analysis would you like to see?



### Continue

[next](https://alex7li.github.io/DataStories/final-project-final)
