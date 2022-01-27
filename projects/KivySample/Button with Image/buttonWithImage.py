from kivy.app import App

from kivy.uix.boxlayout import BoxLayout

from kivy.lang import Builder

Builder.load_string("""

<KivyButton>:

    Button:

        text: "Hello Button!"

        size_hint: .05, .05
        width: 150

        Image:

            source: 'cd000062.jpg'

            center_x: self.parent.center_x

            center_y: self.parent.center_y  
            height: 150
            width:150
    
""")

class KivyButton(App, BoxLayout):
    
    def build(self):
        
        return self
    
KivyButton().run()