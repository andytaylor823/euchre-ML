from inspect import signature  # use this to check the "condition" argument

# Rule's main feature is its "condition" argument
# A standardized way of passing in many different functions looking for many different things in a hand
# Every rule must accept as args: Board and Player. This is all that should be needed to make a choice
class Rule:
	def __init__(self, condition, rule_type, name='rule'):
		if not callable(condition):
			print('Error: condition argument must be a callable function')
			raise(ValueError)
		sig = signature(condition)
		if len(sig.parameters) != 2:
			print('Error: condition argument can only take two arguments')
			raise(ValueError)
		if not isinstance(rule_type, str):
			print('Error: rule_type argument must be a string')
			raise(ValueError)
		if rule_type.lower() not in ['lead', 'follow', 'call']:
			print('Error: rule_type argument can only be "lead", "follow", or "call"')
			raise(ValueError)
		
		self.type = rule_type
		self.condition = condition
		self.name = name
	
	def is_satisfied(self, board, player):
		if self.type.lower() == 'call':
			return self.condition(board, player)
		else:
			c = self.condition(board, player)
			return c # c can be none
	