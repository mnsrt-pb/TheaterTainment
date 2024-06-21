from datetime import datetime, timedelta


yesterday =  (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
tomorrow = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
day_after_tomorrow = (datetime.now() + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)


movie_a = dict(
    tmdb_id = 128,
    title = 'Princess Mononoke',
    route = 'princess-mononoke',
    status = 'Released',
    release_date = datetime.strptime('2001-07-20', '%Y-%m-%d').date(),
    runtime = 134,
    poster_path = '/kifrm5sCZNMa1GsSAANg040Hay5.jpg',
    backdrop_path = '/yoIybVuiUWtDf2X8dCt4vZgfC3q.jpg',
    trailer_path = 'opCxPAwdB6U',
    rating = 'PG-13',
    overview = 'Ashitaka, a prince of the disappearing Emishi people, is cursed by a demonized boar god and must journey to the west to find a cure. Along the way, he encounters San, a young human woman fighting to protect the forest, and Lady Eboshi, who is trying to destroy it. Ashitaka must find a way to bring balance to this conflict.',
)

movie_b = dict(
    tmdb_id = 129,
    title = 'Spirited Away',
    route = 'spirited-away',
    status = 'Released',
    overview = 'A young girl, Chihiro, becomes trapped in a strange new world of spirits. When her parents undergo a mysterious transformation, she must call upon the courage she never knew she had to free her family.',
    release_date = day_after_tomorrow.replace(hour=0, minute=0, second=0, microsecond=0),
    runtime = 125,
    rating = 'PG',
    poster_path = '/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg',
    backdrop_path = '/ogRfsqklWMRpzmq4ZJcI0MvqzlN.jpg',
    trailer_path = 'GAp2_0JJskk'
)

visa = dict(
    card_type = 'Visa',
    card_number = '4032033067980677',
    exp_month = 5,
    exp_year = datetime.today().year + 1,
    zip_code = '44444', # NOTE: cannot be '00000' because of tests
    sec_code = '335' # NOTE: cannot be '000' because of tests
)

showtime_data = dict(
    m_id = 1, # NOTE: It is assumed that there is at least one movie
    a_id = 1, # NOTE: This is dependent on the auditoriums in the theater
    date_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0), # tomorrow at 10AM
    adult_price = 12.5,
    child_price = 10.5,
    senior_price = 9
)

