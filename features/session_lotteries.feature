Feature: Run Session Lotteries

	Scenario Outline: Simple Lottery
		Given the session exists in the system
		And the lottery has not run yet
		And the lottery was scheduled for <min_ago> minutes ago
		And there are <participants> participants in the lottery
		And there is a minimum of <min> players
		And there is a maximum of <max> players
		When we run the lottery
		Then there are <winners> players in the session
		And there are <waitlisted> players on the session's waitlist

		Examples: Simple Examples
			| min_ago | participants | min | max | winners | waitlisted |
			| 15      | 7            | 2   | 4   | 4       | 3          | 
			| 15      | 2            | 2   | 4   | 2       | 0          |
