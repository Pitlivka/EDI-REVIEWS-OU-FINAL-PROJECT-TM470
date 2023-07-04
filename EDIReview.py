import requests
from kivy.metrics import dp
import psycopg2
from requests.models import PreparedRequest
from kivy.graphics import RoundedRectangle
from kivy.uix.togglebutton import ToggleButton
from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty
from kivy.graphics import Color, Line
from kivy.uix.widget import Widget
import uuid
from kivy.uix.label import Label
import textwrap


# Class LoginScreen responsible for login and verification of users.
class LoginScreen(BoxLayout):
    # Function log in which check is the username and password matches the requirements.
    # ( this function is not yet fully implemented, and I am currently working on implementing user
    # credential checks through user registration database )
    def login(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text

        # Perform login logic here
        # Check username and password validity
        # If successful, proceed to the main screen
        if username == '' and password == '':
            self.clear_widgets()  # Clear login screen widgets
            # Add the main screen widgets
            search_bar = SearchBar()
            self.add_widget(search_bar)
        else:
            # Popup content
            content = BoxLayout(orientation='vertical', padding=10, spacing=10)
            message_label = Label(text='Invalid username or password. Please try again.')
            try_again_button = Button(text='Try Again', size_hint=(None, None), size=(100, 40))

            popup = Popup(title='Wrong Credentials', size_hint=(None, None), size=(400, 200))
            content.add_widget(message_label)
            content.add_widget(try_again_button)
            popup.content = content

            # Bind button to dismiss the pup up.

            try_again_button.bind(on_release=popup.dismiss)
            popup.open()


# NavigationPanel class creating simple navigation panel after successful log in.
class NavigationPanel(BoxLayout):
    # Function which logs out the user by clearing all the widgets
    # ( Yet to be fully implemented by making sure all the users variables are cleared )
    def log_out(self):
        # Access the App instance and reset the root widget to LoginScreen
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(LoginScreen())


# Class for KIVY file which enables to create clickable text label in log in screen.
class ClickableLabel(ButtonBehavior, Label):
    pass


# Searchbar class which enables the search bar functionality.
class SearchBar(BoxLayout):
    search_input = ObjectProperty()
    search_results = ObjectProperty()

    Builder.load_file('my.kv')
    Window.size = (450, 800)

    red = 218 / 255
    green = 210 / 255
    blue = 244 / 255
    alpha = 0.31

    Window.clearcolor = (red, green, blue, alpha)

    # Search_locations function which uses LocationIQ API link to fetch the locations and their details based on the
    # search bar input. The input is then passed to GET URL used by LocationIQ Geolocation services.
    def search_locations(self):
        print(self.search_input.text)
        url = 'https://eu1.locationiq.com/v1/search?key="-API key goes here-"&countrycodes=gb&format' \
              '=json&json_callback=<string>&'
        params = {'q': self.search_input.text}
        req = PreparedRequest()
        req.prepare_url(url, params)
        edited_url = req.url

        req = requests.get(edited_url)
        result = req.json()
        print(result)
        self.search_results.clear_widgets()

        # Location results in json format are parsed and each location is then send to Kivy code to be added as
        # widget and displayed under search bar section. Kivy code implements the visual elements.
        for entry in result:
            if 'place_id' in entry:
                self.search_results.add_widget(LocationResult(location=entry))


global_location_id = None


# Class LocationResult which enables to add the location to the database and show locations profile.
class LocationResult(BoxLayout):
    location = ObjectProperty()

    # This function  enables to open a popup window which lets user add new review.
    def show_review_popup(self):

        LocationResult.chosen_loc_id = self.location['place_id']
        print("value is: " + LocationResult.chosen_loc_id)

        popup = AddReviewPopup()
        popup.open()

    # This function is responsible for adding each location was generated and clicked on by user to the database.
    def add_location_to_database(self):
        conn = psycopg2.connect("port=5432 dbname=edi_app user=postgres password=Kura1992")
        cur = conn.cursor()
        cur.execute("SELECT * FROM location.locations WHERE place_id = '%s';" % (self.location['place_id'],))
        record = cur.fetchone()
        global global_location_id
        global_location_id = self.location['place_id']
        if record is not None:
            print("Data already exists in the database")
        else:
            if 'icon' in self.location:
                sql = (
                    "INSERT INTO location.locations(place_id, display_name, class,type, icon, lat, lon) VALUES (%s, "
                    "%s, %s, %s, %s, %s, %s)")
                val = (self.location['place_id'], self.location['display_name'], self.location['class'],
                       self.location['type'], self.location['icon'], self.location['lat'], self.location['lon'])
                cur.execute(sql, val)
                conn.commit()
            else:
                sql = (
                    "INSERT INTO location.locations(place_id, display_name, class,type, lat, lon) VALUES (%s, %s, %s,"
                    "%s, %s, %s)")
                val = (self.location['place_id'], self.location['display_name'], self.location['class'],
                       self.location['type'], self.location['lat'], self.location['lon'])
                cur.execute(sql, val)
                conn.commit()
            print("Data added to the database")

    # This function is responsible for opening profile of the location popup by fetching the name of the location,
    # type of the location and average rating from the database.
    def show_profile_popup(self):
        conn = psycopg2.connect("port=5432 dbname=edi_app user=postgres password=Kura1992")
        cur = conn.cursor()

        # Fetch location data
        cur.execute("SELECT * FROM location.locations WHERE place_id = '%s';" % (self.location['place_id'],))
        record = cur.fetchone()

        if record:
            display_name = record[1]  # Assuming display_name is in the second column
            location_type = record[2]  # Assuming location_type is in the third column
            average_rating = record[7]  # Assuming average_rating is in the eighth column

            # Fetch reviews for the location which is open.
            # This is done by searching the database with place_id value assigned to the location being opened.
            cur.execute("SELECT * FROM location.reviews WHERE location_id = '%s';" % (self.location['place_id'],))
            reviews = cur.fetchall()

            # Create a list to hold review dictionaries
            review_list = []

            # Iterate over the fetched reviews and create review dictionaries
            # All the elements of existing review are saved in review_dict to be used to dynamically
            # display all the reviews ever posted for the location by any user.
            for review in reviews:
                review_dict = {
                    'review_text': review[3],
                    'rating': review[6],
                    'tags': review[2],
                    'name': review[0],
                    'pronounces': review[7],
                    'experience_type': review[8],
                    'reviews_id': review[5],
                    'background': review[1],
                    'sexual_orientation': review[9]
                }
                review_list.append(review_dict)
            # save location name, type, average rating and all the existing reviews in one popup variable.
            popup = ReviewProfilePopup(display_name=display_name, location_type=location_type,
                                       average_rating=average_rating, reviews=review_list)
            # popup which will open ReviewProfilePopup screen showing all the information saved in popup variable.
            popup.open()

            print("Type is ", location_type)
        else:

            pass


# Class responsible for enabling popup of the report window in kivy.
class ReportPopup(Popup):
    submit_report = ObjectProperty(None)


# Class responsible for enabling to pass text variable containing all the options selected by the user in drop down
# menu.
class MultiSelectSpinnerOption(BoxLayout):
    text = StringProperty()


# Class responsible for displaying the screen which enables user to submit new review.
class ReviewProfilePopup(Popup):
    display_name = ObjectProperty(None)
    location_type = ObjectProperty(None)
    average_rating = ObjectProperty(None)
    reviews = ObjectProperty([])
    review_layout = ObjectProperty(None)
    location = ObjectProperty(None)

    # This function opens popup window for adding the review screen.
    def show_review_popup(self):

        popup = AddReviewPopup()
        popup.open()

    # This function saves review_id when report review button is clicked for future reference.
    def handle_button_release(self, review_id):
        # Use the saved_review_id variable here or perform any other operations
        print("Button released for review_id:", review_id)

    # This function fetches all the data from each existing review for the location which is currently opened in
    # its location profile. The method creates all the labels, formats them in required manner and adds them as
    # widgets referenced in to KIVY code which then displays each review in its own section in desired configuration.
    def on_open(self):
        # Clear any previous review widgets
        self.ids.review_layout.clear_widgets()
        self.saved_review_id = None

        # Iterate over the reviews and create review widgets dynamically
        for index, review in enumerate(self.reviews):
            name = review['name']
            review_text = review['review_text']
            rating = review['rating']
            tags = review['tags']
            pronounces = review['pronounces']
            experience = review['experience_type']
            reviews_id = review['reviews_id']
            background = review['background']
            sexual_orientation = review['sexual_orientation']

            # textwrap method used to wrap the text in specified lenght in how many characters to be in one line.
            characters_per_line_review = 100
            wrapped_review_text = textwrap.fill(review_text, characters_per_line_review)

            characters_per_line_tags = 100
            wrapped_tags_text = textwrap.fill(tags, characters_per_line_tags)

            # Calculate the height of the review label based on the number of lines in the wrapped text
            reviews_num_lines = wrapped_review_text.count('\n')
            review_label_height = dp(30 * reviews_num_lines) + 55

            tags_num_lines = wrapped_tags_text.count('\n') + 1
            tags_tags_height = dp(30 * tags_num_lines)

            # Creation of the labels which have predefined GUI style.
            name_label = Label(text=f"[b]Name:[/b] {name}", markup=True, halign='left',
                               size_hint=(1.3, None), height=dp(30), padding=(5, 0), color=(0, 0, 0, 1))

            pronounces_label = Label(text=f"[b]Pronounces:[/b] {pronounces}", markup=True, halign='left',
                                     size_hint=(1.2, None), height=dp(30), padding=(0, 0), color=(0, 0, 0, 1))

            experience_label = Label(text=f"[b]Experience:[/b] {experience}", markup=True, halign='left',
                                     size_hint=(1.3, None), height=dp(30), padding=(5, 0), color=(0, 0, 0, 1))

            rating_label = Label(text=f"[b]Rating:[/b] {rating}", markup=True, halign='left',
                                 size_hint=(1.2, None), height=tags_tags_height, padding=(0, 0), color=(0, 0, 0, 1))

            tags_label = Label(text=f"[b]Tags:[/b] {wrapped_tags_text}", markup=True, halign='justify',
                               size_hint=(1.3, None), height=dp(30), padding=(5, 5), color=(0, 0, 0, 1))

            review_label = Label(text=f"[b]Review:[/b] {review_text}", markup=True, halign='justify',
                                 size_hint=(1, None), height=review_label_height, padding=(5, 0), color=(0, 0, 0, 1))

            report_button = Button(text="Report Review", size_hint=(None, None), size=(dp(120), dp(30)))

            background_label = Label(text=f"[b]Background:[/b] {background}", markup=True, halign='left',
                                     size_hint=(1.3, None), height=dp(30), padding=(5, 0), color=(0, 0, 0, 1))

            sexual_orientation_label = Label(text=f"[b]Sexual orientation:[/b] {sexual_orientation}", markup=True,
                                             halign='left', size_hint=(1.3, None), height=dp(30), padding=(5, 0),
                                             color=(0, 0, 0, 1))

            name_pronounces_layout = BoxLayout(orientation='horizontal', spacing=0,
                                               size_hint=(1, None), height=dp(30))

            name_pronounces_layout.add_widget(name_label)
            name_pronounces_layout.add_widget(pronounces_label)

            experience_rating_layout = BoxLayout(orientation='horizontal', spacing=0,
                                                 size_hint=(1, None), height=dp(30))

            experience_rating_layout.add_widget(experience_label)
            experience_rating_layout.add_widget(rating_label)

            # Create a vertical box layout for each review
            review_layout = BoxLayout(orientation='vertical', spacing=5, padding=(15, 15), size_hint=(1, None))

            review_layout.add_widget(name_pronounces_layout)
            review_layout.add_widget(experience_rating_layout)
            review_layout.add_widget(background_label)
            review_layout.add_widget(sexual_orientation_label)
            review_layout.add_widget(tags_label)
            review_layout.add_widget(review_label)
            review_layout.add_widget(report_button)

            # Wrapping the review_layout in a RelativeLayout
            review_relative_layout = RelativeLayout(size_hint=(None, None),
                                                    size=(dp(400), review_label_height + tags_tags_height + dp(180)))
            review_relative_layout.add_widget(review_layout)

            # Add the review layout to the review layout with a dynamic height
            self.ids.review_layout.add_widget(review_relative_layout)

            # Spacer widget to increase space between widgets.
            if index < len(self.reviews) - 1:
                spacer = Widget(size_hint=(1, None), height=dp(30))
                self.ids.review_layout.add_widget(spacer)

            # Update the width and height of the layouts based on their content
            name_label.bind(size=name_label.setter('text_size'))
            review_label.bind(size=review_label.setter('text_size'))
            rating_label.bind(size=rating_label.setter('text_size'))
            experience_label.bind(size=experience_label.setter('text_size'))
            background_label.bind(size=background_label.setter('text_size'))
            sexual_orientation_label.bind(size=sexual_orientation_label.setter('text_size'))
            pronounces_label.bind(size=pronounces_label.setter('text_size'))
            name_label.bind(size=name_label.setter('text_size'))
            tags_label.bind(size=tags_label.setter('text_size'))

            # review_layout.bind(minimum_height=review_layout.setter('height'))

            report_button.bind(on_release=lambda btn, review_id=reviews_id: self.open_report_popup(review_id))
            report_button.bind(on_release=lambda btn, review_id=reviews_id: self.handle_button_release(review_id))

            bottom_gap_offset = 10
            # Canvas which creates boxed border around each review dynamically updated depending on lenght of the review
            # text.
            with review_relative_layout.canvas.before:
                Color(1, 1, 1, 1)  # Black color
                border_width = 2
                spacing = 3
                red_box_height = review_relative_layout.height + 2 * border_width + 2 + bottom_gap_offset
                Line(rectangle=(
                    review_relative_layout.x - border_width + spacing,
                    review_relative_layout.y - border_width + spacing,
                    review_relative_layout.width + 2 * (border_width + spacing),
                    red_box_height),
                    width=border_width)

    # Function opening popup window for user to submit the report fo review.
    def open_report_popup(self, reviews_id):
        # Open the report popup when the "Report Review" button is clicked
        print("Extra Argument:", reviews_id)
        self.saved_review_id = reviews_id
        popup = ReportPopup()
        popup.submit_report = self.submit_report
        popup.open()

    # This function is responsible for submitting the report in to the review_reports database table.
    def submit_report(self, report_text):
        # Handle the submitted report text
        print("Submitted report:", report_text)

        conn = psycopg2.connect("port=5432 dbname=edi_app user=postgres password=Kura1992")
        cur = conn.cursor()
        sql = (
            "INSERT INTO location.review_reports(location_id,report_content,review_id) VALUES (%s, %s, %s)")
        val = (global_location_id, report_text, self.saved_review_id)
        cur.execute(sql, val)
        conn.commit()


# Class responsible for adding reviews to the database after they have been submitted by the user.
class AddReviewPopup(Popup):
    location_id = ObjectProperty(None)
    rev_name = ObjectProperty(None)
    rev_background = ObjectProperty(None)
    rev_tags = ObjectProperty(None)
    rev_comment = ObjectProperty(None)
    rev_rating = ObjectProperty(None)
    rev_experience = ObjectProperty(None)
    rev_pronounces = ObjectProperty(None)
    rev_sex_orientation = ObjectProperty(None)

    # This function is responsible for updating the average rating for the location every time new review is submitted.
    def update_average_rating(self):
        conn = psycopg2.connect("port=5432 dbname=edi_app user=postgres password=Kura1992")
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*), AVG(rating) FROM location.reviews WHERE location_id = '%s';" % (global_location_id,))
        count, avg_score = cur.fetchone()
        avg_score = "{:.1f}".format(avg_score)
        if count > 0:
            cur.execute(
                "UPDATE location.locations SET average_rating = %s WHERE place_id = '%s';" % (
                    avg_score, global_location_id,))
            conn.commit()
            print("Average rating updated for location with place_id:", global_location_id)
        else:
            print("No reviews found for location with place_id:", global_location_id)

    # This function is responsible for pre-processing the review by fetching extra variables needed so the review can be
    # added to the database. The variables include the locations id number, review experience which is calculated based
    # on the rating selected by the user.
    def process_review(self, rev_name, rev_background, rev_tags, rev_comment, rev_rating, rev_sex_orientation,
                       rev_pronounces):
        conn = psycopg2.connect("port=5432 dbname=edi_app user=postgres password=Kura1992")
        cur = conn.cursor()

        while True:
            # code generating random id.
            rev_id = str(uuid.uuid4())[:10]  # Generate a random unique ID
            # before the random id is selected, it is first checked if the random id already exists to make sure
            # there are no duplicates.
            if not self.review_exists(rev_id, cur):
                break
        if rev_rating >= 4:
            rev_experience = "Positive"
        elif 3 <= rev_rating <= 3.5:
            rev_experience = "Neutral"
        elif 1 <= rev_rating <= 2.5:
            rev_experience = "Negative"

        Reviews.add_review(
            self, rev_id, global_location_id, rev_name, rev_background, rev_tags, rev_comment, rev_rating,
            rev_sex_orientation, rev_experience, rev_pronounces
        )

        cur.close()
        conn.close()

    # This method checks if the review id already exists.
    def review_exists(self, rev_id, cur):
        sql = "SELECT COUNT(*) FROM location.reviews WHERE reviews_id = %s"
        cur.execute(sql, (rev_id,))
        count = cur.fetchone()[0]
        return count > 0

    # Method which formats the tags in the review and assigns them to rev_tags variable.
    def update_tags(self):
        positive_tags = ', '.join(tag.text for tag in self.ids.positive_tags_box.children if tag.state == "down")
        negative_tags = ', '.join(tag.text for tag in self.ids.negative_tags_box.children if tag.state == "down")
        self.rev_tags = f"{positive_tags} {negative_tags}"


