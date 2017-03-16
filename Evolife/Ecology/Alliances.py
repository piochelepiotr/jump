#!/usr/bin/env python
##############################################################################
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Alliances                                                                 #
##############################################################################

""" EVOLIFE: Module Alliances:
		Individuals inherit this class
		which determines who is friend with whom
"""

import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests


from Evolife.Tools.Tools import error

class club(object):
	""" class club: list of individuals associated with their performance.
		The performance is used to decide who gets acquainted with whom.
	"""

	def __init__(self, owner, sizeMax = 0):
		self.__members = []   # list of couples (individual,performance)
		self.sizeMax = sizeMax
		if sizeMax == 0:
			self.sizeMax = sys.maxsize

	# def members(self):	return self.__members
	
	def names(self):	return [T[0] for T in self]

	def performances(self):	return [T[1] for T in self]
		
	def present(self, MemberPerf):	return MemberPerf in self
			
	def ordered(self, ordered=True):
		if ordered:
			return [T[0] for T in sorted(self.__members, key = lambda x: x[1], reverse=True)]
		return [T[0] for T in self]
		
	def rank(self, Member):
		try:	return self.ordered().index(Member)
		except ValueError:	return -1

	def performance(self, Member):
		try:	return self.__members[self.names().index(Member)][1]
		except ValueError:	error('Alliances', 'Searching for non-member')
	
	def size(self):	return len(self.__members)

	def minimal(self):
		" returns the minimal performance among members "
		if self.size():	return min([T[1] for T in self])
		return -1

	def maximal(self):
		" returns the maximal performance among members "		
		if self.size():	return max([T[1] for T in self])
		return -1

	def best(self):
		" returns the member with the best performance "
		# if self.size():	return self.ordered()[0]
		# if self.size():	return max([T for T in self.__members], key=lambda x: x[1])[0]
		if self.size():	return max(self, key=lambda x: x[1])[0]
		return None

	def worst(self):
		" returns the member with the worst performance "
		if self.size():	return self.ordered()[-1]
		return None

	def accepts(self, performance, conservative=True):
		" signals that the new individual can be accepted into the club "
		if self.size() >= self.sizeMax:
			if conservative and performance <= self.minimal():
				return -1   # equality: priority given to former members
			elif performance < self.minimal():	return -1
			# print 'acceptation de', performance, 'a la place de', self.minimal()
		# returning the rank that the candidate would be assigned
		#  return sorted([performance] + self.performances(),reverse=True).index(performance)
		rank = self.size() - sorted([performance] + self.performances()).index(performance)
		if rank <= self.sizeMax:	return rank
		error('Alliances', 'accept')
		
	def enters(self, newMember, performance, conservative=True):
		if self.accepts(performance, conservative=conservative) >= 0:
			# First, check whether newMember is not already a member
			if newMember in self.names():
				self.exits(newMember)   # to prepare the come-back
			if self.size() >= self.sizeMax:
				worst = self.worst() # the redundant individual will be ejected
			else:	worst = None
			self.__members.append((newMember, performance))
			return worst
		error("Alliances: unchecked admittance")
		return None

	def exits(self, oldMember):
		" a member goes out from the club "
		for (M,Perf) in self.__members[:]:  # safe to copy the list as it is changed within the loop
			if M == oldMember:
				self.__members.remove((oldMember,Perf))
				return True
		print('exiled: %s' % str(oldMember))
		error('Alliances: non-member attempting to quit a club')
		return False

	def weakening(self, Factor = 0.9):  # temporary value
		" all performances are reduced (represents temporal erosion)  "
		for (M,Perf) in self.__members[:]:  # safe to copy the list as it is changed within the loop
			self.__members.remove((M, Perf))
			self.__members.append((M, Perf * Factor))

	def __iter__(self):	return iter(self.__members)
		
	def __str__(self):
		# return "[" + '-'.join([T.id for T in self.ordered()]) + "]"
		return "[" + '-'.join([str(T) for T in self.names()]) + "]"

