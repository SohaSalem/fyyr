#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased
from datetime import datetime




#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
		__tablename__ = 'Venue'

		id = db.Column(db.Integer, primary_key=True)
		name = db.Column(db.String())
		city = db.Column(db.String(120))
		state = db.Column(db.String(120))
		address = db.Column(db.String(120))
		phone = db.Column(db.String(120))
		genres = db.Column(ARRAY(String))
		image_link = db.Column(db.String(500))
		facebook_link = db.Column(db.String(120))
		description = db.Column(db.String(500), default='')
		seeking_talent = db.Column(Boolean, default=False)
		website = db.Column(String(120))
		shows = db.relationship('Show', backref='Venue', lazy='dynamic')

		# TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
		__tablename__ = 'Artist'

		id = Column(Integer, primary_key=True)
		name = db.Column(db.String)
		city = db.Column(db.String(120))
		state = db.Column(db.String(120))
		phone = db.Column(db.String(120))
		genres = db.Column(ARRAY(String))
		image_link = db.Column(db.String(500))
		facebook_link = db.Column(db.String(120))
		seeking_venue = db.Column(db.Boolean, default=False)
		seeking_description = db.Column(db.String(120), default=' ')
		website = db.Column(db.String(120))
		shows = db.relationship('Show', backref='Artist', lazy=True)


class Show(db.Model):
		__tablename__ = 'Show'

		id = db.Column(Integer,primary_key=True)
		venue_id = db.Column(Integer, ForeignKey(Venue.id), nullable=False)
		artist_id = db.Column(Integer, ForeignKey(Artist.id), nullable=False)
		start_time = db.Column(String(), nullable=False)

