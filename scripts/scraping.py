import requests
from bs4 import BeautifulSoup

url = "https://www.scrapethissite.com/pages/simple/"

response = requests.get(url)
print("fin")
if response.status_code == 200:
    html = response.text
    # print(html)
    soup = BeautifulSoup(response.content, "html5lib")
    # s=soup.prettify()
    # print(s)
    names = soup.find_all("div", class_="col-md-4 country")
    element = []

    if names:
        for n in names:
            name= n.find("h3", class_="country-name").text.strip()
            infos = n.find("div", class_="country-info")

            population_tag = n.find("span", class_= "country-population").text.strip()
            if int(population_tag)> 200000000:
                element.append(f"name:{name}, population:{(population_tag)}")

            
            
    else:
        print("there is an error")
    
    for row in element:
        print(row)