class Friend:
	"	class Friend: defines an individual's acqaintances "
	def __init__(self, MaxFriends=1):
		self.friends = club(self, MaxFriends)
	
	#################################
	# asymmetrical links            #
	#################################
	def accepts(self, F_perf):	return	self.friends.accepts(F_perf)
	
	def affiliable(self, F_perf, conservative=True):
		" Checks whether affiliation is possible "
		return	self.friends.accepts(F_perf, conservative=conservative) >= 0

	def follow(self, F, F_perf, conservative=True, Quit=None):
		""" the individual wants to be F's disciple due to F's performance
		"""
		# print self.id, "wants to follows", (F.id, F_perf)
		if self.affiliable(F_perf, conservative=conservative):
			# the new friend is good enough
			RF = self.friends.enters(F, F_perf, conservative=conservative)	# returns ejected old friend
			if RF is not None:
				# print('redundant friend of %s: %s' % (self, RF))
				# print('self: %s' % self, ">>> self's friends: %s " % map(str, Friend.social_signature(self)))
				if Quit is None: Quit = self.quit_
				Quit(RF)   # some redundant friend is disowned
			return True
		else:	return False
			
	def follows(self, Friend):	return Friend in self.names()
		# R = Friend in self.friends.names()
		# if R: print self.id, 'is already following', Friend.id
	
	def quit_(self, Friend=None):
		""" the individual no longer follows its friend
		"""
		if Friend is None: Friend = self.friends.worst()
		if Friend is not None:
			# print(self, 'quits ', Friend)
			self.friends.exits(Friend)
	
	def best_friend(self):	return self.friends.best()
	
	def Max(self):	return max(0, self.friends.maximal())
	
	def Friends(self, ordered=True):	return self.friends.ordered(ordered=ordered)

	def names(self):	return self.friends.ordered(ordered=False)
	
	def rank(self, Friend):	return self.friends.rank(Friend)
	
	def nbFriends(self):	return self.friends.size()
	def size(self):			return self.friends.size()
	def sizeMax(self):		return self.friends.sizeMax

	def lessening_friendship(self, Factor=0.9):
		self.friends.weakening(Factor)					

	def checkNetwork(self, membershipFunction=None):
		" updates links by forgetting friends that are gone "
		for F in self:
			if not membershipFunction(F):	self.quit_(F)
		
	def detach(self):
		""" The individual quits its friends	"""
		for F in self:	self.quit_(F)
		
	#################################
	# symmetrical links             #
	#################################
	def acquaintable(self, Offer, Partner, PartnerOffer):
		return self.affiliable(PartnerOffer) and Partner.affiliable(Offer)
	
	def get_friend(self, Offer, Partner, PartnerOffer):
		" Checks mutual acceptance before establishing friendship "
		if self.acquaintable(Offer, Partner, PartnerOffer):
			if not self.follow(Partner, PartnerOffer, Quit=self.end_friendship):
				error("Friend: self changed mind")
			if not Partner.follow(self, Offer, Quit=Partner.end_friendship):
				error("Friend: Partner changed mind")
			return True
		return False
		
	def end_friendship(self, Partner):
		" Partners remove each other from their address book "
		# print('\nsplitting up', self.id, Partner.id)
		self.quit_(Partner)
		Partner.quit_(self)

	def forgetAll(self):
		""" The individual quits its friends	"""
		for F in self:	self.end_friendship(F)

	def __iter__(self):	return iter(self.friends.names())
		
	def social_signature(self):
		# return [F.id for F in self.friends.names()]
		return self.friends.ordered()

	def signature(self):	return self.social_signature()

