import csv


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

motor = create_engine(
    "postgres://tybnzuug:sEd-YLwtFP6juILFYUkAKmwTtHpoNasU@drona.db.elephantsql.com:5432/tybnzuug")
# URL de variable de entorno
# engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind=motor))

# listar vuelos


def main():
    fo = open("books.csv")
    lector = csv.reader(fo)
    for isbn, titulo, autor, year in lector:
        db.execute("INSERT INTO libros (isbn, titulo, autor, year) VALUES(:isbn, :titulo, :autor, :year)", {
                   "isbn": isbn, "titulo": titulo, "autor": autor, "year": year})
        print(f"agregados libro {isbn} , {titulo} , {autor}, {year}")
    db.commit()


if __name__ == "__main__":
    main()
