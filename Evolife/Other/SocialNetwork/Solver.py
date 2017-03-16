#!/usr/bin/env python
## {{{ http://code.activestate.com/recipes/303396/ (r1)
'''equation solver using attributes and introspection'''

from __future__ import division

class Solver(object):
	'''takes a function, named arg value (opt.) and returns a Solver object'''
	
	def __init__(self,f,**args):
		self._f=f
		self._args={}
		# see important note on order of operations in __setattr__ below.
		for arg in f.func_code.co_varnames[0:f.func_code.co_argcount]:
			self._args[arg]=None
		self._setargs(**args)

	def __repr__(self):
		argstring=','.join(['%s=%s' % (arg,str(value)) for (arg,value) in
							 self._args.items()])
		if argstring:
			return 'Solver(%s,%s)' % (self._f.func_code.co_name, argstring)
		else:
			return 'Solver(%s)' % self._f.func_code.co_name

	def __getattr__(self,name):
		'''used to extract function argument values'''
		self._args[name]
		return self._solve_for(name)

	def __setattr__(self,name,value):
		'''sets function argument values'''
		# Note - once self._args is created, no new attributes can
		# be added to self.__dict__.  This is a good thing as it throws
		# an exception if you try to assign to an arg which is inappropriate
		# for the function in the solver.
		if self.__dict__.has_key('_args'):
			if name in self._args:
				self._args[name]=value
			else:
				raise KeyError, name
		else:
			object.__setattr__(self,name,value)

	def _setargs(self,**args):
		'''sets values of function arguments'''
		for arg in args:
			self._args[arg]  # raise exception if arg not in _args
			setattr(self,arg,args[arg])
			   
	def _solve_for(self,arg):
		'''Newton's method solver'''
		TOL=0.0000001	  # tolerance
		ITERLIMIT=1000		# iteration limit
		CLOSE_RUNS=10   # after getting close, do more passes
		args=self._args
		if self._args[arg]:
			x0=self._args[arg]
		else:
			x0=1
		if x0==0:
			x1=1
		else:
			x1=x0*1.1
		def f(x):
			'''function to solve'''
			args[arg]=x
			return self._f(**args)
		fx0=f(x0)
		n=0
		while 1:					# Newton's method loop here
			fx1 = f(x1)
			if fx1==0 or x1==x0:  # managed to nail it exactly
				break
			if abs(fx1-fx0)<TOL:	# very close
				close_flag=True
				if CLOSE_RUNS==0:	   # been close several times
					break
				else:
					CLOSE_RUNS-=1	   # try some more
			else:
				close_flag=False
			if n>ITERLIMIT:
				print "Failed to converge; exceeded iteration limit"
				break
			slope=(fx1-fx0)/(x1-x0)
			if slope==0:
				if close_flag:  # we're close but have zero slope, finish
					break
				else:
					print 'Zero slope and not close enough to solution'
					break
			x2=x0-fx0/slope		   # New 'x1'
			fx0 = fx1
			x0=x1
			x1=x2
			n+=1
		self._args[arg]=x1
		return x1

## end of http://code.activestate.com/recipes/303396/ }}}

######### Example ############
##from math import cos
##
##def toto(x,A):
##    return A-cos(x)
##
##T = Solver(toto)
##T.A = 0
##print 2 * T.x
######### Fin Example ############


def competence(BottomCompetence, Quality):
	return BottomCompetence + (1-BottomCompetence)*Quality

def Profit(b, K, friendQuality, r, NFriends):
	Risk = 1
	for f in range(NFriends):
		Risk *= (1 - K * r**f * competence(b, friendQuality))
	return 1 - Risk

def IntegralProfit(b, K, friendQuality, r, NFriends):
	Sum = 0
	for FQ in range(int(friendQuality * 100.01)):
		Sum += Profit(b, K, FQ/100.1, r, NFriends)
	return Sum / 100.01

def CompetitiveSignal(b, K, q, r, NFriends, cost):
	profit = Profit(b, K, q, r, NFriends)
	integralProfit = IntegralProfit(b, K, q, r, NFriends)
	return (competence(b, q) * profit - (1-b) * ralProfit) / cost

def CompetitiveSignal1FriendsB0(K, q, cost):
	# special case 1 friend and no bottom competence
	return K*q**2/(2*cost)

def CompetitiveSignal2FriendsB0(K, q, r, cost):
	# special case 2 friends and no bottom competence
	return (-2*K**2*r*q**3/(3*cost)+K*q**2*(1+r)/(2*cost))

def CompetitiveSignal3Friends(b, q, r, cost):
	# special case 3 friends 
	return (1-b)*((1+r+r**2)*(b*q+(1-b)*q**2/2) - 2*r*(1+r+r**2)*(b**2*q + (1-b)**2*q**3/3 +2*b*(1-b)*q**2/2) + 3*r**3 *(b**3*q + 3*b**2*(1-b)*q**2/2 + 3*b*(1-b)**2*q**3/3 + (1-b)**3*q**4/4) )/cost

def CompetitiveSignal3FriendsB0(q, r, cost):
	# special case 3 friends and no bottom competence
	return (1+r+r**2) *q**2/(2*cost) - 2*r*(1+r+r**2) *q**3/(3*cost) + 3*r**3* q**4/(4*cost)

def Equil2Friends(b, K, C, eta, r, deltag):
	# for two friends
	ro = 0
	S_eta = competence(b, eta)
	S_tau = competence(b,(1+eta)/2)
	bh =  K * S_tau *(1+r) - K**2 * r * S_tau**2 - C * deltag
	bl = (1 - (1 - (1-ro)*K*S_tau - ro * K * S_eta)*(1 - K*r*(1-ro)*S_tau - ro*K*r*S_eta)) + C * deltag
	# return bh-bl
	#return (1-S_eta)*(1 + r/2 - 3*r*S_eta/2) - 4 * C * deltag
	return K*(1-b)*(1-eta)*(1+r-K*r*(2*b + (1-b)*(3*eta+1)/2))/4 - C*deltag