# This class is responsible for adding review to the database.
class Reviews(BoxLayout):

    # This method adds review and all the necessary variables to the reviews' database.
    def add_review(self, rev_id, rev_loc_id, rev_name, rev_background, rev_tags, rev_comment, rev_rating,
                   rev_sexual_orientation, rev_experience,
                   rev_pronounces):
        conn = psycopg2.connect("port=5432 dbname=edi_app user=postgres password=Kura1992")
        cur = conn.cursor()
        sql = (
            "INSERT INTO location.reviews(reviews_id, location_id, name,background, tags, review_comment, rating, "
            "sexual_orientation, experience_type,pronounces) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s)")
        val = (
            rev_id, rev_loc_id, rev_name, rev_background, rev_tags, rev_comment, rev_rating, rev_sexual_orientation,
            rev_experience, rev_pronounces)
        cur.execute(sql, val)
        conn.commit()


# Class enabling rounded buttons in AddReview screen.
class RoundedToggleButton(ToggleButton):
    def __init__(self, **kwargs):
        super(RoundedToggleButton, self).__init__(**kwargs)
        self.background_color = [1, 1, 1, 0]  # Set initial background color to light gray
        self.background_normal = ''
        self.background_down = ''
        self.bind(size=self._update_background, pos=self._update_background, state=self._update_background)

    # method updating background color of the button when its clicked(selected)
    def _update_background(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.state == 'down':
                Color(0.3, 0.6, 1, 1)  # Light blue color when button is pressed
            else:
                Color(0.5, 0.5, 0.5)  # Light gray color when button is not pressed
            RoundedRectangle(pos=self.pos, size=self.size, radius=[15, ])


class SearchApp(App):
    def build(self):
        return LoginScreen()


if __name__ == '__main__':
    SearchApp().run()
