# Spotify recommendations 

This script is using spotify API to get recommendations based on entered artist, track and genre.


More info can be found in spotify documentation: https://developer.spotify.com/documentation/web-api/reference/#endpoint-get-recommendations


## Example Usage
```
>>> Enter artist: Lola Marsh
>>> Enter track from mentioned artist: Only for a moment
>>> ['acoustic',
 'afrobeat', 
 'alt-rock',
 'alternative',
 'ambient',
 'anime',
 'black-metal',
 'bluegrass',
 'blues', 
 ...
>>> Which genre you would like to choose from genres above?: deep-house
```

## Database

The results are entered into SQL database:

| artist  | song | genre | recommendations | 
| ---------- | ----------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Lola Marsh | Only for a moment | deep-house | Henry And The Waiter - Our Free Souls \| Josh Butler - Got A Feeling - Bontan Remix \| Fritz Kalkbrenner - Wes \| Vance Joy - Riptide - FlicFlac Edit \| Giant Rooks - Heat Up  | 



## Workflow
- first thing is to have client id and secret id which can be requested on spotify developers site
- search via API for entered artist and extract artistID from returned json file
- search for songID of entered song, same procedure as with artist
- list available genres via API call and ask for genre
- for getting recommendations at first you have to request an access token and authenticate, it's done automatically by function
- after successful request response, data are saved into sql database

## Acknowledgments
Base of my code is from:
- https://github.com/codingforentrepreneurs/30-Days-of-Python/tree/master/tutorial-reference/Day%2019

Things which I added are:
- getting inputs from user
- searching for artist/song id and parsing through json file
- genres search
- recommendations api call
- DB insertion