class Follower(Friend):
	" Augmented version of Friends for asymmetrical links - replaces 'Alliances' "
	def __init__(self, MaxGurus, MaxFollowers=0):
		Friend.__init__(self, MaxGurus)
		if MaxFollowers:
			self.followers = Friend(MaxFollowers)	# 'Friend' used as a mirror class to keep track of followers
		else:	self.followers = None
	
	def F_affiliable(self, perf, Guru, G_perf, conservative=True):
		" Checks whether affiliation is possible "
		A = self.affiliable(G_perf, conservative=conservative)	# Guru is acceptable and
		if self.followers is not None:	A &= Guru.followers.affiliable(perf, conservative=conservative)	# self acceptable to Guru
		return A
	
	def F_follow(self, perf, G, G_perf, conservative=True):
		""" the individual wants to be G's disciple because of some of G's performance
			G may evaluate the individual's performance too
		"""
		# print '.',
		if self.F_affiliable(perf, G, G_perf, conservative=conservative):
			# the new guru is good enough and the individual is good enough for the guru
			# print('%s (%s) is about to follow %s (%s)' % (self, list(map(str, self.social_signature())), G, list(map(str, G.social_signature()))))
			if not self.follow(G, G_perf, conservative=conservative, Quit=self.G_quit_):
				error("Alliances", "inconsistent guru")
			if G.followers is not None:	
				if not G.followers.follow(self, perf, conservative=conservative, Quit=G.F_quit_):
					error('Alliances', "inconsistent self")
				# self.consistency()
				# G.consistency()
			return True
		else:	return False

	def G_quit_(self, Guru):
		""" the individual no longer follows its guru
		"""
		# self.consistency()
		# Guru.consistency()
		self.quit_(Guru)
		if Guru.followers is not None: 	Guru.followers.quit_(self)

	def F_quit_(self, Follower):
		""" the individual does not want its disciple any longer
		"""
		if self.followers is not None: 	
			self.followers.quit_(Follower)
			Follower.quit_(self)
		else:	error('Alliances', 'No Follower whatsoever')

	def get_friend(self, Offer, Partner, PartnerOffer):
		" Checks mutual acceptance before establishing friendship "
		if self.acquaintable(Offer, Partner, PartnerOffer):
			if not self.F_follow(Offer, Partner, PartnerOffer):
				error("Friend: self changed mind")
			if not Partner.F_follow(PartnerOffer, self, Offer):
				error("Friend: Partner changed mind")
			return True
		return False
		
	def end_friendship(self, Partner):
		" Partners remove each other from their address book "
		# print('\nsplitting up', self.id, Partner.id)
		# print(self.consistency(), Partner.consistency())		
		self.G_quit_(Partner)
		Partner.G_quit_(self)

	def nbFollowers(self):	return self.followers.nbFriends()

	def follower_rank(self, Friend):
		if self.followers:	return self.followers.rank(Friend)
		return -1
	
	def forgetAll(self):
		if self.followers is None:	Friend.forgetAll(self)
		else:	self.detach()

	def detach(self):
		""" The individual quits its guru and its followers
		"""
		for G in self.names():		self.G_quit_(G)	# G is erased from self's guru list
		if self.names() != []:		error("Alliances: recalcitrant guru")
		if self.followers is not None:
			for F in self.followers.names():	self.F_quit_(F)	# self is erased from F's guru list
			if self.followers.names() != []:	error("Alliances: sticky  followers")
		
	def consistency(self):
		# if self.size() > self.sizeMax():
			# error("Alliances", "too many gurus: %d" % self.friends.size())
		# if self.followers.size() > self.followers.sizeMax():
			# error("Alliances", "too many followers: %d" % self.followers.friends.size())
		for F in self.followers:
			if self not in F:
				print('self: %s' % self)
				print("self's followers: %s" % list(map(str, self.followers.names())))
				print('follower: %s' % F)
				print('its gurus: %s' % list(map(str, F.friends.names())))
				error("Alliances: non following followers")
			if self == F:	error("Alliances: Narcissism")
##            print self.id, ' is in ', F.id, "'s guru list: ", [G.id for G in F.gurus.names()]
		for G in self:
			if self not in G.followers:
				print('\n\nself: %s' % self)
				print("self's gurus: %s" % list(map(str, self.friends.names())))
				print('guru: %s' % G)
				print('its followers: %s' % list(map(str, G.followers.names())))
				error("Alliances: unaware guru")
			if self == G:	error("Alliances: narcissism")
##            print self.id, ' is in ', G.id, "'s follower list: ", [F.id for F in G.followers.names()]
##        print '\t', self.id, ' OK'
		if self.friends.size() > 0:
			if not self.friends.present((self.friends.best(), self.friends.maximal())):
				error("Alliances: best guru is ghost")
		return ('%s consistent' % self.id)
		
