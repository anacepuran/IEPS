SEED_URLS = ['gov.si', 'evem.gov.si', 'e-uprava.gov.si', 'e-prostor.gov.si']
DOMAIN = '.gov.si'
DB_ = {
    'host': 'localhost',
    'port': '5432',
    'db_name': 'spider',
    'username': 'postgres',
    'password': 'postgres'
}
USER_AGENT = "fri-wier-norci"

BINARY_CONTENT = [".pdf", ".doc", ".docx",
                  ".ppt", ".pptx"]
IMAGE_CONTENT = [".png", ".jpg", ".jpeg", ".gif"]
IGNORE_SEED_URLS = ['evem.gov.si', 'e-uprava.gov.si',
                    'e-prostor.gov.si', 'euprava.gov.si', 'eprostor.gov.si']
IGNORE_DOMAIN_VARIATIONS = ('.gov.si', 'gov.si', 'www.gov.si')
PATH_EXCLUSIONS = ["favicon.ico", "data:image", "base64",
                   "maps.googleapis.", "maps.gstatic", "fonts.googleapis.", "getElementById", ".css", ".zip", ".csv", ".xlsx", ".xls", ".PPT"]
EXTRAS = ["https://www.", "http://www.",
          "https://", "http://", ".html", "www.", "www"]
