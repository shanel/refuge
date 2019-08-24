Feature: Session Drops

	Scenario: Drop from a session with a waitlist
		Given the session exists in the system
		And a lottery was scheduled to run before now with 7 participants and a maximum of 4 players and has not
		When we run the lottery
		And a player drops the session
		Then the first player on the waitlist moves into the session
		And there are 4 players in the session
		And there are 2 players on the session's waitlist
	
	Scenario: Drop from a session without a waitlist
		Given the session exists in the system
		And a lottery was scheduled to run before now with 4 participants and a maximum of 4 players and has not
		When we run the lottery
		And a player drops the session
		Then there are 3 players in the session
		And there are 0 players on the session's waitlist
	
	Scenario: Drop from a session's waitlist
		Given the session exists in the system
		And a lottery was scheduled to run before now with 7 participants and a maximum of 3 players and has not
		When we run the lottery
		And a player drops from the waitlist
		Then there are 3 players in the session
		And there are 3 players on the session's waitlist
