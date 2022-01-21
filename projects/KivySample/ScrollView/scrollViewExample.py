from kivy.base import runTouchApp

from kivy.lang import Builder

root = Builder.load_string(r'''

ScrollView:

    Label:
    
        text: 'Scrollview Example' * 500
        
        font_size: 30
        
        size_hint_x: 1
        
        size_hint_y: None
        
        text_size: self.width, None
        
        height: self.texture_size[1]
        
''')

runTouchApp(root)