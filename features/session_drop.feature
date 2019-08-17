Feature: Session Drops

	Scenario: Drop from a session with a waitlist
		Given the session exists in the system
		And the session is full
		And the session has a waitlist
		When a player drops the session
		Then the first player on the waitlist moves into the session
		And the waitlist has one fewer entries
		And the dropping player's noted as dropping at a specific time
		And the promoted player is noted as moving off the waitlist at a specific time
	
	Scenario: Drop from a session without a waitlist
		Given the session exists in the system
		And the session is full
		When a player drops the session
		Then the session is no longer full
		And the dropping player is noted as dropping at a specific time
	
	Scenario: Drop from a session's waitlist
		Given the session exists in the system
		And the session is full
		And the session has a waitlist
		When a player drops from the waitlist
		Then the waitlist has one fewer entries
		And the session is full
