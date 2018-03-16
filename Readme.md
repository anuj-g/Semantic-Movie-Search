A user may want to recollect a movie that he watched a few months back. He checks out search engines and popular movie websites. He leaves in a question, but does not get accurate results for it. 
Based on web mining and analysis from the websites like Movies.stackexchange, IMDB, Quora and others, we observed that the magnitude of this problem is very large. 
There is a  vast amount of questions already queued up in various question-answering portals on the web where most of these questions go unanswered and unattended. 
The most popular movie website IMDb, bases its search functionality on keyword search. This does not give us meaningful and accurate results. 

We start by taking user queries based on what they would remember about a movie. They could remember bits and pieces of the movie, which would help with the search. 
Users could remember certain actions/events from the movie, characters of the movies, theme, location where the movie was shot, etc. 
We filtered out events and characters from the input given by the user and used it for our matching engine. 
We have around 250 movie plots, from where we would take out events and characters to match with the user queries. 
After matching, we would rank the movies according to their scores. 