# TODO: implement any missing fields, as a database migration using Flask-Migrate
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
	date = dateutil.parser.parse(value)
	if format == 'full':
			format="EEEE MMMM, d, y 'at' h:mma"
	elif format == 'medium':
			format="EE MM, dd, y h:mma"
	return babel.dates.format_datetime(date, format)

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
	#       num_shows should be aggregated based on number of upcoming shows per venue.
	venues = Venue.query.all()
	cities = set()
	for venue in venues:
		cities.add((venue.city, venue.state))
	
	data = []

	for city in cities:
		city_venues = Venue.query.filter_by(city=city[0], state=city[1]).all()
		city_data = {
			'city': city[0],
			'state': city[1],
			'venues': city_venues
		}
		data.append(city_data)

	return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
	# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
	# seach for Hop should return "The Musical Hop".
	# search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
	search_term = request.form['search_term']
	result = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

	response = {
		"count":len(result),
		"data": result
	}
	return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
	# shows the venue page with the given venue_id
	# TODO: replace with real venue data from the venues table, using venue_id
	venue = Venue.query.get(venue_id)
	current_datetime = datetime.now()
	venue_shows = Show.query.filter_by(venue_id=venue_id)
	past_shows = []
	upcoming_shows = []
	for show in venue_shows:
		show_artist = Artist.query.get(show.artist_id)
		if(show.start_time < current_datetime.strftime("%d-%m-%Y %H:%M:%S")):
			past_shows.append({
				'artist_id': show_artist.id,
				'artist_name': show_artist.name,
				'artist_image_link': show_artist.image_link,
				'start_time': show.start_time
			})
		else:
			upcoming_shows.append({
				'artist_id': show_artist.id,
				'artist_name': show_artist.name,
				'artist_image_link': show_artist.image_link,
				'start_time': show.start_time
			})

	venue_data={
		"id": venue.id,
		"name": venue.name,
		"genres": venue.genres,
		"address": venue.address,
		"city": venue.city,
		"state": venue.state,
		"phone": venue.phone,
		"website": venue.website,
		"facebook_link": venue.facebook_link,
		"seeking_talent": venue.seeking_talent,
		"seeking_description": venue.description,
		"image_link": venue.image_link,
		"past_shows": past_shows,
		"upcoming_shows": upcoming_shows,
		"past_shows_count": len(past_shows),
		"upcoming_shows_count": len(upcoming_shows),
	}
	
 
	return render_template('pages/show_venue.html', venue=venue_data)

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
		try:
				seeking_talent = False
				seeking_description = ''
				if 'seeking_talent' in request.form:
					seeking_talent = request.form['seeking_talent'] == 'y'
				if 'seeking_description' in request.form:
					seeking_description = request.form['seeking_description']
				venue = Venue(
					name=request.form['name'],
					city=request.form['city'],
					state=request.form['state'],
					address=request.form['address'],
					phone=request.form['phone'],
					genres=request.form.getlist('genres'),
					image_link=request.form['image_link'],
					facebook_link=request.form['facebook_link'],
					seeking_talent=seeking_talent,
			    description=seeking_description,
					website=request.form['website']
					)
				db.session.add(venue)
				db.session.commit()
				flash('Venue ' + request.form['name'] + ' was successfully listed!')
		except SQLAlchemyError as e:
				flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

		return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
	# TODO: Complete this endpoint for taking a venue_id, and using
	# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

	# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
	# clicking that button delete it from the db then redirect the user to the homepage
	return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
	# TODO: replace with real data returned from querying the database

	return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
	# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
	# seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
	# search for "band" should return "The Wild Sax Band".
	search_term=request.form['search_term']
	result=Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
	response={
		"count": len(result),
		"data": result
	}
	return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	# shows the venue page with the given venue_id
	# TODO: replace with real venue data from the venues table, using venue_id
	artist = Artist.query.get(artist_id)
	current_datetime = datetime.now()
	artist_shows = Show.query.filter_by(artist_id=artist_id)
	past_shows = []
	upcoming_shows = []
	for show in artist_shows:
		show_venue = Venue.query.get(show.venue_id)
		if(show.start_time < current_datetime.strftime('%Y-%m-%d %H:%M:%S')):
			past_shows.append({
				'venue_id': show_venue.id,
				'venue_name': show_venue.name,
				'venue_image_link': show_venue.image_link,
				'start_time': show.start_time
			})
		else:
			upcoming_shows.append({
				'artist_id': show_venue.id,
				'artist_name': show_venue.name,
				'artist_image_link': show_venue.image_link,
				'start_time': show.start_time
			})

	artist_data={
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

 
	return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
	form = ArtistForm()
	artist={
		"id": 4,
		"name": "Guns N Petals",
		"genres": ["Rock n Roll"],
		"city": "San Francisco",
		"state": "CA",
		"phone": "326-123-5000",
		"website": "https://www.gunsnpetalsband.com",
		"facebook_link": "https://www.facebook.com/GunsNPetals",
		"seeking_venue": True,
		"seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
		"image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
	}
	# TODO: populate form with fields from artist with ID <artist_id>
	return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
	# TODO: take values from the form submitted, and update existing
	# artist record with ID <artist_id> using the new attributes

	return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
	form = VenueForm()
	venue={
		"id": 1,
		"name": "The Musical Hop",
		"genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
		"address": "1015 Folsom Street",
		"city": "San Francisco",
		"state": "CA",
		"phone": "123-123-1234",
		"website": "https://www.themusicalhop.com",
		"facebook_link": "https://www.facebook.com/TheMusicalHop",
		"seeking_talent": True,
		"seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
		"image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
	}
	# TODO: populate form with values from venue with ID <venue_id>
	return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
	# TODO: take values from the form submitted, and update existing
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
	# TODO: insert form data as a new Venue record in the db, instead
	try:
		seeking_venue = False
		seeking_description = ''
		if 'seeking_venue' in request.form:
			seeking_venue = request.form['seeking_venue'] == 'y'
		if 'seeking_description' in request.form:
			seeking_description = request.form['seeking_description']
			new_artist = Artist(
			name=request.form['name'],
			genres=request.form.getlist('genres'),
			city=request.form['city'],
			state= request.form['state'],
			phone=request.form['phone'],
			image_link=request.form['image_link'],
			facebook_link=request.form['facebook_link'],
			website=request.form['website'],
			seeking_venue=seeking_venue,
			seeking_description=seeking_description,
		)

		db.session.add(new_artist)
		db.session.commit()
	# on successful db insert, flash success
		flash('Artist ' + request.form['name'] + ' was successfully listed!')
	except SQLAlchemyError as e:
	# TODO: on unsuccessful db insert, flash an error instead.
	# e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
		flash('An error occurred. Artist ' + request.form['name'] + 'could not be listed. ')
 
	return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
	# displays list of shows at /shows
	# TODO: replace with real venues data.
	#       num_shows should be aggregated based on number of upcoming shows per venue.
	shows = Show.query.all()
	shows_data = []
	
	for show in shows:
		show_artist = Artist.query.get(show.artist_id)
		show_venue = Venue.query.get(show.venue_id)
		shows_data.append({
			"venue_id": show_venue.id,
			"venue_name": show_venue.name,
			"artist_id": show_artist.id,
			"artist_name": show_artist.name,
			"artist_image_link": show_artist.image_link,
			"start_time": show.start_time
		})

	return render_template('pages/shows.html', shows=shows_data)

@app.route('/shows/create')
def create_shows():
	# renders form. do not touch.
	form = ShowForm()
	return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
	# called to create new shows in the db, upon submitting new show listing form
	# TODO: insert form data as a new Show record in the db, instead

	try:
		if request.form:
				show = Show(
					venue_id=request.form['venue_id'],
					artist_id=request.form['artist_id'],
					start_time=request.form['start_time']
				)
				db.session.add(show)
				db.session.commit()
				flash('Show was successfully listed!')
	except SQLAlchemyError as e:
		flash('An error occurred. Show could not be listed.')

	# on successful db insert, flash success
	# TODO: on unsuccessful db insert, flash an error instead.
	# e.g., flash('An error occurred. Show could not be listed.')
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
