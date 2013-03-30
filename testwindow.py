
import spynner


browser = spynner.Browser()
browser.debug_level = spynner.DEBUG
browser.load_jquery(True)
browser.load("http://localhost:8069/?db=OE")
browser.create_webview()
browser.show()
browser.browse()