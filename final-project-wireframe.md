[home page](https://alex7li.github.io/DataStories/) |
[prev: final project outline](https://alex7li.github.io/DataStories/final-project-outline) |
[next: final final project](https://alex7li.github.io/DataStories/final-project-final)

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

After seeing these results, I was inspired to ask anothe question. I added a graph that sees if easy problems can improve the speed that you solve easy problems at.

<div class="flourish-embed flourish-scatter" data-src="visualisation/12780512"><script src="https://public.flourish.studio/resources/embed.js"></script></div>

It seems that the answer is: not really.
> Actually, there are quite a few numeric issues with the data (it's hard to estimate the change in 'average first solve time' because it's a metric that requires two measurements of 'average first solve time' which itself is a metric that requires many measurements of 'first solve time' which are themselves noisy for reasons like a constestant starting late, or being in a contest where all other competitiors are unusually strong or weak. The latter situation is very common due to a division system. But we're going with 'not really'.

## Storyboards

Introduction: By including imagery of real competitions, we give unfamiliar people an idea of what the sport looks like.

Anaysis: Idk let's just use random 'analysis' images

Call to action: First it's a picture of text reinforcing the message, then we transition into the 'victory' image from I think the winners of last year's ICPC world finals. Maybe the reader will feel like they will be able to get there. Probablly not, statistically speaking.

[View the website preview!](https://preview.shorthand.com/ePD6rBoLNtleDV6i)


## User Research

There is only one target persona: someone who is currently doing competitive programming, and who wants to get better.

Though, to make sure the audience can be more broad, the introduction exists. I will find 2 people with CP experience, and
one person with a more broad experience when gathering feedback.

### Questions to ask in the interview:

After reading the storyboard, do you feel that anything is missing?

What chart was the hardest to comprehend? Why?

Did you agree with the conclusions of the storyboard?

Looking through the storyboard, did any section seem to not fit in with the others?

What other charts/analysis would you like to see?

### Female 20s, Expert on codeforces

Overall, she did not feel like anything was missing from the analysis and could not think
of anything to add to it. While going through the charts, she was surprised at the number
of users in hackerrank.

Upon getting to the easy/hard question story, she mentioned "I hate to solve hard questions"
but still agreed with the premise. Had some confusion with the popups, since the text refers
to them as question marks while they are information icons.

While looking at the last chart, she observed that doing more problems increases solve speed,
which is not the point I wanted to get across.

When asked, she said that the area chart was the most confusing one, because the line
pattern is so complicated. The format of this chart seemed optimal to her.

### Male 20s, Master on codeforces, coach for some competitive programming teams

In the walkthrough, he was thrown off because I had combined both the 'pupil' and 'newbie'
category into one color. He observed that trying to estimate how rating correlated with
number of submissions was not as helpful as number of correct submissions.

He said that the call to action was a very useful section to have and it helped make
the story a lot more actionable. He said that all of the charts were easy for him to
comprehend because
"I am a master of reading charts in addition a master on codeforces." 😼
He could not think of any charts to add.

He felt that one thing that was missing was information on how much people practice
on other platforms, since that's very common. That's a huge project, though.

He had some doubt over the conclusion that easy problems are not useful, saying
that there are many types of problems and some are more helpful than others. He
expressed suspicion at the negative coefficient, wondering if it was due to some
2D phenonana with PCA. He was interested in seeing the results segmented into more
categories than just 'easy' and 'hard'.

He was also interested in trying to segment some of the results based on rating,
because the way that people learn changes a lot as they gain experience.

"When you are below expert, you need to learn ideas. Later, when you get better, you need to apply them."

And, when you are a newbie, you need to learn to code. For easy problems, people can essentially always
either solve them 90% of the time or 10% of the time, in his experience.

### Male 20s, student

The first graph could use a legend, there are too many colors in the treemap. The amount of
text is too high compared to the number of graphs. Consider adding some 15% transparent code
in the background, or a screenshot of one of the websites. In the first graph, you could add logos
for the website. The overall storyline was good.

## Actions to take

- Make the text refering to a question mark refer to an information icon.
- Take the last chart and either make a grid of correlation between variables instead of the existing chart, or change the title to be more clear
- Separate out pupil and newbie category
- Modify the rating vs n submissions to have an x-axis of number of correct submissions, and smooth out the lines.
- Add discussion on limitations due to practice on other platforms.
- Split the linear model into all rating categories.
- Remove colors from the treemap
- Add subtitles to remove text from the website
- Modify some of the background to have more of a coding feel
- CONSIDER a graph above how much people 'get stuck' at a rating for a long time
- CONSIDER add logos in the first graph

### Continue

[next: final final project](https://alex7li.github.io/DataStories/final-project-final)