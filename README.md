# Dash map with data from weather.gov

TODO Add description here

![](./images/img1-screenshot.png)


## Why do I need data dumper?

At some point I realized that I am going to store too much data in the memory of my 
laptop. Apart the fact that I don't need all the data in a RAM as I do not make any
specific analysis at the moment, my laptop cannot handle that much! So, as a short 
term solution I decided to dump all the data to parquet files every month. Basically, 
each file must contain data from the first to the last day of each month (UTC time).
In Redis I am going to store only 1 week of data as required for visualization. Basically,
for a short term, I am going to populate Redis with all the data, and on 2nd day of each 
month offload the historical data to parquet files. In addition, if data have been saved,
I am going to remove it unless it contains the data for the last week.

In long term I am going to use data streams and consume data from Weather.gov, push it
to stream, then consume from a stream and save to Redis and to a long term database. Trim
Redis to have only the most recent week of data.
