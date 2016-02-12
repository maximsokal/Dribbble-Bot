This bot was developed with the purpose of automating tedious tasks on [Dribbble](https://dribbble.com/), a website for designers to share samples of their work with each other.
The general idea is to basically earn yourself Dribbble followers while not following thousands who have no intentional in following you back.
# What It Does
* It obtains a list of newly registered users on Dribbble's [Debuts](https://dribbble.com/shots?list=debuts) page.
* It follows all users on that list, ignoring users already followed, every day. 
* Every two days, if the user followed hasn't followed the bot back, the user is unfollowed and blacklisted by the bot.
* Once a user has been on a list, be it the list of followed users, or the blacklisted users, for a week, their name is purged from the applicable list(s) and there is a small chance that the bot may attempt to follow them again, depending on how many users debut in a given week.

**Note**: This program needs to be ran as part of a daily task or cronjob depending on your operating system. It won't run itself every day :)
