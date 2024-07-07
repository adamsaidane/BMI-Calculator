# BMI Calculator
#### Description:
A simple website where you can calculate your BMI with the option to create an account  and have access to your BMI history which shows your BMI evolution over time.<br>
In order to make this website, I used the FLASK framework, CSS, HTML and a bit of JavaScript as well as SQL for the database.<br>
These are some of the features of the website:<br>
- **BMI Calculation:** Supports both metric and US measurement systems.
- **User Authentication:** Users can register, log in, and log out.
- **BMI History Tracking:** Registered users can view their BMI history in a graphical format.
- **Responsive Design:** The application is styled to be responsive and user-friendly.
- **Error Handling:** Provides error messages for invalid inputs and ensures smooth user interaction.
- **Graphical Representation:** BMI history is displayed in a line graph with date labels shown diagonally for better readability.
- **Dynamic Backgrounds:** The background color of the BMI graph changes based on the BMI values.

The app.py file contains the back-end work of the website where i wrote the login,registration,index functions and the bmi history graph function that puts every calculation in a graph.<br>

The index.html page is the main page that works as a guest account where you can just make a quick calculation and the have the result displayed in a box with its background color changes for each category (blue for underweight, green for healthy, yellow for overweight, red for obese and dark red for extremely obese) and if the user is logged in it adds the height, weight, bmi, category, and timestamp to the database.<br>

The register.html asks the user to enter his username ,email adress, password, the password confirmation and a valid birth date where the register function checks that each input is a valid one and that the confirmation matches the password and then add these information to the database.the password is changed to a hashed password for more security if the username already exists the website displays an error message saying that, if the confirmation and password do not match the website displays an error message saying that. <br>

The login.html asks the user to enter his username or email adress, password where the login function checks that the email/username and the password match the ones registered in the database and if it's wrong it displays an error message saying "wrong username/email or password".<br>

The history.html displays to the user every calculation made with his account in the form of a table showing the timestamp, height, weight, BMI score, BMI category and if the user hasn't made a single calculation it displays an error message saying "empty history".<br>

The history_graph.html displays to the user a graph showing each calculation and in which category each BMI score falls in using the same coloring system.<br>

The bmi.db contains two schemas:
- **Users table:** contains id (an integer a primary key autoincrement not null), username (text not null), email (text not null), username (text not null), birth_date (text )
- **BMI history table:** contains id (an integer a primary key autoincrement not null), user_id (integer not null), bmi (real not null), weight (real not null), height (real not null), category (text not null), timestamp(datetime deafault current_timestamp)

