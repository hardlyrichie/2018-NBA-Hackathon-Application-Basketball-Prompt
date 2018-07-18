#! python3

import csv, pprint

def main():
  # Write header of output csv
  fieldnames = ['Game_ID', 'Player_ID', 'Player_Plus/Minus']
  with open('Your_Team_Name_Q1_BBALL.csv', 'w', newline='') as output_file:    
          writer = csv.DictWriter(output_file, fieldnames=fieldnames)
          writer.writeheader()

  # Teams dict that holds player ids for each team on court currently
  teams = {}
  # Players dict that holds +/- for every player in game
  players = {}

  period_track = 0
  previous_event = None
  game_id = None
  sublist = []

  count = 2

  with open('data.csv', newline='') as data_file:
    data_reader = csv.DictReader(data_file)
    for row in data_reader:

      # Previous game ended, write to csv
      if game_id and row['Game_id'] != game_id:
        write_output(players, game_id, fieldnames)
        
        # Reset all values
        teams = {}
        players = {}
        period_track = 1
        previous_event = None
        sublist = []

      print(f'{count} {row["Event_Msg_Type_Description"]}'.center(100, '*'))

      team_id = row['Team_id_check']
      game_id = row['Game_id']
      period = row['Period']
      event = row['Event_Msg_Type_Description'].lower()

      # Fill teams with starting players at start of each period
      if period != period_track:
        period_track = period
        teams = {}
        print('GETTING LINEUP')
        with open('lineup.csv', newline='') as lineup_file:
          lineup_reader = csv.DictReader(lineup_file)
          for lineup_row in lineup_reader:
            # Get players from the right game and period
            if lineup_row['Game_id'] == game_id and lineup_row['Period'] == period:
              # Fill teams with starting player ids
              if not lineup_row['Team_id'] in teams:
                teams[lineup_row['Team_id']] = []
              teams[lineup_row['Team_id']].append(lineup_row['Person_id'])
              # Fill players if player is not already in list
              if not lineup_row['Person_id'] in players:
                players[lineup_row['Person_id']] = 0
              

      # Sub sublist
      if sublist and event != 'free throw' and (previous_event != 'substitution' or event != 'substitution'):
        print(sublist)
        for sub in sublist:
          teams[sub['team']] = substitute(sub['p1'], sub['p2'], teams[sub['team']])
        sublist = []

      # Calculate +/-
      points = int(row['Option1'])
      if event == 'substitution':
        # Sub later
        if previous_event == 'foul' or previous_event == 'free throw' or previous_event == 'substitution':
          sublist.append({
            'p1': row['Person1'],
            'p2': row['Person2'],
            'team': team_id
          })
        else:
          # Sub now
          teams[team_id] = substitute(row['Person1'], row['Person2'], teams[team_id])
        # Add player to players list if not already in
        if not row['Person2'] in players:
          players[row['Person2']] = 0
      elif event == 'made shot' or event == 'free throw': # points scored
        # Add points to players on court of team that scored
        for player in teams[team_id]:
          players[player] += points
        
        # Get id of other team
        other_team = list(teams.keys())
        other_team.remove(team_id)

        # Subtract points from players on court of team that did not score
        for player in teams[other_team[0]]:
          players[player] -= points

      pprint.pprint(teams)
      pprint.pprint(players)

      previous_event = event

      count += 1

      # if count == 500:
      #   break
  
  write_output(players, game_id, fieldnames)

# Substitute players
def substitute(p1, p2, team):
  print('SUBB')
  new_team = [p2 if p == p1 else p for p in team]
  return new_team

def write_output(players, game_id, fieldnames):
  with open('Your_Team_Name_Q1_BBALL.csv', 'a', newline='') as output_file:
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    for id, plus_minus in players.items():
      writer.writerow({'Game_ID': game_id, 'Player_ID': id, 'Player_Plus/Minus': plus_minus})

if __name__ == '__main__':
  main()
