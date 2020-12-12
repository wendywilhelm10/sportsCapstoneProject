# **Sports Website** #



1. **What goal will your website be designed to achieve?**
 
	The goal of this website is to provide the user the ability to select their favorite sport(s), favorite leagues(s) with that sport and their favorite team(s).  This app will display information about the users favorite teams for their favorite sport(s).



1. **What kind of users will visit your site? In other words, what is the demographic of
your users?**

	The demographic is anybody that enjoys sports and wants to see information about their favorite sports teams.



1. **What data do you plan on using? You may have not picked your actual API yet,
which is fine, just outline what kind of data you would like it to contain.**

	This website will use thesportsdb.com API and it will contain the user’s favorite sports, leagues and teams.  This will be providing some detailed information about the user's favorites teams.


**In brief, outline your approach to creating your project (knowing that you may not
know everything in advance and that these details might change later). Answer
questions like the ones below, but feel free to add more information:**
 

**What does your database schema look like?**

* Users
	* Username
	* Password
	* Email
	* First Name
	* Last Name
* Favorite Sports
	* User Id
	* Sports Id - from API
	* Sports Name
* Favorite League
	* Id from Favorite Sports table
	* League Id - from API
	* League Name
* Favorite Team
	* Id from Favorite League table
	* Team Id - from API
	* Team Name
	* Notes 


**What kinds of issues might you run into with your API?**
 
* There could be an issue if a favorite sport, league or team gets deleted from the API or the associated ID gets updated.

**Is there any sensitive information you need to secure?**

* The only sensitive information that needs to be secured in the username’s password and email address.

**What functionality will your app include?**

* Login/register page. (Create, Update)

* Menu bar across the top to add a new favorite sport, select a favorite league and select a favorite team.  'Add' button to add team for this user. (Create)

* The app will allow a user to delete a selected sport, league or team. (Delete)

* Once a team is added, user can add notes about the team. (Create, Update)

**What will the user flow look like?**

* The user will add a favorite sport, league and team.  They can add notes and/or edit existing notes.

* The website will be split up to show different sections based on the sport.  Different teams within a league will be grouped together within the sport. 

* There will be information about each team displayed to the user.  Will try to display the last 5 events for this team and the next upcoming 5 events.  

* Maybe I’ll incorporate a link or an expansion event that will be on the previous 5 events and when the user clicks, it will show the statistics for that event.