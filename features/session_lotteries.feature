Feature: Run Session Lotteries

	Scenario Outline: Simple Lottery Signup
		Given a lottery was scheduled to run before now with <participants> participants and a maximum of <max> players and has not
		When a player signs up
		Then there are <new> participants

		Examples: Simple Signup Examples
			| participants | max | new |
			| 7            | 4   | 8   |

	Scenario Outline: Simple Lottery
		Given a lottery was scheduled to run before now with <participants> participants and a maximum of <max> players and has not
		When we run the lottery
		Then there are <winners> players in the session
		And there are <waitlisted> players on the session's waitlist

		Examples: Simple Examples
			| participants | max | winners | waitlisted |
			| 7            | 4   | 4       | 3          |
			| 2            | 4   | 2       | 0          |
			| 4            | 4   | 4       | 0          |
			| 0            | 4   | 0       | 0          |

	Scenario Outline: Post Lottery Signup
		Given a lottery has run before now with <participants> participants and a maximum of <max> players
		When a player signs up
		Then there are <winners> players in the session
		And there are <waitlisted> players on the session's waitlist

		Examples: Post Lottery Signup Examples
			| participants | max | winners | waitlisted |
			| 7            | 4   | 4       | 4          |
			| 2            | 4   | 3       | 0          |
			| 4            | 4   | 4       | 1          |
			| 0            | 4   | 1       | 0          |
