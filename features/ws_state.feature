Feature: Send state via Websocket

    Scenario: Run a state test
    Given a running server and a client
    When the client subscribes to state
    And the server publishes state
    Then the client receives the state
    Then close the server and client
