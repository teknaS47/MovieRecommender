FROM mongo

COPY ./the-movies-dataset/movies_metadata_WORD.csv /movies_metadata.csv
COPY ./the-movies-dataset/ratings.csv /ratings.csv
CMD mongoimport --host db --db moviedb --collection newmovies --type csv --file /movies_metadata.csv --headerline && mongoimport --host db --db moviedb --collection ratings --type csv --file /ratings.csv --headerline