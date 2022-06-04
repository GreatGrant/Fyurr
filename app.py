#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
from sys import exc_info
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for
)
from sqlalchemy import ARRAY, String
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate
from models import db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
# ---------------------
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
    artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
    return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venues = db.session.query(Venue.city, Venue.state).distinct(
        Venue.city, Venue.state)
    data = []
    for venue in venues:
        venues_within_city = db.session.query(Venue.id, Venue.name).filter(
            Venue.city == venue.city).filter(Venue.state == venue.state)

        data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": venues_within_city
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    user_search_request = request.form['search_term']
    venue_result = Venue.query.filter(
        Venue.name.ilike(f'%{user_search_request}%')).all()
    data = []
    for result in venue_result:
        data.append({
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": len(result.shows)
        })

    response = {
        "count": len(venue_result),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    filtered_venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

    past_shows = []
    upcoming_shows = []

    data = {
        "id": filtered_venue.id,
        "name": filtered_venue.name,
        "genres": filtered_venue.genre,
        "address": filtered_venue.address,
        "city": filtered_venue.city,
        "state": filtered_venue.state,
        "phone": filtered_venue.phone,
        "website": filtered_venue.website_link,
        "facebook_link": filtered_venue.facebook_link,
        "seeking_talent": filtered_venue.seeking_talent,
        "seeking_description": filtered_venue.seeking_description,
        "image_link": filtered_venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    shows_of_venue = db.session.query(Show).filter(Show.venue_id == venue_id)

    for show in shows_of_venue:
        artist = db.session.query(Artist.name, Artist.image_link).filter(
            Artist.id == show.artist_id).one()

        if (show.start_time < datetime.now()):
            past_shows.append({
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time.strftime('%m/%d/%Y')
            })
        else:
            upcoming_shows.append({
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time.strftime('%m/%d/%Y')
            })

    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows
    data["past_shows_count"] = len(past_shows)
    data["upcoming_shows_count"] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)

    venue = Venue(
        name=form.name.data,
        genre=form.genres.data,
        address=form.address.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        website_link=form.website_link.data,
        facebook_link=form.facebook_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data,
        image_link=form.image_link.data,
    )
    try:
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash(f'Venue  {form.name.data} was successfully listed!')
    except:
        flash(
            f'An error occurred. Venue {form.name.data}  could not be added.')
        print('exc_info()', exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('venues'))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue_to_delete = Venue.query.filter(Venue.id == 'venue_id').all()
        db.session.delete(venue_to_delete)
        db.session.commit()
        flash('Venue successfully deleted!')
    except:
        db.rollback()
        print(exc_info())
        flash('Error: Venue could not be deleted')
    finally:
        db.session.close()

    return redirect(url_for('venues'))
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    # return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():

    user_search_request = request.form['search_term']
    artists_search_result = Artist.query.filter(
        Artist.name.ilike(f'%{user_search_request}%')).all()
    data = []

    for artist in artists_search_result:
        num_upcoming_shows = 0
        shows = db.session.query(Show).filter(Show.artist_id == artist.id)
        for show in shows:
            if(show.start_time > datetime.now()):
                num_upcoming_shows += 1

        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming_shows
        })
    response = {
        "count": len(artists_search_result),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
    past_shows = []
    upcoming_shows = []

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    shows = db.session.query(Show).filter(Show.artist_id == artist_id)
    # Iterate through shows to get needed show details
    for show in shows:
        venue = db.session.query(Venue.name, Venue.image_link).filter(
            Venue.id == show.venue_id).one()
        if (show.start_time < datetime.now()):
            past_shows.append({
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time.strftime('%m/%d/%Y')
            })
        else:
            upcoming_shows.append({
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time.strftime('%m/%d/%Y')
            })

        # Update data with new show details
    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows
    data["past_shows_count"] = len(past_shows)
    data["upcoming_shows_count"] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist_to_edit = db.session.query(
        Artist).filter(Artist.id == artist_id).one()
    return render_template('forms/edit_artist.html', form=form, artist=artist_to_edit)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    artist_to_update = Artist.query.filter(Artist.id == artist_id)

    # updated artist based on user input
    updated_artist_details = {
        "name": form.name.data,
        "genres": form.genres.data,
        "city": form.city.data,
        "state": form.state.data,
        "phone": form.phone.data,
        "website": form.website_link.data,
        "facebook_link": form.facebook_link.data,
        "seeking_venue": form.seeking_venue.data,
        "seeking_description": form.seeking_description.data,
        "image_link": form.image_link.data,
    }

    try:
        artist_to_update.update(updated_artist_details)
        db.session.commit()
        flash(f'Artist {form.name.data}  was successfully updated!')
    except:
        db.session.rollback()
        flash(
            f'An error occurred. artist {form.name.data}  could not be updated.')
        print('exc_info(): ', exc_info())
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter(Venue.id == venue_id).one()
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    venue_to_update = Venue.query.filter(Venue.id == venue_id)

    # Details of venue to be updated based on user input from form
    updated_venue_details = {
        "name": form.name.data,
        "genre": form.genres.data,
        "address": form.address.data,
        "city": form.city.data,
        "state": form.state.data,
        "phone": form.phone.data,
        "website_link": form.website_link.data,
        "facebook_link": form.facebook_link.data,
        "seeking_talent": form.seeking_talent.data,
        "seeking_description": form.seeking_description.data,
        "image_link": form.image_link.data
    }
    try:
        venue_to_update.update(updated_venue_details)
        db.session.commit()
        flash('Venue' + form.name.data + ' was successfully updated!')
    except:
        print('exc_info() ', exc_info())
        db.session.rollback()
        flash('An error occurred. Venue ' +
              form.name.data + ' could not be updated.')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)

    # artist created based on user's input
    created_artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.city.data,
        phone=form.phone.data,
        genres=form.genres.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website=form.website_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data
    )
    try:
        db.session.add(created_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              form.name.data + ' could not be listed.')
        print('exc_info()', exc_info())
    finally:
        return redirect(url_for('artists'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = db.session.query(Show).join(Artist).join(Venue).all()
    data = []
    for show in shows:
        data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)

    # show created based on user's input
    created_show = Show(
        artist_id=form.artist_id.data,
        venue_id=form.venue_id.data,
        start_time=form.start_time.data,
    )
    try:
        db.session.add(created_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
        print('exc_info()', exc_info())
    finally:
        db.session.close()

    return redirect(url_for('shows'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


@app.errorhandler(401)
def unauthorized(error):
    return render_template('errors/401.html'), 401


@app.errorhandler(405)
def invalid_method(error):
    return render_template('errors/405.html'), 405


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
