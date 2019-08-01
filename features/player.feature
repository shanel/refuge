Feature: Player Creation

	Scenario: Create a barebones player
		Given the player does not currenty exist in the system
		When we pass in the requisite player data
		Then a barebones player is created.
	
	Scenario: Read the data of a player
		Given the player exists in the system
		When we request the player's data
		Then we get the requested player's data.

	Scenario: Update the data of a player
		Given the player exists in the system
		When we pass in the fields to be updated for the player
		Then the requested player's data is updated accordingly.

	Scenario: Delete the data of a player
		Given the player exists in the system
		When we request the player be deleted from the system
		Then the player's data is deleted from the system.