def EquilManyFriends(b, K, C, eta, r, deltag, NF):
	S_eta = competence(b, eta)
	S_tau = competence(b,(1+eta)/2)
	return Profit(b,K,S_tau,r,NF) - Profit(b,K,S_eta,r,NF) - 2*C*deltag

def SubEquilManyFriends(b, K, C, eta, tau, theta, r, deltag, NF):
	S_eta = competence(b, eta)
	S_tau = competence(b, tau)
	SubMiddle = competence(b, (theta+eta)/2)
##    return Profit(b,K,S_tau,r,NF) - Profit(b,K,SubMiddle,r,NF) - 2*C*deltag / S_eta
	return Profit(b,K,S_tau,r,NF) - Profit(b,K,SubMiddle,r,NF) - 2*C*deltag
							  
def UniformSignalB0(K, C, eta, r, deltag, NF):
	b = 0   # otherwise false
	S_eta = competence(b, eta)
	S_tau = competence(b,(1+eta)/2)
	Pu = (Profit(b,K,S_tau,r,NF) + Profit(b,K,S_eta,r,NF)) /2
	Pc = IntegralProfit(b, K, eta, r, NF)
	return ( S_eta * Pu - Pc ) / C

def UniformBenefitB0(K, C, eta, theta, r, deltag, NF, sm, ro):
	b = 0   # otherwise false
	S_eta = competence(b, eta)
	S_theta = competence(b, theta)
	S_tau = competence(b,(1+eta)/2)
	Ptau = (1 + ro + ro*ro/4)/2
	#Ptau = (1 + ro)/2
	return Ptau * Profit(b,K,S_tau,r,NF) + (1-Ptau) * Profit(b,K,theta,r,NF) - (C*sm+ro*deltag)/S_theta

def DiffBenefitB0(K, C, eta, theta, r, deltag, NF, sm, ro):
	S_theta = competence(b, theta)
	return UniformBenefitB0(K, C, eta, theta, r, deltag, NF, sm, ro) \
		   - IntegralProfit(b, K, theta, r, NF)/S_theta

Equil = Solver(EquilManyFriends)
#Equil = Solver(Equil2Friends)
Equil.deltag = deltag = 1.2 * 0.11	# Learning noise
Equil.b = b =   0.0	 # BottomCompetence
Equil.K = K =   1.0   
Equil.r = r =   0.6	 # RankEffect
Equil.NF = NF = 2	   # Number of friends
Equil.C = C =   0.6	 # Cost
#Equil.ro =      0.0     # shift from uniform signal
Equil.eta =	 0.1	# threshold for uniform signal (initialization)
ETA = Equil.eta
OffSet = 0
print Equil



#print '%d\t%d' % (int(round(100* ETA)),(100*CompetitiveSignal(b,K,ETA, r, NF, C)))
#print 'Eta: %d\t competitive signal in Eta: %d' % (int(round(100* ETA)),(100*CompetitiveSignal3FriendsB0(ETA, r, C))),
print 'Eta: %d\t competitive signal in Eta: %d' % (int(round(100* ETA)),(100*CompetitiveSignal2FriendsB0(1,ETA, r, C))),

# sm = CompetitiveSignal3FriendsB0(ETA, r, C)
sm = UniformSignalB0(K, C, ETA, r, deltag, NF)
print 'sm: %d' % (100 * sm),


SubEquil = Solver(SubEquilManyFriends)
SubEquil.deltag = deltag	# Learning noise
SubEquil.b = b  # BottomCompetence
SubEquil.K = K   
SubEquil.r = r  # RankEffect
SubEquil.NF = NF	# Number of friends
SubEquil.C = C  # Cost
SubEquil.eta = ETA
SubEquil.tau = ETA
SubEquil.theta =	 0.1	# initialization
THETA = SubEquil.theta

print 'Theta: %d' % (100 * THETA),

### 2nd iteration
##SubEquil.eta = THETA
##SubEquil.theta =     0.1    # initialization
##THTHETA = SubEquil.theta
##print 'ThTheta: %d' % (100 * THTHETA),
print

#print SubEquil

"""
for q in range(1,int(round(100* THETA)),1):
	# print CompetitiveSignal3Friends(0,q/100.0,0.6,0.6),
	print "%01.1f\t" % (100 * CompetitiveSignal1FriendsB0(K,q/100.0,C)),
	#print "%01.1f\t" % (10000 * CompetitiveSignal3FriendsB0(q/100.0,r,C)/q),
for q in range(int(round(100* THETA)),101,1):
	print "%01.1f\t" % (100 * sm),
	#print "%01.1f\t" % (10000 * sm/q),
print
"""

##for q in range(1,int(round(100* ETA)),1):
##    print "%01.2f\t" % (100 * IntegralProfit(b,K,q/100.0,r,NF)),
##print

##for ro in range(-190, 190, 1):
##    Equil.ro = ro/100.0
##    Equil.eta = 0.01
##    ETA = Equil.eta
##    print '%d\t' % (int(round(100* ETA))),
##print
	
##for dtheta in range(-5, 10):
##    theta = ETA - dtheta / 100.0
##    print theta
##    for ro in range(-5,5,1):
##        print "%01.1f\t" % (100 * DiffBenefitB0(K, C, ETA, theta, r, deltag, NF, sm, ro/100.0)),
##    print

#print "%01.1f\t" % (100 * DiffBenefitB0(K, C, ETA, ETA, r, deltag, NF, sm, 0.0))


	


__author__ = 'Dessalles'
