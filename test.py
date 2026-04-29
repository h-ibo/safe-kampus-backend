import os
from app.utils.firecrawl import firecrawl_get

os.environ["FIRECRAWL_API_KEY"] = "fc-8452dfba74ba413bb429c5105dd2b1db"

data = firecrawl_get("https://www.harran.edu.tr")

print(len(data))
print(data[:500])