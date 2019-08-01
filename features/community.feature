Feature: Community Creation

	Scenario: Create a barebones community
		Given the community does not currenty exist in the system
		When we pass in the requisite community data
		Then a barebones community is created.
	
	Scenario: Read the data of a community
		Given the community exists in the system
		When we request the community's data
		Then we get the requested community's data.

	Scenario: Update the data of a community
		Given the community exists in the system
		When we pass in the fields to be updated for the community
		Then the requested community's data is updated accordingly.

	Scenario: Delete the data of a community
		Given the community exists in the system
		When we request the community be deleted from the system
		Then the community's data is deleted from the system.
