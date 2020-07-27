# Survive the Ark Patch Notes and Updates Discord Bot
Ark Game Discord Bot used to monitor updates and patch notes and display them in discord channels. Using async, made 3 loops in a discord bot to handle callbacks and the 2 timers. This needs an api code for discord at a minimum. Watchings youtube, twitter, and SurviveTheArk website patch notes page for changes in code to list patch notes and any updates they post. 

*The license is GNU GPLv3 BUT uses [Common Clause](https://commonsclause.com/) license as the primary, so you may not sell it but can change it how you like. I hope this helps others out with using multiple async loops in a single project as I had a hard time finding anyone who used it this way.*


## Requirements
1. Python 3.7.x or greater
2. API code from Discord Bot page
3. If using twitter portion, twitter api code
4. Port forward for the chosen port to all callbacks to reach your server, highly recommend restricting it to specific IP's, such as the provider you chose to monitor rss/youtube/website/news changes.
