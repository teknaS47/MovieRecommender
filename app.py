import os
from flask import Flask, redirect, url_for, request, render_template
import requests
import json
import numpy as np 
import pandas as pd
import re
import pymongo

app = Flask(__name__)

myclient = pymongo.MongoClient("mongodb://db:27017/")

mydb = myclient["moviedb"]
movies = mydb["newmovies"]
movie_cursor = movies.find()
movies_df = pd.DataFrame(list(movie_cursor))
movies_df["id"] = pd.to_numeric(movies_df["id"])

rating_db = mydb["ratings"]
rating_cursor = rating_db.find()
ratings_df = pd.DataFrame(list(rating_cursor))

allm=movies_df

movies= allm[['id', 'original_title', 'original_language','vote_average']]
movies= movies.rename(columns={'id':'movieId'})
movies = movies[movies['original_language']== 'en']

ratings= ratings_df

ratings= ratings[['userId', 'movieId', 'rating']]

movies.movieId =pd.to_numeric(movies.movieId, errors='coerce')

ratings.movieId = pd.to_numeric(ratings.movieId, errors= 'coerce')

data= pd.merge(ratings, movies, on='movieId', how='inner')
data.head()

matrix= data.pivot_table(index='userId', columns='original_title', values='rating')

class recoomender:
   
    def pearson(self, a, b):
        
        a_m = a-a.mean()
        b_m= b-b.mean()

        return np.sum(a_m*b_m) / np.sqrt(np.sum(a_m**2)* np.sum(b_m**2))

    def recommend(self, movie, n):
        reviews=[]
        m = matrix
        
        for title in m.columns:
            if title == movie:
                continue
            corr= self.pearson(m[movie], m[title])
            if np.isnan(corr):
                continue
            else:
                if(corr>=0.1):
                    reviews.append((title, corr))
        reviews.sort(key=lambda tup:tup[1], reverse=True)
        return reviews[:n]
        

@app.route('/')
def first():

    return render_template("movies.html")
    
r = recoomender()
cache={}

@app.route('/rec',methods=['POST','GET'])
def rec():

    img=""
    title=[]
    error=None
          
    url = "https://imdb8.p.rapidapi.com/title/auto-complete"
    
    q=str(request.args.get("mname"))
    
    querystring = {"q":q.lower()}

    headers = {
        'x-rapidapi-host': "imdb8.p.rapidapi.com",
        'x-rapidapi-key': "a713747970msh612fb6ca24060e1p1b5ce6jsnbdd10929a19c" }

    response = requests.request("GET", url, headers=headers, params=querystring)
    
    response_json = json.loads(response.text)

    title_f=str(response_json['d'][0]['l'])

    if title_f in cache:
        title = cache[title_f]['title']
        s_image = cache[title_f]['image']
    else:
        try:
            recs = r.recommend(title_f,5)

            for i in recs:
                title.append(i[0])

            for j in title:
                querystring2 = {"q":j.lower()}
                response2 = requests.request("GET", url, headers=headers, params=querystring2)
                response_json_2 = json.loads(response2.text)
                img+=response_json_2['d'][0]['i']['imageUrl']+","

                s_image = img.split(",")
                cache[title_f]={'title':title,'image':s_image}
            
        except:
            title=None
            s_image=None
            error="Movie not found"

    return render_template("movies.html",title=title, image=s_image, error=error)

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0')