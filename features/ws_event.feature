Feature: Send event via Websocket

    Scenario: Run an event test
    When the client subscribes to the event
    And the server publishes the event
    Then the client receives the event
