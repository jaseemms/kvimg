import threading

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics.texture import Texture
from kivy.properties import NumericProperty, ListProperty
from kivy.clock import Clock, _default_time as time
from kivy.logger import Logger

from kivy.modules import inspector
from kivy.core.window import Window

from utils import get_image_iterator, image_formats, get_image_bytes
from platform_based import get_permissions


class ImageButton(ButtonBehavior, Image):

    def populate_texture(self, texture):
        texture.blit_buffer(self.cbuffer)


class IconButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(IconButton, self).__init__(**kwargs)
        self.temp = None
        self.press_image = None
       
    def on_press(self):
        if not self.temp:
            self.temp = self.source

        self.source = self.press_image

    def on_release(self):
        self.source = self.temp


class MenuBar(StackLayout):
    pass


class ImageList(ScrollView):
    pass


class ImageBox(BoxLayout):
    pass


class BodyBox(BoxLayout):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(BodyBox, self).__init__(**kwargs)
        self.image_box = ImageBox()
        self.current_button = None
    
    def show_image(self, image_button):
        self.current_button = image_button
        self.image_box.ids.image.source = image_button.path
        self.remove_widget(self.image_list)
        self.add_widget(self.image_box)

    def hide_image(self):
        self.remove_widget(self.image_box)
        self.add_widget(self.image_list)
        self.current_button = None

    def next_image(self):
        next_count = self.current_button.counter + 1

        try:
            self.current_button = self.image_list.image_grid.children[- next_count]
            self.image_box.ids.image.source = self.current_button.path

        except:
            pass

    def previous_image(self):
        previous = self.current_button.counter - 1

        if previous == 0:
            return None
            
        try:
            self.current_button = self.image_list.image_grid.children[- previous]
            self.image_box.ids.image.source = self.current_button.path
            
        except:
            pass


class MainLayout(BoxLayout):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(MainLayout, self).__init__(**kwargs)
        self.menu_bar = None
        self.previous_widget = None
    
    def toggle_menu_bar(self, storage_path=None):

        if self.menu_bar:
            self.body_box.remove_widget(self.menu_bar)
            self.menu_bar = None
            self.body_box.add_widget(self.previous_widget)

        else:
            self.menu_bar = MenuBar()

            if self.body_box.current_button:
                self.body_box.remove_widget(self.body_box.image_box)
                self.previous_widget = self.body_box.image_box

            else:
                self.body_box.remove_widget(self.body_box.image_list)
                self.previous_widget = self.body_box.image_list

            self.body_box.add_widget(self.menu_bar)

        if storage_path:
            app.add_gallery_images(storage_path=storage_path)


class MainApp(App):

    image_counter = NumericProperty(0)
    image_iterator = None
    consumables = NumericProperty(0)
    thread_counter = NumericProperty(1)
    
    def build(self):

        get_permissions()

        self.main_layout = MainLayout()
        self.image_grid = self.main_layout.body_box.image_list.image_grid

        self.add_gallery_images(storage_path='internal')
        Clock.schedule_interval(self.populate_image_content, 0)

        inspector.create_inspector(Window, self.main_layout)

        return self.main_layout

    def add_gallery_images(self, storage_path):

        self.image_grid.clear_widgets()

        self.image_iterator = get_image_iterator(storage_path=storage_path)
        self.image_counter = 0
        self.consumables = 1
        self.thread_counter = 1

        for image_path in self.image_iterator:

            if image_path.endswith(image_formats):
                Logger.info(f"Image Path : {image_path}")

                self.image_counter += 1

                image_button = ImageButton()
                image_button.path = image_path
                image_button.counter = self.image_counter
                image_button.texture = Texture.create(size=image_button.size, colorfmt='RGB',
                bufferfmt='ubyte')
                image_button.cbuffer = None

                self.image_grid.add_widget(image_button)

        threading.Thread(target=self.generate_image_buffer).start()

    def generate_image_buffer(self):
        
        while True:

            Logger.info(f"Running background thread to generate buffer")

            try:
                image_button = self.image_grid.children[- self.thread_counter]
                self.thread_counter += 1

            except IndexError:
                Logger.info(f"Image button not found for thread_counter : {self.thread_counter}")
                return 0

            image_bytes, image_size = get_image_bytes(image_button.path)
            image_button.texture = Texture.create(size=image_size, colorfmt='RGB',
                    bufferfmt='ubyte')
            image_button.cbuffer = image_bytes

    def populate_image_content(self, dt):

        limit = Clock.get_time() + 1 / 60

        while self.consumables and time() < limit:

            Logger.info(f"populating image content for consumables {self.consumables}")

            try:
                image_button = self.image_grid.children[- self.consumables]
            except IndexError:
                Logger.info(f"No consumables {self.consumables} found, reseting consumables to 0")

                self.consumables = 0
                return 0

            if image_button.cbuffer:
                Logger.info(f"populate texture for consumables {self.consumables}")
                image_button.populate_texture(image_button.texture)
                image_button.texture.add_reload_observer(image_button.populate_texture)

                self.consumables = self.consumables + 1

if __name__ == "__main__":
    app = MainApp()
    app.run()