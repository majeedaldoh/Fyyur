#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import abort
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import * 
from models import db, Venue, Show, Artist
from flask_wtf.csrf import CSRFProtect
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db)
db = SQLAlchemy(app)
csrf = CSRFProtect()
# TODO: connect to a local postgresql database
# db = SQLAlchemy(app, db)
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
  # TODO: replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  # get the venues after group it by state and city
  venues = db.session.query(
    Venue.city,
    Venue.state).group_by(
    Venue.state,
    Venue.city).all()

  for venue in venues:
    num_upcoming_shows = 0
    venues_data = []
      # get the venues of specific state and city
    venues_list = Venue.query.filter(
      Venue.city == venue.city).filter(
      Venue.state == venue.state).all()

      # get the number of shows for a venue
    for venue in venues_list:
      upcoming_shows = Show.query.filter(
        Show.venue_id == venue.id).filter(
        Show.start_time > datetime.datetime.now()).all()
      for show in upcoming_shows:
          num_upcomming_shows +=1

          #add the require info of venue to a list
      venues_data.append({
        'id' : venue.id,
        'name': venue.name,
        'num_upcoming_shows': num_upcoming_shows
        })
          # add the requrie info of venue to a list
    data.append({
      'city': venue.city,
      'state': venue.state,
      'venues': venues_data
      })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  search_venues = []
  num_upcoming_shows = 0
  count = 0

  # Get the entered word from search box 
  search_term = request.form['search_term']
  search_data = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))

  # Get the upcoming shows of a venue
  for search in search_data:
    upcoming_shows = Show.query.filter(
      Show.venue_id == search.id).filter(
      Show.start_time > datetime.datetime.now()).all()
    for show in upcoming_shows:
      num_upcoming_shows +=1
      # Add the required info of searched to a list
    search_venues.append({
      'id': search.id,
      'name': search.name,
      'num_upcoming_shows': num_upcoming_shows
    })

    # Get the number of search results of a venue
  for search in search_data:
      count += 1

    # Get the requierd info of searched venue to a list
  response = {
      'count': count,
      'data': search_venues
    }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  past_shows_count = 0
  num_upcoming_shows = 0
  data = []

  # Get venue data by the given id
  venue_list = Venue.query.get(venue_id)

  # Check if the object exist or not

  if not venue_list:
    return render_template('/errors/404.html')
  else:
    # Get upcoming shows for this venue
    upcoming_shows = db.session.query(Show).join(Artist).filter(
      Show.venue_id == venue.id,
      Show.start_time >= datetime.datetime.now()).all()
      # Get the number of the upcomming shows of this venue
    for show in upcoming_shows:
      num_upcoming_shows += 1
      
    if num_upcoming_shows > 0:
        upcoming_shows_data = []

    # Get upcoming shows for this artist in the venue
    for show in upcoming_shows:
        venue = Venue.query.filter(
          Venue.id == show.venue_id).first()
      # add artist data to the list of upcoming shows
        upcoming_shows_data.append({
          'artist_id': show.artist_id,
          'artist_name' : show.artist.name,
          'artist_image_link' : show.artist.image_link,
          'start_time' : str(show.start_time)
          })
    # Get past shows for this venue 
    past_shows = db.session.query(Show).join(Artist).filter(
      Show.venue_id == venue_id,
      Show.start_time <= datetime.datetime.now()).all()
    # Get the number of past shows
    for show in past_shows:
      num_past_shows += 1
    # Get the past shows of the artists in the venue
    if num_past_shows > 0:
      past_shows_data = []

      for show in past_shows:
        venue = Venue.query.filter(
          Venue.id == show.venue_id).first()
    # add artist data to the list of past shows
        past_shows_data.append({
          'artist_id': show.artist.id,
          'artist_name': show.artist.name,
          'start_time': str(show.start_time)
          })

    ## add the venue data
    data = ({
      'id' : venue_list.id,
      'name': venue_list.name,
      'address': venue_list.address,
      'genres': venue_list.genres,
      'city': venue_list.city,
      'state': venue_list.state,
      'phone': venue_list.phone,
      'website_link': venue_list.website_link,
      'facebook_link': venue_list.facebook_link,
      'seeking_talent': venue_list.seeking_talent,
      'seeking_description': venue_list.seeking_description,
      'image_link': venue_list.image_link,
      'past_shows': venue_list.past_shows_data,
      'upcoming_shows': venue_list.upcoming_shows_data,
      'past_shows_count': num_past_shows,
      'upcoming_shows_count': venue_list.num_upcoming_shows
    })
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # form validation
  form = VenueForm(request.form)
  if not form.validate():
    for fieldName, errorMessage in form.errors.items():
      flash(errorMessage)
      return redirect(url_for('create_venue_form'))

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  image_link = request.form['image_link']
  website_link = request.form['website_link']
  facebook_link = request.form['facebook_link']
  seeking_talent = True if 'seeking_talent' in request.form else False
  seeking_description = request.form['seeking_description']

  # Get the required data to create new venue from the form
  new_venue = Venue(
    name=name,
    city=city,
    state=state,
    address=address,
    phone=phone,
    genres=genres,
    image_link=image_link,
    facebook_link=facebook_link,
    website_link=website_link,
    seeking_talent=seeking_talent,
    seeking_description=seeking_description,
    )
    # on successful db insert success
  try:
    Venue.create(new_venue)
    flash('venue' + request.form['name'] +'has been added successfully!')
  except BaseException:
    db.session.rollback()
    flash('an error accured venue '+ request.form['name'] +' could not been added')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.filter(id=venue_id).first()
  try:
    Venue.delete(venue)
    flash(+ venue.name + 'was deleted succussfully')
  except BaseException:
    flash(+ venue.name + 'was not deleted succussfully')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ---------------------------------------------------------------- 
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  artists_data = Artist.query.all()
  data = []
  for artist in artists_data:
    data.append({
      'id': artist.id,
      'name': artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_artists = []
  num_upcoming_shows = 0
  count = 0
  # get the enterd word from the search 
  search_term = request.form['search_term'] 
  search_data = Artist.query.filter(Artist.name.ilike('%' + search_term + '%'))

  # Get upcoming shows of an artist
  for search in search_data:
    upcoming_shows = Show.query.filter(
      Show.artist_id == search.id).filter(
        Show.start_time >= datetime.datetime.now()).all()
  # Get the number of upcoming shows
  for show in upcoming_shows > 0:
    num_upcoming_shows +=1

  search_artists.append({
    'id': search.id,
    'name': search.name,
    'num_upcoming_shows': num_upcoming_shows
  })

  for search in search_data:
      count +=1

  response = {
    'count': count,
    'data': search_artists
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  upcoming_shows_count = 0,
  past_shows_count = 0
  data = []
  
  arttist_list = Artist.query.get(artist_id)
  # Get the data of upcoming shows
  if not artist_list:
    return render_template('errors/404.html')
  else:
    upcoming_shows = db.session.query(Show).join(Venue).filter(
      Show.artist_id == artist_id).filter(
      Show.start_time>= datetime.datetime.now().all()
    )
    # Get the upcoming show count
    for show in upcoming_shows:
      upcoming_shows_count+=1
    if upcoming_shows_count > 0 : 
      upcoming_shows_data = []
      # get the data of venues 
    for show in upcoming_shows:
      show_venue = Venue.query.filter(
        Venue.id == show.venue_id).first()
    # Add the data of venue in upcoming shows to a list
    upcoming_shows_data.append({
      'venue_id': show_venue.id,
      'venue_name': show_venue.name,
      'venue_image_link': show_venue.image_link,
      'start_time': str(show.start_time)
    })

    past_shows = db.session.query(Show).join(Venue).filter(
    Show.artist_id == artist_id).filter(
      Show.start_time < datetime.datetime.now().all()
    )
    # Get the upcoming show count
    for show in past_shows:
      past_shows_count+=1

    if past_shows_count > 0 : 
      past_shows_data = []

    for show in past_shows:
      venue = Venue.query.filter(
        Venue.id == show.venue_id).first()

    past_shows_data.append({
      'venue_id': venue.id,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
      'start_time': str(show.start_time)
    })
    
  data = ({
    'id': artist_list.id,
    'name': artist_list.name,
    'address': artist_list.address,
    'geners': artist_list.geners,
    'city': artist_list.city,
    'state': artist_list.state,
    'phone': artist_list.phone,
    'website_link': artist_list.website_link,
    'facebook_link': artist_list.facebook_link,
    'seeking_venue': artist_list.seeking_venue,
    'seeking_description': artist_list.seeking_description,
    'image_link': artist_list.image_link,
    'past_shows': past_shows_data,
    'upcoming_shows': upcoming_shows_data,
    'past_shows_count': past_shows_count,
    'upcoming_shows_count': upcoming_shows_count
  })
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist = Artist.query.get(artist_id)

  form = ArtistForm()
  form.name.data = artist.name 
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artists.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm()
  if not form.validate():
    for fieldName, errorMessage in form.errors.items():
      flash(errorMessage)
      return redirect(url_for('edit_artist', artist_id = artist_id))
  
  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebool_link']
    artist.website_link = request.form['website_link']
    artist.image_link = request.form['image_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']
    Artist.update(artist)
    flash(" {} Info was updated successfully!".format(artist.name))
  except BaseException:
    db.session.rollback()
    flash(" {} Info wasn't updated successfully!".format(artist.name))
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue = Venue.query.get(venue_id)
  
  form = VenueForm()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.image_link.data = venue.image_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm()
  if not form.validate():
    for fieldName, errorMessage in form.errors.items():
      flash(errorMessage)
      return redirect(url_for('edit_venue', venue_id = venue_id))

  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.image_link = request.form['image_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']
    Venue.update(venue)
    flash(" {} info was updated successfully".format(venue.name))
  except BaseException:
    db.session.rollback()
    flash(" {} info was updated successfully".format(venue.name))
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id = venue_id))
  
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)

  if not form.validate():
    for fieldName, errorMessage in form.errors.items():
      flash(errorMessage)
      return redirect(url_for('create_artist_form'))
  
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link']
  website_link = request.form['website_link']
  image_link = request.form ['image_link']
  seeking_venue = True if 'seeking_venue' in request.form else False
  seeking_description = request.form['seeking_description']

  new_artist = Artist(
    name = name,
    city = city,
    state = state,
    phone = phone,
    genres = genres,
    facebook_link = facebook_link,
    website_link = website_link,
    image_link = image_link,
    seeking_venue = seeking_venue,
    seeking_description = seeking_description,
  )

  try:
    Artist.create(new_artist)
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except BaseException:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = [] 
  shows_data = Show.query.all()
  for show in shows_data:
    data.append({
    'venue_id': show.venue_id,
    'venue_name': show.venue.name,
    'artist_id': show.artist_id,
    'artist_name': show.artist.name,
    'artist_image_link': show.artist.image_link,
    'start_time': str(show.start_time)
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
  # TODO: insert form data as a new Show record in the db, instead

  form = ShowForm()

  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']

  new_show = Show(
    artist_id = artist_id,
    venue_id = venue_id,
    start_time = start_time
  )
  try:
    Show.create(new_show)
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except BaseException:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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