import requests
from datetime import datetime
import time
from email.message import EmailMessage
import smtplib
import ssl


class Player:
  def __init__(self, name, plays):
    self.name = name
    self.plays = plays


class Match:
  def __init__(self, id, date_time, home_team, away_team, actual_quarter):
    self.id = id
    self.date_time = date_time
    self.home_team = home_team
    self.away_team = away_team
    self.actual_quarter = actual_quarter


def get_today_game_info(team_name):
    url_team_schedule = f'https://ar.global.nba.com/stats2/team/schedule.json?countryCode=AR&locale=es_AR&teamCode={team_name}'
    response = requests.get(url_team_schedule).json() 
    months = response.get('payload').get('monthGroups')

    actual_month = datetime.now().month
    actual_day = datetime.now().day
    info_month = list(filter(lambda x : x['number'] == actual_month, months))
    matches = info_month[0]['games']
    info_match = list(filter(lambda x : int(x['profile']['dateTimeEt'][8:10]) == actual_day, matches))
    try:
        game_date = info_match[0]['profile']['dateTimeEt']
        game_id = info_match[0]['profile']['gameId']
        home_team = info_match[0]['homeTeam']['profile']['abbr']
        away_team = info_match[0]['awayTeam']['profile']['abbr']

        return Match(game_id, game_date, home_team, away_team, 1)
    except:
        return Match(0,datetime.now(),'no one', 'no one', 1)


def get_plays(game):
    try:
        url_plays = f'https://ar.global.nba.com/stats2/game/playbyplay.json?gameId={game.id}&locale=es_AR&period={str(game.actual_quarter)}'
        response = requests.get(url_plays).json()
        plays = response.get('payload').get('playByPlays')[0].get('events')
        return plays
    except:
        return [{'description':'Nothing yet'}]


def add_plays_by_player(plays, player):
    for play in plays:
            if player.name in play.get('description') and play not in player.plays:
                print(play.get('description'))
                player.plays.append(play)
                if 'replaced by '+ player.name in play.get('description'):
                    send_email(player)
    return player


def check_if_quarter_ended(plays, game):
    for play in plays:
            if play.get('description') == 'End Period':
                print('Quarter '+ str(game.actual_quarter) +' finished')
                if game.actual_quarter == 1 or game.actual_quarter == 3:
                    time.sleep(10) #700
                elif game.actual_quarter == 2:
                    time.sleep(10) #180
                game.actual_quarter = game.actual_quarter + 1
    return game


def send_email(player):
    # Define email sender and receiver
    email_sender = 'ruizfranco2812@gmail.com'
    email_password = 'your password'
    email_receiver = 'franck2812@hotmail.com'

    # Set the subject and body of the email
    subject = 'Turn on the tv'
    body = f'{player.name} got in the game'

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # Add SSL (layer of security)
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())