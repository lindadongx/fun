import pandas as pd
import numpy as np

INFINITY = 999999999

class Account:
  """Representation of loyalty account containing points to be redeemed."""

  def __init__(self, program, balance = 0):
    self.balance = int(balance)
    self.program = str(program)
    if self.program == None:
        raise Exception("Please specify the Program your account belongs to (United or American Airlines).")
    self.deposit_count = 0
    self.redemption_count = 0

  def deposit(self, deposit_amt):
    self.last_deposit_amt = deposit_amt
    if deposit_amt < 0:
        raise Exception("You cannot deposit a negative amount of points.")
    self.deposit_count += 1
    self.balance += deposit_amt
    print("You have deposited " + str(self.last_deposit_amt) + " points.")

  def redeem(self, redeem_amt):
    self.last_redeem_amt = redeem_amt
    if redeem_amt > self.balance:
        raise Exception("You do not have enough points for this redemption.")
    self.redemption_count += 1
    self.balance -= redeem_amt
    print("You have redeemed " + str(self.last_redeem_amt) + " points.")

  def balance_check(self):
    print("Your " + str(self.program) + " rewards balance is " + str(self.balance) + " points.")

class DataLoader:
  """Service to load current airline rewards data in CSV format."""

  def __init__ (self, file_path):
    df = pd.read_csv(file_path)
    self.rewards = df
    assert set(self.rewards.keys()) == set(['airline','points_cost','destination_region','destination_country']), "Dataset is not formatted correctly."

class Matcher:
  """Service to match user with the roundtrip reward flights they can redeem, given their rewards account balances."""

  def __init__(self):
      pass

  def find_region(self, account, rewards):
    all_results = rewards[(rewards['airline'] == account.program) & (rewards['points_cost'] <= 0.5 * account.balance)]
    unique_results = all_results.destination_region.unique()
    unique_results.sort()
    return unique_results

  def combine_region_results(self, account_american, account_united, rewards):
    american_results = self.find_region(account_american, rewards)
    united_results = self.find_region(account_united, rewards)
    combined_results = np.unique(np.concatenate([american_results, united_results]))
    return combined_results

  def find_country(self, account, rewards, region):
    all_results = rewards[(rewards['airline'] == account.program) & (rewards['destination_region'] == region.lower()) & (rewards['points_cost'] <= 0.5 * account.balance)]
    unique_results = all_results.destination_country.unique()
    unique_results.sort()
    return unique_results

  def combine_country_results(self, account_american, account_united, rewards, region_selection):
    american_results = self.find_country(account_american, rewards, region_selection)
    united_results = self.find_country(account_united, rewards, region_selection)
    combined_results = np.unique(np.concatenate([american_results, united_results]))
    return combined_results

  def find_country_cost_for_airline(self, account, rewards, country):
    all_results = rewards[(rewards['airline'] == account.program) & (rewards['destination_country'] == country.lower()) & (rewards['points_cost'] <= 0.5 * account.balance)]
    assert len(all_results) <= 1, "Table contains duplicate values. Reload data table."
    if len(all_results) == 0:
      cost = INFINITY
    else:
      cost = all_results['points_cost'].iloc[0]
    return cost

  def compare_country_cost_for_airlines(self, american_cost, united_cost):
    if american_cost != INFINITY:
      print("This roundtrip flight on American Airlines costs " + str(2 * american_cost) + " points.")
    if united_cost != INFINITY:
      print("This roundtrip flight on United Airlines costs " + str(2 * united_cost) + " points.")
    if american_cost > united_cost:
      print("We recommend you redeem with United Airlines as the points cost is cheaper.")
    elif american_cost == united_cost:
      print("You may fly with either American or United Airlines for the same points cost.")
    else:
      print("We recommend you redeem with American Airlines as the points cost is cheaper.")


#begin!

load = DataLoader(str(input("Enter file location of CSV containing source rewards data: ")))
account_american = Account("american airlines", int(input("Enter the current balance of your American Airlines rewards account: ")))
account_united = Account("united airlines", int(input("Enter the current balance of your United Airlines rewards account: ")))
matcher = Matcher()
combined_region_results = matcher.combine_region_results(account_american, account_united, load.rewards)
if len(combined_region_results) == 0:
  print("You do not have enough points to redeem roundtrip flights on either American or United Airlines.")
else:
  print("All available regional destinations for a roundtrip flight using current rewards balances: ")
  for reward in combined_region_results:
    print(reward)
  region_selection = str(input("Enter the region you wish to travel to: "))
  combined_country_results = matcher.combine_country_results(account_american,account_united, load.rewards, region_selection)
  print("All available country destinations for a roundtrip flight using current rewards balances: ")
  for reward in combined_country_results:
    print(reward)
  country_selection = str(input("Enter the country you wish to travel to: "))
  american_cost = matcher.find_country_cost_for_airline(account_american, load.rewards, country_selection)
  united_cost = matcher.find_country_cost_for_airline(account_united, load.rewards, country_selection)
  matcher.compare_country_cost_for_airlines(american_cost, united_cost)

