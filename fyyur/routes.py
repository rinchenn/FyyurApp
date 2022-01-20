import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for, abort, jsonify
from fyyur import app, db
from fyyur.models import Venue, Artist, Show
from fyyur.forms import *
import logging


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


def convert_db_genres_to_list(genres):
    return genres[1:-1].split(',')

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

    locals = []
    # Get all the locations (unique)
    locations = Venue.query.distinct(Venue.state, Venue.city).all()

    # Store all the locations as list of dict (local) in locals
    for location in locations:
        local = {
          'city': location.city,
          'state': location.state
        }
        locals.append(local)

    # Get all the venues from the database
    venues = Venue.query.all()

    # Store all the venues in each locations as a list (id and name)
    for local in locals:
        local['venues'] = []
        for venue in venues:
            if venue.city == local['city'] and venue.state == local['state']:
                v = {
                    'id': venue.id,
                    'name': venue.name
                }
                local['venues'].append(v)

    # from pprint import pprint
    # pprint(locals)
    data = locals
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', ' ')
    data = []
    venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

    for venue in venues:
        num_upcoming_shows = 0
        shows = Show.query.filter(Show.venue_id == venue.id)
        for show in shows:
            if show.start_time > datetime.now():
                num_upcoming_shows +=1

        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows
        })

    response = {
        "count": len(venues),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    venue = Venue.query.get(venue_id)
    data = venue.venue_to_dictionary()

    pastshows = []
    upcomingshows = []

    past_shows = list(filter(lambda x: x.start_time < datetime.today(), venue.shows))
    upcoming_shows = list(filter(lambda x: x.start_time > datetime.today(), venue.shows))

    past_shows_count = len(past_shows)
    upcoming_shows_count = len(upcoming_shows)

    for pshow in past_shows:
        artist = Artist.query.get(pshow.artist_id)
        show = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": pshow.start_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        pastshows.append(show)

    print(pastshows)

    for fshow in upcoming_shows:
        artist = Artist.query.get(fshow.artist_id)
        show = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": fshow.start_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        upcomingshows.append(show)

    print(upcomingshows)

    data['past_shows'] = pastshows
    data['upcoming_shows'] = upcomingshows
    data['past_shows_count'] = len(pastshows)
    data['upcoming_shows_count'] = len(upcomingshows)
    print("data: ", data)

    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        venue_form = VenueForm(request.form)

        venue = Venue(name=venue_form.name.data,
                      city=venue_form.city.data,
                      state=venue_form.state.data,
                      address=venue_form.address.data,
                      phone=venue_form.phone.data,
                      genres=venue_form.genres.data,
                      facebook_link=venue_form.facebook_link.data,
                      image_link=venue_form.image_link.data,
                      website=venue_form.website_link.data,
                      seeking_talent=venue_form.seeking_talent.data,
                      seeking_description=venue_form.seeking_description.data
                      )
        print("Venue Name: ", venue.name)
        print("Venue Name: ", venue_form.name.data)

        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info)
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
            abort(500)
        else:
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
            # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    print("Inside DELETE")
    try:
        venue = Venue.query.get(venue_id)

        for show in venue.shows:
            db.session.delete(show)
        db.session.delete(venue)
        db.session.commit()
        print("Inside DELETE - TRY")
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        print("Inside DELETE - EXCEPT")
    finally:
        db.session.close()
        print("Inside DELETE - FINALLY")
        if error:
            # flash('An error occurred. Venue ' + request.form['name'] + ' could not be deleted.')
            print("Inside DELETE - FINALLY - ERROR = TRUE")
            abort(500)
        else:
            # on successful db insert, flash success
            # flash('Venue ' + request.form['name'] + ' was successfully deleted!')
            # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
            # clicking that button delete it from the db then redirect the user to the homepage
            print("Inside DELETE, before RETURN, error = FALSE")

        print("Inside DELETE - FINALLY, before return")
        # return render_template('pages/home.html')
        return jsonify({'success': True})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.order_by('id').all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # Sseach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', ' ')
    data = []
    artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

    for artist in artists:
        num_upcoming_shows = 0
        shows = Show.query.filter(Show.artist_id == artist.id)
        for show in shows:
            if show.start_time > datetime.now():
              num_upcoming_shows += 1

        data.append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": num_upcoming_shows
        })

    response = {
        "count": len(artists),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id

    artist = Artist.query.get(artist_id)

    # data = {}
    data = artist.artist_to_dictionary()

    pastshows = []
    upcomingshows = []

    past_shows = list(filter(lambda x: x.start_time < datetime.today(), artist.shows))
    upcoming_shows = list(filter(lambda x: x.start_time > datetime.today(), artist.shows))

    past_shows_count = len(past_shows)
    upcoming_shows_count = len(upcoming_shows)

    for pshow in past_shows:
        venue = Venue.query.get(pshow.venue_id)
        show = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": pshow.start_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        pastshows.append(show)

    print("past shows: ", pastshows)

    for fshow in upcoming_shows:
        venue = Venue.query.get(fshow.venue_id)
        show = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": fshow.start_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        print("Venue Image link: ", venue.image_link)
        upcomingshows.append(show)

    print("upcoming shows: ", upcomingshows)


    data['past_shows'] = pastshows
    data['upcoming_shows'] = upcomingshows
    data['past_shows_count'] = past_shows_count
    data['upcoming_shows_count'] = upcoming_shows_count

    print("data: ", data)

    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    # Get the artist with artist_id info from database
    artist = Artist.query.get(artist_id)

    # Fill the web form with the data pulled from the db for artist_id
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # artist record with ID <artist_id> using the new attributes
    error = False
    try:
        artist_form = ArtistForm(request.form)

        artist = Artist.query.get(artist_id)

        artist.name = artist_form.name.data
        artist.city = artist_form.city.data
        artist.state = artist_form.state.data
        artist.phone = artist_form.phone.data
        artist.genres = artist_form.genres.data
        artist.facebook_link = artist_form.facebook_link.data
        artist.image_link = artist_form.image_link.data
        artist.website = artist_form.website_link.data
        artist.seeking_venue = artist_form.seeking_venue.data
        artist.seeking_description = artist_form.seeking_description.data

        print("Imaage link: ", artist.image_link)

        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
            abort(500)
        else:
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully updated!')
            return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    # Get the venue with venue_id info from database
    venue = Venue.query.get(venue_id)

    # Fill the web form with the data pulled from the db for venue_id
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    try:
        venue_form = VenueForm(request.form)
        venue = Venue.query.get(venue_id)

        venue.name = venue_form.name.data
        venue.city = venue_form.city.data
        venue.state = venue_form.state.data
        venue.address = venue_form.address.data
        venue.phone = venue_form.phone.data
        venue.image_link = venue_form.image_link.data
        venue.genres = venue_form.genres.data
        venue.facebook_link = venue_form.facebook_link.data
        venue.website = venue_form.website_link.data
        venue.seeking_talent = venue_form.seeking_talent.data
        venue.seeking_description = venue_form.seeking_description.data

        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
            abort(500)
        else:
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully updated!')
            # venue record with ID <venue_id> using the new attributes
            return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()

    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    error = False
    try:
        artist_form = ArtistForm(request.form)

        artist = Artist(name=artist_form.name.data,
                        city=artist_form.city.data,
                        state=artist_form.state.data,
                        phone=artist_form.phone.data,
                        genres=artist_form.genres.data,
                        facebook_link=artist_form.facebook_link.data,
                        image_link=artist_form.image_link.data,
                        website=artist_form.website_link.data,
                        seeking_venue=artist_form.seeking_venue.data,
                        seeking_description=artist_form.seeking_description.data)

        print("Artist Name: ", artist.name)
        print("Artist Name: ", artist_form.name.data)

        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
            abort(500)
        else:
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    shows_query = db.session.query(Show).join(Artist).join(Venue).all()
    data =[]

    for show in shows_query:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    error = False
    try:
        show_form = ShowForm(request.form)

        show = Show(artist_id=show_form.artist_id.data,
                    venue_id=show_form.venue_id.data,
                    start_time=show_form.start_time.data)

        print("artist id:", show_form.artist_id.data)
        print("venue id:", show_form.venue_id.data)
        print("start time:", show_form.start_time.data)

        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        if error:
            print("Error!!!")
            flash('An error occurred. Show could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            abort(500)
        else:
            # on successful db insert, flash success
            flash('Show was successfully listed!')
            return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

