from dataclasses import dataclass
from bs4 import BeautifulSoup as Soup
from requests import get
import csv


@dataclass(frozen=True)
class Product:
    name: str
    price: float
    negotiable: bool
    url: str


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/102.0.5005.72 Safari/537.36 ",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.9 "
}

if __name__ == '__main__':
    products: set[Product] = set()
    print("1. Gry i konsole\n2.Konsole")
    choice = int(input(">>"))
    match choice:
        case 1:
            category = "gry-konsole"
        case 2:
            category = "gry-konsole/konsole"
        case _:
            category = ""
    page = 1
    root_url = f"https://www.olx.pl/d/elektronika/{choice}/?page={page}"
    counter = 0
    while True:
        try:
            root_url = f"https://www.olx.pl/d/elektronika/{category}/?page={page}"
            html = get(url=root_url, headers=HEADERS).text
            soup = Soup(html, 'html.parser')
            product = soup.find_all("div", class_="css-u2ayx9")
            for token in product:
                href = token.find_all_previous('a')[0].get("href")
                url = f"https://www.olx.pl{href}"
                title = token.find_next("h6").text
                price = token.find_next("p").text.strip()
                if price == "Zamienię": continue
                split_price = price.split("zł")
                if split_price[1] == "do negocjacji":
                    negotiable = True
                else:
                    negotiable = False
                try:
                    true_price = float(split_price[0].replace(" ", ""))
                except ValueError:
                    continue
                counter += 1
                products.add(Product(title, true_price, negotiable, url))
                print(f"Added {counter} item")
            page += 1
        except IndexError as e:
            raise e
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)

    write_counter = 0
    with open("data.csv", 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for token in products:
            price = str(token.price).replace('.', ',')
            row = [token.name, price, token.negotiable, token.url]
            try:
                writer.writerow(row)
            except UnicodeEncodeError as e:
                raise e
            write_counter += 1
            if not write_counter % 10:
                print(f"Wrote {write_counter} records")
