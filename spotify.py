import base64
import datetime
from urllib.parse import urlencode
import requests
import pprint
import json
import sqlite3

client_id = ""
client_secret = ""


def main():
    spotify = SpotifyAPI(client_id, client_secret)

    # search for artist id
    person = input("Enter artist: ")
    artist = spotify.search(query=f"artist:{person}")
    artistData = json.loads(artist.text)
    artistId = artistData["artists"]["items"][0]["id"]

    # search for song id
    songName = input("Enter track from mentioned artist: ")
    song = spotify.search(query=f"artist:{person} track:{songName}", search_type="track")
    songData = json.loads(song.text)
    songId = songData["tracks"]["items"][0]["id"]

    # ask for genre
    genresRequest = spotify.get_genres()
    genresData = json.loads(genresRequest.text)
    pprint.pprint(genresData["genres"])
    genreAnswer = input("Which genre you would like to choose from genres above?: ")

    # get recommendations
    result = spotify.get_recommendations(f"{artistId}", f"{genreAnswer}", f"{songId}")
    data = json.loads(result.text)

    dataVar = ""
    for i in range(len(data["tracks"])):
        s = data["tracks"][i]["artists"][0]["name"]
        dataVar += s
        s2 = data["tracks"][i]["name"]
        dataVar += " - " + s2 + " | "

    # inserting into database
    spotify.add_to_database(person, songName, genreAnswer, dataVar)


class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {"Authorization": f"Basic {client_creds_b64}"}

    def get_token_data(self):
        return {"grant_type": "client_credentials"}

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")
            # return False
        data = r.json()
        now = datetime.datetime.now()
        access_token = data["access_token"]
        expires_in = data["expires_in"]  # seconds
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        return headers

    # search / lookup
    def get_resource(self, lookup_id, resource_type="albums", version="v1"):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r

    def get_album(self, _id):
        return self.get_resource(_id, resource_type="albums")

    def get_artist(self, _id):
        return self.get_resource(lookup_id="available-genre-seeds", resource_type="artists")

    def get_genres(self):
        return self.get_resource(lookup_id="available-genre-seeds", resource_type="recommendations")

    # last step
    def base_search(self, query_params, ending="search"):
        headers = self.get_resource_header()
        endpoint = f"https://api.spotify.com/v1/{ending}"
        lookup_url = f"{endpoint}?{query_params}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return lookup_url
        return r

    # formatting input and passing to base_search
    def search(self, query=None, operator=None, operator_query=None, search_type="artist"):
        if query == None:
            raise Exception("A query is required")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k, v in query.items()])
        if operator != None and operator_query != None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({"q": query, "type": search_type.lower()})
        return self.base_search(query_params)

    def get_recommendations(self, artists, genres, tracks):
        query_params = urlencode({"seed_artists": artists, "seed_genres": genres, "seed_tracks": tracks})
        return self.base_search(query_params, ending="recommendations")

    def add_to_database(self, artist, song, genre, recom):
        connection = sqlite3.connect(r"C:\python_projects\spotifyRecommender\data.db")
        c = connection.cursor()
        with connection:
            c.execute(
                "INSERT INTO spotify VALUES (:artist, :song, :genre, :recommendations)",
                {"artist": artist, "song": song, "genre": genre, "recommendations": recom},
            )


if __name__ == "__main__":
    main()


"""
Creating new sql table and printing output:
connection = sqlite3.connect(r'C:\python_projects\spotifyRecommender\data.db')
c = connection.cursor()
c.execute('CREATE TABLE spotify(artist, song, genre, recommendations)')
c.execute('SELECT * FROM spotify')
c.fetchall()
"""
