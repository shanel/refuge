Feature: Session Creation

	Scenario: Create a barebones session
		Given the session does not currenty exist in the system
		When we pass in the requisite session data
		Then a barebones session is created.
	
	Scenario: Read the data of a session
		Given the session exists in the system
		When we request the session's data
		Then we get the requested session's data.

	Scenario: Update the data of a session
		Given the session exists in the system
		When we pass in the fields to be updated for the session
		Then the requested session's data is updated accordingly.

	Scenario: Delete the data of a session
		Given the session exists in the system
		When we request the session be deleted from the system
		Then the session's data is deleted from the system.
