Feature: Send state via Websocket

    Scenario: Run a state test
    When the client subscribes to the state
    And the server publishes the state
    Then the client receives the state
