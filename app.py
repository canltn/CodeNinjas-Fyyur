import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)  

class Shows(db.Model):
    __tablename__ = 'Shows'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    #start_time = db.Column(db.DateTime)

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(800))
    showList = db.relationship('Shows', backref = 'venue', lazy='joined', cascade="all, delete")

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(800))
    showList = db.relationship('Shows', backref = 'artist', lazy='joined', cascade="all, delete")

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

@app.route('/')
def index():
  return render_template('pages/home.html')
@app.route('/venues')
def venues():
  cityandstate = Venue.query.distinct(Venue.city, Venue.state).all()
  venues = Venue.query.all()
  data = []
  for a in cityandstate:
        data.append({
            "city": a.city,
            "state": a.state,
            "venues": [{
                    "id": dt.id,
                    "name": dt.name,
                    "upcoming_shows": len([s for s in dt.showList if s.start_time > datetime.now()])} 
                for dt in venues if dt.city == a.city and dt.state == a.state]})
  return render_template("pages/venues.html", areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  condition_search = request.form.get("condition_search", "")
  filter = Venue.query.filter(Venue.name.like("f%{condition_search}%")).all()
  resultSearch = []
  countData = 0
  list = []
  for a in filter:
    upcoming_shows = []
    for show in a.showList:
      if show.start_time > datetime.now:
         upcoming_shows.append(show)
    countData: len(resultSearch)
    list: resultSearch.append({
      'id': a.id,
      'name': a.name,
      'num_upcoming_shows': len(upcoming_shows)
    })
  response={
    "count": countData,
    "data": list
  }
  return render_template('pages/search_venues.html', results=response, condition_search=request.form.get('condition_search', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = {}
  try:
    venue = Venue.query.get(venue_id)
    coming_Shows = []
    pastShows = []
    for show in venue.showList:
      if show.start_time > datetime.now():
        coming_Shows.append({
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time
        })
      else :
        pastShows.append({
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time
        })
    data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres.split(';'),
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": pastShows,
      "upcoming_shows": coming_Shows,
      "past_shows_count": len(pastShows),
      "upcoming_shows_count": len(coming_Shows)
    }
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/show_venue.html', venue=data)

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
	form = VenueForm()
	return render_template("forms/new_venue.html", form=form)

@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
	try:
		venue = Venue(
			name=request.form["name"],
			city=request.form["city"],
			state=request.form["state"],
			address=request.form["address"],
			phone=request.form["phone"],
			genres=request.form.getlist("genres"),
            facebook_link=request.form["facebook_link"],
			image_link=request.form["image_link"],
			website_link=request.form["website_link"],
			seeking_talent=True if "seeking_talent" in request.form else False,
			seeking_description=request.form["seeking_description"]
		)
		db.session.add(venue)
		db.session.commit()
		flash("Successfully!")
	except Exception as ex:
		print(ex)
		db.session.rollback()
		flash("An error occurred.")
	finally:
		db.session.close()
	return render_template("pages/home.html")

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
        venue = Venue.query.get_or_404(venue_id)
        db.session.delete(venue)
        db.session.commit()
  except Exception as ex:
        print(ex)
        flash("Venue could not be deleted.")
        db.session.rollback()
  finally:
        db.session.close()
  return render_template("pages/home.html")

@app.route('/artists')
def artists():
  data=db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
 searchCondition = "%{}%".format(request.form["search_term"])
 posts = Artist.query.filter(Artist.name.like(searchCondition)).all()
 list = []
 for row in posts:
    up_coming_Shows = []
    for show in row.showList:
      if show.start_time > datetime.now:
         up_coming_Shows.append(show)
    list.append({
      'id': row.id,
      'name': row.name,
      'num_upcoming_shows': len(up_coming_Shows)
    })
 response={
    "count": len(list),
    "data": list
  }
 return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  up_coming_Shows = []
  pastShow = []
  for show in artist.showList:
    show = {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime("%m/%D/%Y, %H:%M"),
    }
    if show.start_time > datetime.now():
      up_coming_Shows.append(show)
    else :
      pastShow.append(show)
      
  data = vars(artist)
  data['past_shows'] = pastShow
  data['past_shows_count'] = len(pastShow)
  data['upcoming_shows'] = up_coming_Shows
  data['upcoming_shows_count'] = len(up_coming_Shows)
  return render_template('pages/show_artist.html', artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get_or_404(artist_id)
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone 
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link
  return render_template("forms/edit_artist.html", form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form, meta={'csrf': False})
  artist = Artist.query.get_or_404(artist_id)
  if form.validate():
    try:
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.website_link = form.website_link.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        artist.image_link = form.image_link.data
        flash(f'Artist {request.form["name"]} was successfully updated!')
        db.session.commit()
    except Exception as ex:
        flash('An error occurred.')
        print(ex)
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("show_artist", artist_id=artist_id))
  else:
        flash('An error occurred.')
        return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get_or_404(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link
  return render_template("forms/edit_venue.html", form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form, meta={'csrf': False})
  venue = Venue.query.get_or_404(venue_id)
  if form.validate():
        try:
            venue.name = form.name.data
            venue.genres = form.genres.data
            venue.address = form.address.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.website_link = form.website_link.data
            venue.facebook_link = form.facebook_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            venue.image_link = form.image_link.data
            flash(f'Venue was successfully updated!')
            db.session.commit()
        except Exception as ex:
            flash(f'An error occurred. Venue {venue_id} could not be updated.')
            print(ex)
            db.session.rollback()
        finally:
            db.session.close()
        return redirect(url_for("show_venue", venue_id=venue_id))
  else:
        message = []
        for field, errors in form.errors.items():
            for error in errors:
                message.append(f"{field}: {error}")
        flash('Please fix the following errors: ' + ', '.join(message))
  return redirect(url_for('show_venue', venue_id=venue_id))

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
	try:
		post = Artist(
			name=request.form["name"],
			city=request.form["city"],
			state=request.form["state"],
			phone=request.form["phone"],
			genres=request.form.getlist("genres"),
			facebook_link=request.form["facebook_link"],
			image_link=request.form["image_link"],
			website_link=request.form["website_link"],
			seeking_venue=True if "seeking_venue" in request.form else False,
			seeking_description=request.form["seeking_description"]
		)
		db.session.add(post)
		db.session.commit()
		flash("Successfully")
	except Exception as ex:
		print(ex)
		db.session.rollback()
		flash("An error occurred.")
	finally:
		db.session.close()
	return render_template("pages/home.html")

@app.route('/shows')
def shows():
  showList = Shows.query.all()
  data = [{
        "venue_id": show.venue_id,
        "venue_name": show.Venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.Artist.name,
        "artist_image_link": show.Artist.image_link
    } for show in showList]
  return render_template("pages/shows.html", showList=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
	try:
		shows = shows(
			artist_id=request.form["artist_id"],
			venue_id=request.form["venue_id"],
			start_time=request.form["start_time"]
		)
		db.session.add(shows)
		db.session.commit()
		flash("Successfully!")
	except Exception as ex:
		print(ex)
		db.session.rollback()
		flash("Show was failed listed!")
	finally:
		db.session.close()
	return render_template("pages/home.html")

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