# # # # class Alliances(object):
	# # # # """	class Alliances: each agent stores both its gurus and its followers 
		# # # # (This is an old class, kept for compatibility (and not tested)	"""

	# # # # def __init__(self, MaxGurus, MaxFollowers):
		# # # # self.gurus = Friend(MaxGurus)
		# # # # self.followers = Friend(MaxFollowers)

	# # # # #################################
	# # # # # hierarchical links			#
	# # # # #################################
	
	# # # # def affiliable(self, perf, Guru, G_perf, conservative=True):
		# # # # " Checks whether affiliation is possible "
		# # # # return	self.gurus.affiliable(G_perf, conservative=conservative) \
			# # # # and	Guru.followers.affiliable(perf, conservative=conservative)
	
	# # # # def follow(self, perf, G, G_perf, conservative=True):
		# # # # """ the individual wants to be G's disciple because of some of G's performance
			# # # # G may evaluate the individual's performance too
		# # # # """
		# # # # if self.affiliable(perf, G, G_perf, conservative=conservative):
			# # # # # the new guru is good enough and the individual is good enough for the guru
			# # # # self.gurus.follow(G, G_perf, conservative=conservative, Quit=self.quit_)
			# # # # G.followers.follow(self, perf, conservative=conservative, Quit=G.quit_)
			# # # # return True
		# # # # else:	return False

	# # # # def quit_(self, Guru):
		# # # # """ the individual no longer follows its guru
		# # # # """
		# # # # Guru.followers.quit_(self)
		# # # # self.gurus.quit_(Guru)

	# # # # def best_friend(self):	return self.gurus.best_friend()
	
	# # # # def friends(self, ordered=True):	return self.gurus.Friends(ordered=ordered)

	# # # # def nbFriends(self):	return self.gurus.nbFriends()

	# # # # def nbFollowers(self):	return self.followers.nbFriends()

	# # # # def lessening_friendship(self, Factor=0.9):
		# # # # self.gurus.lessening_friendship(Factor)					

	# # # # def forgetAll(self):
		# # # # self.gurus.forgetAll()
		# # # # self.followers.forgetAll()

	# # # # #################################
	# # # # # symmetrical links             #
	# # # # #################################
	
	# # # # def acquaintable(self, Partner, Deal):
		# # # # return self.affiliable(Deal, Partner, Deal) and Partner.affiliable(Deal, self, Deal)
	
	# # # # def get_friend(self, Offer, Partner, Return=None):
		# # # # " Checks mutual acceptance before establishing friendship "
		# # # # if Return is None:	Return = Offer
		# # # # if self.affiliable(Offer, Partner, Return) and Partner.affiliable(Return, self, Offer):
			# # # # self.follow(Offer, Partner, Return)
			# # # # Partner.follow(Return, self, Offer)
			# # # # return True
		# # # # return False
	
	# # # # def best_friend_symmetry(self):
		# # # # " Checks whether self is its best friend's friend "
		# # # # BF = self.best_friend()
		# # # # if BF:  return self == BF.best_friend()
		# # # # return False
	
	# # # # def restore_symmetry(self):
		# # # # " Makes sure that self is its friends' friend - Useful for symmmtrical relations "
		# # # # for F in self.gurus.names()[:]:	 # need to copy the list, as it is modified within the loop
			# # # # #print 'checking symmetry for %d' % F.id, F.gurus.names()
			# # # # if self not in F.gurus.names():
				# # # # print('%s quits %s *****  because absent from %s' % (self.id, F.id, str(F.gurus.names())))
				# # # # self.quit_(F)   # no hard feelings 

		
	# # # # #################################
	# # # # # link processing			   #
	# # # # #################################
	# # # # def detach(self):
		# # # # """ The individual quits its guru and its followers
		# # # # """
		# # # # for G in self.gurus.names():		self.quit_(G)
		# # # # for F in self.followers.names():	F.quit_(self)
		# # # # if self.gurus.names() != []:		error("Alliances: recalcitrant guru")
		# # # # if self.followers.names() != []:	error("Alliances: sticky followers")
		
	# # # # def consistency(self):
		# # # # if self.gurus.size() > self.gurus.sizeMax():
			# # # # error("Alliances", "too many gurus: %d" % self.gurus.size())
		# # # # if self.followers.size() > self.followers.sizeMax():
			# # # # error("Alliances", "too many followers: %d" % self.followers.size())
		# # # # for F in self.followers.names():
			# # # # if self not in F.gurus.names():
				# # # # error("Alliances: non following followers")
			# # # # if self == F:	error("Alliances: Narcissism")
# # # # ##            print self.id, ' is in ', F.id, "'s guru list: ", [G.id for G in F.gurus.names()]
		# # # # for G in self.gurus.names():
			# # # # if self not in G.followers.names():
				# # # # # print 'self: ',str(self), "self's gurus: ",Alliances.social_signature(self)
				# # # # # print 'guru: ',str(G), 'its followers: ',[str(F) for F in G.followers.names()]
				# # # # error("Alliances: unaware guru")
			# # # # if self == G:	error("Alliances: narcissism")
# # # # ##            print self.id, ' is in ', G.id, "'s follower list: ", [F.id for F in G.followers.names()]
# # # # ##        print '\t', self.id, ' OK'
		# # # # if self.gurus.size() > 0:
			# # # # if not self.gurus.friends.present((self.gurus.best(), self.gurus.friends.maximal())):
					# # # # error("Alliances: best guru is ghost")

	# # # # def social_signature(self):
# # # # ##        return [F.id for F in self.gurus.names()]
		# # # # return self.gurus.Friends()
			
	# # # # def signature(self):	return self.social_signature()
	
###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	print(Friend.__doc__ + '\n\n')
	raw_input('[Return]')


__author__ = 'Dessalles'
