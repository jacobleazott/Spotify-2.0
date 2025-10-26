source files grab raw data and show you how to normalize data into our structure
track_service keeps track cache, knows which src to prioritize, and how to map tracks

coordinator grabs normalized track data, maps track, maps album, maps artists and returns objects


service normalizes incomming data and any dependencies (if needed) ie normalizes tracks and then track albums and track artists
    it also knows how to map a track

coordinator takes gets normalized data, maps it all into objects and returns models


OKAY OKAY OKAY
so the source files know how to grab raw data and are responsible for normalizing it into expected intermediary format

Then the resolver is responsible for knowing that if you call get_ on a core model it knows how to resolve it's dependencies. THis
is for "immutable" data strucutres like just Tracks, Albums, and Artists. the data we pass around can either be just the id OR the full data
If the full data is passed around then we can resolve it since it's one object, if it's the id it knows whcih method to call from our source file to resolve it
It will include batch resolvers and full hydrators for lists.
It also owns the cache for our "core" models

Then we have service files for things like modifying playlists and stuff like that

Then the coordinator or music app forwards it all into one interface, knowing which methods to call and when to use the resolver and which sources are being passed around

This solves the idea of needing to keep these services talking to each other when we only ever need to resolve, tracks, albums, and artists. THat is one "service"
whcih is the resolver. Then all other services can use the resolver as ncecssary to fill in their tracks, artists, or albums, etc...
The only thing we might have to figure out is how we plan to grab data like all of an artists albums. Maybe that means we put the albums list into the artist model
and then just know how to resolve it.

One final question I know is if we keep resolving the data when does it end? Like if I resolve a track and I only have the album_id when should I resolve the album?
should I only call the resolve when necessary? THis hurts my head