[home page](https://alex7li.github.io/DataStories/)

# Final Project Outline

My final project intends to exploare the mental sport of competitive programming (CP). In a typical CP contest, participants will try to solve as many problems from a set of around 6 problems in about 3 hours. They need to be able to come up with creative solutions to never before seen problems, and then code their ideas into a bug free implementation that passes a comprehensive set of tests.

By analyzing data from popular CP websites, I want to show how practice can improve your performance. I'll look at the most common topics and their prevalance, classify users based on their solving speed and coding speed, and consider how much practice can help to show improvement. By the end, I hope to be able to say something about the best way to practice in order to improve: is it better to solve a bunch of hard problems or just to solve a lot of problems? To solve over a long period of time or within a short burst? How much influence does talent have over work?

The story will begin with an introduction. It will chart out the popularity of the sport over time and familiarize the reader with what a typical contest looks like. Then we get into the more difficult and exciting part of the project, which readers are most interested in: how do I get better?

In this section, I want to show the correlation between practice and improvement. Then I want to try and dive into factors that cause people to deviate from the standard. I'll classify users into axes based on their first-solve speed, total solve counts, and number of incorrect submissions. Then I will use this grouping to try and get a better estimate of how much different types of people improve with practice, and to see if is some kind of 'skill cap' that certain types of people face.

The final topic to explore is the actionable one. I want to create a grouping for different practice strategies: "solve hard problems", "solve more problems", and "do more live contests". I'll explore how different practice strategies correlate with success.

Finally, I can produce a call to action based on the results of my analysis. I will give a summary of how much people should expect to be able to improve, and what people can do to reach their potential.

Though the data analysis isn't done yet, one potential one-line story could be

_Anybody can become quite good at competitive programming by solving lots of problems, though ratings beyond 2100 may require talent._

## Data

For the introduction, at least it it easy to find data on the number of current registered users for popular sites by googling, though there isn't much for the total number of people who have been practicing the sport over time. We can also see data for some contests online line [google code jam](https://vstrimaitis.github.io/google_codejam_stats/#/000000000043580a). There are also some blog posts with useful data, [this is likely the most useful](https://codeforces.com/blog/entry/89502).

After this, though... there is no good dataset on the internet for a lot of this, it's quite a niche topic. The only datasets I could find are list of people's rating on each site, and lists of problems along with their editorials. It seems like we are doomed...

Luckily, the most popular coding platform, codeforces, has [an API](https://codeforces.com/apiHelp) where you can read almost all of their data. Still, we have to scrape a lot of data from it, and since the API is rate limited, it could take days of CPU time get it all, not to mention hundreds of lines of code for all of the edge cases...

Luckily, I know how to code and started the process over break! After a month, I got all of user data stored locally and on kaggle! [TODO: publish kaggle link]. This will be the basis for most of the visualizations beyond the introduction.

Since it's a brand new project, we can be excited to know that the insights in this project are going to be totally original :O
I'm exited to see how it turns out! However, for now, there is still a lot more work to do trying to refine the data into some nice visualizations.

## Sketches

First, I think we can have a chart involving the proportion of users using each site by googling all of the popular ones, along with a chart that states the number of users on I can also get popularity information for big contests and show that. This section may include some text discussion here with reasons for people becoming interested.
[](/IMG-1319.jpg)
Now that the user understands the topic, let's start familiarizing them with the topic by showing them what typical problems look like. We will feed them an exploratory visualization - what topics are most problems focused in, and what difficulty do the topics span?
<div class="flourish-embed flourish-survey" data-src="visualisation/12681260"><script src="https://public.flourish.studio/resources/embed.js"></script></div>

[](/IMG-1320.jpg)

Now, let's get to some more interesting data. As an obvious first inspirational step, we need to include some kind of graphic that displays how much rating changes over time.
<div class="flourish-embed flourish-scatter" data-src="visualisation/12680245"><script src="https://public.flourish.studio/resources/embed.js"></script></div>
We establish that practice does lead to improvements, on average. But still, there is a lot of noise here!
