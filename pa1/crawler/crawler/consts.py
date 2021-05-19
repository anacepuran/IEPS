SEED_URLS = ['gov.si', 'evem.gov.si', 'e-uprava.gov.si', 'e-prostor.gov.si']
DOMAIN = '.gov.si'
DB_ = {
    'host': 'localhost',
    'port': '5432',
    'db_name': 'crawl',
    'username': 'postgres',
    'password': 'postgres'
}
USER_AGENT = "fri-wier-norci"

BINARY_CONTENT = [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".pptm", 
                    ".PDF", ".DOC", ".DOCX", ".PPT", ".PPTX", ".PPTM"]
IMAGE_CONTENT = [".png", ".jpg", ".jpeg", ".gif",
                 ".JPG", ".PNG", ".JPEG", ".GIF" ]
PATH_EXCLUSIONS = ["favicon.ico", "data:image", "base64", "maps.googleapis.", "maps.gstatic", 
                    "fonts.googleapis.", "getElementById", ".css", ".zip", ".csv", ".xlsx", ".xls", 
                    ".PPT", ".mp4",".rar", ".jsp", ".xml", ".tif", ".ai", ".mp3", ".ppsx", ".kmz", 
                    ".prj", ".xsd", ".ZIP", ".aspx", ".odt", ".docm", ".ods", ".potx"]
EXTRAS = ["https://www.", "http://www.",
          "https://", "http://", ".html", "www.", "www"]
